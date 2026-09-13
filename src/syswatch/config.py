"""Configuration loading, schema definition, and validation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from syswatch.alerts.thresholds import ThresholdConfig


class ConfigError(Exception):
    """Exception raised for user configuration loading or validation errors."""



@dataclass
class AppConfig:
    """Master application configuration data model."""

    interval: float = 2.0
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    disk_paths: list[str] = field(default_factory=lambda: ["/"])
    network_enabled: bool = True
    processes_enabled: bool = True
    processes_top_n: int = 10


def _validate_percentage(val: Any, field_name: str) -> float:
    """Validate that a metric threshold percentage is a float between 0.0 and 100.0."""
    try:
        pct = float(val)
    except (TypeError, ValueError):
        raise ConfigError(f"Configuration error: {field_name} must be a valid number, got '{val}'")

    if not (0.0 <= pct <= 100.0):
        raise ConfigError(
            f"Configuration error: {field_name} must be between 0.0 and 100.0 (got {pct:.1f})"
        )
    return pct


def validate_config_dict(data: dict[str, Any]) -> AppConfig:
    """Validate a configuration dictionary and construct an AppConfig object.

    Raises:
        ConfigError: If any value is out of bounds or invalid.
    """
    if not isinstance(data, dict):
        raise ConfigError("Configuration error: YAML root must be a mapping/dictionary")

    # 1. Interval
    interval_raw = data.get("interval", 2.0)
    try:
        interval = float(interval_raw)
    except (TypeError, ValueError):
        raise ConfigError(f"Configuration error: interval must be a number, got '{interval_raw}'")

    if interval <= 0.0:
        raise ConfigError(f"Configuration error: interval must be greater than 0.0 (got {interval})")

    # 2. Thresholds
    thresh_data = data.get("thresholds", {})
    if not isinstance(thresh_data, dict):
        raise ConfigError("Configuration error: 'thresholds' must be a dictionary")

    cpu_warn = _validate_percentage(thresh_data.get("cpu_warning", 80.0), "thresholds.cpu_warning")
    cpu_crit = _validate_percentage(thresh_data.get("cpu_critical", 90.0), "thresholds.cpu_critical")
    if cpu_warn > cpu_crit:
        raise ConfigError(
            f"Configuration error: thresholds.cpu_warning ({cpu_warn}) cannot exceed thresholds.cpu_critical ({cpu_crit})"
        )

    mem_warn = _validate_percentage(thresh_data.get("memory_warning", 80.0), "thresholds.memory_warning")
    mem_crit = _validate_percentage(thresh_data.get("memory_critical", 90.0), "thresholds.memory_critical")
    if mem_warn > mem_crit:
        raise ConfigError(
            f"Configuration error: thresholds.memory_warning ({mem_warn}) cannot exceed thresholds.memory_critical ({mem_crit})"
        )

    swap_warn = _validate_percentage(thresh_data.get("swap_warning", 70.0), "thresholds.swap_warning")
    swap_crit = _validate_percentage(thresh_data.get("swap_critical", 85.0), "thresholds.swap_critical")
    if swap_warn > swap_crit:
        raise ConfigError(
            f"Configuration error: thresholds.swap_warning ({swap_warn}) cannot exceed thresholds.swap_critical ({swap_crit})"
        )

    disk_warn = _validate_percentage(thresh_data.get("disk_warning", 85.0), "thresholds.disk_warning")
    disk_crit = _validate_percentage(thresh_data.get("disk_critical", 95.0), "thresholds.disk_critical")
    if disk_warn > disk_crit:
        raise ConfigError(
            f"Configuration error: thresholds.disk_warning ({disk_warn}) cannot exceed thresholds.disk_critical ({disk_crit})"
        )

    threshold_config = ThresholdConfig(
        cpu_warning=cpu_warn,
        cpu_critical=cpu_crit,
        memory_warning=mem_warn,
        memory_critical=mem_crit,
        swap_warning=swap_warn,
        swap_critical=swap_crit,
        disk_warning=disk_warn,
        disk_critical=disk_crit,
    )

    # 3. Disk Paths
    disk_data = data.get("disk", {})
    disk_paths = ["/"]
    if isinstance(disk_data, dict) and "paths" in disk_data:
        paths = disk_data["paths"]
        if isinstance(paths, list):
            disk_paths = [str(p) for p in paths if p]

    # 4. Network
    net_data = data.get("network", {})
    net_enabled = True
    if isinstance(net_data, dict) and "enabled" in net_data:
        net_enabled = bool(net_data["enabled"])

    # 5. Processes
    proc_data = data.get("processes", {})
    proc_enabled = True
    proc_top_n = 10
    if isinstance(proc_data, dict):
        if "enabled" in proc_data:
            proc_enabled = bool(proc_data["enabled"])
        if "top_n" in proc_data:
            try:
                proc_top_n = int(proc_data["top_n"])
                if proc_top_n < 1:
                    raise ValueError
            except (TypeError, ValueError):
                raise ConfigError(f"Configuration error: processes.top_n must be a positive integer, got '{proc_data['top_n']}'")

    return AppConfig(
        interval=interval,
        thresholds=threshold_config,
        disk_paths=disk_paths,
        network_enabled=net_enabled,
        processes_enabled=proc_enabled,
        processes_top_n=proc_top_n,
    )


def load_config(config_path: str | None = None) -> AppConfig:
    """Load configuration from a YAML file path or return default AppConfig if None.

    Args:
        config_path: Path to YAML configuration file.

    Returns:
        Validated AppConfig instance.

    Raises:
        ConfigError: If file is missing, malformed, or contains invalid parameters.
    """
    if config_path is None:
        return AppConfig()

    path = Path(config_path)
    if not path.is_file():
        raise ConfigError(f"Configuration error: file not found at '{config_path}'")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as err:
        raise ConfigError(f"Configuration error: invalid YAML syntax in '{config_path}': {err}")
    except Exception as err:  # noqa: BLE001
        raise ConfigError(f"Configuration error: unable to read file '{config_path}': {err}")

    if data is None:
        return AppConfig()

    return validate_config_dict(data)
