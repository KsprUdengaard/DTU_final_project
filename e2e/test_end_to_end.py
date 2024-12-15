import pytest
from playwright.sync_api import sync_playwright

def test_weather_page_functionality():
    """Test navigation to 'Weather Data' and its functionality."""
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)  # Use headless=True for faster runs
        context = browser.new_context()
        page = context.new_page()

        page.goto("http://localhost:8501")

        page.locator('text=Historical Weather Data').click()

        page.wait_for_timeout(1000)

        assert page.get_by_role("heading", name="Weather Data").is_visible(), "'Weather Data' heading not found"

        assert page.locator('input[aria-label="From Date"]')
        assert page.locator('input[aria-label="To Date"]')
        assert page.locator('select[aria-label="Choose a resolution"]')

        request_button = page.locator('button:has-text("Request Data")')
        assert request_button.is_visible(), "'Request Data' button is not visible"

        request_button.click()

        page.wait_for_timeout(5000)

        # List of tabs
        tabs = ["Humidity", "Temperature", "Wind speed", "Pressure", "Radiation", "Acc Precipitation", "Cloud cover"]

        # Iterate through each tab and click
        for tab in tabs:
            tab_element = page.get_by_role("tab", name=tab)
            assert tab_element.is_visible(), f"Tab '{tab}' is not visible"
            tab_element.click()
            if tab == "Acc Precipitation":
                tab = "Precipitation"
            text_element = page.get_by_text(f"Historical Average {tab}")
            assert text_element.is_visible(), f"'Historical Average {tab}' text not found"

        browser.close()
            
def test_model_parameters_labels():
    """Test that all model parameter labels are visible."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Use headless=True for faster runs
        context = browser.new_context()
        page = context.new_page()

        page.goto("http://localhost:8501")

        page.locator('text=Model Parameters').click()

        page.wait_for_timeout(2000)

        # List of labels to check
        labels = ["gamma", "max_depth", "eta", "subsample", "colsample_bytree", "min_child_weight"]

        # Iterate over the labels and check visibility
        for label in labels:
            label_element = page.get_by_text(label)
            assert label_element.is_visible(), f"Label '{label}' is not visible"

        retrain_button = page.locator('button:has-text("Retrain model")')
        assert retrain_button.is_visible(), "'Retrain model' button is not visible"

        # Click the button
        retrain_button.click()

        page.wait_for_selector("text=Model Evaluation Metrics", timeout=10000)

        # Validate the table headers
        headers = ["Metric", "Good Value", "Interpretation", "Results"]
        for header in headers:
            header_element = page.get_by_role("columnheader", name=header)
            assert header_element.is_visible(), f"Header '{header}' is not visible"

        # Validate the table data
        metrics = ["RMSE", "MAE", "R²", "RSD%"]
        for metric in metrics:
            metric_element = page.locator(f"text={metric}")
            assert metric_element.is_visible(), f"Metric '{metric}' is not visible"

        browser.close()

def test_forecast_page_plot_headers():
    """Test navigation to the Forecast page, clicking the button, and validating plot headers."""
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)  # Use headless=True for faster runs
        context = browser.new_context()
        page = context.new_page()

        page.goto("http://localhost:8501")

        page.locator('text=Forecast').click()
        page.wait_for_timeout(1000)

        request_button = page.locator('button:has-text("Request Data")')
        assert request_button.is_visible(), "'Request Data' button is not visible"

        request_button.click()

        # Wait for 20 seconds to allow the plots to load
        page.wait_for_timeout(20000)

        spot_pricer_header = page.get_by_text("Spot price predictions for DK1 [DKK]")
        assert spot_pricer_header.is_visible()
        # Validate plot header
        tabs = {"Humidity":"Humidity [%]", 
                "Temperature":"Temperature [°C]", 
                "Wind speed":"Wind speed [m/s]", 
                "Pressure":"Pressure [hPa]", 
                "Radiation":"Radiation [W/m²]", 
                "Acc Precipitation":"Precipitation [mm]", 
                "Cloud cover":"Cloud cover [%]"}

        # Iterate through each tab and click
        for tab in tabs:
            tab_element = page.get_by_role("tab", name=tab)
            assert tab_element.is_visible(), f"Tab '{tab}' is not visible"
            tab_element.click()
            text_element = page.get_by_text(tabs[tab])
            assert text_element.is_visible()

        browser.close()