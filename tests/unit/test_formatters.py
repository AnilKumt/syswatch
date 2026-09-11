"""Unit tests for human-readable output formatters."""

from syswatch.output.formatters import format_bytes, format_rate, format_uptime


def test_format_bytes() -> None:
    """Test raw byte values formatted into human-readable binary units."""
    assert format_bytes(0) == "0 B"
    assert format_bytes(500) == "500 B"
    assert format_bytes(1024) == "1.0 KiB"
    assert format_bytes(1048576) == "1.0 MiB"
    assert format_bytes(8804682956) == "8.2 GiB"
    assert format_bytes(-100) == "0 B"


def test_format_rate() -> None:
    """Test transfer rates formatted into human-readable strings."""
    assert format_rate(2500000) == "2.4 MiB/s"
    assert format_rate(410000) == "400.4 KiB/s"


def test_format_uptime() -> None:
    """Test seconds formatted into human-readable uptime strings."""
    assert format_uptime(0) == "0s"
    assert format_uptime(45) == "45s"
    assert format_uptime(3665) == "1h 1m 5s"
    assert format_uptime(225070) == "2d 14h 31m"
