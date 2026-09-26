from fastapi import APIRouter, Body
from typing import List
from app.models.schemas import FeederStatus

router = APIRouter(prefix="/discom", tags=["DISCOM Operator"])

@router.get("/feeders", response_model=List[FeederStatus])
async def get_feeder_network_status():
    """
    Returns substation feeder map with active loading, solar, battery,
    and thermal risk indicators for regional utility operators.
    """
    feeders = [
        FeederStatus(
            feeder_id="FDR-01",
            name="Feeder 1 - Sector 4 Residential",
            current_load_kw=68.4,
            capacity_kw=120.0,
            loading_pct=57.0,
            solar_connected_kw=45.0,
            battery_storage_kwh=100.0,
            flexible_capacity_kw=24.0,
            risk_level="GREEN",
            status_reason="Optimal headroom. Solar generation offsetting 35% of local load."
        ),
        FeederStatus(
            feeder_id="FDR-02",
            name="Feeder 2 - Commercial High Street",
            current_load_kw=82.1,
            capacity_kw=130.0,
            loading_pct=63.2,
            solar_connected_kw=30.0,
            battery_storage_kwh=50.0,
            flexible_capacity_kw=18.0,
            risk_level="GREEN",
            status_reason="Stable afternoon commercial load within safe thermal envelope."
        ),
        FeederStatus(
            feeder_id="FDR-03",
            name="Feeder 3 - Mixed Residential & Schools",
            current_load_kw=108.5,
            capacity_kw=125.0,
            loading_pct=86.8,
            solar_connected_kw=25.0,
            battery_storage_kwh=80.0,
            flexible_capacity_kw=15.0,
            risk_level="YELLOW",
            status_reason="Moderate thermal stress. Evening cooking and lighting ramp detected."
        ),
        FeederStatus(
            feeder_id="FDR-04",
            name="Feeder 4 - Sector 7 Dense Community (Active Pilot)",
            current_load_kw=114.2,
            capacity_kw=125.0,
            loading_pct=91.4,
            solar_connected_kw=80.0,
            battery_storage_kwh=100.0,
            flexible_capacity_kw=32.0,
            risk_level="RED",
            status_reason="Impending transformer thermal overload: Demand +28%, Solar -18%, simultaneous EV charging cluster."
        ),
        FeederStatus(
            feeder_id="FDR-05",
            name="Feeder 5 - Municipal Water & Services",
            current_load_kw=42.0,
            capacity_kw=100.0,
            loading_pct=42.0,
            solar_connected_kw=15.0,
            battery_storage_kwh=20.0,
            flexible_capacity_kw=12.0,
            risk_level="GREEN",
            status_reason="Pumps operating on scheduled off-peak window."
        )
    ]
    return feeders

@router.post("/trigger-dr")
async def trigger_feeder_demand_response(
    feeder_id: str = Body(..., embed=True),
    target_reduction_kw: float = Body(default=15.0, embed=True)
):
    """
    Substation operator triggers automated Demand Response event on a stressed feeder.
    """
    return {
        "status": "DISPATCHED",
        "feeder_id": feeder_id,
        "target_reduction_kw": target_reduction_kw,
        "actions_initiated": [
            "Battery discharge set to 15.0 kW",
            "EV chargers in pilot zone paused/curtailed (estimated ~8.5 kW)",
            "Water pumping deferred until 22:30"
        ],
        "projected_new_loading_pct": 74.5,
        "message": f"Demand response dispatched to {feeder_id}. Expected relief: {target_reduction_kw} kW."
    }
