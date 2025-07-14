from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from loguru import logger
from tiacore_lib.handlers.auth_handler import get_current_user
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.handlers.permissions_handler import (
    with_permission_and_company_from_body_check,
)
from tiacore_lib.utils.validate_helpers import validate_company_access, validate_exists
from tortoise.expressions import Q

from app.database.models import City, Warehouse
from app.pydantic_models.warehouse_models import (
    WarehouseCreateSchema,
    WarehouseEditSchema,
    WarehouseListResponseSchema,
    WarehouseResponseSchema,
    WarehouseSchema,
    warehouse_filter_params,
)

warehouse_router = APIRouter()


@warehouse_router.post(
    "/add",
    response_model=WarehouseResponseSchema,
    summary="Добавление нового склада",
    status_code=status.HTTP_201_CREATED,
)
async def add_warehouse(
    data: WarehouseCreateSchema = Body(...),
    context=Depends(with_permission_and_company_from_body_check("add_warehouse")),
):
    await validate_exists(City, data.city_id, "Город")
    warehouse = await Warehouse.create(
        created_by=context["user_id"],
        modified_by=context["user_id"],
        **data.model_dump(exclude_unset=True),
    )
    if not warehouse:
        logger.error("Не удалось создать склад")
        raise HTTPException(status_code=500, detail="Не удалось создать склад")

    logger.success(f"склад {warehouse.name} ({warehouse.id}) успешно создан")
    return {"warehouse_id": str(warehouse.id)}


@warehouse_router.patch(
    "/{warehouse_id}",
    summary="Изменение склада",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def edit_warehouse(
    warehouse_id: UUID = Path(..., title="ID склада", description="ID изменяемого склада"),
    data: WarehouseEditSchema = Body(...),
    context=Depends(with_permission_and_company_from_body_check("edit_warehouse")),
):
    logger.info(f"Обновление склада {warehouse_id}")

    warehouse = await Warehouse.filter(id=warehouse_id).first()
    if not warehouse:
        logger.warning(f"склад {warehouse_id} не найден")
        raise HTTPException(status_code=404, detail="Склад не найден")
    if data.city_id:
        await validate_exists(City, data.city_id, "Город")
    validate_company_access(warehouse, context, "складом")
    warehouse.modified_by = context["user_id"]
    await warehouse.update_from_dict(data.model_dump(exclude_unset=True))
    await warehouse.save()


@warehouse_router.delete(
    "/{warehouse_id}",
    summary="Удаление склада",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_warehouse(
    warehouse_id: UUID = Path(..., title="ID склада", description="ID удаляемого склада"),
    context=Depends(require_permission_in_context("delete_warehouse")),
):
    warehouse = await Warehouse.filter(id=warehouse_id).first()
    if not warehouse:
        logger.warning(f"склад {warehouse_id} не найден")
        raise HTTPException(status_code=404, detail="склад не найден")
    validate_company_access(warehouse, context, "складом")
    await warehouse.delete()


@warehouse_router.get(
    "/all",
    response_model=WarehouseListResponseSchema,
    summary="Получение списка складов с фильтрацией",
)
async def get_warehouses(
    filters: dict = Depends(warehouse_filter_params),
    context=Depends(get_current_user),
):
    query = Q()
    if filters.get("city_id"):
        query &= Q(city_id=filters["city_id"])
    if filters.get("company_id"):
        query &= Q(company_id=filters.get("company_id"))
    if filters.get("warehouse_name"):
        query &= Q(name__icontains=filters["warehouse_name"])
    if filters.get("description"):
        query &= Q(description__icontains=filters["description"])

    order_by = f"{'-' if filters.get('order') == 'desc' else ''}{filters.get('sort_by', 'name')}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)

    total_count = await Warehouse.filter(query).count()

    warehouses = await Warehouse.filter(query).order_by(order_by).offset((page - 1) * page_size).limit(page_size)

    return WarehouseListResponseSchema(
        total=total_count,
        warehouses=[WarehouseSchema.model_validate(warehouse) for warehouse in warehouses],
    )


@warehouse_router.get("/{warehouse_id}", response_model=WarehouseSchema, summary="Просмотр склады")
async def get_warehouse(
    warehouse_id: UUID = Path(..., title="ID склады", description="ID просматриваемой склады"),
    context=Depends(get_current_user),
):
    logger.info(f"Запрос на просмотр склады: {warehouse_id}")
    warehouse = await Warehouse.filter(id=warehouse_id).first()
    validate_company_access(warehouse, context, "складом")
    if warehouse is None:
        logger.warning(f"склада {warehouse_id} не найдена")
        raise HTTPException(status_code=404, detail="склада не найдена")

    warehouse_schema = WarehouseSchema.model_validate(warehouse)

    logger.success(f"склада найдена: {warehouse_schema}")
    return warehouse_schema
