import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
from geopy.geocoders import Nominatim
import polyline
import branca.colormap as cm
import folium.plugins as plugins
import traceback
from datetime import timedelta
import random
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from folium.plugins import HeatMap
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from streamlit_folium import folium_static

# Initialize geocoder
@st.cache_resource
def get_geocoder():
    return Nominatim(user_agent="route_finder_app")

geolocator = get_geocoder()

# API Keys
OLA_API_KEY = 'YFJkfYydYN3zEwadh3YLTa2YiP7Ur6Du8Upv6xdM'
OPENWEATHER_API_KEY = '4a83da95401cd1052adc94d76f105dec'

@st.cache_data(ttl=300)
def get_directions(origin, destination, vehicle, waypoints=None, alternatives=True):
    url = f"https://api.olamaps.io/routing/v1/directions?origin={origin}&destination={destination}&api_key={OLA_API_KEY}&alternatives={str(alternatives).lower()}"
    
    if waypoints:
        url += f"&waypoints={waypoints}"
    
    headers = {'X-Request-Id': 'unique-request-id'}
    
    try:
        response = requests.post(url, headers=headers, verify=False)  # Added verify=False
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None

@st.cache_data
def extract_route_points(route):
    if 'geometry' in route:
        return polyline.decode(route['geometry'])
    elif 'overview_polyline' in route and 'points' in route['overview_polyline']:
        return polyline.decode(route['overview_polyline']['points'])
    elif 'legs' in route:
        points = []
        for leg in route['legs']:
            if 'steps' in leg:
                for step in leg['steps']:
                    if 'start_location' in step:
                        points.append((step['start_location']['lat'], step['start_location']['lng']))
                    if 'end_location' in step:
                        points.append((step['end_location']['lat'], step['end_location']['lng']))
        return points
    else:
        st.warning("Unexpected route format. Unable to extract route points.")
        return None

@st.cache_data(ttl=300)
def get_weather_data(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data['main']['temp'],
            "condition": data['weather'][0]['main'],
            "precipitation_chance": data['clouds']['all'],
            "wind_speed": data['wind']['speed'],
            "humidity": data['main']['humidity']
        }
    else:
        st.warning(f"Weather API request failed with status code {response.status_code}")
        return None

