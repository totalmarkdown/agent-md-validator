"""CLI entry point for agent-md-validator."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .reporter import report_json, report_text
from .validator import validate_bundle, validate_file


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, help="Treat warnings as errors.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format.",
)
def main(path: str, strict: bool, output_format: str) -> None:
    """Validate agent-md-specs configuration files.

    PATH can be a single .md file or a directory containing spec files.
    """
    target = Path(path)

    if target.is_file():
        results = [validate_file(target)]
    elif target.is_dir():
        results = validate_bundle(target)
    else:
        click.echo(f"Error: {path} is not a file or directory", err=True)
        sys.exit(1)

    if not results:
        click.echo("No spec files found.")
        sys.exit(0)

    if output_format == "json":
        exit_code = report_json(results, strict=strict)
    else:
        exit_code = report_text(results, strict=strict)

    sys.exit(exit_code)
