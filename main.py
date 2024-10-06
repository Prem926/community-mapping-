import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from folium.plugins import MarkerCluster, HeatMap, Draw
import random
import pandas as pd
import plotly.express as px
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from sklearn.ensemble import RandomForestClassifier
import plotly.graph_objects as go

# Function to get weather data
def get_weather_data(location):
    api_key = "4a83da95401cd1052adc94d76f105dec"  # Replace with your OpenWeatherMap API key
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)  # Set timeout to 10 seconds
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.Timeout:
        st.error("The request timed out. Please try again.")
        return {}
    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP error occurred: {err}")
        return {}
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return {}

def create_map(lat, lon, location_name):
    map_ = folium.Map(location=[lat, lon], zoom_start=12)

    # Adding layer control
    folium.LayerControl().add_to(map_)

    # Adding different map views
    folium.TileLayer('OpenStreetMap').add_to(map_)
    folium.TileLayer('CartoDB positron', name='CartoDB Positron').add_to(map_)
    folium.TileLayer('CartoDB dark_matter', name='CartoDB Dark Matter').add_to(map_)
    
    # Adding Satellite view using Esri
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite',
        overlay=False,
        control=True
    ).add_to(map_)

    # Adding MarkerCluster for multiple markers
    marker_cluster = MarkerCluster().add_to(map_)

    # Adding drawing tools
    draw = Draw(
        draw_options={
            'polyline': True,
            'rectangle': True,
            'polygon': True,
            'circle': True,
            'marker': True,
            'circlemarker': False
        },
        edit_options={'edit': True}
    )
    draw.add_to(map_)

    # Adding Marker for the location
    folium.Marker([lat, lon], tooltip=location_name, icon=folium.Icon(color='blue', icon='cloud')).add_to(marker_cluster)

    # Adding some custom animation (e.g., Pulse animation)
    folium.Marker(
        [lat, lon],
        tooltip=f"{location_name} - Click for more info",
        icon=folium.Icon(color='blue', icon='cloud', prefix='fa'),
    ).add_to(marker_cluster)

    # Example data for other markers (could be replaced with actual data)
    other_locations = [
        {'name': 'Park', 'lat': lat + 0.01, 'lon': lon - 0.01},
        {'name': 'Community Center', 'lat': lat - 0.01, 'lon': lon + 0.01},
        {'name': 'School', 'lat': lat + 0.015, 'lon': lon + 0.015}
    ]

    for loc in other_locations:
        folium.Marker(
            [loc['lat'], loc['lon']],
            tooltip=loc['name'],
            icon=folium.Icon(color='green')
        ).add_to(marker_cluster)

    # Urban flooding prediction (demo)
    flood_risk_areas = [
        {'lat': lat + 0.02, 'lon': lon - 0.02, 'risk': 'high'},
        {'lat': lat - 0.015, 'lon': lon + 0.025, 'risk': 'medium'},
        {'lat': lat + 0.03, 'lon': lon + 0.01, 'risk': 'low'}
    ]

    for area in flood_risk_areas:
        color = 'red' if area['risk'] == 'high' else 'orange' if area['risk'] == 'medium' else 'yellow'
        folium.Circle(
            location=[area['lat'], area['lon']],
            radius=300,
            popup=f"Flood risk: {area['risk']}",
            color=color,
            fill=True
        ).add_to(map_)

    # Traffic information (demo)
    traffic_data = [
        {'lat': lat + 0.01, 'lon': lon - 0.01, 'intensity': 0.8},
        {'lat': lat - 0.01, 'lon': lon + 0.01, 'intensity': 0.5},
        {'lat': lat + 0.015, 'lon': lon + 0.015, 'intensity': 0.3}
    ]
    HeatMap([(d['lat'], d['lon'], d['intensity']) for d in traffic_data], name="Traffic Heatmap").add_to(map_)

    # Construction sites (demo)
    construction_sites = [
        {'lat': lat + 0.005, 'lon': lon - 0.005, 'info': 'Road repair'},
        {'lat': lat - 0.008, 'lon': lon + 0.007, 'info': 'New building'}
    ]
    for site in construction_sites:
        folium.Marker(
            [site['lat'], site['lon']],
            popup=site['info'],
            icon=folium.Icon(color='orange', icon='hard-hat', prefix='fa')
        ).add_to(marker_cluster)

    # Water Scarcity Solutions
    water_solutions = [
        {'lat': lat + 0.02, 'lon': lon - 0.02, 'name': 'Rainwater Harvesting', 'icon': 'tint'},
        {'lat': lat - 0.02, 'lon': lon + 0.02, 'name': 'Wastewater Treatment Plant', 'icon': 'recycle'},
        {'lat': lat + 0.03, 'lon': lon + 0.01, 'name': 'Efficient Irrigation System', 'icon': 'seedling'}
    ]
    for solution in water_solutions:
        folium.Marker(
            [solution['lat'], solution['lon']],
            popup=solution['name'],
            icon=folium.Icon(color='blue', icon=solution['icon'], prefix='fa')
        ).add_to(marker_cluster)

    # Urban Heat Island Mitigation
    green_spaces = [
        {'lat': lat + 0.01, 'lon': lon - 0.01, 'name': 'Urban Garden', 'icon': 'leaf'},
        {'lat': lat - 0.01, 'lon': lon + 0.01, 'name': 'Rooftop Green Space', 'icon': 'building'},
        {'lat': lat + 0.015, 'lon': lon + 0.015, 'name': 'Tree Planting Area', 'icon': 'tree'}
    ]
    for space in green_spaces:
        folium.Marker(
            [space['lat'], space['lon']],
            popup=space['name'],
            icon=folium.Icon(color='green', icon=space['icon'], prefix='fa')
        ).add_to(marker_cluster)

    # Air Pollution Solutions
    clean_initiatives = [
        {'lat': lat + 0.025, 'lon': lon - 0.025, 'name': 'Electric Vehicle Charging Station', 'icon': 'charging-station'},
        {'lat': lat - 0.025, 'lon': lon + 0.025, 'name': 'Public Transport Hub', 'icon': 'bus'},
        {'lat': lat + 0.035, 'lon': lon + 0.015, 'name': 'Clean Industry Zone', 'icon': 'industry'}
    ]
    for initiative in clean_initiatives:
        folium.Marker(
            [initiative['lat'], initiative['lon']],
            popup=initiative['name'],
            icon=folium.Icon(color='purple', icon=initiative['icon'], prefix='fa')
        ).add_to(marker_cluster)

    return map_

