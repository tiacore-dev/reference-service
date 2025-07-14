import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class CashRegisterCreateSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, alias="cash_register_name")
    description: Optional[str] = Field(None)
    company_id: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class CashRegisterEditSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100, alias="cash_register_name")
    description: Optional[str] = Field(None)
    company_id: Optional[UUID] = Field(None)

    class Config:
        from_attributes = True
        populate_by_name = True


class CashRegisterSchema(BaseModel):
    id: UUID = Field(..., alias="cash_register_id")
    name: str = Field(..., alias="cash_register_name")
    description: Optional[str] = Field(None)
    company_id: UUID = Field(...)
    created_at: datetime.datetime = Field(...)
    created_by: UUID = Field(...)
    modified_by: UUID = Field(...)
    modified_at: datetime.datetime = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class CashRegisterResponseSchema(BaseModel):
    cash_register_id: UUID


class CashRegisterListResponseSchema(BaseModel):
    total: int
    cash_registers: List[CashRegisterSchema]


def cash_register_filter_params(
    cash_register_name: Optional[str] = Query(None, description="Фильтр по названию промпта"),
    description: Optional[str] = Query(None, description="Фильтр по тексту"),
    company_id: Optional[UUID] = Query(None),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "cash_register_name": cash_register_name,
        "company_id": company_id,
        "description": description,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
