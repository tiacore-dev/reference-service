from uuid import uuid4

import pytest

from app.database.models import CashRegister, City, Warehouse


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
async def seed_warehouse():
    warehouse = await Warehouse.create(
        name="Test Warehouse",
        created_by=uuid4(),
        modified_by=uuid4(),
        company_id=uuid4(),
    )

    return warehouse


@pytest.mark.usefixtures("setup_db")
@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def seed_city():
    city = await City.create(
        name="Test City", code="666666", region="Nsk", external_id="0000000000"
    )

    return city
