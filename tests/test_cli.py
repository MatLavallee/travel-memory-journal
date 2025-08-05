"""Test AI Journaling Assistant CLI."""

from typer.testing import CliRunner

from ai_journaling_assistant.cli import app

runner = CliRunner()


def test_fire() -> None:
    """Test that the fire command works as expected."""
    name = "GLaDOS"
    result = runner.invoke(app, ["--name", name])
    assert result.exit_code == 0
    assert name in result.stdout
