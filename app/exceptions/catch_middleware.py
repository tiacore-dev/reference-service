import traceback
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class CatchAllExceptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            if response.status_code == 400:
                body = await request.body()
                logger.error("🚨 400 Bad Request от FastAPI")
                logger.error(f"➡️ URL: {request.url}")
                logger.error(f"➡️ Headers: {dict(request.headers)}")
                logger.error(
                    f"➡️ Body: {body.decode('utf-8', errors='ignore')}")
            return response
        except Exception as e:
            tb = traceback.format_exc()
            logger.critical("🔥 Исключение в middleware!")
            logger.critical(f"{e}\n{tb}")
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
