import pytest
from app.ingestion.normalizer import MeasurementNormalizer
from app.ingestion.validator import DataValidationEngine

def test_measurement_normalizer_units():
    # Watts to kW
    metric, val, unit = MeasurementNormalizer.normalize("active_power", 5400.0, "W")
    assert metric == "active_power"
    assert val == 5.4
    assert unit == "kW"
    
    # Megawatts to kW
    metric, val, unit = MeasurementNormalizer.normalize("power", 0.085, "MW")
    assert metric == "active_power"
    assert val == 85.0
    assert unit == "kW"
    
    # Wh to kWh
    metric, val, unit = MeasurementNormalizer.normalize("energy", 12500.0, "Wh")
    assert val == 12.5
    assert unit == "kWh"

def test_data_validation_range_checks():
    val_engine = DataValidationEngine()
    
    # Normal active power reading
    quality, conf, reason = val_engine.validate("METER_01", "active_power", 45.0)
    assert quality == "VALID"
    assert conf == 1.0
    assert reason is None
    
    # Absurd out-of-range reading (e.g. 50,000 kW on a 500 kW limit)
    quality, conf, reason = val_engine.validate("METER_01", "active_power", 50000.0)
    assert quality == "REJECTED"
    assert conf == 0.0
    assert "Physical range violation" in reason

def test_data_validation_rate_of_change():
    val_engine = DataValidationEngine()
    # Step 1: Valid initial value
    val_engine.validate("METER_02", "active_power", 50.0)
    
    # Step 2: Instantaneous 250 kW jump (exceeds 2x max_step 60kW)
    quality, conf, reason = val_engine.validate("METER_02", "active_power", 300.0)
    assert quality == "REJECTED"
    assert "Extreme instantaneous jump" in reason
