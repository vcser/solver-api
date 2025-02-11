from fastapi import FastAPI
from api.endpoints import geography, prediction
from api.config import settings

app = FastAPI(
    title="Fire Prediction API",
    version="1.0.0",
    description="API for wildfire prediction and analysis"
)

# Include routers
# app.include_router(geography.router)
app.include_router(prediction.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)