from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "legal_entities" 
        ALTER COLUMN "ogrn" TYPE VARCHAR(15) 
        USING "ogrn"::VARCHAR(15);
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "legal_entities" 
        ALTER COLUMN "ogrn" TYPE VARCHAR(13) 
        USING "ogrn"::VARCHAR(13);
    """
