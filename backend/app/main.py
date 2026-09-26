import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.data.historical_seed import generate_and_seed_historical_data
from app.ingestion.mqtt_client import mqtt_bridge

from app.api.devices import router as devices_router
from app.api.ingestion import router as ingestion_router
from app.api.measurements import router as measurements_router
from app.api.baseline import router as baseline_router
from app.api.anomalies import router as anomalies_router
from app.api.forecasts import router as forecasts_router
from app.api.optimization import router as optimization_router
from app.api.daily_analysis import router as daily_analysis_router
from app.api.what_if import router as what_if_router
from app.api.discom import router as discom_router
from app.api.websocket import router as websocket_router, telemetry_broadcaster_loop

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("neighbourflex")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Sequence
    logger.info("Starting NeighbourFlex Real-Time Energy Intelligence Platform...")
    
    # 1. Initialize SQLite / TimescaleDB schema
    await init_db()
    logger.info("Database schema initialized.")
    
    # 2. Seed 21-day historical baseline and default assets
    generate_and_seed_historical_data()
    
    # 3. Start MQTT ingestion bridge
    mqtt_bridge.start()
    
    # 4. Start background real-time WebSocket broadcast task
    broadcaster_task = asyncio.create_task(telemetry_broadcaster_loop())
    
    yield
    
    # Shutdown Sequence
    logger.info("Shutting down NeighbourFlex services...")
    broadcaster_task.cancel()
    mqtt_bridge.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Real-Time AI Neighbourhood Energy Intelligence & Flexibility Platform",
    lifespan=lifespan
)

# Enable CORS for local Vite and production frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(devices_router, prefix=settings.API_V1_STR)
app.include_router(ingestion_router, prefix=settings.API_V1_STR)
app.include_router(measurements_router, prefix=settings.API_V1_STR)
app.include_router(baseline_router, prefix=settings.API_V1_STR)
app.include_router(anomalies_router, prefix=settings.API_V1_STR)
app.include_router(forecasts_router, prefix=settings.API_V1_STR)
app.include_router(optimization_router, prefix=settings.API_V1_STR)
app.include_router(daily_analysis_router, prefix=settings.API_V1_STR)
app.include_router(what_if_router, prefix=settings.API_V1_STR)
app.include_router(discom_router, prefix=settings.API_V1_STR)
app.include_router(websocket_router)

@app.get("/")
async def root():
    return {
        "status": "ONLINE",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_url": "/health",
        "api_prefix": settings.API_V1_STR
    }

@app.get("/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mqtt_connected": mqtt_bridge.is_connected
    }

