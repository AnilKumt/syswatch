"""Unit test for __main__.py module entry point."""

from unittest.mock import MagicMock
import pytest


def test_main_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test importing and executing __main__.py calls syswatch.cli.main."""
    mock_main = MagicMock()
    monkeypatch.setattr("syswatch.cli.main", mock_main)

    import syswatch.__main__ as main_mod

    # Execute module code under __name__ == "__main__"
    main_mod.main()
    mock_main.assert_called_once()
