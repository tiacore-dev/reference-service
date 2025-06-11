from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.pydantic_models.entity_company_relation_models import (
    EntityCompanyRelationCreateSchema,
    EntityCompanyRelationEditSchema,
    EntityCompanyRelationListResponseSchema,
    EntityCompanyRelationResponseSchema,
    EntityCompanyRelationSchema,
    entity_company_filter_params,
)
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import (
    EntityCompanyRelation,
    LegalEntity,
)
from app.dependencies.permissions import with_permission_and_legal_entity_company_check

entity_relation_router = APIRouter()


@entity_relation_router.post(
    "/add",
    response_model=EntityCompanyRelationResponseSchema,
    summary="Добавить связь компании и юрлица",
    status_code=status.HTTP_201_CREATED,
)
async def add_entity_company_relation(
    data: EntityCompanyRelationCreateSchema,
    context: dict = Depends(
        require_permission_in_context("add_legal_entity_company_relation")
    ),
):
    try:
        await validate_exists(LegalEntity, data.legal_entity_id, "Entity")

        if not context.get("is_superadmin"):
            if data.company_id not in context["companies"]:
                raise HTTPException(
                    status_code=403, detail="Вы не имеете доступа к этой компании"
                )

        relation = await EntityCompanyRelation.create(
            company_id=data.company_id,
            legal_entity_id=data.legal_entity_id,
            relation_type=data.relation_type,
            description=data.description,
        )
        return EntityCompanyRelationResponseSchema(
            entity_company_relation_id=relation.id
        )
    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Ошибка данных: {e}")
        raise HTTPException(status_code=400, detail="Некорректные данные") from e


@entity_relation_router.patch(
    "/{relation_id}",
    response_model=EntityCompanyRelationResponseSchema,
    summary="Изменить связь компании и юрлица",
)
async def update_entity_company_relation(
    relation_id: UUID,
    data: EntityCompanyRelationEditSchema,
    _=with_permission_and_legal_entity_company_check(
        "edit_legal_entity_company_relation"
    ),
):
    relation = await EntityCompanyRelation.filter(id=relation_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")

    update_data = data.model_dump(exclude_unset=True)

    if "legal_entity_id" in update_data:
        await validate_exists(LegalEntity, data.legal_entity_id, "Entity")

    await relation.update_from_dict(update_data)
    await relation.save()

    return {"entity_company_relation_id": str(relation.id)}


@entity_relation_router.delete(
    "/{relation_id}",
    summary="Удалить связь компании и юрлица",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_entity_company_relation(
    relation_id: UUID,
    _=with_permission_and_legal_entity_company_check(
        "delete_legal_entity_company_relation"
    ),
):
    relation = await EntityCompanyRelation.filter(id=relation_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    await relation.delete()


@entity_relation_router.get(
    "/all",
    response_model=EntityCompanyRelationListResponseSchema,
    summary="Получение списка связей компании и юрлица",
)
async def get_entity_company_relations(
    filters: dict = Depends(entity_company_filter_params),
    context: dict = Depends(
        require_permission_in_context("get_all_legal_entity_company_relations")
    ),
):
    query = Q()
    if filters.get("legal_entity_id"):
        query &= Q(legal_entity_id=filters["legal_entity_id"])
    if context["is_superadmin"]:
        company_filter = filters.get("company_id")
        if company_filter:
            query &= Q(company_id=company_filter)
    else:
        query &= Q(company_id=context["company"])
    if filters.get("relation_type"):
        query &= Q(relation_type__icontains=filters["relation_type"])
    if filters.get("description"):
        query &= Q(description__icontains=filters["description"])

    sort_by = filters.get("sort_by", "act_date")
    order = filters.get("order", "asc").lower()
    if order not in ("asc", "desc"):
        raise HTTPException(
            status_code=422, detail="order должен быть 'asc' или 'desc'"
        )

    sort_field = sort_by if order == "asc" else f"-{sort_by}"

    total_count = await EntityCompanyRelation.filter(query).count()
    relations = (
        await EntityCompanyRelation.filter(query)
        .order_by(sort_field)
        .prefetch_related("legal_entity")
        .offset((filters["page"] - 1) * filters["page_size"])
        .limit(filters["page_size"])
    )

    return EntityCompanyRelationListResponseSchema(
        total=total_count,
        relations=[
            EntityCompanyRelationSchema(
                entity_company_relation_id=relation.id,
                company_id=relation.company_id,
                legal_entity_id=relation.legal_entity.id,
                relation_type=relation.relation_type,
                description=relation.description,
                created_at=relation.created_at,
            )
            for relation in relations
        ],
    )


@entity_relation_router.get(
    "/{relation_id}",
    response_model=EntityCompanyRelationSchema,
    summary="Просмотр связи компании и юрлица",
)
async def get_entity_company_relation(
    relation_id: UUID,
    _=with_permission_and_legal_entity_company_check(
        "view_legal_entity_company_relation"
    ),
):
    relation = (
        await EntityCompanyRelation.filter(id=relation_id)
        .prefetch_related("legal_entity")
        .first()
    )

    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")

    return EntityCompanyRelationSchema(
        entity_company_relation_id=relation.id,
        company_id=relation.company_id,
        legal_entity_id=relation.legal_entity.id,
        relation_type=relation.relation_type,
        description=relation.description,
        created_at=relation.created_at,
    )
