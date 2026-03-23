"""Simple asyncio background task manager."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Coroutine
from typing import Any

logger = logging.getLogger(__name__)

_tasks: set[asyncio.Task] = set()


def submit(coro: Coroutine[Any, Any, Any], name: str | None = None) -> asyncio.Task:
    """Submit a coroutine as a background task."""
    task = asyncio.create_task(coro, name=name)
    _tasks.add(task)
    task.add_done_callback(_on_done)
    return task


def _on_done(task: asyncio.Task) -> None:
    _tasks.discard(task)
    if task.cancelled():
        logger.debug("Task %s cancelled", task.get_name())
    elif exc := task.exception():
        logger.error("Task %s failed: %s", task.get_name(), exc, exc_info=exc)
    else:
        logger.debug("Task %s completed", task.get_name())


async def shutdown() -> None:
    """Cancel all running tasks and wait for them to finish."""
    if not _tasks:
        return
    for task in _tasks:
        task.cancel()
    await asyncio.gather(*_tasks, return_exceptions=True)
    _tasks.clear()
