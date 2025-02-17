from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent
    CREDS_PATH: Path = ROOT_DIR / "creds.json"
    BIN_PATH: Path = ROOT_DIR / "bin"
    RASTER_PATHS: dict = {
        "slope": ROOT_DIR / "data/Pendiente.tif",
        "fuel_model": ROOT_DIR / "data/Mod_combustible.tif"
    }
    SHAPEFILE_PATHS: dict = {
        "stations": ROOT_DIR / "data/PUNTOS_METFOR.shp",
        "cities": ROOT_DIR / "data/Ciudades.shp"
    }
    CRS_TRANSFORMATIONS: dict = {
        "default": ("EPSG:32718", "EPSG:4326")
    }

settings = Settings()