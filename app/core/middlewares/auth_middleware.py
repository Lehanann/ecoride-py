from fastapi import Request, FastAPI

def register_middlewares(app: FastAPI):
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        token = request.headers.get("authorization")
        print("TOKEN:", token)
        if token and token.isdigit():
            request.state.user_id = int(token)
        else:
            request.state.user_id = None

        return await call_next(request)
