from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict
from .fire import Incendio
from .resource import Recurso, CostoRecurso
from .geo import GeoPoint, Geography
from .weather import Meteorology


class RequestData(BaseModel):
    class WildfirePointInput(GeoPoint):
        timestamp: datetime
        incompatibilities: List[str] = []
        builtLineLength: float = 0.0

    timestamp: datetime
    fires: List[WildfirePointInput]


class ResponseData(BaseModel):
    class FireMetrics(BaseModel):
        area: float
        damage: float
        extinguishedTime: float
        perimeter: float
        savedDamage: float

    class FireResource(BaseModel):
        cost: float
        id: str
        line: float

    class Fire(BaseModel):
        id: int
        metrics: "ResponseData.FireMetrics"
        resources: List["ResponseData.FireResource"]

    fires: List[Fire]
    notUsed: List[str]


class ModelInputData(BaseModel):
    timestamp: datetime
    fires: List[Incendio]
    resources: List[Recurso]
    performanceMatrix: List[List[float]]
    resourceCosts: Dict[str, CostoRecurso]

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

    def from_request_data(self, data: RequestData):
        self.timestamp = data.timestamp
        self.fires = [
            Incendio(
                id=i,
                lat=fire.lat,
                lon=fire.lon,
                humidity=0,
                windSpeed=0,
                windDirection=0,
                temperature=0,
                slope=0,
                vplFactor=0,
                timestamp=fire.timestamp,
                rodalValue=0,
                fuelModel="",
                cityDistanceMeters=0,
                builtLineLength=fire.builtLineLength,
                incompatibilities=fire.incompatibilities
            )
            for i, fire in enumerate(data.fires)
        ]
        self.resources = []
        self.performanceMatrix = []
        self.resourceCosts = {}
