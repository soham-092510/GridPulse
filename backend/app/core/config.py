import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "NeighbourFlex"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database configuration
    # Default to high-performance local SQLite for friction-free execution, with seamless Postgres/TimescaleDB support
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/neighbourflex.db")
    SYNC_DATABASE_URL: str = os.getenv("SYNC_DATABASE_URL", f"sqlite:///{BASE_DIR}/neighbourflex.db")
    
    # MQTT Broker configuration
    MQTT_BROKER_HOST: str = os.getenv("MQTT_BROKER_HOST", "localhost")
    MQTT_BROKER_PORT: int = int(os.getenv("MQTT_BROKER_PORT", 1883))
    MQTT_TOPIC_PREFIX: str = "neighbourflex"
    
    # Geographic Location (Default: Mumbai / Maharashtra SLDC grid region)
    LATITUDE: float = float(os.getenv("LATITUDE", 19.0760))
    LONGITUDE: float = float(os.getenv("LONGITUDE", 72.8777))
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Kolkata")
    
    # Feeder Limits & Asset Specifications
    DEFAULT_FEEDER_CAPACITY_KW: float = float(os.getenv("FEEDER_CAPACITY_KW", 125.0))
    DEFAULT_BATTERY_CAPACITY_KWH: float = float(os.getenv("BATTERY_CAPACITY_KWH", 100.0))
    DEFAULT_BATTERY_MAX_POWER_KW: float = float(os.getenv("BATTERY_MAX_POWER_KW", 30.0))
    DEFAULT_SOLAR_CAPACITY_KW: float = float(os.getenv("SOLAR_CAPACITY_KW", 80.0))
    
    # Simulation & Stream speeds
    SIMULATION_TICK_SECONDS: int = 2
    REPLAY_SPEED_MULTIPLIER: int = 10
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