def get_nasa_satellite_data(lat, lon):
    # Simulated NASA Earth observation data (replace with actual API call)
    return {
        "vegetation_index": np.random.uniform(0, 1),
        "land_surface_temperature": np.random.uniform(20, 40),
        "precipitation": np.random.uniform(0, 100),
        "air_quality_index": np.random.randint(0, 500)
    }

def predict_future_trends(historical_data):
    # Simulated predictive modeling
    future_trends = {
        "air_quality": np.random.choice(["Improving", "Worsening", "Stable"]),
        "green_cover": np.random.choice(["Increasing", "Decreasing", "Stable"]),
        "urban_heat": np.random.choice(["Intensifying", "Reducing", "Stable"])
    }
    return future_trends

def calculate_biodiversity_index():
    # This would typically involve complex calculations based on species data
    # Here's a simplified version for demonstration
    species_count = {
        "Birds": 50,
        "Insects": 200,
        "Plants": 150,
        "Mammals": 20
    }
    total_species = sum(species_count.values())
    index = total_species / 1000  # Simplified index calculation
    return index, species_count

def analyze_green_space_accessibility(lat, lon):
    # This is a simplified version. In a real scenario, you'd use actual city data
    city = gpd.GeoDataFrame({'geometry': [Point(lon, lat).buffer(0.1)]})
    green_spaces = gpd.GeoDataFrame({
        'geometry': [Point(lon+0.02, lat+0.02).buffer(0.01), Point(lon-0.03, lat-0.01).buffer(0.015)]
    })
    
    accessibility = (green_spaces.area.sum() / city.area.sum()) * 100
    return accessibility

def predict_flood_risk(rainfall, elevation, proximity_to_water):
    # This is a simplified model. In a real scenario, you'd train this on historical data
    model = RandomForestClassifier()
    # Simulate training data
    X = [[50, 10, 5], [100, 5, 1], [75, 15, 3]]
    y = [0, 1, 1]  # 0: Low risk, 1: High risk
    model.fit(X, y)
    
    prediction = model.predict([[rainfall, elevation, proximity_to_water]])
    return "High" if prediction[0] == 1 else "Low"

