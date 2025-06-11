from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import Storage


@pytest.mark.asyncio
async def test_add_storage(test_app: AsyncClient, jwt_token_admin: dict):
    """Тест добавления нового промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"storage_name": "Test Storage", "company_id": str(uuid4())}

    response = await test_app.post("/api/storages/add", headers=headers, json=data)
    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    storage = await Storage.filter(name="Test Storage").first()

    assert storage is not None, "Промпт не был сохранён в БД"
    assert response_data["storage_id"] == str(storage.id)


@pytest.mark.asyncio
async def test_edit_storage(
    test_app: AsyncClient, jwt_token_admin: dict, seed_storage: Storage
):
    """Тест редактирования промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "storage_name": "Updated Storage",
    }

    response = await test_app.patch(
        f"/api/storages/{seed_storage.id}", headers=headers, json=data
    )

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    storage = await Storage.filter(id=seed_storage.id).first()

    assert storage is not None, "Промпт не найден в базе"
    assert storage.name == "Updated Storage"


@pytest.mark.asyncio
async def test_view_storage(
    test_app: AsyncClient, jwt_token_admin: dict, seed_storage: Storage
):
    """Тест просмотра промпта по ID."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/storages/{seed_storage.id}", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    assert response_data["storage_id"] == str(seed_storage.id)
    assert response_data["storage_name"] == seed_storage.name


@pytest.mark.asyncio
async def test_delete_storage(
    test_app: AsyncClient, jwt_token_admin: dict, seed_storage: Storage
):
    """Тест удаления промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/storages/{seed_storage.id}", headers=headers
    )

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    storage = await Storage.filter(id=seed_storage.id).first()
    assert storage is None, "Промпт не был удалён из базы"


@pytest.mark.asyncio
async def test_get_storages(
    test_app: AsyncClient, jwt_token_admin: dict, seed_storage: Storage
):
    """Тест получения списка промптов с фильтрацией."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/storages/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    storages = response_data.get("storages")
    assert isinstance(storages, list), "Ответ должен быть списком"
    assert response_data.get("total") > 0

    storage_ids = [storage["storage_id"] for storage in storages]
    assert str(seed_storage.id) in storage_ids, "Тестовый промпт отсутствует в списке"
