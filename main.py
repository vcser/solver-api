from fastapi import FastAPI, HTTPException, Security, status, Depends
from api.endpoints import prediction
from api.config import settings
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv
import os

load_dotenv()

# Configuración de la API key
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

app = FastAPI(
    title="Fire Prediction API",
    version="1.0.0",
    description="API for wildfire prediction and analysis"
)

# Dependency que verifica la API key
async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key no válida"
        )
    return api_key

# Se agrega la dependency de verificación a nivel del router.
app.include_router(prediction.router, dependencies=[Depends(verify_api_key)])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
