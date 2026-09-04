"""Unit tests for CPU metrics collector."""

from unittest.mock import MagicMock

import pytest

import syswatch.collectors.cpu as cpu_module
from syswatch.collectors.cpu import collect_cpu_metrics, get_system_load_avg
from syswatch.models import CpuMetrics


def test_collect_cpu_metrics_normal(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CPU metric collection under normal operating conditions."""
    monkeypatch.setattr("psutil.cpu_percent", lambda interval=None, percpu=False: 42.5)
    monkeypatch.setattr("psutil.cpu_count", lambda logical=True: 8 if logical else 4)
    monkeypatch.setattr("psutil.getloadavg", lambda: (1.5, 1.2, 0.9))

    metrics = collect_cpu_metrics(interval=0.1)

    assert isinstance(metrics, CpuMetrics)
    assert metrics.usage_percent == 42.5
    assert metrics.core_count == 8
    assert metrics.physical_core_count == 4
    assert metrics.load_average == (1.5, 1.2, 0.9)
    assert metrics.per_cpu_percent is None


def test_collect_cpu_metrics_per_cpu(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CPU metric collection with per-core breakdown enabled."""

    def mock_cpu_percent(interval=None, percpu=False):
        if percpu:
            return [10.0, 20.0, 30.0, 40.0]
        return 25.0

    monkeypatch.setattr("psutil.cpu_percent", mock_cpu_percent)
    monkeypatch.setattr("psutil.cpu_count", lambda logical=True: 4)

    metrics = collect_cpu_metrics(per_cpu=True)
    assert metrics.per_cpu_percent == [10.0, 20.0, 30.0, 40.0]


def test_get_system_load_avg_os_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test load average fallback to os.getloadavg when psutil has no getloadavg."""
    monkeypatch.delattr(cpu_module.psutil, "getloadavg", raising=False)
    monkeypatch.setattr("os.getloadavg", lambda: (2.0, 1.5, 1.0), raising=False)

    load_avg = get_system_load_avg()
    assert load_avg == (2.0, 1.5, 1.0)


def test_get_system_load_avg_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test load average returns None gracefully if platform raises AttributeError."""
    monkeypatch.setattr("psutil.getloadavg", MagicMock(side_effect=AttributeError), raising=False)
    monkeypatch.setattr("os.getloadavg", MagicMock(side_effect=AttributeError), raising=False)

    load_avg = get_system_load_avg()
    assert load_avg is None