def community_project_tracker():
    st.subheader("Community Project Tracker")
    projects = [
        {"name": "Green Roof Initiative", "progress": 65},
        {"name": "Bike Lane Expansion", "progress": 40},
        {"name": "Community Solar Project", "progress": 80}
    ]
    for project in projects:
        st.write(f"**{project['name']}**")
        st.progress(project['progress'] / 100)
        st.write(f"Progress: {project['progress']}%")

def generate_heat_island_data(lat, lon):
    x = np.linspace(lon-0.1, lon+0.1, 100)
    y = np.linspace(lat-0.1, lat+0.1, 100)
    xx, yy = np.meshgrid(x, y)
    zz = np.exp(-((xx-lon)**2 + (yy-lat)**2) / 0.01)
    return x, y, zz

def get_air_quality(lat, lon):
    api_key = "4a83da95401cd1052adc94d76f105dec"  # OpenWeatherMap API key
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if 'list' in data and len(data['list']) > 0 and 'main' in data['list'][0] and 'aqi' in data['list'][0]['main']:
            return data['list'][0]['main']['aqi']
        else:
            st.warning("Air quality data not available for this location.")
            return "N/A"
    except Exception as e:
        st.error(f"Error fetching air quality data: {e}")
        return "N/A"

def community_engagement_game():
    st.subheader("EcoChampion: Community Engagement Game")
    points = st.session_state.get('eco_points', 0)
    level = points // 100 + 1
    
    col1, col2 = st.columns(2)
    col1.metric("EcoPoints", points)
    col2.metric("Level", level)
    
    st.progress(points % 100 / 100)
    
    if st.button("Report a local environmental issue"):
        points += 10
        st.success("Thank you for your report! +10 EcoPoints")
    
    if st.button("Participate in community clean-up"):
        points += 50
        st.success("Great job participating! +50 EcoPoints")
    
    st.session_state['eco_points'] = points

# Streamlit app layout
st.set_page_config(page_title="Community Mapping and Urban Solutions", layout="wide")
st.title("🌍 Community Mapping and Urban Solutions")

# Add this at the beginning of your main function, after the title
st.markdown("""
Welcome to the Community Mapping and Urban Solutions Explorer! This tool helps you visualize and analyze urban data 
to support community-driven solutions for sustainable development.
""")

# Quick stats dashboard
col1, col2, col3, col4 = st.columns(4)
col1.metric("Population", "5.5M", "2.1%")
col2.metric("Green Cover", "20%", "-0.5%")
col3.metric("Air Quality Index", "153", "10")
col4.metric("Renewable Energy", "12%", "3%")

# Sidebar for searching a place and selecting features
location = st.selectbox("Select or enter your community location", 
                        ["Ahmedabad", "Mumbai", "Delhi", "Bangalore", "Chennai"])

if location != "Ahmedabad":
    st.warning("You've selected a different city. Some data may be simulated for demonstration purposes.")

show_water_solutions = st.sidebar.checkbox("Show Water Scarcity Solutions")
show_heat_mitigation = st.sidebar.checkbox("Show Urban Heat Island Mitigation")
show_air_solutions = st.sidebar.checkbox("Show Air Pollution Solutions")

# Fetch weather data
weather_data = get_weather_data(location)

if weather_data.get("cod") != 200:
    st.error("Location not found. Please enter a valid place name.")
