from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """

        ALTER TABLE "legal_entities" DROP COLUMN "entity_type_id";
        DROP TABLE IF EXISTS "legal_entity_types";
        DROP TABLE IF EXISTS "entity_company_relations";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "legal_entities" ADD "entity_type_id" VARCHAR(255);
        ALTER TABLE "legal_entities" ADD CONSTRAINT "fk_legal_entity" FOREIGN KEY ("entity_type_id") REFERENCES "legal_entity_types" ("id") ON DELETE CASCADE;"""
