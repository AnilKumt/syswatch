"""Machine-readable JSON serialization renderer for syswatch health reports and processes."""

import json
from datetime import UTC, datetime
from typing import Any

from syswatch.models import OverallHealth, ProcessMetrics


def render_json_report(health: OverallHealth, indent: int | None = 2) -> str:
    """Serialize OverallHealth snapshot into a structured, machine-readable JSON string."""
    now_utc = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    data: dict[str, Any] = {
        "timestamp": now_utc,
        "status": health.status.value,
        "hostname": health.system_metrics.hostname if health.system_metrics else "unknown",
        "os": {
            "name": health.system_metrics.os_name if health.system_metrics else "unknown",
            "release": health.system_metrics.os_release if health.system_metrics else "unknown",
            "architecture": health.system_metrics.architecture if health.system_metrics else "unknown",
            "uptime_seconds": health.system_metrics.uptime_seconds if health.system_metrics else 0.0,
        },
        "cpu": {
            "status": health.cpu_status.value,
            "usage_percent": health.cpu_metrics.usage_percent if health.cpu_metrics else 0.0,
            "core_count": health.cpu_metrics.core_count if health.cpu_metrics else 0,
            "load_average": list(health.cpu_metrics.load_average) if health.cpu_metrics and health.cpu_metrics.load_average else None,
        },
        "memory": {
            "status": health.memory_status.value,
            "used_percent": health.memory_metrics.used_percent if health.memory_metrics else 0.0,
            "used_bytes": health.memory_metrics.used_bytes if health.memory_metrics else 0,
            "total_bytes": health.memory_metrics.total_bytes if health.memory_metrics else 0,
            "available_bytes": health.memory_metrics.available_bytes if health.memory_metrics else 0,
        },
        "swap": {
            "status": health.swap_status.value,
            "used_percent": health.swap_metrics.used_percent if health.swap_metrics else 0.0,
            "used_bytes": health.swap_metrics.used_bytes if health.swap_metrics else 0,
            "total_bytes": health.swap_metrics.total_bytes if health.swap_metrics else 0,
        },
        "disk": {
            "status": health.disk_status.value,
            "partitions": {
                part.path: {
                    "used_percent": part.used_percent,
                    "used_bytes": part.used_bytes,
                    "total_bytes": part.total_bytes,
                    "free_bytes": part.free_bytes,
                }
                for part in health.disk_metrics.partitions
            }
            if health.disk_metrics
            else {},
            "errors": health.disk_metrics.errors if health.disk_metrics else {},
        },
        "network": {
            "total_bytes_sent": health.network_metrics.total_bytes_sent if health.network_metrics else 0,
            "total_bytes_recv": health.network_metrics.total_bytes_recv if health.network_metrics else 0,
            "bytes_sent_per_sec": health.network_metrics.bytes_sent_per_sec if health.network_metrics else 0.0,
            "bytes_recv_per_sec": health.network_metrics.bytes_recv_per_sec if health.network_metrics else 0.0,
        },
        "alerts": [
            {
                "metric": alert.metric_name,
                "severity": alert.severity.value,
                "value": alert.value,
                "threshold": alert.threshold,
                "message": alert.message,
            }
            for alert in health.alerts
        ],
    }

    return json.dumps(data, indent=indent)


def render_process_json(metrics: ProcessMetrics, indent: int | None = 2) -> str:
    """Serialize ProcessMetrics snapshot into JSON string format.

    Args:
        metrics: ProcessMetrics instance.
        indent: Indentation spaces.

    Returns:
        JSON string.
    """
    now_utc = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    data = {
        "timestamp": now_utc,
        "total_processes": metrics.total_processes,
        "processes": [
            {
                "pid": p.pid,
                "name": p.name,
                "username": p.username,
                "cpu_percent": p.cpu_percent,
                "memory_percent": p.memory_percent,
                "status": p.status,
            }
            for p in metrics.processes
        ],
    }
    return json.dumps(data, indent=indent)
