from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GlucoseReadingBase(BaseModel):
    level: float = Field(..., description="Blood glucose level in mg/dL", gt=0)
    notes: Optional[str] = Field(None, description="Optional notes about the reading")

class GlucoseReadingCreate(GlucoseReadingBase):
    pass

class GlucoseReading(GlucoseReadingBase):
    id: int
    timestamp: datetime
    
    class Config:
        orm_mode = True

class RemoteReading(BaseModel):
    """Remote glucose reading with value and epoch timestamp."""
    value: float = Field(..., description="Glucose value")
    timestamp: int = Field(..., description="Epoch timestamp in seconds")