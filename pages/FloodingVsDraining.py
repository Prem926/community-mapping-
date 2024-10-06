import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import folium
from streamlit_folium import folium_static
from folium.plugins import Draw, MousePosition
import plotly.graph_objects as go
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from streamlit_lottie import st_lottie
import requests
from branca.colormap import LinearColormap
import json

# Set page config
st.set_page_config(page_title="Flood and Drainage Prediction", layout="wide")

# Load Lottie animation
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load the trained models
model_flood = joblib.load(r'models/best_flood_time_model.pkl')
model_drain = joblib.load(r'models/best_drainage_time_model.pkl')

# Load the scaler
scaler = joblib.load(r'models/scaler.pkl')

# Title of the Streamlit app
st.title("🌊 Advanced Flood and Drainage Time Prediction")

# Load water animation
lottie_water = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_gkgqj2yq.json")
st_lottie(lottie_water, height=200, key="water_animation")

# Geocoding function
def geocode_address(address):
    geolocator = Nominatim(user_agent="flood_prediction_app")
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except GeocoderTimedOut:
        st.error("Geocoding service timed out. Please try again.")
        return None, None

# Sidebar for user inputs
st.sidebar.header("📊 Input Parameters")

def user_input_features():
    address = st.sidebar.text_input("Enter address", "Mumbai, India")
    latitude, longitude = geocode_address(address)
    
    if latitude and longitude:
        st.sidebar.success(f"Location found: {latitude}, {longitude}")
    else:
        st.sidebar.error("Location not found. Please enter a valid address.")
        latitude, longitude = 19.0760, 72.8777  # Default to Mumbai

    rainfall_intensity = st.sidebar.slider("Rainfall Intensity (mm/hr)", min_value=0, max_value=500, value=150)
    humidity = st.sidebar.slider("Humidity (%)", min_value=0, max_value=100, value=80)
    pressure = st.sidebar.slider("Pressure (hPa)", min_value=900, max_value=1100, value=1010)
    visibility = st.sidebar.slider("Visibility (km)", min_value=0, max_value=10, value=5)
    road_size_length = st.sidebar.slider("Road Length (meters)", min_value=0, max_value=1000, value=300)
    road_size_width = st.sidebar.slider("Road Width (meters)", min_value=0, max_value=100, value=20)
    road_depth = st.sidebar.slider("Road Depth (meters)", min_value=0.0, max_value=5.0, value=0.5)
    elevation = st.sidebar.slider("Elevation (meters)", min_value=0, max_value=100, value=10)
    drainage_capacity = st.sidebar.slider("Drainage Capacity (cubic meters/hour)", min_value=0, max_value=500, value=50)
    evaporation_rate = st.sidebar.slider("Evaporation Rate (cubic meters/hour/square meter)", min_value=0.0, max_value=1.0, value=0.005)

    data = {
        'latitude': latitude,
        'longitude': longitude,
        'rainfall_intensity': rainfall_intensity,
        'humidity': humidity,
        'pressure': pressure,
        'visibility': visibility,
        'road_size_length': road_size_length,
        'road_size_width': road_size_width,
        'road_depth': road_depth,
        'elevation': elevation,
        'drainage_capacity': drainage_capacity,
        'evaporation_rate': evaporation_rate
    }
    features = pd.DataFrame(data, index=[0])
    return features

df = user_input_features()

# Show user inputs
st.subheader('🔍 User Input Parameters')
st.write(df)

# Function to simulate based on new input
def simulate_flood_and_drainage(latitude, longitude, rainfall_intensity, humidity, pressure, visibility,
                                road_size_length, road_size_width, road_depth, elevation,
                                drainage_capacity, evaporation_rate):
    
    # Calculate road area
    road_area = road_size_length * road_size_width
    
    # Create a DataFrame for the new input
    new_data = pd.DataFrame({
        'rainfall_intensity': [rainfall_intensity],
        'road_area': [road_area],
        'road_depth': [road_depth],
        'drainage_capacity': [drainage_capacity],
        'evaporation_rate': [evaporation_rate],
        'humidity': [humidity],
        'pressure': [pressure],
        'elevation': [elevation]
    })
    
    # Scale the new data
    new_data_scaled = scaler.transform(new_data)
    
    # Predict flood time and drainage time
    flood_time_pred = model_flood.predict(new_data_scaled)
    drain_time_pred = model_drain.predict(new_data_scaled)
    
    return flood_time_pred[0], drain_time_pred[0], road_area

