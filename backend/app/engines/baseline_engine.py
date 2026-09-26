import numpy as np
import pandas as pd
from datetime import datetime, time
from typing import Dict, Any, Optional, Tuple
import math

class BaselineEngine:
    """
    Computes stratified historical energy baselines considering:
    - Day of week (Monday vs Saturday vs Sunday)
    - 15-minute time slot of the day (0 to 95)
    - Ambient temperature stratification (<28°C, 28-33°C, >33°C)
    - Continuous rolling accumulation from newly stored historical data.
    """
    
    def __init__(self):
        # Baseline profile lookup tables
        self.is_trained = False
        self.profile_lookup: Dict[Tuple[int, int, str], Dict[str, float]] = {}
        self.overall_weekday_profiles: Dict[Tuple[int, int], float] = {}
        self.recent_7d_weights: Dict[int, float] = {}
        
    def _get_temp_bin(self, temp_c: float) -> str:
        if temp_c < 28.0:
            return "COOL"
        elif temp_c <= 33.5:
            return "MODERATE"
        else:
            return "HOT"

    def fit_from_dataframe(self, df: pd.DataFrame):
        """
        Fits baseline tables from historical DataFrame with columns:
        ['timestamp', 'active_power', 'temperature_c']
        """
        if df.empty:
            return
            
        df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['slot_15m'] = (df['timestamp'].dt.hour * 60 + df['timestamp'].dt.minute) // 15
        df['temp_bin'] = df['temperature_c'].apply(self._get_temp_bin)
        
        # Group by (day_of_week, slot_15m, temp_bin)
        grouped = df.groupby(['day_of_week', 'slot_15m', 'temp_bin'])['active_power'].agg(
            mean='mean',
            std='std',
            p10=lambda x: np.percentile(x, 10),
            p90=lambda x: np.percentile(x, 90),
            count='count'
        ).reset_index()
        
        self.profile_lookup.clear()
        for _, row in grouped.iterrows():
            key = (int(row['day_of_week']), int(row['slot_15m']), str(row['temp_bin']))
            std_val = row['std'] if not pd.isna(row['std']) and row['std'] > 0 else 4.5
            self.profile_lookup[key] = {
                "mean": round(float(row['mean']), 2),
                "std": round(float(std_val), 2),
                "p10": round(float(row['p10']), 2),
                "p90": round(float(row['p90']), 2),
                "count": int(row['count'])
            }
            
        # Fallback profile grouped only by (day_of_week, slot_15m)
        weekday_grouped = df.groupby(['day_of_week', 'slot_15m'])['active_power'].mean().reset_index()
        self.overall_weekday_profiles.clear()
        for _, row in weekday_grouped.iterrows():
            self.overall_weekday_profiles[(int(row['day_of_week']), int(row['slot_15m']))] = round(float(row['active_power']), 2)
            
        self.is_trained = True

    def get_expected_demand(self, dt: datetime, ambient_temp_c: float = 30.0) -> Dict[str, Any]:
        """
        Returns weather-normalized expected demand and normal bounds for given time and temp.
        """
        dow = dt.weekday()
        slot = (dt.hour * 60 + dt.minute) // 15
        temp_bin = self._get_temp_bin(ambient_temp_c)
        key = (dow, slot, temp_bin)
        
        if key in self.profile_lookup:
            stats = self.profile_lookup[key]
            mean_val = stats["mean"]
            std_val = stats["std"]
            p10 = stats["p10"]
            p90 = stats["p90"]
            label = f"Stratified Baseline (Weekday {dow}, Slot {slot}, {temp_bin})"
        elif (dow, slot) in self.overall_weekday_profiles:
            mean_val = self.overall_weekday_profiles[(dow, slot)]
            # Adjust slightly for temperature (+2.5% per °C above 32°C for air conditioning)
            if ambient_temp_c > 32.0:
                mean_val *= (1.0 + (ambient_temp_c - 32.0) * 0.035)
            std_val = 5.5
            p10 = max(10.0, mean_val - 1.64 * std_val)
            p90 = mean_val + 1.64 * std_val
            label = f"Weekday Baseline with Temp Adjustment (Weekday {dow}, Slot {slot})"
        else:
            # Synthetic diurnal fallback if no data loaded yet
            hour_float = dt.hour + dt.minute / 60.0
            # Typical residential/neighbourhood profile (low at night 25kW, morning rise 65kW, evening peak 85kW)
            base = 40.0 + 25.0 * math.sin((hour_float - 6.0) / 12.0 * math.pi)
            if 18.0 <= hour_float <= 22.5:
                base += 28.0 # Evening peak
            if ambient_temp_c > 32.0:
                base += (ambient_temp_c - 32.0) * 2.8
            mean_val = round(base, 2)
            std_val = 6.0
            p10 = round(mean_val - 10.0, 2)
            p90 = round(mean_val + 12.0, 2)
            label = "Analytical Default Neighbourhood Baseline"
            
        return {
            "expected_kw": round(mean_val, 2),
            "std_kw": round(std_val, 2),
            "min_expected_kw": round(p10, 2),
            "max_expected_kw": round(p90, 2),
            "baseline_label": label,
            "temp_bin": temp_bin
        }

    def get_expected_solar(self, dt: datetime, cloud_cover_pct: float = 15.0, solar_capacity_kw: float = 80.0) -> Dict[str, Any]:
        """Calculates expected clean-sky and cloud-attenuated solar generation."""
        hour_float = dt.hour + dt.minute / 60.0
        if 6.0 <= hour_float <= 18.5:
            # Sinusoidal solar generation
            day_fraction = (hour_float - 6.0) / 12.5
            clear_sky_output = solar_capacity_kw * math.sin(day_fraction * math.pi)
            # Cloud attenuation factor (1 - 0.75 * (cloud / 100)^1.5)
            attenuation = max(0.1, 1.0 - 0.75 * math.pow(cloud_cover_pct / 100.0, 1.5))
            expected_solar = clear_sky_output * attenuation
        else:
            expected_solar = 0.0
            
        return {
            "expected_solar_kw": round(max(0.0, expected_solar), 2),
            "clear_sky_kw": round(max(0.0, clear_sky_output if 6.0 <= hour_float <= 18.5 else 0.0), 2)
        }

baseline_engine = BaselineEngine()
