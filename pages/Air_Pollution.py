import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import pandas as pd
import plotly.express as px

# Hardcoded API key (not recommended for production)
API_KEY = "4a83da95401cd1052adc94d76f105dec"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to get air pollution data with retry and fallback
def create_session_with_retries(retries=5, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_air_pollution_data(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    
    session = create_session_with_retries()
    
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to air pollution API: {str(e)}")
        st.error(f"Failed to connect to air pollution API. Please try again later.")
        return None

# Function to get weather data with retry and fallback
def get_weather_data(location):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": location,
        "appid": API_KEY,
        "units": "metric"
    }
    
    session = create_session_with_retries()
    
    try:
        response = session.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching weather data: {e}")
        return None

# Fallback function for weather data
def get_fallback_weather_data(location):
    return {
        "cod": 200,
        "name": location,
        "coord": {"lat": 0, "lon": 0},
        "main": {"temp": 25, "humidity": 60},
        "weather": [{"description": "clear sky"}]
    }

# Fallback function for air pollution data
def get_fallback_air_pollution_data():
    return {
        "list": [{
            "main": {"aqi": 2},
            "components": {
                "co": 300.5,
                "no": 5.2,
                "no2": 22.1,
                "o3": 55.3,
                "so2": 10.1,
                "pm2_5": 20.5,
                "pm10": 30.2,
                "nh3": 2.1
            }
        }]
    }

# Streamlit app layout
st.set_page_config(page_title="Air Pollution Data", layout="wide")
st.title("🌍 Air Pollution Data")

# Sidebar for searching a place
location = st.sidebar.text_input("Enter a place name", "Delhi")

# Fetch weather data to get coordinates
weather_data = get_weather_data(location)

if weather_data is None:
    st.error("Unable to fetch weather data. Please check your internet connection and try again.")
elif weather_data.get("cod") != 200:
    st.error(f"Location not found. Please enter a valid place name. Error: {weather_data.get('message', 'Unknown error')}")
else:
    # Extract coordinates
    lat = weather_data["coord"]["lat"]
    lon = weather_data["coord"]["lon"]
    
    # Fetch air pollution data
    air_pollution_data = get_air_pollution_data(lat, lon)
    
    if air_pollution_data is None:
        st.error("Unable to fetch air pollution data. Please check your internet connection and try again.")
    elif "list" in air_pollution_data:
        air_quality = air_pollution_data["list"][0]["main"]
        components = air_pollution_data["list"][0]["components"]

        # Display air quality index
        st.subheader(f"Air Quality Index (AQI) for {location.capitalize()}:")
        aqi = air_quality["aqi"]
        st.write(f"**AQI Level:** {aqi}")
        
        # AQI Conditional Coloring
        if aqi == 1:
            aqi_description = "Good"
            aqi_color = "green"
        elif aqi == 2:
            aqi_description = "Fair"
            aqi_color = "yellow"
        elif aqi == 3:
            aqi_description = "Moderate"
            aqi_color = "orange"
        elif aqi == 4:
            aqi_description = "Poor"
            aqi_color = "red"
        else:
            aqi_description = "Very Poor"
            aqi_color = "purple"

        st.markdown(f"<h2 style='color:{aqi_color}'>{aqi_description}</h2>", unsafe_allow_html=True)

        # Display air pollutants data
        st.subheader("Air Pollutant Levels (μg/m³):")
        df_pollutants = pd.DataFrame.from_dict(components, orient='index', columns=["Concentration"])
        df_pollutants.reset_index(inplace=True)
        df_pollutants.rename(columns={"index": "Pollutant"}, inplace=True)

        def pollutant_color(val):
            if val > 100:
                color = 'red'
            elif val > 50:
                color = 'orange'
            elif val > 25:
                color = 'yellow'
            else:
                color = 'green'
            return f'background-color: {color}'

        styled_pollutants = df_pollutants.style.applymap(pollutant_color, subset=["Concentration"])
        st.dataframe(styled_pollutants, height=300)

        # Visualization of pollutants using a bar chart
        fig = px.bar(df_pollutants, x="Pollutant", y="Concentration",
                     title="Pollutant Concentration Levels",
                     labels={"Concentration": "Concentration (μg/m³)"},
                     color="Concentration",
                     color_continuous_scale=["green", "yellow", "orange", "red"])

        fig.update_layout(
            font=dict(size=12),
            plot_bgcolor='white',
            xaxis_title="Pollutant",
            yaxis_title="Concentration (μg/m³)"
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Air pollution data is currently unavailable for this location.")

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

def main():
    st.title("Air Pollution Dashboard")
    
    location = st.text_input("Enter a city name:", "London")
    
    if st.button("Get Air Pollution Data"):
        weather_data = get_weather_data(location)
        
        if weather_data:
            # Process and display the data
            # ... (your existing code to handle the data)
            st.write(weather_data)  # For debugging, remove in production

if __name__ == "__main__":
    main()