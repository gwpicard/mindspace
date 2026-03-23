"""FastAPI dependency injection."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from mindspace.web.db.engine import get_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    factory = get_session_factory()
    async with factory() as session:
        yield session
