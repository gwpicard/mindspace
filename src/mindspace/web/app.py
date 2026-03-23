"""FastAPI application factory."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from mindspace.infra.paths import ensure_dirs
from mindspace.web.db.engine import close_db, init_db
from mindspace.web import tasks as task_manager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: ensure dirs, create tables, migrate CLI data. Shutdown: cancel tasks, close DB."""
    ensure_dirs()
    await init_db()

    # Check for API key
    from mindspace.infra.config import get_settings
    settings = get_settings()
    if not settings.anthropic_api_key:
        logger.warning("ANTHROPIC_API_KEY not set — chat will not work. Add it to .env")

    # Auto-migrate CLI captures (idempotent)
    try:
        from mindspace.web.migrate_cli import run_migration
        await run_migration()
    except Exception as e:
        logger.warning("CLI migration skipped: %s", e)

    logger.info("Mindspace web app started")
    yield
    await task_manager.shutdown()
    await close_db()
    logger.info("Mindspace web app stopped")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Mindspace", version="0.1.0", lifespan=lifespan)

    # CORS for local dev (SvelteKit dev server)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    from mindspace.web.routers import conversations, channels, resources, search
    app.include_router(conversations.router)
    app.include_router(channels.router)
    app.include_router(resources.router)
    app.include_router(search.router)

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    # Test-only reset endpoint
    if os.environ.get("MINDSPACE_TEST_MODE") == "1":
        @app.post("/_test/reset", status_code=204)
        async def test_reset():
            from mindspace.web.db.models import Base
            from mindspace.web.db.engine import get_engine
            engine = get_engine()
            async with engine.begin() as conn:
                for table in reversed(Base.metadata.sorted_tables):
                    await conn.execute(table.delete())
            return Response(status_code=204)

    # Serve frontend static files (built SvelteKit SPA)
    frontend_dist = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"
    if frontend_dist.is_dir():
        app.mount("/_app", StaticFiles(directory=str(frontend_dist / "_app")), name="static_app")

        @app.get("/{path:path}")
        async def spa_fallback(request: Request, path: str):
            # Try to serve static file first
            file_path = frontend_dist / path
            if file_path.is_file():
                return FileResponse(str(file_path))
            # Fallback to index.html for SPA routing
            return FileResponse(str(frontend_dist / "index.html"))

    return app


def main() -> None:
    """Entry point for the mindspace-web command."""
    import argparse
    import uvicorn

    from mindspace.infra.config import get_settings

    parser = argparse.ArgumentParser(description="Mindspace Web Server")
    parser.add_argument("--host", default=None, help="Host to bind to")
    parser.add_argument("--port", type=int, default=None, help="Port to bind to")
    args = parser.parse_args()

    settings = get_settings()
    host = args.host or settings.server_host
    port = args.port or settings.server_port

    uvicorn.run(
        "mindspace.web.app:create_app",
        factory=True,
        host=host,
        port=port,
        reload=False,
    )
