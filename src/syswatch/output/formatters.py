"""Formatting helpers for human-readable terminal rendering."""


def format_bytes(bytes_value: float) -> str:
    """Format raw byte counts into human-readable binary units (GiB, MiB, KiB, B).

    Args:
        bytes_value: Byte amount to format.

    Returns:
        Formatted string (e.g., '8.2 GiB', '512.0 MiB').
    """
    if bytes_value < 0:
        return "0 B"

    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    value = float(bytes_value)
    unit_index = 0

    while value >= 1024.0 and unit_index < len(units) - 1:
        value /= 1024.0
        unit_index += 1

    if unit_index == 0:
        return f"{int(value)} B"
    return f"{value:.1f} {units[unit_index]}"


def format_rate(bytes_per_sec: float) -> str:
    """Format byte transfer rates into human-readable strings (e.g., '2.4 MiB/s').

    Args:
        bytes_per_sec: Transfer rate in bytes per second.

    Returns:
        Formatted string.
    """
    formatted = format_bytes(bytes_per_sec)
    return f"{formatted}/s"


def format_uptime(seconds: float) -> str:
    """Format total seconds into human-readable uptime (e.g., '2d 14h 31m').

    Args:
        seconds: Total uptime in seconds.

    Returns:
        Formatted uptime string.
    """
    if seconds <= 0:
        return "0s"

    total_seconds = int(seconds)
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")

    return " ".join(parts[:3]) if len(parts) > 3 else " ".join(parts)
