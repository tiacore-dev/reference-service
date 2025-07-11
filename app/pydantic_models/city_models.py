from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import Field
from tiacore_lib.pydantic_models.clean_model import CleanableBaseModel


class CityCreateSchema(CleanableBaseModel):
    name: str = Field(..., max_length=100, alias="city_name")
    region: str = Field(...)
    code: Optional[str] = Field(None)
    external_id: Optional[str] = Field(None)
    timezone: int

    class Config:
        from_attributes = True
        populate_by_name = True


class CityEditSchema(CleanableBaseModel):
    name: Optional[str] = Field(None, max_length=100, alias="city_name")
    region: Optional[str] = Field(None)
    code: Optional[str] = Field(None)
    external_id: Optional[str] = Field(None)
    timezone: Optional[int] = Field(None)

    class Config:
        from_attributes = True
        populate_by_name = True


class CitySchema(CleanableBaseModel):
    id: UUID = Field(..., alias="city_id")
    name: str = Field(..., alias="city_name")
    region: str = Field(...)
    code: Optional[str] = Field(None)
    external_id: Optional[str] = Field(None)
    timezone: int

    class Config:
        from_attributes = True
        populate_by_name = True


class CityResponseSchema(CleanableBaseModel):
    city_id: UUID


class CityListResponseSchema(CleanableBaseModel):
    total: int
    cities: List[CitySchema]


def city_filter_params(
    city_name: Optional[str] = Query(None, description="Фильтр по названию промпта"),
    region: Optional[str] = Query(None),
    code: Optional[str] = Query(None),
    external_id: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc / desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "city_name": city_name,
        "region": region,
        "code": code,
        "external_id": external_id,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
