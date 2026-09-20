# syswatch

[![CI Pipeline](https://github.com/syswatch/syswatch/actions/workflows/ci.yml/badge.svg)](https://github.com/syswatch/syswatch/actions)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-quality Linux system health monitoring CLI built in Python. Designed for system administrators and developers who need clear terminal health dashboards, configurable threshold alerts, real-time live monitoring, and structured JSON output for automation.

---

## Key Features

- **Human-Readable Health Dashboard**: Rich terminal UI with component status badges (`OK`, `WARNING`, `CRITICAL`).
- **Structured Machine-Readable JSON**: `--json` flag output for shell scripts, `jq` pipelines, and monitoring agents.
- **Real-Time Continuous Monitoring**: Live terminal dashboard with configurable refresh intervals and rate calculations.
- **Process Monitoring**: Inspect active processes sorted by CPU or Memory usage.
- **Configurable YAML Thresholds**: Custom thresholds for CPU, memory, swap, and disk paths with path error tolerance.

---

<details>
<summary><b>Quick Start & Installation</b></summary>

### Installation from Source

```bash
git clone https://github.com/syswatch/syswatch.git
cd syswatch
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Basic Commands

```bash
# Display system health status
syswatch status

# Output machine-readable JSON status
syswatch status --json

# Run real-time live monitoring (press Ctrl+C to stop)
syswatch monitor --interval 2.0

# View top processes sorted by CPU usage
syswatch processes --sort cpu --limit 10

# Validate configuration file
syswatch --config config/example.yaml config validate
```

</details>

---

<details>
<summary><b>CLI Command Reference</b></summary>

### `syswatch [GLOBAL OPTIONS] COMMAND [ARGS]...`

#### Global Options
* `-c, --config PATH`: Specify path to YAML configuration file.
* `--version`: Show package version and exit.
* `--help`: Show help message.

#### Subcommands

| Subcommand | Flags | Description |
| :--- | :--- | :--- |
| `status` | `--json` | Generates a single health report snapshot (Exit codes: 0=OK, 1=WARNING, 2=CRITICAL/Error). |
| `monitor` | `-i, --interval FLOAT`, `--json` | Runs continuous monitoring loop (Ctrl+C to stop). |
| `processes` | `-s, --sort [cpu\|memory]`, `-n, --limit INT`, `--json` | Displays top resource-consuming processes. |
| `config validate` | None | Validates custom YAML configuration syntax and threshold values. |

</details>

---

<details>
<summary><b>Configuration Guide (YAML)</b></summary>

Default configuration settings can be overridden by passing a custom YAML file using `syswatch --config PATH status`.

Example `config.yaml`:

```yaml
interval: 2.0

thresholds:
  cpu_warning: 80.0
  cpu_critical: 90.0
  memory_warning: 80.0
  memory_critical: 90.0
  swap_warning: 70.0
  swap_critical: 85.0
  disk_warning: 85.0
  disk_critical: 95.0

disk:
  paths:
    - /
    - /home

network:
  enabled: true

processes:
  enabled: true
  top_n: 10
```

</details>

---

<details>
<summary><b>Machine-Readable JSON Output Schema</b></summary>

`syswatch status --json` outputs ISO-8601 UTC timestamped JSON:

```json
{
  "timestamp": "2026-09-23T14:39:31Z",
  "status": "OK",
  "hostname": "dev-machine",
  "os": {
    "name": "Linux",
    "release": "6.1.0",
    "architecture": "x86_64",
    "uptime_seconds": 3600.0
  },
  "cpu": {
    "status": "OK",
    "usage_percent": 10.2,
    "core_count": 8,
    "load_average": [0.0, 0.0, 0.0]
  },
  "memory": {
    "status": "OK",
    "used_percent": 58.7,
    "used_bytes": 7409254400,
    "total_bytes": 12656099328,
    "available_bytes": 5246844928
  },
  "swap": {
    "status": "OK",
    "used_percent": 8.9,
    "used_bytes": 273874944,
    "total_bytes": 3087007744
  },
  "disk": {
    "status": "OK",
    "partitions": {
      "/": {
        "used_percent": 29.0,
        "used_bytes": 39405674496,
        "total_bytes": 135653224448,
        "free_bytes": 96247549952
      }
    },
    "errors": {}
  },
  "network": {
    "total_bytes_sent": 275567616,
    "total_bytes_recv": 1073741824,
    "bytes_sent_per_sec": 0.0,
    "bytes_recv_per_sec": 0.0
  },
  "alerts": []
}
```

</details>

---

<details>
<summary><b>Docker Deployment & Host Monitoring</b></summary>

### Building the Image

```bash
docker build -t syswatch .
```

### Running Host Health Monitoring in Docker

Container isolation prevents containers from viewing host PIDs, physical network cards, and host disk mounts by default. To monitor the host machine from inside Docker:

```bash
docker run --rm \
  --pid=host \
  --net=host \
  -v /:/host/root:ro \
  syswatch status
```

</details>

---

<details>
<summary><b>Architecture & Engineering Design</b></summary>

`syswatch` follows a strict layered architecture pattern:

```text
CLI Layer (Click)
    │
    ▼
Config Layer (PyYAML) ──► Application Layer (HealthEvaluatorService, ContinuousMonitorService)
                                  │
                   ┌──────────────┴──────────────┐
                   ▼                             ▼
           Collectors (psutil)             Domain Models (Dataclasses)
                   │                             │
                   └──────────────┬──────────────┘
                                  ▼
                     Output Layer (Rich / JSON)
```

- **Unidirectional Data Flow**: Collectors populate dataclass models in raw units (`bytes`, `percentages`). Formatting and coloring happen solely in presentation renderers.
- **Fail-Safe Disk Monitoring**: Non-existent or restricted disk paths store partition errors without halting evaluation of other valid partitions.
- **Signal Handling**: Graceful `Ctrl+C` interrupt catching prevents Python stack traces on user terminals.

</details>

---

<details>
<summary><b>Development & Testing</b></summary>

### Running Tests

```bash
pytest
```

### Code Formatting & Linting

```bash
ruff check src tests
```

### Building Distribution Packages

```bash
python -m build
twine check dist/*
```

</details>

---

## License

This project is licensed under the [MIT License](LICENSE).
