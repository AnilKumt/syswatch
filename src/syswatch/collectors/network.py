"""Network metrics collector using psutil."""


import psutil

from syswatch.models import NetworkInterfaceStats, NetworkMetrics


def collect_network_metrics(
    prev_metrics: NetworkMetrics | None = None,
    time_delta: float | None = None,
) -> NetworkMetrics:
    """Collect system network interface statistics and calculate transfer rates.

    Args:
        prev_metrics: Previous NetworkMetrics snapshot used to calculate transfer rates.
        time_delta: Time difference in seconds between prev_metrics and current sample.

    Returns:
        NetworkMetrics dataclass containing cumulative metrics and calculated rates.
    """
    net_io = psutil.net_io_counters(pernic=True)

    interfaces: list[NetworkInterfaceStats] = []
    total_sent = 0
    total_recv = 0
    total_pkts_sent = 0
    total_pkts_recv = 0

    for name, stats in net_io.items():
        if_stats = NetworkInterfaceStats(
            name=name,
            bytes_sent=int(stats.bytes_sent),
            bytes_recv=int(stats.bytes_recv),
            packets_sent=int(stats.packets_sent),
            packets_recv=int(stats.packets_recv),
            errin=int(stats.errin),
            errout=int(stats.errout),
            dropin=int(stats.dropin),
            dropout=int(stats.dropout),
        )
        interfaces.append(if_stats)

        total_sent += if_stats.bytes_sent
        total_recv += if_stats.bytes_recv
        total_pkts_sent += if_stats.packets_sent
        total_pkts_recv += if_stats.packets_recv

    bytes_sent_per_sec = 0.0
    bytes_recv_per_sec = 0.0

    if prev_metrics is not None and time_delta is not None and time_delta > 0:
        sent_diff = max(0, total_sent - prev_metrics.total_bytes_sent)
        recv_diff = max(0, total_recv - prev_metrics.total_bytes_recv)
        bytes_sent_per_sec = sent_diff / time_delta
        bytes_recv_per_sec = recv_diff / time_delta

    return NetworkMetrics(
        total_bytes_sent=total_sent,
        total_bytes_recv=total_recv,
        total_packets_sent=total_pkts_sent,
        total_packets_recv=total_pkts_recv,
        interfaces=interfaces,
        bytes_sent_per_sec=bytes_sent_per_sec,
        bytes_recv_per_sec=bytes_recv_per_sec,
    )
