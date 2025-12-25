
import pytest
import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from engine.location_system import LocationManager

class MockTimeSystem:
    def __init__(self, hour=0):
        self.current_time = datetime(1995, 10, 14, hour, 0)

    def set_time(self, hour):
        self.current_time = self.current_time.replace(hour=hour)

def test_location_time_gating():
    # Setup
    loc_mgr = LocationManager()

    # Manually inject test data to avoid dependency on real files
    loc_mgr.locations = {
        "clinic_front": {
            "name": "Kaltvik Clinic",
            "enter_conditions": {
                "time_range": [7, 22],
                "time_msg": "Closed."
            }
        },
        "aurora_ridge": {
            "name": "Aurora Ridge",
            "enter_conditions": {
                "restricted_hours": [1, 3],
                "restricted_msg": "Too dangerous."
            }
        },
        "records_room": {
            "name": "Records Room",
            "enter_conditions": {
                "min_days_passed": 1,
                "days_msg": "Wait for tomorrow."
            }
        }
    }

    # Test 1: Clinic (Open 7-22)
    # Case A: Too early (02:00)
    game_state = {"time": datetime(1995, 10, 14, 2, 0), "days_passed": 0}
    allowed, reason = loc_mgr.can_enter("clinic_front", game_state)
    assert not allowed
    assert reason == "Closed."

    # Case B: Open (10:00)
    game_state["time"] = datetime(1995, 10, 14, 10, 0)
    allowed, reason = loc_mgr.can_enter("clinic_front", game_state)
    assert allowed

    # Test 2: Aurora Ridge (Restricted 01-03)
    # Case A: Safe (05:00)
    game_state["time"] = datetime(1995, 10, 14, 5, 0)
    allowed, reason = loc_mgr.can_enter("aurora_ridge", game_state)
    assert allowed

    # Case B: Dangerous (02:00)
    game_state["time"] = datetime(1995, 10, 14, 2, 0)
    allowed, reason = loc_mgr.can_enter("aurora_ridge", game_state)
    assert not allowed
    assert reason == "Too dangerous."

    # Test 3: Records Room (Min Days 1)
    # Case A: Day 0
    game_state["days_passed"] = 0
    allowed, reason = loc_mgr.can_enter("records_room", game_state)
    assert not allowed
    assert reason == "Wait for tomorrow."

    # Case B: Day 1
    game_state["days_passed"] = 1
    allowed, reason = loc_mgr.can_enter("records_room", game_state)
    assert allowed

if __name__ == "__main__":
    test_location_time_gating()
