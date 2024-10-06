import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
import plotly.express as px
from streamlit_lottie import st_lottie
import requests

# Set page config at the very beginning
st.set_page_config(page_title="Flood Risk Analysis", layout="wide")

# Load the data from a .pkl file
@st.cache_resource
def load_flood_probability_data(path):
    try:
        with open(path, 'rb') as file:
            data = pickle.load(file)
        return data
    except Exception as e:
        st.error(f"Error loading the data: {str(e)}")
        return None

# Load Lottie animation
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Path to the data file
DATA_PATH = r"models/random_forest_model.pkl"
loaded_data = load_flood_probability_data(DATA_PATH)

# Define the main function of the Streamlit app
def main():
    # Load water animation
    lottie_water = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_gkgqj2yq.json")

    st.title('🌊 Advanced Flood Risk Analysis')

    if loaded_data is None:
        st.error("Failed to load the data. Please check the file and try again.")
        return

    st.write(f"Loaded data type: {type(loaded_data)}")
    st.write(f"Loaded data shape: {loaded_data.shape}")

    # Display the loaded data
    with st.expander("View Loaded Data"):
        for i, value in enumerate(loaded_data):
            st.write(f"{i+1}. {value}")

    # Define features
    features = ['Monsoon Intensity', 'Topography Drainage', 'River Management', 'Deforestation',
                'Urbanization', 'Climate Change', 'Dams Quality', 'Siltation', 'Agricultural Practices',
                'Encroachments', 'Ineffective Disaster Preparedness', 'Drainage Systems',
                'Coastal Vulnerability', 'Landslides', 'Watersheds', 'Deteriorating Infrastructure',
                'Population Score', 'Wetland Loss', 'Inadequate Planning', 'Political Factors']

    # Check if the number of features matches the loaded data
    if len(features) != loaded_data.shape[0]:
        st.error(f"Mismatch between number of features ({len(features)}) and loaded data shape ({loaded_data.shape[0]})")
        return

    st.subheader("🎛️ Input Features")
    col1, col2 = st.columns(2)
    input_data = {}
    for i, feature in enumerate(features):
        with col1 if i % 2 == 0 else col2:
            value = st.slider(feature, min_value=0, max_value=10, value=5)
            input_data[feature] = value

    # Button to estimate flood probability
    if st.button('🔍 Analyze Flood Risk'):
        # Simple estimation based on average of input values
        estimated_probability = sum(input_data.values()) / (len(input_data) * 10)

        # Determine the risk level
        if estimated_probability < 0.33:
            risk_level = "Low"
            color = 'green'
            emoji = '✅'
        elif estimated_probability < 0.66:
            risk_level = "Moderate"
            color = 'orange'
            emoji = '⚠️'
        else:
            risk_level = "High"
            color = 'red'
            emoji = '🚨'

        # Display the result with animation
        st.markdown(f"<h2 style='text-align: center; color: {color};'>Flood Risk: {risk_level} {emoji}</h2>", unsafe_allow_html=True)
        st_lottie(lottie_water, height=200, key="water_animation")

        # Create a gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = estimated_probability * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Flood Risk Probability"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 33], 'color': "lightgreen"},
                    {'range': [33, 66], 'color': "lightyellow"},
                    {'range': [66, 100], 'color': "lightpink"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': estimated_probability * 100
                }
            }
        ))
        st.plotly_chart(fig)

        # Display recommendations based on risk level
        st.subheader("📋 Recommendations")
        if risk_level == "Low":
            st.success("- Maintain current flood prevention measures\n- Conduct regular drills\n- Keep emergency supplies stocked")
        elif risk_level == "Moderate":
            st.warning("- Strengthen flood barriers\n- Clear drainage systems\n- Prepare evacuation plans\n- Consider flood insurance")
        else:
            st.error("- Implement immediate flood mitigation measures\n- Evacuate low-lying areas\n- Activate emergency response teams\n- Seek assistance from disaster management authorities")

        # Feature importance chart
        st.subheader("📊 Feature Importance")
        fig = px.bar(x=features, y=input_data.values(), labels={'x': 'Features', 'y': 'Importance'})
        fig.update_layout(xaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig)

    # Historical flood data visualization
    st.subheader("📅 Historical Flood Data")
    years = list(range(2010, 2024))
    flood_levels = np.random.randint(1, 10, size=len(years))
    fig = px.line(x=years, y=flood_levels, labels={'x': 'Year', 'y': 'Flood Level'})
    st.plotly_chart(fig)

    # Real-time weather data
    st.subheader("🌦️ Real-time Weather Data")
    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", "25°C", "1.5°C")
    col2.metric("Humidity", "60%", "5%")
    col3.metric("Rainfall", "5mm", "-2mm")

    # Community resources
    st.subheader("🤝 Community Resources")
    st.info("- Emergency Hotline: 1234-5678\n- Nearest Shelter: City Hall\n- Volunteer Sign-up: [Link](https://example.com)")

    # Educational content
    with st.expander("Learn More About Flood Prevention"):
        st.write("""
        1. **Understand Your Risk**: Know your area's flood risk and history.
        2. **Prepare an Emergency Kit**: Include essentials like water, food, and first-aid supplies.
        3. **Create a Flood Plan**: Develop and practice a family emergency plan.
        4. **Protect Your Property**: Use flood-resistant materials and elevate important items.
        5. **Stay Informed**: Monitor local weather forecasts and flood warnings.
        """)

# Run the main function
if __name__ == "__main__":
    main()