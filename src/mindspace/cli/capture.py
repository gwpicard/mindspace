"""CLI commands for capturing content."""

import os
import subprocess
import sys
import tempfile
from typing import Optional

import typer
from rich.console import Console

from mindspace.pipelines.ingest import DuplicateError
from mindspace.pipelines import ingest

capture_app = typer.Typer(no_args_is_help=True)
console = Console()


def _parse_tags(tag: list[str] | None) -> list[str]:
    return tag if tag else []


def _prompt_tags(capture_text: str, current_tags: list[str], source_tags: list[str] | None = None) -> list[str]:
    """Suggest tags interactively and return final tag list."""
    if len(current_tags) >= 4:
        return current_tags

    from mindspace.capture.store import all_tags
    from mindspace.derived.tag_suggester import suggest_tags

    existing = all_tags()
    suggestions = suggest_tags(
        text=capture_text,
        existing_tags=existing,
        source_tags=source_tags,
    )
    # Filter out tags the user already provided
    suggestions = [s for s in suggestions if s not in current_tags]
    if not suggestions:
        return current_tags

    console.print(f"Suggested tags: [cyan]{', '.join(suggestions)}[/cyan]")

    if not sys.stdin.isatty():
        return current_tags + suggestions

    choice = console.input("Accept? [Y/n/edit]: ").strip().lower()
    if choice in ("", "y", "yes"):
        return current_tags + suggestions
    elif choice in ("n", "no"):
        return current_tags
    else:
        # Treat as comma-separated edit
        edited = [t.strip() for t in choice.split(",") if t.strip()]
        return current_tags + edited


@capture_app.command()
def url(
    target_url: str = typer.Argument(help="URL to capture"),
    tag: Optional[list[str]] = typer.Option(None, "--tag", "-t", help="Tags"),
) -> None:
    """Capture a URL (auto-extracts content)."""
    try:
        with console.status("Extracting and embedding..."):
            capture = ingest.ingest_url(target_url, tags=_parse_tags(tag))
    except DuplicateError as e:
        console.print(f"[yellow]Already captured as[/yellow] [dim]{e.existing.id}[/dim] ({e.existing.created_at:%Y-%m-%d})")
        return
    console.print(f"[green]Captured[/green] {capture.type.value} [dim]{capture.id}[/dim]")
    if hasattr(capture.content, "title") and capture.content.title:
        console.print(f"  Title: {capture.content.title}")
    if hasattr(capture.content, "word_count") and capture.content.word_count:
        console.print(f"  Words: {capture.content.word_count}")

    text = capture.text_for_embedding()
    new_tags = _prompt_tags(text, capture.context.tags)
    if new_tags != capture.context.tags:
        capture.context.tags = new_tags
        from mindspace.capture import store
        store.save(capture)


@capture_app.command()
def repo(
    repo_url: str = typer.Argument(help="GitHub repo URL"),
    tag: Optional[list[str]] = typer.Option(None, "--tag", "-t", help="Tags"),
) -> None:
    """Capture a GitHub repo (README + metadata)."""
    try:
        with console.status("Fetching repo metadata..."):
            capture = ingest.ingest_repo(repo_url, tags=_parse_tags(tag))
    except DuplicateError as e:
        console.print(f"[yellow]Already captured as[/yellow] [dim]{e.existing.id}[/dim] ({e.existing.created_at:%Y-%m-%d})")
        return
    console.print(f"[green]Captured[/green] repo [dim]{capture.id}[/dim]")
    content = capture.content
    console.print(f"  Repo: {content.owner}/{content.repo_name}")
    if content.description:
        console.print(f"  Description: {content.description}")
    if content.stars is not None:
        console.print(f"  Stars: {content.stars}")
    if content.language:
        console.print(f"  Language: {content.language}")

    text = capture.text_for_embedding()
    source_tags = list(content.topics)
    if content.language:
        source_tags.append(content.language.lower())
    new_tags = _prompt_tags(text, capture.context.tags, source_tags=source_tags)
    if new_tags != capture.context.tags:
        capture.context.tags = new_tags
        from mindspace.capture import store
        store.save(capture)


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

    new_tags = _prompt_tags(text, capture.context.tags)
    if new_tags != capture.context.tags:
        capture.context.tags = new_tags
        from mindspace.capture import store
        store.save(capture)


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

    new_tags = _prompt_tags(text, capture.context.tags)
    if new_tags != capture.context.tags:
        capture.context.tags = new_tags
        from mindspace.capture import store
        store.save(capture)


@capture_app.command()
def question(
    text: str = typer.Argument(help="Question text"),
    urgency: str = typer.Option("background", "--urgency", help="Urgency: active|background|someday"),
    tag: Optional[list[str]] = typer.Option(None, "--tag", "-t", help="Tags"),
) -> None:
    """Capture a question."""
    capture = ingest.ingest_question(
        text=text, urgency=urgency, tags=_parse_tags(tag)
    )
    console.print(f"[green]Captured[/green] question [dim]{capture.id}[/dim]")

    new_tags = _prompt_tags(text, capture.context.tags)
    if new_tags != capture.context.tags:
        capture.context.tags = new_tags
        from mindspace.capture import store
        store.save(capture)


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

        new_tags = _prompt_tags(text, capture.context.tags)
        if new_tags != capture.context.tags:
            capture.context.tags = new_tags
            from mindspace.capture import store
            store.save(capture)
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
