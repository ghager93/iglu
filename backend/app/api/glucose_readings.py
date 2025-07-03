import json
from typing import Annotated, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from fastapi.responses import Response, StreamingResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.glucose_controller import (
    bulk_create_readings,
    delete_reading_by_id,
    export_readings,
    fetch_remote_readings,
    get_latest_reading,
    get_reading_by_id,
    list_readings,
    remove_readings,
)
from app.db.database import get_db
from app.db.sse_queue import sse_queue
from app.schemas import glucose_reading as schemas
from app.schemas.glucose_reading import RemoteReading

router = APIRouter(
    prefix="/glucose-readings",
    tags=["glucose-readings"],
)

@router.get("/", response_model=List[schemas.GlucoseReading])
async def get_glucose_readings(
    from_ts: Optional[int] = Query(None, alias="from", description="Epoch start timestamp (inclusive)"),
    to_ts: Optional[int] = Query(None, alias="to", description="Epoch end timestamp (inclusive)"),
    skip: Optional[int] = Query(0, description="Skip the first n readings"),
    limit: Optional[int] = Query(100, description="Limit the number of readings to return"),
    order: Optional[str] = Query("asc", description="Order of readings (asc or desc)"),
    db: AsyncSession = Depends(get_db)
):
    """Get glucose readings from DB, optionally filtering by from/to epoch timestamps"""
    return await list_readings(db, from_ts, to_ts, skip, limit, order)

@router.put("/", response_model=list[schemas.GlucoseReading])
async def create_glucose_readings(
    readings: Annotated[list[schemas.GlucoseReadingCreate], Body(embed=True)],
    db: AsyncSession = Depends(get_db)
):
    """Create new glucose readings"""
    return await bulk_create_readings(db, readings)

@router.delete("/", response_model=list[schemas.GlucoseReading])
async def delete_glucose_readings(
    ids: Optional[list[str]] = Query(None, description="List of glucose reading IDs to delete"),
    from_ts: Optional[int] = Query(None, alias="from", description="Epoch start timestamp (inclusive)"),
    to_ts: Optional[int] = Query(None, alias="to", description="Epoch end timestamp (inclusive)"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Delete glucose readings from DB, optionally filtering by from/to epoch timestamps"""
    return await remove_readings(db, ids, from_ts, to_ts)

@router.get("/export")
async def export_glucose_readings(
    from_ts: Optional[int] = Query(None, alias="from", description="Epoch start timestamp (inclusive)"),
    to_ts: Optional[int] = Query(None, alias="to", description="Epoch end timestamp (inclusive)"),
    format: str = Query("json", description="Export format (json, csv, html)"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Export readings in bulk. Can be exported in json, csv, or html format."""
    result = await export_readings(db, format, from_ts, to_ts, skip, limit)
    
    # Return appropriate response based on format
    if format == "html":
        return Response(content=result, media_type="text/html")
    elif format == "csv":
        return Response(content=result, media_type="text/csv")
    else:  # json format
        return result

@router.get("/latest", response_model=schemas.GlucoseReading)
async def get_latest_glucose_reading(db: AsyncSession = Depends(get_db)):
    """Get the latest glucose reading from the database"""
    reading = await get_latest_reading(db)
    if reading is None:
        raise HTTPException(status_code=404, detail="No readings found")
    return reading

async def fetch_and_save_remote_readings(db: AsyncSession) -> List[RemoteReading]:
    """Fetch remote glucose readings and upsert into the database via service"""
    return await fetch_remote_readings(db)

@router.post("/import", response_model=list[schemas.GlucoseReading])
async def import_glucose_readings(
    readings: Annotated[list[schemas.GlucoseReadingCreate], Body(embed=True)],
    format: Annotated[str, Body(embed=True)] = "json",
    db: AsyncSession = Depends(get_db)
):
    """Import glucose readings in bulk"""
    return await bulk_create_readings(db, readings, format)

@router.get("/stream")
async def stream_readings(
    request: Request,
):
    """Stream events from the server"""
    async def event_stream():
        while True:
            logger.debug("Waiting for new data...")
            if await request.is_disconnected():
                break
            
            data = await sse_queue.get()
            # send JSON-formatted data for easier client parsing
            yield f"data: {json.dumps(data)}\n\n"
        
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.get("/{reading_id}", response_model=schemas.GlucoseReading)
async def get_glucose_reading(reading_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific glucose reading by ID"""
    return await get_reading_by_id(db, reading_id)

@router.delete("/{reading_id}")
async def delete_glucose_reading(reading_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a glucose reading"""
    return await delete_reading_by_id(db, reading_id)