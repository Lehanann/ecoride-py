from fastapi import FastAPI
import app.core.logging
from app.core.middlewares.auth_middleware import register_middlewares
from app.api.v1.endpoints import (user_router,
                                  brand_router,
                                  car_router,
                                  carpooling_router,
                                  opinion_router,
                                  reservation_router
                                  )

app = FastAPI()

register_middlewares(app)
app.include_router(user_router)
app.include_router(brand_router)
app.include_router(car_router)
app.include_router(carpooling_router)
app.include_router(opinion_router)
app.include_router(reservation_router)

@app.get("/")
async def root():
    """
    Entrypoint ecoride backend fastapi

    Returns: Welcome message
    """
    return {"message": "Welcome API EcoRide!"}