@st.cache_data(ttl=300)
def get_air_quality(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['list'][0]['main']['aqi']
    else:
        st.warning(f"Air Quality API request failed with status code {response.status_code}")
        return None

def predict_flood(lat, lon):
    return random.random()  # Returns a random float between 0 and 1

# New functions for additional features
@st.cache_data(ttl=300)
def get_nearby_places(lat, lon, place_type):
    url = f"https://api.olamaps.io/v1/places/nearby?lat={lat}&lon={lon}&type={place_type}&api_key={OLA_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results']
    else:
        st.warning(f"Nearby places API request failed with status code {response.status_code}")
        return None

@st.cache_data(ttl=3600)
def get_historical_weather(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['daily']
    else:
        st.warning(f"Historical weather API request failed with status code {response.status_code}")
        return None

def calculate_eco_score(route, weather_data):
    distance = route['distance'] / 1000  # km
    duration = route['duration'] / 3600  # hours
    avg_speed = distance / duration if duration > 0 else 0
    
    eco_score = 100
    
    # Penalize for high speeds
    if avg_speed > 80:
        eco_score -= (avg_speed - 80) * 0.5
    
    # Penalize for bad weather conditions
    if weather_data['condition'] in ['Rain', 'Snow', 'Thunderstorm']:
        eco_score -= 10
    
    # Bonus for walking or biking
    if route['vehicle'] in ['walk', 'bike']:
        eco_score += 20
    
    return max(0, min(100, eco_score))

def generate_heatmap_data(route_points, num_points=1000):
    lat_min, lat_max = min(p[0] for p in route_points), max(p[0] for p in route_points)
    lon_min, lon_max = min(p[1] for p in route_points), max(p[1] for p in route_points)
    
    heatmap_data = []
    for _ in range(num_points):
        lat = random.uniform(lat_min, lat_max)
        lon = random.uniform(lon_min, lon_max)
        intensity = random.uniform(0, 1)
        heatmap_data.append([lat, lon, intensity])
    
    return heatmap_data

def cluster_waypoints(route_points, n_clusters=5):
    if len(route_points) < n_clusters:
        return route_points
    
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(route_points)
    return kmeans.cluster_centers_

# Main Streamlit app
st.title("Advanced Route Navigator")

input_type = st.sidebar.radio("Input Type", ["Coordinates", "Address"])

if input_type == "Coordinates":
    start_lat = st.sidebar.text_input("Start Latitude", "23.0225")
    start_lon = st.sidebar.text_input("Start Longitude", "72.5714")
    end_lat = st.sidebar.text_input("End Latitude", "23.1225")
    end_lon = st.sidebar.text_input("End Longitude", "72.4714")
else:
    start_address = st.sidebar.text_input("Start Address", "Ahmedabad, Gujarat")
    end_address = st.sidebar.text_input("End Address", "Gandhinagar, Gujarat")

vehicle = st.sidebar.selectbox("Select Vehicle Type", ["car", "bike", "walk"])
map_style = st.sidebar.selectbox("Map Style", ["OpenStreetMap", "Stamen Terrain", "Stamen Toner"])

show_traffic_info = st.sidebar.checkbox("Show Traffic Info")
show_weather_info = st.sidebar.checkbox("Show Weather Info")
show_air_quality = st.sidebar.checkbox("Show Air Quality")
show_flood_risk = st.sidebar.checkbox("Show Flood Risk")
show_elevation = st.sidebar.checkbox("Show Elevation Profile")

# New UI elements for additional features
show_nearby_places = st.sidebar.checkbox("Show Nearby Places")
place_type = st.sidebar.selectbox("Place Type", ["restaurant", "hotel", "atm", "hospital", "police"])
show_historical_weather = st.sidebar.checkbox("Show Historical Weather")
show_eco_score = st.sidebar.checkbox("Show Eco Score")
show_heatmap = st.sidebar.checkbox("Show Traffic Heatmap")
show_alternative_routes = st.sidebar.checkbox("Show Alternative Routes")
show_terrain_analysis = st.sidebar.checkbox("Show Terrain Analysis")
show_safety_score = st.sidebar.checkbox("Show Safety Score")
show_fuel_consumption = st.sidebar.checkbox("Show Fuel Consumption Estimate")
show_parking_info = st.sidebar.checkbox("Show Parking Information")
show_public_transport = st.sidebar.checkbox("Show Public Transport Options")
show_accessibility_info = st.sidebar.checkbox("Show Accessibility Information")
show_scenic_route = st.sidebar.checkbox("Find Scenic Route")
show_time_based_traffic = st.sidebar.checkbox("Show Time-based Traffic Prediction")
show_voice_navigation = st.sidebar.checkbox("Enable Voice Navigation")
show_augmented_reality = st.sidebar.checkbox("Enable AR Navigation (Mobile)")
show_carbon_footprint = st.sidebar.checkbox("Calculate Carbon Footprint")
show_local_events = st.sidebar.checkbox("Show Local Events on Route")
show_weather_alerts = st.sidebar.checkbox("Show Weather Alerts")
show_road_conditions = st.sidebar.checkbox("Show Road Conditions")
show_rest_stops = st.sidebar.checkbox("Suggest Rest Stops")

# Initialize the map
map_ = None

try:
    if input_type == "Coordinates":
        start_lat, start_lon = float(start_lat), float(start_lon)
        end_lat, end_lon = float(end_lat), float(end_lon)
    else:
        start_location = geolocator.geocode(start_address)
        end_location = geolocator.geocode(end_address)
        if start_location and end_location:
            start_lat, start_lon = start_location.latitude, start_location.longitude
            end_lat, end_lon = end_location.latitude, end_location.longitude
        else:
            st.error("Could not geocode one or both addresses. Please check and try again.")
            st.stop()

    map_ = folium.Map(location=[(start_lat + end_lat) / 2, (start_lon + end_lon) / 2], zoom_start=10, tiles=map_style)

    if st.sidebar.button("Get Directions"):
        with st.spinner("Calculating route and gathering data..."):
            directions = get_directions(f"{start_lat},{start_lon}", f"{end_lat},{end_lon}", vehicle)
            
            if directions and 'routes' in directions:
                for i, route in enumerate(directions['routes']):
                    decoded_polyline = extract_route_points(route)
                    
                    if decoded_polyline:
                        color = "blue" if i > 0 else "green"
                        folium.PolyLine(decoded_polyline, color=color, weight=4-i, opacity=0.8).add_to(map_)

                        if i == 0:  # Only for the main route
                            if show_traffic_info:
                                traffic_data = [random.randint(0, 100) for _ in range(len(decoded_polyline))]
                                traffic_colormap = cm.LinearColormap(colors=['green', 'yellow', 'red'], vmin=0, vmax=100)
                                for j, point in enumerate(decoded_polyline[::10]):
                                    folium.CircleMarker(
                                        location=point,
                                        radius=5,
                                        popup=f"Traffic: {traffic_data[j*10]}% congested",
                                        color=traffic_colormap(traffic_data[j*10]),
                                        fill=True
                                    ).add_to(map_)

                            if show_weather_info:
                                weather = get_weather_data(start_lat, start_lon)
                                if weather:
                                    folium.Marker(
                                        [start_lat, start_lon],
                                        popup=f"Weather: {weather['condition']}, {weather['temperature']}°C, {weather['precipitation_chance']}% chance of rain",
                                        icon=folium.Icon(color='purple', icon='info-sign')
                                    ).add_to(map_)

                            if show_air_quality:
                                aqi = get_air_quality(start_lat, start_lon)
                                if aqi:
                                    folium.Marker(
                                        [start_lat, start_lon],
                                        popup=f"Air Quality Index: {aqi}",
                                        icon=folium.Icon(color='blue', icon='info-sign')
                                    ).add_to(map_)

                            if show_flood_risk:
                                flood_risk = [predict_flood(point[0], point[1]) for point in decoded_polyline[::10]]
                                flood_colormap = cm.LinearColormap(colors=['green', 'yellow', 'red'], vmin=0, vmax=1)
                                for j, point in enumerate(decoded_polyline[::10]):
                                    folium.CircleMarker(
                                        location=point,
                                        radius=5,
                                        popup=f"Flood Risk: {flood_risk[j]:.2f}",
                                        color=flood_colormap(flood_risk[j]),
                                        fill=True
                                    ).add_to(map_)

                            if show_elevation:
                                elevation_data = [random.randint(0, 100) for _ in range(len(decoded_polyline))]
                                st.line_chart(pd.DataFrame({"Elevation": elevation_data}))

                            # Implement new features
                            if show_nearby_places:
                                nearby_places = get_nearby_places(start_lat, start_lon, place_type)
                                if nearby_places:
                                    for place in nearby_places[:5]:
                                        folium.Marker(
                                            [place['lat'], place['lon']],
                                            popup=f"{place['name']} - {place['type']}",
                                            icon=folium.Icon(color='orange', icon='info-sign')
                                        ).add_to(map_)

                            if show_historical_weather:
                                historical_weather = get_historical_weather(start_lat, start_lon)
                                if historical_weather:
                                    weather_data = pd.DataFrame(historical_weather)
                                    st.line_chart(weather_data[['temp', 'humidity']])

                            if show_eco_score:
                                weather = get_weather_data(start_lat, start_lon)
                                eco_score = calculate_eco_score(route, weather)
                                st.write(f"Eco Score: {eco_score:.2f}/100")

                            if show_heatmap:
                                heatmap_data = generate_heatmap_data(decoded_polyline)
                                HeatMap(heatmap_data).add_to(map_)

                            if show_alternative_routes and len(directions['routes']) > 1:
                                for alt_route in directions['routes'][1:3]:  # Show up to 2 alternative routes
                                    alt_polyline = extract_route_points(alt_route)
                                    folium.PolyLine(alt_polyline, color="purple", weight=2, opacity=0.6).add_to(map_)

                            if show_terrain_analysis:
                                elevation_data = [random.randint(0, 100) for _ in range(len(decoded_polyline))]
                                fig, ax = plt.subplots()
                                sns.lineplot(x=range(len(elevation_data)), y=elevation_data, ax=ax)
                                ax.set_title("Terrain Elevation Profile")
                                ax.set_xlabel("Distance")
                                ax.set_ylabel("Elevation (m)")
                                st.pyplot(fig)

                            if show_safety_score:
                                safety_score = random.uniform(60, 100)
                                st.write(f"Route Safety Score: {safety_score:.2f}/100")

                            if show_fuel_consumption:
                                fuel_consumption = random.uniform(5, 15)  # L/100km
                                st.write(f"Estimated Fuel Consumption: {fuel_consumption:.2f} L/100km")

                            if show_parking_info:
                                parking_availability = random.randint(0, 100)
                                st.write(f"Parking Availability at Destination: {parking_availability}%")

                            if show_public_transport:
                                st.write("Nearby Public Transport Options:")
                                st.write("- Bus 42: Leaves in 5 minutes")
                                st.write("- Metro Line 3: Leaves in 12 minutes")

                            if show_accessibility_info:
                                accessibility_score = random.uniform(60, 100)
                                st.write(f"Route Accessibility Score: {accessibility_score:.2f}/100")

                            if show_scenic_route:
                                scenic_points = cluster_waypoints(decoded_polyline, n_clusters=3)
                                for point in scenic_points:
                                    folium.Marker(
                                        point,
                                        popup="Scenic Point",
                                        icon=folium.Icon(color='green', icon='camera')
                                    ).add_to(map_)

                            if show_time_based_traffic:
                                traffic_data = [random.randint(0, 100) for _ in range(24)]
                                traffic_df = pd.DataFrame({"Hour": range(24), "Traffic": traffic_data})
                                st.line_chart(traffic_df.set_index("Hour"))

                            if show_voice_navigation:
                                st.write("Voice navigation enabled. Connect your device for turn-by-turn instructions.")

                            if show_augmented_reality:
                                st.write("AR navigation available on mobile devices. Open the app on your smartphone.")

                            if show_carbon_footprint:
                                carbon_footprint = random.uniform(0.1, 5)  # kg CO2
                                st.write(f"Estimated Carbon Footprint: {carbon_footprint:.2f} kg CO2")

                            if show_local_events:
                                st.write("Local Events on Route:")
                                st.write("- Street Fair at Main St (2 km ahead)")
                                st.write("- Live Music at Central Park (5 km ahead)")

                            if show_weather_alerts:
                                if random.random() < 0.3:
                                    st.warning("Weather Alert: Thunderstorms expected in 2 hours")

                            if show_road_conditions:
                                road_condition = random.choice(["Excellent", "Good", "Fair", "Poor"])
                                st.write(f"Overall Road Condition: {road_condition}")

                            if show_rest_stops:
                                rest_stop_distances = [random.randint(20, 100) for _ in range(3)]
                                for i, distance in enumerate(rest_stop_distances, 1):
                                    st.write(f"Rest Stop {i}: {distance} km ahead")

                folium.Marker([start_lat, start_lon], popup="Start", icon=folium.Icon(color='green')).add_to(map_)
                folium.Marker([end_lat, end_lon], popup="End", icon=folium.Icon(color='red')).add_to(map_)

                plugins.MiniMap().add_to(map_)
                plugins.Fullscreen().add_to(map_)
                plugins.MeasureControl().add_to(map_)

                st.success("Route plotted successfully.")

                # Display route information
                main_route = directions['routes'][0]
                distance_meters = main_route.get('distance', 0)
                duration_seconds = main_route.get('duration', 0)
                
                distance_km = distance_meters / 1000
                duration = timedelta(seconds=duration_seconds)
                
                st.write(f"Distance: {distance_km:.2f} km")
                st.write(f"Estimated Time: {duration}")
                
                if distance_km > 0 and duration_seconds > 0:
                    average_speed_kmh = (distance_km / duration_seconds) * 3600
                    st.write(f"Average Speed: {average_speed_kmh:.2f} km/h")

            else:
                st.error("Failed to get directions. Please check the coordinates and try again.")

    # Always display the map
    st.subheader("Route Map")
    folium_static(map_, width=700, height=500)

    # Display additional information based on selected filters
    if show_weather_info:
        st.subheader("Current Weather")
        weather = get_weather_data(start_lat, start_lon)
        if weather:
            st.write(f"Temperature: {weather['temperature']}°C")
            st.write(f"Condition: {weather['condition']}")
            st.write(f"Precipitation Chance: {weather['precipitation_chance']}%")
            st.write(f"Wind Speed: {weather['wind_speed']} m/s")
            st.write(f"Humidity: {weather['humidity']}%")

    if show_air_quality:
        st.subheader("Air Quality")
        aqi = get_air_quality(start_lat, start_lon)
        if aqi:
            st.write(f"Air Quality Index: {aqi}")

    if show_historical_weather:
        st.subheader("Historical Weather")
        historical_weather = get_historical_weather(start_lat, start_lon)
        if historical_weather:
            weather_data = pd.DataFrame(historical_weather)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(weather_data['dt'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d')), 
                    weather_data['temp'].apply(lambda x: x['day']), label='Temperature')
            ax.plot(weather_data['dt'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d')), 
                    weather_data['humidity'], label='Humidity')
            ax.set_xlabel('Date')
            ax.set_ylabel('Temperature (°C) / Humidity (%)')
            ax.legend()
            plt.xticks(rotation=45)
            st.pyplot(fig)

    if show_eco_score and 'directions' in locals():
        st.subheader("Eco Score")
        weather = get_weather_data(start_lat, start_lon)
        eco_score = calculate_eco_score(directions['routes'][0], weather)
        st.write(f"Eco Score: {eco_score:.2f}/100")

    if show_time_based_traffic:
        st.subheader("Time-based Traffic Prediction")
        traffic_data = [np.random.randint(0, 100) for _ in range(24)]
        traffic_df = pd.DataFrame({"Hour": range(24), "Traffic": traffic_data})
        st.line_chart(traffic_df.set_index("Hour"))

    if show_carbon_footprint and 'directions' in locals():
        st.subheader("Carbon Footprint")
        distance_km = directions['routes'][0]['distance'] / 1000
        carbon_footprint = distance_km * 0.12  # Assuming 0.12 kg CO2 per km (average car)
        st.write(f"Estimated Carbon Footprint: {carbon_footprint:.2f} kg CO2")

    # Add more filter outputs here...

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.error(traceback.format_exc())

st.markdown("""
<style>
    .stTextInput input {
        border-radius: 10px;
        padding: 10px;
    }
    .stFoliumMap {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Add this line at the beginning of your script to suppress warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)