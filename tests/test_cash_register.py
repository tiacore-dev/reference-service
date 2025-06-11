from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import CashRegister


@pytest.mark.asyncio
async def test_add_cash_register(test_app: AsyncClient, jwt_token_admin: dict):
    """Тест добавления нового промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"cash_register_name": "Test CashRegister", "company_id": str(uuid4())}

    response = await test_app.post(
        "/api/cash-registers/add", headers=headers, json=data
    )
    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    cash_register = await CashRegister.filter(name="Test CashRegister").first()

    assert cash_register is not None, "Промпт не был сохранён в БД"
    assert response_data["cash_register_id"] == str(cash_register.id)


@pytest.mark.asyncio
async def test_edit_cash_register(
    test_app: AsyncClient, jwt_token_admin: dict, seed_cash_register: CashRegister
):
    """Тест редактирования промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"cash_register_name": "Updated CashRegister"}

    response = await test_app.patch(
        f"/api/cash-registers/{seed_cash_register.id}", headers=headers, json=data
    )

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    cash_register = await CashRegister.filter(id=seed_cash_register.id).first()

    assert cash_register is not None, "Промпт не найден в базе"
    assert cash_register.name == "Updated CashRegister"


@pytest.mark.asyncio
async def test_view_cash_register(
    test_app: AsyncClient, jwt_token_admin: dict, seed_cash_register: CashRegister
):
    """Тест просмотра промпта по ID."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(
        f"/api/cash-registers/{seed_cash_register.id}", headers=headers
    )

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    assert response_data["cash_register_id"] == str(seed_cash_register.id)
    assert response_data["cash_register_name"] == seed_cash_register.name


@pytest.mark.asyncio
async def test_delete_cash_register(
    test_app: AsyncClient, jwt_token_admin: dict, seed_cash_register: CashRegister
):
    """Тест удаления промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/cash-registers/{seed_cash_register.id}", headers=headers
    )

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    cash_register = await CashRegister.filter(id=seed_cash_register.id).first()
    assert cash_register is None, "Промпт не был удалён из базы"


@pytest.mark.asyncio
async def test_get_cash_registers(
    test_app: AsyncClient, jwt_token_admin: dict, seed_cash_register: CashRegister
):
    """Тест получения списка промптов с фильтрацией."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/cash-registers/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    cash_registers = response_data.get("cash_registers")
    assert isinstance(cash_registers, list), "Ответ должен быть списком"
    assert response_data.get("total") > 0

    cash_register_ids = [
        cash_register["cash_register_id"] for cash_register in cash_registers
    ]
    assert str(seed_cash_register.id) in cash_register_ids, (
        "Тестовый промпт отсутствует в списке"
    )
