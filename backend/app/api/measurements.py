from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.core.database import get_db
from app.models.schemas import LiveStateResponse, EnergyMeasurementModel
from app.ingestion.weather_service import weather_service
from app.simulation.digital_twin import digital_twin
from app.engines.baseline_engine import baseline_engine
from app.engines.anomaly_engine import anomaly_engine
from app.engines.risk_engine import risk_engine
from app.engines.forecast_engine import forecast_engine
from app.core.config import settings

router = APIRouter(prefix="/measurements", tags=["Measurements"])

# Global state tracker for live mode
current_system_mode = "DIGITAL_TWIN" # "LIVE", "DIGITAL_TWIN", "REPLAY"

@router.get("/live", response_model=LiveStateResponse)
async def get_live_state(db: AsyncSession = Depends(get_db)):
    """
    Returns the real-time aggregated energy state of the neighbourhood,
    including demand, solar, battery, EV, grid loading, weather, and reliability risk.
    """
    now = datetime.utcnow()
    weather = await weather_service.get_current_weather()
    
    # Step digital twin or read latest live measurements
    twin_data = digital_twin.step(now, weather)
    
    # Check baseline expectation
    baseline_data = baseline_engine.get_expected_demand(now, weather["temperature_c"])
    expected_demand = baseline_data["expected_kw"]
    
    solar_base = baseline_engine.get_expected_solar(now, weather["cloud_cover_pct"])
    expected_solar = solar_base["expected_solar_kw"]
    
    # Anomaly detection & root cause check
    anomalies = anomaly_engine.evaluate_live_state(
        timestamp=now,
        current_demand_kw=twin_data["current_demand_kw"],
        solar_generation_kw=twin_data["solar_generation_kw"],
        battery_power_kw=twin_data["battery_power_kw"],
        ev_charging_kw=twin_data["ev_charging_kw"],
        ev_active_count=twin_data["ev_active_count"],
        temperature_c=weather["temperature_c"],
        cloud_cover_pct=weather["cloud_cover_pct"],
        solar_radiation_w_m2=weather["solar_radiation_w_m2"]
    )
    
    # Lookahead for 1-hour risk
    forecast_data = await forecast_engine.generate_forecasts(
        now, twin_data["current_demand_kw"], twin_data["solar_generation_kw"], weather["temperature_c"]
    )
    
    risk_info = risk_engine.assess_risk(
        current_demand_kw=twin_data["current_demand_kw"],
        solar_generation_kw=twin_data["solar_generation_kw"],
        battery_soc_pct=twin_data["battery_soc_pct"],
        battery_capacity_kwh=settings.DEFAULT_BATTERY_CAPACITY_KWH,
        forecast_points_1h=forecast_data["horizon_1h"]
    )
    
    demand_dev = ((twin_data["current_demand_kw"] - expected_demand) / max(10.0, expected_demand)) * 100.0
    
    return LiveStateResponse(
        timestamp=now.isoformat(),
        current_demand_kw=twin_data["current_demand_kw"],
        household_demand_kw=twin_data.get("household_demand_kw", 65.0),
        expected_demand_kw=round(expected_demand, 1),
        demand_deviation_pct=round(demand_dev, 1),
        solar_generation_kw=twin_data["solar_generation_kw"],
        expected_solar_kw=round(expected_solar, 1),
        battery_soc_pct=twin_data["battery_soc_pct"],
        battery_power_kw=twin_data["battery_power_kw"],
        ev_charging_kw=twin_data["ev_charging_kw"],
        ev_active_count=twin_data["ev_active_count"],
        net_grid_import_kw=twin_data["net_grid_import_kw"],
        voltage_v=twin_data.get("voltage_v", 415.0),
        current_a=twin_data.get("current_a", 120.0),
        power_factor=twin_data.get("power_factor", 0.95),
        feeder_capacity_kw=risk_info["feeder_capacity_kw"],
        feeder_loading_pct=risk_info["current_loading_pct"],
        ambient_temperature_c=weather["temperature_c"],
        cloud_cover_pct=weather["cloud_cover_pct"],
        solar_radiation_w_m2=weather["solar_radiation_w_m2"],
        reliability_risk_level=risk_info["risk_level"],
        reliability_risk_reason=risk_info["status_reason"],
        data_quality_score=99.8,
        active_anomalies_count=len(anomalies),
        active_scenario=twin_data.get("active_scenario", "NORMAL"),
        active_anomalies=anomalies,
        system_mode=current_system_mode
    )


@router.get("/history")
async def get_recent_history(
    hours: int = Query(default=6, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """Returns recent historical energy time-series for dashboard charting."""
    # Query database for recent active_power measurements
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    q = (
        select(EnergyMeasurementModel)
        .where(EnergyMeasurementModel.metric == "active_power")
        .where(EnergyMeasurementModel.timestamp >= cutoff)
        .order_by(EnergyMeasurementModel.timestamp.asc())
    )
    result = await db.execute(q)
    rows = result.scalars().all()
    
    # Format for chart
    return [
        {
            "timestamp": r.timestamp.isoformat(),
            "active_power_kw": r.value,
            "quality": r.quality
        }
        for r in rows
    ]
