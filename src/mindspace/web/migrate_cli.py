"""One-time migration of CLI captures into the web app's SQLite database."""

from __future__ import annotations

import json
import logging

from mindspace.core.ids import generate_id
from mindspace.web.db.engine import get_session_factory
from mindspace.web.db.models import Resource

logger = logging.getLogger(__name__)


async def run_migration() -> None:
    """Import existing CLI captures as Resource records in SQLite.

    Existing ChromaDB embeddings in the "captures" collection remain valid
    and are searched alongside conversation_chunks by the search service.
    This migration just makes CLI captures visible in the resource list.
    """
    from mindspace.capture.store import iterate_all

    factory = get_session_factory()
    async with factory() as db:
        # Load existing resource IDs with cli_capture_id to avoid re-importing
        from sqlalchemy import select
        result = await db.execute(select(Resource))
        existing = set()
        for r in result.scalars().all():
            if r.metadata_json:
                meta = json.loads(r.metadata_json)
                if cid := meta.get("cli_capture_id"):
                    existing.add(cid)

        captures = iterate_all()
        imported = 0
        skipped = 0

        for capture in captures:
            if capture.id in existing:
                skipped += 1
                continue

            content_data = capture.content.model_dump(mode="json")
            source_url = content_data.get("url")
            title = content_data.get("title") or content_data.get("text", "")[:80]
            raw_content = capture.text_for_embedding()

            resource = Resource(
                id=generate_id(),
                type=capture.type.value,
                source_url=source_url,
                title=title,
                raw_content=raw_content,
                metadata_json=json.dumps({
                    "cli_capture_id": capture.id,
                    "stream": capture.stream.value,
                    "tags": capture.context.tags,
                    "created_at": capture.created_at.isoformat(),
                }),
                processing_status="completed",
                is_embedded=True,  # Already in ChromaDB "captures" collection
                created_at=capture.created_at,
            )
            db.add(resource)
            imported += 1

        await db.commit()

    logger.info("CLI migration complete: %d imported, %d skipped", imported, skipped)
