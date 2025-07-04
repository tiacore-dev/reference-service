from fastapi import FastAPI
from tiacore_lib.routes.company_route import company_router
from tiacore_lib.routes.user_route import user_router

from .cash_register_route import cash_register_router
from .city_route import city_router
from .legal_entity_route import entity_router
from .monitoring_route import monitoring_router
from .warehouse_route import warehouse_router


def register_routes(app: FastAPI):
    app.include_router(user_router, prefix="/api/users", tags=["Users"])
    app.include_router(company_router, prefix="/api/companies", tags=["Companies"])
    app.include_router(
        cash_register_router, prefix="/api/cash-registers", tags=["CashRegisters"]
    )
    app.include_router(warehouse_router, prefix="/api/warehouses", tags=["Warehouse"])
    app.include_router(city_router, prefix="/api/cities", tags=["Cities"])
    app.include_router(monitoring_router, tags=["Monitoring"])

    app.include_router(
        entity_router, prefix="/api/legal-entities", tags=["LegalEntities"]
    )
