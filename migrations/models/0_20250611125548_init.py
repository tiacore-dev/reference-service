from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "cash_registers" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "cities" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "region" VARCHAR(255) NOT NULL,
    "code" VARCHAR(20) NOT NULL,
    "external_id" VARCHAR(40) NOT NULL
);
CREATE TABLE IF NOT EXISTS "legal_entity_types" (
    "id" VARCHAR(255) NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "legal_entities" (
    "id" UUID NOT NULL PRIMARY KEY,
    "full_name" VARCHAR(255),
    "short_name" VARCHAR(255) NOT NULL,
    "inn" VARCHAR(12) NOT NULL,
    "kpp" VARCHAR(9),
    "ogrn" VARCHAR(13) NOT NULL UNIQUE,
    "vat_rate" INT NOT NULL DEFAULT 0,
    "address" VARCHAR(255),
    "opf" VARCHAR(255),
    "signer" VARCHAR(255),
    "entity_type_id" VARCHAR(255) REFERENCES "legal_entity_types" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_legal_entit_inn_06a077" UNIQUE ("inn", "kpp")
);
CREATE TABLE IF NOT EXISTS "entity_company_relations" (
    "id" UUID NOT NULL PRIMARY KEY,
    "company_id" UUID NOT NULL,
    "relation_type" VARCHAR(10) NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "legal_entity_id" UUID NOT NULL REFERENCES "legal_entities" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "storages" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
