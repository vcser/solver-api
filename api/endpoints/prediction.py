from fastapi import APIRouter, Request
from api.endpoints.utils import validate_input
from api.models.data import RequestData
from api.models.solver import SolverOutputData
from api.services.prediction_service import PredictionService

router = APIRouter(prefix="/prediction", tags=["Prediction"])

@router.post("/")
@validate_input(RequestData)
async def predict_simulation(request: Request, validated_data: RequestData) -> SolverOutputData:
    return await PredictionService.run_prediction(validated_data)
