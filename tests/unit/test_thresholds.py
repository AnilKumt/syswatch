"""Boundary unit tests for threshold rules and alerts."""

import pytest

from syswatch.alerts.thresholds import check_metric_alert, evaluate_threshold
from syswatch.models import HealthStatus, Severity


@pytest.mark.parametrize(
    "value, warning, critical, expected_status",
    [
        (79.9, 80.0, 90.0, HealthStatus.OK),
        (80.0, 80.0, 90.0, HealthStatus.WARNING),
        (80.1, 80.0, 90.0, HealthStatus.WARNING),
        (89.9, 80.0, 90.0, HealthStatus.WARNING),
        (90.0, 80.0, 90.0, HealthStatus.CRITICAL),
        (90.1, 80.0, 90.0, HealthStatus.CRITICAL),
        (0.0, 80.0, 90.0, HealthStatus.OK),
        (100.0, 80.0, 90.0, HealthStatus.CRITICAL),
    ],
)
def test_evaluate_threshold_boundaries(
    value: float, warning: float, critical: float, expected_status: HealthStatus
) -> None:
    """Test boundary conditions for threshold evaluation rules."""
    assert evaluate_threshold(value, warning, critical) == expected_status


def test_check_metric_alert_trigger() -> None:
    """Test alert creation for WARNING and CRITICAL levels."""
    ok_alert = check_metric_alert("CPU", 50.0, 80.0, 90.0)
    assert ok_alert is None

    warn_alert = check_metric_alert("CPU", 85.0, 80.0, 90.0)
    assert warn_alert is not None
    assert warn_alert.severity == Severity.WARNING
    assert "WARNING" in warn_alert.message
    assert warn_alert.threshold == 80.0

    crit_alert = check_metric_alert("CPU", 95.0, 80.0, 90.0)
    assert crit_alert is not None
    assert crit_alert.severity == Severity.CRITICAL
    assert "CRITICAL" in crit_alert.message
    assert crit_alert.threshold == 90.0
