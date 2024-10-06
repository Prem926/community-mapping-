import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def calculate_parameters(vegetation, construction, barren):    
    # Infiltration rate calculation using empirical modifications
    base_infiltration_rate = 0.1  # Base value in m/hour
    vegetation_modifier = max(0.0, 0.004 * vegetation)  # Prevent negative effect
    construction_modifier = max(0.0, 0.003 * (100 - construction))  # Reduce infiltration as construction increases
    infiltration_rate = base_infiltration_rate + vegetation_modifier - construction_modifier
    
    # Drainage capacity: Affected by construction and vegetation
    base_drainage_capacity = 20  # Base drainage capacity in cubic meters per hour
    vegetation_impact = max(0.0, 3 * vegetation / 100)  # Vegetation can only improve drainage
    construction_impact = max(0.0, 2 * construction / 100)  # Construction's impact is negative
    drainage_capacity = base_drainage_capacity + vegetation_impact - construction_impact
    
    # Evaporation rate: Impacted by the barren land and vegetation
    base_evaporation_rate = 0.01  # Base evaporation rate in cubic meters per hour per square meter
    vegetation_effect = max(0.0, 0.0005 * vegetation)  # Vegetation slightly increases evaporation
    barren_effect = max(0.0, 0.001 * barren)  # Barren land increases evaporation rate
    evaporation_rate = base_evaporation_rate + vegetation_effect + barren_effect
    
    return max(0.0, infiltration_rate), max(0.0, drainage_capacity), max(0.0, evaporation_rate)


def plot_results(flood_time, drainage_time, infiltration_rate, drainage_capacity, evaporation_rate):
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))
    
    # Bar chart for times
    axs[0].bar(['Flood Time', 'Drainage Time'], [flood_time, drainage_time], color=['blue', 'red'])
    axs[0].set_title('Flood and Drainage Times')
    axs[0].set_ylabel('Time (hours)')

    # Line plot for rates
    parameters = ['Infiltration Rate', 'Drainage Capacity', 'Evaporation Rate']
    values = [infiltration_rate, drainage_capacity/100, evaporation_rate]
    for i, v in enumerate(values):
        axs[ 1].text(i, v + 0.01, str(f"{v:.2f}"), color='black', ha='right')
    axs[ 1].plot(parameters, values, marker='o' )
    axs[ 1].set_title('Hydraulic Parameters')
    
    st.pyplot(fig)

def main():
    st.title("Urban Flooding What-If Simulator")

    # Sidebar for input parameters
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        vegetation = st.number_input('Vegetation (%)', min_value=0, max_value=100, value=30, step=1)
    with col2:
        construction = st.number_input('Construction (%)', min_value=0, max_value=100, value=30, step=1)
    with col3:
        barren = st.number_input('Barren Land (%)', min_value=0, max_value=100, value=40, step=1)

    # Ensuring the sum remains 100
    total = vegetation + construction + barren
    if total != 100:
        st.sidebar.error("Total percentage must equal 100%")
        return

    if st.sidebar.button("Simulate"):
        area = 10000  # Fixed area for simulations
        depth = 0.3   # Fixed flooding depth
        rainfall_intensity = 550  # Assume a fixed moderate rainfall for simplicity
        
        infiltration_rate, drainage_capacity, evaporation_rate = calculate_parameters(vegetation, construction, barren)
        flood_volume = area * depth
        flood_time = flood_volume / (rainfall_intensity * infiltration_rate)
        drainage_time = flood_volume / (drainage_capacity + (evaporation_rate * area))
        
        plot_results(flood_time, drainage_time, infiltration_rate, drainage_capacity, evaporation_rate)

if __name__ == "__main__":
    main()
