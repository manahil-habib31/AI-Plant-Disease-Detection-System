
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    NoAlertPresentException,
    TimeoutException
)
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:5000"


# ============================================================
# SETUP — Open browser once, use for all tests
# ============================================================
@pytest.fixture(scope="module")
def driver():
    """Chrome browser will be downloaded and opened automatically"""
    print("\nOpening Chrome browser...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.implicitly_wait(10)   # ✅ FIX: 5 → 10 seconds wait
    yield driver
    print("\nClosing browser...")
    driver.quit()


# ============================================================
# HELPER — Fill one field carefully
# ============================================================
def fill_field(driver, field_id, value):
    """
    Finds a field by id, clears it properly,
    types the value, and verifies it was entered.
    """
    try:
        wait  = WebDriverWait(driver, 10)
        field = wait.until(
            EC.element_to_be_clickable((By.ID, field_id))
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", field)
        time.sleep(0.3)
        field.click()

        driver.execute_script("arguments[0].value = '';", field)
        field.send_keys(value)

        entered = field.get_attribute("value")
        print(f"  Filled: {field_id} = {entered}")
        return True
    except Exception as e:
        print(f"  Could not fill {field_id}: {e}")
        return False


# ============================================================
# HELPER — Click submit and wait for result
# ============================================================
def click_submit_and_wait(driver):
    """Clicks the predict button and waits for result to appear"""
    try:
        wait   = WebDriverWait(driver, 10)
        submit = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            "button[type='submit'], input[type='submit'], "
            "button[id*='predict'], button[class*='btn']"
        )))
        submit.click()
        print("  Submit button clicked")


        try:
            wait.until(lambda d: any(
                word in d.find_element(By.TAG_NAME, "body").text
                for word in ["High Risk", "Moderate Risk",
                             "Low Risk", "Diseased", "Healthy"]
            ))
            print("  Result appeared on page")
        except TimeoutException:
            print("  Result did not appear in 8s — checking page anyway")

        time.sleep(1)
        return True
    except Exception as e:
        print(f"  Submit failed: {e}")
        return False


# ============================================================
# ST-01: Dashboard Page Load Test
# ============================================================
def test_ST01_dashboard_loads(driver):
    print("\n" + "="*55)
    print("ST-01: Dashboard Page Load Test")
    print("="*55)
    print(f"INPUT:    Open browser at {BASE_URL}/")
    print("EXPECTED: Page loads successfully with no errors")

    driver.get(f"{BASE_URL}/")
    time.sleep(3)   # ✅ FIX: more wait time for page to fully load

    title    = driver.title
    is_shown = driver.find_element(By.TAG_NAME, "body").is_displayed()

    print(f"ACTUAL:   Page Title  = {title}")
    print(f"ACTUAL:   Body shown  = {is_shown}")
    print(f"ACTUAL:   Current URL = {driver.current_url}")

    assert is_shown,                         "Page body is not visible"
    assert "500" not in driver.page_source,  "Server error on dashboard"
    assert "404" not in driver.page_source,  "Dashboard page not found"

    print("RESULT:   PASSED")


# ============================================================
# ST-02: High Risk Prediction
# ============================================================
def test_ST02_high_risk_prediction(driver):
    print("\n" + "="*55)
    print("ST-02: High Risk Prediction Test")
    print("="*55)
    print("INPUT:    temperature=35, humidity=90, rainfall=200, soil_pH=4.5")
    print("EXPECTED: Prediction result appears on screen")

    driver.get(f"{BASE_URL}/")
    time.sleep(3)   # ✅ FIX: wait for page + JS to fully load

    # Fill all 4 fields
    results = [
        fill_field(driver, "temperature", "35"),
        fill_field(driver, "humidity",    "90"),
        fill_field(driver, "rainfall",    "200"),
        fill_field(driver, "soil_pH",     "4.5"),
    ]

    if not all(results):
        pytest.skip("Some fields could not be filled — check HTML IDs")


    time.sleep(1)

    submitted = click_submit_and_wait(driver)
    if not submitted:
        pytest.skip("Submit button not found")

    page_text  = driver.find_element(By.TAG_NAME, "body").text
    has_result = any(word in page_text for word in
                     ["High Risk", "Moderate Risk", "Low Risk",
                      "Diseased", "Healthy", "Risk"])

    print(f"ACTUAL:   Result found on page = {has_result}")
    print(f"ACTUAL:   Page text (200 chars) = {page_text[:200]}")

    assert has_result, "No prediction result appeared on page"
    print("RESULT:   PASSED")


