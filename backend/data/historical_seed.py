import math
import random
from datetime import datetime, timedelta
import pandas as pd
from app.core.database import SessionLocalSync, init_db, sync_engine
from app.models.schemas import (
    DeviceModel, EnergyMeasurementModel, SolarMeasurementModel,
    BatteryMeasurementModel, WeatherMeasurementModel, DailySummaryModel,
    AnomalyEventModel
)
from app.engines.baseline_engine import baseline_engine

def generate_and_seed_historical_data():
    """
    Generates 20 full days of historical neighbourhood data (Sept 1 to Sept 20, 2026)
    and seeds default devices, measurements, daily retrospectives, and trains baseline engine.
    """
    db = SessionLocalSync()
    try:
        # Check if devices already exist
        existing_devices = db.query(DeviceModel).count()
        if existing_devices > 0:
            print("[INFO] Historical data already seeded. Loading baseline from database...")
            # Load historical energy data for baseline engine
            df_hist = pd.read_sql(
                "SELECT timestamp, value as active_power FROM energy_measurements WHERE metric='active_power'",
                sync_engine
            )
            if not df_hist.empty:
                # Add default temp column if missing
                df_hist['temperature_c'] = 31.0
                baseline_engine.fit_from_dataframe(df_hist)
                print(f"[INFO] Baseline engine trained on {len(df_hist)} historical readings.")
            return

        print("[INFO] Seeding NeighbourFlex initial devices and 21-day historical dataset...")
        
        # 1. Register Standard Hardware & Virtual Devices
        devices = [
            DeviceModel(
                device_id="SMART_METER_MAIN",
                name="Neighbourhood Main Substation Feeder Meter",
                device_type="smart_meter",
                manufacturer="Schneider Electric",
                model="PowerLogic PM8000",
                location="Distribution Transformer DT-04, Sector 7",
                protocol="mqtt",
                status="online",
                health_score=1.0,
                packets_received=45120,
                packets_rejected=4,
                last_seen=datetime.utcnow()
            ),
            DeviceModel(
                device_id="ROOFTOP_SOLAR_ARRAY",
                name="Community Rooftop Solar PV Aggregator",
                device_type="solar_inverter",
                manufacturer="Schneider Electric",
                model="Conext CL 60",
                location="Rooftop Cluster (40 homes)",
                protocol="modbus",
                status="online",
                health_score=0.98,
                packets_received=44980,
                packets_rejected=12,
                last_seen=datetime.utcnow()
            ),
            DeviceModel(
                device_id="COMMUNITY_BATTERY_01",
                name="Community Energy Storage System (BESS)",
                device_type="battery_bms",
                manufacturer="Schneider Electric",
                model="EcoStruxure Energy Storage 100kWh",
                location="Substation Enclosure A",
                protocol="can_gateway",
                status="online",
                health_score=1.0,
                packets_received=45050,
                packets_rejected=2,
                last_seen=datetime.utcnow()
            ),
            DeviceModel(
                device_id="EV_CHARGER_CLUSTER",
                name="Smart EV Charging Fleet Gateway (20 Bays)",
                device_type="ev_charger",
                manufacturer="Schneider Electric",
                model="EVlink Pro AC 22kW",
                location="Community Parking Lot & Garages",
                protocol="ocpp",
                status="online",
                health_score=0.99,
                packets_received=44800,
                packets_rejected=6,
                last_seen=datetime.utcnow()
            ),
            DeviceModel(
                device_id="WEATHER_STATION_01",
                name="Microclimate & Solar Irradiance Station",
                device_type="weather_station",
                manufacturer="Open-Meteo Integration",
                model="SLDC Micro-Station API",
                location="Neighbourhood Sensor Mast",
                protocol="rest",
                status="online",
                health_score=1.0,
                packets_received=2880,
                packets_rejected=0,
                last_seen=datetime.utcnow()
            )
        ]
        for d in devices:
            db.add(d)
        db.commit()

        # 2. Generate 20 Days of Data: Sept 1 to Sept 20, 2026
        start_date = datetime(2026, 9, 1, 0, 0, 0)
        history_rows = []
        daily_summaries = []
        
        for day_offset in range(20):
            current_day = start_date + timedelta(days=day_offset)
            date_str = current_day.strftime("%Y-%m-%d")
            is_weekend = (current_day.weekday() >= 5)
            
            # Weather variation for this day
            base_temp = 30.5 + random.uniform(-2.0, 3.5) # Heatwave on some days
            if day_offset == 11: # Heatwave spike on Sept 12
                base_temp = 36.2
                
            cloud_cover_base = 15.0 if day_offset != 4 else 75.0 # Cloudy on Sept 5
            
            day_total_kwh = 0.0
            day_solar_kwh = 0.0
            day_grid_kwh = 0.0
            day_peak_kw = 0.0
            day_peak_time = "19:30"
            day_min_kw = 999.0
            powers = []
            
            # 96 15-minute intervals
            for slot in range(96):
                slot_time = current_day + timedelta(minutes=slot * 15)
                hour_float = slot_time.hour + slot_time.minute / 60.0
                
                # Temperature
                temp_c = base_temp + 4.0 * math.sin((hour_float - 9.0) / 12.0 * math.pi)
                
                # Solar
                if 6.0 <= hour_float <= 18.5:
                    rad = 850.0 * math.sin((hour_float - 6.0) / 12.5 * math.pi) * (1.0 - 0.7 * (cloud_cover_base / 100.0) ** 1.5)
                    solar_kw = max(0.0, 80.0 * (rad / 1000.0))
                else:
                    rad = 0.0
                    solar_kw = 0.0
                    
                # Demand base
                if is_weekend:
                    base_load = 32.0 + 22.0 * math.sin((hour_float - 10.0) / 10.0 * math.pi)
                else:
                    morn = 28.0 * math.exp(-0.5 * ((hour_float - 8.5) / 1.5) ** 2)
                    eve = 48.0 * math.exp(-0.5 * ((hour_float - 20.0) / 2.0) ** 2)
                    base_load = 26.0 + morn + eve
                    
                # AC load
                ac_load = max(0.0, (temp_c - 31.0) * 3.2) if 12.0 <= hour_float <= 23.0 else 0.0
                
                # EV charging
                ev_load = (18.0 if 18.0 <= hour_float <= 22.0 else 4.0) + random.uniform(-2.0, 2.0)
                
                # Total demand
                demand_kw = round(base_load + ac_load + ev_load + random.uniform(-2.0, 2.0), 2)
                demand_kw = max(18.0, demand_kw)
                
                # Historical anomaly injection on specific days
                if day_offset == 11 and 18.0 <= hour_float <= 20.5: # Severe heatwave peak on Sept 12
                    demand_kw += 28.0
                if day_offset == 17 and 19.0 <= hour_float <= 21.0: # EV cluster spike on Sept 18
                    demand_kw += 24.0
                    
                powers.append(demand_kw)
                day_total_kwh += (demand_kw * 0.25)
                day_solar_kwh += (solar_kw * 0.25)
                net_import = max(0.0, demand_kw - solar_kw)
                day_grid_kwh += (net_import * 0.25)
                
                if demand_kw > day_peak_kw:
                    day_peak_kw = demand_kw
                    day_peak_time = slot_time.strftime("%H:%M")
                if demand_kw < day_min_kw:
                    day_min_kw = demand_kw
                    
                history_rows.append({
                    "timestamp": slot_time,
                    "active_power": demand_kw,
                    "temperature_c": round(temp_c, 1),
                    "solar_kw": round(solar_kw, 2)
                })
                
                # Add individual energy reading
                db.add(EnergyMeasurementModel(
                    timestamp=slot_time,
                    device_id="SMART_METER_MAIN",
                    metric="active_power",
                    value=demand_kw,
                    unit="kW",
                    quality="VALID",
                    confidence=1.0
                ))
                
                # Add solar reading
                db.add(SolarMeasurementModel(
                    timestamp=slot_time,
                    device_id="ROOFTOP_SOLAR_ARRAY",
                    power_kw=round(solar_kw, 2),
                    energy_kwh=round(day_solar_kwh, 2),
                    irradiance_w_m2=round(rad, 1),
                    cloud_cover_pct=round(cloud_cover_base, 1),
                    quality="VALID"
                ))

            # Store daily summary
            avg_kw = sum(powers) / len(powers)
            explanation = (
                f"Normal operational consumption profile. Solar supplied {round((day_solar_kwh/max(1, day_total_kwh))*100, 1)}% of total energy."
            )
            if day_offset == 11:
                explanation = "Heatwave peak event (+24% above normal): Extreme temperatures (36.2°C) combined with simultaneous domestic evening AC cooling surge."
            elif day_offset == 17:
                explanation = "EV charging synchrony event (+18% above normal): Uncoordinated cluster of 14 EVs charging during evening peak."
            elif day_offset == 4:
                explanation = "Solar shortfall day: Heavy monsoon cloud occlusion reduced rooftop solar generation by 62%."

            summary = DailySummaryModel(
                date_str=date_str,
                total_consumption_kwh=round(day_total_kwh, 1),
                peak_demand_kw=round(day_peak_kw, 1),
                peak_time=day_peak_time,
                min_demand_kw=round(day_min_kw, 1),
                avg_demand_kw=round(avg_kw, 1),
                solar_generation_kwh=round(day_solar_kwh, 1),
                grid_import_kwh=round(day_grid_kwh, 1),
                battery_throughput_kwh=round(48.5 + random.uniform(-5.0, 5.0), 1),
                anomaly_count=2 if day_offset in [4, 11, 17] else 0,
                opt_actions_count=3 if day_offset in [11, 17] else 1,
                peak_reduction_achieved_kw=16.8 if day_offset in [11, 17] else 8.4,
                explanation=explanation,
                baseline_deviation_pct=round(((avg_kw - 58.0) / 58.0) * 100.0, 1)
            )
            db.add(summary)

        db.commit()
        print(f"[INFO] Successfully seeded {len(history_rows)} historical readings across 20 days!")
        
        # Train baseline engine on the created history
        df_hist = pd.DataFrame(history_rows)
        baseline_engine.fit_from_dataframe(df_hist)
        print(f"[INFO] Baseline engine successfully fitted on {len(df_hist)} points.")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding historical data: {e}")
    finally:
        db.close()
