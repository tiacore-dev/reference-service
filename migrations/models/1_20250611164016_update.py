from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cash_registers" ADD "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "cash_registers" ADD "created_by" UUID NOT NULL;
        ALTER TABLE "cash_registers" ADD "modified_by" UUID NOT NULL;
        ALTER TABLE "cash_registers" ADD "company_id" UUID NOT NULL;
        ALTER TABLE "cash_registers" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "storages" ADD "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "storages" ADD "created_by" UUID NOT NULL;
        ALTER TABLE "storages" ADD "modified_by" UUID NOT NULL;
        ALTER TABLE "storages" ADD "company_id" UUID NOT NULL;
        ALTER TABLE "storages" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "storages" DROP COLUMN "modified_at";
        ALTER TABLE "storages" DROP COLUMN "created_by";
        ALTER TABLE "storages" DROP COLUMN "modified_by";
        ALTER TABLE "storages" DROP COLUMN "company_id";
        ALTER TABLE "storages" DROP COLUMN "created_at";
        ALTER TABLE "cash_registers" DROP COLUMN "modified_at";
        ALTER TABLE "cash_registers" DROP COLUMN "created_by";
        ALTER TABLE "cash_registers" DROP COLUMN "modified_by";
        ALTER TABLE "cash_registers" DROP COLUMN "company_id";
        ALTER TABLE "cash_registers" DROP COLUMN "created_at";"""
