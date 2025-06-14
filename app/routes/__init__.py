from fastapi import FastAPI
from tiacore_lib.routes.auth_route import auth_router

from .cash_register_route import cash_register_router
from .city_route import city_router
from .entity_company_relation_route import entity_relation_router
from .entity_type_route import entity_types_router
from .legal_entity_route import entity_router
from .monitoring_route import monitoring_router
from .storage_route import storage_router


def register_routes(app: FastAPI):
    app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
    app.include_router(
        cash_register_router, prefix="/api/cash-registers", tags=["CashRegisters"]
    )
    app.include_router(storage_router, prefix="/api/storages", tags=["Storage"])
    app.include_router(city_router, prefix="/api/cities", tags=["Cities"])
    app.include_router(monitoring_router, tags=["Monitoring"])
    app.include_router(
        entity_types_router, prefix="/api/legal-entity-types", tags=["LegalEntityTypes"]
    )
    app.include_router(
        entity_router, prefix="/api/legal-entities", tags=["LegalEntities"]
    )
    app.include_router(
        entity_relation_router,
        prefix="/api/entity-company-relations",
        tags=["EntityCompanyRelations"],
    )
