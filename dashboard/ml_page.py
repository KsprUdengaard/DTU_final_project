import streamlit as st
import pandas
from utility_classes import *

def show():

	### Variables ###
	
	apiFetcher = ApiFetcher()
	model_url = "http://127.0.0.1:8000/model"

	### UI ###
	st.title('Model Parameters')
	st.write('Here you can change the model parameters and retrain')
	col1, col2 = st.columns(2)
	with col1:
		gamma_slider = st.slider("gamma", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
		eta_slider = st.slider("eta", min_value=0.0, max_value=0.3, value=0.1, step=0.01)
		colsample_bytree_slider = st.slider("colsample_bytree", min_value=0.3, max_value=1.0, value=0.8, step=0.01)
		
	with col2:
		max_depth_slider = st.slider("max_depth", min_value=3, max_value=12, value=6, step=1)
		subsample_slider = st.slider("subsample", min_value=0.5, max_value=1.0, value=0.7, step=0.01)
		min_child_weight_slider = st.slider("min_child_weight", min_value=1, max_value=10, value=1, step=1)

	if st.button('Retrain model'):
		payload = {'gamma':gamma_slider,
				   'eta':eta_slider,
				   'colsample':colsample_bytree_slider,
				   'max_depth':max_depth_slider,
				   'subsample':subsample_slider,
				   'min_child_weight':min_child_weight_slider}
		response = apiFetcher.fetch_data(model_url, payload, 'post')

		data = {
		    "Metric": ["RMSE", "MAE", "R²", "RSD%"],
		    "Good Value": ["Lower", "Lower", "Close to 1", "Lower"],
		    "Interpretation": [
		        "Smaller prediction errors; penalizes large errors more.",
		        "Average absolute error; less sensitive to outliers.",
		        "Model explains most of the variance.",
		        "Model error as a percentage of the mean value."
		    ],
		    "Results":[response["rmse"], response["mea"], response["r2"], f'{response["rsd"]}']
		}
		metrics_df = pd.DataFrame(data)
		
		st.markdown("---")
		st.write("Model Evaluation Metrics")
		st.table(metrics_df)