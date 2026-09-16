"""Unit tests for Process metrics collector."""

import psutil
import pytest

from syswatch.collectors.processes import collect_process_metrics
from syswatch.models import ProcessMetrics


class BadProc:
    """Mock process object raising NoSuchProcess when accessing info property."""

    @property
    def info(self):
        raise psutil.NoSuchProcess(pid=999)


class GoodProc:
    """Mock process object returning valid info dictionary."""

    def __init__(self, pid: int, name: str, cpu: float, mem: float, status: str, user: str):
        self._info = {
            "pid": pid,
            "name": name,
            "cpu_percent": cpu,
            "memory_percent": mem,
            "status": status,
            "username": user,
        }

    @property
    def info(self):
        return self._info


def test_collect_process_metrics_sorting(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test process metric collection and sorting by CPU and Memory."""
    p1 = GoodProc(101, "python", 50.0, 10.0, "running", "user")
    p2 = GoodProc(102, "chrome", 10.0, 40.0, "sleeping", "user")
    p3 = GoodProc(103, "code", 30.0, 20.0, "running", "user")

    monkeypatch.setattr("psutil.process_iter", lambda attrs: [p1, p2, p3])

    # Sort by CPU
    cpu_metrics = collect_process_metrics(sort_by="cpu", limit=2)
    assert isinstance(cpu_metrics, ProcessMetrics)
    assert cpu_metrics.total_processes == 3
    assert len(cpu_metrics.processes) == 2
    assert cpu_metrics.processes[0].name == "python"
    assert cpu_metrics.processes[1].name == "code"

    # Sort by Memory
    mem_metrics = collect_process_metrics(sort_by="memory", limit=2)
    assert len(mem_metrics.processes) == 2
    assert mem_metrics.processes[0].name == "chrome"
    assert mem_metrics.processes[1].name == "code"


def test_collect_process_metrics_handles_disappearing_process(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test process collector handles NoSuchProcess or AccessDenied mid-scan gracefully."""
    p1 = GoodProc(201, "systemd", 1.0, 1.0, "running", "root")
    p2 = BadProc()

    monkeypatch.setattr("psutil.process_iter", lambda attrs: [p1, p2])

    metrics = collect_process_metrics()
    assert metrics.total_processes == 2
    assert len(metrics.processes) == 1
    assert metrics.processes[0].name == "systemd"
