import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
from utility_classes import *

def plot_data(weather_data:dict, forecast_data:dict, plot_type:str, y_axis_label:str, title:str):
	plot_functions = {
		'line': px.line,
		'scatter': px.scatter,
		'bar': px.bar,
		'box': px.box,
		'histogram': px.histogram
	}
	weather_df = pd.DataFrame(weather_data)
	weather_df["Source"] = "Historical"
	forecast_df = pd.DataFrame(forecast_data)
	forecast_df["Source"] = "Future"
	combined_df = pd.concat([weather_df, forecast_df])

	if plot_type in plot_functions:
		fig = plot_functions[plot_type](
			combined_df,
			x="timestamps",
			y="values",
			color="Source", 
			title=title,
			labels={'timestamps':'Time (UTC)',
					'values':y_axis_label,
					'source':'Data Type'
					})	
		st.plotly_chart(fig)
	else:
		st.error(f"Unsupported plot type: {plot_type}")

def show():

	### Variables ###
	weather_url = "http://127.0.0.1:8000/weather"
	resolutions = 'hour'	
	data_limit = 120
	forecast_url = 'http://127.0.0.1:8000/forecast'
	coords = 'POINT(11.7644 55.9594)'
	tab_data = [
		{"title": "Acc precipitation", "parameter": "acc_precip",'edr_parameter':'total-precipitation', "y_axis_label": "Precipitation [mm]", "plot_type": "bar"},
   		{"title": "Cloud cover","parameter": "mean_cloud_cover",'edr_parameter':'low-cloud-cover',"y_axis_label": "Cloud cover [%]","plot_type": "line"},
   		{"title": "Pressure ", "parameter": "mean_pressure",'edr_parameter':'pressure-surface', "y_axis_label": "Pressure [hPa]", "plot_type": "line"},
		{"title": "Radiation", "parameter": "mean_radiation",'edr_parameter':'global-radiation-flux',"y_axis_label": "Radiation [W/m²]", "plot_type": "line"},
   		{"title": "Humidity", "parameter": "mean_relative_hum",'edr_parameter':'relative-humidity-2m', "y_axis_label": "Humidity [%]", "plot_type": "line"},
   		{"title": "Temperature", "parameter": "mean_temp",'edr_parameter':'temperature-2m', "y_axis_label": "Temperature [°C]", "plot_type": "line"},
   		{"title": "Wind speed", "parameter": "mean_wind_speed",'edr_parameter':'wind-speed-10m', "y_axis_label": "Wind speed [m/s]", "plot_type": "line"}
   		]


	### UI ###
	st.title("Forecast")
	st.write('This forecast show weather and energy spot prices from the past five days and forcast for the coming two days')
	st.markdown("---")

	forecast_frame = st.empty()
	tabs =st.tabs([tab['title'] for tab in tab_data])

	weather_payloads = {'items':[]}
	forecast_payloads = {'items':[]}
	if st.button('Request Data'):
		with st.spinner('Fetching data, please wait...'):
			for tab in tab_data:	
				historical_payload={
						'parameter':tab['parameter'],
						'limit': data_limit,
						'resolution': 'hour',
						'time_from': (datetime.today()-timedelta(days=5)).isoformat()[:10],
						'time_to': datetime.today().isoformat()[:10]
						}
				weather_payloads['items'].append(historical_payload)
				forecast_payload={
						'coords':coords,
						'crs':'crs84',
						'parameter':tab['edr_parameter']
						}
				forecast_payloads['items'].append(forecast_payload)
			weather_data = ApiFetcher.fetch_data(weather_url, weather_payloads)
			forecast_data = ApiFetcher.fetch_data(forecast_url, forecast_payloads)
			if 'status_code' in forecast_data:
					st.write(f'Error occured: {forecast_data['error']}')
			else:
				forecast_frame.empty()
				with forecast_frame.container():
					forecast_data['SpotPriceDKK']
					spot_price_df = pd.DataFrame.from_dict(forecast_data['SpotPriceDKK'], orient='index', columns=['SpotPriceDKK']).reset_index()
					spot_price_df.rename(columns={'index':'HourUTC'}, inplace=True)
					fig = px.line(
								spot_price_df,
								x='HourUTC',
								y='SpotPriceDKK',
								title='Spot price predictions for DK1 [DKK]',
								labels={'HourUTC':'Hour (UTC)',
										'SpotPriceDKK':'Spot Price (DKK/kWh)'
										}
								)
					st.plotly_chart(fig)
				for idx, tab in enumerate(tabs):
					with tab:
						plot_data(weather_data={'timestamps':weather_data['results'][idx]['timestamps'], 'values':weather_data['results'][idx]['values']},
								  forecast_data={'timestamps':forecast_data['results'][idx]['timestamps'], 'values':forecast_data['results'][idx]['values']},
								  plot_type=tab_data[idx]['plot_type'],
								  y_axis_label=tab_data[idx]['y_axis_label'],
								  title=tab_data[idx]['title'])