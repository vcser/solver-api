from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from .fire import Fire
from .resource import Resource, CostoRecurso
from .geography import Geography
from .meteorology import Meteorology
from .data import RequestData


class Metrics(BaseModel):
    area: float
    damage: float
    extinguishedTime: float
    perimeter: float
    savedDamage: float


class RecommendedResource(BaseModel):
    cost: float
    id: str
    line: float


class Recommendation(BaseModel):
    id: int
    metrics: Metrics
    resources: List[RecommendedResource] = []


class SolverOutputData(BaseModel):
    fires: List[Recommendation]
    notUsed: List[str]


class SolverInputData(BaseModel):
    timestamp: str
    fires: List[Fire] = []
    resources: List[Resource] = []
    performanceMatrix: List[List[float]] = []
    resourceCosts: Dict[str, CostoRecurso] = {}