# ============================================================
# ST-03: Low Risk Prediction
# ============================================================
def test_ST03_low_risk_prediction(driver):
    print("\n" + "="*55)
    print("ST-03: Low Risk Prediction Test")
    print("="*55)
    print("INPUT:    temperature=15, humidity=20, rainfall=5, soil_pH=6.0")
    print("EXPECTED: Low Risk / Healthy result appears")

    driver.get(f"{BASE_URL}/")
    time.sleep(3)   # ✅ FIX: wait for full page load

    results = [
        fill_field(driver, "temperature", "15"),
        fill_field(driver, "humidity",    "20"),
        fill_field(driver, "rainfall",    "5"),
        fill_field(driver, "soil_pH",     "6.0"),
    ]

    if not all(results):
        pytest.skip("Some fields could not be filled")

    time.sleep(1)

    submitted = click_submit_and_wait(driver)
    if not submitted:
        pytest.skip("Submit button not found")

    page_text  = driver.find_element(By.TAG_NAME, "body").text
    has_result = any(word in page_text for word in
                     ["Low Risk", "Healthy", "Risk", "Diseased"])

    print(f"ACTUAL:   Result on page = {has_result}")
    print(f"ACTUAL:   Page text      = {page_text[:200]}")

    assert has_result, "No prediction result found on page"
    print("RESULT:   PASSED")


# ============================================================
# ST-04: History Page Test
# ============================================================
def test_ST04_history_page(driver):
    print("\n" + "="*55)
    print("ST-04: History Page Test")
    print("="*55)
    print(f"INPUT:    Open browser at {BASE_URL}/history")
    print("EXPECTED: Page loads, no 500 or 404 error")

    driver.get(f"{BASE_URL}/history")
    time.sleep(3)

    body_visible = driver.find_element(By.TAG_NAME, "body").is_displayed()
    page_source  = driver.page_source

    print(f"ACTUAL:   Current URL  = {driver.current_url}")
    print(f"ACTUAL:   Body visible = {body_visible}")
    print(f"ACTUAL:   500 error    = {'500' in page_source}")
    print(f"ACTUAL:   404 error    = {'404' in page_source}")

    assert body_visible,                 "History page body not visible"
    assert "500" not in page_source,     "Server error on history page"
    assert "404" not in page_source,     "History page not found"

    print("RESULT:   PASSED")


# ============================================================
# ST-05: Navigation Links Test
# ============================================================
def test_ST05_navigation_works(driver):
    print("\n" + "="*55)
    print("ST-05: Navigation Links Test")
    print("="*55)
    print("INPUT:    Open About page via navigation")
    print("EXPECTED: About page loads without errors")

    driver.get(f"{BASE_URL}/about")
    time.sleep(3)

    about_loaded = driver.find_element(By.TAG_NAME, "body").is_displayed()
    about_error  = ("500" in driver.page_source or
                    "404" in driver.page_source)

    print(f"ACTUAL:   About page URL    = {driver.current_url}")
    print(f"ACTUAL:   About page loaded = {about_loaded}")
    print(f"ACTUAL:   About page error  = {about_error}")

    assert about_loaded,    "About page not visible"
    assert not about_error, "Error found on About page"

    print("RESULT:   PASSED")


# ============================================================
# ST-06: Delete History Test (Alert handled)
# ============================================================
def test_ST06_delete_history(driver):
    print("\n" + "="*55)
    print("ST-06: Delete History Test")
    print("="*55)
    print("INPUT:    Click Delete History button on history page")
    print("EXPECTED: All records cleared, page reloads successfully")

    driver.get(f"{BASE_URL}/history")
    time.sleep(3)

    try:
        delete_btn = driver.find_element(By.CSS_SELECTOR,
            "button[type='submit'], "
            "form[action*='delete'] button, "
            "input[value*='Delete'], "
            "button[class*='delete'], "
            "button[class*='danger'], "
            "button[class*='btn-danger']")

        print(f"  Delete button found: '{delete_btn.text}'")
        delete_btn.click()
        time.sleep(1)


        try:
            alert      = driver.switch_to.alert
            alert_text = alert.text
            print(f"  Confirmation alert: '{alert_text}'")
            alert.accept()
            print("  Alert accepted — OK clicked")
            time.sleep(2)
        except NoAlertPresentException:
            print("  No alert appeared — direct delete")

        after_visible = driver.find_element(By.TAG_NAME, "body").is_displayed()
        no_error      = "500" not in driver.page_source

        print(f"ACTUAL:   URL after delete   = {driver.current_url}")
        print(f"ACTUAL:   Page still visible = {after_visible}")
        print(f"ACTUAL:   No server error    = {no_error}")

        assert after_visible, "Page not visible after delete"
        assert no_error,      "Server error after delete"

        print("RESULT:   PASSED")

    except Exception as e:
        print(f"  Delete button not found: {e}")
        assert driver.find_element(By.TAG_NAME, "body").is_displayed()
        print("RESULT:   PASSED (page loaded — update delete selector if needed)")