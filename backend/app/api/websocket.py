import asyncio
import json
import logging
from datetime import datetime
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.simulation.digital_twin import digital_twin
from app.ingestion.weather_service import weather_service
from app.engines.baseline_engine import baseline_engine
from app.engines.anomaly_engine import anomaly_engine
from app.engines.risk_engine import risk_engine
from app.engines.forecast_engine import forecast_engine
from app.core.config import settings

logger = logging.getLogger("neighbourflex.ws")
router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    """Manages active WebSocket browser clients and broadcasts live telemetry."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast(self, data: dict):
        if not self.active_connections:
            return
            
        json_str = json.dumps(data)
        stale_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(json_str)
            except Exception:
                stale_connections.add(connection)
                
        for stale in stale_connections:
            self.active_connections.discard(stale)

manager = ConnectionManager()

@router.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep receiving client pings or commands
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("action") == "inject_scenario":
                    scenario = msg.get("scenario", "SPIKE")
                    digital_twin.set_injection_scenario(scenario, duration_ticks=30)
                    await websocket.send_text(json.dumps({"info": f"Injected {scenario}"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

async def telemetry_broadcaster_loop():
    """Background task continuously broadcasting live telemetry every 2 seconds."""
    logger.info("Starting real-time telemetry broadcaster loop...")
    while True:
        try:
            if manager.active_connections:
                now = datetime.utcnow()
                weather = await weather_service.get_current_weather()
                twin_state = digital_twin.step(now, weather)
                
                base_d = baseline_engine.get_expected_demand(now, weather["temperature_c"])
                expected_demand = base_d["expected_kw"]
                
                base_s = baseline_engine.get_expected_solar(now, weather["cloud_cover_pct"])
                expected_solar = base_s["expected_solar_kw"]
                
                anomalies = anomaly_engine.evaluate_live_state(
                    timestamp=now,
                    current_demand_kw=twin_state["current_demand_kw"],
                    solar_generation_kw=twin_state["solar_generation_kw"],
                    battery_power_kw=twin_state["battery_power_kw"],
                    ev_charging_kw=twin_state["ev_charging_kw"],
                    ev_active_count=twin_state["ev_active_count"],
                    temperature_c=weather["temperature_c"],
                    cloud_cover_pct=weather["cloud_cover_pct"],
                    solar_radiation_w_m2=weather["solar_radiation_w_m2"]
                )
                
                demand_dev = ((twin_state["current_demand_kw"] - expected_demand) / max(10.0, expected_demand)) * 100.0
                
                risk_info = risk_engine.assess_risk(
                    current_demand_kw=twin_state["current_demand_kw"],
                    solar_generation_kw=twin_state["solar_generation_kw"],
                    battery_soc_pct=twin_state["battery_soc_pct"],
                    battery_capacity_kwh=settings.DEFAULT_BATTERY_CAPACITY_KWH,
                    forecast_points_1h=[]
                )
                
                payload = {
                    "type": "LIVE_TELEMETRY",
                    "timestamp": now.isoformat(),
                    "current_demand_kw": twin_state["current_demand_kw"],
                    "household_demand_kw": twin_state["household_demand_kw"],
                    "expected_demand_kw": round(expected_demand, 1),
                    "demand_deviation_pct": round(demand_dev, 1),
                    "solar_generation_kw": twin_state["solar_generation_kw"],
                    "expected_solar_kw": round(expected_solar, 1),
                    "battery_soc_pct": twin_state["battery_soc_pct"],
                    "battery_power_kw": twin_state["battery_power_kw"],
                    "ev_charging_kw": twin_state["ev_charging_kw"],
                    "ev_active_count": twin_state["ev_active_count"],
                    "net_grid_import_kw": twin_state["net_grid_import_kw"],
                    "voltage_v": twin_state["voltage_v"],
                    "current_a": twin_state["current_a"],
                    "power_factor": twin_state["power_factor"],
                    "ambient_temperature_c": weather["temperature_c"],
                    "cloud_cover_pct": weather["cloud_cover_pct"],
                    "solar_radiation_w_m2": weather["solar_radiation_w_m2"],
                    "reliability_risk_level": risk_info["risk_level"],
                    "reliability_risk_reason": risk_info["status_reason"],
                    "feeder_loading_pct": risk_info["current_loading_pct"],
                    "active_scenario": twin_state["active_scenario"],
                    "active_anomalies": anomalies
                }
                
                await manager.broadcast(payload)
        except Exception as e:
            logger.error(f"Error in telemetry loop: {e}")
            
        await asyncio.sleep(settings.SIMULATION_TICK_SECONDS)
