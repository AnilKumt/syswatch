"""Memory and Swap metrics collector using psutil."""

import psutil

from syswatch.models import MemoryMetrics, SwapMetrics


def collect_memory_metrics() -> MemoryMetrics:
    """Collect system RAM usage metrics.

    Returns:
        MemoryMetrics dataclass instance containing memory statistics in bytes.
    """
    vmem = psutil.virtual_memory()
    return MemoryMetrics(
        total_bytes=int(vmem.total),
        available_bytes=int(vmem.available),
        used_bytes=int(vmem.used),
        used_percent=float(vmem.percent),
    )


def collect_swap_metrics() -> SwapMetrics:
    """Collect system Swap space metrics.

    Returns:
        SwapMetrics dataclass instance containing swap statistics in bytes.
    """
    swap = psutil.swap_memory()
    return SwapMetrics(
        total_bytes=int(swap.total),
        used_bytes=int(swap.used),
        free_bytes=int(swap.free),
        used_percent=float(swap.percent),
    )
