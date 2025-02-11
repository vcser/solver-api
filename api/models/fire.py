from typing import Optional
from .geo import Geography
from .weather import Meteorology
from .data import RequestDataPoint

class Incendio(RequestDataPoint, Geography, Meteorology):
    # id: int
    # lat: float
    # lon: float
    # humidity: int
    # windSpeed: float
    # windDirection: int
    # temperature: float
    # slope: float
    # vplFactor: float
    # timestamp: datetime
    # rodalValue: int
    # fuelModel: str
    # cityDistanceMeters: float
    builtLineLength: Optional[float] = 0
    # incompatibilities: List[str]

    def __init__(self, point: RequestDataPoint):
        self.id = point.id
        self.lat = point.lat
        self.lon = point.lon
        self.timestamp = point.timestamp
        self.incompatibilities = point.incompatibilities

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
