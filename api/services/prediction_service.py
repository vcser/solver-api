import asyncio
import json
import uuid
import os
from fastapi import HTTPException
from api.models.solver import SolverInputData
from api.services.geo_service import GeoService
from api.services.weather_service import WeatherService
from api.services.firebase_service import FirebaseService
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    @classmethod
    async def run_prediction(cls, validated_data):
        try:
            # Crear nombres de archivo únicos para cada request
            request_id = str(uuid.uuid4())
            input_path = f"input_{request_id}.json"
            output_path = f"output_{request_id}.json"

            logger.info(f"Running prediction for request {request_id}")

            input_data = SolverInputData.from_request_data(validated_data)

            # 1. Obtener información geográfica
            geo_data = await GeoService.get_geography(input_data)
            input_data.update_geo_data(geo_data)
            logger.debug(f"Updated input data with geo data: {geo_data}")

            # 2. Obtener información climática
            weather_data = await WeatherService.fetch_meteorology(input_data)
            input_data.update_weather_data(weather_data)
            logger.debug(f"Updated input data with weather data: {weather_data}")

            # # 3. Obtener datos de recursos desde Firebase
            # resource_data = FirebaseService("recursos").get_all_documents()
            # input_data.update_resource_data(resource_data)
            # logger.debug(f"Updated input data with resource data: {resource_data}")

            # # 4. Obtener matriz de rendimiento
            # performance_data = FirebaseService("rendimientos_combustibles").get_document("rendimientos")
            # input_data.update_performance_data(performance_data)
            # logger.debug(f"Updated input data with performance data: {performance_data}")

            # # 5. Obtener matriz de costos
            # cost_data = FirebaseService("costos").get_all_documents()
            # input_data.update_cost_data(cost_data)
            # logger.debug(f"Updated input data with cost data: {cost_data}")

            # Guardar la entrada en un archivo
            with open(input_path, "w") as f:
                json.dump(validated_data.model_dump(), f)

            # Ejecutar el solver
            proc = await asyncio.create_subprocess_exec(
                "./solver", "-i", input_path, "-o", output_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                raise HTTPException(500, detail=stderr.decode())

            # Leer el archivo de salida
            with open(output_path) as f:
                result = json.load(f)

            # Eliminar los archivos temporales
            os.remove(input_path)
            os.remove(output_path)

            return result

        except Exception as e:
            raise HTTPException(500, detail=str(e))
