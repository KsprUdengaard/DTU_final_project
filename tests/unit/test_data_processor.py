import pytest
from unittest.mock import Mock
from api.api_utility_classes import Transformer, HistoricalWeatherDataProcessor, ForecastDataProcessor

@pytest.fixture
def mock_transformer():
    """Fixture to mock the Transformer class."""
    transformer = Mock(spec=Transformer)
    transformer.transform = Mock(return_value=[1.0, 2.0, 3.0])
    return transformer

@pytest.fixture
def historical_weather_json():
    """Fixture for sample historical weather JSON data."""
    return {
        "features": [
            {"properties": {"from": "2023-01-01T00:00:00Z", "value": 273.15}},
            {"properties": {"from": "2023-01-01T01:00:00Z", "value": 274.15}},
            {"properties": {"from": "2023-01-01T02:00:00Z", "value": 275.15}}
        ]
    }

@pytest.fixture
def forecast_json():
    """Fixture for sample forecast JSON data."""
    return {
        "parameters": {"temperature-2m": []},
        "domain": {
            "axes": {
                "t": {
                    "values": ["2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z", "2023-01-01T02:00:00Z"]
                }
            }
        },
        "ranges": {
            "temperature-2m": {
                "values": [273.15, 274.15, 275.15]
            }
        }
    }


def test_historical_weather_data_processor(historical_weather_json, mock_transformer):
    processor = HistoricalWeatherDataProcessor()
    result = processor.process_data(
        json_data=historical_weather_json,
        transformer=mock_transformer,
        parameter="temperature-2m"
    )

    assert result["parameterId"] == "temperature-2m"
    assert result["timestamps"] == ["2023-01-01T00", "2023-01-01T01", "2023-01-01T02"]
    assert result["values"] == [1.0, 2.0, 3.0]
    mock_transformer.transform.assert_called_once_with(
        values=[273.15, 274.15, 275.15], parameter="temperature-2m"
    )


def test_historical_weather_empty_features(mock_transformer):
    processor = HistoricalWeatherDataProcessor()
    result = processor.process_data(
        json_data={"features": []},
        transformer=mock_transformer,
        parameter="temperature-2m"
    )

    assert result["parameterId"] == "temperature-2m"
    assert result["timestamps"] == []
    assert result["values"] == []
    mock_transformer.transform.assert_not_called()


def test_historical_weather_partial_features(mock_transformer):
    processor = HistoricalWeatherDataProcessor()
    mock_transformer.transform.side_effect = lambda values, parameter: [round(v / 273.15, 1) for v in values]

    json_data = {
        "features": [
            {"properties": {"from": "2023-01-01T00:00:00Z", "value": 273.15}},
            {"properties": {}},
            {"properties": {"from": "2023-01-01T02:00:00Z", "value": 275.15}}
        ]
    }

    result = processor.process_data(
        json_data=json_data,
        transformer=mock_transformer,
        parameter="temperature-2m"
    )

    assert result["parameterId"] == "temperature-2m"
    assert result["timestamps"] == ["2023-01-01T00", "2023-01-01T02"]
    assert result["values"] == [1.0, 1.0]
    mock_transformer.transform.assert_called_once_with(
        values=[273.15, 275.15], parameter="temperature-2m"
    )


def test_forecast_data_processor(forecast_json, mock_transformer):
    processor = ForecastDataProcessor()
    result = processor.process_data(
        json_data=forecast_json,
        transformer=mock_transformer,
        parameter="temperature-2m"
    )

    assert result["parameterId"] == "temperature-2m"
    assert result["timestamps"] == ["2023-01-01T00", "2023-01-01T01", "2023-01-01T02"]
    assert result["values"] == [1.0, 2.0, 3.0]
    mock_transformer.transform.assert_called_once_with(
        values=[273.15, 274.15, 275.15], parameter="temperature-2m"
    )


def test_forecast_data_processor_empty_data(mock_transformer):
    processor = ForecastDataProcessor()
    result = processor.process_data(
        json_data={"domain": {}, "ranges": {}},
        transformer=mock_transformer,
        parameter="temperature-2m"
    )

    assert result["parameterId"] == "temperature-2m"
    assert result["timestamps"] == []
    assert result["values"] == []
    mock_transformer.transform.assert_not_called() 


def test_forecast_data_processor_missing_keys(mock_transformer):
    processor = ForecastDataProcessor()
    result = processor.process_data(
        json_data={},
        transformer=mock_transformer,
        parameter="temperature-2m"
    )

    assert result["parameterId"] == "temperature-2m"
    assert result["timestamps"] == []
    assert result["values"] == []
    mock_transformer.transform.assert_not_called()
