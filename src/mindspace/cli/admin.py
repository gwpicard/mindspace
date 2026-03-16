"""CLI commands for administration and maintenance."""

import typer
from rich.console import Console
from rich.table import Table

from mindspace.capture import store
from mindspace.derived.registry import DerivationRegistry
from mindspace.infra.paths import ensure_dirs, data_root
from mindspace.infra.vectordb import VectorDB
from mindspace.pipelines.reindex import reindex
from mindspace.pipelines.reprocess import reprocess

admin_app = typer.Typer(no_args_is_help=True)
console = Console()


@admin_app.command("init")
def admin_init() -> None:
    """Create data directories."""
    ensure_dirs()
    console.print(f"[green]Initialized[/green] data directory at {data_root()}")


@admin_app.command("stats")
def admin_stats() -> None:
    """Show corpus statistics."""
    total = store.count()
    by_type = store.count_by_type()
    by_stream = store.count_by_stream()

    try:
        vectordb = VectorDB()
        embedded = vectordb.count()
    except Exception:
        embedded = 0

    try:
        registry = DerivationRegistry()
        registered = registry.count_embedded()
    except Exception:
        registered = 0

    table = Table(title="Corpus Statistics")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total captures", str(total))
    table.add_row("Embedded", str(embedded))
    table.add_row("", "")

    for stream, count in sorted(by_stream.items()):
        table.add_row(f"Stream: {stream}", str(count))

    for ctype, count in sorted(by_type.items()):
        table.add_row(f"Type: {ctype}", str(count))

    console.print(table)


@admin_app.command("reindex")
def admin_reindex() -> None:
    """Wipe all embeddings and re-derive from raw captures."""
    with console.status("Reindexing all captures..."):
        stats = reindex()
    console.print(f"[green]Reindexed:[/green] {stats['embedded']} embedded, {stats['skipped']} skipped (of {stats['total']} total)")


@admin_app.command("reprocess")
def admin_reprocess() -> None:
    """Re-extract content for all captures and rebuild embeddings."""
    with console.status("Reprocessing all captures..."):
        stats = reprocess()
    console.print(
        f"[green]Reprocessed:[/green] {stats['enriched']} enriched, "
        f"{stats['skipped']} skipped (of {stats['total']} total)"
    )
    if "reindex" in stats:
        ri = stats["reindex"]
        console.print(
            f"[green]Reindexed:[/green] {ri['embedded']} embedded, "
            f"{ri['skipped']} skipped"
        )
