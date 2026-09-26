from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.schemas import DeviceModel, DeviceCreate, DeviceResponse

router = APIRouter(prefix="/devices", tags=["Devices"])

@router.get("", response_model=List[DeviceResponse])
async def list_devices(db: AsyncSession = Depends(get_db)):
    """Lists all registered physical and virtual energy devices."""
    result = await db.execute(select(DeviceModel).order_by(DeviceModel.created_at.asc()))
    devices = result.scalars().all()
    return devices

@router.post("", response_model=DeviceResponse)
async def create_device(device_in: DeviceCreate, db: AsyncSession = Depends(get_db)):
    """Registers a new energy device (Smart Meter, Solar Inverter, Battery, EV Charger)."""
    existing = await db.get(DeviceModel, device_in.device_id)
    if existing:
        raise HTTPException(status_code=400, detail="Device ID already registered")
        
    device = DeviceModel(
        device_id=device_in.device_id,
        name=device_in.name,
        device_type=device_in.device_type,
        manufacturer=device_in.manufacturer,
        model=device_in.model,
        location=device_in.location,
        protocol=device_in.protocol or "mqtt",
        status=device_in.status or "online",
        health_score=1.0,
        config=device_in.config or {},
        last_seen=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device

@router.delete("/{device_id}")
async def delete_device(device_id: str, db: AsyncSession = Depends(get_db)):
    """Removes a device registration."""
    device = await db.get(DeviceModel, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    await db.delete(device)
    await db.commit()
    return {"message": f"Device {device_id} deleted successfully"}
