# syswatch Configuration Reference

`syswatch` uses YAML for optional configuration files.

---

## Configuration Schema

<details>
<summary><b>Complete Options Reference</b></summary>

```yaml
# Sampling refresh interval for continuous monitoring (seconds)
interval: 2.0

# Health evaluation threshold percentages (0.0 to 100.0)
thresholds:
  cpu_warning: 80.0
  cpu_critical: 90.0
  memory_warning: 80.0
  memory_critical: 90.0
  swap_warning: 70.0
  swap_critical: 85.0
  disk_warning: 85.0
  disk_critical: 95.0

# Filesystem directory paths to monitor for disk space
disk:
  paths:
    - /
    - /home

# Enable or disable network statistics collection
network:
  enabled: true

# Process monitoring settings
processes:
  enabled: true
  top_n: 10
```

</details>

---

<details>
<summary><b>Validation Rules & Constraints</b></summary>

1. **Numeric Limits**: All threshold values must be numeric percentages between `0.0` and `100.0`.
2. **Precedence Constraint**: Warning thresholds cannot exceed critical thresholds (`warning <= critical`).
3. **Interval**: `interval` must be a positive float greater than `0.0`.
4. **Validation Command**: Run `syswatch --config config.yaml config validate` to test a file before deploying.

</details>
