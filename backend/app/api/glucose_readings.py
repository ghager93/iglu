from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models import glucose_reading as models
from app.schemas import glucose_reading as schemas
from app.schemas.glucose_reading import RemoteReading
import fetch_glucose
from loguru import logger

router = APIRouter(
    prefix="/glucose-readings",
    tags=["glucose-readings"],
)

@router.get("/", response_model=List[schemas.GlucoseReading])
def get_glucose_readings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all glucose readings"""
    readings = db.query(models.GlucoseReading).offset(skip).limit(limit).all()
    return readings

@router.post("/", response_model=schemas.GlucoseReading)
def create_glucose_reading(reading: schemas.GlucoseReadingCreate, db: Session = Depends(get_db)):
    """Create a new glucose reading"""
    db_reading = models.GlucoseReading(
        level=reading.level,
        notes=reading.notes
    )
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

@router.get("/remote", response_model=List[RemoteReading])
def get_remote_readings():
    """Fetch glucose readings from remote API and return list of RemoteReading"""
    logger.debug("get_remote_readings called")
    try:
        token = fetch_glucose.get_token()
        logger.debug(f"Retrieved token: {token[:8]}... (truncated)")
        # fetch raw readings
        readings = fetch_glucose.fetch_glucose_readings(token)
        logger.debug(f"Raw remote readings response: {readings}")
        logger.info(f"Successfully fetched {len(readings)} remote readings")
        return readings
    except Exception as e:
        logger.exception("Error in get_remote_readings")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{reading_id}", response_model=schemas.GlucoseReading)
def get_glucose_reading(reading_id: int, db: Session = Depends(get_db)):
    """Get a specific glucose reading by ID"""
    db_reading = db.query(models.GlucoseReading).filter(models.GlucoseReading.id == reading_id).first()
    if db_reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    return db_reading

@router.delete("/{reading_id}")
def delete_glucose_reading(reading_id: int, db: Session = Depends(get_db)):
    """Delete a glucose reading"""
    db_reading = db.query(models.GlucoseReading).filter(models.GlucoseReading.id == reading_id).first()
    if db_reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    db.delete(db_reading)
    db.commit()
    return {"message": "Reading deleted successfully"}
