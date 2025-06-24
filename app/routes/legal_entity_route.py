from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import (
    EntityCompanyRelation,
    LegalEntity,
    LegalEntityType,
)
from app.pydantic_models.entity_models import LegalEntityByIdsRequestSchema
from app.utils.db_helpers import get_entities_by_query

entity_router = APIRouter()


@entity_router.post(
    "/add",
    response_model=LegalEntityResponseSchema,
    summary="Добавить юридическое лицо",
    status_code=status.HTTP_201_CREATED,
)
async def add_legal_entity(
    data: LegalEntityCreateSchema,
    context=Depends(get_current_user),
):
    entity_type = None

    # if not context.get("is_superadmin"):
    #     if data.company_id not in context["companies"]:
    #         raise HTTPException(
    #             status_code=403, detail="Вы не имеете доступа к этой компании"
    #         )
    if data.entity_type_id is not None:
        await validate_exists(LegalEntityType, data.entity_type_id, "LegalEntityType")

    if data.kpp:
        existing_entity = await LegalEntity.exists(inn=data.inn, kpp=data.kpp)
    else:
        existing_entity = await LegalEntity.exists(inn=data.inn)

    if existing_entity:
        logger.warning(f"Юрлицо с ИНН {data.inn} уже существует")
        raise HTTPException(
            status_code=400, detail=f"Юрлицо с ИНН {data.inn} уже существует"
        )
    if data.ogrn:
        existing_entity = await LegalEntity.exists(ogrn=data.ogrn)
        if existing_entity:
            raise HTTPException(
                status_code=400, detail=f"Юрлицо с ОГРН {data.ogrn} уже существует"
            )

    entity = await LegalEntity.create(
        short_name=data.short_name,
        full_name=data.full_name,
        inn=data.inn,
        kpp=data.kpp,
        ogrn=data.ogrn,
        vat_rate=data.vat_rate,
        opf=data.opf,
        address=data.address,
        entity_type=entity_type,
        signer=data.signer,
    )
    if data.relation_type:
        await EntityCompanyRelation.create(
            company_id=data.company_id,
            legal_entity=entity,
            relation_type=data.relation_type,
            description=data.description,
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
    context=Depends(get_current_user),
):
    # if not context.get("is_superadmin"):
    #     if data.company_id not in context["companies"]:
    #         raise HTTPException(
    #             status_code=403, detail="Вы не имеете доступа к этой компании"
    #         )

    if data.kpp:
        existing_entity = await LegalEntity.exists(inn=data.inn, kpp=data.kpp)
    else:
        existing_entity = await LegalEntity.exists(inn=data.inn)

    if existing_entity:
        logger.warning(f"Юрлицо с ИНН {data.inn} уже существует")
        raise HTTPException(
            status_code=400, detail=f"Юрлицо с ИНН {data.inn} уже существует"
        )

    entity_data = await fetch_egrul_data(data.inn)
    org_data = entity_data["СвЮЛ"]

    # Валидация КПП: если указан, должен быть среди филиалов
    if data.kpp:
        branch_kpps = [
            филиал.get("СвУчетНОФилиал", {}).get("@attributes", {}).get("КПП")
            for филиал in org_data.get("СвПодразд", {}).get("СвФилиал", [])
            if филиал.get("СвУчетНОФилиал", {}).get("@attributes", {}).get("КПП")
        ]
        if data.kpp not in branch_kpps and data.kpp != org_data["@attributes"].get(
            "КПП"
        ):
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
    if data.relation_type:
        await EntityCompanyRelation.create(
            company_id=data.company_id,
            legal_entity=entity,
            relation_type=data.relation_type,
            description=data.description,
        )

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

    if "entity_type_id" in update_data:
        await validate_exists(LegalEntityType, data.entity_type_id, "LegalEntityType")

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
    company_id: Optional[UUID] = Query(None),
    filters: dict = Depends(legal_entity_filter_params),
    context: dict = Depends(get_current_user),
):
    query = Q()

    if context["is_superadmin"]:
        company_filter = filters.get("company_id")
        if company_filter:
            query &= Q(entity_company_relations__company_id=company_filter)

        else:
            related_entity_ids = await EntityCompanyRelation.filter(
                company_id=company_id
            ).values_list("legal_entity_id", flat=True)

            if not related_entity_ids:
                return LegalEntityListResponseSchema(total=0, entities=[])

            query &= Q(id__in=related_entity_ids)

    if filters.get("entity_type_id"):
        query &= Q(entity_type_id=filters["entity_type_id"])

    total_count, entities = await get_entities_by_query(query)

    return LegalEntityListResponseSchema(
        total=total_count,
        entities=[LegalEntitySchema(**entity) for entity in entities],
    )


