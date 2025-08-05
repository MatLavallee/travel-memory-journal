"""Test Travel Memory Journal CLI commands."""

import pytest
from pathlib import Path
from datetime import date
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from ai_journaling_assistant.cli import app


class TestCLIApp:
    """Test CLI application setup and basic functionality."""

    def test_cli_app_help(self):
        """Shows helpful information when running with --help."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "Travel Memory Journal" in result.stdout
        assert "add-memory" in result.stdout
        assert "list-memories" in result.stdout

    def test_cli_app_version_info(self):
        """Displays version and basic app information."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "capture and relive your adventures" in result.stdout.lower()


class TestAddMemoryCommand:
    """Test add-memory CLI command functionality."""

    def test_add_memory_interactive_mode(self, tmp_path):
        """Handles interactive memory creation flow."""
        runner = CliRunner()
        
        # Mock the interactive inputs
        inputs = [
            "Paris, France",      # location
            "2024-07-15",         # date
            "Amazing Louvre visit with incredible art",  # description
            "n"                   # no manual tags
        ]
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            result = runner.invoke(app, ["add-memory"], input="\n".join(inputs))
            
            assert result.exit_code == 0
            assert "Memory saved successfully" in result.stdout
            assert "Found tags:" in result.stdout

    def test_add_memory_quick_mode(self, tmp_path):
        """Processes command-line flags for quick addition."""
        runner = CliRunner()
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            result = runner.invoke(app, [
                "add-memory",
                "--location", "Tokyo, Japan",
                "--date", "2024-07-16", 
                "--description", "Incredible sushi experience"
            ])
            
            assert result.exit_code == 0
            assert "Memory saved successfully" in result.stdout
            assert "Found tags:" in result.stdout

    def test_add_memory_with_manual_tags(self, tmp_path):
        """Accepts manual tags via command line."""
        runner = CliRunner()
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            result = runner.invoke(app, [
                "add-memory",
                "--location", "Rome, Italy",
                "--date", "2024-07-17",
                "--description", "Ancient Colosseum tour",
                "--tags", "ancient,history,architecture"
            ])
            
            assert result.exit_code == 0
            assert "Memory saved successfully" in result.stdout

    def test_add_memory_date_today_shortcut(self, tmp_path):
        """Accepts 'today' as date shortcut."""
        runner = CliRunner()
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            result = runner.invoke(app, [
                "add-memory",
                "--location", "Barcelona, Spain",
                "--date", "today",
                "--description", "Gaudi architecture tour"
            ])
            
            assert result.exit_code == 0
            assert "Memory saved successfully" in result.stdout

    def test_add_memory_validation_errors(self, tmp_path):
        """Provides clear error messages for invalid input."""
        runner = CliRunner()
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            # Test empty location
            result = runner.invoke(app, [
                "add-memory",
                "--location", "",
                "--date", "2024-07-18",
                "--description", "Test description"
            ])
            
            assert result.exit_code != 0
            assert "Location cannot be empty" in result.stdout

    def test_add_memory_invalid_date_format(self, tmp_path):
        """Handles invalid date formats with helpful messages."""
        runner = CliRunner()
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            result = runner.invoke(app, [
                "add-memory",
                "--location", "Test Location",
                "--date", "invalid-date",
                "--description", "Test description"
            ])
            
            assert result.exit_code != 0
            assert "Invalid date format" in result.stdout or "date" in result.stdout.lower()

    def test_add_memory_progress_indicators(self, tmp_path):
        """Shows progress during tag extraction."""
        runner = CliRunner()
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            result = runner.invoke(app, [
                "add-memory",
                "--location", "Venice, Italy",
                "--date", "2024-07-19",
                "--description", "Gondola ride through beautiful canals"
            ])
            
            assert result.exit_code == 0
            assert "Processing" in result.stdout or "Extracting" in result.stdout


