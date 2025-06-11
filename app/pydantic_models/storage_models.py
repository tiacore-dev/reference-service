from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import Field
from tiacore_lib.pydantic_models.clean_model import CleanableBaseModel


class StorageCreateSchema(CleanableBaseModel):
    name: str = Field(..., min_length=3, max_length=100, alias="storage_name")
    description: Optional[str] = Field(None)

    class Config:
        from_attributes = True
        populate_by_name = True


class StorageEditSchema(CleanableBaseModel):
    name: Optional[str] = Field(
        None, min_length=3, max_length=100, alias="storage_name"
    )
    description: Optional[str] = Field(None)

    class Config:
        from_attributes = True
        populate_by_name = True


class StorageSchema(CleanableBaseModel):
    id: UUID = Field(..., alias="storage_id")
    name: str = Field(..., alias="storage_name")
    description: Optional[str] = Field(None)

    class Config:
        from_attributes = True
        populate_by_name = True


class StorageResponseSchema(CleanableBaseModel):
    storage_id: UUID


class StorageListResponseSchema(CleanableBaseModel):
    total: int
    storages: List[StorageSchema]


def storage_filter_params(
    storage_name: Optional[str] = Query(None, description="Фильтр по названию промпта"),
    description: Optional[str] = Query(None, description="Фильтр по тексту"),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "storage_name": storage_name,
        "description": description,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
