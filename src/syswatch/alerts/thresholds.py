"""Threshold evaluation rules and alert configuration models."""

from dataclasses import dataclass

from syswatch.models import Alert, HealthStatus, Severity


@dataclass
class ThresholdConfig:
    """Configured health evaluation threshold limits."""

    cpu_warning: float = 80.0
    cpu_critical: float = 90.0
    memory_warning: float = 80.0
    memory_critical: float = 90.0
    swap_warning: float = 70.0
    swap_critical: float = 85.0
    disk_warning: float = 85.0
    disk_critical: float = 95.0


def evaluate_threshold(value: float, warning: float, critical: float) -> HealthStatus:
    """Evaluate a numeric metric value against warning and critical thresholds.

    Rules:
        - value >= critical  -> HealthStatus.CRITICAL
        - value >= warning   -> HealthStatus.WARNING
        - value < warning    -> HealthStatus.OK

    Args:
        value: Observed metric percentage/value.
        warning: Warning threshold level.
        critical: Critical threshold level.

    Returns:
        HealthStatus enum value.
    """
    if value >= critical:
        return HealthStatus.CRITICAL
    if value >= warning:
        return HealthStatus.WARNING
    return HealthStatus.OK


def check_metric_alert(
    metric_name: str,
    value: float,
    warning_threshold: float,
    critical_threshold: float,
    unit: str = "%",
) -> Alert | None:
    """Check if a metric triggers a Warning or Critical alert.

    Returns:
        Alert instance if threshold exceeded, otherwise None.
    """
    status = evaluate_threshold(value, warning_threshold, critical_threshold)
    if status == HealthStatus.CRITICAL:
        return Alert(
            metric_name=metric_name,
            value=value,
            threshold=critical_threshold,
            severity=Severity.CRITICAL,
            message=f"{metric_name} usage is CRITICAL: {value:.1f}{unit} (threshold: {critical_threshold:.1f}{unit})",
        )
    if status == HealthStatus.WARNING:
        return Alert(
            metric_name=metric_name,
            value=value,
            threshold=warning_threshold,
            severity=Severity.WARNING,
            message=f"{metric_name} usage is WARNING: {value:.1f}{unit} (threshold: {warning_threshold:.1f}{unit})",
        )
    return None
