from typing import Dict, Any, Tuple
import re

class MeasurementNormalizer:
    """Normalizes heterogeneous incoming telemetry into canonical units and metrics."""
    
    UNIT_MAPPINGS = {
        # Power
        "w": ("kW", 0.001),
        "watt": ("kW", 0.001),
        "watts": ("kW", 0.001),
        "kw": ("kW", 1.0),
        "kilowatt": ("kW", 1.0),
        "mw": ("kW", 1000.0),
        "megawatt": ("kW", 1000.0),
        
        # Energy
        "wh": ("kWh", 0.001),
        "kwh": ("kWh", 1.0),
        "mwh": ("kWh", 1000.0),
        
        # Voltage
        "v": ("V", 1.0),
        "volt": ("V", 1.0),
        "volts": ("V", 1.0),
        "kv": ("V", 1000.0),
        
        # Current
        "a": ("A", 1.0),
        "amp": ("A", 1.0),
        "amps": ("A", 1.0),
        "ma": ("A", 0.001),
        
        # Power factor
        "pf": ("cos_phi", 1.0),
        "cos_phi": ("cos_phi", 1.0),
        
        # Solar Irradiance
        "w/m2": ("W/m2", 1.0),
        "w/m^2": ("W/m2", 1.0),
        "wm-2": ("W/m2", 1.0),
        
        # Temperature
        "c": ("C", 1.0),
        "degc": ("C", 1.0),
        "f": ("C", lambda f: (f - 32.0) * 5.0 / 9.0),
        
        # Percentage
        "%": ("%", 1.0),
        "pct": ("%", 1.0),
        "percent": ("%", 1.0),
    }
    
    METRIC_ALIASES = {
        "p": "active_power",
        "power": "active_power",
        "active_power": "active_power",
        "activepower": "active_power",
        "kw": "active_power",
        "demand": "active_power",
        "solar_power": "solar_power",
        "generation": "solar_power",
        "pv": "solar_power",
        "soc": "battery_soc",
        "state_of_charge": "battery_soc",
        "v": "voltage",
        "volts": "voltage",
        "i": "current",
        "amps": "current",
        "pf": "power_factor",
        "cosphi": "power_factor",
        "temp": "temperature",
        "temperature": "temperature",
    }
    
    @classmethod
    def normalize(cls, metric: str, value: float, raw_unit: str) -> Tuple[str, float, str]:
        """
        Normalizes metric name, numerical value, and standard unit.
        Returns: (canonical_metric, normalized_value, canonical_unit)
        """
        clean_metric = cls.METRIC_ALIASES.get(metric.lower().strip(), metric.lower().strip())
        unit_key = raw_unit.lower().strip()
        
        if unit_key in cls.UNIT_MAPPINGS:
            target_unit, factor = cls.UNIT_MAPPINGS[unit_key]
            if callable(factor):
                norm_val = factor(value)
            else:
                norm_val = value * factor
            return clean_metric, round(norm_val, 4), target_unit
        
        # Fallback if unit is unknown
        return clean_metric, round(value, 4), raw_unit