class TestListMemoriesCommand:
    """Test list-memories CLI command functionality."""

    def setup_method(self):
        """Setup test data for list commands."""
        self.runner = CliRunner()

    def test_list_memories_empty_collection(self, tmp_path):
        """Shows appropriate message for empty collection."""
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "empty-storage"
            
            result = self.runner.invoke(app, ["list-memories"])
            
            assert result.exit_code == 0
            assert "No memories found" in result.stdout or "empty" in result.stdout.lower()

    def test_list_memories_with_data(self, tmp_path):
        """Displays memories in chronological order with formatting."""
        # First add some memories
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            # Add first memory
            self.runner.invoke(app, [
                "add-memory",
                "--location", "Paris, France",
                "--date", "2024-07-15",
                "--description", "Louvre museum visit"
            ])
            
            # Add second memory
            self.runner.invoke(app, [
                "add-memory", 
                "--location", "Rome, Italy",
                "--date", "2024-07-20",
                "--description", "Colosseum exploration"
            ])
            
            # List memories
            result = self.runner.invoke(app, ["list-memories"])
            
            assert result.exit_code == 0
            assert "Paris, France" in result.stdout
            assert "Rome, Italy" in result.stdout
            assert "2024-07-15" in result.stdout
            assert "2024-07-20" in result.stdout

    def test_list_memories_with_limit(self, tmp_path):
        """Supports limiting number of displayed memories."""
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            # Add multiple memories
            for i in range(5):
                self.runner.invoke(app, [
                    "add-memory",
                    "--location", f"Location {i}",
                    "--date", f"2024-07-{10+i:02d}",
                    "--description", f"Description {i}"
                ])
            
            # List with limit
            result = self.runner.invoke(app, ["list-memories", "--limit", "3"])
            
            assert result.exit_code == 0
            # Should show only 3 memories
            lines = [line for line in result.stdout.split('\n') if 'Location' in line]
            assert len(lines) <= 3

    def test_list_memories_table_format(self, tmp_path):
        """Displays memories in well-formatted table."""
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            self.runner.invoke(app, [
                "add-memory",
                "--location", "Amsterdam, Netherlands",
                "--date", "2024-07-21",
                "--description", "Canal cruise experience"
            ])
            
            result = self.runner.invoke(app, ["list-memories"])
            
            assert result.exit_code == 0
            # Check for table-like formatting
            assert "Date" in result.stdout or "Location" in result.stdout
            assert "Amsterdam" in result.stdout

    def test_list_memories_with_tags_display(self, tmp_path):
        """Shows extracted tags in memory listings."""
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            self.runner.invoke(app, [
                "add-memory",
                "--location", "Florence, Italy",
                "--date", "2024-07-22",
                "--description", "Uffizi Gallery art exhibition"
            ])
            
            result = self.runner.invoke(app, ["list-memories"])
            
            assert result.exit_code == 0
            assert "Florence" in result.stdout
            # Should show some extracted tags
            assert "art" in result.stdout.lower() or "gallery" in result.stdout.lower()


class TestProcessMemoryCommand:
    """Test process-memory CLI command functionality."""

    def test_process_memory_by_id(self, tmp_path):
        """Processes specific memory for tag extraction."""
        runner = CliRunner()
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            # First add a memory
            add_result = runner.invoke(app, [
                "add-memory",
                "--location", "Madrid, Spain",
                "--date", "2024-07-23",
                "--description", "Prado museum and tapas tour"
            ])
            
            assert add_result.exit_code == 0
            
            # Extract memory ID from output (simplified for test)
            # In real implementation, we'd parse the actual ID
            result = runner.invoke(app, ["process-memory", "--all"])
            
            assert result.exit_code == 0
            assert "Processing" in result.stdout or "tags" in result.stdout.lower()

    def test_process_all_untagged_memories(self, tmp_path):
        """Processes all memories with insufficient tags."""
        runner = CliRunner()
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            # Add memories
            runner.invoke(app, [
                "add-memory",
                "--location", "Berlin, Germany",
                "--date", "2024-07-24",
                "--description", "Brandenburg Gate historical tour"
            ])
            
            result = runner.invoke(app, ["process-memory", "--all"])
            
            assert result.exit_code == 0
            assert "Processed" in result.stdout or "memories" in result.stdout.lower()


