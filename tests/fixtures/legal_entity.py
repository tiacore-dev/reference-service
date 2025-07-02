import pytest

from app.database.models import (
    LegalEntity,
)


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_legal_entity():
    legal_entity = await LegalEntity.create(
        short_name="Test Legal Entity",
        inn="1234567890",
        kpp="123456789",
        vat_rate=20,
        ogrn="1027700132195",
        address="Test Address",
        signer="Test Signer",
    )

    return legal_entity


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_legal_entity_buyer():
    """Создает тестовое юридическое лицо, передавая объекты вместо ID."""

    # Создаем юридическое лицо, передавая объекты
    legal_entity = await LegalEntity.create(
        short_name="Test Legal Entity Buyer",
        inn="123456789013",
        kpp="123456789",
        vat_rate=20,
        ogrn="1027700132185",
        address="Test Address",
        signer="Test Signer",
    )

    return legal_entity
