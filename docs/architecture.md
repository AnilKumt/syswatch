# syswatch Architecture Documentation

This document explains the design principles, architectural boundaries, and data flow of `syswatch`.

---

## Architectural Blueprint

```mermaid
flowchart TD
    subgraph CLI ["CLI Layer (Click)"]
        CMD["syswatch commands (status, monitor, processes, config)"]
    end

    subgraph Config ["Configuration Layer"]
        CFG["Config Loader (PyYAML) & Schema Validation"]
    end

    subgraph Domain ["Domain & Application Services"]
        MODELS["Metrics & Health Dataclasses"]
        HEALTH["Health Evaluator Service"]
        MONITOR["Continuous Monitor Engine"]
    end

    subgraph Collectors ["Collectors Layer"]
        CPU_C["CPU Collector"]
        MEM_C["Memory & Swap Collector"]
        DISK_C["Disk Partition Collector"]
        NET_C["Network Collector"]
        SYS_C["System & Uptime Collector"]
        PROC_C["Process Collector"]
    end

    subgraph Output ["Presentation Layer"]
        RICH["Rich Terminal Renderer"]
        JSON["JSON Serializer"]
    end

    CMD --> CFG
    CMD --> HEALTH
    HEALTH --> Collectors
    Collectors --> MODELS
    MODELS --> HEALTH
    HEALTH --> RICH
    HEALTH --> JSON
```

---

## Core Layers & Responsibilities

<details>
<summary><b>1. CLI Layer (<code>cli.py</code>)</b></summary>

- Routes command line flags using `Click`.
- Handles global context (`--config PATH`).
- Maps business status (`OK`, `WARNING`, `CRITICAL`) to standard CLI exit codes ($0, 1, 2$).
- Catches top-level user interrupts (`KeyboardInterrupt`) cleanly.

</details>

<details>
<summary><b>2. Application & Business Logic Services (<code>services/</code>)</b></summary>

- **`HealthEvaluatorService`**: Compares raw metric values against warning and critical thresholds. Escalates system health to the worst-case status among components (`CRITICAL` > `WARNING` > `UNKNOWN` > `OK`).
- **`ContinuousMonitorService`**: Controls live sampling loops, calculates network transfer rates ($\text{MB/s}$) across time deltas ($\Delta t$), and updates Rich `Live` displays.

</details>

<details>
<summary><b>3. Metric Collectors (<code>collectors/</code>)</b></summary>

- Interfaces with `psutil`, `platform`, and Linux `/proc` kernel interfaces.
- Returns pure dataclass domain models.
- Implements path error isolation in disk collection and catches `NoSuchProcess` / `AccessDenied` exceptions during process scanning.

</details>

<details>
<summary><b>4. Presentation Layer (<code>output/</code>)</b></summary>

- **`rich_output.py`**: Formats binary units (`GiB`, `MiB`), uptime, panels, tables, and status badges.
- **`json_output.py`**: Serializes domain snapshots into machine-readable JSON strings with ISO-8601 UTC timestamps.

</details>
