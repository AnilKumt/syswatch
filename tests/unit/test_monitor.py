"""Unit tests for ContinuousMonitorService engine."""

import pytest
from rich.console import Console

from syswatch.services.monitor import ContinuousMonitorService


def test_monitor_collect_snapshot() -> None:
    """Test collect_snapshot computes time delta and returns OverallHealth object."""
    monitor = ContinuousMonitorService()

    snapshot1 = monitor.collect_snapshot()
    assert snapshot1 is not None
    assert snapshot1.cpu_metrics is not None

    snapshot2 = monitor.collect_snapshot()
    assert snapshot2 is not None


def test_monitor_run_live_json(capsys: pytest.CaptureFixture[str]) -> None:
    """Test run_live streaming JSON output for specified max_iterations."""
    monitor = ContinuousMonitorService()
    monitor.run_live(interval=0.001, json_output=True, max_iterations=2)

    captured = capsys.readouterr()
    lines = [line for line in captured.out.strip().split("\n") if line]
    assert len(lines) == 2
    assert '"status":' in lines[0]
    assert '"hostname":' in lines[1]


def test_monitor_run_live_rich() -> None:
    """Test run_live rendering Rich Live display for specified max_iterations."""
    console = Console(record=True, width=100)
    monitor = ContinuousMonitorService(console=console)
    monitor.run_live(interval=0.001, json_output=False, max_iterations=2)

    output = console.export_text()
    assert "SYSWATCH LIVE MONITORING" in output
