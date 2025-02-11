from pydantic import BaseModel

class Settings(BaseModel):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RASTER_PATHS: dict = {
        "slope": "data/Pendiente.tif",
        "fuel_model": "data/Mod_combustible.tif"
    }
    SHAPEFILE_PATHS: dict = {
        "stations": "data/PUNTOS_METFOR.shp",
        "cities": "data/Ciudades.shp"
    }
    CRS_TRANSFORMATIONS: dict = {
        "default": ("EPSG:4326", "EPSG:32718")
    }

settings = Settings()