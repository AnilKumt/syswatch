"""Unit tests for Rich terminal UI renderer."""

from rich.console import Console

from syswatch.models import (
    Alert,
    CpuMetrics,
    DiskMetrics,
    DiskPartitionUsage,
    HealthStatus,
    MemoryMetrics,
    NetworkMetrics,
    OverallHealth,
    Severity,
    SystemMetrics,
)
from syswatch.output.rich_output import render_health_report


def test_render_health_report_ok() -> None:
    """Test rendering a healthy system health report."""
    console = Console(record=True, width=100)

    health = OverallHealth(
        status=HealthStatus.OK,
        cpu_status=HealthStatus.OK,
        memory_status=HealthStatus.OK,
        swap_status=HealthStatus.OK,
        disk_status=HealthStatus.OK,
        system_metrics=SystemMetrics("dev-box", "Linux", "6.1.0", "x86_64", 0.0, 3600.0),
        cpu_metrics=CpuMetrics(42.1, 4, load_average=(1.0, 0.8, 0.5)),
        memory_metrics=MemoryMetrics(16_000_000_000, 8_000_000_000, 8_000_000_000, 50.0),
        disk_metrics=DiskMetrics([DiskPartitionUsage("/", 100_000_000_000, 40_000_000_000, 60_000_000_000, 40.0)]),
        network_metrics=NetworkMetrics(1000, 2000, 10, 20),
    )

    render_health_report(health, console=console)
    output = console.export_text()

    assert "SYSWATCH SYSTEM HEALTH REPORT" in output
    assert "dev-box" in output
    assert "Linux 6.1.0" in output
    assert "CPU" in output
    assert "42.1%" in output
    assert "OK" in output


def test_render_health_report_with_alerts() -> None:
    """Test rendering a report containing active threshold alerts."""
    console = Console(record=True, width=100)

    alert = Alert("Disk (/)", 96.0, 95.0, Severity.CRITICAL, "Disk (/) usage is CRITICAL: 96.0% (threshold: 95.0%)")

    health = OverallHealth(
        status=HealthStatus.CRITICAL,
        cpu_status=HealthStatus.OK,
        memory_status=HealthStatus.OK,
        swap_status=HealthStatus.OK,
        disk_status=HealthStatus.CRITICAL,
        alerts=[alert],
    )

    render_health_report(health, console=console)
    output = console.export_text()

    assert "Active Alerts:" in output
    assert "CRITICAL" in output
    assert "Disk (/) usage is CRITICAL" in output
