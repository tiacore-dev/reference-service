import pytest
from httpx import AsyncClient

from app.database.models import City


@pytest.mark.asyncio
async def test_add_city(test_app: AsyncClient, jwt_token_admin: dict):
    """Тест добавления нового промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "city_name": "Test City",
        "region": "Test Region",
        "code": "66666",
        "external_id": "1111",
    }

    response = await test_app.post("/api/cities/add", headers=headers, json=data)
    assert response.status_code == 201, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    city = await City.filter(name="Test City").first()

    assert city is not None, "Промпт не был сохранён в БД"
    assert response_data["city_id"] == str(city.id)


@pytest.mark.asyncio
async def test_edit_city(test_app: AsyncClient, jwt_token_admin: dict, seed_city: City):
    """Тест редактирования промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {"city_name": "Updated City"}

    response = await test_app.patch(
        f"/api/cities/{seed_city.id}", headers=headers, json=data
    )

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    city = await City.filter(id=seed_city.id).first()

    assert city is not None, "Промпт не найден в базе"
    assert city.name == "Updated City"


@pytest.mark.asyncio
async def test_view_city(test_app: AsyncClient, jwt_token_admin: dict, seed_city: City):
    """Тест просмотра промпта по ID."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(f"/api/cities/{seed_city.id}", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    assert response_data["city_id"] == str(seed_city.id)
    assert response_data["city_name"] == seed_city.name


@pytest.mark.asyncio
async def test_delete_city(
    test_app: AsyncClient, jwt_token_admin: dict, seed_city: City
):
    """Тест удаления промпта."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(f"/api/cities/{seed_city.id}", headers=headers)

    assert response.status_code == 204, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    city = await City.filter(id=seed_city.id).first()
    assert city is None, "Промпт не был удалён из базы"


@pytest.mark.asyncio
async def test_get_cities(
    test_app: AsyncClient, jwt_token_admin: dict, seed_city: City
):
    """Тест получения списка промптов с фильтрацией."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/cities/all", headers=headers)

    assert response.status_code == 200, (
        f"Ошибка: {response.status_code}, {response.text}"
    )

    response_data = response.json()
    cities = response_data.get("cities")
    assert isinstance(cities, list), "Ответ должен быть списком"
    assert response_data.get("total") > 0

    city_ids = [city["city_id"] for city in cities]
    assert str(seed_city.id) in city_ids, "Тестовый промпт отсутствует в списке"
