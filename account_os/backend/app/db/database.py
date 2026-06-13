from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
import os

# Use environment variable for DB URL or default to a local sqlite for testing if needed
# In production, this would be a PostgreSQL URL: postgresql+asyncpg://user:pass@host/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./account_os.db")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def get_db_context(user_email: str = None):
    """
    Async context manager for database sessions.
    Optionally sets the RLS context for PostgreSQL.
    """
    async with AsyncSessionLocal() as session:
        try:
            if user_email and "postgresql" in DATABASE_URL:
                from sqlalchemy import text
                await session.execute(text(f"SET app.current_user_email = :email"), {"email": user_email})
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
