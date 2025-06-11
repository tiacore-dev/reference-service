from fastapi import APIRouter, Depends
from loguru import logger
from tiacore_lib.handlers.auth_handler import get_current_user
from tiacore_lib.pydantic_models.entity_type_models import (
    FilterParams,
    LegalEntityTypeListResponse,
    LegalEntityTypeSchema,
)
from tortoise.expressions import Q

from app.database.models import LegalEntityType

entity_types_router = APIRouter()


@entity_types_router.get(
    "/all",
    response_model=LegalEntityTypeListResponse,
    summary="Получение списка типов юр. лиц с фильтрацией",
)
async def get_entity_types(
    filters: FilterParams = Depends(),
    _: str = Depends(get_current_user),
):
    logger.info(f"Запрос на список типов юр. лиц: {filters}")

    query = Q()

    if filters.entity_name:
        query &= Q(name__icontains=filters.entity_name)

    order = filters.order
    sort_by = filters.sort_by
    order_by = f"{'-' if order == 'desc' else ''}{sort_by}"

    page = filters.page
    page_size = filters.page_size

    total_count = await LegalEntityType.filter(query).count()

    entity_types = [
        LegalEntityTypeSchema(**p)
        for p in await LegalEntityType.filter(query)
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .values("id", "name")
    ]

    if not entity_types:
        logger.info("Список разрешений пуст")
    return LegalEntityTypeListResponse(
        total=total_count, legal_entity_types=entity_types
    )
