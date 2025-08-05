"""Test Travel Memory Journal application services."""

import pytest
from pathlib import Path
from datetime import date
from unittest.mock import Mock, patch

from ai_journaling_assistant.services import MemoryService
from ai_journaling_assistant.models import Memory, MemoryCollection, create_memory_id


class TestMemoryService:
    """Test memory service initialization and setup."""

    def test_memory_service_initialization(self, tmp_path):
        """Initializes with storage and tag extraction services."""
        storage_path = tmp_path / "test-service"
        
        service = MemoryService(storage_path)
        
        assert hasattr(service, 'storage')
        assert hasattr(service, 'tag_extractor')
        assert service.storage.storage_path == storage_path

    def test_memory_service_custom_config(self, tmp_path):
        """Accepts custom configuration parameters."""
        storage_path = tmp_path / "custom-service"
        
        service = MemoryService(storage_path, max_backups=10)
        
        assert service.storage.max_backups == 10


class TestMemoryServiceAddMemory:
    """Test adding memories with orchestration."""

    def test_memory_service_add_memory_with_auto_tags(self, tmp_path):
        """Integrates storage and tag extraction for memory creation."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        memory_data = {
            "location": "Paris, France",
            "date": date(2024, 7, 15),
            "description": "Amazing day at the Louvre museum with incredible art"
        }
        
        memory_id = service.add_memory(**memory_data)
        
        # Verify memory was created and stored
        assert memory_id is not None
        stored_memory = service.get_memory_by_id(memory_id)
        assert stored_memory is not None
        assert stored_memory.location == "Paris, France"
        assert stored_memory.description == "Amazing day at the Louvre museum with incredible art"
        
        # Verify tags were automatically extracted
        assert len(stored_memory.tags) > 0
        assert "museum" in stored_memory.tags
        assert "art" in stored_memory.tags

    def test_memory_service_add_memory_with_manual_tags(self, tmp_path):
        """Combines manual tags with auto-extracted tags."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        memory_data = {
            "location": "Tokyo, Japan",
            "date": date(2024, 7, 16),
            "description": "Incredible sushi experience",
            "manual_tags": ["favorite", "expensive"]
        }
        
        memory_id = service.add_memory(**memory_data)
        stored_memory = service.get_memory_by_id(memory_id)
        
        # Should have both manual and auto-extracted tags
        assert "favorite" in stored_memory.tags
        assert "expensive" in stored_memory.tags
        # Auto-extracted from description
        assert any(tag in stored_memory.tags for tag in ["sushi", "food", "restaurant"])

    def test_memory_service_add_memory_validation_error(self, tmp_path):
        """Handles validation errors with clear messages."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        invalid_data = {
            "location": "",  # Invalid: empty location
            "date": date(2024, 7, 17),
            "description": "Test description"
        }
        
        with pytest.raises(ValueError) as exc_info:
            service.add_memory(**invalid_data)
        
        assert "validation" in str(exc_info.value).lower()

    def test_memory_service_add_memory_storage_error(self, tmp_path):
        """Handles storage errors gracefully."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        # Mock storage to raise error
        with patch.object(service.storage, 'add_memory', side_effect=PermissionError("Mock error")):
            with pytest.raises(PermissionError):
                service.add_memory(
                    location="Test Location",
                    date=date(2024, 7, 18),
                    description="Test description"
                )


