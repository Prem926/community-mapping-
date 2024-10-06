import streamlit as st
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

# Set the title of the app
st.title('City Road Network Visualizer')

# Add sidebar for city input
city = st.sidebar.text_input('Enter a city name', 'Ahmedabad')

# Function to plot the road network
def plot_road_network(city):
    # Use the osmnx library to get the graph
    G = ox.graph_from_place(city, network_type='drive')
    fig, ax = ox.plot_graph(ox.project_graph(G), show=False, close=False)
    return fig

if city:
    # Display the graph
    st.pyplot(plot_road_network(city))
