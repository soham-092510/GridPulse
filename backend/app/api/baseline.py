from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.engines.baseline_engine import baseline_engine
from app.ingestion.weather_service import weather_service

router = APIRouter(prefix="/baseline", tags=["Baseline"])

@router.get("/profile")
async def get_today_baseline_profile():
    """
    Returns 96 intervals of expected baseline curve for today
    with confidence envelope [P10, P90].
    """
    now = datetime.utcnow()
    weather = await weather_service.get_current_weather()
    current_temp = weather.get("temperature_c", 31.0)
    
    start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
    profile = []
    
    for slot in range(96):
        t = start_of_day + timedelta(minutes=slot * 15)
        # Approximate temperature variation for slot
        slot_hour = t.hour + t.minute / 60.0
        est_temp = current_temp + (2.5 if 12 <= slot_hour <= 17 else -2.0)
        
        base_d = baseline_engine.get_expected_demand(t, est_temp)
        base_s = baseline_engine.get_expected_solar(t, weather.get("cloud_cover_pct", 20.0))
        
        profile.append({
            "time": t.strftime("%H:%M"),
            "expected_demand_kw": base_d["expected_kw"],
            "min_expected_kw": base_d["min_expected_kw"],
            "max_expected_kw": base_d["max_expected_kw"],
            "expected_solar_kw": base_s["expected_solar_kw"],
            "temp_bin": base_d["temp_bin"]
        })
        
    return {
        "date": now.strftime("%Y-%m-%d"),
        "weekday": now.strftime("%A"),
        "ambient_temp_c": current_temp,
        "profile": profile
    }
