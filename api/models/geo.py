from pydantic import BaseModel, Field, field_validator

# class GeoPoint(BaseModel):
#     lat: float = Field(ge=-90, le=90)
#     lon: float = Field(ge=-180, le=180)

#     @field_validator('lat', 'lon', mode='before')
#     @classmethod
#     def round_coordinates(cls, v):
#         return round(v, 6)

class Geography(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    slope: float
    fuelModel: str
    vplFactor: float
    nearest_populated_area: tuple[str, float]
    rodalValue: int = 3337
