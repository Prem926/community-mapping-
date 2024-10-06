import streamlit as st
import openai
import json

# OpenAI API key
openai.api_key = "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"  # Replace with your OpenAI API key


# Function to get safety tips based on weather
import openai

def get_safety_tips(weather_data , weather_description, temperature, rainfall, wind_speed , location):
    prompt = (
        f"You are a weather safety expert. A user has asked for safety tips based on the current weather conditions at {location}. "
        f"The current weather is described as '{weather_description}' with a temperature of {temperature}°C, "
        f"rainfall of {rainfall} mm, and wind speed of {wind_speed} m/s. "
        f"complete weather json data is <json start>{weather_data} <json end>"
        "Please provide three sections of advice: "
        "1. General Guidelines for this weather. "
        "2. Alerts or warnings people should be aware of. "
        "3. Specific Dangers to avoid in these conditions."
        "Return the advice in the json format: "
        "   'General Guidelines': [guidelines], "
        "   'Alerts': [alerts], "
        "   'Dangers': [dangers]."
    )

    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.7,
        )
        
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred while calling the OpenAI API: {str(e)}")
        return None

# Streamlit app layout
st.set_page_config(page_title="Safety Tips", layout="wide")
st.title("🚨 Safety Tips Based on Current Weather")

# Weather details from session state (shared across pages)
if "weather_data" in st.session_state:
    weather_data = st.session_state["weather_data"]
    weather_description = weather_data["weather"][0]["description"]
    temperature = weather_data["main"]["temp"]
    rainfall = weather_data.get("rain", {}).get("1h", 0)
    wind_speed = weather_data["wind"]["speed"]
    
    location = st.session_state["location"]

    # Get safety tips
    safety_tips = get_safety_tips(weather_data , weather_description, temperature, rainfall, wind_speed , location)

    # Display the safety tips
    st.subheader(f"🌤️ Safety Tips for {weather_description.capitalize()} Conditions at {location.capitalize()}")
    
    print(safety_tips)
    
    # trim the response to get only the json part
    safety_tips = safety_tips[safety_tips.find("{"):safety_tips.rfind("}")+1]   
    
    
    #convert string to json
    safety_tips = json.loads(safety_tips)
    
    st.markdown("### 📝 General Guidelines")
    for tip in safety_tips["General Guidelines"]:
        st.write(tip.strip())

    st.markdown("### ⚠️ Alerts")
    for alert in safety_tips["Alerts"]:
        st.write(alert.strip())

    st.markdown("### 🚨 Dangers")
    for danger in safety_tips["Dangers"]:
        st.write(danger.strip())
        
        
    
else:
    st.error("Please go back to the main page and enter a location to get weather details first.")

# Style improvements
st.markdown("""
<style>
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        border-radius: 10px;
        padding: 10px 20px;
    }
    .stTextInput input {
        border-radius: 10px;
        padding: 10px;
    }
    h1, h2, h3 {
        color: #4CAF50;
    }
    h3 {
        margin-top: 20px;
    }
    .stMarkdown {
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)
