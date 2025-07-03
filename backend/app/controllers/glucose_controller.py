from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.glucose_reading import GlucoseReadingCreate, RemoteReading, GlucoseReading as GlucoseReadingSchema
from app.services.glucose_service import (
    get_glucose_readings as svc_get_readings,
    create_glucose_reading as svc_create,
    create_bulk_readings as svc_create_bulk,
    delete_glucose_readings as svc_delete_readings,
    export_glucose_readings as svc_export,
    get_latest_glucose_reading as svc_get_latest,
    fetch_and_save_remote as svc_fetch_remote
)

async def list_readings(
    session: AsyncSession,
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    order: Optional[str] = "asc"
) -> List[GlucoseReadingSchema]:
    return await svc_get_readings(session, from_ts, to_ts, skip, limit, order)

async def bulk_create_readings(
    session: AsyncSession,
    readings: List[GlucoseReadingCreate],
    format: str = "json"
) -> List[GlucoseReadingSchema]:
    return await svc_create_bulk(session, readings, format)

async def remove_readings(
    session: AsyncSession,
    ids: Optional[List[int]] = None,
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None
) -> List[GlucoseReadingSchema]:
    return await svc_delete_readings(session, ids, from_ts, to_ts)

async def export_readings(
    session: AsyncSession,
    format: str = "json",
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
):
    return await svc_export(session, format, from_ts, to_ts, skip, limit)

async def get_latest_reading(
    session: AsyncSession
) -> GlucoseReadingSchema:
    reading = await svc_get_latest(session)
    if reading is None:
        raise HTTPException(status_code=404, detail="No readings found")
    return reading

async def fetch_remote_readings(
    session: AsyncSession
) -> List[RemoteReading]:
    return await svc_fetch_remote(session)

async def get_reading_by_id(
    session: AsyncSession,
    reading_id: int
) -> GlucoseReadingSchema:
    readings = await svc_get_readings(session)
    reading = next((r for r in readings if r.id == reading_id), None)
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    return reading

async def delete_reading_by_id(
    session: AsyncSession,
    reading_id: int
) -> dict:
    await svc_delete_readings(session, [reading_id])
    return {"message": "Reading deleted successfully"}
