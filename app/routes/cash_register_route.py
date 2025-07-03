from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from loguru import logger
from tiacore_lib.handlers.auth_handler import get_current_user
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.handlers.permissions_handler import (
    with_permission_and_company_from_body_check,
)
from tiacore_lib.utils.validate_helpers import validate_company_access
from tortoise.expressions import Q

from app.database.models import CashRegister
from app.pydantic_models.cash_register_models import (
    CashRegisterCreateSchema,
    CashRegisterEditSchema,
    CashRegisterListResponseSchema,
    CashRegisterResponseSchema,
    CashRegisterSchema,
    cash_register_filter_params,
)

cash_register_router = APIRouter()


# Чисто для коммита
@cash_register_router.post(
    "/add",
    response_model=CashRegisterResponseSchema,
    summary="Добавление новой кассы",
    status_code=status.HTTP_201_CREATED,
)
async def add_cash_register(
    data: CashRegisterCreateSchema = Body(...),
    context=Depends(with_permission_and_company_from_body_check("add_cash_register")),
):
    cash_register = await CashRegister.create(
        created_by=context["user_id"],
        modified_by=context["user_id"],
        **data.model_dump(exclude_unset=True),
    )
    if not cash_register:
        logger.error("Не удалось создать кассу")
        raise HTTPException(status_code=500, detail="Не удалось создать кассу")

    logger.success(f"касса {cash_register.name} ({cash_register.id}) успешно создана")
    return {"cash_register_id": str(cash_register.id)}


@cash_register_router.patch(
    "/{cash_register_id}",
    summary="Изменение кассы",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def edit_cash_register(
    cash_register_id: UUID = Path(
        ..., title="ID кассы", description="ID изменяемой кассы"
    ),
    data: CashRegisterEditSchema = Body(...),
    context=Depends(with_permission_and_company_from_body_check("edit_cash_register")),
):
    logger.info(f"Обновление кассы {cash_register_id}")

    cash_register = await CashRegister.filter(id=cash_register_id).first()
    if not cash_register:
        logger.warning(f"касса {cash_register_id} не найдена")
        raise HTTPException(status_code=404, detail="касса не найдена")
    validate_company_access(cash_register, context, "кассой")

    cash_register.modified_by = context["user_id"]
    await cash_register.update_from_dict(data.model_dump(exclude_unset=True))

    await cash_register.save()


@cash_register_router.delete(
    "/{cash_register_id}",
    summary="Удаление кассы",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_cash_register(
    cash_register_id: UUID = Path(
        ..., title="ID кассы", description="ID удаляемой кассы"
    ),
    context=Depends(require_permission_in_context("delete_cash_register")),
):
    cash_register = await CashRegister.filter(id=cash_register_id).first()
    if not cash_register:
        logger.warning(f"касса {cash_register_id} не найдена")
        raise HTTPException(status_code=404, detail="касса не найдена")
    validate_company_access(cash_register, context, "кассой")
    await cash_register.delete()


@cash_register_router.get(
    "/all",
    response_model=CashRegisterListResponseSchema,
    summary="Получение списка кассов с фильтрацией",
)
async def get_cash_registers(
    filters: dict = Depends(cash_register_filter_params),
    context=Depends(get_current_user),
):
    query = Q()
    if not context["is_superadmin"]:
        query &= Q(company_id=context["company_id"])
    if filters.get("cash_register_name"):
        query &= Q(name__icontains=filters["cash_register_name"])
    if filters.get("description"):
        query &= Q(description__icontains=filters["description"])

    order_by = f"{'-' if filters.get('order') == 'desc' else ''}{
        filters.get('sort_by', 'name')
    }"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)

    total_count = await CashRegister.filter(query).count()

    cash_registers = (
        await CashRegister.filter(query)
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .values(
            "id",
            "name",
            "description",
            "created_at",
            "created_by",
            "modified_at",
            "modified_by",
            "company_id",
        )
    )

    return CashRegisterListResponseSchema(
        total=total_count,
        cash_registers=[
            CashRegisterSchema(**cash_register) for cash_register in cash_registers
        ],
    )


@cash_register_router.get(
    "/{cash_register_id}", response_model=CashRegisterSchema, summary="Просмотр кассы"
)
async def get_cash_register(
    cash_register_id: UUID = Path(
        ..., title="ID кассы", description="ID просматриваемой кассы"
    ),
    context=Depends(get_current_user),
):
    logger.info(f"Запрос на просмотр кассы: {cash_register_id}")
    cash_register = (
        await CashRegister.filter(id=cash_register_id)
        .first()
        .values(
            "id",
            "name",
            "description",
            "created_at",
            "created_by",
            "modified_at",
            "modified_by",
            "company_id",
        )
    )

    if cash_register is None:
        logger.warning(f"касса {cash_register_id} не найдена")
        raise HTTPException(status_code=404, detail="Касса не найдена")
    validate_company_access(cash_register, context, "кассой")

    cash_register_schema = CashRegisterSchema(**cash_register)

    logger.success(f"касса найдена: {cash_register_schema}")
    return cash_register_schema
