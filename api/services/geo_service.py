import rasterio
import shapefile
from shapely.geometry import Point, shape
from pyproj import Transformer
from geopy.distance import geodesic
from fastapi import HTTPException
import logging
from api.config import settings
from api.models.geo import GeoPoint

logger = logging.getLogger(__name__)

class GeoService:
    _instance = None
    _rasters = {}
    _shapefiles = {}

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._load_rasters()
            cls._instance._load_shapefiles()
        return cls._instance

    def _load_rasters(self):
        for name, path in settings.RASTER_PATHS.items():
            try:
                self._rasters[name] = rasterio.open(path)
                logger.info(f"Loaded raster: {name}")
            except Exception as e:
                logger.error(f"Error loading raster {name}: {str(e)}")
                raise HTTPException(500, detail=f"Error loading raster {name}")

    def _load_shapefiles(self):
        for name, path in settings.SHAPEFILE_PATHS.items():
            try:
                sf = shapefile.Reader(path)
                features = []
                transformer = Transformer.from_crs(*settings.CRS_TRANSFORMATIONS["default"])
                
                for record, shp in zip(sf.records(), sf.shapes()):
                    polygon = shape(shp)
                    lon, lat = transformer.transform(shp.points[0][0], shp.points[0][1])
                    features.append({
                        "name": record[1],
                        "coordinates": (lat, lon),
                        "geometry": polygon
                    })
                
                self._shapefiles[name] = features
                logger.info(f"Loaded shapefile: {name}")
            except Exception as e:
                logger.error(f"Error loading shapefile {name}: {str(e)}")
                raise HTTPException(500, detail=f"Error loading shapefile {name}")

    async def get_raster_value(self, raster_name: str, point: GeoPoint):
        try:
            src = self._rasters[raster_name]
            transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
            x, y = transformer.transform(point.lon, point.lat)
            row, col = src.index(x, y)
            return src.read(1)[row, col]
        except Exception as e:
            logger.error(f"Raster error: {str(e)}")
            raise HTTPException(500, detail="Error processing raster data")

    async def nearest_feature(self, shapefile_name: str, point: GeoPoint):
        try:
            features = self._shapefiles[shapefile_name]
            user_point = Point(point.lon, point.lat)
            
            for feature in features:
                if feature["geometry"].contains(user_point):
                    return {"name": feature["name"], "distance": 0}
            
            closest = min(features, key=lambda f: geodesic(
                (point.lat, point.lon), f["coordinates"]).meters)
            distance = geodesic((point.lat, point.lon), closest["coordinates"]).meters
            return {"name": closest["name"], "distance": distance}
        except Exception as e:
            logger.error(f"Shapefile error: {str(e)}")
            raise HTTPException(500, detail="Error processing spatial data")