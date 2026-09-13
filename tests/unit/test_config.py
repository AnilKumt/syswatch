"""Unit tests for configuration loading and schema validation."""

from pathlib import Path

import pytest

from syswatch.config import AppConfig, ConfigError, load_config, validate_config_dict


def test_load_config_default() -> None:
    """Test loading configuration with None returns default AppConfig."""
    config = load_config(None)
    assert isinstance(config, AppConfig)
    assert config.interval == 2.0
    assert config.thresholds.cpu_warning == 80.0
    assert config.disk_paths == ["/"]


def test_load_config_example_file() -> None:
    """Test loading valid example YAML configuration file."""
    example_path = Path("config/example.yaml")
    if not example_path.exists():
        pytest.skip("example.yaml not found in working dir")

    config = load_config(str(example_path))
    assert config.interval == 2.0
    assert config.thresholds.cpu_warning == 80.0
    assert config.disk_paths == ["/", "/home"]


def test_load_config_missing_file() -> None:
    """Test loading a non-existent configuration file raises ConfigError."""
    with pytest.raises(ConfigError) as exc_info:
        load_config("non_existent_config.yaml")
    assert "file not found" in str(exc_info.value)


def test_load_config_invalid_yaml_syntax(tmp_path: Path) -> None:
    """Test loading malformed YAML syntax raises ConfigError."""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("thresholds: [unclosed list", encoding="utf-8")

    with pytest.raises(ConfigError) as exc_info:
        load_config(str(bad_yaml))
    assert "invalid YAML syntax" in str(exc_info.value)


def test_validate_config_dict_invalid_percentage() -> None:
    """Test threshold percentage out of 0-100 bounds raises ConfigError."""
    bad_dict = {"thresholds": {"cpu_warning": 150.0}}
    with pytest.raises(ConfigError) as exc_info:
        validate_config_dict(bad_dict)
    assert "must be between 0.0 and 100.0" in str(exc_info.value)


def test_validate_config_dict_warning_exceeds_critical() -> None:
    """Test warning threshold exceeding critical threshold raises ConfigError."""
    bad_dict = {"thresholds": {"cpu_warning": 95.0, "cpu_critical": 85.0}}
    with pytest.raises(ConfigError) as exc_info:
        validate_config_dict(bad_dict)
    assert "cannot exceed thresholds.cpu_critical" in str(exc_info.value)


def test_validate_config_dict_invalid_interval() -> None:
    """Test negative or zero interval raises ConfigError."""
    bad_dict = {"interval": -1.0}
    with pytest.raises(ConfigError) as exc_info:
        validate_config_dict(bad_dict)
    assert "interval must be greater than 0.0" in str(exc_info.value)


def test_validate_config_dict_invalid_top_n() -> None:
    """Test invalid processes top_n raises ConfigError."""
    bad_dict = {"processes": {"top_n": 0}}
    with pytest.raises(ConfigError) as exc_info:
        validate_config_dict(bad_dict)
    assert "processes.top_n must be a positive integer" in str(exc_info.value)
