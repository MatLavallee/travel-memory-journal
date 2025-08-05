"""Test Travel Memory Journal configuration."""

import pytest
from pathlib import Path
from unittest.mock import patch

from ai_journaling_assistant.config import (
    get_app_config,
    get_storage_path,
    get_tag_categories,
    AppConfig
)


class TestAppConfig:
    """Test application configuration management."""

    def test_config_default_values(self):
        """Uses sensible defaults for missing config."""
        config = get_app_config()
        
        assert isinstance(config, AppConfig)
        assert config.storage_dir.name == ".travel-memory-journal"
        assert config.backup_count == 5
        assert config.max_memories == 10000
        assert config.version == "1.0"

    @patch('pathlib.Path.home')
    def test_config_storage_path_home_directory(self, mock_home):
        """Creates storage path in user home directory."""
        mock_home.return_value = Path("/Users/testuser")
        
        config = get_app_config()
        
        assert str(config.storage_dir) == "/Users/testuser/.travel-memory-journal"

    def test_config_custom_storage_path(self):
        """Accepts custom storage directory path."""
        custom_path = Path("/tmp/custom-journal")
        
        config = get_app_config(storage_dir=custom_path)
        
        assert config.storage_dir == custom_path


class TestStoragePath:
    """Test storage path creation and management."""

    def test_storage_path_creation(self, tmp_path):
        """Creates storage directory structure."""
        storage_path = tmp_path / "test-journal"
        
        result = get_storage_path(storage_path)
        
        assert result.exists()
        assert result.is_dir()
        assert (result / "backups").exists()
        assert (result / "backups").is_dir()

    def test_storage_path_already_exists(self, tmp_path):
        """Handles existing storage directory gracefully."""
        storage_path = tmp_path / "existing-journal"
        storage_path.mkdir()
        
        result = get_storage_path(storage_path)
        
        assert result == storage_path
        assert result.exists()

    def test_storage_path_permissions_error(self, tmp_path):
        """Handles permission errors gracefully."""
        # Create a directory with restricted permissions
        restricted_path = tmp_path / "restricted"
        restricted_path.mkdir(mode=0o000)
        storage_path = restricted_path / "journal"
        
        with pytest.raises(PermissionError):
            get_storage_path(storage_path)

    def test_storage_path_returns_absolute_path(self, tmp_path):
        """Returns absolute path for storage directory."""
        relative_path = Path("relative-journal")
        
        result = get_storage_path(tmp_path / relative_path)
        
        assert result.is_absolute()


class TestTagCategories:
    """Test travel tag categories and keywords."""

    def test_tag_categories_loading(self):
        """Loads predefined travel tag categories."""
        categories = get_tag_categories()
        
        assert isinstance(categories, dict)
        assert "food" in categories
        assert "culture" in categories
        assert "outdoor" in categories
        assert "transport" in categories
        assert "accommodation" in categories

    def test_tag_categories_food_keywords(self):
        """Contains expected food-related keywords."""
        categories = get_tag_categories()
        food_tags = categories["food"]
        
        assert "restaurant" in food_tags
        assert "coffee" in food_tags
        assert "wine" in food_tags
        assert "market" in food_tags
        assert "cuisine" in food_tags

    def test_tag_categories_culture_keywords(self):
        """Contains expected culture-related keywords.""" 
        categories = get_tag_categories()
        culture_tags = categories["culture"]
        
        assert "museum" in culture_tags
        assert "temple" in culture_tags
        assert "art" in culture_tags
        assert "architecture" in culture_tags
        assert "history" in culture_tags

    def test_tag_categories_outdoor_keywords(self):
        """Contains expected outdoor activity keywords."""
        categories = get_tag_categories()
        outdoor_tags = categories["outdoor"]
        
        assert "hiking" in outdoor_tags
        assert "beach" in outdoor_tags
        assert "mountain" in outdoor_tags
        assert "nature" in outdoor_tags
        assert "park" in outdoor_tags

    def test_tag_categories_transport_keywords(self):
        """Contains expected transportation keywords."""
        categories = get_tag_categories()
        transport_tags = categories["transport"]
        
        assert "flight" in transport_tags
        assert "train" in transport_tags
        assert "bus" in transport_tags
        assert "taxi" in transport_tags
        assert "walking" in transport_tags

    def test_tag_categories_accommodation_keywords(self):
        """Contains expected accommodation keywords."""
        categories = get_tag_categories()
        accommodation_tags = categories["accommodation"]
        
        assert "hotel" in accommodation_tags
        assert "hostel" in accommodation_tags
        assert "airbnb" in accommodation_tags
        assert "resort" in accommodation_tags
        assert "camping" in accommodation_tags

    def test_tag_categories_immutable(self):
        """Returns copy to prevent accidental modification."""
        categories1 = get_tag_categories()
        categories2 = get_tag_categories()
        
        # Modify one copy
        categories1["food"].append("new_food_item")
        
        # Original should be unchanged
        assert "new_food_item" not in categories2["food"]