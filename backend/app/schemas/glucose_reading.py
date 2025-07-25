from pydantic import BaseModel, Field


class GlucoseReadingBase(BaseModel):
    value: float = Field(..., description="Blood glucose level in mmol/L", gt=0)
    timestamp: int = Field(..., description="Timestamp of the reading in seconds since epoch")

class GlucoseReadingCreate(GlucoseReadingBase):
    pass

class GlucoseReading(GlucoseReadingBase):
    id: int
    
    class Config:
        orm_mode = True

class RemoteReading(BaseModel):
    """Remote glucose reading with value and epoch timestamp."""
    value: float = Field(..., description="Glucose value")
    timestamp: int = Field(..., description="Epoch timestamp in seconds")
    
class GlucoseReadingResponse(GlucoseReadingBase):
    ...