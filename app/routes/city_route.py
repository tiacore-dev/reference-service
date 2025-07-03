from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from loguru import logger
from tiacore_lib.handlers.auth_handler import get_current_user, require_superadmin
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import City
from app.pydantic_models.city_models import (
    CityCreateSchema,
    CityEditSchema,
    CityListResponseSchema,
    CityResponseSchema,
    CitySchema,
    city_filter_params,
)

city_router = APIRouter()


@city_router.post(
    "/add",
    response_model=CityResponseSchema,
    summary="Добавление нового города",
    status_code=status.HTTP_201_CREATED,
)
async def add_city(
    data: CityCreateSchema = Body(...),
    _=Depends(require_superadmin),
):
    city = await City.create(**data.model_dump(exclude_unset=True))
    if not city:
        logger.error("Не удалось создать город")
        raise HTTPException(status_code=500, detail="Не удалось создать город")

    logger.success(f"город {city.name} ({city.id}) успешно создан")
    return {"city_id": str(city.id)}


@city_router.patch(
    "/{city_id}",
    summary="Изменение города",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def edit_city(
    city_id: UUID = Path(..., title="ID города", description="ID изменяемого города"),
    data: CityEditSchema = Body(...),
    _=Depends(require_superadmin),
):
    logger.info(f"Обновление города {city_id}")

    city = await City.filter(id=city_id).first()
    if not city:
        logger.warning(f"город {city_id} не найден")
        raise HTTPException(status_code=404, detail="город не найден")
    await city.update_from_dict(data.model_dump(exclude_unset=True))
    await city.save()


@city_router.delete(
    "/{city_id}",
    summary="Удаление города",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_city(
    city_id: UUID = Path(..., title="ID города", description="ID удаляемого города"),
    _=Depends(require_permission_in_context("delete_city")),
):
    city = await City.filter(id=city_id).first()
    if not city:
        logger.warning(f"город {city_id} не найден")
        raise HTTPException(status_code=404, detail="город не найден")
    await city.delete()


@city_router.get(
    "/all",
    response_model=CityListResponseSchema,
    summary="Получение списка кассов с фильтрацией",
)
async def get_citys(
    filters: dict = Depends(city_filter_params),
    _=Depends(get_current_user),
):
    query = Q()

    if filters.get("city_name"):
        query &= Q(name__icontains=filters["city_name"])
    if filters.get("code"):
        query &= Q(description__icontains=filters["code"])
    if filters.get("region"):
        query &= Q(region__icontains=filters["region"])
    if filters.get("external_id"):
        query &= Q(external_id__icontains=filters["external_id"])

    order_by = f"{'-' if filters.get('order') == 'desc' else ''}{
        filters.get('sort_by', 'name')
    }"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)

    total_count = await City.filter(query).count()

    citys = (
        await City.filter(query)
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .values("id", "name", "external_id", "region", "code")
    )

    return CityListResponseSchema(
        total=total_count,
        cities=[CitySchema(**city) for city in citys],
    )


@city_router.get("/{city_id}", response_model=CitySchema, summary="Просмотр города")
async def get_city(
    city_id: UUID = Path(
        ..., title="ID города", description="ID просматриваемого города"
    ),
    _=Depends(get_current_user),
):
    logger.info(f"Запрос на просмотр города: {city_id}")
    city = (
        await City.filter(id=city_id)
        .first()
        .values("id", "name", "external_id", "region", "code")
    )

    if city is None:
        logger.warning(f"город {city_id} не найден")
        raise HTTPException(status_code=404, detail="город не найден")

    city_schema = CitySchema(**city)

    logger.success(f"город найден: {city_schema}")
    return city_schema
