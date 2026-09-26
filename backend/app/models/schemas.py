from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, String, Float, DateTime, Integer, Boolean, JSON, ForeignKey, Text, Index
)
from pydantic import BaseModel, Field
from app.core.database import Base

# ==========================================
# SQLAlchemy ORM Models
# ==========================================

class DeviceModel(Base):
    __tablename__ = "devices"
    
    device_id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    device_type = Column(String(32), nullable=False) # 'smart_meter', 'solar_inverter', 'battery_bms', 'ev_charger', 'weather_station', 'grid_feeder'
    manufacturer = Column(String(64), nullable=True)
    model = Column(String(64), nullable=True)
    location = Column(String(128), nullable=True)
    protocol = Column(String(32), default="mqtt") # 'mqtt', 'rest', 'modbus', 'ocpp', 'virtual'
    status = Column(String(32), default="online") # 'online', 'offline', 'degraded'
    health_score = Column(Float, default=1.0)
    packets_received = Column(Integer, default=0)
    packets_rejected = Column(Integer, default=0)
    last_seen = Column(DateTime, default=datetime.utcnow)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class EnergyMeasurementModel(Base):
    __tablename__ = "energy_measurements"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    device_id = Column(String(64), nullable=False, index=True)
    metric = Column(String(32), nullable=False) # active_power, reactive_power, voltage, current, power_factor, energy_kwh
    value = Column(Float, nullable=False)
    unit = Column(String(16), nullable=False) # kW, kVAR, V, A, cos_phi, kWh
    quality = Column(String(16), default="VALID") # VALID, SUSPECT, MISSING, REJECTED
    confidence = Column(Float, default=1.0)

    __table_args__ = (
        Index("idx_energy_time_device", "timestamp", "device_id"),
    )


class SolarMeasurementModel(Base):
    __tablename__ = "solar_measurements"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    device_id = Column(String(64), nullable=False, index=True)
    power_kw = Column(Float, nullable=False)
    energy_kwh = Column(Float, nullable=False)
    irradiance_w_m2 = Column(Float, nullable=True)
    cloud_cover_pct = Column(Float, nullable=True)
    quality = Column(String(16), default="VALID")


class BatteryMeasurementModel(Base):
    __tablename__ = "battery_measurements"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    battery_id = Column(String(64), nullable=False, index=True)
    soc_pct = Column(Float, nullable=False) # 0.0 to 100.0%
    power_kw = Column(Float, nullable=False) # (+) Discharge, (-) Charge
    temperature_c = Column(Float, nullable=True)
    health_soh_pct = Column(Float, default=98.5)
    quality = Column(String(16), default="VALID")


class EVMeasurementModel(Base):
    __tablename__ = "ev_measurements"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    ev_id = Column(String(64), nullable=False, index=True)
    connected = Column(Boolean, default=False)
    charging = Column(Boolean, default=False)
    charging_power_kw = Column(Float, default=0.0)
    soc_pct = Column(Float, default=50.0)
    required_departure = Column(DateTime, nullable=True)
    target_soc_pct = Column(Float, default=85.0)
    user_consent = Column(Boolean, default=True)
    quality = Column(String(16), default="VALID")


class WeatherMeasurementModel(Base):
    __tablename__ = "weather_measurements"
    
    timestamp = Column(DateTime, primary_key=True)
    temperature_c = Column(Float, nullable=False)
    humidity_pct = Column(Float, nullable=False)
    cloud_cover_pct = Column(Float, nullable=False)
    solar_radiation_w_m2 = Column(Float, nullable=False)
    wind_speed_kmh = Column(Float, nullable=False)
    rain_mm = Column(Float, default=0.0)
    quality = Column(String(16), default="VALID")


