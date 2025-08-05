"""Test AI Journaling Assistant CLI."""

from typer.testing import CliRunner

from ai_journaling_assistant.cli import app

runner = CliRunner()


def test_cli_help() -> None:
    """Test that the CLI help works as expected."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Travel Memory Journal" in result.stdout
    assert "add-memory" in result.stdout
