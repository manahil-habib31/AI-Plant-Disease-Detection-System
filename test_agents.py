import pytest
from app import confidence_agent, disease_agent, decision_agent

def test_confidence_low_middle():
    input_val = 0.50
    expected  = "Low"
    actual    = confidence_agent(input_val)
    print(f"\nInput: confidence_agent({input_val})")
    print(f"Expected: {expected} | Actual: {actual}")
    assert actual == expected


def test_confidence_low_boundary_start():
    input_val = 0.45
    expected  = "Low"
    actual    = confidence_agent(input_val)
    print(f"\nInput: confidence_agent({input_val})")
    print(f"Expected: {expected} | Actual: {actual}")
    assert actual == expected


def test_confidence_low_boundary_end():
    input_val = 0.55
    expected  = "Low"
    actual    = confidence_agent(input_val)
    print(f"\nInput: confidence_agent({input_val})")
    print(f"Expected: {expected} | Actual: {actual}")
    assert actual == expected


def test_confidence_high_above():
    input_val = 0.90
    expected  = "High"
    actual    = confidence_agent(input_val)
    print(f"\nInput: confidence_agent({input_val})")
    print(f"Expected: {expected} | Actual: {actual}")
    assert actual == expected


def test_confidence_high_below():
    input_val = 0.10
    expected  = "High"
    actual    = confidence_agent(input_val)
    print(f"\nInput: confidence_agent({input_val})")
    print(f"Expected: {expected} | Actual: {actual}")
    assert actual == expected


def test_confidence_medium():
    input_val = 0.60
    expected  = "Medium"
    actual    = confidence_agent(input_val)
    print(f"\nInput: confidence_agent({input_val})")
    print(f"Expected: {expected} | Actual: {actual}")
    assert actual == expected


# ============================================================
# AGENT 2: disease_agent()
# Logic:
#   p >= 0.25  → "Diseased"
#   p <  0.25  → "Healthy"
# ============================================================

def test_disease_exactly_at_threshold():
    input_val = 0.25
    expected  = "Diseased"
    actual    = disease_agent(input_val)
    print(f"\nInput: disease_agent({input_val})")
    print(f"Expected: {expected} | Actual: {actual}")
    assert actual == expected


def test_disease_above_threshold():
    input_val = 0.75
    expected  = "Diseased"
    actual    = disease_agent(input_val)
    print(f"\nInput: disease_agent({input_val})")
    print(f"Expected: {expected} | Actual: {actual}")
    assert actual == expected


def test_disease_healthy():
    input_val = 0.15
    expected  = "Healthy"
    actual    = disease_agent(input_val)
    print(f"\nInput: disease_agent({input_val})")
    print(f"Expected: {expected} | Actual: {actual}")
    assert actual == expected


def test_disease_just_below_threshold():
    input_val = 0.24
    expected  = "Healthy"
    actual    = disease_agent(input_val)
    print(f"\nInput: disease_agent({input_val})")
    print(f"Expected: {expected} | Actual: {actual}")
    assert actual == expected


# ============================================================
# AGENT 3: decision_agent()
# Logic:
#   p >= 0.35  → High Risk,     red
#   p >= 0.25  → Moderate Risk, orange
#   else       → Low Risk,      green
# ============================================================

def test_decision_high_risk_status_and_color():
    input_val       = 0.80
    expected_status = "High Risk"
    expected_color  = "red"
    actual          = decision_agent(input_val)
    print(f"\nInput: decision_agent({input_val})")
    print(f"Expected: {expected_status}, {expected_color} | Actual: {actual['status']}, {actual['color']}")
    assert actual["status"] == expected_status
    assert actual["color"]  == expected_color


def test_decision_high_risk_at_boundary():
    input_val       = 0.35
    expected_status = "High Risk"
    actual          = decision_agent(input_val)
    print(f"\nInput: decision_agent({input_val})")
    print(f"Expected: {expected_status} | Actual: {actual['status']}")
    assert actual["status"] == expected_status


def test_decision_moderate_risk():
    input_val       = 0.30
    expected_status = "Moderate Risk"
    expected_color  = "orange"
    actual          = decision_agent(input_val)
    print(f"\nInput: decision_agent({input_val})")
    print(f"Expected: {expected_status}, {expected_color} | Actual: {actual['status']}, {actual['color']}")
    assert actual["status"] == expected_status
    assert actual["color"]  == expected_color


def test_decision_low_risk():
    input_val       = 0.10
    expected_status = "Low Risk"
    expected_color  = "green"
    actual          = decision_agent(input_val)
    print(f"\nInput: decision_agent({input_val})")
    print(f"Expected: {expected_status}, {expected_color} | Actual: {actual['status']}, {actual['color']}")
    assert actual["status"] == expected_status
    assert actual["color"]  == expected_color


def test_decision_recommendations_not_empty():
    input_val = 0.50
    actual    = decision_agent(input_val)
    print(f"\nInput: decision_agent({input_val})")
    print(f"Expected: recommendations > 0 | Actual: {len(actual['recommendations'])}")
    assert len(actual["recommendations"]) > 0