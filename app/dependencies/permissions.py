from uuid import UUID

from fastapi import Depends, HTTPException, Path
from tiacore_lib.handlers.dependency_handler import require_permission_in_context

from app.database.models import (
    EntityCompanyRelation,
)


def with_permission_and_entity_company_check(permission: str):
    async def dependency(
        legal_entity_id: UUID = Path(..., description="ID юридического лица"),
        context: dict = Depends(require_permission_in_context(permission)),
    ):
        if context.get("is_superadmin"):
            return context

        # Проверка, связано ли это юр. лицо с компанией пользователя
        is_related = await EntityCompanyRelation.exists(
            legal_entity_id=legal_entity_id, company_id=context["company"]
        )

        if not is_related:
            raise HTTPException(
                status_code=403,
                detail="Вы не можете изменять юридические лица другой компании",
            )

        return context

    return Depends(dependency)


def with_permission_and_legal_entity_company_check(permission: str):
    async def dependency(
        relation_id: UUID = Path(..., description="ID связи компании и юрлица"),
        context: dict = Depends(require_permission_in_context(permission)),
    ):
        if context.get("is_superadmin"):
            return context

        relation = await EntityCompanyRelation.get_or_none(
            id=relation_id
        ).prefetch_related("company")

        if not relation or str(relation.company_id) != str(context["company"]):
            raise HTTPException(
                status_code=403,
                detail="Связь не принадлежит компании пользователя или не найдена",
            )

        return context

    return Depends(dependency)
