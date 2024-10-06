import streamlit as st
import folium
from streamlit_folium import st_folium

# Function to generate OpenWeatherMap Tile URL
def generate_tile_url(layer, api_key):
    return f"https://tile.openweathermap.org/map/{layer}/{{z}}/{{x}}/{{y}}.png?appid={api_key}"

# Streamlit app layout
st.set_page_config(page_title="Weather Maps", layout="wide")
st.title("🗺️ Weather Maps")

# Sidebar for selecting the weather map layer
st.sidebar.header("Select Weather Map Layer")
layer_options = {
    "Clouds": "clouds_new",
    "Precipitation": "precipitation_new",
    "Sea Level Pressure": "pressure_new",
    "Wind Speed": "wind_new",
    "Temperature": "temp_new",
}
selected_layer = st.sidebar.selectbox("Weather Layer", list(layer_options.keys()))

# Fetch API key from user or hardcode it
api_key = "325a9360036a3077bec1b55e67c4410b" # Replace with your OpenWeatherMap API key

# Generate the tile URL for the selected layer
tile_url = generate_tile_url(layer_options[selected_layer], api_key)

# Create a folium map centered over India with the selected weather layer
map_center = [20.5937, 78.9629]  # Centered over India
folium_map = folium.Map(location=map_center, zoom_start=5)

# Add the weather layer to the folium map
folium.TileLayer(tiles=tile_url, name=selected_layer, attr="OpenWeatherMap").add_to(folium_map)

# Display the map in Streamlit
st_folium(folium_map, width=800, height=600)

# Add a description of the selected layer
st.subheader(f"About the {selected_layer} Layer")
layer_descriptions = {
    "Clouds": "This layer shows the current cloud cover across the region.",
    "Precipitation": "This layer displays areas of precipitation, including rain and snow.",
    "Sea Level Pressure": "This layer indicates the atmospheric pressure at sea level.",
    "Wind Speed": "This layer illustrates the wind speed in meters per second.",
    "Temperature": "This layer shows the current temperature in Celsius.",
}
st.write(layer_descriptions[selected_layer])

# Style improvements
st.markdown("""
<style>
    .stButton button {
        background-color: #4682B4;
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
