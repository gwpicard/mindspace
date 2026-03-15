"""CLI commands for capturing content."""

import os
import subprocess
import tempfile
from typing import Optional

import typer
from rich.console import Console

from mindspace.pipelines import ingest

capture_app = typer.Typer(no_args_is_help=True)
console = Console()


def _parse_tags(tag: list[str] | None) -> list[str]:
    return tag if tag else []


@capture_app.command()
def url(
    target_url: str = typer.Argument(help="URL to capture"),
    tag: Optional[list[str]] = typer.Option(None, "--tag", "-t", help="Tags"),
) -> None:
    """Capture a URL (auto-extracts content)."""
    with console.status("Extracting and embedding..."):
        capture = ingest.ingest_url(target_url, tags=_parse_tags(tag))
    console.print(f"[green]Captured[/green] {capture.type.value} [dim]{capture.id}[/dim]")
    if hasattr(capture.content, "title") and capture.content.title:
        console.print(f"  Title: {capture.content.title}")
    if hasattr(capture.content, "word_count") and capture.content.word_count:
        console.print(f"  Words: {capture.content.word_count}")


@capture_app.command()
def snippet(
    text: str = typer.Option(..., "--text", help="Snippet text"),
    source: Optional[str] = typer.Option(None, "--source", help="Source description"),
    source_url: Optional[str] = typer.Option(None, "--source-url", help="Source URL"),
    tag: Optional[list[str]] = typer.Option(None, "--tag", "-t", help="Tags"),
) -> None:
    """Capture a text snippet."""
    capture = ingest.ingest_snippet(
        text=text,
        source_description=source,
        source_url=source_url,
        tags=_parse_tags(tag),
    )
    console.print(f"[green]Captured[/green] snippet [dim]{capture.id}[/dim]")


@capture_app.command()
def thought(
    text: Optional[str] = typer.Option(None, "--text", help="Thought text (opens $EDITOR if omitted)"),
    thinking_type: str = typer.Option("observation", "--type", help="Type: reflection|hypothesis|synthesis|observation|prediction"),
    tag: Optional[list[str]] = typer.Option(None, "--tag", "-t", help="Tags"),
) -> None:
    """Capture a thought."""
    if text is None:
        text = _editor_input()
        if not text:
            console.print("[red]No text provided, aborting.[/red]")
            raise typer.Exit(1)
    capture = ingest.ingest_thought(text=text, thinking_type=thinking_type, tags=_parse_tags(tag))
    console.print(f"[green]Captured[/green] thought [dim]{capture.id}[/dim]")


@capture_app.command()
def question(
    text: str = typer.Argument(help="Question text"),
    domain: Optional[str] = typer.Option(None, "--domain", help="Domain/topic"),
    urgency: str = typer.Option("background", "--urgency", help="Urgency: active|background|someday"),
    tag: Optional[list[str]] = typer.Option(None, "--tag", "-t", help="Tags"),
) -> None:
    """Capture a question."""
    capture = ingest.ingest_question(
        text=text, domain=domain, urgency=urgency, tags=_parse_tags(tag)
    )
    console.print(f"[green]Captured[/green] question [dim]{capture.id}[/dim]")


@capture_app.command()
def react(
    capture_id: str = typer.Argument(help="ID of capture to react to"),
    text: str = typer.Option(..., "--text", help="Reaction text"),
    stance: str = typer.Option("extend", "--stance", help="Stance: agree|disagree|extend|question|synthesize"),
    tag: Optional[list[str]] = typer.Option(None, "--tag", "-t", help="Tags"),
) -> None:
    """React to an existing capture."""
    try:
        capture = ingest.ingest_reaction(
            text=text, reacting_to=capture_id, stance=stance, tags=_parse_tags(tag)
        )
        console.print(f"[green]Captured[/green] reaction [dim]{capture.id}[/dim]")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _editor_input() -> str | None:
    """Open $EDITOR for text input."""
    editor = os.environ.get("EDITOR", "vim")
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w+", delete=False) as f:
        f.write("# Enter your thought below (save and close to capture)\n\n")
        f.flush()
        path = f.name
    try:
        subprocess.run([editor, path], check=True)
        with open(path) as f:
            lines = f.readlines()
        # Strip the instruction comment
        text = "".join(line for line in lines if not line.startswith("# "))
        return text.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    finally:
        os.unlink(path)
