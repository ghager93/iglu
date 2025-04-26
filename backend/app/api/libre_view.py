from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated, List, Optional

from app.db.database import get_db
from app.models import glucose_reading as models
from app.schemas import glucose_reading as schemas
from app.schemas.glucose_reading import RemoteReading
import fetch_glucose
from loguru import logger
from sqlalchemy.dialects.sqlite import insert as sqlite_insert


router = APIRouter(
    prefix="/libre-view",
    tags=["libre-view"],
)


@router.get("/", response_model=List[RemoteReading])
async def get_libre_view_readings(db: AsyncSession = Depends(get_db)):
    """Fetch glucose readings from remote API and return list of RemoteReading"""
    logger.debug("get_libre_view_readings called")
    try:
        token = await fetch_glucose.get_token()
        logger.debug(f"Retrieved token: {token[:8]}... (truncated)")
        readings = await fetch_glucose.fetch_glucose_readings(token)
        return readings
    except Exception as e:
        logger.exception("Error in get_libre_view_readings")
        raise HTTPException(status_code=500, detail=str(e))