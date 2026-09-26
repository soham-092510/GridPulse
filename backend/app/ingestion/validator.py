from typing import Tuple, Dict, Any, Optional
from datetime import datetime

class DataValidationEngine:
    """
    Validates physical plausibility, rate of change, and sensor integrity
    of incoming telemetry measurements.
    """
    
    PHYSICAL_LIMITS = {
        "active_power": {"min": -10.0, "max": 500.0, "max_step": 60.0}, # kW
        "voltage": {"min": 170.0, "max": 480.0, "max_step": 30.0},       # V
        "current": {"min": 0.0, "max": 800.0, "max_step": 150.0},         # A
        "power_factor": {"min": 0.4, "max": 1.0, "max_step": 0.5},       # cos_phi
        "battery_soc": {"min": 0.0, "max": 100.0, "max_step": 20.0},      # %
        "solar_power": {"min": 0.0, "max": 300.0, "max_step": 80.0},      # kW
        "temperature": {"min": -10.0, "max": 58.0, "max_step": 10.0},     # C
        "solar_radiation": {"min": 0.0, "max": 1400.0, "max_step": 600.0},# W/m2
        "cloud_cover": {"min": 0.0, "max": 100.0, "max_step": 80.0},     # %
    }
    
    def __init__(self):
        # Keeps last known valid reading per (device_id, metric) for rate of change checks
        self._last_values: Dict[Tuple[str, str], float] = {}
        self._last_timestamps: Dict[Tuple[str, str], datetime] = {}
        
    def validate(
        self,
        device_id: str,
        metric: str,
        value: float,
        timestamp: Optional[datetime] = None
    ) -> Tuple[str, float, Optional[str]]:
        """
        Validates a single normalized telemetry point.
        Returns: (quality_status, confidence_score, rejection_or_warning_reason)
        quality_status in ['VALID', 'SUSPECT', 'REJECTED']
        """
        ts = timestamp or datetime.utcnow()
        key = (device_id, metric)
        
        limits = self.PHYSICAL_LIMITS.get(metric)
        if not limits:
            # Metric without strict boundary rules
            self._last_values[key] = value
            self._last_timestamps[key] = ts
            return "VALID", 1.0, None
            
        # 1. Hard Physical Range Check
        if value < limits["min"] or value > limits["max"]:
            reason = f"Physical range violation: {value} outside [{limits['min']}, {limits['max']}]"
            return "REJECTED", 0.0, reason
            
        # 2. Rate of Change / Step jump check
        last_val = self._last_values.get(key)
        if last_val is not None:
            step = abs(value - last_val)
            max_step = limits.get("max_step", 1e9)
            if step > max_step * 2.0:
                reason = f"Extreme instantaneous jump: delta={round(step, 2)} exceeds 2x max_step ({max_step * 2.0})"
                return "REJECTED", 0.0, reason
            elif step > max_step:
                reason = f"Suspicious rapid change: delta={round(step, 2)} exceeds expected max_step ({max_step})"
                self._last_values[key] = value
                self._last_timestamps[key] = ts
                return "SUSPECT", 0.6, reason
                
        # Passed all checks
        self._last_values[key] = value
        self._last_timestamps[key] = ts
        return "VALID", 1.0, None

validator_engine = DataValidationEngine()
