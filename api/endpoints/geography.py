from fastapi import APIRouter, HTTPException
from api.models.geo import GeoPoint, Geography
from api.services.geo_service import GeoService
import asyncio

router = APIRouter(prefix="/geography", tags=["Geography"])

# Definir los mapeos aquí
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

# @router.get("/", response_model=GeoResponse)
async def get_geography(point: GeoPoint) -> Geography:
    geo = GeoService()
    try:
        # Ejecutar operaciones en paralelo
        slope, fuel_value = await asyncio.gather(
            geo.get_raster_value("slope", point),
            geo.get_raster_value("fuel_model", point)
        )
        
        # Obtener el modelo de combustible
        fuel_model = FUEL_MODEL_MAPPING.get(int(fuel_value), "Unknown")
        
        # Obtener el área poblada más cercana
        populated_area = await geo.nearest_feature("cities", point)
        
        return Geography(
            coordinates=point,
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