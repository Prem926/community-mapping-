import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import folium_static
import folium
import numpy as np
from shapely.geometry import Polygon
from datetime import datetime, timedelta
import requests
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

class SustainableUrbanDevelopmentPlatform:
    def __init__(self):
        self.openweather_api_key = "4a83da95401cd1052adc94d76f105dec"
        self.load_data()
        self.setup_page()
        self.train_simple_models()

    def load_data(self):
        self.city_boundary = self.generate_mock_city_boundary()
        self.projects = self.generate_mock_projects()
        self.environmental_data = self.generate_mock_environmental_data()

    def generate_mock_city_boundary(self):
        polygon = gpd.GeoDataFrame({
            'geometry': [Polygon([
                (72.4, 22.9), (72.7, 22.9), (72.7, 23.1), (72.4, 23.1)
            ])]
        })
        polygon.crs = "EPSG:4326"
        return polygon

    def generate_mock_projects(self):
        n_projects = 50
        return pd.DataFrame({
            'name': [f'Project {i}' for i in range(n_projects)],
            'latitude': np.random.uniform(22.9, 23.1, n_projects),
            'longitude': np.random.uniform(72.4, 72.7, n_projects),
            'impact_score': np.random.randint(1, 100, n_projects),
            'green_score': np.random.randint(1, 100, n_projects)
        })

    def generate_mock_environmental_data(self):
        n_points = 1000
        n_timestamps = 10
        data = []
        for t in range(n_timestamps):
            timestamp = datetime(2023, 1, 1) + timedelta(days=t)
            data.extend([
                {
                    'timestamp': timestamp,
                    'latitude': np.random.uniform(22.9, 23.1),
                    'longitude': np.random.uniform(72.4, 72.7),
                    'air_quality_index': np.random.randint(0, 500)
                } for _ in range(n_points)
            ])
        return pd.DataFrame(data)

    def setup_page(self):
        st.set_page_config(layout="wide", page_title="Ahmedabad Sustainable Urban Development")
        st.title("Ahmedabad Sustainable Urban Development Platform")

        tabs = st.tabs(["Infrastructure Planning", "Environmental Monitoring", "Sustainable Development", "Community Engagement"])

        with tabs[0]:
            self.infrastructure_planning()
        with tabs[1]:
            self.environmental_monitoring()
        with tabs[2]:
            self.sustainable_development()
        with tabs[3]:
            self.community_engagement()

    def infrastructure_planning(self):
        st.header("Infrastructure and Construction Planning")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self.project_registration()
        
        with col2:
            self.impact_assessment()

    def project_registration(self):
        st.subheader("Project Registration")
        project_name = st.text_input("Project Name")
        project_type = st.selectbox("Project Type", ["Residential", "Commercial", "Industrial", "Infrastructure"])
        project_area = st.number_input("Project Area (sq m)", min_value=0.0)
        project_cost = st.number_input("Estimated Cost (in lakhs INR)", min_value=0.0)
        
        if st.button("Register Project"):
            st.success(f"Project '{project_name}' registered successfully!")
            self.predict_impact(project_name, project_type, project_area, project_cost)

    def predict_impact(self, name, type, area, cost):
        st.subheader("Predicted Impact Analysis")
        
        # Mock impact prediction (replace with actual model in real implementation)
        environmental_impact = np.random.uniform(0, 100)
        economic_impact = np.random.uniform(0, 100)
        social_impact = np.random.uniform(0, 100)
        
        impact_df = pd.DataFrame({
            'Impact Type': ['Environmental', 'Economic', 'Social'],
            'Impact Score': [environmental_impact, economic_impact, social_impact]
        })
        
        fig = px.bar(impact_df, x='Impact Type', y='Impact Score', title=f"Predicted Impact for {name}")
        st.plotly_chart(fig)
        
        st.write(f"Based on the project details:")
        st.write(f"- Environmental Impact: {environmental_impact:.2f}")
        st.write(f"- Economic Impact: {economic_impact:.2f}")
        st.write(f"- Social Impact: {social_impact:.2f}")
        
        if environmental_impact > 70:
            st.warning("High environmental impact. Consider implementing more green technologies.")
        if economic_impact < 30:
            st.warning("Low economic impact. Review the project's economic viability.")
        if social_impact < 50:
            st.warning("Moderate social impact. Consider ways to increase community benefits.")

    def impact_assessment(self):
        st.subheader("Impact Assessment")
        m = folium.Map(location=[23.0225, 72.5714], zoom_start=11)
        
        for _, project in self.projects.iterrows():
            folium.Marker(
                [project['latitude'], project['longitude']],
                popup=f"Project: {project['name']}<br>Impact: {project['impact_score']}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
        
        folium_static(m)

    def get_real_time_air_quality(self):
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat=23.0225&lon=72.5714&appid={self.openweather_api_key}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'list' in data and data['list']:
                df = pd.DataFrame(data['list'])
                df['datetime'] = pd.to_datetime(df['dt'], unit='s')
                df['value'] = df['components'].apply(lambda x: x['pm2_5'])
                df['location'] = 'Ahmedabad'
                df['coordinates.latitude'] = 23.0225
                df['coordinates.longitude'] = 72.5714
                return df[['datetime', 'location', 'coordinates.latitude', 'coordinates.longitude', 'value']]
            else:
                st.error("No data available from OpenWeather for Ahmedabad")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch data from OpenWeather: {e}")
            return None

    def get_color_for_aqi(self, aqi):
        if aqi <= 12:
            return 'green'
        elif aqi <= 35.4:
            return 'yellow'
        elif aqi <= 55.4:
            return 'orange'
        elif aqi <= 150.4:
            return 'red'
        elif aqi <= 250.4:
            return 'purple'
        else:
            return 'maroon'

    def environmental_monitoring(self):
        st.header("Environmental Monitoring")
        
        real_time_data = self.get_real_time_air_quality()
        
        if real_time_data is not None and not real_time_data.empty:
            st.subheader("Real-time Air Quality Map")
            m = folium.Map(location=[23.0225, 72.5714], zoom_start=11)
            
            for _, row in real_time_data.iterrows():
                folium.CircleMarker(
                    location=[row['coordinates.latitude'], row['coordinates.longitude']],
                    radius=10,
                    popup=f"Location: {row['location']}<br>PM2.5: {row['value']} µg/m³<br>Time: {row['datetime']}",
                    color=self.get_color_for_aqi(row['value']),
                    fill=True,
                    fillColor=self.get_color_for_aqi(row['value'])
                ).add_to(m)
            
            folium_static(m)
            
            st.subheader("Air Quality Statistics")
            st.write(f"Average PM2.5: {real_time_data['value'].mean():.2f} µg/m³")
            st.write(f"Max PM2.5: {real_time_data['value'].max():.2f} µg/m³")
            st.write(f"Min PM2.5: {real_time_data['value'].min():.2f} µg/m³")
            
            st.subheader("PM2.5 Levels by Location")
            fig = self.create_animated_bar_chart(real_time_data)
            st.plotly_chart(fig)
            
            st.subheader("Air Quality Heatmap")
            fig = self.create_air_quality_heatmap(real_time_data)
            st.plotly_chart(fig)
            
            self.show_historical_trend(real_time_data)
        else:
            st.warning("No real-time air quality data available for Ahmedabad.")
            st.write("This could be due to temporary data unavailability or API issues.")
            st.write("Please check back later or contact the administrator if the problem persists.")

    def create_animated_bar_chart(self, data):
        fig = px.bar(data, x='location', y='value', 
                     title='PM2.5 Levels by Location',
                     labels={'value': 'PM2.5 (µg/m³)', 'location': 'Location'},
                     animation_frame='datetime',
                     range_y=[0, data['value'].max() * 1.1])
        fig.update_layout(
            updatemenus=[{
                'buttons': [
                    {'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}],
                     'label': 'Play',
                     'method': 'animate'},
                    {'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                     'label': 'Pause',
                     'method': 'animate'}
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }],
            sliders=[{
                'active': 0,
                'yanchor': 'top',
                'xanchor': 'left',
                'currentvalue': {
                    'font': {'size': 20},
                    'prefix': 'Timestamp:',
                    'visible': True,
                    'xanchor': 'right'
                },
                'transition': {'duration': 300, 'easing': 'cubic-in-out'},
                'pad': {'b': 10, 't': 50},
                'len': 0.9,
                'x': 0.1,
                'y': 0,
                'steps': [
                    {'args': [[t.strftime('%Y-%m-%d %H:%M:%S')], {'frame': {'duration': 300, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 300}}],
                     'label': t.strftime('%Y-%m-%d %H:%M:%S'),
                     'method': 'animate'} for t in data['datetime'].unique()
                ]
            }]
        )
        return fig

    def create_air_quality_heatmap(self, data):
        fig = go.Figure(data=go.Densitymapbox(
            lat=data['coordinates.latitude'],
            lon=data['coordinates.longitude'],
            z=data['value'],
            radius=20,
            colorscale='Viridis',
            zmin=0,
            zmax=data['value'].max(),
            colorbar=dict(title='PM2.5 (µg/m³)')
        ))
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_center_lat=23.0225,
            mapbox_center_lon=72.5714,
            mapbox_zoom=10,
            updatemenus=[{
                'buttons': [
                    {'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}],
                     'label': 'Play',
                     'method': 'animate'},
                    {'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                     'label': 'Pause',
                     'method': 'animate'}
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }],
            sliders=[{
                'active': 0,
                'yanchor': 'top',
                'xanchor': 'left',
                'currentvalue': {
                    'font': {'size': 20},
                    'prefix': 'Timestamp:',
                    'visible': True,
                    'xanchor': 'right'
                },
                'transition': {'duration': 300, 'easing': 'cubic-in-out'},
                'pad': {'b': 10, 't': 50},
                'len': 0.9,
                'x': 0.1,
                'y': 0,
                'steps': [
                    {'args': [[t.strftime('%Y-%m-%d %H:%M:%S')], {'frame': {'duration': 300, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 300}}],
                     'label': t.strftime('%Y-%m-%d %H:%M:%S'),
                     'method': 'animate'} for t in data['datetime'].unique()
                ]
            }]
        )
        frames = [go.Frame(data=[go.Densitymapbox(
            lat=data[data['datetime'] == t]['coordinates.latitude'],
            lon=data[data['datetime'] == t]['coordinates.longitude'],
            z=data[data['datetime'] == t]['value'],
            radius=20,
            colorscale='Viridis',
            zmin=0,
            zmax=data['value'].max()
        )]) for t in data['datetime'].unique()]
        fig.frames = frames
        return fig

    def show_historical_trend(self, real_time_data):
        st.subheader("Historical Air Quality Trend")
        historical_data = self.get_historical_air_quality()
        if historical_data is not None and not historical_data.empty:
            fig = px.line(historical_data, x='datetime', y='value', 
                          title='PM2.5 Levels Over Time',
                          labels={'value': 'PM2.5 (µg/m³)', 'datetime': 'Date and Time'})
            fig.update_traces(mode='lines+markers')
            fig.update_layout(
                hovermode="x unified",
                updatemenus=[dict(
                    type="buttons",
                    direction="left",
                    buttons=[
                        dict(label="Play",
                             method="animate",
                             args=[None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}]),
                        dict(label="Pause",
                             method="animate",
                             args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])
                    ]
                )]
            )
            st.plotly_chart(fig)
        else:
            st.warning("No historical air quality data available.")

    def get_historical_air_quality(self):
        # This is a placeholder. In a real scenario, you would fetch historical data from an API or database
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        date_range = pd.date_range(start=start_date, end=end_date, freq='H')
        historical_data = pd.DataFrame({
            'datetime': date_range,
            'value': np.random.uniform(10, 100, len(date_range))
        })
        return historical_data

    def sustainable_development(self):
        st.header("Sustainable Development Tools")
        
        # Enhanced 3D scatter plot with animation
        fig = go.Figure(data=[go.Scatter3d(
            x=self.projects['latitude'],
            y=self.projects['longitude'],
            z=self.projects['green_score'],
            mode='markers',
            marker=dict(
                size=5,
                color=self.projects['green_score'],
                colorscale='Viridis',
                opacity=0.8
            ),
            text=self.projects['name'],
            hoverinfo='text'
        )])

        fig.update_layout(
            scene=dict(
                xaxis_title='Latitude',
                yaxis_title='Longitude',
                zaxis_title='Green Building Score'
            ),
            title='3D Visualization of Green Building Scores',
            updatemenus=[dict(
                type='buttons',
                showactive=False,
                buttons=[dict(label='Play',
                              method='animate',
                              args=[None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}]),
                         dict(label='Pause',
                              method='animate',
                              args=[[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate'}])]
            )]
        )

        frames = [go.Frame(data=[go.Scatter3d(
            x=self.projects['latitude'],
            y=self.projects['longitude'],
            z=self.projects['green_score'] * (i / 100),
            mode='markers',
            marker=dict(
                size=5,
                color=self.projects['green_score'] * (i / 100),
                colorscale='Viridis',
                opacity=0.8
            )
        )]) for i in range(0, 101, 10)]

        fig.frames = frames

        st.plotly_chart(fig)

        # Add a new section for sustainability metrics
        st.subheader("Sustainability Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Green Score", f"{self.projects['green_score'].mean():.2f}")
        with col2:
            st.metric("Total Green Projects", len(self.projects[self.projects['green_score'] > 70]))
        with col3:
            st.metric("Sustainability Index", f"{self.calculate_sustainability_index():.2f}")

    def sdg_alignment(self):
        st.header("SDG Alignment Analysis")
        
        sdgs = {
            "SDG 6: Clean Water and Sanitation": 0,
            "SDG 7: Affordable and Clean Energy": 0,
            "SDG 11: Sustainable Cities and Communities": 0,
            "SDG 13: Climate Action": 0
        }
        
        for _, project in self.projects.iterrows():
            # Analyze each project and update SDG scores
            sdgs["SDG 6: Clean Water and Sanitation"] += self.calculate_water_impact(project)
            sdgs["SDG 7: Affordable and Clean Energy"] += self.calculate_energy_impact(project)
            sdgs["SDG 11: Sustainable Cities and Communities"] += self.calculate_urban_impact(project)
            sdgs["SDG 13: Climate Action"] += self.calculate_climate_impact(project)
        
        # Normalize scores
        max_score = max(sdgs.values())
        sdgs = {k: v / max_score * 100 for k, v in sdgs.items()}
        
        # Create animated radar chart
        fig = go.Figure()

        for i in range(0, 101, 10):
            fig.add_trace(go.Scatterpolar(
                r=[v * i / 100 for v in sdgs.values()],
                theta=list(sdgs.keys()),
                fill='toself',
                name=f'Step {i}',
                visible=False
            ))

        fig.data[0].visible = True

        steps = []
        for i in range(len(fig.data)):
            step = dict(
                method="update",
                args=[{"visible": [False] * len(fig.data)},
                      {"title": f"SDG Alignment - Step {i*10}"}],
                label=f"Step {i*10}"
            )
            step["args"][0]["visible"][i] = True
            steps.append(step)

        sliders = [dict(
            active=0,
            currentvalue={"prefix": "Step: "},
            pad={"t": 50},
            steps=steps
        )]

        fig.update_layout(
            sliders=sliders,
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=False
        )

        st.plotly_chart(fig)
        
        # Provide recommendations based on SDG alignment
        self.sdg_recommendations(sdgs)

    def calculate_water_impact(self, project):
        # Placeholder function, replace with actual calculation
        return np.random.uniform(0, 1)

    def calculate_energy_impact(self, project):
        # Placeholder function, replace with actual calculation
        return np.random.uniform(0, 1)

    def calculate_urban_impact(self, project):
        # Placeholder function, replace with actual calculation
        return np.random.uniform(0, 1)

    def calculate_climate_impact(self, project):
        # Placeholder function, replace with actual calculation
        return np.random.uniform(0, 1)

    def sdg_recommendations(self, sdgs):
        st.subheader("SDG Alignment Recommendations")
        for sdg, score in sdgs.items():
            if score < 50:
                st.warning(f"{sdg} alignment is low. Consider implementing more projects that address this goal.")
            elif score < 75:
                st.info(f"{sdg} alignment is moderate. There's room for improvement in this area.")
            else:
                st.success(f"{sdg} alignment is strong. Keep up the good work in this area.")

    def community_engagement(self):
        st.header("Community Engagement Platform")
        st.write("This section would include features for community feedback and participation.")

    def train_simple_models(self):
        # Placeholder function, replace with actual model training
        pass

    def calculate_sustainability_index(self):
        # Placeholder function, replace with actual calculation
        return np.random.uniform(0, 100)

if __name__ == "__main__":
    app = SustainableUrbanDevelopmentPlatform()