# Run the simulation
flood_time, drain_time, road_area = simulate_flood_and_drainage(
    df['latitude'][0], df['longitude'][0], df['rainfall_intensity'][0], df['humidity'][0], df['pressure'][0],
    df['visibility'][0], df['road_size_length'][0], df['road_size_width'][0], df['road_depth'][0], df['elevation'][0],
    df['drainage_capacity'][0], df['evaporation_rate'][0]
)

flood_time = float(flood_time)
drain_time = float(drain_time)
road_area = float(road_area)

# Show the results
st.subheader("🎯 Predicted Results")
col1, col2 = st.columns(2)
with col1:
    st.metric("Time to flood the road", f"{flood_time:.2f} hours", delta=f"{flood_time:.2f}")
with col2:
    st.metric("Time to drain the road", f"{drain_time:.2f} hours", delta=f"{drain_time:.2f}")

# Create a folium map centered on the location
map_flood = folium.Map(location=[df['latitude'][0], df['longitude'][0]], zoom_start=13)

# Simulate flood areas using circles (for demonstration)
flood_radius = np.sqrt(road_area / np.pi)  # Calculate radius from area

# Create a color map for flood severity
colormap = LinearColormap(colors=['green', 'yellow', 'red'], vmin=0, vmax=24)

# Add circles to represent different flood severity levels
for i in range(3):
    folium.Circle(
        location=[df['latitude'][0], df['longitude'][0]],
        radius=flood_radius * (i + 1) / 3,
        color=colormap(flood_time * (i + 1) / 3),
        fill=True,
        fill_opacity=0.3,
        popup=f"Flood Severity: {['Low', 'Medium', 'High'][i]}",
    ).add_to(map_flood)

# Add a marker for the location
folium.Marker(
    location=[df['latitude'][0], df['longitude'][0]],
    popup=f"Flood Time: {flood_time:.2f} hrs, Drainage Time: {drain_time:.2f} hrs",
    icon=folium.Icon(color="red", icon="info-sign"),
).add_to(map_flood)

# Add color map to the map
colormap.add_to(map_flood)
colormap.caption = "Flood Severity (hours)"

# Add Draw plugin to allow user to add markers
draw = Draw(
    draw_options={
        'polyline': False,
        'rectangle': False,
        'polygon': False,
        'circle': False,
        'marker': True,
        'circlemarker': False},
    edit_options={'edit': False}
)
draw.add_to(map_flood)

# Add MousePosition plugin to show coordinates
MousePosition().add_to(map_flood)

# Display the map
st.subheader("🗺️ Flood Area Visualization")
st.write("Click on the map to add a marker and get flood predictions for specific locations.")
folium_static(map_flood, width=700, height=500)

# Create placeholders for clicked point information
clicked_lat = st.empty()
clicked_lng = st.empty()
clicked_flood_time = st.empty()
clicked_drain_time = st.empty()
clicked_risk = st.empty()

# Add a button to simulate getting predictions for a clicked point
if st.button("Simulate Click Prediction"):
    # Generate random coordinates near the original point
    lat_offset = np.random.uniform(-0.01, 0.01)
    lng_offset = np.random.uniform(-0.01, 0.01)
    clicked_lat.write(f"Clicked latitude: {df['latitude'][0] + lat_offset:.6f}")
    clicked_lng.write(f"Clicked longitude: {df['longitude'][0] + lng_offset:.6f}")
    
    # Simulate flood and drainage times (replace with actual predictions in a real scenario)
    simulated_flood_time = np.random.uniform(0, 24)
    simulated_drain_time = np.random.uniform(0, 24)
    clicked_flood_time.write(f"Predicted flood time: {simulated_flood_time:.2f} hours")
    clicked_drain_time.write(f"Predicted drainage time: {simulated_drain_time:.2f} hours")
    
    if simulated_flood_time < 8:
        clicked_risk.success("Low flood risk")
    elif simulated_flood_time < 16:
        clicked_risk.warning("Medium flood risk")
    else:
        clicked_risk.error("High flood risk")

