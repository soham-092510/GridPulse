from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import settings

class ReliabilityRiskEngine:
    """
    Evaluates feeder loading margin, transformer capacity headroom,
    and predicts impending energy shortages or thermal overloads.
    """
    
    def __init__(self, feeder_capacity_kw: Optional[float] = None):
        self.feeder_capacity_kw = feeder_capacity_kw or settings.DEFAULT_FEEDER_CAPACITY_KW
        
    def assess_risk(
        self,
        current_demand_kw: float,
        solar_generation_kw: float,
        battery_soc_pct: float,
        battery_capacity_kwh: float,
        forecast_points_1h: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assesses live risk and looks ahead 1 hour for potential peak overload or shortage.
        """
        net_import_kw = max(0.0, current_demand_kw - solar_generation_kw)
        loading_pct = (net_import_kw / self.feeder_capacity_kw) * 100.0
        
        # Available battery power headroom
        battery_usable_kwh = max(0.0, (battery_soc_pct - 20.0) / 100.0 * battery_capacity_kwh)
        battery_max_discharge_kw = min(settings.DEFAULT_BATTERY_MAX_POWER_KW, battery_usable_kwh * 2.0)
        
        # Check peak in next 1 hour
        max_upcoming_net_kw = net_import_kw
        critical_window = None
        for pt in forecast_points_1h:
            upcoming_net = pt.get("predicted_net_load_kw", 0.0)
            if upcoming_net > max_upcoming_net_kw:
                max_upcoming_net_kw = upcoming_net
                critical_window = pt.get("target_time")
                
        projected_loading_pct = (max_upcoming_net_kw / self.feeder_capacity_kw) * 100.0
        
        # Risk classification
        if projected_loading_pct > 105.0:
            risk_level = "CRITICAL"
            shortage_kw = max_upcoming_net_kw - self.feeder_capacity_kw
            reason = f"Impending Feeder Overload: Net demand ({max_upcoming_net_kw:.1f} kW) exceeds safe feeder limit ({self.feeder_capacity_kw:.0f} kW) by {shortage_kw:.1f} kW around {critical_window[-8:-3] if critical_window else 'shortly'}."
        elif projected_loading_pct > 88.0:
            risk_level = "HIGH"
            reason = f"High Transformer Stress: Feeder projected to reach {projected_loading_pct:.1f}% capacity. Flexibility activation recommended."
        elif projected_loading_pct > 75.0:
            risk_level = "MEDIUM"
            reason = f"Moderate Loading ({projected_loading_pct:.1f}%). Normal reserve margin; monitoring solar and EV trends."
        else:
            risk_level = "LOW"
            reason = f"Grid Feeder Healthy: {projected_loading_pct:.1f}% loading with ample headroom ({self.feeder_capacity_kw - max_upcoming_net_kw:.1f} kW available)."
            
        return {
            "risk_level": risk_level,
            "feeder_capacity_kw": self.feeder_capacity_kw,
            "current_loading_pct": round(loading_pct, 1),
            "projected_loading_pct": round(projected_loading_pct, 1),
            "available_battery_kw": round(battery_max_discharge_kw, 1),
            "headroom_kw": round(max(0.0, self.feeder_capacity_kw - max_upcoming_net_kw), 1),
            "status_reason": reason,
            "critical_window": critical_window
        }

risk_engine = ReliabilityRiskEngine()
