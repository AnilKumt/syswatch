# syswatch Developer & Testing Guide

This guide covers local environment setup, running tests, code quality checks, and packaging.

---

<details>
<summary><b>1. Development Environment Setup</b></summary>

```bash
# Clone repository
git clone https://github.com/syswatch/syswatch.git
cd syswatch

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install package in editable mode with development dependencies
pip install -e ".[dev]"
```

</details>

---

<details>
<summary><b>2. Testing & Coverage Execution</b></summary>

Run the test suite with coverage:

```bash
pytest
```

Run specific test sub-suites:

```bash
pytest tests/unit/
pytest tests/integration/
```

</details>

---

<details>
<summary><b>3. Code Formatting & Linting</b></summary>

Check code for PEP 8 compliance and import ordering using `ruff`:

```bash
ruff check src tests
```

Auto-fix issues:

```bash
ruff check --fix src tests
```

</details>

---

<details>
<summary><b>4. Building Distribution Artifacts</b></summary>

```bash
python -m build
twine check dist/*
```

</details>
