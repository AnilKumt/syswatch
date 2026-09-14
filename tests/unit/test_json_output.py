"""Unit tests for machine-readable JSON output serializer."""

import json

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
from syswatch.output.json_output import render_json_report


def test_render_json_report_schema() -> None:
    """Test JSON output conforms strictly to valid JSON schema."""
    health = OverallHealth(
        status=HealthStatus.OK,
        cpu_status=HealthStatus.OK,
        memory_status=HealthStatus.OK,
        swap_status=HealthStatus.OK,
        disk_status=HealthStatus.OK,
        system_metrics=SystemMetrics("dev-machine", "Linux", "6.1.0", "x86_64", 0.0, 3600.0),
        cpu_metrics=CpuMetrics(42.1, 4, load_average=(1.0, 0.8, 0.5)),
        memory_metrics=MemoryMetrics(16_000_000_000, 8_000_000_000, 8_000_000_000, 50.0),
        disk_metrics=DiskMetrics([DiskPartitionUsage("/", 100_000_000_000, 40_000_000_000, 60_000_000_000, 40.0)]),
        network_metrics=NetworkMetrics(1000, 2000, 10, 20),
    )

    json_str = render_json_report(health)
    parsed = json.loads(json_str)

    assert parsed["status"] == "OK"
    assert parsed["hostname"] == "dev-machine"
    assert parsed["os"]["name"] == "Linux"
    assert parsed["cpu"]["usage_percent"] == 42.1
    assert parsed["memory"]["used_percent"] == 50.0
    assert "/" in parsed["disk"]["partitions"]
    assert parsed["disk"]["partitions"]["/"]["used_percent"] == 40.0
    assert parsed["timestamp"].endswith("Z")


def test_render_json_report_with_alerts() -> None:
    """Test JSON serializer outputs active threshold alerts correctly."""
    alert = Alert("Disk (/)", 96.0, 95.0, Severity.CRITICAL, "Disk (/) usage is CRITICAL")
    health = OverallHealth(
        status=HealthStatus.CRITICAL,
        cpu_status=HealthStatus.OK,
        memory_status=HealthStatus.OK,
        swap_status=HealthStatus.OK,
        disk_status=HealthStatus.CRITICAL,
        alerts=[alert],
    )

    json_str = render_json_report(health)
    parsed = json.loads(json_str)

    assert parsed["status"] == "CRITICAL"
    assert len(parsed["alerts"]) == 1
    assert parsed["alerts"][0]["severity"] == "CRITICAL"
    assert parsed["alerts"][0]["metric"] == "Disk (/)"
