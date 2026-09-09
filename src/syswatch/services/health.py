"""Health evaluation service layer for syswatch metrics."""


from syswatch.alerts.thresholds import (
    ThresholdConfig,
    check_metric_alert,
    evaluate_threshold,
)
from syswatch.models import (
    Alert,
    CpuMetrics,
    DiskMetrics,
    HealthStatus,
    MemoryMetrics,
    NetworkMetrics,
    OverallHealth,
    SwapMetrics,
    SystemMetrics,
)


class HealthEvaluatorService:
    """Service evaluating system health metrics against configured thresholds."""

    def __init__(self, config: ThresholdConfig | None = None) -> None:
        self.config = config or ThresholdConfig()

    def _determine_overall_status(self, statuses: list[HealthStatus]) -> HealthStatus:
        """Determine worst-case overall status from a list of component health statuses."""
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        if HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        if HealthStatus.UNKNOWN in statuses:
            return HealthStatus.UNKNOWN
        return HealthStatus.OK

    def evaluate(
        self,
        system_metrics: SystemMetrics | None = None,
        cpu_metrics: CpuMetrics | None = None,
        memory_metrics: MemoryMetrics | None = None,
        swap_metrics: SwapMetrics | None = None,
        disk_metrics: DiskMetrics | None = None,
        network_metrics: NetworkMetrics | None = None,
    ) -> OverallHealth:
        """Evaluate system health snapshot against thresholds and return OverallHealth object.

        Args:
            system_metrics: System platform metrics.
            cpu_metrics: CPU utilization metrics.
            memory_metrics: RAM memory usage metrics.
            swap_metrics: Swap space usage metrics.
            disk_metrics: Partition disk usage metrics.
            network_metrics: Network statistics metrics.

        Returns:
            OverallHealth dataclass populated with status enums and active alerts.
        """
        alerts: list[Alert] = []
        statuses: list[HealthStatus] = []

        # Evaluate CPU
        if cpu_metrics is not None:
            cpu_status = evaluate_threshold(
                cpu_metrics.usage_percent,
                self.config.cpu_warning,
                self.config.cpu_critical,
            )
            alert = check_metric_alert(
                "CPU",
                cpu_metrics.usage_percent,
                self.config.cpu_warning,
                self.config.cpu_critical,
            )
            if alert:
                alerts.append(alert)
        else:
            cpu_status = HealthStatus.UNKNOWN
        statuses.append(cpu_status)

        # Evaluate Memory
        if memory_metrics is not None:
            memory_status = evaluate_threshold(
                memory_metrics.used_percent,
                self.config.memory_warning,
                self.config.memory_critical,
            )
            alert = check_metric_alert(
                "Memory",
                memory_metrics.used_percent,
                self.config.memory_warning,
                self.config.memory_critical,
            )
            if alert:
                alerts.append(alert)
        else:
            memory_status = HealthStatus.UNKNOWN
        statuses.append(memory_status)

        # Evaluate Swap
        if swap_metrics is not None:
            swap_status = evaluate_threshold(
                swap_metrics.used_percent,
                self.config.swap_warning,
                self.config.swap_critical,
            )
            alert = check_metric_alert(
                "Swap",
                swap_metrics.used_percent,
                self.config.swap_warning,
                self.config.swap_critical,
            )
            if alert:
                alerts.append(alert)
        else:
            swap_status = HealthStatus.UNKNOWN
        statuses.append(swap_status)

        # Evaluate Disk (Worst status across all partitions)
        disk_status = HealthStatus.OK
        if disk_metrics is not None and disk_metrics.partitions:
            partition_statuses: list[HealthStatus] = []
            for part in disk_metrics.partitions:
                p_status = evaluate_threshold(
                    part.used_percent,
                    self.config.disk_warning,
                    self.config.disk_critical,
                )
                partition_statuses.append(p_status)
                alert = check_metric_alert(
                    f"Disk ({part.path})",
                    part.used_percent,
                    self.config.disk_warning,
                    self.config.disk_critical,
                )
                if alert:
                    alerts.append(alert)
            disk_status = self._determine_overall_status(partition_statuses)
        elif disk_metrics is None:
            disk_status = HealthStatus.UNKNOWN
        statuses.append(disk_status)

        overall_status = self._determine_overall_status(statuses)

        return OverallHealth(
            status=overall_status,
            cpu_status=cpu_status,
            memory_status=memory_status,
            swap_status=swap_status,
            disk_status=disk_status,
            alerts=alerts,
            system_metrics=system_metrics,
            cpu_metrics=cpu_metrics,
            memory_metrics=memory_metrics,
            swap_metrics=swap_metrics,
            disk_metrics=disk_metrics,
            network_metrics=network_metrics,
        )
