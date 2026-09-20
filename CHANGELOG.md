# Changelog

All notable changes to `syswatch` will be documented in this file. Format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2026-09-23

### Added
- `syswatch status` human-readable health dashboard powered by Rich.
- `syswatch status --json` machine-readable structured JSON report with ISO-8601 UTC timestamps.
- `syswatch monitor` real-time live monitoring engine with flicker-free updates and transfer rate calculations.
- `syswatch processes` process inspection sorted by CPU or Memory.
- YAML configuration loading and schema validation (`syswatch config validate`).
- Multi-stage Dockerfile and Docker host monitoring guide.
- GitHub Actions CI pipeline running pytest across Python 3.11, 3.12, 3.13.