# Visualize the predictions
st.subheader("📈 Prediction Analysis")

# Create a gauge chart for flood risk
def create_gauge(value, title):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, 24], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 8], 'color': 'green'},
                {'range': [8, 16], 'color': 'yellow'},
                {'range': [16, 24], 'color': 'red'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value}}))
    fig.update_layout(height=300)
    return fig

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(create_gauge(flood_time, "Flood Time (hours)"), use_container_width=True)
with col2:
    st.plotly_chart(create_gauge(drain_time, "Drainage Time (hours)"), use_container_width=True)

# Create a comparison bar chart
fig = go.Figure(data=[
    go.Bar(name='Flood Time', x=['Time'], y=[flood_time], marker_color='blue'),
    go.Bar(name='Drainage Time', x=['Time'], y=[drain_time], marker_color='green')
])
fig.update_layout(barmode='group', title='Comparison of Flood and Drainage Times')
st.plotly_chart(fig, use_container_width=True)

# Add a radar chart for input parameters
st.subheader("🕸️ Input Parameter Analysis")
input_params = ['Rainfall', 'Humidity', 'Pressure', 'Visibility', 'Road Size', 'Elevation', 'Drainage']
input_values = [df['rainfall_intensity'][0]/5, df['humidity'][0], (df['pressure'][0]-900)/2, 
                df['visibility'][0]*10, (df['road_size_length'][0]*df['road_size_width'][0])/1000, 
                df['elevation'][0], df['drainage_capacity'][0]/5]

fig = go.Figure(data=go.Scatterpolar(
  r=input_values,
  theta=input_params,
  fill='toself'
))

fig.update_layout(
  polar=dict(
    radialaxis=dict(
      visible=True,
      range=[0, 100]
    )),
  showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# Add a time series forecast
st.subheader("📊 Flood Risk Forecast")
forecast_hours = 24
forecast_times = list(range(forecast_hours))
forecast_values = [max(0, flood_time - i * (flood_time / drain_time)) for i in range(forecast_hours)]

fig = px.line(x=forecast_times, y=forecast_values, 
              labels={'x': 'Hours from now', 'y': 'Flood Risk'},
              title='24-Hour Flood Risk Forecast')
fig.add_hline(y=8, line_dash="dash", line_color="green", annotation_text="Low Risk")
fig.add_hline(y=16, line_dash="dash", line_color="red", annotation_text="High Risk")
st.plotly_chart(fig, use_container_width=True)

# Add some educational content
st.subheader("📚 Flood Prevention Tips")
st.write("""
1. **Improve Drainage Systems**: Ensure proper maintenance of storm drains and sewers.
2. **Create Green Spaces**: Increase permeable surfaces to absorb rainwater.
3. **Elevate Critical Infrastructure**: Raise important equipment above potential flood levels.
4. **Install Flood Barriers**: Use temporary or permanent barriers to protect vulnerable areas.
5. **Develop Early Warning Systems**: Implement systems to alert residents of potential flooding.
""")

# Add a call to action
st.subheader("🚨 Emergency Contacts")
st.info("In case of flooding, contact your local emergency services or call the national flood helpline.")

# Add a section for community engagement
st.subheader("🤝 Community Engagement")
st.write("""
Join our community efforts to prevent and mitigate flooding:
- Volunteer for local clean-up drives
- Participate in flood awareness workshops
- Report blocked drains or other infrastructure issues to local authorities
- Share this tool with your neighbors to increase community preparedness
""")

# Provide a download link for a detailed report
st.subheader("📥 Download Detailed Report")
report_data = f"""
Flood and Drainage Analysis Report

Location: {df['latitude'][0]}, {df['longitude'][0]}
Predicted Flood Time: {flood_time:.2f} hours
Predicted Drainage Time: {drain_time:.2f} hours

Input Parameters:
{df.to_string()}

Recommendations:
1. Monitor local weather forecasts closely
2. Prepare emergency supplies
3. Review your flood insurance policy
4. Implement flood prevention measures as needed

For more information, visit our website or contact local authorities.
"""

st.download_button(
    label="Download Report",
    data=report_data,
    file_name="flood_analysis_report.txt",
    mime="text/plain"
)