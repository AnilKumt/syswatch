"""Real-time continuous system monitoring service engine."""

import time

from rich.console import Console
from rich.live import Live

from syswatch.collectors import (
    collect_cpu_metrics,
    collect_disk_metrics,
    collect_memory_metrics,
    collect_network_metrics,
    collect_swap_metrics,
    collect_system_metrics,
)
from syswatch.config import AppConfig
from syswatch.models import NetworkMetrics, OverallHealth
from syswatch.output.json_output import render_json_report
from syswatch.output.rich_output import build_live_display
from syswatch.services.health import HealthEvaluatorService


class ContinuousMonitorService:
    """Service managing real-time continuous system monitoring loop."""

    def __init__(
        self, app_config: AppConfig | None = None, console: Console | None = None
    ) -> None:
        self.config = app_config or AppConfig()
        self.console = console or Console()
        self.evaluator = HealthEvaluatorService(config=self.config.thresholds)

        self._last_time: float | None = None
        self._prev_network: NetworkMetrics | None = None

    def collect_snapshot(self) -> OverallHealth:
        """Collect a fresh system metrics snapshot and compute transfer rates.

        Returns:
            OverallHealth snapshot object.
        """
        now = time.time()
        time_delta: float | None = None
        if self._last_time is not None:
            time_delta = max(0.001, now - self._last_time)

        # 1. Collect metrics
        sys_m = collect_system_metrics()
        cpu_m = collect_cpu_metrics(interval=None)
        mem_m = collect_memory_metrics()
        swap_m = collect_swap_metrics()
        disk_m = collect_disk_metrics(paths=self.config.disk_paths)

        net_m = None
        if self.config.network_enabled:
            net_m = collect_network_metrics(
                prev_metrics=self._prev_network, time_delta=time_delta
            )
            self._prev_network = net_m

        self._last_time = now

        # 2. Evaluate Health
        return self.evaluator.evaluate(
            system_metrics=sys_m,
            cpu_metrics=cpu_m,
            memory_metrics=mem_m,
            swap_metrics=swap_m,
            disk_metrics=disk_m,
            network_metrics=net_m,
        )

    def run_live(
        self,
        interval: float | None = None,
        json_output: bool = False,
        max_iterations: int | None = None,
    ) -> None:
        """Run continuous monitoring loop.

        Args:
            interval: Refresh interval in seconds (defaults to self.config.interval).
            json_output: If True, streams JSON lines/objects per tick instead of Rich UI.
            max_iterations: Optional tick limit for automated testing/CI execution.
        """
        refresh_interval = interval if interval is not None else self.config.interval
        iteration = 0

        if json_output:
            while max_iterations is None or iteration < max_iterations:
                health = self.collect_snapshot()
                print(render_json_report(health, indent=None), flush=True)
                iteration += 1
                if max_iterations is None or iteration < max_iterations:
                    time.sleep(refresh_interval)
        else:
            initial_health = self.collect_snapshot()
            initial_panel = build_live_display(initial_health, title="SYSWATCH LIVE MONITORING")

            with Live(
                initial_panel,
                console=self.console,
                refresh_per_second=4,
                screen=False,
            ) as live:
                iteration = 1
                while max_iterations is None or iteration < max_iterations:
                    time.sleep(refresh_interval)
                    health = self.collect_snapshot()
                    panel = build_live_display(health, title="SYSWATCH LIVE MONITORING")
                    live.update(panel)
                    iteration += 1
