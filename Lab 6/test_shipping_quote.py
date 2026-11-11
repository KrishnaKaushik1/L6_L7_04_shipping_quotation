import pytest
from shipping_quote import process_shipments, monitor_container_pressures

# Example test case:
def test_single_ground_shipment():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "is_fragile": False,
            "express_priority": False,
            "packages": [{"weight_kg": 10, "is_hazmat": False}]
        }
    ]
    result = process_shipments(shipments, 20.0)
    assert result["total_quote"] == 60.0
    assert result["status"] == "CLEARED"

# --- Tests for process_shipments ---

def test_invalid_shipments_type():
    with pytest.raises(ValueError):
        process_shipments(None, 10.0)

def test_negative_handling_fee():
    with pytest.raises(ValueError):
        process_shipments([], -5.0)

def test_unapproved_manifest():
    shipments = [{"manifest_approved": False}]
    result = process_shipments(shipments, 10.0)
    assert result["status"] == "NO_CARGO"

def test_invalid_transport_mode():
    shipments = [{"manifest_approved": True, "mode": "sea"}]
    result = process_shipments(shipments, 10.0)
    assert result["status"] == "NO_CARGO"

def test_air_standard_weight():
    # Air mode (base 12), weight <= 30. Cost = 10 (handling) + (10 * 12) = 130
    shipments = [{
        "manifest_approved": True,
        "mode": "air",
        "packages": [{"weight_kg": 10, "is_hazmat": False}]
    }]
    result = process_shipments(shipments, 10.0)
    assert result["total_quote"] == 130.0
    assert result["status"] == "CLEARED"

def test_ground_heavy_weight():
    # Ground mode (base 4), weight > 30. Cost = 5 (handling) + (40 * 4 * 1.5) = 245
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [{"weight_kg": 40, "is_hazmat": False}]
    }]
    result = process_shipments(shipments, 5.0)
    assert result["total_quote"] == 245.0

def test_invalid_weight():
    # Weight <= 0 gets rejected
    shipments = [{
        "manifest_approved": True,
        "packages": [{"weight_kg": 0}]
    }]
    # Handling fee is 0.0 so the total remains 0.0
    result = process_shipments(shipments, 0.0)
    assert result["status"] == "NO_CARGO"

def test_hazmat_and_fragile():
    # Hazmat + Fragile triggers cost 0 and breaks loop
    shipments = [{
        "manifest_approved": True,
        "is_fragile": True,
        "packages": [{"is_hazmat": True, "weight_kg": 10}]
    }]
    result = process_shipments(shipments, 10.0)
    assert result["total_quote"] == 0.0

def test_hazmat_not_fragile():
    # Hazmat only adds 50
    shipments = [{
        "manifest_approved": True,
        "is_fragile": False,
        "packages": [{"is_hazmat": True, "weight_kg": 10}]
    }]
    result = process_shipments(shipments, 10.0)
    # 10 handling + 50 hazmat = 60
    assert result["total_quote"] == 60.0

def test_express_priority():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "express_priority": True,
        "packages": [{"weight_kg": 10}]
    }]
    result = process_shipments(shipments, 0.0)
    # Cost: 10 * 4 = 40. Express: 40 * 1.25 = 50
    assert result["total_quote"] == 50.0

def test_flagged_review():
    # More than 3 rejected parcels flags the shipment
    shipments = [{
        "manifest_approved": True,
        "packages": [
            {"weight_kg": 0}, # Reject 1
            {"weight_kg": -1}, # Reject 2
            {"weight_kg": 0}, # Reject 3
            {"weight_kg": 0}  # Reject 4
        ]
    }]
    result = process_shipments(shipments, 10.0)
    assert result["status"] == "FLAGGED_REVIEW"

# --- Tests for monitor_container_pressures ---

def test_monitor_no_data():
    assert monitor_container_pressures([]) == "NO_DATA"
    assert monitor_container_pressures(None) == "NO_DATA"

def test_monitor_stable():
    # Pressures all >= 14.0
    logs = [[15.0, 14.5], [14.0, 16.0]]
    assert monitor_container_pressures(logs) == "STABLE"

def test_monitor_streak_reset():
    # Drops below 14.0 but doesn't hit 2 in a row
    logs = [[15.0, 13.5, 14.5, 13.0]]
    assert monitor_container_pressures(logs) == "STABLE"

def test_monitor_leak_detected():
    # Drops below 14.0 twice in a row
    logs = [[15.0, 13.9, 13.8]]
    assert monitor_container_pressures(logs) == "LEAK_DETECTED"