"""Root Typer application."""

import typer

from mindspace.cli.admin import admin_app
from mindspace.cli.capture import capture_app
from mindspace.cli.eval import eval_app
from mindspace.cli.search import search_app

app = typer.Typer(
    name="ms",
    help="Mindspace — Personal Intelligence System",
    no_args_is_help=True,
)

app.add_typer(capture_app, name="capture", help="Capture URLs, snippets, thoughts, questions, reactions")
app.add_typer(search_app, name="search", help="Search and browse captures")
app.add_typer(admin_app, name="admin", help="Administration and maintenance")
app.add_typer(eval_app, name="eval", help="Retrieval quality evaluation")

if __name__ == "__main__":
    app()
