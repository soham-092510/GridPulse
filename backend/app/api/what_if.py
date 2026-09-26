from fastapi import APIRouter, Request
from app.models.schemas import WhatIfRequest, WhatIfResponse
from app.core.limiter import limiter

router = APIRouter(prefix="/what-if", tags=["What-If Simulation"])

@router.post("/simulate", response_model=WhatIfResponse)
@limiter.limit("20/minute")
async def simulate_scenario(request: Request, req: WhatIfRequest):

    """
    Simulates asset expansion and demand-response scenarios:
    - Expanded community battery capacity (e.g., 100 kWh -> 250 kWh)
    - EV Demand Response participation rate (0% to 100%)
    - Solar capacity scaling (e.g., +20% or +50%)
    """
    baseline_peak_kw = 104.5
    baseline_grid_kwh = 1230.0
    
    # Mathematical sensitivity multipliers
    # Battery shaving power potential ~ 0.3 * capacity_kwh
    batt_headroom = max(0.0, req.battery_capacity_kwh - 100.0)
    extra_battery_shaving_kw = min(25.0, batt_headroom * 0.18)
    
    # EV DR shifting potential
    ev_shifting_kw = (req.ev_dr_participation_pct / 100.0) * 18.0
    
    # Solar scaling effect
    solar_peak_gain_kw = (req.solar_capacity_multiplier - 1.0) * 80.0
    
    # Temperature offset effect
    temp_load_penalty_kw = req.simulated_temperature_offset_c * 3.2
    
    total_peak_reduction_kw = max(2.0, (14.0 + extra_battery_shaving_kw + ev_shifting_kw) - temp_load_penalty_kw * 0.4)
    optimized_peak_kw = round(baseline_peak_kw - total_peak_reduction_kw, 1)
    peak_reduction_pct = round((total_peak_reduction_kw / baseline_peak_kw) * 100.0, 1)
    
    # Grid energy reduction (solar self-consumption + peak loss avoidance)
    grid_kwh_saved = (extra_battery_shaving_kw * 3.5) + (solar_peak_gain_kw * 4.2) + (ev_shifting_kw * 2.0)
    optimized_grid_kwh = round(max(300.0, baseline_grid_kwh - grid_kwh_saved), 1)
    grid_reduction_pct = round(((baseline_grid_kwh - optimized_grid_kwh) / baseline_grid_kwh) * 100.0, 1)
    
    # Carbon & Cost savings (Average DISCOM tariff ₹8.5/kWh, 0.82 kg CO2 / kWh)
    co2_saved_kg = round(grid_kwh_saved * 0.82, 1)
    cost_savings_inr = round(grid_kwh_saved * 8.50, 2)
    feeder_stress_hours = round(max(0.5, 4.0 - (total_peak_reduction_kw / 6.0)), 1)
    
    hourly_comparison = []
    for h in range(24):
        base_h = 75.0 + 25.0 * (1.0 if 18 <= h <= 21 else 0.4)
        opt_h = base_h
        if 18 <= h <= 21:
            opt_h -= total_peak_reduction_kw
        hourly_comparison.append({
            "hour": f"{h:02d}:00",
            "baseline_kw": round(base_h, 1),
            "simulated_kw": round(opt_h, 1)
        })

    return WhatIfResponse(
        baseline_peak_kw=baseline_peak_kw,
        optimized_peak_kw=optimized_peak_kw,
        peak_reduction_kw=round(total_peak_reduction_kw, 1),
        peak_reduction_pct=peak_reduction_pct,
        baseline_grid_import_kwh=baseline_grid_kwh,
        optimized_grid_import_kwh=optimized_grid_kwh,
        grid_reduction_pct=grid_reduction_pct,
        co2_saved_kg=co2_saved_kg,
        estimated_cost_savings_inr=cost_savings_inr,
        feeder_stress_hours_saved=feeder_stress_hours,
        hourly_comparison=hourly_comparison
    )
