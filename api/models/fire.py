from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime
from .geo import Geography
from .weather import Meteorology

class Incendio(BaseModel):
    id: int
    lat: float
    lon: float
    humidity: int
    windSpeed: float
    windDirection: int
    temperature: float
    slope: float
    vplFactor: float
    timestamp: datetime
    rodalValue: int
    fuelModel: str
    cityDistanceMeters: float
    builtLineLength: float
    incompatibilities: List[str]

    def update_from_geography(self, geo: Geography):
        self.slope = geo.slope
        self.vplFactor = geo.vplFactor
        self.fuelModel = geo.fuelModel
        self.cityDistanceMeters = geo.nearest_populated_area[1]
        self.rodalValue = geo.rodalValue
    
    def update_from_meteorology(self, meteo: Meteorology):
        self.humidity = meteo.humidity
        self.windSpeed = meteo.velocity
        self.windDirection = meteo.direction
        self.temperature = meteo.temperature
