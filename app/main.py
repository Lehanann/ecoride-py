from pathlib import Path

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

import app.core.logging
from app.core.middlewares.auth_middleware import register_middlewares
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import (user_router,
                                  brand_router,
                                  car_router,
                                  carpooling_router,
                                  opinion_router,
                                  reservation_router,
                                  authentication_router,
                                  )

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_middlewares(app)
app.include_router(user_router)
app.include_router(brand_router)
app.include_router(car_router)
app.include_router(carpooling_router)
app.include_router(opinion_router)
app.include_router(reservation_router)
app.include_router(authentication_router)

BASE_DIR = Path(__file__).resolve().parent.parent
profiles_path = BASE_DIR / "storage" / "profiles"
app.mount("/profiles", StaticFiles(directory=profiles_path), name="profiles")

@app.get("/")
async def root():
    """
    Entrypoint ecoride backend fastapi

    Returns: Welcome message
    """
    return {"message": "Welcome API EcoRide!"}