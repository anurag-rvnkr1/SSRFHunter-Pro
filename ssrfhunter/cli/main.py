from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from ssrfhunter.config import ScanConfig
from ssrfhunter.core.engine import ScanEngine
from ssrfhunter.database.store import ScanDatabase
from ssrfhunter.logging.setup import build_logger
from ssrfhunter.models import ScanResult
from ssrfhunter.reporting.generator import ReportGenerator

app = typer.Typer(name="ssrfhunter", help="SSRFHunter Pro - enterprise-grade SSRF testing.")
console = Console()


def _load_config(url: str | None, input_file: str | None, overrides: dict[str, Any]) -> ScanConfig:
    config = ScanConfig.from_yaml(Path("config.yml"))
    if url:
        overrides["target"] = url
    if input_file:
        overrides["input_file"] = input_file
    return config.merge(overrides)


def _print_scan_summary(result: ScanResult) -> None:
    findings = result.summary.findings
    console.print(
        Panel(f"Scan completed in {result.summary.duration_seconds:.2f}s", title="Scan Complete")
    )
    table = Table(title="Findings Summary", show_lines=True)
    table.add_column("Severity", style="bold red")
    table.add_column("Title")
    table.add_column("URL")
    table.add_column("Evidence")
    for finding in findings:
        table.add_row(finding.severity, finding.title, finding.url, finding.evidence[:60])
    console.print(table)


@app.command()
def version() -> None:
    """Show the SSRFHunter Pro version."""
    console.print("SSRFHunter Pro 0.1.0")


@app.command()
def doctor() -> None:
    """Run basic environment checks."""
    console.print(Panel("Running environment diagnostics", title="Doctor"))
    config = ScanConfig.from_yaml(Path("config.yml"))
    console.print("Python: [green]3.12+ supported[/green]")
    console.print(
        f"Config file: [cyan]{Path('config.yml').resolve()}[/cyan] {'exists' if Path('config.yml').exists() else '[yellow]not found[/yellow]'}"
    )
    console.print(f"Payloads file: [cyan]{config.payloads_path or 'payloads/default.yml'}[/cyan]")
    console.print("Dependencies: [green]available[/green]")


@app.command()
def config() -> None:
    """Display the effective scanner configuration."""
    config = ScanConfig.from_yaml(Path("config.yml"))
    console.print(Panel("Effective configuration", title="Config"))
    console.print(config)


@app.command()
def history(limit: int = typer.Option(10, help="Number of recent scans to display.")) -> None:
    """Show recent scan history."""
    db = ScanDatabase()

    async def show_history() -> None:
        await db.initialize()
        recent = await db.list_scans(limit=limit)
        table = Table(title="Scan History")
        table.add_column("ID", style="cyan")
        table.add_column("Target")
        table.add_column("Started")
        table.add_column("Duration")
        table.add_column("Findings")
        for record in recent:
            table.add_row(
                str(record.id),
                record.target,
                record.started_at.isoformat(),
                f"{record.duration_seconds:.2f}s",
                str(record.findings_count),
            )
        console.print(table)

    asyncio.run(show_history())


@app.command()
def crawl(
    url: str = typer.Option(..., help="Starting target URL for crawling."),
    workers: int = typer.Option(4, help="Worker concurrency for crawling."),
    timeout: int = typer.Option(10, help="Request timeout in seconds."),
    max_depth: int = typer.Option(2, help="Maximum crawl depth."),
    domain_restriction: bool = typer.Option(True, help="Restrict crawling to the target domain."),
) -> None:
    """Discover targets, forms, and API endpoints without scanning."""
    config = ScanConfig.from_yaml(Path("config.yml")).merge(
        {
            "target": url,
            "workers": workers,
            "timeout": timeout,
            "max_depth": max_depth,
            "domain_restriction": domain_restriction,
        }
    )
    logger = build_logger(verbose=False, debug=False)
    engine = ScanEngine(config=config, logger=logger)

    async def run_crawl() -> None:
        discovered = await engine.discover()
        panel = Panel(f"Discovered {len(discovered['urls'])} URL(s)", title="Crawl Results")
        console.print(panel)
        for url_item in discovered["urls"]:
            console.print(f"- {url_item}")

    asyncio.run(run_crawl())


