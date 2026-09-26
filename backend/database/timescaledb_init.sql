-- ==========================================================
-- NeighbourFlex TimescaleDB & PostgreSQL Production Schema
-- Real-Time AI Neighbourhood Energy Intelligence & Flexibility
-- ==========================================================

-- Enable TimescaleDB Extension if available
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- 1. Devices Registry
CREATE TABLE IF NOT EXISTS devices (
    device_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    device_type VARCHAR(32) NOT NULL, -- 'smart_meter', 'solar_inverter', 'battery_bms', 'ev_charger', 'weather_station', 'grid_feeder'
    manufacturer VARCHAR(64),
    model VARCHAR(64),
    location VARCHAR(128),
    protocol VARCHAR(32) DEFAULT 'mqtt', -- 'mqtt', 'rest', 'modbus', 'ocpp', 'virtual'
    status VARCHAR(32) DEFAULT 'online', -- 'online', 'offline', 'degraded'
    health_score FLOAT DEFAULT 1.0,      -- 0.0 to 1.0
    last_seen TIMESTAMPTZ,
    config JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Canonical Energy Measurements (Hypertable)
CREATE TABLE IF NOT EXISTS energy_measurements (
    timestamp TIMESTAMPTZ NOT NULL,
    device_id VARCHAR(64) NOT NULL,
    metric VARCHAR(32) NOT NULL, -- 'active_power', 'reactive_power', 'voltage', 'current', 'power_factor', 'energy_kwh'
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(16) NOT NULL,   -- 'kW', 'kVAR', 'V', 'A', 'cos_phi', 'kWh'
    quality VARCHAR(16) NOT NULL DEFAULT 'VALID', -- 'VALID', 'SUSPECT', 'MISSING', 'REJECTED'
    confidence FLOAT DEFAULT 1.0,
    CONSTRAINT pk_energy_measurements PRIMARY KEY (timestamp, device_id, metric)
);

-- Convert to Hypertable partitioned by 1-day chunks
SELECT create_hypertable('energy_measurements', 'timestamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_energy_meas_dev_time ON energy_measurements (device_id, timestamp DESC);

-- 3. Solar Generation Measurements (Hypertable)
CREATE TABLE IF NOT EXISTS solar_measurements (
    timestamp TIMESTAMPTZ NOT NULL,
    device_id VARCHAR(64) NOT NULL,
    power_kw DOUBLE PRECISION NOT NULL,
    energy_kwh DOUBLE PRECISION NOT NULL,
    irradiance_w_m2 DOUBLE PRECISION,
    cloud_cover_pct DOUBLE PRECISION,
    quality VARCHAR(16) DEFAULT 'VALID',
    CONSTRAINT pk_solar_measurements PRIMARY KEY (timestamp, device_id)
);
SELECT create_hypertable('solar_measurements', 'timestamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE);

-- 4. Battery Storage Telemetry (Hypertable)
CREATE TABLE IF NOT EXISTS battery_measurements (
    timestamp TIMESTAMPTZ NOT NULL,
    battery_id VARCHAR(64) NOT NULL,
    soc_pct DOUBLE PRECISION NOT NULL,     -- 0.0 to 100.0%
    power_kw DOUBLE PRECISION NOT NULL,    -- (+) Discharging to neighbourhood, (-) Charging from solar/grid
    temperature_c DOUBLE PRECISION,
    health_soh_pct DOUBLE PRECISION DEFAULT 98.5,
    quality VARCHAR(16) DEFAULT 'VALID',
    CONSTRAINT pk_battery_measurements PRIMARY KEY (timestamp, battery_id)
);
SELECT create_hypertable('battery_measurements', 'timestamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE);

-- 5. EV Charging Telemetry (Hypertable)
CREATE TABLE IF NOT EXISTS ev_measurements (
    timestamp TIMESTAMPTZ NOT NULL,
    ev_id VARCHAR(64) NOT NULL,
    connected BOOLEAN NOT NULL DEFAULT FALSE,
    charging BOOLEAN NOT NULL DEFAULT FALSE,
    charging_power_kw DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    soc_pct DOUBLE PRECISION NOT NULL,
    required_departure TIMESTAMPTZ,
    target_soc_pct DOUBLE PRECISION DEFAULT 85.0,
    user_consent BOOLEAN DEFAULT TRUE,
    quality VARCHAR(16) DEFAULT 'VALID',
    CONSTRAINT pk_ev_measurements PRIMARY KEY (timestamp, ev_id)
);
SELECT create_hypertable('ev_measurements', 'timestamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE);

-- 6. Weather & Climate Telemetry (Hypertable)
CREATE TABLE IF NOT EXISTS weather_measurements (
    timestamp TIMESTAMPTZ NOT NULL PRIMARY KEY,
    temperature_c DOUBLE PRECISION NOT NULL,
    humidity_pct DOUBLE PRECISION NOT NULL,
    cloud_cover_pct DOUBLE PRECISION NOT NULL,
    solar_radiation_w_m2 DOUBLE PRECISION NOT NULL,
    wind_speed_kmh DOUBLE PRECISION NOT NULL,
    rain_mm DOUBLE PRECISION DEFAULT 0.0,
    quality VARCHAR(16) DEFAULT 'VALID'
);
SELECT create_hypertable('weather_measurements', 'timestamp', chunk_time_interval => INTERVAL '7 days', if_not_exists => TRUE);

-- 7. Energy Anomalies & Root-Cause Events
CREATE TABLE IF NOT EXISTS anomaly_events (
    event_id VARCHAR(64) PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    device_id VARCHAR(64),
    anomaly_type VARCHAR(64) NOT NULL, -- 'demand_spike', 'demand_drop', 'solar_underperformance', 'ev_cluster', 'night_anomaly', 'forecast_divergence'
    expected_value DOUBLE PRECISION NOT NULL,
    actual_value DOUBLE PRECISION NOT NULL,
    deviation_pct DOUBLE PRECISION NOT NULL,
    severity VARCHAR(16) NOT NULL,     -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    root_cause TEXT,
    diagnostic_details JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(32) DEFAULT 'ACTIVE' -- 'ACTIVE', 'RESOLVED', 'ACKNOWLEDGED'
);
CREATE INDEX IF NOT EXISTS idx_anomaly_time ON anomaly_events (timestamp DESC);

-- 8. Multi-Horizon Forecasts (Hypertable)
CREATE TABLE IF NOT EXISTS forecasts (
    timestamp TIMESTAMPTZ NOT NULL,    -- Time forecast was created
    target_time TIMESTAMPTZ NOT NULL,  -- Future point in time
    horizon VARCHAR(16) NOT NULL,      -- '15m', '1h', '6h', '24h'
    metric VARCHAR(32) NOT NULL,       -- 'demand_kw', 'solar_kw', 'net_load_kw'
    predicted_value DOUBLE PRECISION NOT NULL,
    lower_bound DOUBLE PRECISION,
    upper_bound DOUBLE PRECISION,
    model_version VARCHAR(32) DEFAULT 'v1.0.0',
    CONSTRAINT pk_forecasts PRIMARY KEY (timestamp, target_time, horizon, metric)
);
SELECT create_hypertable('forecasts', 'timestamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE);

-- 9. Flexibility Optimization & Control Actions
CREATE TABLE IF NOT EXISTS optimization_actions (
    action_id VARCHAR(64) PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    target_asset VARCHAR(64) NOT NULL, -- 'COMMUNITY_BATTERY_01', 'EV_FLEET', 'MUNICIPAL_WATER_PUMP_A', 'HVAC_FLEX_ZONE'
    action_type VARCHAR(32) NOT NULL,  -- 'BATTERY_DISCHARGE', 'BATTERY_CHARGE', 'SHIFT_EV_LOAD', 'CURTAIL_FLEXIBLE_LOAD'
    command_payload JSONB NOT NULL,
    scheduled_start TIMESTAMPTZ NOT NULL,
    scheduled_end TIMESTAMPTZ NOT NULL,
    expected_peak_reduction_kw DOUBLE PRECISION,
    actual_peak_reduction_kw DOUBLE PRECISION,
    effectiveness_pct DOUBLE PRECISION,
    status VARCHAR(32) DEFAULT 'RECOMMENDED' -- 'RECOMMENDED', 'APPROVED', 'REJECTED', 'EXECUTING', 'COMPLETED'
);

-- 10. Continuous Aggregates: Hourly Rollup View
CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_energy_summary
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', timestamp) AS hour_bucket,
    device_id,
    AVG(value) FILTER (WHERE metric = 'active_power') AS avg_power_kw,
    MAX(value) FILTER (WHERE metric = 'active_power') AS peak_power_kw,
    MIN(value) FILTER (WHERE metric = 'active_power') AS min_power_kw
FROM energy_measurements
WHERE quality = 'VALID'
GROUP BY hour_bucket, device_id
WITH NO DATA;
