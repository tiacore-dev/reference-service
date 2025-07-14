import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class WarehouseCreateSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, alias="warehouse_name")
    description: Optional[str] = Field(None)
    address: str = Field(...)
    city_id: UUID = Field(...)
    company_id: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class WarehouseEditSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100, alias="warehouse_name")
    description: Optional[str] = Field(None)
    address: Optional[str] = Field(None)
    company_id: Optional[UUID] = Field(None)
    city_id: Optional[UUID] = Field(None)

    class Config:
        from_attributes = True
        populate_by_name = True


class WarehouseSchema(BaseModel):
    id: UUID = Field(..., alias="warehouse_id")
    name: str = Field(..., alias="warehouse_name")
    city_id: UUID = Field(...)
    address: str = Field(...)
    description: Optional[str] = Field(None)
    company_id: UUID = Field(...)
    created_at: datetime.datetime = Field(...)
    created_by: UUID = Field(...)
    modified_by: UUID = Field(...)
    modified_at: datetime.datetime = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class WarehouseResponseSchema(BaseModel):
    warehouse_id: UUID


class WarehouseListResponseSchema(BaseModel):
    total: int
    warehouses: List[WarehouseSchema]


def warehouse_filter_params(
    warehouse_name: Optional[str] = Query(None, description="Фильтр по названию промпта"),
    city_id: Optional[UUID] = Query(None),
    company_id: Optional[str] = Query(None, description="Фильтр по городуу"),
    description: Optional[str] = Query(None, description="Фильтр по тексту"),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "warehouse_name": warehouse_name,
        "city_id": city_id,
        "description": description,
        "company_id": company_id,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
