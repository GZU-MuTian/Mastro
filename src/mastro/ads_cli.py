"""
CLI for NASA ADS search, export, and PDF download.
"""

import json
import logging
import logging.config
from pathlib import Path
from typing import List, Literal, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from .nasa_ads import ADSClient

console = Console(highlight=False)
logger = logging.getLogger(__name__)

app = typer.Typer(
    help="[bold]AI4SNRpy[/] — ADS & SNR Catalogue Toolkit",
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


@app.command(help="Search ADS and display results as a table or JSON.")
def search(
    query: str = typer.Argument(..., help="ADS search query."),
    rows: int = typer.Option(10, "--rows", "-n", help="Number of results to return."),
    sort: Optional[str] = typer.Option(
        None, "--sort", "-s", help="Sort expression (e.g. 'citation_count desc')."
    ),
    as_json: bool = typer.Option(
        False, "--json", help="Print raw JSON instead of a table."
    ),
) -> None:
    """Run an ADS search and present the results."""
    try:
        with ADSClient() as client:
            result = client.search(query, rows=rows, sort=sort)
    except Exception:
        logger.exception("Search failed")
        raise typer.Exit(1)

    if as_json:
        console.print_json(json.dumps(result, ensure_ascii=False, default=str))
        return

    response = result.get("response", {})
    docs = response.get("docs", [])
    num_found = response.get("numFound", 0)

    table = Table(title=f"{num_found} results found", show_lines=False)
    table.add_column("#", justify="right", style="dim", width=4)
    table.add_column("Bibcode", style="cyan", no_wrap=True)
    table.add_column("Year", justify="right")
    table.add_column("Cite", justify="right")
    table.add_column("Title")

    for idx, doc in enumerate(docs, start=1):
        title = doc.get("title", [""])[0] if isinstance(doc.get("title"), list) else doc.get("title", "")
        table.add_row(
            str(idx),
            doc.get("bibcode", ""),
            str(doc.get("year", "")),
            str(doc.get("citation_count", "")),
            title,
        )

    console.print(table)


@app.command(help="Export ADS metadata (BibTeX, AASTeX, etc.).")
def export(
    bibcodes: List[str] = typer.Argument(..., help="One or more ADS bibcodes."),
    fmt: str = typer.Option("bibtex", "--format", "-f", help="Export format."),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Write output to file instead of stdout."
    ),
) -> None:
    """Export metadata for the given bibcodes."""
    try:
        with ADSClient() as client:
            content = client.export(bibcodes, fmt=fmt)
    except Exception:
        logger.exception("Export failed")
        raise typer.Exit(1)

    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        console.print(f"✅ Saved to [green]{path}[/green]")
    else:
        console.print(content)


@app.command(help="Download PDF(s) from ADS.")
def download(
    urls_or_bibcodes: List[str] = typer.Argument(
        ..., help="ADS URLs or bibcodes to download."
    ),
    output_dir: str = typer.Option(
        ..., "--output-dir", "-d", help="Directory to save PDFs."
    ),
) -> None:
    """Download PDFs and report per-item status."""
    out_path = Path(output_dir)
    if not out_path.exists():
        out_path.mkdir(parents=True, exist_ok=True)
        console.print(f"📂 Created output directory: {out_path}")

    try:
        with ADSClient() as client:
            results = client.fetch(urls_or_bibcodes, output_dir=str(out_path))
    except Exception:
        logger.exception("Download failed")
        raise typer.Exit(1)

    table = Table(show_lines=False)
    table.add_column("Bibcode", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Message")

    for item in results:
        status = "[green]OK[/green]" if item["success"] else "[red]FAIL[/red]"
        table.add_row(item["bibcode"], status, item["message"])

    console.print(table)

    success = sum(1 for item in results if item["success"])
    console.print(f"✅ {success}/{len(results)} downloaded")


if __name__ == "__main__":
    app()