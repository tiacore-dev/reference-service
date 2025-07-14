from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "warehouses" ADD "address" VARCHAR(255)NOT NULL DEFAULT ' ';
        ALTER TABLE "warehouses" ALTER COLUMN "description" TYPE TEXT USING "description"::TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "warehouses" DROP COLUMN "address";
        ALTER TABLE "warehouses" ALTER COLUMN "description" TYPE VARCHAR(255) USING "description"::VARCHAR(255);"""
