from sqlalchemy import Column, Integer, Float, DateTime, String
from sqlalchemy.sql import func
from app.db.database import Base

class GlucoseReading(Base):
    __tablename__ = "glucose_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(Integer, server_default=func.now(), unique=True, index=True)
    