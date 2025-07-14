from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from tiacore_lib.handlers.auth_handler import get_current_user
from tiacore_lib.pydantic_models.legal_entity_models import (
    LegalEntityCreateSchema,
    LegalEntityEditSchema,
    LegalEntityINNCreateSchema,
    LegalEntityListResponseSchema,
    LegalEntityResponseSchema,
    LegalEntitySchema,
    LegalEntityShortSchema,
    inn_kpp_filter_params,
    legal_entity_filter_params,
)
from tiacore_lib.utils.entity_data_get import fetch_egrul_data
from tiacore_lib.utils.helpers import format_address
from tortoise.expressions import Q

from app.database.models import (
    LegalEntity,
)
from app.pydantic_models.entity_models import LegalEntityByIdsRequestSchema

entity_router = APIRouter()


@entity_router.post(
    "/add",
    response_model=LegalEntityResponseSchema,
    summary="Добавить юридическое лицо",
    status_code=status.HTTP_201_CREATED,
)
async def add_legal_entity(
    data: LegalEntityCreateSchema,
    _=Depends(get_current_user),
):
    if data.kpp:
        existing_entity = await LegalEntity.exists(inn=data.inn, kpp=data.kpp)
    else:
        existing_entity = await LegalEntity.exists(inn=data.inn)

    if existing_entity:
        logger.warning(f"Юрлицо с ИНН {data.inn} уже существует")
        raise HTTPException(status_code=400, detail=f"Юрлицо с ИНН {data.inn} уже существует")
    if data.ogrn:
        existing_entity = await LegalEntity.exists(ogrn=data.ogrn)
        if existing_entity:
            raise HTTPException(status_code=400, detail=f"Юрлицо с ОГРН {data.ogrn} уже существует")

    entity = await LegalEntity.create(
        short_name=data.short_name,
        full_name=data.full_name,
        inn=data.inn,
        kpp=data.kpp,
        ogrn=data.ogrn,
        vat_rate=data.vat_rate,
        opf=data.opf,
        address=data.address,
        signer=data.signer,
    )
    return LegalEntityResponseSchema(legal_entity_id=entity.id)


@entity_router.post(
    "/add-by-inn",
    response_model=LegalEntityResponseSchema,
    summary="Добавить юридическое лицо по ИНН и КПП",
    status_code=status.HTTP_201_CREATED,
)
async def add_legal_entity_by_inn(
    data: LegalEntityINNCreateSchema,
    _=Depends(get_current_user),
):
    if data.kpp:
        existing_entity = await LegalEntity.exists(inn=data.inn, kpp=data.kpp)
    else:
        existing_entity = await LegalEntity.exists(inn=data.inn)

    if existing_entity:
        logger.warning(f"Юрлицо с ИНН {data.inn} уже существует")
        raise HTTPException(status_code=400, detail=f"Юрлицо с ИНН {data.inn} уже существует")

    entity_data = await fetch_egrul_data(data.inn)
    # logger.debug(f"Полученный ответ о юр лице: {entity_data}")
    if entity_data.get("СвЮЛ"):
        org_data = entity_data["СвЮЛ"]

        # Валидация КПП: если указан, должен быть среди филиалов
        if data.kpp:
            branches = org_data.get("СвПодразд", {}).get("СвФилиал", [])
            if isinstance(branches, dict):
                branches = [branches]
            elif isinstance(branches, str):
                branches = []  # или можно залогировать неожиданный формат

            branch_kpps = [
                branch.get("СвУчетНОФилиал", {}).get("@attributes", {}).get("КПП")
                for branch in branches
                if isinstance(branch, dict) and branch.get("СвУчетНОФилиал", {}).get("@attributes", {}).get("КПП")
            ]
            if data.kpp not in branch_kpps and data.kpp != org_data["@attributes"].get("КПП"):
                raise HTTPException(
                    status_code=404,
                    detail=f"""КПП {data.kpp} не найден ни у
                    головной организации, ни среди филиалов""",
                )

        addr = org_data["СвАдресЮЛ"].get("АдресРФ") or {}

        entity = await LegalEntity.create(
            short_name=org_data["СвНаимЮЛ"]["СвНаимЮЛСокр"]["@attributes"]["НаимСокр"],
            inn=org_data["@attributes"]["ИНН"],
            kpp=data.kpp or org_data["@attributes"]["КПП"],
            ogrn=org_data["@attributes"]["ОГРН"],
            address=format_address(addr),
        )
    elif entity_data.get("СвИП"):
        org_data = entity_data["СвИП"]
        fio_data = org_data.get("СвФЛ", {}).get("ФИОРус", {}).get("@attributes", {})

        # Собираем ФИО как наименование
        full_name = " ".join(
            filter(
                None,
                [
                    fio_data.get("Фамилия"),
                    fio_data.get("Имя"),
                    fio_data.get("Отчество"),
                ],
            )
        )

        addr = entity_data.get("СвРегОрг", {}).get("@attributes", {}).get("АдрРО") or ""

        entity = await LegalEntity.create(
            short_name=full_name,
            inn=org_data["@attributes"].get("ИННФЛ"),
            kpp=data.kpp,
            ogrn=org_data["@attributes"].get("ОГРНИП"),
            address=addr,
        )
    else:
        raise HTTPException(status_code=400, detail="Организация не является ни Юр Лицом, ни ИП")

    return LegalEntityResponseSchema(legal_entity_id=entity.id)


