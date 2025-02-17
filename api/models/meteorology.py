from pydantic import BaseModel

class Meteorology(BaseModel):
    temperature: float
    humidity: float
    windSpeed: float
    windDirection: float