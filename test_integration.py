import os
import json
import sqlite3
import pytest
from app import app, init_db

DB_PATH = "predictions.db"

@pytest.fixture
def client():
    # Ensure a clean database for each test run
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    init_db()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

    # Teardown: remove DB after tests
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


# ============================================================
# TEST 1: FULL PREDICTION FLOW (EXPECTED vs ACTUAL)
# ============================================================
def test_predict_full_flow(client):
    data = {
        "temperature": 30,
        "humidity": 80,
        "rainfall": 200,
        "soil_pH": 6.5
    }

    expected_keys = [
        "status",
        "disease_status",
        "risk_percentage",
        "confidence",
        "recommendations",
        "color"
        "severity"
    ]
    expected_status_values = ["High Risk", "Moderate Risk", "Low Risk"]
    expected_disease_values = ["Healthy", "Diseased"]
    expected_confidence_values = ["Low", "Medium", "High"]

    response = client.post(
        "/predict",
        data=json.dumps(data),
        content_type="application/json"
    )

    # Try to parse JSON even if status is not 200
    try:
        result = response.get_json()
    except Exception:
        result = None

    print("\n--- Integration Test: FULL PREDICTION FLOW ---")
    print("INPUT:", data)
    print("\nEXPECTED:")
    print("HTTP status: 200")
    print("JSON keys:", expected_keys)
    print("status ∈", expected_status_values)
    print("disease_status ∈", expected_disease_values)
    print("confidence ∈", expected_confidence_values)

    print("\nACTUAL:")
    print("HTTP status:", response.status_code)
    print("Response JSON:", result)

    # Assertions
    assert response.status_code == 200, "Expected HTTP 200 from /predict for valid input"
    assert isinstance(result, dict), "Response JSON must be an object"
    for key in expected_keys:
        assert key in result, f"Missing key in response JSON: {key}"

    # Validate value domains where possible
    assert result["status"] in expected_status_values, f"Unexpected status: {result['status']}"
    assert result["disease_status"] in expected_disease_values, f"Unexpected disease_status: {result['disease_status']}"
    assert result["confidence"] in expected_confidence_values, f"Unexpected confidence: {result['confidence']}"
    # risk_percentage should be numeric (int/float) or numeric string convertible to float
    try:
        rp = float(result["risk_percentage"])
        assert 0.0 <= rp <= 100.0
    except Exception:
        pytest.fail("risk_percentage is not a numeric value between 0 and 100")


# ============================================================
# TEST 2: CHECK DATABASE INSERT (EXPECTED vs ACTUAL)
# ============================================================
def test_prediction_saved_in_db(client):
    data = {
        "temperature": 28,
        "humidity": 70,
        "rainfall": 150,
        "soil_pH": 6.0
    }

    response = client.post(
        "/predict",
        data=json.dumps(data),
        content_type="application/json"
    )

    # Ensure the endpoint responded (200 or handled error)
    assert response.status_code == 200, "Expected HTTP 200 from /predict for valid input"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM prediction_history")
    count = c.fetchone()[0]

    print("\n--- DATABASE INSERT TEST ---")
    print("INPUT:", data)
    print("EXPECTED: COUNT > 0")
    print("ACTUAL COUNT:", count)

    assert count > 0, "prediction_history should contain at least one record after POST /predict"

    conn.close()


# ============================================================
# TEST 3: INVALID INPUT HANDLING (EXPECTED vs ACTUAL)
# ============================================================
def test_invalid_input(client):
    data = {
        "temperature": "abc",  # invalid type
        "humidity": 70,
        "rainfall": 150,
        "soil_pH": 6.0
    }

    response = client.post(
        "/predict",
        data=json.dumps(data),
        content_type="application/json"
    )

    # Try to parse JSON safely
    try:
        result = response.get_json()
    except Exception:
        result = None

    print("\n--- INVALID INPUT TEST ---")
    print("INPUT:", data)
    print("\nEXPECTED: HTTP 4xx or JSON containing 'error' key describing invalid input")
    print("ACTUAL HTTP status:", response.status_code)
    print("ACTUAL RESPONSE JSON:", result)

    # Accept either a 4xx status or a 200 with an "error" key in the JSON body
    if 400 <= response.status_code < 500:

        assert True
    else:
        # If server returned 200, ensure it returned an error payload
        assert isinstance(result, dict), "Expected JSON response for invalid input"
        assert "error" in result, "Expected 'error' key in response JSON for invalid input"