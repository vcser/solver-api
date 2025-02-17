from pydantic import BaseModel
from typing import List
from datetime import datetime

class Resource(BaseModel):
    id: str
    type: str
    workedHours: float = 0.0
    lat: float
    lon: float
    state: int
    isGrouped: bool = True
    assignedFire: int = -1
    fireETAs: List[str] = []
    incompatibilities: List[str] = []

class CostoRecurso(BaseModel):
    transportUSD: float
    hourUSD: float