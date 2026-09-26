import pytest
from datetime import datetime
from app.engines.baseline_engine import baseline_engine
from app.engines.anomaly_engine import anomaly_engine

def test_baseline_stratification():
    t_monday_noon = datetime(2026, 9, 21, 12, 0, 0)
    base_cool = baseline_engine.get_expected_demand(t_monday_noon, ambient_temp_c=25.0)
    base_hot = baseline_engine.get_expected_demand(t_monday_noon, ambient_temp_c=36.0)
    
    assert base_cool["expected_kw"] > 0
    assert base_hot["expected_kw"] >= base_cool["expected_kw"]
    assert base_cool["min_expected_kw"] < base_cool["expected_kw"] < base_cool["max_expected_kw"]

def test_anomaly_spike_and_root_cause_attribution():
    t_evening = datetime(2026, 9, 21, 19, 0, 0)
    
    # Inject a 105 kW sudden demand spike with 35°C temperature and 7 active EVs drawing 24 kW
    anomalies = anomaly_engine.evaluate_live_state(
        timestamp=t_evening,
        current_demand_kw=105.0, # Expected is ~65-72 kW
        solar_generation_kw=0.0,
        battery_power_kw=0.0,
        ev_charging_kw=24.0,
        ev_active_count=7,
        temperature_c=35.5,
        cloud_cover_pct=20.0,
        solar_radiation_w_m2=0.0
    )
    
    assert len(anomalies) >= 1
    spike_event = [a for a in anomalies if a["anomaly_type"] == "demand_spike"][0]
    assert spike_event["severity"] in ["HIGH", "CRITICAL"]
    assert spike_event["deviation_pct"] > 30.0
    # Verify root cause text mentions temperature / air-conditioning and EV charging
    assert "air-conditioning" in spike_event["root_cause"].lower() or "temperature" in spike_event["root_cause"].lower()
    assert "ev" in spike_event["root_cause"].lower()
