from tortoise import Tortoise
from tortoise.transactions import in_transaction

from app.database.models import LegalEntity


async def drop_all_tables():
    conn = Tortoise.get_connection("default")
    tables = await conn.execute_query_dict("""
        SELECT tablename FROM pg_tables WHERE schemaname = 'public';
    """)
    async with in_transaction() as tx:
        for table in tables:
            await tx.execute_query(
                f'DROP TABLE IF EXISTS "{table["tablename"]}" CASCADE;'
            )


async def get_entities_by_query(query):
    total_count = await LegalEntity.filter(query).count()
    entities = (
        await LegalEntity.filter(query)
        .prefetch_related("entity_type", "entity_company_relations")
        .all()
        .values(
            "id",
            "full_name",
            "short_name",
            "inn",
            "kpp",
            "opf",
            "vat_rate",
            "address",
            "entity_type_id",
            "signer",
            "ogrn",
        )
    )
    return total_count, entities
