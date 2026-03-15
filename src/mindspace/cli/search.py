"""CLI commands for searching and browsing captures."""

import json
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mindspace.capture import store
from mindspace.derived.embeddings import EmbeddingPipeline

search_app = typer.Typer(no_args_is_help=True)
console = Console()


@search_app.command("query")
def search_query(
    query_text: str = typer.Argument(help="Search query"),
    num: int = typer.Option(5, "--num", "-n", help="Number of results"),
) -> None:
    """Semantic search across all captures."""
    pipeline = EmbeddingPipeline()
    results = pipeline.search(query_text, n_results=num)

    if not results:
        console.print("[dim]No results found.[/dim]")
        return

    table = Table(title=f"Results for: {query_text}")
    table.add_column("ID", style="dim", width=28)
    table.add_column("Type", width=10)
    table.add_column("Score", width=8)
    table.add_column("Preview", overflow="fold")

    for hit in results:
        score = f"{1 - hit['distance']:.3f}"
        preview = hit["document"][:120] + "..." if len(hit["document"]) > 120 else hit["document"]
        table.add_row(
            hit["id"],
            hit["metadata"].get("type", ""),
            score,
            preview,
        )

    console.print(table)


@search_app.command("show")
def search_show(
    capture_id: str = typer.Argument(help="Capture ID to display"),
) -> None:
    """Display full details of a capture."""
    try:
        capture = store.load(capture_id)
    except FileNotFoundError:
        console.print(f"[red]Capture {capture_id} not found[/red]")
        raise typer.Exit(1)

    data = capture.model_dump(mode="json")
    formatted = json.dumps(data, indent=2, ensure_ascii=False)

    title = f"{capture.type.value} ({capture.stream.value})"
    console.print(Panel(formatted, title=title, subtitle=capture.id))
