import pytest
from api.api_utility_classes import Transformer

@pytest.mark.parametrize(
    "values, parameter, expected",
    [
      
        ([273.15, 274.15, 275.15], 'temperature-2m', [0.0, 1.0, 2.0]),
        ([300.15, 310.15, 320.15], 'temperature-2m', [27.0, 37.0, 47.0]),
        ([0.0], 'temperature-2m', [-273.1]),
        ([], 'temperature-2m', []),

        ([101325, 102000], 'pressure-surface', [1013.2, 1020.0]),
        ([90000], 'pressure-surface', [900.0]),
        ([0], 'pressure-surface', [0.0]),
        ([], 'pressure-surface', []),  

        ([0, 3600, 7200], 'global-radiation-flux', [0.0, 1.0, 1.0]),
        ([100, 150, 250], 'global-radiation-flux', [0.0, 0.0, 0.0]),
        ([10], 'global-radiation-flux', [0.0]), 
        ([], 'global-radiation-flux', []),


        ([0, 5, 10], 'total-precipitation', [0.0, 5.0, 5.0]),
        ([10, 20, 35], 'total-precipitation', [0.0, 10.0, 15.0]),
        ([50], 'total-precipitation', [0.0]),  
        ([], 'total-precipitation', []),

        ([1.234, 2.345, 3.456], 'unknown', [1.2, 2.3, 3.5]),
        ([0.123456], 'unknown', [0.1]),
        ([], 'unknown', []),
    ]
)


def test_transform(values, parameter, expected):
    transformer = Transformer()
    result = transformer.transform(values, parameter)
    assert result == expected, f"Failed for parameter '{parameter}' with values {values}"


def test_transform_invalid_data():
    transformer = Transformer()

    with pytest.raises(TypeError):
        transformer.transform(["a", "b", "c"], "temperature-2m")

    with pytest.raises(TypeError):
        transformer.transform(None, "pressure-surface")

    with pytest.raises(TypeError):
        transformer.transform([1, "b", 3], "total-precipitation")


def test_transform_large_input():
    transformer = Transformer()
    large_input = [273.15 + i for i in range(10000)]
    expected_output = [round(x - 273.15, 1) for x in large_input]
    result = transformer.transform(large_input, "temperature-2m")
    assert result == expected_output, "Large input transformation failed."
