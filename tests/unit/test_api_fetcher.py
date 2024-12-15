import pytest
from unittest.mock import patch, Mock
import requests
from dashboard.utility_classes import ApiFetcher

@patch('requests.get')
def test_fetch_data_get_success(mock_get):
    """Test fetch_data with a successful GET request."""
    mock_response = Mock()
    mock_response.json.return_value = {"key": "value"}
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    url = "http://example.com/api"
    payload = {"param": "test"}
    result = ApiFetcher.fetch_data(url, payload, method="get")

    mock_get.assert_called_once_with(url, json=payload)
    assert result == {"key": "value"}

@patch('requests.post')
def test_fetch_data_post_success(mock_post):
    """Test fetch_data with a successful POST request."""
    mock_response = Mock()
    mock_response.json.return_value = {"key": "value"}
    mock_response.status_code = 201
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    url = "http://example.com/api"
    payload = {"param": "test"}
    result = ApiFetcher.fetch_data(url, payload, method="post")

    mock_post.assert_called_once_with(url, json=payload)
    assert result == {"key": "value"}

@patch('requests.get')
def test_fetch_data_http_error(mock_get):
    """Test fetch_data handling an HTTP error."""
    mock_response = Mock()
    mock_response.status_code = 404
    http_error = requests.exceptions.HTTPError("HTTP Error")
    http_error.response = mock_response
    
    mock_response.raise_for_status.side_effect = http_error
    mock_get.return_value = mock_response

    url = "http://example.com/api"
    payload = {"param": "test"}
    result = ApiFetcher.fetch_data(url, payload, method="get")

    assert result["error"] == "HTTP error occurred: HTTP Error"
    assert result["status_code"] == 404

@patch('requests.get')
def test_fetch_data_request_exception(mock_get):
    """Test fetch_data handling a generic request exception."""
    mock_get.side_effect = requests.exceptions.RequestException("Request Exception")

    url = "http://example.com/api"
    payload = {"param": "test"}
    result = ApiFetcher.fetch_data(url, payload, method="get")

    assert result["error"] == "API fetch error: Request Exception"
    assert result["status_code"] == 500
