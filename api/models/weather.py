from pydantic import BaseModel

class Meteorology(BaseModel):
    temperature: float
    humidity: float
    velocity: float
    direction: float