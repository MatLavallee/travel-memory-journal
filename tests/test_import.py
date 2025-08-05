"""Test AI Journaling Assistant."""

import ai_journaling_assistant


def test_import() -> None:
    """Test that the app can be imported."""
    assert isinstance(ai_journaling_assistant.__name__, str)
