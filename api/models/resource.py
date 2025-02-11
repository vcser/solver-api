from pydantic import BaseModel
from typing import List
from datetime import datetime

class Recurso(BaseModel):
    id: str
    type: str
    workedHours: float
    lat: float
    lon: float
    state: int
    isGrouped: bool
    assignedFire: int
    fireETAs: List[datetime]
    incompatibilities: List[str]

class CostoRecurso(BaseModel):
    transportUSD: float
    hourUSD: float