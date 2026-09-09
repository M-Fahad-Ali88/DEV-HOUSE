import asyncio
from urllib.parse import quote_plus

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

DB_PASSWORD = "fahad@3549"

DATABASE_URL = (
    f"postgresql+asyncpg://postgres:{quote_plus(DB_PASSWORD)}"
    "@127.0.0.1:5432/event_analytics"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def test_connection():
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        print("Database connection successful!")
        print("Test result:", result.scalar())


async def main():
    try:
        await test_connection()
    except Exception as e:
        print("Database connection failed!")
        print("Error:", e)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())