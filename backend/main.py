from contextlib import asynccontextmanager
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.api import glucose_readings
import asyncio
from app.db.database import SessionLocal
from app.api.glucose_readings import fetch_and_save_remote_readings
from loguru import logger
from app.db.sse_queue import sse_queue
from app.repositories.glucose_repository import upsert_readings
from app.models.glucose_reading import GlucoseReading
import fetch_glucose


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Launch background task to fetch and save remote readings every minute"""
    async def fetch_loop():
        while True:
            try:
                async with SessionLocal() as db:
                    # await fetch_and_save_remote_readings(db)
                    
                    token = await fetch_glucose.get_token()
                    readings = await fetch_glucose.fetch_glucose_readings(token)
                    data = [dict(value=r["value"], timestamp=r["timestamp"]) for r in readings]
                    
                    stmt = select(GlucoseReading).where(
                        GlucoseReading.timestamp >= data[0]["timestamp"],
                    )
                    result = await db.execute(stmt)
                    db_data = [(r.value, r.timestamp) for r in result.scalars().all()]
                    db_data = sorted(db_data, key=lambda x: x[1])
                    new_data = list({"value": e[0], "timestamp": e[1]} for e in set((r["value"], r["timestamp"]) for r in data) - set(db_data))      
                    if new_data:
                        await sse_queue.put(json.dumps(new_data))
                    if data:
                        await upsert_readings(db, data)
                    logger.info(f"Service: fetched and saved {len(readings)} remote readings")
            except Exception:
                logger.exception("Error in scheduled fetch_and_save_remote_readings")
            await asyncio.sleep(60)
    fetch_loop_task = asyncio.ensure_future(fetch_loop())
    yield
    # Cleanup code can be added here if needed
    fetch_loop_task.cancel()
    
    
app = FastAPI(
    title="Diabetes Management API",
    description="API for managing diabetes-related data",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(glucose_readings.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Welcome to the Diabetes Management API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)