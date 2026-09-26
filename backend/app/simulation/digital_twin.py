import math
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.core.config import settings

class DigitalTwinNeighbourhood:
    """
    High-fidelity physics and stochastic simulator for a 100-home neighbourhood.
    Subsystems simulated:
    - 100 residential households + 10 commercial shops
    - Rooftop solar arrays (80 kW community aggregated capacity)
    - 100 kWh Community Battery Storage System (BESS)
    - 20 EV Chargers with stochastic arrival and charging states
    - Flexible municipal water pump (12 kW)
    """
    
    def __init__(self):
        self.battery_capacity_kwh = settings.DEFAULT_BATTERY_CAPACITY_KWH
        self.battery_soc_pct = 72.0
        self.battery_power_kw = 0.0 # (+) discharge, (-) charge
        
        # EV fleet state
        self.ev_chargers = [
            {
                "ev_id": f"EV_{i+1:02d}",
                "connected": (i < 12),
                "charging": (i < 8),
                "power_kw": 7.2 if (i < 8) else 0.0,
                "soc_pct": random.uniform(30.0, 75.0),
                "user_consent": (i % 5 != 0) # 80% consent
            }
            for i in range(20)
        ]
        
        # Scenario injection state
        self.anomaly_injection_mode: str = "NORMAL" # "SPIKE", "SOLAR_DROP", "NORMAL"
        self.injection_timer: int = 0
        
    def set_injection_scenario(self, scenario: str, duration_ticks: int = 30):
        """Allows front-end or tester to inject a spike or solar drop for demonstration."""
        self.anomaly_injection_mode = scenario
        self.injection_timer = duration_ticks

    def step(self, current_time: datetime, weather: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advances digital twin by one simulation tick and produces holistic telemetry.
        """
        hour_float = current_time.hour + current_time.minute / 60.0 + current_time.second / 3600.0
        temp_c = weather.get("temperature_c", 31.0)
        cloud_pct = weather.get("cloud_cover_pct", 20.0)
        radiation = weather.get("solar_radiation_w_m2", 500.0)
        
        # 1. Base Household Demand
        # Diurnal double-peak: Morning (07:30 - 09:30) and Evening (18:30 - 22:00)
        morning_peak = 35.0 * math.exp(-0.5 * ((hour_float - 8.5) / 1.5) ** 2)
        evening_peak = 52.0 * math.exp(-0.5 * ((hour_float - 20.0) / 2.0) ** 2)
        baseload = 28.0 + random.uniform(-1.5, 1.5)
        
        # Temperature cooling sensitivity (~3.0 kW per °C above 31°C)
        cooling_load = max(0.0, (temp_c - 31.0) * 3.2) if 11.0 <= hour_float <= 23.0 else 0.0
        
        raw_household_demand = baseload + morning_peak + evening_peak + cooling_load
        
        # 2. EV Fleet Demand
        # EV arrival increases in evening hours
        total_ev_kw = 0.0
        active_ev_count = 0
        for ev in self.ev_chargers:
            if 17.0 <= hour_float <= 22.0:
                ev["connected"] = True
                ev["charging"] = True
                ev["power_kw"] = 3.3 if random.random() > 0.5 else 7.2
            elif 0.0 <= hour_float <= 5.0:
                ev["connected"] = True
                ev["charging"] = (random.random() > 0.7) # mostly finish charging
                ev["power_kw"] = 3.3 if ev["charging"] else 0.0
            else:
                ev["connected"] = (random.random() > 0.6)
                ev["charging"] = ev["connected"] and (random.random() > 0.5)
                ev["power_kw"] = 7.2 if ev["charging"] else 0.0
                
            if ev["charging"]:
                total_ev_kw += ev["power_kw"]
                active_ev_count += 1
                
        # 3. Rooftop Solar Generation
        if 6.0 <= hour_float <= 18.5 and radiation > 10.0:
            solar_eff = 0.17 # Efficiency
            raw_solar_kw = (settings.DEFAULT_SOLAR_CAPACITY_KW * (radiation / 1000.0)) * (1.0 - 0.7 * (cloud_pct / 100.0) ** 1.5)
            raw_solar_kw = max(0.0, min(settings.DEFAULT_SOLAR_CAPACITY_KW, raw_solar_kw + random.uniform(-1.0, 1.0)))
        else:
            raw_solar_kw = 0.0
            
        # 4. Scenario Injections
        if self.injection_timer > 0:
            self.injection_timer -= 1
            if self.anomaly_injection_mode == "SPIKE":
                raw_household_demand += 32.0 # Sudden 32 kW spike (heavy cooling + industrial load)
                total_ev_kw += 18.0
                active_ev_count += 4
            elif self.anomaly_injection_mode == "SOLAR_DROP":
                raw_solar_kw *= 0.35 # Solar sudden cloud shading or inverter trip
        else:
            self.anomaly_injection_mode = "NORMAL"

        total_demand_kw = round(raw_household_demand + total_ev_kw, 2)
        total_solar_kw = round(raw_solar_kw, 2)
        
        # 5. Community Battery Behavior
        # If solar > demand, charge battery. If peak evening, discharge.
        if total_solar_kw > total_demand_kw and self.battery_soc_pct < 95.0:
            excess = total_solar_kw - total_demand_kw
            charge_rate = min(settings.DEFAULT_BATTERY_MAX_POWER_KW, excess)
            self.battery_power_kw = -round(charge_rate, 2) # (-) indicates charging
            self.battery_soc_pct = min(95.0, self.battery_soc_pct + (charge_rate * (2.0 / 3600.0) / self.battery_capacity_kwh * 100.0))
        elif hour_float >= 18.5 and hour_float <= 21.5 and self.battery_soc_pct > 25.0:
            discharge_rate = min(settings.DEFAULT_BATTERY_MAX_POWER_KW, (total_demand_kw - 65.0))
            if discharge_rate > 5.0:
                self.battery_power_kw = round(discharge_rate, 2)
                self.battery_soc_pct = max(20.0, self.battery_soc_pct - (discharge_rate * (2.0 / 3600.0) / self.battery_capacity_kwh * 100.0))
            else:
                self.battery_power_kw = 0.0
        else:
            self.battery_power_kw = 0.0

        # Net Grid Import (kW)
        net_grid_kw = max(0.0, total_demand_kw - total_solar_kw - self.battery_power_kw)
        
        # Voltage and Current based on 3-phase 415V distribution
        voltage_v = round(415.0 + random.uniform(-4.0, 3.0), 1)
        power_factor = round(0.95 + random.uniform(-0.02, 0.02), 3)
        current_a = round((total_demand_kw * 1000.0) / (math.sqrt(3) * voltage_v * power_factor), 1)
        
        return {
            "timestamp": current_time.isoformat(),
            "current_demand_kw": total_demand_kw,
            "household_demand_kw": round(raw_household_demand, 2),
            "solar_generation_kw": total_solar_kw,
            "battery_soc_pct": round(self.battery_soc_pct, 1),
            "battery_power_kw": self.battery_power_kw,
            "ev_charging_kw": round(total_ev_kw, 2),
            "ev_active_count": active_ev_count,
            "net_grid_import_kw": round(net_grid_kw, 2),
            "voltage_v": voltage_v,
            "current_a": current_a,
            "power_factor": power_factor,
            "ambient_temperature_c": round(temp_c, 1),
            "cloud_cover_pct": round(cloud_pct, 1),
            "solar_radiation_w_m2": round(radiation, 1),
            "active_scenario": self.anomaly_injection_mode
        }

digital_twin = DigitalTwinNeighbourhood()
