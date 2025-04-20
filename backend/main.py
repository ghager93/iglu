from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import glucose_readings
import asyncio
from app.db.database import SessionLocal
from app.api.glucose_readings import fetch_and_save_remote_readings
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Launch background task to fetch and save remote readings every minute"""
    async def fetch_loop():
        while True:
            try:
                async with SessionLocal() as db:
                    await fetch_and_save_remote_readings(db)
            except Exception:
                logger.exception("Error in scheduled fetch_and_save_remote_readings")
            await asyncio.sleep(60)
    # asyncio.create_task(fetch_loop())
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