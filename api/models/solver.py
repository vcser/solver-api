from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
from .fire import Incendio
from .resource import Recurso, CostoRecurso
from .geo import Geography
from .weather import Meteorology

class SolverOutputData(BaseModel):
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
        metrics: "SolverOutputData.Metrics"
        resources: List["SolverOutputData.RecommendedResource"]

    fires: List[Recommendation]
    notUsed: List[str]


class SolverInputData(BaseModel):
    from .data import RequestData
    timestamp: datetime
    fires: List[Incendio]
    resources: List[Recurso]
    performanceMatrix: List[List[float]]
    resourceCosts: Dict[str, CostoRecurso]

    def __init__(self, data: RequestData):
        self.timestamp = data.timestamp
        self.fires = [Incendio(fire) for fire in data.fires]
        self.resources = []
        self.performanceMatrix = []
        self.resourceCosts = {}

    def update_geo_data(self, geo_data: List[Geography]):
        for fire in self.fires:
            for geo in geo_data:
                if fire.lat == geo.coordinates.lat and fire.lon == geo.coordinates.lon:
                    fire.update_from_geography(geo)
                    break

    def update_weather_data(self, weather_data: List[Meteorology]):
        for fire in self.fires:
            for weather in weather_data:
                if fire.timestamp == weather.timestamp:
                    fire.update_from_meteorology(weather)
                    break

    def update_resource_data(self, resource_data: List[Recurso]):
        self.resources = resource_data

    def update_performance_data(self, performance_data: List[List[float]]):
        self.performanceMatrix = performance_data

    def update_cost_data(self, cost_data: Dict[str, CostoRecurso]):
        self.resourceCosts = cost_data
