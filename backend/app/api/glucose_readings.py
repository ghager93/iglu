from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.database import get_db
from app.models import glucose_reading as models
from app.schemas import glucose_reading as schemas
from app.schemas.glucose_reading import RemoteReading
import fetch_glucose
from loguru import logger
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

router = APIRouter(
    prefix="/glucose-readings",
    tags=["glucose-readings"],
)

@router.get("/", response_model=List[schemas.GlucoseReading])
async def get_glucose_readings(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all glucose readings"""
    result = await db.execute(select(models.GlucoseReading).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/", response_model=schemas.GlucoseReading)
async def create_glucose_reading(reading: schemas.GlucoseReadingCreate, db: AsyncSession = Depends(get_db)):
    """Create a new glucose reading"""
    db_reading = models.GlucoseReading(
        level=reading.level,
        notes=reading.notes
    )
    db.add(db_reading)
    await db.commit()
    await db.refresh(db_reading)
    return db_reading

async def fetch_and_save_remote_readings(db: AsyncSession) -> List[RemoteReading]:
    """Fetch remote glucose readings and upsert into the database."""
    logger.debug("fetch_and_save_remote_readings called")
    token = await fetch_glucose.get_token()
    logger.debug(f"Retrieved token: {token[:8]}... (truncated)")
    readings = await fetch_glucose.fetch_glucose_readings(token)
    rows = [{"value": r["value"], "timestamp": r["timestamp"]} for r in readings]
    if rows:
        stmt = sqlite_insert(models.GlucoseReading).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["timestamp"],
            set_={"value": stmt.excluded["value"]}
        )
        await db.execute(stmt)
        await db.commit()
    logger.info(f"Successfully fetched {len(readings)} remote readings")
    return readings

@router.get("/remote", response_model=List[RemoteReading])
async def get_remote_readings(db: AsyncSession = Depends(get_db)):
    """Fetch glucose readings from remote API and return list of RemoteReading"""
    logger.debug("get_remote_readings called")
    try:
        return await fetch_and_save_remote_readings(db)
    except Exception as e:
        logger.exception("Error in get_remote_readings")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/db", response_model=List[schemas.RemoteReading])
async def get_db_readings(db: AsyncSession = Depends(get_db)):
    """Get glucose readings from DB with epoch timestamp"""
    result = await db.execute(select(models.GlucoseReading))
    readings = result.scalars().all()
    return readings

@router.get("/{reading_id}", response_model=schemas.GlucoseReading)
async def get_glucose_reading(reading_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific glucose reading by ID"""
    result = await db.execute(select(models.GlucoseReading).filter(models.GlucoseReading.id == reading_id))
    db_reading = result.scalars().first()
    if db_reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    return db_reading

@router.delete("/{reading_id}")
async def delete_glucose_reading(reading_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a glucose reading"""
    result = await db.execute(select(models.GlucoseReading).filter(models.GlucoseReading.id == reading_id))
    db_reading = result.scalars().first()
    if db_reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    await db.delete(db_reading)
    await db.commit()
    return {"message": "Reading deleted successfully"}
