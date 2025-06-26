from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "legal_entities" ALTER COLUMN "ogrn" TYPE VARCHAR(15) USING "ogrn"::VARCHAR(15);
        CREATE TABLE IF NOT EXISTS "warehouses" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" VARCHAR(255),
    "company_id" UUID NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by" UUID NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "modified_by" UUID NOT NULL
);
        DROP TABLE IF EXISTS "storages";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "legal_entities" ALTER COLUMN "ogrn" TYPE VARCHAR(13) USING "ogrn"::VARCHAR(13);
        DROP TABLE IF EXISTS "warehouses";"""
