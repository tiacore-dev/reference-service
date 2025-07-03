from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cities" ALTER COLUMN "code" DROP NOT NULL;
        ALTER TABLE "cities" ALTER COLUMN "external_id" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cities" ALTER COLUMN "code" SET NOT NULL;
        ALTER TABLE "cities" ALTER COLUMN "external_id" SET NOT NULL;"""
