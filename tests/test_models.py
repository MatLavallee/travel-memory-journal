"""Test Travel Memory Journal data models."""

import pytest
from datetime import datetime, date
from uuid import UUID
from pydantic import ValidationError

from ai_journaling_assistant.models import Memory, MemoryCollection, create_memory_id


class TestMemory:
    """Test Memory model validation and behavior."""

    def test_memory_creation_valid_data(self):
        """Creates memory successfully with valid data."""
        memory_data = {
            "id": "test-123",
            "location": "Paris, France",
            "date": "2024-07-15",
            "description": "Amazing day at the Louvre museum",
            "tags": ["museum", "art", "culture"],
        }
        
        memory = Memory(**memory_data)
        
        assert memory.id == "test-123"
        assert memory.location == "Paris, France"
        assert memory.date == date(2024, 7, 15)
        assert memory.description == "Amazing day at the Louvre museum"
        assert memory.tags == ["museum", "art", "culture"]
        assert isinstance(memory.created_at, datetime)
        assert isinstance(memory.updated_at, datetime)

    def test_memory_validation_invalid_date(self):
        """Rejects invalid date formats with clear error."""
        memory_data = {
            "id": "test-123",
            "location": "Paris, France", 
            "date": "invalid-date",
            "description": "Test description",
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Memory(**memory_data)
        
        assert "date" in str(exc_info.value)

    def test_memory_requires_location(self):
        """Requires location field for memory creation."""
        memory_data = {
            "id": "test-123",
            "date": "2024-07-15",
            "description": "Test description",
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Memory(**memory_data)
        
        assert "location" in str(exc_info.value)

    def test_memory_requires_description(self):
        """Requires non-empty description for memory creation."""
        memory_data = {
            "id": "test-123",
            "location": "Paris, France",
            "date": "2024-07-15",
            "description": "",
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Memory(**memory_data)
        
        assert "description" in str(exc_info.value)

    def test_memory_tags_default_empty(self):
        """Defaults to empty tags list when not provided."""
        memory_data = {
            "id": "test-123",
            "location": "Paris, France",
            "date": "2024-07-15", 
            "description": "Test description",
        }
        
        memory = Memory(**memory_data)
        
        assert memory.tags == []

    def test_memory_auto_timestamps(self):
        """Automatically sets created_at and updated_at timestamps."""
        memory_data = {
            "id": "test-123",
            "location": "Paris, France",
            "date": "2024-07-15",
            "description": "Test description",
        }
        
        before = datetime.now()
        memory = Memory(**memory_data)
        after = datetime.now()
        
        assert before <= memory.created_at <= after
        assert before <= memory.updated_at <= after


class TestMemoryCollection:
    """Test MemoryCollection model and operations."""

    def test_memory_collection_creation(self):
        """Creates empty memory collection with metadata."""
        collection = MemoryCollection()
        
        assert collection.memories == []
        assert collection.metadata["version"] == "1.0"
        assert isinstance(collection.metadata["created_at"], datetime)
        assert collection.metadata["total_memories"] == 0

    def test_memory_collection_with_memories(self):
        """Creates collection with initial memories."""
        memory1 = Memory(
            id="test-1",
            location="Paris, France",
            date="2024-07-15",
            description="Louvre visit"
        )
        memory2 = Memory(
            id="test-2", 
            location="Rome, Italy",
            date="2024-07-16",
            description="Colosseum tour"
        )
        
        collection = MemoryCollection(memories=[memory1, memory2])
        
        assert len(collection.memories) == 2
        assert collection.metadata["total_memories"] == 2

    def test_memory_collection_add_memory(self):
        """Adds memory to collection and updates metadata."""
        collection = MemoryCollection()
        memory = Memory(
            id="test-1",
            location="Tokyo, Japan",
            date="2024-07-17",
            description="Sushi experience"
        )
        
        collection.add_memory(memory)
        
        assert len(collection.memories) == 1
        assert collection.memories[0] == memory
        assert collection.metadata["total_memories"] == 1

    def test_memory_collection_get_memory_by_id(self):
        """Retrieves memory by ID from collection."""
        memory = Memory(
            id="test-123",
            location="Barcelona, Spain", 
            date="2024-07-18",
            description="Gaudi architecture"
        )
        collection = MemoryCollection(memories=[memory])
        
        found = collection.get_memory_by_id("test-123")
        not_found = collection.get_memory_by_id("nonexistent")
        
        assert found == memory
        assert not_found is None


class TestMemoryIdGeneration:
    """Test memory ID generation utilities."""

    def test_memory_id_uniqueness(self):
        """Generates unique IDs for different calls."""
        id1 = create_memory_id()
        id2 = create_memory_id()
        
        assert id1 != id2
        assert isinstance(UUID(id1), UUID)  # Valid UUID format
        assert isinstance(UUID(id2), UUID)

    def test_memory_id_format(self):
        """Generates IDs in expected UUID format."""
        memory_id = create_memory_id()
        
        # Should be valid UUID string
        uuid_obj = UUID(memory_id)
        assert str(uuid_obj) == memory_id