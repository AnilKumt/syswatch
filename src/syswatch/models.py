"""Core domain data models for syswatch metrics, alerts, and health status."""

from dataclasses import dataclass, field
from enum import Enum


class HealthStatus(str, Enum):
    """System and component health status levels."""

    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class Severity(str, Enum):
    """Alert severity levels."""

    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class Alert:
    """Triggered health threshold alert."""

    metric_name: str
    value: float
    threshold: float
    severity: Severity
    message: str


@dataclass
class CpuMetrics:
    """CPU metrics data model."""

    usage_percent: float
    core_count: int
    physical_core_count: int | None = None
    load_average: tuple[float, float, float] | None = None
    per_cpu_percent: list[float] | None = None


@dataclass
class MemoryMetrics:
    """RAM memory metrics data model."""

    total_bytes: int
    available_bytes: int
    used_bytes: int
    used_percent: float


@dataclass
class SwapMetrics:
    """Swap space metrics data model."""

    total_bytes: int
    used_bytes: int
    free_bytes: int
    used_percent: float


@dataclass
class DiskPartitionUsage:
    """Usage metrics for a single disk partition/path."""

    path: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    used_percent: float


@dataclass
class DiskMetrics:
    """Aggregated disk usage metrics for monitored paths."""

    partitions: list[DiskPartitionUsage] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)


@dataclass
class NetworkInterfaceStats:
    """Statistics for a single network interface."""

    name: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int


@dataclass
class NetworkMetrics:
    """Aggregated network statistics and rate metrics."""

    total_bytes_sent: int
    total_bytes_recv: int
    total_packets_sent: int
    total_packets_recv: int
    interfaces: list[NetworkInterfaceStats] = field(default_factory=list)
    bytes_sent_per_sec: float = 0.0
    bytes_recv_per_sec: float = 0.0


@dataclass
class SystemMetrics:
    """Operating system and system hardware info data model."""

    hostname: str
    os_name: str
    os_release: str
    architecture: str
    boot_time_timestamp: float
    uptime_seconds: float


@dataclass
class ProcessInfo:
    """Single process information dataclass."""

    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str
    username: str | None = None


@dataclass
class ProcessMetrics:
    """Aggregated system processes snapshot."""

    processes: list[ProcessInfo] = field(default_factory=list)
    total_processes: int = 0


@dataclass
class OverallHealth:
    """Comprehensive system health evaluation snapshot."""

    status: HealthStatus
    cpu_status: HealthStatus
    memory_status: HealthStatus
    swap_status: HealthStatus
    disk_status: HealthStatus
    alerts: list[Alert] = field(default_factory=list)
    system_metrics: SystemMetrics | None = None
    cpu_metrics: CpuMetrics | None = None
    memory_metrics: MemoryMetrics | None = None
    swap_metrics: SwapMetrics | None = None
    disk_metrics: DiskMetrics | None = None
    network_metrics: NetworkMetrics | None = None
