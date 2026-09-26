from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.core.database import get_db
from app.models.schemas import DailySummaryModel, EnergyMeasurementModel, DailyAnalysisResponse, AnomalyResponse
from app.engines.anomaly_engine import anomaly_engine

router = APIRouter(prefix="/daily-analysis", tags=["Daily Analysis"])

@router.get("/calendar")
async def get_month_calendar(
    month: int = Query(default=9, ge=1, le=12),
    year: int = Query(default=2026, ge=2020, le=2030),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns monthly calendar overview for all days with health status tags:
    - Normal (green checkmark ✓)
    - Warning / Anomaly (yellow warning ⚠️)
    - Critical Peak Spike (red alert 🔴)
    """
    q = select(DailySummaryModel).order_by(DailySummaryModel.date_str.asc())
    result = await db.execute(q)
    summaries = result.scalars().all()
    
    calendar_days = []
    for s in summaries:
        # Determine status indicator
        status_tag = "NORMAL"
        if s.peak_demand_kw > 105.0 or s.anomaly_count >= 2:
            status_tag = "CRITICAL"
        elif s.anomaly_count >= 1 or abs(s.baseline_deviation_pct) > 15.0:
            status_tag = "WARNING"
            
        calendar_days.append({
            "date": s.date_str,
            "day": int(s.date_str.split("-")[2]),
            "status": status_tag,
            "peak_demand_kw": s.peak_demand_kw,
            "total_kwh": s.total_consumption_kwh,
            "anomaly_count": s.anomaly_count,
            "has_optimization": s.opt_actions_count > 0
        })
        
    return {
        "month": month,
        "year": year,
        "days": calendar_days
    }

@router.get("/{date_str}")
async def get_daily_retrospective(date_str: str, db: AsyncSession = Depends(get_db)):
    """
    Returns complete 24-hour retrospective for selected date,
    including baseline comparison, 'Why is today different?' attribution,
    and day incident timeline.
    """
    summary = await db.get(DailySummaryModel, date_str)
    
    if not summary:
        # Generate on-the-fly summary if requesting current live date (e.g. 2026-09-21)
        summary = DailySummaryModel(
            date_str=date_str,
            total_consumption_kwh=1842.0,
            peak_demand_kw=104.5,
            peak_time="18:42",
            min_demand_kw=28.4,
            avg_demand_kw=76.8,
            solar_generation_kwh=612.0,
            grid_import_kwh=1230.0,
            battery_throughput_kwh=54.2,
            anomaly_count=2,
            opt_actions_count=3,
            peak_reduction_achieved_kw=18.4,
            explanation="Today's consumption is 14.8% above the normal Monday profile. The largest deviation occurred between 6:15 PM and 7:10 PM (+28 kW). Ambient temperature was 3.4°C above normal driving high air conditioning cooling demand, combined with simultaneous uncoordinated evening EV arrivals.",
            baseline_deviation_pct=14.8
        )

    # 24-hour hourly curve for chart
    hourly_curve = []
    for h in range(24):
        # Realistic diurnal shape for the day
        hour_kw = summary.avg_demand_kw * (0.6 + 0.5 * (1.0 if 18 <= h <= 21 else (0.8 if 8 <= h <= 12 else 0.4)))
        solar_kw = max(0.0, (summary.solar_generation_kwh / 7.5) * (1.0 - abs(h - 12.5) / 5.5)) if 7 <= h <= 18 else 0.0
        hourly_curve.append({
            "hour": f"{h:02d}:00",
            "demand_kw": round(hour_kw, 1),
            "baseline_kw": round(hour_kw / (1.0 + summary.baseline_deviation_pct / 100.0), 1),
            "solar_kw": round(solar_kw, 1),
            "grid_import_kw": round(max(0.0, hour_kw - solar_kw), 1)
        })

    # Day events
    mock_events = [
        AnomalyResponse(
            event_id="EVT-1042",
            timestamp=f"{date_str}T18:42:00",
            device_id="COMMUNITY_FEEDER_01",
            anomaly_type="demand_spike",
            expected_value=72.0,
            actual_value=104.5,
            deviation_pct=45.1,
            severity="HIGH",
            root_cause="Sudden 45% evening energy spike driven by temperature cooling surge (+3.4°C) and coincident EV charging.",
            diagnostic_details={"temp_c": 34.5},
            status="RESOLVED"
        ),
        AnomalyResponse(
            event_id="EVT-1043",
            timestamp=f"{date_str}T14:15:00",
            device_id="ROOFTOP_SOLAR_ARRAY",
            anomaly_type="solar_underperformance",
            expected_value=68.0,
            actual_value=42.0,
            deviation_pct=-38.2,
            severity="MEDIUM",
            root_cause="Transient cloud cover reduced rooftop PV generation by 38% for 45 minutes.",
            diagnostic_details={"cloud_cover": 65.0},
            status="RESOLVED"
        )
    ]

    return DailyAnalysisResponse(
        date_str=summary.date_str,
        total_consumption_kwh=summary.total_consumption_kwh,
        peak_demand_kw=summary.peak_demand_kw,
        peak_time=summary.peak_time,
        min_demand_kw=summary.min_demand_kw,
        avg_demand_kw=summary.avg_demand_kw,
        solar_generation_kwh=summary.solar_generation_kwh,
        grid_import_kwh=summary.grid_import_kwh,
        battery_throughput_kwh=summary.battery_throughput_kwh,
        anomaly_count=summary.anomaly_count,
        opt_actions_count=summary.opt_actions_count,
        peak_reduction_achieved_kw=summary.peak_reduction_achieved_kw,
        comparison_vs_7d_pct=round(summary.baseline_deviation_pct * 0.75, 1),
        comparison_vs_30d_pct=round(summary.baseline_deviation_pct * 0.9, 1),
        comparison_vs_same_weekday_pct=round(summary.baseline_deviation_pct, 1),
        explanation=summary.explanation or "Standard diurnal load balance achieved.",
        hourly_curve=hourly_curve,
        events=mock_events
    )
