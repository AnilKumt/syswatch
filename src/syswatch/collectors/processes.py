"""Process metrics collector using psutil."""


import psutil

from syswatch.models import ProcessInfo, ProcessMetrics


def collect_process_metrics(sort_by: str = "cpu", limit: int = 10) -> ProcessMetrics:
    """Collect running system process statistics, sorted by CPU or Memory usage.

    Args:
        sort_by: Metric attribute to sort processes by ('cpu' or 'memory').
        limit: Maximum number of top processes to return.

    Returns:
        ProcessMetrics dataclass containing top N process records and total count.
    """
    procs: list[ProcessInfo] = []
    total_count = 0

    for proc in psutil.process_iter(
        attrs=["pid", "name", "cpu_percent", "memory_percent", "status", "username"]
    ):
        try:
            total_count += 1
            info = proc.info
            p_info = ProcessInfo(
                pid=int(info["pid"]),
                name=str(info["name"] or "unknown"),
                cpu_percent=float(info["cpu_percent"] or 0.0),
                memory_percent=float(info["memory_percent"] or 0.0),
                status=str(info["status"] or "unknown"),
                username=str(info["username"]) if info.get("username") else None,
            )
            procs.append(p_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        except Exception:  # noqa: BLE001, S112
            continue

    # Sort processes
    sort_key = (
        (lambda p: p.memory_percent)
        if sort_by.lower() == "memory"
        else (lambda p: p.cpu_percent)
    )
    sorted_procs = sorted(procs, key=sort_key, reverse=True)

    return ProcessMetrics(
        processes=sorted_procs[: max(1, limit)],
        total_processes=total_count,
    )
