from fastapi import APIRouter, Body
from typing import List, Dict, Any

from app.models.schemas import AnomalyResponse
from app.engines.anomaly_engine import anomaly_engine
from app.simulation.digital_twin import digital_twin

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])

@router.get("/active", response_model=List[AnomalyResponse])
async def get_active_anomalies():
    """Returns all currently active detected anomalies and their root-cause explanations."""
    return [AnomalyResponse(**a) for a in anomaly_engine.active_incidents]

@router.get("/history", response_model=List[AnomalyResponse])
async def get_incident_history():
    """Returns chronological log of recent energy anomaly incidents."""
    return [AnomalyResponse(**a) for a in reversed(anomaly_engine.incident_history)]

@router.post("/inject")
async def inject_anomaly(
    scenario: str = Body(..., embed=True), # 'SPIKE', 'SOLAR_DROP', 'NORMAL'
    duration_ticks: int = Body(default=30, embed=True)
):
    """
    Hackathon Demo Control: Injects a real-time energy spike or sudden solar shortfall
    into the digital twin to showcase instantaneous anomaly detection and AI response.
    """
    valid_scenarios = ["SPIKE", "SOLAR_DROP", "NORMAL"]
    if scenario not in valid_scenarios:
        return {"error": f"Invalid scenario. Choose from: {valid_scenarios}"}
        
    digital_twin.set_injection_scenario(scenario, duration_ticks)
    return {
        "message": f"Injected '{scenario}' scenario for next {duration_ticks} ticks ({duration_ticks * 2} seconds).",
        "active_mode": scenario
    }
