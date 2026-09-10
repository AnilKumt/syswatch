"""Unit tests for HealthEvaluatorService."""

from syswatch.alerts.thresholds import ThresholdConfig
from syswatch.models import (
    CpuMetrics,
    DiskMetrics,
    DiskPartitionUsage,
    HealthStatus,
    MemoryMetrics,
    SwapMetrics,
)
from syswatch.services.health import HealthEvaluatorService


def test_health_evaluator_all_ok() -> None:
    """Test health evaluation when all metrics are within normal limits."""
    service = HealthEvaluatorService(
        config=ThresholdConfig(
            cpu_warning=80.0, cpu_critical=90.0,
            memory_warning=80.0, memory_critical=90.0,
            swap_warning=70.0, swap_critical=85.0,
            disk_warning=85.0, disk_critical=95.0,
        )
    )

    cpu = CpuMetrics(usage_percent=45.0, core_count=4)
    mem = MemoryMetrics(total_bytes=100, available_bytes=50, used_bytes=50, used_percent=50.0)
    swap = SwapMetrics(total_bytes=100, used_bytes=10, free_bytes=90, used_percent=10.0)
    disk = DiskMetrics(
        partitions=[DiskPartitionUsage(path="/", total_bytes=100, used_bytes=60, free_bytes=40, used_percent=60.0)]
    )

    result = service.evaluate(cpu_metrics=cpu, memory_metrics=mem, swap_metrics=swap, disk_metrics=disk)

    assert result.status == HealthStatus.OK
    assert result.cpu_status == HealthStatus.OK
    assert result.memory_status == HealthStatus.OK
    assert result.swap_status == HealthStatus.OK
    assert result.disk_status == HealthStatus.OK
    assert len(result.alerts) == 0


def test_health_evaluator_worst_status_escalation() -> None:
    """Test overall status escalates to CRITICAL if any component is CRITICAL."""
    service = HealthEvaluatorService()

    cpu = CpuMetrics(usage_percent=40.0, core_count=4)  # OK
    mem = MemoryMetrics(total_bytes=100, available_bytes=15, used_bytes=85, used_percent=85.0)  # WARNING
    disk = DiskMetrics(
        partitions=[DiskPartitionUsage(path="/", total_bytes=100, used_bytes=98, free_bytes=2, used_percent=98.0)]
    )  # CRITICAL

    result = service.evaluate(cpu_metrics=cpu, memory_metrics=mem, disk_metrics=disk)

    assert result.cpu_status == HealthStatus.OK
    assert result.memory_status == HealthStatus.WARNING
    assert result.disk_status == HealthStatus.CRITICAL
    assert result.status == HealthStatus.CRITICAL
    assert len(result.alerts) == 2  # 1 warning alert + 1 critical alert


def test_health_evaluator_missing_metrics_returns_unknown() -> None:
    """Test missing metric components evaluate to UNKNOWN status."""
    service = HealthEvaluatorService()
    result = service.evaluate()  # no metrics provided

    assert result.cpu_status == HealthStatus.UNKNOWN
    assert result.memory_status == HealthStatus.UNKNOWN
    assert result.swap_status == HealthStatus.UNKNOWN
    assert result.disk_status == HealthStatus.UNKNOWN
    assert result.status == HealthStatus.UNKNOWN


def test_determine_overall_status_unknown_priority() -> None:
    """Test that UNKNOWN takes priority over OK when no CRITICAL or WARNING present."""
    service = HealthEvaluatorService()
    status = service._determine_overall_status([HealthStatus.OK, HealthStatus.UNKNOWN])
    assert status == HealthStatus.UNKNOWN
