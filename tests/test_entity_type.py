import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_legal_entity_types(
    seed_legal_entity_type, test_app: AsyncClient, jwt_token_admin
):
    """Тест получения всех типов юр. лиц."""
    headers = {"Authorization": f"Bearer {jwt_token_admin['access_token']}"}
    response = await test_app.get("/api/legal-entity-types/all", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert {item["entity_type_name"] for item in data["legal_entity_types"]} == {"ООО"}
