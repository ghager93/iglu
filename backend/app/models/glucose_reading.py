from sqlalchemy import Column, Integer, Float, DateTime, String
from sqlalchemy.sql import func
from app.db.database import Base

class GlucoseReading(Base):
    __tablename__ = "glucose_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(String, nullable=True)
    
    # Additional fields could be added later:
    # user_id = Column(Integer, ForeignKey("users.id"))
    # meal_relation = Column(String) # e.g., "before_meal", "after_meal", "fasting"