"""Metrics collectors subpackage for syswatch."""

from syswatch.collectors.cpu import collect_cpu_metrics
from syswatch.collectors.disk import collect_disk_metrics
from syswatch.collectors.memory import collect_memory_metrics, collect_swap_metrics
from syswatch.collectors.network import collect_network_metrics
from syswatch.collectors.processes import collect_process_metrics
from syswatch.collectors.system import collect_system_metrics

__all__ = [
    "collect_cpu_metrics",
    "collect_disk_metrics",
    "collect_memory_metrics",
    "collect_network_metrics",
    "collect_process_metrics",
    "collect_swap_metrics",
    "collect_system_metrics",
]
