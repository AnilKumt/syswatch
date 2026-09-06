"""Disk usage metrics collector using psutil."""


import psutil

from syswatch.models import DiskMetrics, DiskPartitionUsage


def collect_disk_metrics(paths: list[str] | None = None) -> DiskMetrics:
    """Collect usage metrics for a list of filesystem paths.

    Args:
        paths: List of file system directory paths to inspect. Defaults to ["/"].

    Returns:
        DiskMetrics instance containing collected partition metrics and path errors.
    """
    if not paths:
        paths = ["/"]

    partitions: list[DiskPartitionUsage] = []
    errors: dict[str, str] = {}

    for path in paths:
        try:
            usage = psutil.disk_usage(path)
            partitions.append(
                DiskPartitionUsage(
                    path=path,
                    total_bytes=int(usage.total),
                    used_bytes=int(usage.used),
                    free_bytes=int(usage.free),
                    used_percent=float(usage.percent),
                )
            )
        except (PermissionError, FileNotFoundError, OSError) as err:
            errors[path] = f"Access or path error: {err}"
        except Exception as err:  # noqa: BLE001
            errors[path] = f"Unexpected error: {err}"

    return DiskMetrics(partitions=partitions, errors=errors)