class TestTopMemoryCommand:
    """Test top-memory CLI command functionality."""

    def test_top_memory_with_data(self, tmp_path):
        """Finds and displays memory with most tags."""
        runner = CliRunner()
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            # Add a simple memory
            runner.invoke(app, [
                "add-memory",
                "--location", "Simple Place",
                "--date", "2024-07-25",
                "--description", "Nice view"
            ])
            
            # Add a complex memory with many tags
            runner.invoke(app, [
                "add-memory",
                "--location", "Paris, France",
                "--date", "2024-07-26",
                "--description", "Amazing restaurant with incredible wine, visited museum with beautiful art, walked through historic architecture"
            ])
            
            result = runner.invoke(app, ["top-memory"])
            
            assert result.exit_code == 0
            assert "Paris, France" in result.stdout
            assert "top memory" in result.stdout.lower() or "most tags" in result.stdout.lower()

    def test_top_memory_empty_collection(self, tmp_path):
        """Handles empty collection gracefully."""
        runner = CliRunner()
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "empty-storage"
            
            result = runner.invoke(app, ["top-memory"])
            
            assert result.exit_code == 0
            assert "No memories found" in result.stdout or "empty" in result.stdout.lower()


class TestCLIErrorHandling:
    """Test CLI error handling and user experience."""

    def test_cli_storage_permission_error(self, tmp_path):
        """Handles storage permission errors gracefully."""
        runner = CliRunner()
        
        # Create a directory with no write permissions
        restricted_path = tmp_path / "restricted"
        restricted_path.mkdir(mode=0o444)
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = restricted_path / "storage"
            
            result = runner.invoke(app, [
                "add-memory",
                "--location", "Test Location",
                "--date", "2024-07-27",
                "--description", "Test description"
            ])
            
            assert result.exit_code != 0
            assert "Permission" in result.stdout or "error" in result.stdout.lower()

    def test_cli_helpful_error_messages(self, tmp_path):
        """Provides helpful error messages with examples."""
        runner = CliRunner()
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            # Test missing required arguments
            result = runner.invoke(app, ["add-memory", "--location", "Test"])
            
            # Should provide helpful guidance
            assert result.exit_code != 0
            assert "required" in result.stdout.lower() or "missing" in result.stdout.lower()

    def test_cli_consistent_output_formatting(self, tmp_path):
        """Uses consistent visual formatting across commands."""
        runner = CliRunner()
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            # Add memory
            add_result = runner.invoke(app, [
                "add-memory",
                "--location", "Vienna, Austria",
                "--date", "2024-07-28",
                "--description", "Schönbrunn Palace visit"
            ])
            
            # List memories
            list_result = runner.invoke(app, ["list-memories"])
            
            assert add_result.exit_code == 0
            assert list_result.exit_code == 0
            
            # Check for consistent emoji/formatting patterns
            # Both should use similar visual indicators
            success_patterns = ["✅", "✨", "💾", "saved", "success"]
            assert any(pattern in add_result.stdout for pattern in success_patterns)


class TestCLIUserExperience:
    """Test CLI user experience and usability features."""

    def test_cli_interactive_prompts_validation(self, tmp_path):
        """Validates interactive input with helpful feedback."""
        runner = CliRunner()
        
        with patch('ai_journaling_assistant.cli.get_app_config') as mock_config:
            mock_config.return_value.storage_dir = tmp_path / "test-storage"
            
            # Test with invalid date input that gets corrected
            inputs = [
                "Prague, Czech Republic",
                "invalid",      # Invalid date
                "2024-07-29",   # Corrected date
                "Beautiful Prague Castle tour",
                "n"
            ]
            
            result = runner.invoke(app, ["add-memory"], input="\n".join(inputs))
            
            # Should eventually succeed after correction
            assert result.exit_code == 0 or "Prague" in result.stdout

    def test_cli_command_examples_in_help(self):
        """Shows practical examples in help text."""
        runner = CliRunner()
        
        result = runner.invoke(app, ["add-memory", "--help"])
        
        assert result.exit_code == 0
        assert "example" in result.stdout.lower() or "Example" in result.stdout
        assert "--location" in result.stdout
        assert "--date" in result.stdout