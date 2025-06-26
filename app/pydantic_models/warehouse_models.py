import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import Field
from tiacore_lib.pydantic_models.clean_model import CleanableBaseModel


class WarehouseCreateSchema(CleanableBaseModel):
    name: str = Field(..., min_length=3, max_length=100, alias="warehouse_name")
    description: Optional[str] = Field(None)
    company_id: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class WarehouseEditSchema(CleanableBaseModel):
    name: Optional[str] = Field(
        None, min_length=3, max_length=100, alias="warehouse_name"
    )
    description: Optional[str] = Field(None)
    company_id: Optional[UUID] = Field(None)

    class Config:
        from_attributes = True
        populate_by_name = True


class WarehouseSchema(CleanableBaseModel):
    id: UUID = Field(..., alias="warehouse_id")
    name: str = Field(..., alias="warehouse_name")
    description: Optional[str] = Field(None)
    company_id: UUID = Field(...)
    created_at: datetime.datetime = Field(...)
    created_by: UUID = Field(...)
    modified_by: UUID = Field(...)
    modified_at: datetime.datetime = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class WarehouseResponseSchema(CleanableBaseModel):
    warehouse_id: UUID


class WarehouseListResponseSchema(CleanableBaseModel):
    total: int
    warehouses: List[WarehouseSchema]


def warehouse_filter_params(
    warehouse_name: Optional[str] = Query(
        None, description="Фильтр по названию промпта"
    ),
    company_id: Optional[str] = Query(None),
    description: Optional[str] = Query(None, description="Фильтр по тексту"),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "warehouse_name": warehouse_name,
        "description": description,
        "company_id": company_id,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
