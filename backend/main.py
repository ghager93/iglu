from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import glucose_readings

app = FastAPI(
    title="Diabetes Management API",
    description="API for managing diabetes-related data",
    version="0.1.0"
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