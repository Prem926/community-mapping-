import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from folium.plugins import MarkerCluster, HeatMap, Draw
import random
import pandas as pd
import plotly.express as px

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

# Streamlit app layout
st.set_page_config(page_title="Community Mapping and Urban Solutions", layout="wide")
st.title("🌍 Community Mapping and Urban Solutions")

# Sidebar for searching a place and selecting features
location = st.sidebar.text_input("Enter a place name", "Ahmedabad")
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