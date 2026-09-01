"""CLI entry point and command group definition using Click."""

import sys

import click

from syswatch import __version__
from syswatch.collectors import (
    collect_cpu_metrics,
    collect_disk_metrics,
    collect_memory_metrics,
    collect_network_metrics,
    collect_process_metrics,
    collect_swap_metrics,
    collect_system_metrics,
)
from syswatch.config import ConfigError, load_config
from syswatch.models import HealthStatus
from syswatch.output.json_output import render_json_report, render_process_json
from syswatch.output.rich_output import render_health_report, render_process_report
from syswatch.services.health import HealthEvaluatorService
from syswatch.services.monitor import ContinuousMonitorService


@click.group(invoke_without_command=True)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, readable=True),
    help="Path to YAML configuration file.",
)
@click.version_option(version=__version__, prog_name="syswatch")
@click.pass_context
def cli(ctx: click.Context, config_path: str | None) -> None:
    """syswatch: Production-Quality Linux System Health Monitor CLI."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command(name="status")
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output machine-readable JSON health report.",
)
@click.pass_context
def status_cmd(ctx: click.Context, json_output: bool) -> None:
    """Display system health status report (human-readable or JSON)."""
    config_path = ctx.obj.get("config_path")
    try:
        app_config = load_config(config_path)
    except ConfigError as err:
        click.echo(str(err), err=True)
        sys.exit(2)

    # 1. Collect all metrics snapshots
    system_metrics = collect_system_metrics()
    cpu_metrics = collect_cpu_metrics(interval=0.1)
    memory_metrics = collect_memory_metrics()
    swap_metrics = collect_swap_metrics()
    disk_metrics = collect_disk_metrics(paths=app_config.disk_paths)
    network_metrics = collect_network_metrics() if app_config.network_enabled else None

    # 2. Evaluate overall health using configured thresholds
    evaluator = HealthEvaluatorService(config=app_config.thresholds)
    overall_health = evaluator.evaluate(
        system_metrics=system_metrics,
        cpu_metrics=cpu_metrics,
        memory_metrics=memory_metrics,
        swap_metrics=swap_metrics,
        disk_metrics=disk_metrics,
        network_metrics=network_metrics,
    )

    # 3. Render Output (JSON or Rich Terminal UI)
    if json_output:
        click.echo(render_json_report(overall_health))
    else:
        render_health_report(overall_health)

    # 4. Return appropriate CLI exit code
    if overall_health.status == HealthStatus.OK:
        sys.exit(0)
    elif overall_health.status == HealthStatus.WARNING:
        sys.exit(1)
    else:  # CRITICAL or UNKNOWN
        sys.exit(2)


@cli.command(name="monitor")
@click.option(
    "-i",
    "--interval",
    type=float,
    default=None,
    help="Refresh interval in seconds.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Stream continuous JSON snapshots.",
)
@click.pass_context
def monitor_cmd(ctx: click.Context, interval: float | None, json_output: bool) -> None:
    """Run continuously updating real-time system monitoring."""
    config_path = ctx.obj.get("config_path")
    try:
        app_config = load_config(config_path)
    except ConfigError as err:
        click.echo(str(err), err=True)
        sys.exit(2)

    monitor_service = ContinuousMonitorService(app_config=app_config)

    try:
        monitor_service.run_live(interval=interval, json_output=json_output)
    except KeyboardInterrupt:
        if not json_output:
            click.echo("\nMonitoring stopped by user.")
        sys.exit(0)


@cli.command(name="processes")
@click.option(
    "-s",
    "--sort",
    "sort_by",
    type=click.Choice(["cpu", "memory"], case_sensitive=False),
    default="cpu",
    help="Sort processes by 'cpu' or 'memory' utilization.",
)
@click.option(
    "-n",
    "--limit",
    "limit",
    type=int,
    default=10,
    help="Number of top processes to display.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output processes in machine-readable JSON format.",
)
@click.pass_context
def processes_cmd(ctx: click.Context, sort_by: str, limit: int, json_output: bool) -> None:
    """Display top running system processes sorted by CPU or Memory usage."""
    metrics = collect_process_metrics(sort_by=sort_by, limit=limit)

    if json_output:
        click.echo(render_process_json(metrics))
    else:
        render_process_report(metrics)


@cli.group(name="config")
def config_group() -> None:
    """Manage and validate syswatch configuration."""


@config_group.command(name="validate")
@click.pass_context
def config_validate_cmd(ctx: click.Context) -> None:
    """Validate a syswatch YAML configuration file."""
    config_path = ctx.obj.get("config_path")
    if not config_path:
        click.echo("No configuration file specified. Usage: syswatch --config PATH config validate", err=True)
        sys.exit(1)

    try:
        app_config = load_config(config_path)
    except ConfigError as err:
        click.echo(str(err), err=True)
        sys.exit(2)

    click.echo(f"Configuration file '{config_path}' is valid.")
    click.echo(f"  Refresh interval : {app_config.interval}s")
    click.echo(f"  Disk paths       : {', '.join(app_config.disk_paths)}")
    click.echo(f"  CPU thresholds   : warn >= {app_config.thresholds.cpu_warning}%, crit >= {app_config.thresholds.cpu_critical}%")
    click.echo(f"  Memory thresholds: warn >= {app_config.thresholds.memory_warning}%, crit >= {app_config.thresholds.memory_critical}%")


def main() -> None:
    """Main execution wrapper handling graceful exits."""
    try:
        cli(prog_name="syswatch")
    except SystemExit as err:
        sys.exit(err.code)
    except Exception as err:  # noqa: BLE001
        click.echo(f"Error: {err}", err=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