else:
    # Extracting relevant data
    lat = weather_data["coord"]["lat"]
    lon = weather_data["coord"]["lon"]
    temperature = weather_data["main"]["temp"]
    weather_description = weather_data["weather"][0]["description"]
    humidity = weather_data["main"]["humidity"]
    pressure = weather_data["main"]["pressure"]
    wind_speed = weather_data["wind"]["speed"]
    rainfall = weather_data.get("rain", {}).get("1h", 0)  # Rainfall in last 1 hour, if available

    # put info in the session state
    st.session_state["weather_data"] = weather_data
    st.session_state["location"] = location

    # Creating the map
    map_ = create_map(lat, lon, location)

    # Display the map
    st_folium(map_, width=700, height=500)

    # Display weather details
    st.subheader(f"Weather details for {location.capitalize()}:")
    st.write(f"**🌡️ Temperature:** {temperature}°C")
    st.write(f"**🌤️ Weather:** {weather_description.capitalize()}")
    st.write(f"**💧 Humidity:** {humidity}%")
    st.write(f"**🔄 Pressure:** {pressure} hPa")
    st.write(f"**💨 Wind Speed:** {wind_speed} m/s")
    st.write(f"**🌧️ Rainfall (last 1 hour):** {rainfall} mm")

    # Community Challenges and Solutions
    st.header("Community Challenges and Solutions")

    # Water Scarcity
    st.subheader("🚰 Water Scarcity Solutions")
    st.write("Explore innovative water management solutions in your community:")
    water_solutions = pd.DataFrame({
        'Solution': ['Rainwater Harvesting', 'Wastewater Treatment', 'Efficient Irrigation'],
        'Impact': [80, 90, 70]
    })
    fig_water = px.bar(water_solutions, x='Solution', y='Impact', 
                       title='Potential Impact of Water Management Solutions')
    st.plotly_chart(fig_water)

    # Urban Heat Island Effect
    st.subheader("🌳 Urban Heat Island Mitigation")
    st.write("Green infrastructure to cool down urban areas:")
    heat_mitigation = pd.DataFrame({
        'Initiative': ['Urban Gardens', 'Rooftop Green Spaces', 'Tree Planting'],
        'Cooling Effect (°C)': [2.5, 3.0, 1.5]
    })
    fig_heat = px.bar(heat_mitigation, x='Initiative', y='Cooling Effect (°C)', 
                      title='Cooling Effect of Green Infrastructure')
    st.plotly_chart(fig_heat)

    # Air Pollution
    st.subheader("💨 Air Pollution Solutions")
    st.write("Initiatives to improve air quality:")
    air_solutions = pd.DataFrame({
        'Solution': ['Electric Vehicles', 'Public Transport', 'Clean Industries'],
        'Pollution Reduction (%)': [30, 25, 20]
    })
    fig_air = px.bar(air_solutions, x='Solution', y='Pollution Reduction (%)', 
                     title='Potential Air Pollution Reduction')
    st.plotly_chart(fig_air)

    # Community Engagement Section
    st.header("🤝 Community Engagement")
    st.write("""
        This application is designed to help you engage with your community and contribute to urban solutions:
    """)
    st.write("1. **Explore the Map**: Discover water management, heat mitigation, and air quality initiatives in your area.")
    st.write("2. **Contribute Data**: Use the drawing tools on the map to mark new green spaces or suggest locations for initiatives.")
    st.write("3. **Report Issues**: Help identify areas that need attention or improvement.")
    st.write("4. **Learn More**: Access educational resources about urban challenges and solutions.")

    # Feedback and Reporting
    st.subheader("📝 Community Feedback and Reporting")
    report_type = st.selectbox("What would you like to report or suggest?", 
                               ["", "Water Management Idea", "Green Space Suggestion", "Air Quality Concern", "Other"])
    if report_type:
        report_details = st.text_area(f"Please provide details about your {report_type.lower()}:")
        if st.button("Submit Report"):
            if report_details:
                st.success("Thank you for your input! Your suggestion will be reviewed and considered for implementation.")
            else:
                st.error("Please enter some details before submitting.")

    # Educational Resources
    st.subheader("📚 Educational Resources")
    st.write("Learn more about urban challenges and solutions:")
    st.write("- [Sustainable Water Management Practices](https://example.com/water-management)")
    st.write("- [Urban Heat Island Effect and Mitigation Strategies](https://example.com/heat-island)")
    st.write("- [Improving Urban Air Quality](https://example.com/air-quality)")
    st.write("- [Community-Driven Urban Planning](https://example.com/community-planning)")

    # Optionally, display the raw weather data
    with st.expander("See raw weather data"):
        st.json(weather_data)

    # Add this in your main function after creating the map
    nasa_data = get_nasa_satellite_data(lat, lon)
    fig = go.Figure(data=[
        go.Bar(name='NASA Earth Observations', 
               x=['Vegetation Index', 'Land Surface Temp (°C)', 'Precipitation (mm)', 'Air Quality Index'],
               y=[nasa_data['vegetation_index'], nasa_data['land_surface_temperature'], 
                  nasa_data['precipitation'], nasa_data['air_quality_index']],
               marker_color=['green', 'red', 'blue', 'purple'])
    ])
    fig.update_layout(title_text='NASA Earth Observations for ' + location, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

    # Predictive Insights
    st.header("Predictive Insights")
    future_trends = predict_future_trends(None)  # Pass historical data when available

    st.subheader(f"Projected Urban Trends for {location}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Future Air Quality", future_trends['air_quality'])
    col2.metric("Green Cover Trend", future_trends['green_cover'])
    col3.metric("Urban Heat Island Effect", future_trends['urban_heat'])

    st.subheader("Recommended Actions")
    if future_trends['air_quality'] == "Worsening":
        st.warning("Implement stricter emission controls and promote public transportation.")
    if future_trends['green_cover'] == "Decreasing":
        st.warning("Initiate large-scale tree planting programs and create more urban parks.")
    if future_trends['urban_heat'] == "Intensifying":
        st.warning("Increase green roof initiatives and use cool pavement technologies.")

    # Community Projects Voting
    st.subheader("Community Projects Voting")
    projects = [
        {"name": "Community Garden", "description": "Create a shared garden space for local residents.", "votes": 45},
        {"name": "Bike Lane Extension", "description": "Extend the bike lane network for safer cycling.", "votes": 62},
        {"name": "Solar Panel Initiative", "description": "Install solar panels on public buildings.", "votes": 38}
    ]
    for project in projects:
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"**{project['name']}**: {project['description']}")
        col2.write(f"Votes: {project['votes']}")
        if col3.button("Vote", key=project['name']):
            project['votes'] += 1
            st.experimental_rerun()

    # Urban Biodiversity Index
    bio_index, species_data = calculate_biodiversity_index()
    st.metric("Urban Biodiversity Index", f"{bio_index:.2f}")
    fig = px.pie(values=species_data.values(), names=species_data.keys(), title="Species Distribution")
    st.plotly_chart(fig)

    # Green Space Accessibility
    accessibility = analyze_green_space_accessibility(lat, lon)
    st.metric("Green Space Accessibility", f"{accessibility:.1f}%")

    # Sustainable Transportation Planner
    def sustainable_transport_planner():
        st.subheader("Sustainable Transportation Planner")
        start = st.text_input("Start Location")
        end = st.text_input("End Location")
        if st.button("Plan Route"):
            # Here you would integrate with a routing API
            st.success("Route planned! Estimated CO2 savings: 2.5 kg")
            # Display a dummy map (replace with actual route)
            m = folium.Map(location=[lat, lon], zoom_start=12)
            folium.PolyLine(locations=[[lat, lon], [lat+0.05, lon+0.05]], color="green", weight=2.5, opacity=1).add_to(m)
            folium_static(m)

    # In your main app:
    sustainable_transport_planner()

    # Predictive Flood Risk Model
    rainfall = st.slider("Average Annual Rainfall (mm)", 0, 200, 100)
    elevation = st.slider("Elevation above sea level (m)", 0, 50, 25)
    proximity = st.slider("Proximity to water bodies (km)", 0, 10, 5)

    risk = predict_flood_risk(rainfall, elevation, proximity)
    st.write(f"Predicted Flood Risk: **{risk}**")

    # Community Project Tracker
    community_project_tracker()

    # Urban Heat Island Visualization
    x, y, z = generate_heat_island_data(lat, lon)
    fig = go.Figure(data=[go.Surface(z=z, x=x, y=y, colorscale='Hot')])
    fig.update_layout(title='Urban Heat Island Effect', autosize=False,
                      width=800, height=600,
                      scene=dict(xaxis_title='Longitude', yaxis_title='Latitude', zaxis_title='Temperature'))
    st.plotly_chart(fig, use_container_width=True)

    # Real-time Air Quality Monitoring
    aqi = get_air_quality(lat, lon)
    if aqi != "N/A":
        st.metric("Real-time Air Quality Index", aqi, delta=None)
    else:
        st.write("Real-time Air Quality Index: Not available")

    # Community Engagement Game
    community_engagement_game()