@entity_router.post(
    "/by-ids",
    response_model=LegalEntityListResponseSchema,
    summary="Получить список юридических лиц по списку ID",
)
async def get_legal_entities_by_ids(
    data: LegalEntityByIdsRequestSchema,
    _: dict = Depends(get_current_user),  # или with_permission, если хочешь
):
    entities = await LegalEntity.filter(id__in=data.ids).values(
        "id",
        "full_name",
        "short_name",
        "inn",
        "kpp",
        "opf",
        "vat_rate",
        "address",
        "entity_type_id",
        "signer",
        "ogrn",
    )

    return LegalEntityListResponseSchema(
        total=len(entities),
        entities=[LegalEntitySchema(**entity) for entity in entities],
    )


@entity_router.get(
    "/get-buyers",
    response_model=LegalEntityListResponseSchema,
    summary="Получение списка buyers",
)
async def get_buyers(
    company_id: Optional[UUID] = Query(None),
    context: dict = Depends(get_current_user),
):
    try:
        if context["is_superadmin"]:
            related_entity_ids = await EntityCompanyRelation.filter(
                relation_type="buyer"
            ).values_list("legal_entity_id", flat=True)
        else:
            related_entity_ids = await EntityCompanyRelation.filter(
                company_id=company_id, relation_type="buyer"
            ).values_list("legal_entity_id", flat=True)

        if not related_entity_ids:
            return LegalEntityListResponseSchema(total=0, entities=[])

        query = Q(id__in=related_entity_ids)

        total_count, entities = await get_entities_by_query(query)

        return LegalEntityListResponseSchema(
            total=total_count,
            entities=[LegalEntitySchema(**entity) for entity in entities],
        )

    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


@entity_router.get(
    "/get-sellers",
    response_model=LegalEntityListResponseSchema,
    summary="Получение списка sellers",
)
async def get_sellers(
    company_id: Optional[UUID] = Query(None),
    context: dict = Depends(get_current_user),
):
    try:
        # Ищем все legal_entity_id, связанные с этими компаниями
        if context["is_superadmin"]:
            related_entity_ids = await EntityCompanyRelation.filter(
                relation_type="seller"
            ).values_list("legal_entity_id", flat=True)
        else:
            related_entity_ids = await EntityCompanyRelation.filter(
                company_id=company_id, relation_type="seller"
            ).values_list("legal_entity_id", flat=True)

        if not related_entity_ids:
            return LegalEntityListResponseSchema(total=0, entities=[])
        query = Q(id__in=related_entity_ids)

        total_count, entities = await get_entities_by_query(query)
        return LegalEntityListResponseSchema(
            total=total_count,
            entities=[LegalEntitySchema(**entity) for entity in entities],
        )

    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


@entity_router.get(
    "/get-by-company",
    response_model=LegalEntityListResponseSchema,
    summary="Получение списка организаций по компании",
)
async def get_by_company(
    company_id: UUID = Query(..., description="ID компании"),
    _: dict = Depends(get_current_user),
):
    try:
        related_entity_ids = await EntityCompanyRelation.filter(
            company_id=company_id
        ).values_list("legal_entity_id", flat=True)

        if not related_entity_ids:
            return LegalEntityListResponseSchema(total=0, entities=[])

        query = Q(id__in=related_entity_ids)

        total_count, entities = await get_entities_by_query(query)

        return LegalEntityListResponseSchema(
            total=total_count,
            entities=[LegalEntitySchema(**entity) for entity in entities],
        )

    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


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
    context: dict = Depends(get_current_user),
):
    entity = (
        await LegalEntity.filter(id=legal_entity_id)
        .prefetch_related("entity_type", "entity_company_relations")
        .first()
    )

    if not entity:
        raise HTTPException(status_code=404, detail="Юридическое лицо не найдено")

    related_company_ids = [rel.company_id for rel in entity.entity_company_relations]

    if not context["is_superadmin"] and context["company"] not in related_company_ids:
        raise HTTPException(status_code=403, detail="Нет доступа к этой записи")

    return LegalEntitySchema(**entity.__dict__)
