import jwt
from fastapi import Request, FastAPI
from app.utils.auth_utils import decode_access_token

def register_middlewares(app: FastAPI):
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):

        request.state.user_id = None

        token = request.cookies.get("access_token")

        if token:
            try:

                payload = decode_access_token(token)

                request.state.user_id = int(payload.sub)

            except (ValueError, jwt.InvalidTokenError, jwt.ExpiredSignatureError):
                request.state.user_id = None

        return await call_next(request)
