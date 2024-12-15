import streamlit as st
import plotly.express as px
import requests
import pandas as pd
from datetime import datetime, timedelta
from utility_classes import *

# Function to plot the data
def plot_weather_data(x_axis:list, y_axis:list, plot_type:str, y_axis_label:str, title:str)->None:
	plot_functions = {
		'line': px.line,
		'scatter': px.scatter,
		'bar': px.bar,
		'box': px.box,
		'histogram': px.histogram
	}

	if plot_type in plot_functions:
		fig = plot_functions[plot_type](x=x_axis, y=y_axis, title=title, labels={'timestamps':'Time (UTC)','values':y_axis_label})
		fig.update_layout(yaxis_title=y_axis_label, xaxis_title="Time (UTC)")
		st.plotly_chart(fig)
	else:
		st.error(f"Unsupported plot type: {plot_type}")

def show():
	### Variables ###
	weather_url = "http://127.0.0.1:8000/weather"
	resolutions = ['hour', 'day', 'month', 'year']	
	data_limit = 1000
	
	### UI ###
	st.title('Weather Data')	
	col1, col2, col3 = st.columns(3)
	with col1:
		start_date = st.date_input('From Date', datetime.today()-timedelta(days=1), min_value=datetime(2000, 1, 1))
	with col2:
		end_date = st.date_input('To Date', datetime.today(), min_value=datetime(2000, 1, 1))
	with col3:
		resolution = st.selectbox('Choose a resolution', resolutions)

	st.write('<small>*The maximum number of data points that can be requested is limited to 1,000</small>', unsafe_allow_html=True)

	tab_data = [
		{"title": "Humidity", "y_axis_label": "Humidity [%]", "plot_type": "line", "df_index": 0, "header": "Historical Average Humidity", "parameter": "mean_relative_hum"},
		{"title": "Temperature", "y_axis_label": "Temperature [°C]", "plot_type": "line", "df_index": 1, "header": "Historical Average Temperature", "parameter": "mean_temp"},
		{"title": "Wind speed", "y_axis_label": "Wind speed [m/s]", "plot_type": "line", "df_index": 2, "header": "Historical Average Wind Speed", "parameter": "mean_wind_speed"},
		{"title": "Pressure", "y_axis_label": "Pressure [hPa]", "plot_type": "line", "df_index": 3, "header": "Historical Average Pressure", "parameter": "mean_pressure"},
		{"title": "Radiation", "y_axis_label": "Radiation [W/m²]", "plot_type": "line", "df_index": 4, "header": "Historical Average Radiation", "parameter": "mean_radiation"},
		{"title": "Acc Precipitation", "y_axis_label": "Precipitation [mm]", "plot_type": "bar", "df_index": 5, "header": "Historical Average Precipitation", "parameter": "acc_precip"},
		{"title": "Cloud cover", "y_axis_label": "Cloud cover [%]", "plot_type": "line", "df_index": 6, "header": "Historical Average Cloud Cover", "parameter": "mean_cloud_cover"}
	]

	tabs = st.tabs([tab["title"] for tab in tab_data])
	apiFetcher = ApiFetcher()

	### Interface ###
	payloads = []
	if st.button('Request Data'):
		if end_date > datetime.today().date():
			st.error('Cannot fetch future data')
		elif start_date > end_date:
			st.error('Cannot have a **From** date past the **To** date')
		else:
			with st.spinner("Fetching historical data... Please wait."):
				for tab in tab_data:
					payload={
							'parameter':tab['parameter'],
							'limit': data_limit,
							'resolution': resolution,
							'time_from': start_date.isoformat(),
							'time_to': end_date.isoformat()
							}
					payloads.append(payload)				
				weather_payload ={}
				weather_payload['items'] = payloads
				weather_data = apiFetcher.fetch_data(weather_url, weather_payload)
				for idx, tab in enumerate(tabs):
					with tab:
						st.header(tab_data[idx]['header'])
						x_axis = weather_data["results"][idx]['timestamps']
						y_axis = weather_data["results"][idx]['values']
						plot_type = tab_data[idx]["plot_type"]
						y_axis_label = tab_data[idx]["y_axis_label"]
						title = tab_data[idx]["title"]
						plot_weather_data(x_axis, y_axis, plot_type, y_axis_label, title)