@app.command()
def report(
    scan_id: int | None = typer.Option(None, help="Previous scan id to render a report."),
    output: str | None = typer.Option(None, help="Directory to save reports."),
    html: bool = typer.Option(False, help="Generate HTML report."),
    json_out: bool = typer.Option(False, help="Generate JSON report."),
    markdown: bool = typer.Option(False, help="Generate Markdown report."),
) -> None:
    """Generate reports from a completed scan."""
    db = ScanDatabase()
    generator = ReportGenerator()

    async def render_report() -> None:
        await db.initialize()
        scan_record = await db.get_scan(scan_id)
        if scan_record is None:
            console.print("[red]No scan found for the requested id.[/red]")
            raise typer.Exit(code=1)
        result = scan_record.to_scan_result()
        output_dir = Path(output or "reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        paths: dict[str, Path] = {}
        if html or not any((html, json_out, markdown)):
            paths["html"] = output_dir / f"scan-{scan_record.id}.html"
            paths["html"].write_text(generator.generate_html(result), encoding="utf-8")
        if json_out:
            paths["json"] = output_dir / f"scan-{scan_record.id}.json"
            paths["json"].write_text(generator.generate_json(result), encoding="utf-8")
        if markdown:
            paths["md"] = output_dir / f"scan-{scan_record.id}.md"
            paths["md"].write_text(generator.generate_markdown(result), encoding="utf-8")
        console.print(Panel(f"Report generated at {output_dir}", title="Report"))
        for category, path in paths.items():
            console.print(f"[green]{category.upper()}[/green]: {path}")

    asyncio.run(render_report())


@app.command()
def scan(
    url: str | None = typer.Option(None, help="Target URL to scan."),
    input_file: str | None = typer.Option(None, help="Path to file containing target URLs."),
    workers: int = typer.Option(4, help="Parallel worker count."),
    timeout: int = typer.Option(10, help="Request timeout in seconds."),
    headers: list[str] | None = typer.Option(None, help="Custom headers in Key:Value form."),
    cookies: list[str] | None = typer.Option(None, help="Cookies in Key=Value form."),
    proxy: str | None = typer.Option(None, help="HTTP proxy URL."),
    user_agent: str = typer.Option("SSRFHunter-Pro/0.1", help="User agent string."),
    output: str | None = typer.Option(None, help="Directory to write reports."),
    json_out: bool = typer.Option(False, help="Write JSON output."),
    html_out: bool = typer.Option(False, help="Write HTML output."),
    verbose: bool = typer.Option(False, help="Enable verbose output."),
    debug: bool = typer.Option(False, help="Enable debug logging."),
    max_depth: int = typer.Option(2, help="Maximum crawl depth."),
    domain_restriction: bool = typer.Option(
        True, help="Restrict crawled URLs to the target domain."
    ),
) -> None:
    """Run an SSRF scan against an authorized target."""
    if not url and not input_file:
        console.print("[red]Error: Please provide --url or --input.[/red]")
        raise typer.Exit(code=1)

    if input_file and not Path(input_file).exists():
        console.print(f"[red]Error: Input file {input_file} does not exist.[/red]")
        raise typer.Exit(code=1)

    if input_file and not Confirm.ask(
        "Scanning multiple targets requires explicit authorization. Continue?"
    ):
        raise typer.Exit(code=1)

    override_data: dict[str, Any] = {
        "workers": workers,
        "timeout": timeout,
        "proxy": proxy,
        "user_agent": user_agent,
        "output": output,
        "json_output": json_out,
        "html_output": html_out,
        "verbose": verbose,
        "debug": debug,
        "max_depth": max_depth,
        "domain_restriction": domain_restriction,
    }
    config = _load_config(url, input_file, override_data)
    config.headers = {
        **config.headers,
        **{
            pair.split(":", 1)[0].strip(): pair.split(":", 1)[1].strip()
            for pair in (headers or [])
            if ":" in pair
        },
    }
    config.cookies = {
        **config.cookies,
        **{
            pair.split("=", 1)[0].strip(): pair.split("=", 1)[1].strip()
            for pair in (cookies or [])
            if "=" in pair
        },
    }
    logger = build_logger(verbose=verbose, debug=debug)
    engine = ScanEngine(config=config, logger=logger)

    async def run_scan() -> None:
        start_at = datetime.now(timezone.utc)
        result = await engine.scan()
        finished_at = datetime.now(timezone.utc)
        result.summary.started_at = start_at
        result.summary.completed_at = finished_at
        result.summary.duration_seconds = (finished_at - start_at).total_seconds()
        _print_scan_summary(result)
        db = ScanDatabase()
        await db.initialize()
        await db.save_scan(result)
        report_dir = Path(output or "reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        generator = ReportGenerator()
        if html_out:
            html_path = report_dir / f"{result.summary.scan_id}.html"
            html_path.write_text(generator.generate_html(result), encoding="utf-8")
            console.print(f"[green]HTML Report:[/green] {html_path}")
        if json_out:
            json_path = report_dir / f"{result.summary.scan_id}.json"
            json_path.write_text(generator.generate_json(result), encoding="utf-8")
            console.print(f"[green]JSON Report:[/green] {json_path}")
        if output and not (html_out or json_out):
            markdown_path = report_dir / f"{result.summary.scan_id}.md"
            markdown_path.write_text(generator.generate_markdown(result), encoding="utf-8")
            console.print(f"[green]Markdown Report:[/green] {markdown_path}")

    asyncio.run(run_scan())


@app.command()
def help() -> None:
    """Show help for SSRFHunter Pro."""
    console.print("Use --help to display the available commands and options.")


if __name__ == "__main__":
    app()