class AnomalyEventModel(Base):
    __tablename__ = "anomaly_events"
    
    event_id = Column(String(64), primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    device_id = Column(String(64), nullable=True)
    anomaly_type = Column(String(64), nullable=False) # demand_spike, demand_drop, solar_underperformance, ev_cluster, night_anomaly
    expected_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=False)
    deviation_pct = Column(Float, nullable=False)
    severity = Column(String(16), nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    root_cause = Column(Text, nullable=True)
    diagnostic_details = Column(JSON, default=dict)
    status = Column(String(32), default="ACTIVE") # ACTIVE, RESOLVED, ACKNOWLEDGED


class ForecastModel(Base):
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    target_time = Column(DateTime, nullable=False, index=True)
    horizon = Column(String(16), nullable=False) # 15m, 1h, 6h, 24h
    metric = Column(String(32), nullable=False) # demand_kw, solar_kw, net_load_kw
    predicted_value = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    model_version = Column(String(32), default="v1.0.0")


class OptimizationActionModel(Base):
    __tablename__ = "optimization_actions"
    
    action_id = Column(String(64), primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    target_asset = Column(String(64), nullable=False) # COMMUNITY_BATTERY, EV_CHARGER_FLEET, MUNICIPAL_PUMP, HVAC_FLEX
    action_type = Column(String(32), nullable=False) # BATTERY_DISCHARGE, BATTERY_CHARGE, SHIFT_EV_LOAD, CURTAIL_LOAD
    command_payload = Column(JSON, default=dict)
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    expected_peak_reduction_kw = Column(Float, default=0.0)
    actual_peak_reduction_kw = Column(Float, default=0.0)
    effectiveness_pct = Column(Float, default=100.0)
    status = Column(String(32), default="RECOMMENDED") # RECOMMENDED, APPROVED, REJECTED, EXECUTING, COMPLETED


class DailySummaryModel(Base):
    __tablename__ = "daily_summaries"
    
    date_str = Column(String(16), primary_key=True) # YYYY-MM-DD
    total_consumption_kwh = Column(Float, nullable=False)
    peak_demand_kw = Column(Float, nullable=False)
    peak_time = Column(String(16), nullable=False)
    min_demand_kw = Column(Float, nullable=False)
    avg_demand_kw = Column(Float, nullable=False)
    solar_generation_kwh = Column(Float, nullable=False)
    grid_import_kwh = Column(Float, nullable=False)
    battery_throughput_kwh = Column(Float, default=0.0)
    anomaly_count = Column(Integer, default=0)
    opt_actions_count = Column(Integer, default=0)
    peak_reduction_achieved_kw = Column(Float, default=0.0)
    explanation = Column(Text, nullable=True)
    baseline_deviation_pct = Column(Float, default=0.0)


# ==========================================
# Pydantic Schemas / DTOs
# ==========================================

class DeviceBase(BaseModel):
    device_id: str
    name: str
    device_type: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    protocol: Optional[str] = "mqtt"
    status: Optional[str] = "online"
    health_score: Optional[float] = 1.0
    config: Optional[Dict[str, Any]] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    packets_received: int = 0
    packets_rejected: int = 0
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class IngestionPayload(BaseModel):
    device_id: str
    timestamp: Optional[str] = None
    metric: str
    value: float
    unit: str
    metadata: Optional[Dict[str, Any]] = None


class LiveStateResponse(BaseModel):
    timestamp: str
    current_demand_kw: float
    household_demand_kw: float = 0.0
    expected_demand_kw: float
    demand_deviation_pct: float
    solar_generation_kw: float
    expected_solar_kw: float
    battery_soc_pct: float
    battery_power_kw: float # (+) discharge, (-) charge
    ev_charging_kw: float
    ev_active_count: int
    net_grid_import_kw: float
    voltage_v: float = 415.0
    current_a: float = 120.0
    power_factor: float = 0.95
    feeder_capacity_kw: float
    feeder_loading_pct: float
    ambient_temperature_c: float
    cloud_cover_pct: float
    solar_radiation_w_m2: float
    reliability_risk_level: str # LOW, MEDIUM, HIGH, CRITICAL
    reliability_risk_reason: str
    data_quality_score: float = 100.0 # 0.0 to 100%
    active_anomalies_count: int = 0
    active_scenario: str = "NORMAL"
    active_anomalies: List[Dict[str, Any]] = []
    system_mode: str = "DIGITAL_TWIN" # LIVE, DIGITAL_TWIN, REPLAY



class AnomalyResponse(BaseModel):
    event_id: str
    timestamp: str
    device_id: Optional[str]
    anomaly_type: str
    expected_value: float
    actual_value: float
    deviation_pct: float
    severity: str
    root_cause: Optional[str]
    diagnostic_details: Optional[Dict[str, Any]]
    status: str

    class Config:
        from_attributes = True


class ForecastPoint(BaseModel):
    target_time: str
    predicted_demand_kw: float
    baseline_demand_kw: float
    predicted_solar_kw: float
    predicted_net_load_kw: float
    lower_bound_kw: float
    upper_bound_kw: float


class ForecastAccuracy(BaseModel):
    horizon: str
    mae_kw: float
    rmse_kw: float
    mape_pct: float
    confidence_score_pct: float


class MultiHorizonForecastResponse(BaseModel):
    timestamp: str
    horizon_15m: List[ForecastPoint]
    horizon_1h: List[ForecastPoint]
    horizon_6h: List[ForecastPoint]
    horizon_24h: List[ForecastPoint]
    accuracy_metrics: List[ForecastAccuracy]


class OptimizationActionDTO(BaseModel):
    action_id: str
    timestamp: str
    target_asset: str
    action_type: str
    command_payload: Dict[str, Any]
    scheduled_start: str
    scheduled_end: str
    expected_peak_reduction_kw: float
    actual_peak_reduction_kw: float
    effectiveness_pct: float
    status: str

    class Config:
        from_attributes = True


class OptimizationApprovalRequest(BaseModel):
    action_id: str
    approved: bool


class DailyAnalysisResponse(BaseModel):
    date_str: str
    total_consumption_kwh: float
    peak_demand_kw: float
    peak_time: str
    min_demand_kw: float
    avg_demand_kw: float
    solar_generation_kwh: float
    grid_import_kwh: float
    battery_throughput_kwh: float
    anomaly_count: int
    opt_actions_count: int
    peak_reduction_achieved_kw: float
    comparison_vs_7d_pct: float
    comparison_vs_30d_pct: float
    comparison_vs_same_weekday_pct: float
    explanation: str
    hourly_curve: List[Dict[str, Any]]
    events: List[AnomalyResponse]


class WhatIfRequest(BaseModel):
    battery_capacity_kwh: float = 100.0
    ev_dr_participation_pct: float = 30.0 # 0 to 100%
    solar_capacity_multiplier: float = 1.0 # 1.0 = baseline, 1.2 = +20%
    simulated_temperature_offset_c: float = 0.0


class WhatIfResponse(BaseModel):
    baseline_peak_kw: float
    optimized_peak_kw: float
    peak_reduction_kw: float
    peak_reduction_pct: float
    baseline_grid_import_kwh: float
    optimized_grid_import_kwh: float
    grid_reduction_pct: float
    co2_saved_kg: float
    estimated_cost_savings_inr: float
    feeder_stress_hours_saved: float
    hourly_comparison: List[Dict[str, Any]]


class FeederStatus(BaseModel):
    feeder_id: str
    name: str
    current_load_kw: float
    capacity_kw: float
    loading_pct: float
    solar_connected_kw: float
    battery_storage_kwh: float
    flexible_capacity_kw: float
    risk_level: str # GREEN, YELLOW, RED
    status_reason: str