@entity_router.patch(
    "/{legal_entity_id}",
    response_model=LegalEntityResponseSchema,
    summary="Изменить юридическое лицо",
)
async def update_legal_entity(
    legal_entity_id: UUID,
    data: LegalEntityEditSchema,
    _=Depends(get_current_user),
):
    entity = await LegalEntity.filter(id=legal_entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Юридическое лицо не найдено")

    update_data = data.model_dump(exclude_unset=True)

    await entity.update_from_dict(update_data)
    await entity.save()

    return {"legal_entity_id": str(entity.id)}


@entity_router.delete(
    "/{legal_entity_id}",
    summary="Удалить юридическое лицо",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_legal_entity(
    legal_entity_id: UUID,
    _=Depends(get_current_user),
):
    entity = await LegalEntity.filter(id=legal_entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Юридическое лицо не найдено")

    await entity.delete()
    return


@entity_router.get(
    "/all",
    response_model=LegalEntityListResponseSchema,
    summary="Получение списка юридических лиц",
)
async def get_legal_entities(
    filters: dict = Depends(legal_entity_filter_params),
    _: dict = Depends(get_current_user),
):
    query = Q()

    sort_by = filters.get("sort_by", "short_name")

    sort_field_map = {
        "name": "short_name",
        "short_name": "short_name",
    }

    sort_field = sort_field_map.get(sort_by, sort_by)

    order_prefix = "-" if filters.get("order") == "desc" else ""
    order_by = f"{order_prefix}{sort_field}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await LegalEntity.filter(query).count()
    entities = (
        await LegalEntity.filter(query)
        .order_by(order_by)
        .offset(offset)
        .limit(page_size)
        .values(
            "id",
            "full_name",
            "short_name",
            "inn",
            "kpp",
            "opf",
            "vat_rate",
            "address",
            "signer",
            "ogrn",
        )
    )

    return LegalEntityListResponseSchema(
        total=total_count,
        entities=[LegalEntitySchema(**entity) for entity in entities],
    )


@entity_router.post(
    "/by-ids",
    response_model=LegalEntityListResponseSchema,
    summary="Получить список юридических лиц по списку ID с фильтрацией и пагинацией",
)
async def get_legal_entities_by_ids(
    data: LegalEntityByIdsRequestSchema,
    filters: dict = Depends(legal_entity_filter_params),
    _: dict = Depends(get_current_user),
):
    if not data.ids:
        return LegalEntityListResponseSchema(total=0, entities=[])

    query = Q(id__in=data.ids)

    sort_by = filters.get("sort_by", "short_name")

    # Маппинг алиасов → реальные поля модели
    sort_field_map = {
        "name": "short_name",
        "short_name": "short_name",
        # можно расширить при необходимости
    }

    sort_field = sort_field_map.get(sort_by, sort_by)

    order_prefix = "-" if filters.get("order") == "desc" else ""
    order_by = f"{order_prefix}{sort_field}"

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await LegalEntity.filter(query).count()
    entities = (
        await LegalEntity.filter(query)
        .order_by(order_by)
        .offset(offset)
        .limit(page_size)
        .values(
            "id",
            "full_name",
            "short_name",
            "inn",
            "kpp",
            "opf",
            "vat_rate",
            "address",
            "signer",
            "ogrn",
        )
    )

    return LegalEntityListResponseSchema(
        total=total_count,
        entities=[LegalEntitySchema(**entity) for entity in entities],
    )


@entity_router.get(
    "/inn-kpp",
    response_model=LegalEntityShortSchema,
    summary="Получение организации по инн и кпп",
)
async def get_legal_entity_by_inn_kpp(
    filters: dict[str, Optional[str]] = Depends(inn_kpp_filter_params),
    _: dict = Depends(get_current_user),
):
    try:
        kpp = filters.get("kpp")
        if not kpp:
            entity = await LegalEntity.filter(inn=filters["inn"]).first()
        else:
            entity = await LegalEntity.filter(inn=filters["inn"], kpp=kpp).first()
        if not entity:
            raise HTTPException(status_code=404, detail="Организация не найдена")
        return LegalEntityShortSchema(
            legal_entity_id=entity.id,
            legal_entity_name=entity.short_name,
        )
    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


@entity_router.get(
    "/{legal_entity_id}",
    response_model=LegalEntitySchema,
    summary="Просмотр одного юридического лица",
)
async def get_legal_entity(
    legal_entity_id: UUID,
    _: dict = Depends(get_current_user),
):
    entity = await LegalEntity.filter(id=legal_entity_id).first()

    if not entity:
        raise HTTPException(status_code=404, detail="Юридическое лицо не найдено")

    return LegalEntitySchema(**entity.__dict__)
