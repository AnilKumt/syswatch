"""Unit tests for System information collector."""

import pytest

from syswatch.collectors.system import collect_system_metrics
from syswatch.models import SystemMetrics


def test_collect_system_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test gathering OS platform information and uptime calculation."""
    monkeypatch.setattr("platform.node", lambda: "test-node")
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr("platform.release", lambda: "6.1.0-generic")
    monkeypatch.setattr("platform.machine", lambda: "x86_64")
    monkeypatch.setattr("psutil.boot_time", lambda: 1000.0)
    monkeypatch.setattr("time.time", lambda: 1500.0)

    metrics = collect_system_metrics()

    assert isinstance(metrics, SystemMetrics)
    assert metrics.hostname == "test-node"
    assert metrics.os_name == "Linux"
    assert metrics.os_release == "6.1.0-generic"
    assert metrics.architecture == "x86_64"
    assert metrics.boot_time_timestamp == 1000.0
    assert metrics.uptime_seconds == 500.0
