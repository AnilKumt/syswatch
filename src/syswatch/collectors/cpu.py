"""CPU metrics collector using psutil."""

import os

import psutil

from syswatch.models import CpuMetrics


def get_system_load_avg() -> tuple[float, float, float] | None:
    """Fetch 1, 5, and 15 minute system load averages if available on the platform."""
    try:
        if hasattr(psutil, "getloadavg"):
            return psutil.getloadavg()
        if hasattr(os, "getloadavg"):
            return os.getloadavg()
    except (AttributeError, OSError):
        pass
    return None


def collect_cpu_metrics(
    interval: float | None = None, per_cpu: bool = False
) -> CpuMetrics:
    """Collect current system CPU metrics.

    Args:
        interval: Blocking interval in seconds to calculate CPU percent over.
            If None or 0.0, compares against previous call time non-blockingly.
        per_cpu: If True, includes individual usage percentage for each core.

    Returns:
        CpuMetrics dataclass instance containing collected metrics.
    """
    usage_percent = float(psutil.cpu_percent(interval=interval))
    core_count = psutil.cpu_count(logical=True) or 1
    physical_core_count = psutil.cpu_count(logical=False)
    load_avg = get_system_load_avg()

    per_cpu_percent: list[float] | None = None
    if per_cpu:
        per_cpu_percent = [
            float(val) for val in psutil.cpu_percent(interval=interval, percpu=True)
        ]

    return CpuMetrics(
        usage_percent=usage_percent,
        core_count=core_count,
        physical_core_count=physical_core_count,
        load_average=load_avg,
        per_cpu_percent=per_cpu_percent,
    )
