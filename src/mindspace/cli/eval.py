"""CLI commands for evaluation framework."""

import json

import typer
from rich.console import Console
from rich.table import Table

from mindspace.derived.embeddings import EmbeddingPipeline
from mindspace.eval.history import compare_runs, load_history, save_run
from mindspace.eval.runner import EvalRunner
from mindspace.eval.types import EvalCase, EvalDataset
from mindspace.infra.paths import ensure_dirs, golden_path

eval_app = typer.Typer(no_args_is_help=True)
console = Console()


def _load_golden() -> EvalDataset:
    """Load golden dataset from disk."""
    path = golden_path()
    if not path.exists():
        return EvalDataset()
    data = json.loads(path.read_text())
    return EvalDataset.model_validate(data)


def _save_golden(dataset: EvalDataset) -> None:
    """Save golden dataset to disk."""
    path = golden_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dataset.model_dump_json(indent=2))


@eval_app.command("run")
def eval_run(
    k: int = typer.Option(5, "--k", help="Top-k for retrieval"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show per-case results"),
) -> None:
    """Run golden dataset evaluation and save results."""
    ensure_dirs()
    dataset = _load_golden()
    if not dataset.cases:
        console.print("[yellow]No cases in golden dataset. Use 'ms eval add-case' to create some.[/yellow]")
        raise typer.Exit(1)

    pipeline = EmbeddingPipeline()
    runner = EvalRunner(pipeline)
    result = runner.run(dataset, k=k)

    # Print summary
    s = result.summary
    console.print()
    console.print(f"[bold]Eval Results[/bold]  (k={k}, {s.num_cases} cases)")
    console.print(f"  Pass rate:    [bold]{s.pass_rate:.0%}[/bold]")
    console.print(f"  Hit rate:     {s.hit_rate:.0%}")
    console.print(f"  Mean MRR:     {s.mean_mrr:.3f}")
    console.print(f"  Mean P@{k}:    {s.mean_precision_at_k:.3f}")
    console.print(f"  Mean R@{k}:    {s.mean_recall_at_k:.3f}")

    if verbose:
        console.print()
        for cr in result.per_case:
            status = "[green]PASS[/green]" if cr.hit else "[red]FAIL[/red]"
            console.print(f"  {status}  {cr.case.query}")
            console.print(f"         Retrieved: {cr.retrieved_ids}")
            console.print(f"         Expected:  {cr.case.expected_ids}")
            if cr.leaked_negatives:
                console.print(f"         [red]Leaked: {cr.leaked_negatives}[/red]")

    # Save to history
    save_run(result)
    console.print(f"\n[dim]Saved to eval history.[/dim]")


@eval_app.command("history")
def eval_history() -> None:
    """Show past evaluation runs."""
    runs = load_history()
    if not runs:
        console.print("[dim]No eval history yet. Run 'ms eval run' first.[/dim]")
        return

    table = Table(title="Eval History")
    table.add_column("Timestamp", style="dim")
    table.add_column("k")
    table.add_column("Cases")
    table.add_column("Pass Rate", justify="right")
    table.add_column("MRR", justify="right")
    table.add_column("P@k", justify="right")
    table.add_column("R@k", justify="right")

    for run in runs:
        s = run.summary
        table.add_row(
            run.timestamp[:19],
            str(run.k),
            str(s.num_cases),
            f"{s.pass_rate:.0%}",
            f"{s.mean_mrr:.3f}",
            f"{s.mean_precision_at_k:.3f}",
            f"{s.mean_recall_at_k:.3f}",
        )

    console.print(table)


@eval_app.command("compare")
def eval_compare() -> None:
    """Compare the last two evaluation runs."""
    runs = load_history()
    if len(runs) < 2:
        console.print("[yellow]Need at least 2 runs to compare. Run 'ms eval run' more.[/yellow]")
        return

    a, b = runs[-2], runs[-1]
    deltas = compare_runs(a, b)

    console.print()
    console.print(f"[bold]Comparing[/bold]")
    console.print(f"  Before: {a.timestamp[:19]}")
    console.print(f"  After:  {b.timestamp[:19]}")
    console.print()

    for metric, delta in deltas.items():
        if delta > 0:
            style = "green"
            sign = "+"
        elif delta < 0:
            style = "red"
            sign = ""
        else:
            style = "dim"
            sign = ""
        console.print(f"  {metric:<20} [{style}]{sign}{delta:.3f}[/{style}]")


@eval_app.command("add-case")
def eval_add_case() -> None:
    """Interactively create an eval case from a search query."""
    ensure_dirs()

    query = typer.prompt("Query")

    pipeline = EmbeddingPipeline()
    results = pipeline.search(query, n_results=10)

    if not results:
        console.print("[dim]No results found.[/dim]")
        raise typer.Exit(1)

    console.print()
    for i, hit in enumerate(results):
        score = 1 - hit["distance"]
        doc_preview = hit["document"][:120].replace("\n", " ")
        console.print(f"  [{i}] {hit['id']}  ({score:.0%})  {doc_preview}")

    console.print()
    expected_input = typer.prompt(
        "Enter indices of relevant results (comma-separated, or 'none')"
    )

    if expected_input.strip().lower() == "none":
        expected_ids = []
    else:
        indices = [int(x.strip()) for x in expected_input.split(",") if x.strip().isdigit()]
        expected_ids = [results[i]["id"] for i in indices if i < len(results)]

    negative_input = typer.prompt(
        "Enter indices of results that should NOT appear (comma-separated, or 'none')",
        default="none",
    )

    if negative_input.strip().lower() == "none":
        negative_ids = []
    else:
        indices = [int(x.strip()) for x in negative_input.split(",") if x.strip().isdigit()]
        negative_ids = [results[i]["id"] for i in indices if i < len(results)]

    notes = typer.prompt("Notes (optional)", default="")

    case = EvalCase(
        query=query,
        expected_ids=expected_ids,
        negative_ids=negative_ids,
        notes=notes,
    )

    dataset = _load_golden()
    dataset.cases.append(case)
    _save_golden(dataset)

    console.print(f"\n[green]Added case. Golden dataset now has {len(dataset.cases)} cases.[/green]")


@eval_app.command("golden")
def eval_golden() -> None:
    """List current golden dataset cases."""
    dataset = _load_golden()
    if not dataset.cases:
        console.print("[dim]Golden dataset is empty. Use 'ms eval add-case' to add cases.[/dim]")
        return

    console.print(f"\n[bold]Golden Dataset[/bold] ({len(dataset.cases)} cases)\n")
    for i, case in enumerate(dataset.cases):
        console.print(f"  [{i}] [bold]{case.query}[/bold]")
        console.print(f"      Expected: {case.expected_ids}")
        if case.negative_ids:
            console.print(f"      Negative: {case.negative_ids}")
        if case.notes:
            console.print(f"      Notes: {case.notes}")
        console.print()
