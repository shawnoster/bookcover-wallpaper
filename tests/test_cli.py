"""Tests for CLI interface."""

from click.testing import CliRunner
from bookcover_wallpaper.cli import main


def test_cli_help():
    """Test that CLI help works."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Generate landscape wallpapers" in result.output


def test_cli_basic():
    """Test basic CLI invocation."""
    runner = CliRunner()
    result = runner.invoke(main, ["--source", "local"])
    assert result.exit_code == 0
    assert "Implementation in progress" in result.output
