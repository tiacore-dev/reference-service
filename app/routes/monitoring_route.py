from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

monitoring_router = APIRouter()


@monitoring_router.get("/metrics")
def monitoring():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
