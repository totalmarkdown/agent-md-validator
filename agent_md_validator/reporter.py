"""Output formatting for validation results."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from .validator import ValidationResult

console = Console()


def report_text(results: list[ValidationResult], strict: bool = False) -> int:
    """Print human-readable validation report. Returns exit code."""
    total_errors = 0
    total_warnings = 0
    passed = 0

    for result in results:
        errors = [i for i in result.issues if i.level == "error"]
        warnings = [i for i in result.issues if i.level == "warning"]

        if not errors and not warnings:
            passed += 1
            continue

        if strict:
            total_errors += len(errors) + len(warnings)
        else:
            total_errors += len(errors)
            total_warnings += len(warnings)

        console.print(f"\n[bold]{result.path}[/bold]")
        for issue in errors:
            console.print(f"  [red]ERROR[/red]   {issue.message}")
        for issue in warnings:
            level = "ERROR" if strict else "WARN"
            style = "red" if strict else "yellow"
            console.print(f"  [{style}]{level}[/{style}]    {issue.message}")

    # Summary
    console.print()
    table = Table(title="Validation Summary", show_header=False)
    table.add_column("Metric", style="bold")
    table.add_column("Count", justify="right")
    table.add_row("Files checked", str(len(results)))
    table.add_row("Passed", f"[green]{passed}[/green]")
    table.add_row("Errors", f"[red]{total_errors}[/red]" if total_errors else "0")
    if not strict:
        table.add_row(
            "Warnings",
            f"[yellow]{total_warnings}[/yellow]" if total_warnings else "0",
        )
    console.print(table)

    if total_errors:
        console.print("[red]FAILED[/red]")
        return 1
    if total_warnings:
        console.print("[green]PASSED[/green] (with warnings)")
    else:
        console.print("[green]PASSED[/green]")
    return 0


def report_json(results: list[ValidationResult], strict: bool = False) -> int:
    """Print JSON validation report. Returns exit code."""
    output = {
        "files_checked": len(results),
        "passed": sum(1 for r in results if not r.issues),
        "results": [],
    }

    has_failure = False
    for result in results:
        entry = {
            "path": result.path,
            "valid": result.is_valid if not strict else not result.issues,
            "issues": [
                {"level": i.level, "message": i.message} for i in result.issues
            ],
        }
        output["results"].append(entry)
        if not entry["valid"]:
            has_failure = True

    output["overall"] = "FAILED" if has_failure else "PASSED"
    print(json.dumps(output, indent=2))
    return 1 if has_failure else 0
