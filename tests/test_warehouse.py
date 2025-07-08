from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import City, Warehouse


@pytest.mark.asyncio
async def test_add_warehouse(test_app: AsyncClient, jwt_token_admin: dict, seed_city: City):
    """Тест добавления нового промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"warehouse_name": "Test Warehouse", "company_id": str(uuid4()), "city_id": str(seed_city.id)}

    response = await test_app.post("/api/warehouses/add", headers=headers, json=data)
    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    warehouse = await Warehouse.filter(name="Test Warehouse").first()

    assert warehouse is not None, "Промпт не был сохранён в БД"
    assert response_data["warehouse_id"] == str(warehouse.id)


@pytest.mark.asyncio
async def test_edit_warehouse(test_app: AsyncClient, jwt_token_admin: dict, seed_warehouse: Warehouse):
    """Тест редактирования промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "warehouse_name": "Updated Warehouse",
    }

    response = await test_app.patch(f"/api/warehouses/{seed_warehouse.id}", headers=headers, json=data)

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    warehouse = await Warehouse.filter(id=seed_warehouse.id).first()

    assert warehouse is not None, "Промпт не найден в базе"
    assert warehouse.name == "Updated Warehouse"


@pytest.mark.asyncio
async def test_view_warehouse(test_app: AsyncClient, jwt_token_admin: dict, seed_warehouse: Warehouse):
    """Тест просмотра промпта по ID."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/warehouses/{seed_warehouse.id}", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    assert response_data["warehouse_id"] == str(seed_warehouse.id)
    assert response_data["warehouse_name"] == seed_warehouse.name


@pytest.mark.asyncio
async def test_delete_warehouse(test_app: AsyncClient, jwt_token_admin: dict, seed_warehouse: Warehouse):
    """Тест удаления промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(f"/api/warehouses/{seed_warehouse.id}", headers=headers)

    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"

    warehouse = await Warehouse.filter(id=seed_warehouse.id).first()
    assert warehouse is None, "Промпт не был удалён из базы"


@pytest.mark.asyncio
async def test_get_warehouses(test_app: AsyncClient, jwt_token_admin: dict, seed_warehouse: Warehouse):
    """Тест получения списка промптов с фильтрацией."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/warehouses/all", headers=headers)

    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"

    response_data = response.json()
    warehouses = response_data.get("warehouses")
    assert isinstance(warehouses, list), "Ответ должен быть списком"
    assert response_data.get("total") > 0

    warehouse_ids = [warehouse["warehouse_id"] for warehouse in warehouses]
    assert str(seed_warehouse.id) in warehouse_ids, "Тестовый промпт отсутствует в списке"
