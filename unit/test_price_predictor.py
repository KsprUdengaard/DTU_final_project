import pytest
from unittest.mock import Mock, patch
import pandas as pd
import xgboost as xgb
from xgboost import DMatrix
from api.api_utility_classes import PricePredictor

@pytest.fixture
def mock_model():
	model = Mock(spec=xgb.Booster)
	model.predict = Mock(return_value=[1000.0, 2000.0, 3000.0])  # Mocked predictions
	return model

@pytest.fixture
def mock_data():
	return [
		{"parameterId": "temperature-2m", "timestamps": ["2023-01-01T00", "2023-01-01T01", "2023-01-01T02"], "values": [273.15, 274.15, 275.15]},
		{"parameterId": "relative-humidity-2m", "timestamps": ["2023-01-01T00", "2023-01-01T01", "2023-01-01T02"], "values": [50, 55, 60]}
	]

@patch('xgboost.Booster.load_model')
def test_price_predictor_initialization(mock_load_model, mock_model):
	mock_load_model.return_value = None  
	predictor = PricePredictor(model_path="mock_model_path")
	predictor.model = mock_model

	assert isinstance(predictor, PricePredictor)
	mock_load_model.assert_called_once_with("mock_model_path")

@patch('xgboost.DMatrix')
@patch('xgboost.Booster.load_model')
def test_predict_energy_prices(mock_load_model, mock_dmatrix, mock_model, mock_data):
	mock_load_model.return_value = None
	predictor = PricePredictor(model_path="mock_model_path")
	predictor.model = mock_model

	mock_dmatrix.return_value = Mock()

	result = predictor.predict_energy_prices(mock_data)

	expected_df = pd.DataFrame({
		"HourUTC": ["2023-01-01T00", "2023-01-01T01", "2023-01-01T02"],
		"mean_temp": [273.15, 274.15, 275.15],
		"mean_relative_hum": [50, 55, 60]
	})
	expected_df["HourUTC"] = pd.to_datetime(expected_df["HourUTC"]).astype(int) / 10**9

	passed_df = mock_dmatrix.call_args[0][0]
	pd.testing.assert_frame_equal(passed_df, expected_df)

	assert result == {
		"2023-01-01T00": 1.0,
		"2023-01-01T01": 2.0,
		"2023-01-01T02": 3.0
	}
	mock_model.predict.assert_called_once_with(mock_dmatrix.return_value)


@patch('xgboost.DMatrix')
@patch('xgboost.Booster.load_model')
def test_predict_energy_prices_invalid_data(mock_dmatrix, mock_load_model, mock_model):
   
    mock_load_model.return_value = None

    predictor = PricePredictor(model_path="mock_model_path")
    predictor.model = mock_model

    mock_dmatrix.side_effect = ValueError("Invalid data for DMatrix")

    with pytest.raises(KeyError):
        predictor.predict_energy_prices([{"parameterId": "temperature-2m", "values": [273.15, 274.15]}])

    with pytest.raises(IndexError):
        predictor.predict_energy_prices([])

    with pytest.raises(TypeError):
        predictor.predict_energy_prices("invalid_data")


@patch('xgboost.DMatrix')
@patch('xgboost.Booster.load_model')
def test_predict_energy_prices_unmapped_parameter(mock_load_model, mock_dmatrix, mock_model):
	mock_load_model.return_value = None
	predictor = PricePredictor(model_path="mock_model_path")
	predictor.model = mock_model

	mock_dmatrix.return_value = Mock()

	mock_data = [
		{"parameterId": "unknown-parameter", "timestamps": ["2023-01-01T00"], "values": [100]}
	]

	result = predictor.predict_energy_prices(mock_data)

	expected_df = pd.DataFrame({
		"HourUTC": ["2023-01-01T00"],
		"unknown-parameter": [100]
	})
	expected_df["HourUTC"] = pd.to_datetime(expected_df["HourUTC"]).astype(int) / 10**9

	passed_df = mock_dmatrix.call_args[0][0]
	pd.testing.assert_frame_equal(passed_df, expected_df)

	assert result == {"2023-01-01T00": 1.0}

