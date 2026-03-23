"""Async SQLAlchemy engine and session factory."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from mindspace.infra.paths import db_path

_engine = None
_session_factory = None


def get_engine():
    """Get or create the async engine (singleton)."""
    global _engine
    if _engine is None:
        url = f"sqlite+aiosqlite:///{db_path()}"
        _engine = create_async_engine(url, echo=False)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the session factory (singleton)."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


async def init_db():
    """Create all tables and enable WAL mode."""
    from mindspace.web.db.models import Base

    engine = get_engine()

    # Enable WAL mode for concurrent reads during background writes
    async with engine.begin() as conn:
        await conn.exec_driver_sql("PRAGMA journal_mode=WAL")
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Dispose the engine."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
