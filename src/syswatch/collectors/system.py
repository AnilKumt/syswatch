"""System information and uptime collector."""

import platform
import time

import psutil

from syswatch.models import SystemMetrics


def collect_system_metrics() -> SystemMetrics:
    """Collect OS platform information, kernel version, hostname, and system uptime.

    Returns:
        SystemMetrics dataclass instance containing system identity and uptime.
    """
    boot_time = float(psutil.boot_time())
    now = time.time()
    uptime = max(0.0, now - boot_time)

    return SystemMetrics(
        hostname=platform.node() or "unknown",
        os_name=platform.system() or "Linux",
        os_release=platform.release() or "unknown",
        architecture=platform.machine() or "unknown",
        boot_time_timestamp=boot_time,
        uptime_seconds=uptime,
    )
