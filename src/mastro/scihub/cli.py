"""CLI for Sci-Hub PDF download."""

import logging
import logging.config
from pathlib import Path
from typing import List, Literal, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from .scihub import SciHubClient

console = Console(highlight=False)
logger = logging.getLogger(__name__)

app = typer.Typer(
    help="[bold]Mastro[/] — Sci-Hub PDF Download Toolkit",
    rich_markup_mode="rich",
)

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


@app.callback()
def main(
    log_level: LogLevel = typer.Option(
        "WARNING", "--log-level", "-v",
        help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    ),
) -> None:
    """Configure Rich logging for all commands."""
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(message)s",
                "datefmt": "[%X]",
            }
        },
        "handlers": {
            "rich": {
                "()": RichHandler,
                "level": log_level,
                "rich_tracebacks": True,
                "show_time": True,
                "show_path": False,
                "formatter": "default",
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["rich"],
        },
    })


@app.command(help="Download PDF(s) from Sci-Hub by DOI.")
def download(
    dois: List[str] = typer.Argument(
        ..., help="One or more DOIs to download."
    ),
    output_dir: str = typer.Option(
        ..., "--output-dir", "-d", help="Directory to save PDFs."
    ),
    mirrors: Optional[List[str]] = typer.Option(
        None, "--mirror", "-m", help="Custom Sci-Hub mirror(s) to use."
    ),
) -> None:
    """Download PDFs from Sci-Hub and report per-item status."""
    out_path = Path(output_dir)
    if not out_path.exists():
        out_path.mkdir(parents=True, exist_ok=True)
        console.print(f"📂 Created output directory: {out_path}")

    table = Table(show_lines=False)
    table.add_column("DOI", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Message")

    success = 0
    with SciHubClient(mirrors=mirrors) as client:
        for doi in dois:
            # Generate filename from DOI
            safe_doi = doi.replace("/", "_").replace(":", "_")
            pdf_path = out_path / f"{safe_doi}.pdf"

            result = client.download(doi, pdf_path)
            if result:
                table.add_row(doi, "[green]OK[/green]", result)
                success += 1
            else:
                table.add_row(doi, "[red]FAIL[/red]", "Download failed")

    console.print(table)
    console.print(f"✅ {success}/{len(dois)} downloaded")


if __name__ == "__main__":
    app()
