from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class RequestDataPoint(BaseModel):
    id: int
    lat: float
    lon: float
    timestamp: datetime
    incompatibilities: Optional[List[str]] = []


class RequestData(BaseModel):
    timestamp: datetime
    fires: List[RequestDataPoint]
