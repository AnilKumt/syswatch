"""Unit tests for Network metrics collector."""

from collections import namedtuple

import pytest

from syswatch.collectors.network import collect_network_metrics
from syswatch.models import NetworkMetrics

NetIoMock = namedtuple(
    "NetIoMock",
    [
        "bytes_sent",
        "bytes_recv",
        "packets_sent",
        "packets_recv",
        "errin",
        "errout",
        "dropin",
        "dropout",
    ],
)


def test_collect_network_metrics_cumulative(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test gathering cumulative network metrics per interface."""
    mock_net_io = {
        "eth0": NetIoMock(1000, 2000, 10, 20, 0, 0, 0, 0),
        "lo": NetIoMock(500, 500, 5, 5, 0, 0, 0, 0),
    }
    monkeypatch.setattr("psutil.net_io_counters", lambda pernic=True: mock_net_io)

    metrics = collect_network_metrics()

    assert isinstance(metrics, NetworkMetrics)
    assert metrics.total_bytes_sent == 1500
    assert metrics.total_bytes_recv == 2500
    assert metrics.total_packets_sent == 15
    assert metrics.total_packets_recv == 25
    assert len(metrics.interfaces) == 2
    assert metrics.bytes_sent_per_sec == 0.0
    assert metrics.bytes_recv_per_sec == 0.0


def test_collect_network_metrics_rate_calculation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test transfer rate calculation given previous metrics and time delta."""
    mock_net_io_1 = {"eth0": NetIoMock(1000, 2000, 10, 20, 0, 0, 0, 0)}
    monkeypatch.setattr("psutil.net_io_counters", lambda pernic=True: mock_net_io_1)
    prev_metrics = collect_network_metrics()

    # Simulate 2 seconds passing with 2000 additional bytes sent and 4000 received
    mock_net_io_2 = {"eth0": NetIoMock(3000, 6000, 30, 60, 0, 0, 0, 0)}
    monkeypatch.setattr("psutil.net_io_counters", lambda pernic=True: mock_net_io_2)

    new_metrics = collect_network_metrics(prev_metrics=prev_metrics, time_delta=2.0)

    assert new_metrics.bytes_sent_per_sec == 1000.0  # (3000 - 1000) / 2.0
    assert new_metrics.bytes_recv_per_sec == 2000.0  # (6000 - 2000) / 2.0
