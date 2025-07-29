from pydantic import BaseModel, Field

class CurrentReading(BaseModel):
    """Current glucose reading with value and epoch timestamp."""
    value: float = Field(..., description="Glucose value")
    timestamp: int = Field(..., description="Epoch timestamp in seconds")