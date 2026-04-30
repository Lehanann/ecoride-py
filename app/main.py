from fastapi import FastAPI
from app.api.v1.endpoints import (user_router,
                                  brand_router
                                  )

app = FastAPI()
app.include_router(user_router)
app.include_router(brand_router)


@app.get("/")
async def root():
    """
    Entrypoint ecoride backend fastapi

    Returns: Welcome message
    """
    return {"message": "Welcome API EcoRide!"}