from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    user_auth = request.headers.get("authorization")
    request.state.user_id = user_auth
    response = await call_next(request)
    return response