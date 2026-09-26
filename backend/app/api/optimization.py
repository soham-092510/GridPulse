from fastapi import APIRouter, Body, HTTPException, Request
from datetime import datetime
from typing import List, Dict, Any

from app.models.schemas import OptimizationActionDTO, OptimizationApprovalRequest
from app.engines.optimizer import flexibility_optimizer
from app.simulation.digital_twin import digital_twin
from app.ingestion.weather_service import weather_service
from app.core.limiter import limiter

router = APIRouter(prefix="/optimization", tags=["Optimization"])

@router.get("/actions")
@limiter.limit("30/minute")
async def get_optimization_actions(request: Request):

    """Returns currently pending recommended flexibility actions and past execution logs."""
    pending = list(flexibility_optimizer.pending_actions.values())
    history = flexibility_optimizer.action_history
    
    # If no pending actions exist, generate an initial schedule
    if not pending:
        now = datetime.utcnow()
        weather = await weather_service.get_current_weather()
        twin_state = digital_twin.step(now, weather)
        opt_res = flexibility_optimizer.solve_flexibility_schedule(
            current_time=now,
            current_demand_kw=twin_state["current_demand_kw"],
            current_solar_kw=twin_state["solar_generation_kw"],
            battery_soc_pct=twin_state["battery_soc_pct"]
        )
        pending = opt_res.get("recommended_actions", [])
        
    return {
        "pending_recommendations": pending,
        "action_history": list(reversed(history))[:20]
    }

@router.post("/approve")
async def approve_action(req: OptimizationApprovalRequest):
    """
    Human-in-the-loop operator approval or rejection of an AI-recommended flexibility dispatch.
    """
    updated_action = flexibility_optimizer.set_action_status(req.action_id, req.approved)
    if not updated_action:
        raise HTTPException(status_code=404, detail="Optimization action not found")
        
    return {
        "message": f"Action {req.action_id} {'APPROVED' if req.approved else 'REJECTED'}",
        "action": updated_action
    }

@router.post("/recompute")
async def recompute_schedule():
    """Forces an immediate MILP re-optimization run."""
    now = datetime.utcnow()
    weather = await weather_service.get_current_weather()
    twin_state = digital_twin.step(now, weather)
    
    res = flexibility_optimizer.solve_flexibility_schedule(
        current_time=now,
        current_demand_kw=twin_state["current_demand_kw"],
        current_solar_kw=twin_state["solar_generation_kw"],
        battery_soc_pct=twin_state["battery_soc_pct"]
    )
    return res
