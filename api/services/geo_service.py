import rasterio
import shapefile
from shapely.geometry import Point, shape
from pyproj import Transformer
from geopy.distance import geodesic
from fastapi import HTTPException
import logging
from api.config import settings
from api.models.geo import Geography
from api.models.data import RequestDataPoint, RequestData
import asyncio

logger = logging.getLogger(__name__)

FUEL_MODEL_MAPPING = {
    0: "NC", 1: "PCH1", 2: "PCH2", 3: "PCH3", 4: "PCH4", 5: "PCH5",
    6: "MT01", 7: "MT02", 8: "MT03", 9: "MT04", 10: "MT05", 11: "MT06",
    12: "MT07", 13: "MT08", 14: "BN01", 15: "BN02", 16: "BN03", 17: "BN04",
    18: "BN05", 19: "PL01", 20: "PL02", 21: "PL03", 22: "PL04", 23: "PL05",
    24: "PL06", 25: "PL07", 26: "PL08", 27: "PL09", 28: "PL10", 29: "PL11",
    30: "DX01", 31: "DX02", 999: "NC"
}

VPL_FACTOR_MAPPING = {
    "PCH1": 0.01888, "PCH2": 0.016027, "PCH3": 0.010235,
    "PCH4": 0.00869, "PCH5": 0.001009, "MT01": 0.007603,
    "MT02": 0.008147, "MT03": 0.001672, "MT04": 0.004886,
    "MT05": 0.010321, "MT06": 0.009234, "MT07": 0.001787,
    "MT08": 0.004342, "BN01": 0.002249, "BN02": 0.001441,
    "BN03": 0.000979, "BN04": 0.001556, "BN05": 0.002365,
    "PL01": 0.013174, "PL02": 0.005973, "PL03": 0.002481,
    "PL04": 0.002712, "PL05": 0.006516, "PL06": 0.003255,
    "PL07": 0.002596, "PL08": 0.009777, "PL09": 0.005429,
    "PL10": 0.003799, "PL11": 0.001325, "DX01": 0.002134,
    "DX02": 0.001903,
}


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
                transformer = Transformer.from_crs(
                    *settings.CRS_TRANSFORMATIONS["default"])

                for record, shp in zip(sf.records(), sf.shapes()):
                    polygon = shape(shp)
                    lon, lat = transformer.transform(
                        shp.points[0][0], shp.points[0][1])
                    features.append({
                        "name": record[1],
                        "coordinates": (lat, lon),
                        "geometry": polygon
                    })

                self._shapefiles[name] = features
                logger.info(f"Loaded shapefile: {name}")
            except Exception as e:
                logger.error(f"Error loading shapefile {name}: {str(e)}")
                raise HTTPException(
                    500, detail=f"Error loading shapefile {name}")

    async def get_raster_value(self, raster_name: str, point: RequestDataPoint):
        try:
            src = self._rasters[raster_name]
            transformer = Transformer.from_crs(
                "EPSG:4326", src.crs, always_xy=True)
            x, y = transformer.transform(point.lon, point.lat)
            row, col = src.index(x, y)
            return src.read(1)[row, col]
        except Exception as e:
            logger.error(f"Raster error: {str(e)}")
            raise HTTPException(500, detail="Error processing raster data")

    async def nearest_feature(self, shapefile_name: str, point: RequestDataPoint):
        try:
            features = self._shapefiles[shapefile_name]
            user_point = Point(point.lon, point.lat)

            for feature in features:
                if feature["geometry"].contains(user_point):
                    return {"name": feature["name"], "distance": 0}

            closest = min(features, key=lambda f: geodesic(
                (point.lat, point.lon), f["coordinates"]).meters)
            distance = geodesic((point.lat, point.lon),
                                closest["coordinates"]).meters
            return {"name": closest["name"], "distance": distance}
        except Exception as e:
            logger.error(f"Shapefile error: {str(e)}")
            raise HTTPException(500, detail="Error processing spatial data")

    async def get_point_geography(self, point: RequestDataPoint) -> Geography:
        try:
            # Ejecutar operaciones en paralelo
            slope, fuel_value = await asyncio.gather(
                self.get_raster_value("slope", point),
                self.get_raster_value("fuel_model", point)
            )

            # Obtener el modelo de combustible
            fuel_model = FUEL_MODEL_MAPPING.get(int(fuel_value), "Unknown")

            # Obtener el área poblada más cercana
            populated_area = await self.nearest_feature("cities", point)

            return Geography(
                lat=point.lat,
                lon=point.lon,
                slope=float(slope),
                fuelModel=fuel_model,
                vplFactor=VPL_FACTOR_MAPPING.get(fuel_model, 0.0),
                nearest_populated_area=populated_area
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing geography data: {str(e)}"
            )

    async def get_geography(self, data: RequestData) -> list[Geography]:
        return await asyncio.gather(
            *[self.get_point_geography(fire) for fire in data.fires]
        )
