"""Integration tests for CLI commands and options."""

import json
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from syswatch import __version__
from syswatch.cli import cli


def test_cli_version(cli_runner: CliRunner) -> None:
    """Verify `syswatch --version` outputs current package version."""
    result = cli_runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output
    assert "syswatch" in result.output


def test_cli_help(cli_runner: CliRunner) -> None:
    """Verify `syswatch --help` prints usage information."""
    result = cli_runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "syswatch: Production-Quality Linux System Health Monitor CLI." in result.output
    assert "status" in result.output
    assert "monitor" in result.output
    assert "processes" in result.output
    assert "config" in result.output


def test_cli_status_command(cli_runner: CliRunner) -> None:
    """Verify `syswatch status` command executes cleanly and displays Rich health report."""
    result = cli_runner.invoke(cli, ["status"])
    assert result.exit_code in (0, 1, 2)
    assert "SYSWATCH SYSTEM HEALTH REPORT" in result.output


def test_cli_status_json_command(cli_runner: CliRunner) -> None:
    """Verify `syswatch status --json` outputs valid machine-readable JSON."""
    result = cli_runner.invoke(cli, ["status", "--json"])
    assert result.exit_code in (0, 1, 2)

    parsed = json.loads(result.output)
    assert "status" in parsed
    assert "hostname" in parsed
    assert "cpu" in parsed
    assert "memory" in parsed
    assert "disk" in parsed


def test_cli_processes_command(cli_runner: CliRunner) -> None:
    """Verify `syswatch processes` command displays Rich process table."""
    result = cli_runner.invoke(cli, ["processes", "--sort", "cpu", "--limit", "5"])
    assert result.exit_code == 0
    assert "SYSWATCH TOP PROCESSES" in result.output
    assert "PID" in result.output


def test_cli_processes_json_command(cli_runner: CliRunner) -> None:
    """Verify `syswatch processes --json` outputs machine-readable JSON process list."""
    result = cli_runner.invoke(cli, ["processes", "--sort", "memory", "--limit", "5", "--json"])
    assert result.exit_code == 0

    parsed = json.loads(result.output)
    assert "total_processes" in parsed
    assert "processes" in parsed
    assert isinstance(parsed["processes"], list)


def test_cli_monitor_keyboard_interrupt(cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify `syswatch monitor` handles Ctrl+C (KeyboardInterrupt) cleanly with exit code 0."""
    mock_run_live = MagicMock(side_effect=KeyboardInterrupt)
    monkeypatch.setattr("syswatch.services.monitor.ContinuousMonitorService.run_live", mock_run_live)

    result = cli_runner.invoke(cli, ["monitor"])
    assert result.exit_code == 0
    assert "Monitoring stopped by user." in result.output


def test_cli_status_with_config(cli_runner: CliRunner) -> None:
    """Verify `syswatch --config config/example.yaml status` executes with custom config."""
    result = cli_runner.invoke(cli, ["--config", "config/example.yaml", "status"])
    assert result.exit_code in (0, 1, 2)
    assert "SYSWATCH SYSTEM HEALTH REPORT" in result.output


def test_cli_config_validate_command(cli_runner: CliRunner) -> None:
    """Verify `syswatch --config config/example.yaml config validate` validates file."""
    result = cli_runner.invoke(cli, ["--config", "config/example.yaml", "config", "validate"])
    assert result.exit_code == 0
    assert "Configuration file 'config/example.yaml' is valid." in result.output


def test_cli_config_validate_without_file(cli_runner: CliRunner) -> None:
    """Verify `syswatch config validate` without --config errors gracefully."""
    result = cli_runner.invoke(cli, ["config", "validate"])
    assert result.exit_code == 1
    assert "No configuration file specified" in result.output


def test_cli_invalid_config_error_handling(cli_runner: CliRunner) -> None:
    """Verify invalid config produces user-friendly error without stack trace."""
    result = cli_runner.invoke(cli, ["--config", "non_existent.yaml", "status"])
    assert result.exit_code == 2
