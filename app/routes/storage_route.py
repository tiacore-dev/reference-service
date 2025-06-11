from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from loguru import logger
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import Storage
from app.pydantic_models.storage_models import (
    StorageCreateSchema,
    StorageEditSchema,
    StorageListResponseSchema,
    StorageResponseSchema,
    StorageSchema,
    storage_filter_params,
)

storage_router = APIRouter()


@storage_router.post(
    "/add",
    response_model=StorageResponseSchema,
    summary="Добавление нового склада",
    status_code=status.HTTP_201_CREATED,
)
async def add_storage(
    data: StorageCreateSchema = Body(...),
    _=Depends(require_permission_in_context("add_storage")),
):
    storage = await Storage.create(**data.model_dump(exclude_unset=True))
    if not storage:
        logger.error("Не удалось создать склад")
        raise HTTPException(status_code=500, detail="Не удалось создать склад")

    logger.success(f"склад {storage.name} ({storage.id}) успешно создан")
    return {"storage_id": str(storage.id)}


@storage_router.patch(
    "/{storage_id}",
    summary="Изменение склада",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def edit_storage(
    storage_id: UUID = Path(
        ..., title="ID склада", description="ID изменяемого склада"
    ),
    data: StorageEditSchema = Body(...),
    _=Depends(require_permission_in_context("edit_storage")),
):
    logger.info(f"Обновление склада {storage_id}")

    storage = await Storage.filter(id=storage_id).first()
    if not storage:
        logger.warning(f"склад {storage_id} не найден")
        raise HTTPException(status_code=404, detail="Склад не найден")
    await storage.update_from_dict(data.model_dump(exclude_unset=True))
    await storage.save()


@storage_router.delete(
    "/{storage_id}",
    summary="Удаление склада",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_storage(
    storage_id: UUID = Path(..., title="ID склада", description="ID удаляемого склада"),
    _=Depends(require_permission_in_context("delete_storage")),
):
    storage = await Storage.filter(id=storage_id).first()
    if not storage:
        logger.warning(f"склад {storage_id} не найден")
        raise HTTPException(status_code=404, detail="склад не найден")
    await storage.delete()


@storage_router.get(
    "/all",
    response_model=StorageListResponseSchema,
    summary="Получение списка складов с фильтрацией",
)
async def get_storages(
    filters: dict = Depends(storage_filter_params),
    _=Depends(require_permission_in_context("get_all_storages")),
):
    query = Q()

    if filters.get("storage_name"):
        query &= Q(name__icontains=filters["storage_name"])
    if filters.get("description"):
        query &= Q(description__icontains=filters["description"])

    order_by = f"{'-' if filters.get('order') == 'desc' else ''}{
        filters.get('sort_by', 'name')
    }"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)

    total_count = await Storage.filter(query).count()

    storages = (
        await Storage.filter(query)
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .values("id", "name", "description")
    )

    return StorageListResponseSchema(
        total=total_count,
        storages=[StorageSchema(**storage) for storage in storages],
    )


@storage_router.get(
    "/{storage_id}", response_model=StorageSchema, summary="Просмотр склады"
)
async def get_storage(
    storage_id: UUID = Path(
        ..., title="ID склады", description="ID просматриваемой склады"
    ),
    _=Depends(require_permission_in_context("view_storage")),
):
    logger.info(f"Запрос на просмотр склады: {storage_id}")
    storage = (
        await Storage.filter(id=storage_id).first().values("id", "name", "description")
    )

    if storage is None:
        logger.warning(f"склада {storage_id} не найдена")
        raise HTTPException(status_code=404, detail="склада не найдена")

    storage_schema = StorageSchema(**storage)

    logger.success(f"склада найдена: {storage_schema}")
    return storage_schema
