from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "warehouses" ADD "city_id" UUID NOT NULL;
        ALTER TABLE "warehouses" ADD CONSTRAINT "fk_warehous_cities" FOREIGN KEY ("city_id") REFERENCES "cities" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "warehouses" DROP CONSTRAINT "fk_warehous_cities";
        ALTER TABLE "warehouses" DROP COLUMN "city_id";"""
