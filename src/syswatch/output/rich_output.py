"""Rich terminal UI output renderer for syswatch health reports and process tables."""


from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from syswatch.models import HealthStatus, OverallHealth, ProcessMetrics, Severity
from syswatch.output.formatters import format_bytes, format_rate, format_uptime


def get_status_badge(status: HealthStatus) -> str:
    """Return colored Rich string representation of a HealthStatus enum value."""
    if status == HealthStatus.OK:
        return "[bold green]OK[/bold green]"
    if status == HealthStatus.WARNING:
        return "[bold yellow]WARNING[/bold yellow]"
    if status == HealthStatus.CRITICAL:
        return "[bold red]CRITICAL[/bold red]"
    return "[dim white]UNKNOWN[/dim white]"


def build_live_display(
    health: OverallHealth, title: str = "SYSWATCH SYSTEM HEALTH REPORT"
) -> Panel:
    """Build a Rich Panel renderable representation of OverallHealth.

    Args:
        health: OverallHealth snapshot to display.
        title: Panel title header string.

    Returns:
        Rich Panel instance.
    """
    # System Info Header Table
    sys_table = Table(show_header=False, box=None, padding=(0, 2))
    sys_table.add_column("Key", style="bold cyan")
    sys_table.add_column("Value", style="white")

    if health.system_metrics:
        sys = health.system_metrics
        sys_table.add_row("Hostname", sys.hostname)
        sys_table.add_row("OS Platform", f"{sys.os_name} {sys.os_release}")
        sys_table.add_row("Architecture", sys.architecture)
        sys_table.add_row("Uptime", format_uptime(sys.uptime_seconds))

    # Health Metrics Table
    metrics_table = Table(box=None, padding=(0, 1), expand=True)
    metrics_table.add_column("Component", style="bold white", width=16)
    metrics_table.add_column("Usage / Details", style="white", ratio=2)
    metrics_table.add_column("Status", justify="right", width=12)

    # CPU Row
    if health.cpu_metrics:
        cpu = health.cpu_metrics
        load_str = ""
        if cpu.load_average:
            l1, l5, l15 = cpu.load_average
            load_str = f" | Load: {l1:.2f}, {l5:.2f}, {l15:.2f}"
        details = f"{cpu.usage_percent:.1f}% ({cpu.core_count} cores{load_str})"
        metrics_table.add_row("CPU", details, get_status_badge(health.cpu_status))

    # Memory Row
    if health.memory_metrics:
        mem = health.memory_metrics
        details = (
            f"{mem.used_percent:.1f}% ({format_bytes(mem.used_bytes)} / {format_bytes(mem.total_bytes)})"
        )
        metrics_table.add_row("Memory", details, get_status_badge(health.memory_status))

    # Swap Row
    if health.swap_metrics:
        swap = health.swap_metrics
        details = (
            f"{swap.used_percent:.1f}% ({format_bytes(swap.used_bytes)} / {format_bytes(swap.total_bytes)})"
        )
        metrics_table.add_row("Swap", details, get_status_badge(health.swap_status))

    # Disk Partitions
    if health.disk_metrics:
        for part in health.disk_metrics.partitions:
            p_status = get_status_badge(
                HealthStatus.CRITICAL
                if part.used_percent >= 95.0
                else HealthStatus.WARNING
                if part.used_percent >= 85.0
                else HealthStatus.OK
            )
            details = (
                f"{part.used_percent:.1f}% ({format_bytes(part.used_bytes)} / {format_bytes(part.total_bytes)})"
            )
            metrics_table.add_row(f"Disk ({part.path})", details, p_status)

        for err_path, err_msg in health.disk_metrics.errors.items():
            metrics_table.add_row(f"Disk ({err_path})", f"[red]{err_msg}[/red]", get_status_badge(HealthStatus.UNKNOWN))

    # Network Section
    if health.network_metrics:
        net = health.network_metrics
        sent_str = format_bytes(net.total_bytes_sent)
        recv_str = format_bytes(net.total_bytes_recv)
        rate_str = ""
        if net.bytes_sent_per_sec > 0 or net.bytes_recv_per_sec > 0:
            rate_str = f" | Rate: ↓{format_rate(net.bytes_recv_per_sec)} ↑{format_rate(net.bytes_sent_per_sec)}"
        details = f"Sent: {sent_str} | Recv: {recv_str}{rate_str}"
        metrics_table.add_row("Network", details, "[dim green]LIVE[/dim green]")

    # Active Alerts Section
    alerts_renderable = ""
    if health.alerts:
        alert_table = Table(show_header=True, header_style="bold red", box=None, expand=True)
        alert_table.add_column("Severity", width=12)
        alert_table.add_column("Alert Description")

        for alert in health.alerts:
            sev_style = "[bold red]CRITICAL[/bold red]" if alert.severity == Severity.CRITICAL else "[bold yellow]WARNING[/bold yellow]"
            alert_table.add_row(sev_style, alert.message)
        alerts_renderable = alert_table

    # Overall Status Panel Header Title
    status_badge = get_status_badge(health.status)

    panel_content = Table.grid(expand=True)
    panel_content.add_row(sys_table)
    panel_content.add_row(Text(""))  # Spacer
    panel_content.add_row(metrics_table)

    if alerts_renderable:
        panel_content.add_row(Text("\n[bold red]Active Alerts:[/bold red]"))
        panel_content.add_row(alerts_renderable)

    panel_content.add_row(Text(""))  # Spacer
    panel_content.add_row(Text.from_markup(f"Overall System Health: {status_badge}", justify="center"))

    return Panel(
        panel_content,
        title=f"[bold cyan]{title}[/bold cyan]",
        subtitle="[dim]Press Ctrl+C to exit[/dim]",
        border_style="cyan" if health.status == HealthStatus.OK else "yellow" if health.status == HealthStatus.WARNING else "red",
        padding=(1, 2),
    )


def render_health_report(
    health: OverallHealth, console: Console | None = None
) -> None:
    """Render a human-readable system health report to terminal using Rich."""
    if console is None:
        console = Console()

    panel = build_live_display(health, title="SYSWATCH SYSTEM HEALTH REPORT")
    console.print(panel)


def render_process_report(
    metrics: ProcessMetrics, console: Console | None = None
) -> None:
    """Render top running system processes in a Rich terminal table.

    Args:
        metrics: ProcessMetrics snapshot.
        console: Optional Rich Console instance.
    """
    if console is None:
        console = Console()

    table = Table(box=None, expand=True, padding=(0, 1))
    table.add_column("PID", style="bold cyan", justify="right", width=8)
    table.add_column("NAME", style="bold white", ratio=2)
    table.add_column("USER", style="dim white", width=14)
    table.add_column("CPU %", style="bold green", justify="right", width=10)
    table.add_column("MEMORY %", style="bold yellow", justify="right", width=10)
    table.add_column("STATUS", style="white", justify="center", width=12)

    for proc in metrics.processes:
        table.add_row(
            str(proc.pid),
            proc.name,
            proc.username or "N/A",
            f"{proc.cpu_percent:.1f}",
            f"{proc.memory_percent:.1f}",
            proc.status,
        )

    panel = Panel(
        table,
        title=f"[bold cyan]SYSWATCH TOP PROCESSES ({len(metrics.processes)} of {metrics.total_processes} active)[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )

    console.print(panel)
