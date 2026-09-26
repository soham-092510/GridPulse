import httpx
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.core.config import settings

class WeatherService:
    """
    Fetches real-time and forecast solar & meteorological variables from Open-Meteo.
    Includes caching and robust fallback solar irradiance physics models.
    """
    
    def __init__(self):
        self._cached_current: Optional[Dict[str, Any]] = None
        self._cached_forecast: Optional[Dict[str, Any]] = None
        self._last_fetch_time: Optional[datetime] = None
        self._cache_duration = timedelta(minutes=15)
        
    async def get_current_weather(self) -> Dict[str, Any]:
        """Returns current weather readings (live Open-Meteo or cached/fallback)."""
        now = datetime.utcnow()
        if self._cached_current and self._last_fetch_time and (now - self._last_fetch_time < self._cache_duration):
            return self._cached_current
            
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": settings.LATITUDE,
                "longitude": settings.LONGITUDE,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "cloud_cover",
                    "direct_normal_irradiance",
                    "diffuse_radiation",
                    "direct_radiation",
                    "wind_speed_10m"
                ],
                "timezone": "auto"
            }
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    curr = data.get("current", {})
                    direct_rad = curr.get("direct_radiation", 0.0) or 0.0
                    diffuse_rad = curr.get("diffuse_radiation", 0.0) or 0.0
                    total_rad = direct_rad + diffuse_rad
                    
                    result = {
                        "timestamp": now.isoformat(),
                        "temperature_c": float(curr.get("temperature_2m", 31.5)),
                        "humidity_pct": float(curr.get("relative_humidity_2m", 65.0)),
                        "cloud_cover_pct": float(curr.get("cloud_cover", 20.0)),
                        "solar_radiation_w_m2": round(total_rad, 2),
                        "wind_speed_kmh": float(curr.get("wind_speed_10m", 12.0)),
                        "source": "Open-Meteo Live API"
                    }
                    self._cached_current = result
                    self._last_fetch_time = now
                    return result
        except Exception:
            pass
            
        # Fallback to diurnal solar model
        return self._fallback_diurnal_weather(now)

    async def get_hourly_forecast(self, hours: int = 24) -> Dict[str, Any]:
        """Returns hourly weather forecast for the specified horizon."""
        now = datetime.utcnow()
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": settings.LATITUDE,
                "longitude": settings.LONGITUDE,
                "hourly": [
                    "temperature_2m",
                    "cloud_cover",
                    "direct_radiation",
                    "diffuse_radiation"
                ],
                "forecast_days": 2,
                "timezone": "auto"
            }
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json().get("hourly", {})
                    times = data.get("time", [])
                    temps = data.get("temperature_2m", [])
                    clouds = data.get("cloud_cover", [])
                    direct = data.get("direct_radiation", [])
                    diffuse = data.get("diffuse_radiation", [])
                    
                    forecast_list = []
                    for i in range(min(hours, len(times))):
                        rad = (direct[i] or 0.0) + (diffuse[i] or 0.0)
                        forecast_list.append({
                            "time": times[i],
                            "temperature_c": temps[i] if i < len(temps) else 30.0,
                            "cloud_cover_pct": clouds[i] if i < len(clouds) else 20.0,
                            "solar_radiation_w_m2": round(rad, 2)
                        })
                    return {"forecast": forecast_list, "source": "Open-Meteo API"}
        except Exception:
            pass
            
        # Fallback hourly model
        forecast_list = []
        for i in range(hours):
            t = now + timedelta(hours=i)
            w = self._fallback_diurnal_weather(t)
            forecast_list.append({
                "time": t.strftime("%Y-%m-%dT%H:00:00"),
                "temperature_c": w["temperature_c"],
                "cloud_cover_pct": w["cloud_cover_pct"],
                "solar_radiation_w_m2": w["solar_radiation_w_m2"]
            })
        return {"forecast": forecast_list, "source": "Diurnal Solar Model Fallback"}

    def _fallback_diurnal_weather(self, dt: datetime) -> Dict[str, Any]:
        """Calculates physically plausible solar radiation and ambient temperature based on time of day."""
        hour = dt.hour + dt.minute / 60.0
        
        # Solar radiation model (Peak ~ 850 W/m2 at 12:30 PM, zero before 06:00 and after 18:30)
        if 6.0 <= hour <= 18.5:
            day_fraction = (hour - 6.0) / (18.5 - 6.0)
            radiation = 850.0 * math.sin(day_fraction * math.pi)
        else:
            radiation = 0.0
            
        # Diurnal Temperature model (Min 25°C at 05:30 AM, Max 34.5°C at 15:00 PM)
        temp = 29.5 + 4.5 * math.sin((hour - 9.0) / 12.0 * math.pi)
        
        return {
            "timestamp": dt.isoformat(),
            "temperature_c": round(temp, 1),
            "humidity_pct": 65.0,
            "cloud_cover_pct": 18.0,
            "solar_radiation_w_m2": round(max(0.0, radiation), 1),
            "wind_speed_kmh": 12.5,
            "source": "Solar Geometry Fallback"
        }

weather_service = WeatherService()
