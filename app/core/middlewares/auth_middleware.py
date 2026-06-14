from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    token = request.headers.get("authorization")
    request.state.user_id = token
    response = await call_next(request)
    return response