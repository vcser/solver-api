from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import subprocess
import json
import traceback
from starlette.middleware.cors import CORSMiddleware
import shapefile
from geopy.distance import geodesic
import rasterio
from rasterio.enums import Resampling
from pyproj import Transformer
from shapely.geometry import Point, shape

# Configuración inicial de FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constantes y mapeos
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

# Modelos Pydantic
class Incendio(BaseModel):
    latitud: float
    longitud: float
    humedad_relativa: float
    velocidad_viento: float
    direccion_viento: float
    temperatura: float
    pendiente: float
    factor_vpl: float
    timestamp_inicio: datetime
    valor_rodal_usd: float
    modelo_combustible: str
    distancia_ciudad: float
    metros_construidos: float

class Recurso(BaseModel):
    id: str
    tipo: str
    horas_trabajo: float
    latitud: float
    longitud: float
    id_estado: int
    id_asignacion: Optional[int] = None
    agrupado: int
    timestamps_eta: List[datetime]

class Rendimiento(BaseModel):
    modelo_combustible: str
    tipo_recurso: str
    rendimiento: float

class Costo(BaseModel):
    tipo_recurso: str
    costo_usd_hr: float

class Factibilidad(BaseModel):
    tipo_recurso: str
    num_incendio: int
    disponible: int

class DatosEntrada(BaseModel):
    timestamp: datetime
    num_incendios: int
    incendios: List[Incendio]
    num_recursos: int
    recursos: List[Recurso]
    rendimientos: List[Rendimiento]
    costos: List[Costo]
    factibilidad: List[Factibilidad]

# Helpers geoespaciales
def read_raster_value(file_path: str, lat: float, lon: float):
    """Lee un valor de un archivo raster en las coordenadas especificadas."""
    try:
        with rasterio.open(file_path) as src:
            transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
            x, y = transformer.transform(lon, lat)
            row, col = src.index(x, y)
            return src.read(1)[row, col]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading raster: {str(e)}")

def load_shapefile(file_path: str, crs_from: str = "EPSG:32718"):
    """Carga un shapefile y devuelve sus características con geometría transformada."""
    try:
        sf = shapefile.Reader(file_path)
        transformer = Transformer.from_crs(crs_from, "EPSG:4326", always_xy=True)
        
        features = []
        for record, shp in zip(sf.records(), sf.shapes()):
            polygon = shape(shp)
            lon, lat = transformer.transform(shp.points[0][0], shp.points[0][1])
            features.append({
                "name": record[1],
                "coordinates": (lat, lon),
                "geometry": polygon
            })
        return features
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading shapefile: {str(e)}")

def find_nearest_feature(lat: float, lon: float, features: list, feature_type: str):
    """Encuentra la característica más cercana a las coordenadas dadas."""
    try:
        user_point = Point(lon, lat)
        for feature in features:
            if feature["geometry"].contains(user_point):
                return {"name": feature["name"], "distance_meters": 0}
        
        closest = min(features, key=lambda f: geodesic((lat, lon), f["coordinates"]).meters)
        distance = geodesic((lat, lon), closest["coordinates"]).meters
        return {"name": closest["name"], "distance_meters": distance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding {feature_type}: {str(e)}")

# Endpoints principales
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de predicción"}

@app.post("/predict")
async def predict(request: Request):
    try:
        data = await request.body()
        result = subprocess.run(
            ["./solver", "-o", "output.json"],
            input=data.decode("utf-8"),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise HTTPException(500, detail=result.stderr)
            
        with open("output.json") as f:
            return json.load(f)
            
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, detail=str(e))

@app.get("/geography")
def get_geography(lat: float, lon: float):
    try:
        # Obtener pendiente
        slope = read_raster_value("data/Pendiente.tif", lat, lon)
        
        # Obtener modelo de combustible
        fuel_value = read_raster_value("data/Mod_combustible.tif", lat, lon)
        fuel_model = FUEL_MODEL_MAPPING.get(int(fuel_value), "Unknown")
        vpl_factor = VPL_FACTOR_MAPPING.get(fuel_model, 0)
        
        # Obtener área poblada más cercana
        areas = load_shapefile("data/Ciudades.shp")
        populated_area = find_nearest_feature(lat, lon, areas, "populated area")
        
        return {
            "latitude": lat,
            "longitude": lon,
            "slope": float(slope),
            "fuel_model": fuel_model,
            "vpl_factor": vpl_factor,
            "populated_area": populated_area["name"],
            "distance_meters": populated_area["distance_meters"]
        }
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# Endpoints adicionales para características individuales
@app.get("/nearest-station")
def get_nearest_station(lat: float, lon: float):
    stations = load_shapefile("data/PUNTOS_METFOR.shp", "EPSG:4326")
    return find_nearest_feature(lat, lon, stations, "weather station")

@app.get("/slope")
def get_slope(lat: float, lon: float):
    return {"slope": read_raster_value("data/Pendiente.tif", lat, lon)}

@app.get("/fuel-model")
def get_fuel_model(lat: float, lon: float):
    fuel_value = read_raster_value("data/Mod_combustible.tif", lat, lon)
    fuel_model = FUEL_MODEL_MAPPING.get(int(fuel_value), "Unknown")
    return {
        "fuel_model": fuel_model,
        "vpl_factor": VPL_FACTOR_MAPPING.get(fuel_model, 0)
    }