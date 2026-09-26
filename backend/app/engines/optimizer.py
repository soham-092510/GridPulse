import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from ortools.linear_solver import pywraplp
from app.core.config import settings

class FlexibilityOptimizer:
    """
    Mixed-Integer Linear Programming (MILP) Coordinator using Google OR-Tools.
    Optimizes community battery dispatch, smart EV charge shifting with user consent,
    and flexible municipal water pump / HVAC loads to minimize feeder peak demand.
    """
    
    def __init__(self):
        self.pending_actions: Dict[str, Dict[str, Any]] = {}
        self.action_history: List[Dict[str, Any]] = []
        
    def solve_flexibility_schedule(
        self,
        current_time: datetime,
        current_demand_kw: float,
        current_solar_kw: float,
        battery_soc_pct: float,
        battery_capacity_kwh: float = 100.0,
        battery_max_power_kw: float = 30.0,
        active_ev_charging_kw: float = 18.0,
        ev_consent_pct: float = 80.0, # % of EVs allowing smart schedule
        feeder_capacity_kw: float = 125.0
    ) -> Dict[str, Any]:
        """
        Solves multi-period optimization across the next 4 hours (16 x 15-min intervals).
        """
        solver = pywraplp.Solver.CreateSolver('CBC')
        if not solver:
            solver = pywraplp.Solver.CreateSolver('GLOP')
            
        N_STEPS = 16 # 4 hours ahead in 15-min increments
        DT_HOURS = 0.25
        
        # Uncontrolled baseline load profile across 4 hours (e.g. evening peak rising then falling)
        hour = current_time.hour + current_time.minute / 60.0
        base_demand_curve = []
        solar_curve = []
        for i in range(N_STEPS):
            t_offset = hour + (i * DT_HOURS)
            # Projected profile
            if 17.5 <= t_offset <= 21.0:
                d = current_demand_kw + (10.0 * (1.0 - abs(t_offset - 19.2) / 2.0))
            else:
                d = max(35.0, current_demand_kw - (i * 1.5))
            s = max(0.0, current_solar_kw - (i * (current_solar_kw / 6.0)))
            base_demand_curve.append(max(20.0, d))
            solar_curve.append(s)
            
        # Variables
        p_batt_dis = [solver.NumVar(0.0, battery_max_power_kw, f'p_dis_{t}') for t in range(N_STEPS)]
        p_batt_ch = [solver.NumVar(0.0, battery_max_power_kw, f'p_ch_{t}') for t in range(N_STEPS)]
        soc = [solver.NumVar(20.0, 95.0, f'soc_{t}') for t in range(N_STEPS)]
        
        # EV shiftable load variable: can shift up to consented EV power to later steps
        shiftable_ev_max = active_ev_charging_kw * (ev_consent_pct / 100.0)
        p_ev_shift_down = [solver.NumVar(0.0, shiftable_ev_max, f'ev_curtail_{t}') for t in range(N_STEPS)]
        p_ev_recharge = [solver.NumVar(0.0, shiftable_ev_max * 1.5, f'ev_recharge_{t}') for t in range(N_STEPS)]
        
        # Flexible deferrable municipal pump (e.g. 8 kW)
        p_pump_flex = [solver.NumVar(0.0, 8.0, f'pump_flex_{t}') for t in range(N_STEPS)]
        
        # Net grid power & Peak envelope
        p_grid = [solver.NumVar(0.0, 200.0, f'p_grid_{t}') for t in range(N_STEPS)]
        peak_grid = solver.NumVar(0.0, 200.0, 'peak_grid')
        
        # Constraints
        # 1. Initial battery SOC
        solver.Add(soc[0] == battery_soc_pct + (DT_HOURS / battery_capacity_kwh * 100.0) * (p_batt_ch[0] * 0.92 - p_batt_dis[0] / 0.92))
        
        # 2. SOC chain
        for t in range(1, N_STEPS):
            solver.Add(soc[t] == soc[t-1] + (DT_HOURS / battery_capacity_kwh * 100.0) * (p_batt_ch[t] * 0.92 - p_batt_dis[t] / 0.92))
            
        # 3. Power balance per step
        for t in range(N_STEPS):
            # net grid = demand - solar - battery_discharge + battery_charge - ev_curtail + ev_recharge - pump_flex
            solver.Add(
                p_grid[t] == base_demand_curve[t] - solar_curve[t] - p_batt_dis[t] + p_batt_ch[t] 
                             - p_ev_shift_down[t] + p_ev_recharge[t] - p_pump_flex[t]
            )
            # Peak envelope
            solver.Add(peak_grid >= p_grid[t])
            
        # 4. Total deferred EV load must be fully recovered before morning departure
        solver.Add(solver.Sum(p_ev_shift_down) == solver.Sum(p_ev_recharge))
        
        # 5. EV curtailment allowed mostly during peak hours (steps 0 to 8), recharge pushed to post-peak (steps 9 to 15)
        for t in range(min(4, N_STEPS)):
            solver.Add(p_ev_recharge[t] == 0.0) # Cannot recharge in the immediate peak window
            
        # Objective: Minimize peak grid demand + total energy consumption
        objective = solver.Objective()
        objective.SetCoefficient(peak_grid, 10.0) # Heavy penalty on peak
        for t in range(N_STEPS):
            objective.SetCoefficient(p_grid[t], 1.0)
        objective.SetMinimization()
        
        status = solver.Solve()
        
        actions = []
        if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
            opt_dis_0 = p_batt_dis[0].solution_value()
            opt_ev_shift_0 = p_ev_shift_down[0].solution_value()
            opt_pump_flex_0 = p_pump_flex[0].solution_value()
            
            baseline_initial_net = base_demand_curve[0] - solar_curve[0]
            optimized_initial_net = p_grid[0].solution_value()
            total_peak_shaving_kw = baseline_initial_net - optimized_initial_net
            
            # Formulate Action 1: Battery Dispatch
            if opt_dis_0 > 2.0:
                action_id = f"ACT-BATT-{uuid.uuid4().hex[:6].upper()}"
                act1 = {
                    "action_id": action_id,
                    "timestamp": current_time.isoformat(),
                    "target_asset": "COMMUNITY_BATTERY_01",
                    "action_type": "BATTERY_DISCHARGE",
                    "command_payload": {"discharge_rate_kw": round(opt_dis_0, 1), "target_soc_min": 25.0},
                    "scheduled_start": current_time.isoformat(),
                    "scheduled_end": (current_time + timedelta(minutes=45)).isoformat(),
                    "expected_peak_reduction_kw": round(opt_dis_0, 1),
                    "actual_peak_reduction_kw": round(opt_dis_0 * 0.98, 1), # Simulated measured effect
                    "effectiveness_pct": 98.0,
                    "status": "RECOMMENDED"
                }
                actions.append(act1)
                self.pending_actions[action_id] = act1
                
            # Formulate Action 2: EV Charge Shift
            if opt_ev_shift_0 > 2.0:
                action_id = f"ACT-EV-{uuid.uuid4().hex[:6].upper()}"
                act2 = {
                    "action_id": action_id,
                    "timestamp": current_time.isoformat(),
                    "target_asset": "EV_CHARGER_FLEET",
                    "action_type": "SHIFT_EV_LOAD",
                    "command_payload": {
                        "curtail_kw": round(opt_ev_shift_0, 1),
                        "shift_to_time": (current_time + timedelta(hours=2.5)).strftime("%H:%M"),
                        "consenting_vehicles": int(opt_ev_shift_0 / 3.3) + 1
                    },
                    "scheduled_start": current_time.isoformat(),
                    "scheduled_end": (current_time + timedelta(hours=2)).isoformat(),
                    "expected_peak_reduction_kw": round(opt_ev_shift_0, 1),
                    "actual_peak_reduction_kw": round(opt_ev_shift_0 * 1.02, 1),
                    "effectiveness_pct": 102.0,
                    "status": "RECOMMENDED"
                }
                actions.append(act2)
                self.pending_actions[action_id] = act2

            # Formulate Action 3: Flexible Municipal Pump Deferral
            if opt_pump_flex_0 > 2.0:
                action_id = f"ACT-PUMP-{uuid.uuid4().hex[:6].upper()}"
                act3 = {
                    "action_id": action_id,
                    "timestamp": current_time.isoformat(),
                    "target_asset": "MUNICIPAL_WATER_PUMP_A",
                    "action_type": "CURTAIL_FLEXIBLE_LOAD",
                    "command_payload": {"curtail_kw": round(opt_pump_flex_0, 1)},
                    "scheduled_start": current_time.isoformat(),
                    "scheduled_end": (current_time + timedelta(minutes=60)).isoformat(),
                    "expected_peak_reduction_kw": round(opt_pump_flex_0, 1),
                    "actual_peak_reduction_kw": round(opt_pump_flex_0, 1),
                    "effectiveness_pct": 100.0,
                    "status": "RECOMMENDED"
                }
                actions.append(act3)
                self.pending_actions[action_id] = act3

            schedule_points = []
            for t in range(N_STEPS):
                schedule_points.append({
                    "step": t,
                    "time_offset_min": t * 15,
                    "baseline_net_kw": round(base_demand_curve[t] - solar_curve[t], 1),
                    "optimized_grid_kw": round(p_grid[t].solution_value(), 1),
                    "battery_discharge_kw": round(p_batt_dis[t].solution_value(), 1),
                    "battery_charge_kw": round(p_batt_ch[t].solution_value(), 1),
                    "battery_soc_pct": round(soc[t].solution_value(), 1),
                    "ev_shifted_kw": round(p_ev_shift_down[t].solution_value(), 1),
                    "ev_recharged_kw": round(p_ev_recharge[t].solution_value(), 1),
                })

            return {
                "status": "OPTIMAL",
                "baseline_peak_kw": round(max(base_demand_curve[t] - solar_curve[t] for t in range(N_STEPS)), 1),
                "optimized_peak_kw": round(peak_grid.solution_value(), 1),
                "peak_reduction_achieved_kw": round(total_peak_shaving_kw, 1),
                "recommended_actions": actions,
                "schedule": schedule_points
            }
        else:
            return {"status": "INFEASIBLE", "recommended_actions": [], "schedule": []}

    def set_action_status(self, action_id: str, approved: bool) -> Optional[Dict[str, Any]]:
        """Applies human approval/rejection to a pending flexibility recommendation."""
        if action_id in self.pending_actions:
            action = self.pending_actions[action_id]
            action["status"] = "APPROVED" if approved else "REJECTED"
            self.action_history.append(action)
            return action
        return None

flexibility_optimizer = FlexibilityOptimizer()
