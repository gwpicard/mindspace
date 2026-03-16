"""CLI commands for searching and browsing captures."""

import json
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from mindspace.capture import store
from mindspace.derived.embeddings import EmbeddingPipeline

search_app = typer.Typer(no_args_is_help=True)
console = Console()

MIN_RELEVANCE_SCORE = 0.20


@search_app.command("query")
def search_query(
    query_text: str = typer.Argument(help="Search query"),
    num: int = typer.Option(5, "--num", "-n", help="Number of results"),
    all: bool = typer.Option(False, "--all", help="Show all results (ignore relevance threshold)"),
) -> None:
    """Semantic search across all captures."""
    pipeline = EmbeddingPipeline()
    results = pipeline.search(query_text, n_results=num)

    if not results:
        console.print("[dim]No results found.[/dim]")
        return

    # Filter by relevance unless --all
    if not all:
        results = [r for r in results if (1 - r["distance"]) >= MIN_RELEVANCE_SCORE]

    if not results:
        console.print("[dim]No relevant results found.[/dim] Use [bold]--all[/bold] to see low-relevance matches.")
        return

    console.print()
    for i, hit in enumerate(results):
        score = 1 - hit["distance"]
        ctype = hit["metadata"].get("type", "")
        tags = hit["metadata"].get("tags", "")
        doc = hit["document"]

        # Truncate preview to ~200 chars at a word boundary
        if len(doc) > 200:
            preview = doc[:200].rsplit(" ", 1)[0] + "..."
        else:
            preview = doc

        # Score color
        if score >= 0.5:
            score_style = "green bold"
        elif score >= 0.3:
            score_style = "yellow"
        else:
            score_style = "dim"

        # Header line
        console.print(
            f"  [{score_style}]{score:.0%}[/{score_style}]  "
            f"[bold]{ctype}[/bold]  "
            f"[dim]{hit['id']}[/dim]"
            + (f"  [cyan]#{tags.replace(',', ' #')}[/cyan]" if tags else "")
        )
        # Preview
        console.print(f"       {preview}")
        if i < len(results) - 1:
            console.print()

    console.print()


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
