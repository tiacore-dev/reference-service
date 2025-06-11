from uuid import uuid4

import pytest

from app.database.models import (
    EntityCompanyRelation,
    LegalEntity,
    LegalEntityType,
)


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_legal_entity_type():
    """Создает тестовый тип юридического лица."""
    entity_type = await LegalEntityType.create(id="ooo", name="ООО")
    return entity_type


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_legal_entity(seed_legal_entity_type: LegalEntityType):
    entity_type = await LegalEntityType.get_or_none(id=seed_legal_entity_type.id)

    if not entity_type:
        raise ValueError(
            "Ошибка: Не удалось получить объекты Company или LegalEntityType"
        )

    legal_entity = await LegalEntity.create(
        short_name="Test Legal Entity",
        inn="1234567890",
        kpp="123456789",
        vat_rate=20,
        ogrn="1027700132195",
        address="Test Address",
        entity_type=entity_type,
        signer="Test Signer",
    )

    # Создаем связь entity ↔ company
    await EntityCompanyRelation.create(
        company_id=uuid4(),
        legal_entity=legal_entity,
        relation_type="seller",
    )

    return legal_entity


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_legal_entity_buyer(seed_legal_entity_type: LegalEntityType):
    """Создает тестовое юридическое лицо, передавая объекты вместо ID."""

    entity_type = await LegalEntityType.get_or_none(id=seed_legal_entity_type.id)

    if not entity_type:
        raise ValueError(
            "Ошибка: Не удалось получить объекты Company или LegalEntityType"
        )

    # Создаем юридическое лицо, передавая объекты
    legal_entity = await LegalEntity.create(
        short_name="Test Legal Entity Buyer",
        inn="123456789013",
        kpp="123456789",
        vat_rate=20,
        ogrn="1027700132185",
        address="Test Address",
        entity_type=entity_type,
        signer="Test Signer",
    )

    await EntityCompanyRelation.create(
        legal_entity=legal_entity, company_id=uuid4(), relation_type="buyer"
    )

    return legal_entity


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_entity_relation(seed_legal_entity: LegalEntity):
    entity = await LegalEntity.get_or_none(id=seed_legal_entity.id)

    relation = await EntityCompanyRelation.create(
        company_id=uuid4(), legal_entity=entity, relation_type="buyer"
    )
    return relation
