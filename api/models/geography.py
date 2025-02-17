from pydantic import BaseModel, Field


class Geography(BaseModel):
    # lat: float = Field(ge=-90, le=90)
    # lon: float = Field(ge=-180, le=180)
    slope: float
    fuelModel: str
    vplFactor: float
    cityDistanceMeters: float
    rodalValue: int = 3337
