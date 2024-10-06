import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# Function to get forecast data
def get_forecast_data(location):
    api_key = "4a83da95401cd1052adc94d76f105dec"    # Replace with your OpenWeatherMap API key
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()

# Function to process forecast data into a DataFrame
def process_forecast_data(forecast_data):
    df = pd.DataFrame([{
        "Datetime": item["dt_txt"],
        "Temperature (°C)": item["main"]["temp"],
        "Weather": item["weather"][0]["description"],
        "Wind Speed (m/s)": item["wind"]["speed"],
        "Humidity (%)": item["main"]["humidity"],
        "Rainfall (mm)": item.get("rain", {}).get("3h", 0),
    } for item in forecast_data["list"]])

    df["Datetime"] = pd.to_datetime(df["Datetime"])
    return df

# Function to plot forecast data
def plot_forecast(df):
    fig = px.line(df, x="Datetime", y="Rainfall (mm)", title="5-Day Rainfall Forecast", markers=True)
    fig.update_traces(line_color='blue', line=dict(width=3))
    fig.update_layout(xaxis_title="Date & Time", yaxis_title="Rainfall (mm)")
    fig.update_layout(
        font=dict(size=12 , color="black"),
        plot_bgcolor='black',
        hovermode="x unified",
        hoverlabel=dict(bgcolor="black", font_size=12),
        yaxis=dict(showgrid=True, zeroline=False),
        xaxis=dict(showgrid=False)
    )
    return fig

# New function for water scarcity analysis
def analyze_water_scarcity(df):
    rainfall_sum = df['Rainfall (mm)'].sum()
    water_scarcity_risk = 'Low' if rainfall_sum > 50 else 'Moderate' if rainfall_sum > 25 else 'High'
    return rainfall_sum, water_scarcity_risk

# New function for urban heat island effect analysis
def analyze_heat_island(df):
    avg_temp = df['Temperature (°C)'].mean()
    heat_island_risk = 'Low' if avg_temp < 25 else 'Moderate' if avg_temp < 30 else 'High'
    return avg_temp, heat_island_risk

# New function for air pollution analysis
def analyze_air_pollution(location):
    api_key = "4a83da95401cd1052adc94d76f105dec"
    url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?q={location}&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    if 'list' in data:
        aqi_values = [item['main']['aqi'] for item in data['list']]
        avg_aqi = sum(aqi_values) / len(aqi_values)
        pollution_level = 'Low' if avg_aqi < 2 else 'Moderate' if avg_aqi < 4 else 'High'
        return avg_aqi, pollution_level
    return None, None

# New function to create a map of green spaces (simulated data)
def create_green_space_map(location):
    # Simulated data for green spaces
    green_spaces = [
        {"name": "City Park", "lat": 28.61, "lon": 77.23, "area": 5000},
        {"name": "Rooftop Garden", "lat": 28.63, "lon": 77.22, "area": 1000},
        {"name": "Urban Forest", "lat": 28.62, "lon": 77.21, "area": 3000},
    ]
    
    fig = px.scatter_mapbox(green_spaces, lat="lat", lon="lon", size="area",
                            color_discrete_sequence=["green"],
                            zoom=10, height=300,
                            hover_name="name", hover_data=["area"])
    fig.update_layout(mapbox_style="open-street-map")
    return fig

# New function for energy consumption prediction
def predict_energy_consumption(temp):
    # Simplified model: Energy consumption increases with temperature
    base_consumption = 100  # kWh
    temp_factor = 2  # kWh per degree Celsius
    return base_consumption + temp_factor * max(0, temp - 20)

# New function for flood risk assessment
def assess_flood_risk(rainfall):
    if rainfall > 100:
        return "High"
    elif rainfall > 50:
        return "Moderate"
    else:
        return "Low"

# New function for air quality index prediction
def predict_aqi(temp, humidity):
    # Simplified model: AQI increases with temperature and humidity
    return min(300, max(0, int(temp * 2 + humidity * 0.5)))

