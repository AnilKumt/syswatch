"""Pytest configuration and shared test fixtures."""

import pytest
from click.testing import CliRunner


@pytest.fixture
def cli_runner() -> CliRunner:
    """Fixture providing Click CLI test runner instance."""
    return CliRunner()
