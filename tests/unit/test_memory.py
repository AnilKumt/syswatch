"""Unit tests for Memory and Swap collectors."""

from collections import namedtuple

import pytest

from syswatch.collectors.memory import collect_memory_metrics, collect_swap_metrics
from syswatch.models import MemoryMetrics, SwapMetrics

VmemMock = namedtuple("VmemMock", ["total", "available", "used", "percent"])
SwapMock = namedtuple("SwapMock", ["total", "used", "free", "percent"])


def test_collect_memory_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test virtual memory metric collection."""
    mock_vmem = VmemMock(
        total=16_000_000_000,
        available=4_000_000_000,
        used=12_000_000_000,
        percent=75.0,
    )
    monkeypatch.setattr("psutil.virtual_memory", lambda: mock_vmem)

    metrics = collect_memory_metrics()

    assert isinstance(metrics, MemoryMetrics)
    assert metrics.total_bytes == 16_000_000_000
    assert metrics.available_bytes == 4_000_000_000
    assert metrics.used_bytes == 12_000_000_000
    assert metrics.used_percent == 75.0


def test_collect_swap_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test swap space metric collection."""
    mock_swap = SwapMock(
        total=8_000_000_000,
        used=2_000_000_000,
        free=6_000_000_000,
        percent=25.0,
    )
    monkeypatch.setattr("psutil.swap_memory", lambda: mock_swap)

    metrics = collect_swap_metrics()

    assert isinstance(metrics, SwapMetrics)
    assert metrics.total_bytes == 8_000_000_000
    assert metrics.used_bytes == 2_000_000_000
    assert metrics.free_bytes == 6_000_000_000
    assert metrics.used_percent == 25.0
