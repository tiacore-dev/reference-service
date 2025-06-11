from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.database.models import LegalEntity, LegalEntityType


@pytest.mark.asyncio
async def test_add_legal_entity(
    test_app: AsyncClient,
    jwt_token_admin: dict,
    seed_legal_entity_type: LegalEntityType,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    short_name = "Новая организация"
    data = {
        "short_name": short_name,
        "inn": "999999999999",
        "kpp": "123456789",
        "vat_rate": 20,
        "address": "Где-то в России",
        "ogrn": "1027700132185",
        "entity_type": str(seed_legal_entity_type.id),
        "signer": "Директор Директорыч",
        "relation_type": "buyer",
        "company_id": str(uuid4()),
    }

    response = await test_app.post(
        "/api/legal-entities/add",
        headers=headers,
        json=data,
    )

    assert response.status_code == 201, f"{response.status_code=} {response.text=}"
    json_data = response.json()
    assert "legal_entity_id" in json_data

    # Проверка, что созданный объект действительно есть в базе
    created_entity = await LegalEntity.get_or_none(short_name=short_name)
    assert created_entity is not None, "Юридическое лицо не найдено в базе"
    assert str(created_entity.id) == json_data["legal_entity_id"]
    assert created_entity.inn == data["inn"]
    assert created_entity.kpp == data["kpp"]
    assert created_entity.address == data["address"]


@pytest.mark.asyncio
async def test_edit_legal_entity(
    test_app: AsyncClient,
    jwt_token_admin: dict,
    seed_legal_entity: LegalEntity,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    new_data = {
        "short_name": "Обновлённое имя",
        "address": "Новый адрес",
        "description": "Новое описание",
    }

    response = await test_app.patch(
        f"/api/legal-entities/{seed_legal_entity.id}",
        headers=headers,
        json=new_data,
    )

    assert response.status_code == 200
    updated = await LegalEntity.get(id=seed_legal_entity.id)
    assert updated.short_name == new_data["short_name"]
    assert updated.address == new_data["address"]


@pytest.mark.asyncio
async def test_view_legal_entity(
    test_app: AsyncClient,
    jwt_token_admin: dict,
    seed_legal_entity: LegalEntity,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get(
        f"/api/legal-entities/{seed_legal_entity.id}",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["legal_entity_id"] == str(seed_legal_entity.id)
    assert data["short_name"] == seed_legal_entity.short_name


@pytest.mark.asyncio
async def test_delete_legal_entity(
    test_app: AsyncClient,
    jwt_token_admin: dict,
    seed_legal_entity: LegalEntity,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.delete(
        f"/api/legal-entities/{seed_legal_entity.id}",
        headers=headers,
    )

    assert response.status_code == 204
    assert await LegalEntity.get_or_none(id=seed_legal_entity.id) is None


@pytest.mark.asyncio
async def test_get_legal_entities(
    test_app: AsyncClient,
    jwt_token_admin: dict,
    seed_legal_entity: LegalEntity,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/legal-entities/all", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(
        item["legal_entity_id"] == str(seed_legal_entity.id)
        for item in data["entities"]
    )


@pytest.mark.asyncio
async def test_add_legal_entity_by_inn(
    test_app: AsyncClient,
    jwt_token_admin: dict,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    data = {
        "inn": "5406989176",
        "company_id": str(uuid4()),
        "relation_type": "buyer",
    }

    response = await test_app.post(
        "/api/legal-entities/add-by-inn", headers=headers, json=data
    )

    assert response.status_code == 201, f"{response.status_code=} {response.text=}"
    assert "legal_entity_id" in response.json()


@pytest.mark.asyncio
async def test_get_buyers(
    test_app: AsyncClient,
    jwt_token_admin: dict,
    seed_legal_entity_buyer: LegalEntity,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/legal-entities/get-buyers", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(
        e["legal_entity_id"] == str(seed_legal_entity_buyer.id)
        for e in data["entities"]
    )


@pytest.mark.asyncio
async def test_get_sellers(
    test_app: AsyncClient,
    jwt_token_admin: dict,
    seed_legal_entity: LegalEntity,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}

    response = await test_app.get("/api/legal-entities/get-sellers", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(
        e["legal_entity_id"] == str(seed_legal_entity.id) for e in data["entities"]
    )


@pytest.mark.asyncio
async def test_get_legal_entity_by_inn_kpp(
    test_app: AsyncClient,
    jwt_token_admin: dict,
    seed_legal_entity: LegalEntity,
):
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    params = {"inn": seed_legal_entity.inn, "kpp": seed_legal_entity.kpp}

    response = await test_app.get(
        "/api/legal-entities/inn-kpp", headers=headers, params=params
    )

    assert response.status_code == 200
    data = response.json()
    assert data["legal_entity_id"] == str(seed_legal_entity.id)
