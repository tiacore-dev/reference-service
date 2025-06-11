from uuid import uuid4

import pytest

from app.database.models import CashRegister, City, Storage


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_cash_register():
    cash_register = await CashRegister.create(
        name="Test Register",
        created_by=uuid4(),
        modified_by=uuid4(),
        company_id=uuid4(),
    )

    return cash_register


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_storage():
    storage = await Storage.create(
        name="Test Storage", created_by=uuid4(), modified_by=uuid4(), company_id=uuid4()
    )

    return storage


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_city():
    city = await City.create(
        name="Test City", code="666666", region="Nsk", external_id="0000000000"
    )

    return city
