"""Unit tests for Disk metrics collector."""

from collections import namedtuple

import pytest

from syswatch.collectors.disk import collect_disk_metrics
from syswatch.models import DiskMetrics

DiskUsageMock = namedtuple("DiskUsageMock", ["total", "used", "free", "percent"])


def test_collect_disk_metrics_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test disk metrics collection for valid paths."""
    mock_usage = DiskUsageMock(
        total=500_000_000_000,
        used=250_000_000_000,
        free=250_000_000_000,
        percent=50.0,
    )
    monkeypatch.setattr("psutil.disk_usage", lambda path: mock_usage)

    metrics = collect_disk_metrics(paths=["/"])

    assert isinstance(metrics, DiskMetrics)
    assert len(metrics.partitions) == 1
    assert metrics.partitions[0].path == "/"
    assert metrics.partitions[0].total_bytes == 500_000_000_000
    assert metrics.partitions[0].used_percent == 50.0
    assert len(metrics.errors) == 0


def test_collect_disk_metrics_default_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test disk metrics collection defaults to ['/'] when paths is None."""
    mock_usage = DiskUsageMock(total=100, used=50, free=50, percent=50.0)
    monkeypatch.setattr("psutil.disk_usage", lambda path: mock_usage)

    metrics = collect_disk_metrics(paths=None)
    assert len(metrics.partitions) == 1
    assert metrics.partitions[0].path == "/"


def test_collect_disk_metrics_handles_path_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test disk metrics collection handles non-existent, restricted, or unexpected errors gracefully."""

    def mock_disk_usage(path: str):
        if path == "/nonexistent":
            raise FileNotFoundError("No such file or directory")
        if path == "/restricted":
            raise PermissionError("Permission denied")
        if path == "/unexpected":
            raise RuntimeError("Unexpected failure")
        return DiskUsageMock(total=100, used=50, free=50, percent=50.0)

    monkeypatch.setattr("psutil.disk_usage", mock_disk_usage)

    metrics = collect_disk_metrics(paths=["/", "/nonexistent", "/restricted", "/unexpected"])

    assert len(metrics.partitions) == 1
    assert metrics.partitions[0].path == "/"
    assert len(metrics.errors) == 3
    assert "/nonexistent" in metrics.errors
    assert "/restricted" in metrics.errors
    assert "/unexpected" in metrics.errors
