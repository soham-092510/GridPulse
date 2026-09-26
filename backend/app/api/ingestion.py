from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Dict, Any, List

from app.core.database import get_db
from app.models.schemas import IngestionPayload, DeviceModel, EnergyMeasurementModel
from app.ingestion.normalizer import MeasurementNormalizer
from app.ingestion.validator import validator_engine

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])

@router.post("/telemetry")
async def ingest_single_reading(payload: IngestionPayload, db: AsyncSession = Depends(get_db)):
    """
    Universal Data Gateway single-point telemetry endpoint.
    Accepts raw device reading, normalizes units, validates physical boundaries,
    and stores measurement with quality and confidence scores.
    """
    ts = datetime.fromisoformat(payload.timestamp) if payload.timestamp else datetime.utcnow()
    
    # 1. Normalize
    metric, norm_val, unit = MeasurementNormalizer.normalize(payload.metric, payload.value, payload.unit)
    
    # 2. Validate
    quality, confidence, warning = validator_engine.validate(payload.device_id, metric, norm_val, ts)
    
    # 3. Update device status
    device = await db.get(DeviceModel, payload.device_id)
    if device:
        device.last_seen = ts
        device.packets_received += 1
        if quality == "REJECTED":
            device.packets_rejected += 1
        # Recalculate health score
        total = device.packets_received
        device.health_score = round(max(0.0, 1.0 - (device.packets_rejected / max(1, total))), 3)
    
    if quality == "REJECTED":
        if device:
            await db.commit()
        return {
            "status": "REJECTED",
            "reason": warning,
            "device_id": payload.device_id,
            "metric": metric,
            "value": norm_val,
            "unit": unit
        }
        
    # 4. Save Measurement
    meas = EnergyMeasurementModel(
        timestamp=ts,
        device_id=payload.device_id,
        metric=metric,
        value=norm_val,
        unit=unit,
        quality=quality,
        confidence=confidence
    )
    db.add(meas)
    await db.commit()
    
    return {
        "status": "ACCEPTED",
        "quality": quality,
        "confidence": confidence,
        "warning": warning,
        "normalized_value": norm_val,
        "canonical_unit": unit,
        "timestamp": ts.isoformat()
    }

@router.post("/batch")
async def ingest_batch_readings(payloads: List[IngestionPayload], db: AsyncSession = Depends(get_db)):
    """Batch telemetry ingestion for CSV uploads or multi-meter gateways."""
    accepted = 0
    rejected = 0
    
    for p in payloads:
        ts = datetime.fromisoformat(p.timestamp) if p.timestamp else datetime.utcnow()
        metric, norm_val, unit = MeasurementNormalizer.normalize(p.metric, p.value, p.unit)
        quality, conf, _ = validator_engine.validate(p.device_id, metric, norm_val, ts)
        
        if quality != "REJECTED":
            meas = EnergyMeasurementModel(
                timestamp=ts,
                device_id=p.device_id,
                metric=metric,
                value=norm_val,
                unit=unit,
                quality=quality,
                confidence=conf
            )
            db.add(meas)
            accepted += 1
        else:
            rejected += 1
            
    await db.commit()
    return {"message": "Batch processed", "accepted": accepted, "rejected": rejected}
