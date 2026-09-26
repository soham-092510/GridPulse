from fastapi import APIRouter, Request
from datetime import datetime
from app.models.schemas import MultiHorizonForecastResponse
from app.engines.forecast_engine import forecast_engine
from app.simulation.digital_twin import digital_twin
from app.ingestion.weather_service import weather_service
from app.core.limiter import limiter

router = APIRouter(prefix="/forecasts", tags=["Forecasts"])

@router.get("/multi-horizon", response_model=MultiHorizonForecastResponse)
@limiter.limit("30/minute")
async def get_multi_horizon_forecasts(request: Request):

    """
    Returns multi-horizon demand, solar, and net load predictions
    across 15-minute, 1-hour, 6-hour, and 24-hour lookahead windows
    with empirical accuracy benchmarks (MAE, RMSE, MAPE).
    """
    now = datetime.utcnow()
    weather = await weather_service.get_current_weather()
    twin_state = digital_twin.step(now, weather)
    
    forecasts = await forecast_engine.generate_forecasts(
        current_time=now,
        current_demand_kw=twin_state["current_demand_kw"],
        current_solar_kw=twin_state["solar_generation_kw"],
        current_temp_c=weather["temperature_c"]
    )
    
    return MultiHorizonForecastResponse(**forecasts)
