import pytest
from datetime import datetime
from app.engines.optimizer import flexibility_optimizer

def test_milp_flexibility_optimizer():
    t_evening_peak = datetime(2026, 9, 21, 18, 30, 0)
    
    # Solve flexibility optimization during evening peak
    res = flexibility_optimizer.solve_flexibility_schedule(
        current_time=t_evening_peak,
        current_demand_kw=102.0,
        current_solar_kw=5.0,
        battery_soc_pct=80.0,
        battery_capacity_kwh=100.0,
        battery_max_power_kw=30.0,
        active_ev_charging_kw=21.0,
        ev_consent_pct=80.0,
        feeder_capacity_kw=125.0
    )
    
    assert res["status"] in ["OPTIMAL", "FEASIBLE"]
    assert res["peak_reduction_achieved_kw"] > 0
    assert res["optimized_peak_kw"] < res["baseline_peak_kw"]
    
    actions = res["recommended_actions"]
    assert len(actions) >= 1
    
    # Verify battery action
    batt_act = [a for a in actions if a["action_type"] == "BATTERY_DISCHARGE"]
    if batt_act:
        assert batt_act[0]["expected_peak_reduction_kw"] > 0
        assert batt_act[0]["status"] == "RECOMMENDED"
        
        # Test approval workflow
        act_id = batt_act[0]["action_id"]
        approved = flexibility_optimizer.set_action_status(act_id, True)
        assert approved["status"] == "APPROVED"