# Streamlit app layout
st.set_page_config(page_title="5-Day Forecast & Environmental Analysis", layout="wide")
st.title("📅 5-Day Weather Forecast & Environmental Analysis")

# Sidebar for searching a place
location = st.sidebar.text_input("Enter a place name", "Delhi")

# Fetch forecast data
forecast_data = get_forecast_data(location)

if forecast_data.get("cod") != "200":
    st.error("Location not found. Please enter a valid place name.")
else:
    df_forecast = process_forecast_data(forecast_data)
    
    # Display the forecast data
    st.subheader(f"5-Day Forecast for {location.capitalize()}:")

    # Plot temperature forecast
    st.plotly_chart(plot_forecast(df_forecast), use_container_width=True)
    
    # Display raw data in a styled table
    styled_df = df_forecast.style.applymap(lambda val: f'background-color: {"red" if val > 30 else "green" if val > 20 else "blue"}', subset=["Temperature (°C)"])
    styled_df = styled_df.applymap(lambda val: f'background-color: {"red" if val > 0 else "green"}', subset=["Rainfall (mm)"])
    st.dataframe(styled_df, height=400)

    # Add a summary of forecast
    avg_temp = df_forecast["Temperature (°C)"].mean()
    max_temp = df_forecast["Temperature (°C)"].max()
    min_temp = df_forecast["Temperature (°C)"].min()
    st.write(f"### Summary:")
    st.write(f"**Average Temperature:** {avg_temp:.2f}°C")
    st.write(f"**Max Temperature:** {max_temp:.2f}°C")
    st.write(f"**Min Temperature:** {min_temp:.2f}°C")

    # Advanced Analysis
    st.write("## Advanced Environmental Analysis")

    # Water Scarcity Analysis
    rainfall_sum, water_scarcity_risk = analyze_water_scarcity(df_forecast)
    st.write(f"### Water Scarcity Risk: {water_scarcity_risk}")
    st.write(f"Total expected rainfall: {rainfall_sum:.2f} mm")
    st.write("Recommendations:")
    st.write("- Implement rainwater harvesting systems")
    st.write("- Promote water-efficient irrigation techniques")
    st.write("- Encourage wastewater treatment and reuse")

    # Urban Heat Island Effect Analysis
    avg_temp, heat_island_risk = analyze_heat_island(df_forecast)
    st.write(f"### Urban Heat Island Risk: {heat_island_risk}")
    st.write(f"Average temperature: {avg_temp:.2f}°C")
    st.write("Recommendations:")
    st.write("- Increase urban green spaces")
    st.write("- Promote rooftop gardens")
    st.write("- Implement cool pavement technologies")

    # Air Pollution Analysis
    avg_aqi, pollution_level = analyze_air_pollution(location)
    if avg_aqi and pollution_level:
        st.write(f"### Air Pollution Level: {pollution_level}")
        st.write(f"Average Air Quality Index: {avg_aqi:.2f}")
        st.write("Recommendations:")
        st.write("- Promote use of electric vehicles")
        st.write("- Improve public transportation")
        st.write("- Encourage industries to adopt cleaner technologies")

    # Energy Consumption Prediction
    energy_consumption = predict_energy_consumption(avg_temp)
    st.write(f"### Predicted Energy Consumption: {energy_consumption:.2f} kWh")
    st.write("Recommendations:")
    st.write("- Implement smart grid technologies")
    st.write("- Promote energy-efficient appliances")
    st.write("- Encourage the use of renewable energy sources")

    # Flood Risk Assessment
    flood_risk = assess_flood_risk(rainfall_sum)
    st.write(f"### Flood Risk: {flood_risk}")
    st.write("Recommendations:")
    st.write("- Improve drainage systems")
    st.write("- Develop early warning systems")
    st.write("- Create flood-resistant infrastructure")

    # Visualizations
    st.write("## Environmental Visualizations")

    # Temperature and Rainfall Line Chart
    fig_temp_rain = go.Figure()
    fig_temp_rain.add_trace(go.Scatter(x=df_forecast['Datetime'], y=df_forecast['Temperature (°C)'], name='Temperature'))
    fig_temp_rain.add_trace(go.Scatter(x=df_forecast['Datetime'], y=df_forecast['Rainfall (mm)'], name='Rainfall', yaxis='y2'))
    fig_temp_rain.update_layout(
        title='Temperature and Rainfall Forecast',
        yaxis=dict(title='Temperature (°C)'),
        yaxis2=dict(title='Rainfall (mm)', overlaying='y', side='right')
    )
    st.plotly_chart(fig_temp_rain, use_container_width=True)

    # Wind Speed Polar Chart
    fig_wind = px.scatter_polar(df_forecast, r='Wind Speed (m/s)', theta='Datetime', color='Temperature (°C)')
    fig_wind.update_layout(title='Wind Speed and Direction')
    st.plotly_chart(fig_wind, use_container_width=True)

    # Humidity Heatmap
    fig_humidity = px.imshow(df_forecast.pivot(index='Datetime', columns='Temperature (°C)', values='Humidity (%)'))
    fig_humidity.update_layout(title='Humidity Heatmap')
    st.plotly_chart(fig_humidity, use_container_width=True)

    # AQI Prediction
    aqi_predictions = [predict_aqi(temp, humidity) for temp, humidity in zip(df_forecast['Temperature (°C)'], df_forecast['Humidity (%)'])]
    fig_aqi = px.line(x=df_forecast['Datetime'], y=aqi_predictions, title='Predicted Air Quality Index')
    fig_aqi.update_layout(yaxis_title='AQI')
    st.plotly_chart(fig_aqi, use_container_width=True)

    # Green Spaces Map
    st.write("### Green Spaces Map")
    st.plotly_chart(create_green_space_map(location), use_container_width=True)

    # Additional Features
    st.write("## Additional Environmental Features")

    # 1. Carbon Footprint Calculator
    st.write("### Carbon Footprint Calculator")
    energy_usage = st.slider("Monthly Energy Usage (kWh)", 0, 1000, 500)
    travel_distance = st.slider("Monthly Travel Distance (km)", 0, 1000, 200)
    carbon_footprint = energy_usage * 0.5 + travel_distance * 0.2
    st.write(f"Estimated Carbon Footprint: {carbon_footprint:.2f} kg CO2")

    # 2. Sustainable Living Tips
    st.write("### Sustainable Living Tips")
    tips = [
        "Use energy-efficient appliances",
        "Reduce, reuse, and recycle",
        "Use public transportation or carpool",
        "Plant trees or support local green initiatives",
        "Conserve water by fixing leaks and using water-saving fixtures"
    ]
    for tip in tips:
        st.write(f"- {tip}")

    # 3. Environmental Policy Tracker
    st.write("### Environmental Policy Tracker")
    policies = {
        "Carbon Tax": "Implemented",
        "Renewable Energy Incentives": "In Progress",
        "Plastic Ban": "Proposed",
        "Electric Vehicle Subsidies": "Implemented",
        "Green Building Standards": "In Progress"
    }
    for policy, status in policies.items():
        st.write(f"- {policy}: {status}")

    # 4. Biodiversity Index
    st.write("### Local Biodiversity Index")
    biodiversity_score = np.random.randint(50, 100)
    st.progress(biodiversity_score)
    st.write(f"Biodiversity Score: {biodiversity_score}/100")

    # 5. Waste Management Efficiency
    st.write("### Waste Management Efficiency")
    waste_recycled = np.random.randint(20, 80)
    waste_landfill = 100 - waste_recycled
    fig_waste = px.pie(values=[waste_recycled, waste_landfill], names=['Recycled', 'Landfill'], title='Waste Management')
    st.plotly_chart(fig_waste, use_container_width=True)

# Style improvements
st.markdown("""
<style>
    .stButton button {
        background-color: #FFA07A;
        color: white;
        font-size: 16px;
        border-radius: 10px;
        padding: 10px 20px;
    }
    .stTextInput input {
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)