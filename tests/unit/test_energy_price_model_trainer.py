import pytest
from unittest.mock import patch, Mock
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from api.api_utility_classes import EnergyPriceModelTrainer

@pytest.fixture
def mock_data():
	np.random.seed(42)
	n_samples = 100
	return pd.DataFrame({
		"Feature1": np.random.rand(n_samples) * 100,
		"Feature2": np.random.rand(n_samples) * 50,
		"SpotPriceDKK": np.random.rand(n_samples) * 500
	})


@patch('xgboost.DMatrix')
@patch('xgboost.train')
def test_train_model(mock_train, mock_dmatrix, mock_data):
	mock_model = Mock()
	mock_model.predict = Mock(return_value=np.random.rand(20) * 500)  # Mock predictions
	mock_model.save_model = Mock()
	mock_train.return_value = mock_model

	result = EnergyPriceModelTrainer.train_model(
		data=mock_data,
		gamma=0.1,
		max_depth=3,
		eta=0.3,
		subsample=0.8,
		colsample_bytree=0.8,
		min_child_weight=1,
		num_rounds=50
	)

	mock_dmatrix.assert_called()
	mock_train.assert_called_once()
	mock_model.save_model.assert_called_once_with('xgboost_model_test.json')

	assert "rmse" in result
	assert "mea" in result
	assert "r2" in result
	assert "rsd" in result
	assert isinstance(result["rmse"], float)
	assert isinstance(result["mea"], float)
	assert isinstance(result["r2"], float)
	assert isinstance(result["rsd"], float)

@patch('xgboost.DMatrix')
def test_train_model_invalid_data(mock_dmatrix):
	mock_dmatrix.return_value = Mock()

	with pytest.raises(KeyError):
		EnergyPriceModelTrainer.train_model(
			data=pd.DataFrame({"Feature1": [1, 2], "Feature2": [3, 4]}),
			gamma=0.1,
			max_depth=3,
			eta=0.3,
			subsample=0.8,
			colsample_bytree=0.8,
			min_child_weight=1,
			num_rounds=50
		)

	with pytest.raises(ValueError):
		EnergyPriceModelTrainer.train_model(
			data=pd.DataFrame(),
			gamma=0.1,
			max_depth=3,
			eta=0.3,
			subsample=0.8,
			colsample_bytree=0.8,
			min_child_weight=1,
			num_rounds=50
		)


@patch('xgboost.DMatrix')
@patch('xgboost.train')
def test_train_model_edge_cases(mock_train, mock_dmatrix, mock_data):
	mock_model = Mock()
	mock_model.predict = Mock(return_value=np.random.rand(20) * 500)  # Mock predictions
	mock_model.save_model = Mock()
	mock_train.return_value = mock_model

	result = EnergyPriceModelTrainer.train_model(
		data=mock_data,
		gamma=10.0,  
		max_depth=20,
		eta=0.01,  
		subsample=0.1,  
		colsample_bytree=0.1,
		min_child_weight=10,
		num_rounds=10
	)

	assert "rmse" in result
	assert "mea" in result
	assert "r2" in result
	assert "rsd" in result
	assert isinstance(result["rmse"], float)
	assert isinstance(result["mea"], float)
	assert isinstance(result["r2"], float)
	assert isinstance(result["rsd"], float)


@patch('xgboost.DMatrix')
def test_train_model_no_values(mock_dmatrix):
    mock_dmatrix.return_value = Mock()

    empty_values_data = pd.DataFrame(columns=["Feature1", "Feature2", "SpotPriceDKK"])

    with pytest.raises(ValueError, match="Input DataFrame is empty."):
        EnergyPriceModelTrainer.train_model(
            data=empty_values_data,
            gamma=0.1,
            max_depth=3,
            eta=0.3,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=1,
            num_rounds=50
        )