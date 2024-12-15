import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from api.api import app
from api.api_utility_classes import Transformer, HistoricalWeatherDataProcessor, ForecastDataProcessor

client = TestClient(app)

# Mock responses for external APIs
MOCK_WEATHER_RESPONSE = {
    "features": [
        {
            "properties": {
                "from": "2024-12-06T00:00:00Z",
                "value": 273.15,
            }
        },
        {
            "properties": {
                "from": "2024-12-07T00:00:00Z",
                "value": 274.15,
            }
        },
    ]
}

MOCK_FORECAST_RESPONSE = {
    "domain": {
        "axes": {"t": {"values": ["2024-12-06T00:00:00Z", "2024-12-07T00:00:00Z"]}},
    },
    "ranges": {"temperature-2m": {"values": [273.15, 274.15]}},
}

# Tests
@pytest.mark.asyncio
async def test_weather_api_single_request():
    """Test the /weather endpoint with a single WeatherRequest."""
    with patch("httpx.AsyncClient.get", AsyncMock(return_value=AsyncMock(status_code=200, json=AsyncMock(return_value=MOCK_WEATHER_RESPONSE)))):
        request_data = {
            "parameter": "temperature-2m",
            "limit": 2,
            "resolution": "hour",
            "time_to": "2024-12-07",
            "time_from": "2024-12-06",
        }
        response = client.get("/weather", json=request_data)
        assert response.status_code == 200
        result = response.json()
        assert result["parameterId"] == "temperature-2m"
        assert result["values"] == [0.0, 1.0]  # Converted from Kelvin to Celsius


@pytest.mark.asyncio
async def test_forecast_api_single_request():
    """Test the /forecast endpoint with a single ForecastRequest."""
    with patch("httpx.AsyncClient.get", AsyncMock(return_value=AsyncMock(status_code=200, json=AsyncMock(return_value=MOCK_FORECAST_RESPONSE)))):
        request_data = {
            "coords": "55.6761,12.5683",
            "crs": "EPSG:4326",
            "parameter": "temperature-2m",
        }
        response = client.get("/forecast", json=request_data)
        assert response.status_code == 200
        result = response.json()
        assert result["parameterId"] == "temperature-2m"
        assert result["values"] == [0.0, 1.0]  # Converted from Kelvin to Celsius
