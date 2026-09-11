"""Output presentation subpackage for human-readable and machine-readable views."""

from syswatch.output.formatters import format_bytes, format_rate, format_uptime
from syswatch.output.json_output import render_json_report, render_process_json
from syswatch.output.rich_output import render_health_report, render_process_report

__all__ = [
    "format_bytes",
    "format_rate",
    "format_uptime",
    "render_health_report",
    "render_json_report",
    "render_process_json",
    "render_process_report",
]
