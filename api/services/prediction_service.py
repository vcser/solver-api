import asyncio
import json
import uuid
import os
from fastapi import HTTPException
from api.models.solver import SolverInputData, SolverOutputData
from api.services.geography_service import GeographyService, FUEL_MODEL_MAPPING
from api.services.meteorology_service import MeteorologyService
from api.services.firebase_service import FirebaseService
from api.models.data import RequestData
from api.models.fire import Fire
from api.models.resource import Resource, CostoRecurso
from api.config import settings
import logging

logger = logging.getLogger(__name__)


class PredictionService:
    @classmethod
    async def run_prediction(cls, validated_data: RequestData):
        return await asyncio.create_task(cls._run_prediction_task(validated_data))

    @classmethod
    async def _run_prediction_task(cls, validated_data: RequestData):
        try:
            # Crear nombres de archivo únicos para cada request
            request_id = str(uuid.uuid4())
            # input_path = settings.BIN_PATH / f"input_{request_id}.json"
            # output_path = settings.BIN_PATH / f"output_{request_id}.json"

            logger.info(f"Running prediction for request {request_id}")

            # Obtener los datos de entrada para el solver
            solver_input_data = await cls.get_solver_input_data(validated_data)

            # Guardar la entrada en un archivo
            # with open(input_path, "w") as f:
            #     json.dump(solver_input_data.model_dump(), f)

            # Ejecutar el solver
            proc = await asyncio.create_subprocess_exec(
                "./solver",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=settings.BIN_PATH
            )

            stdout, stderr = await proc.communicate(input=json.dumps(solver_input_data.model_dump()).encode())

            # stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                raise HTTPException(500, detail=stderr.decode())

            # Leer el archivo de salida
            # with open(output_path) as f:
            #     result = json.load(f)

            result = json.loads(stdout)

            # Eliminar los archivos temporales
            # os.remove(input_path)
            # os.remove(output_path)

            output_data = SolverOutputData(**result)
            return output_data

        except Exception as e:
            raise HTTPException(500, detail=str(e))

    @classmethod
    async def get_fire_data(cls, data: RequestData) -> list[Fire]:
        # 1. Obtener información geográfica
        geography_data, meteorology_data = await asyncio.gather(
            GeographyService().get_geography(data),
            MeteorologyService.fetch_meteorology(data)
        )

        # 3. Crear lista de incendios
        fires = []
        for i, fire in enumerate(data.fires):
            fire_data = {
                "id": fire.id,
                "lat": fire.lat,
                "lon": fire.lon,
                "timestamp": fire.timestamp.isoformat(),
                "incompatibilities": fire.incompatibilities,
                **geography_data[i].model_dump(),
                **meteorology_data[i].model_dump()
            }
            fire_model = Fire(**fire_data)
            fires.append(fire_model)

        return fires

    @classmethod
    async def get_solver_input_data(cls, data: RequestData):
        # 1. Obtener lista de incendios
        fires = await cls.get_fire_data(data)

        # 2. Obtener lista de recursos
        resources = FirebaseService("recursos").get_all_documents()
        resources = [Resource(id=r["name"], type=r["type"], lat=r["lat"], lon=r["long"], state=r["state"],
                             workedHours=r["hours"], assignedFire=r["assigned"]) for r in resources if r["state"]]

        # 2.1. Obtener ETAs
        ETAs = await GeographyService.get_ETAs(data.timestamp, resources, fires)

        # 2.2. Asignar ETAs a los recursos
        for i, resource in enumerate(resources):
            resource.fireETAs = ETAs[i]

        # 3. Obtener matriz de rendimiento
        performanceMatrix = [None] * 31
        performances = FirebaseService(
            "rendimientos_combustibles").get_document("rendimientos")
        reverse_mapping = {v: k for k, v in FUEL_MODEL_MAPPING.items()}
        for key, value in performances.items():
            performanceMatrix[reverse_mapping[key]-1] = value

        # 4. Obtener matriz de costos
        costs = FirebaseService("costos").get_all_documents()
        costs = {c["id"].replace(" ", ""): CostoRecurso(
            transportUSD=c["transporte"], hourUSD=c["uso"]) for c in costs}

        solver_input_data = {
            "timestamp": data.timestamp.isoformat(),
            "fires": fires,
            "resources": resources,
            "performanceMatrix": performanceMatrix,
            "resourceCosts": costs
        }

        return SolverInputData(**solver_input_data)
