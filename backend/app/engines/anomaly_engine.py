import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.engines.baseline_engine import baseline_engine

class AnomalyEngine:
    """
    Detects abnormal energy behavior and investigates physical root causes
    by correlating telemetry across demand, weather, solar, EV, and battery subsystems.
    """
    
    def __init__(self):
        self.active_incidents: List[Dict[str, Any]] = []
        self.incident_history: List[Dict[str, Any]] = []
        
    def evaluate_live_state(
        self,
        timestamp: datetime,
        current_demand_kw: float,
        solar_generation_kw: float,
        battery_power_kw: float,
        ev_charging_kw: float,
        ev_active_count: int,
        temperature_c: float,
        cloud_cover_pct: float,
        solar_radiation_w_m2: float
    ) -> List[Dict[str, Any]]:
        """
        Evaluates current neighbourhood telemetry against baseline and physical models.
        Returns list of newly detected or active anomaly events.
        """
        anomalies = []
        
        # 1. Fetch Expected Baseline Values
        base_demand = baseline_engine.get_expected_demand(timestamp, temperature_c)
        expected_demand = base_demand["expected_kw"]
        std_demand = base_demand["std_kw"]
        
        base_solar = baseline_engine.get_expected_solar(timestamp, cloud_cover_pct)
        expected_solar = base_solar["expected_solar_kw"]
        
        hour = timestamp.hour + timestamp.minute / 60.0
        
        # -------------------------------------------------------------
        # CHECK 1: Demand Spike
        # -------------------------------------------------------------
        demand_deviation_pct = ((current_demand_kw - expected_demand) / max(10.0, expected_demand)) * 100.0
        if demand_deviation_pct > 25.0 and (current_demand_kw - expected_demand) > 12.0:
            severity = "CRITICAL" if demand_deviation_pct > 45.0 else ("HIGH" if demand_deviation_pct > 30.0 else "MEDIUM")
            
            # Root cause diagnostics
            causes = []
            if temperature_c > 33.0:
                cooling_surge_kw = round((temperature_c - 30.0) * 3.5, 1)
                causes.append(f"Elevated ambient temperature ({temperature_c:.1f}°C) driving approx ~{cooling_surge_kw} kW additional air-conditioning cooling load")
            if ev_charging_kw > 15.0 or ev_active_count >= 5:
                causes.append(f"Concurrent uncoordinated EV charging cluster ({ev_active_count} active vehicles drawing {ev_charging_kw:.1f} kW)")
            if 18.0 <= hour <= 21.5:
                causes.append("Coincident domestic evening activity peak (cooking, lighting, appliances)")
                
            if not causes:
                causes.append("Unscheduled heavy commercial or municipal pump operation")
                
            root_cause_text = " + ".join(causes)
            
            event = {
                "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": timestamp.isoformat(),
                "device_id": "COMMUNITY_FEEDER_01",
                "anomaly_type": "demand_spike",
                "expected_value": round(expected_demand, 1),
                "actual_value": round(current_demand_kw, 1),
                "deviation_pct": round(demand_deviation_pct, 1),
                "severity": severity,
                "root_cause": f"Abnormal Demand Spike (+{demand_deviation_pct:.1f}%): {root_cause_text}",
                "diagnostic_details": {
                    "temperature_c": temperature_c,
                    "ev_charging_kw": ev_charging_kw,
                    "ev_count": ev_active_count,
                    "expected_range": [base_demand["min_expected_kw"], base_demand["max_expected_kw"]]
                },
                "status": "ACTIVE"
            }
            anomalies.append(event)
            
        # -------------------------------------------------------------
        # CHECK 2: Demand Drop
        # -------------------------------------------------------------
        elif demand_deviation_pct < -30.0 and (expected_demand - current_demand_kw) > 15.0:
            event = {
                "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": timestamp.isoformat(),
                "device_id": "COMMUNITY_FEEDER_01",
                "anomaly_type": "demand_drop",
                "expected_value": round(expected_demand, 1),
                "actual_value": round(current_demand_kw, 1),
                "deviation_pct": round(demand_deviation_pct, 1),
                "severity": "HIGH",
                "root_cause": "Sudden Demand Drop: Possible local sub-circuit trip, transformer fault, or scheduled facility shutdown.",
                "diagnostic_details": {"temperature_c": temperature_c},
                "status": "ACTIVE"
            }
            anomalies.append(event)

        # -------------------------------------------------------------
        # CHECK 3: Night Baseload Anomaly (1 AM - 5 AM)
        # -------------------------------------------------------------
        if 1.0 <= hour <= 5.0 and current_demand_kw > 45.0:
            event = {
                "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": timestamp.isoformat(),
                "device_id": "COMMUNITY_FEEDER_01",
                "anomaly_type": "night_anomaly",
                "expected_value": round(expected_demand, 1),
                "actual_value": round(current_demand_kw, 1),
                "deviation_pct": round(demand_deviation_pct, 1),
                "severity": "MEDIUM",
                "root_cause": f"Abnormal Off-Peak Baseload: Unattended overnight equipment or water pumping running during baseload hours ({round(current_demand_kw, 1)} kW vs expected {round(expected_demand, 1)} kW).",
                "diagnostic_details": {"hour": hour},
                "status": "ACTIVE"
            }
            anomalies.append(event)

        # -------------------------------------------------------------
        # CHECK 4: Solar Underperformance
        # -------------------------------------------------------------
        if expected_solar > 15.0 and (expected_solar - solar_generation_kw) > 18.0:
            solar_dev_pct = ((solar_generation_kw - expected_solar) / expected_solar) * 100.0
            if solar_dev_pct < -25.0:
                causes = []
                if cloud_cover_pct > 60.0:
                    causes.append(f"Transient thick cloud occlusion (cloud cover {cloud_cover_pct:.0f}%)")
                else:
                    causes.append("Potential solar array soiling, inverter partial clipping, or string fault")
                    
                event = {
                    "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
                    "timestamp": timestamp.isoformat(),
                    "device_id": "ROOFTOP_SOLAR_ARRAY",
                    "anomaly_type": "solar_underperformance",
                    "expected_value": round(expected_solar, 1),
                    "actual_value": round(solar_generation_kw, 1),
                    "deviation_pct": round(solar_dev_pct, 1),
                    "severity": "MEDIUM" if solar_dev_pct > -45.0 else "HIGH",
                    "root_cause": f"Solar Generation Deficit ({solar_dev_pct:.1f}%): " + " & ".join(causes),
                    "diagnostic_details": {
                        "cloud_cover_pct": cloud_cover_pct,
                        "solar_radiation": solar_radiation_w_m2
                    },
                    "status": "ACTIVE"
                }
                anomalies.append(event)

        # -------------------------------------------------------------
        # CHECK 5: EV Charging Clustering
        # -------------------------------------------------------------
        if ev_active_count >= 8 and ev_charging_kw > 35.0:
            event = {
                "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": timestamp.isoformat(),
                "device_id": "EV_CHARGER_CLUSTER",
                "anomaly_type": "ev_cluster",
                "expected_value": 15.0,
                "actual_value": round(ev_charging_kw, 1),
                "deviation_pct": round(((ev_charging_kw - 15.0) / 15.0) * 100.0, 1),
                "severity": "HIGH",
                "root_cause": f"Simultaneous EV Charging Synchrony: {ev_active_count} EVs pulling {ev_charging_kw:.1f} kW concurrent load during grid stress window.",
                "diagnostic_details": {"active_evs": ev_active_count},
                "status": "ACTIVE"
            }
            anomalies.append(event)

        # Keep history capped at 100 entries
        for a in anomalies:
            # Avoid duplicate rapid triggers for same anomaly type within 5 minutes
            recent_same = [h for h in self.incident_history if h["anomaly_type"] == a["anomaly_type"]]
            if not recent_same or (datetime.fromisoformat(a["timestamp"]) - datetime.fromisoformat(recent_same[-1]["timestamp"])).total_seconds() > 300:
                self.incident_history.append(a)
                if len(self.incident_history) > 100:
                    self.incident_history.pop(0)

        self.active_incidents = anomalies
        return anomalies

anomaly_engine = AnomalyEngine()