class TestMemoryServiceListMemories:
    """Test listing and retrieving memories."""

    def test_memory_service_list_memories_empty(self, tmp_path):
        """Returns empty list for new service."""
        storage_path = tmp_path / "empty-service"
        service = MemoryService(storage_path)
        
        memories = service.list_memories()
        
        assert isinstance(memories, list)
        assert len(memories) == 0

    def test_memory_service_list_memories_with_data(self, tmp_path):
        """Returns formatted memory list in chronological order."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        # Add memories in non-chronological order
        memory1_id = service.add_memory(
            location="Rome, Italy",
            date=date(2024, 7, 20),
            description="Colosseum visit"
        )
        memory2_id = service.add_memory(
            location="Paris, France", 
            date=date(2024, 7, 15),
            description="Louvre museum"
        )
        
        memories = service.list_memories()
        
        assert len(memories) == 2
        # Should be sorted chronologically (oldest first)
        assert memories[0].date == date(2024, 7, 15)
        assert memories[1].date == date(2024, 7, 20)

    def test_memory_service_list_memories_with_limit(self, tmp_path):
        """Supports limiting number of returned memories."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        # Add multiple memories
        for i in range(5):
            service.add_memory(
                location=f"Location {i}",
                date=date(2024, 7, 10 + i),
                description=f"Description {i}"
            )
        
        limited_memories = service.list_memories(limit=3)
        
        assert len(limited_memories) == 3

    def test_memory_service_list_memories_with_tag_filter(self, tmp_path):
        """Filters memories by tags."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        # Add memories with different content
        service.add_memory(
            location="Paris, France",
            date=date(2024, 7, 15),
            description="Amazing museum visit with incredible art"
        )
        service.add_memory(
            location="Tokyo, Japan",
            date=date(2024, 7, 16), 
            description="Delicious sushi at local restaurant"
        )
        
        # Filter by culture tags
        culture_memories = service.list_memories(tag_filter=["museum", "art"])
        food_memories = service.list_memories(tag_filter=["restaurant", "sushi"])
        
        assert len(culture_memories) == 1
        assert culture_memories[0].location == "Paris, France"
        assert len(food_memories) == 1
        assert food_memories[0].location == "Tokyo, Japan"


class TestMemoryServiceTagProcessing:
    """Test tag processing and extraction operations."""

    def test_memory_service_process_memory_tags(self, tmp_path):
        """Extracts tags from existing memory descriptions."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        # Add memory without tags
        memory_id = service.add_memory(
            location="Barcelona, Spain",
            date=date(2024, 7, 19),
            description="Gaudi architecture tour and beach relaxation"
        )
        
        # Process tags for specific memory
        updated_memory = service.process_memory_tags(memory_id)
        
        assert updated_memory is not None
        assert "architecture" in updated_memory.tags
        assert "beach" in updated_memory.tags

    def test_memory_service_process_all_untagged(self, tmp_path):
        """Processes all memories with insufficient tags."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        # Add memories with minimal tags
        memory1_id = service.add_memory(
            location="Rome, Italy",
            date=date(2024, 7, 20),
            description="Ancient Colosseum and Roman history",
            manual_tags=["ancient"]  # Only one tag
        )
        memory2_id = service.add_memory(
            location="Venice, Italy",
            date=date(2024, 7, 21),
            description="Gondola ride through beautiful canals"
        )
        
        processed_count = service.process_all_untagged_memories()
        
        assert processed_count >= 1  # Only memory2 should be processed (memory1 has 2 tags: "ancient" + "history")
        
        # Verify tags were added
        memory1 = service.get_memory_by_id(memory1_id)
        memory2 = service.get_memory_by_id(memory2_id)
        
        assert len(memory1.tags) > 1  # Should have more than just "ancient"
        assert len(memory2.tags) > 0  # Should have extracted tags


class TestMemoryServiceAnalytics:
    """Test memory analytics and insights."""

    def test_memory_service_get_top_memory(self, tmp_path):
        """Identifies memory with most tags."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        # Add memories with different tag counts
        simple_memory_id = service.add_memory(
            location="Simple Place",
            date=date(2024, 7, 22),
            description="Nice view"  # Minimal tags
        )
        
        complex_memory_id = service.add_memory(
            location="Paris, France",
            date=date(2024, 7, 23),
            description="Amazing restaurant with incredible wine, visited museum with beautiful art, walked through historic architecture and enjoyed local market shopping"
        )
        
        top_memory = service.get_top_memory()
        
        assert top_memory is not None
        assert top_memory.id == complex_memory_id
        assert len(top_memory.tags) > 5  # Should have many extracted tags

    def test_memory_service_get_top_memory_empty_collection(self, tmp_path):
        """Handles empty memory collection gracefully."""
        storage_path = tmp_path / "empty-service"
        service = MemoryService(storage_path)
        
        top_memory = service.get_top_memory()
        
        assert top_memory is None

    def test_memory_service_get_memory_statistics(self, tmp_path):
        """Provides statistics about memory collection."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        # Add sample memories
        service.add_memory(
            location="Paris, France",
            date=date(2024, 7, 15),
            description="Museum and restaurant visit"
        )
        service.add_memory(
            location="Tokyo, Japan",
            date=date(2024, 7, 16),
            description="Sushi and temple experience"
        )
        
        stats = service.get_memory_statistics()
        
        assert isinstance(stats, dict)
        assert stats["total_memories"] == 2
        assert stats["total_tags"] > 0
        assert "most_common_tags" in stats
        assert "locations_visited" in stats
        assert len(stats["locations_visited"]) == 2


class TestMemoryServiceSearch:
    """Test memory search and filtering capabilities."""

    def test_memory_service_search_by_text(self, tmp_path):
        """Searches memories by description text."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        service.add_memory(
            location="Paris, France",
            date=date(2024, 7, 15),
            description="Amazing Louvre museum experience"
        )
        service.add_memory(
            location="Rome, Italy",
            date=date(2024, 7, 16),
            description="Incredible Colosseum history tour"
        )
        
        # Search for specific terms
        louvre_results = service.search_memories("Louvre")
        museum_results = service.search_memories("museum")
        history_results = service.search_memories("history")
        
        assert len(louvre_results) == 1
        assert louvre_results[0].location == "Paris, France"
        assert len(museum_results) == 1
        assert len(history_results) == 1

    def test_memory_service_search_by_location(self, tmp_path):
        """Searches memories by location."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        service.add_memory(
            location="Paris, France",
            date=date(2024, 7, 15),
            description="Paris experience"
        )
        service.add_memory(
            location="Lyon, France", 
            date=date(2024, 7, 16),
            description="Lyon visit"
        )
        service.add_memory(
            location="Rome, Italy",
            date=date(2024, 7, 17),
            description="Rome tour"
        )
        
        france_results = service.search_memories_by_location("France")
        italy_results = service.search_memories_by_location("Italy")
        paris_results = service.search_memories_by_location("Paris")
        
        assert len(france_results) == 2
        assert len(italy_results) == 1
        assert len(paris_results) == 1

    def test_memory_service_search_no_results(self, tmp_path):
        """Handles search with no matching results."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        service.add_memory(
            location="Paris, France",
            date=date(2024, 7, 15),
            description="Museum visit"
        )
        
        no_results = service.search_memories("nonexistent")
        
        assert isinstance(no_results, list)
        assert len(no_results) == 0


class TestMemoryServiceErrorHandling:
    """Test error handling and edge cases."""

    def test_memory_service_get_nonexistent_memory(self, tmp_path):
        """Handles requests for nonexistent memories."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        result = service.get_memory_by_id("nonexistent-id")
        
        assert result is None

    def test_memory_service_process_nonexistent_memory_tags(self, tmp_path):
        """Handles tag processing for nonexistent memory."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        result = service.process_memory_tags("nonexistent-id")
        
        assert result is None

    def test_memory_service_error_propagation(self, tmp_path):
        """Properly propagates errors from underlying services."""
        storage_path = tmp_path / "test-service"
        service = MemoryService(storage_path)
        
        # Mock storage to raise specific error
        with patch.object(service.storage, 'load_memories', side_effect=ValueError("Mock storage error")):
            with pytest.raises(ValueError) as exc_info:
                service.list_memories()
            
            assert "Mock storage error" in str(exc_info.value)