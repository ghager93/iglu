from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.glucose_reading import GlucoseReading as GlucoseReadingModel
from app.schemas.glucose_reading import GlucoseReadingCreate, RemoteReading
from app.repositories.glucose_repository import (
    fetch_readings, fetch_latest, upsert_readings, delete_readings
)
import fetch_glucose
from loguru import logger

async def get_glucose_readings(
    session: AsyncSession,
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None,
    skip: int = 0,
    limit: Optional[int] = None
) -> List[GlucoseReadingModel]:
    return await fetch_readings(session, from_ts, to_ts, skip, limit)

async def create_glucose_reading(
    session: AsyncSession,
    reading: GlucoseReadingCreate
) -> GlucoseReadingModel:
    model = GlucoseReadingModel(value=reading.value, timestamp=reading.timestamp)
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model

async def create_bulk_readings(
    session: AsyncSession,
    readings: List[GlucoseReadingCreate],
    format: str = "json"
) -> List[GlucoseReadingModel]:
    data = [dict(value=r.value, timestamp=r.timestamp) for r in readings]
    await upsert_readings(session, data)
    # fetch and return updated entities
    return await fetch_readings(session)

async def fetch_and_save_remote(
    session: AsyncSession
) -> List[RemoteReading]:
    logger.debug("Service: fetching remote readings")
    token = await fetch_glucose.get_token()
    readings = await fetch_glucose.fetch_glucose_readings(token)
    data = [dict(value=r["value"], timestamp=r["timestamp"]) for r in readings]
    if data:
        await upsert_readings(session, data)
    logger.info(f"Service: fetched and saved {len(readings)} remote readings")
    return readings

async def delete_glucose_readings(
    session: AsyncSession,
    ids: Optional[List[int]] = None,
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None
) -> List[GlucoseReadingModel]:
    return await delete_readings(session, ids, from_ts, to_ts)

async def export_glucose_readings(
    session: AsyncSession,
    format: str = "json",
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None,
    skip: int = 0,
    limit: Optional[int] = None
):
    readings = await fetch_readings(session, from_ts, to_ts, skip, limit)
    if format == "json":
        return [r.__dict__ for r in readings]
    # CSV/HTML export logic to be implemented elsewhere
    raise ValueError("Unsupported format")

async def get_latest_glucose_reading(
    session: AsyncSession
) -> Optional[GlucoseReadingModel]:
    return await fetch_latest(session)
