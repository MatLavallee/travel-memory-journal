"""Test Travel Memory Journal storage service."""

import json
import pytest
from pathlib import Path
from datetime import datetime, date
from unittest.mock import patch, mock_open

from ai_journaling_assistant.storage import StorageService
from ai_journaling_assistant.models import Memory, MemoryCollection, create_memory_id


class TestStorageService:
    """Test storage service initialization and setup."""

    def test_storage_creates_directory(self, tmp_path):
        """Creates storage directory if missing."""
        storage_path = tmp_path / "test-storage"
        
        service = StorageService(storage_path)
        
        assert storage_path.exists()
        assert storage_path.is_dir()
        assert (storage_path / "backups").exists()

    def test_storage_uses_existing_directory(self, tmp_path):
        """Uses existing storage directory without errors."""
        storage_path = tmp_path / "existing-storage"
        storage_path.mkdir()
        
        service = StorageService(storage_path)
        
        assert service.storage_path == storage_path

    def test_storage_initializes_empty_collection(self, tmp_path):
        """Initializes with empty memory collection when no file exists."""
        storage_path = tmp_path / "empty-storage"
        
        service = StorageService(storage_path)
        memories = service.load_memories()
        
        assert isinstance(memories, MemoryCollection)
        assert len(memories.memories) == 0
        assert memories.metadata["version"] == "1.0"

    def test_storage_file_paths(self, tmp_path):
        """Sets correct file paths for memories and backups."""
        storage_path = tmp_path / "test-storage"
        
        service = StorageService(storage_path)
        
        assert service.memories_file == storage_path / "memories.json"
        assert service.backups_dir == storage_path / "backups"


class TestStorageLoadMemories:
    """Test loading memories from JSON storage."""

    def test_storage_load_empty_file(self, tmp_path):
        """Handles empty or missing JSON file gracefully."""
        storage_path = tmp_path / "test-storage"
        service = StorageService(storage_path)
        
        memories = service.load_memories()
        
        assert isinstance(memories, MemoryCollection)
        assert len(memories.memories) == 0

    def test_storage_load_valid_json(self, tmp_path):
        """Loads valid JSON memory data successfully."""
        storage_path = tmp_path / "test-storage"
        service = StorageService(storage_path)
        
        # Create test data
        test_data = {
            "memories": [
                {
                    "id": "test-123",
                    "location": "Paris, France",
                    "date": "2024-07-15",
                    "description": "Amazing Louvre visit",
                    "tags": ["museum", "art"],
                    "created_at": "2024-07-15T10:00:00",
                    "updated_at": "2024-07-15T10:00:00"
                }
            ],
            "metadata": {
                "version": "1.0",
                "created_at": "2024-07-15T09:00:00",
                "total_memories": 1
            }
        }
        
        # Write test data to file
        with open(service.memories_file, 'w') as f:
            json.dump(test_data, f)
        
        memories = service.load_memories()
        
        assert len(memories.memories) == 1
        assert memories.memories[0].id == "test-123"
        assert memories.memories[0].location == "Paris, France"
        assert memories.metadata["total_memories"] == 1

    def test_storage_load_corrupted_json(self, tmp_path):
        """Handles corrupted JSON file with clear error."""
        storage_path = tmp_path / "test-storage"
        service = StorageService(storage_path)
        
        # Write invalid JSON
        with open(service.memories_file, 'w') as f:
            f.write("invalid json content {")
        
        with pytest.raises(ValueError) as exc_info:
            service.load_memories()
        
        assert "Invalid JSON" in str(exc_info.value)

    def test_storage_load_invalid_data_format(self, tmp_path):
        """Handles invalid data format with validation error."""
        storage_path = tmp_path / "test-storage"
        service = StorageService(storage_path)
        
        # Write JSON with invalid memory data
        test_data = {
            "memories": [
                {
                    "id": "test-123",
                    "location": "",  # Invalid: empty location
                    "date": "invalid-date",  # Invalid: bad date format
                    "description": "Test"
                }
            ],
            "metadata": {"version": "1.0", "total_memories": 1}
        }
        
        with open(service.memories_file, 'w') as f:
            json.dump(test_data, f)
        
        with pytest.raises(ValueError) as exc_info:
            service.load_memories()
        
        assert "validation error" in str(exc_info.value).lower()


class TestStorageSaveMemories:
    """Test saving memories to JSON storage."""

    def test_storage_atomic_write(self, tmp_path):
        """Ensures atomic write operations prevent corruption."""
        storage_path = tmp_path / "test-storage"
        service = StorageService(storage_path)
        
        # Create test memory collection
        memory = Memory(
            id="test-123",
            location="Tokyo, Japan",
            date=date(2024, 7, 16),
            description="Sushi experience"
        )
        collection = MemoryCollection(memories=[memory])
        
        # Mock file operations to simulate failure during write
        original_rename = Path.rename
        
        def mock_rename_failure(self, target):
            if ".tmp" in str(self):
                raise OSError("Simulated write failure")
            return original_rename(self, target)
        
        with patch.object(Path, 'rename', mock_rename_failure):
            with pytest.raises(OSError):
                service.save_memories(collection)
        
        # Original file should not exist or be corrupted
        assert not service.memories_file.exists() or service.memories_file.stat().st_size == 0

    def test_storage_backup_creation(self, tmp_path):
        """Creates backup before each write operation."""
        storage_path = tmp_path / "test-storage"
        service = StorageService(storage_path)
        
        # Create initial memory
        memory1 = Memory(
            id="test-1",
            location="Rome, Italy",
            date=date(2024, 7, 17),
            description="Colosseum visit"
        )
        collection1 = MemoryCollection(memories=[memory1])
        service.save_memories(collection1)
        
        # Add second memory (should create backup of first)
        memory2 = Memory(
            id="test-2",
            location="Florence, Italy", 
            date=date(2024, 7, 18),
            description="Uffizi Gallery"
        )
        collection1.add_memory(memory2)
        service.save_memories(collection1)
        
        # Check that backup was created
        backup_files = list(service.backups_dir.glob("memories-*.json"))
        assert len(backup_files) >= 1
        
        # Verify backup contains original data
        with open(backup_files[0]) as f:
            backup_data = json.load(f)
        assert backup_data["metadata"]["total_memories"] == 1

    def test_storage_successful_save(self, tmp_path):
        """Saves memory collection successfully."""
        storage_path = tmp_path / "test-storage"
        service = StorageService(storage_path)
        
        memory = Memory(
            id="test-save",
            location="Barcelona, Spain",
            date=date(2024, 7, 19),
            description="Gaudi architecture tour",
            tags=["architecture", "culture"]
        )
        collection = MemoryCollection(memories=[memory])
        
        service.save_memories(collection)
        
        # Verify file was created and contains correct data
        assert service.memories_file.exists()
        
        with open(service.memories_file) as f:
            saved_data = json.load(f)
        
        assert len(saved_data["memories"]) == 1
        assert saved_data["memories"][0]["id"] == "test-save"
        assert saved_data["memories"][0]["location"] == "Barcelona, Spain"
        assert saved_data["metadata"]["total_memories"] == 1

    def test_storage_error_handling(self, tmp_path):
        """Handles file permission and corruption errors."""
        storage_path = tmp_path / "test-storage"
        service = StorageService(storage_path)
        
        # Make directory read-only to simulate permission error
        storage_path.chmod(0o444)
        
        memory = Memory(
            id="test-permission",
            location="Test Location",
            date=date(2024, 7, 20),
            description="Test description"
        )
        collection = MemoryCollection(memories=[memory])
        
        with pytest.raises(PermissionError):
            service.save_memories(collection)


class TestStorageMemoryOperations:
    """Test individual memory operations."""

    def test_storage_add_memory(self, tmp_path):
        """Adds single memory to collection and persists."""
        storage_path = tmp_path / "test-storage"
        service = StorageService(storage_path)
        
        memory = Memory(
            id="add-test",
            location="Amsterdam, Netherlands",
            date=date(2024, 7, 21),
            description="Canal cruise"
        )
        
        service.add_memory(memory)
        
        # Verify memory was persisted
        loaded = service.load_memories()
        assert len(loaded.memories) == 1
        assert loaded.memories[0].id == "add-test"

    def test_storage_get_memory_by_id(self, tmp_path):
        """Retrieves specific memory by ID."""
        storage_path = tmp_path / "test-storage"
        service = StorageService(storage_path)
        
        memory1 = Memory(id="find-1", location="Location 1", date=date(2024, 7, 22), description="Desc 1")
        memory2 = Memory(id="find-2", location="Location 2", date=date(2024, 7, 23), description="Desc 2")
        
        service.add_memory(memory1)
        service.add_memory(memory2)
        
        found = service.get_memory_by_id("find-1")
        not_found = service.get_memory_by_id("nonexistent")
        
        assert found is not None
        assert found.id == "find-1"
        assert not_found is None

    def test_storage_list_memories(self, tmp_path):
        """Returns all memories with optional filtering."""
        storage_path = tmp_path / "test-storage"
        service = StorageService(storage_path)
        
        memory1 = Memory(id="list-1", location="Paris", date=date(2024, 7, 24), description="Paris trip")
        memory2 = Memory(id="list-2", location="London", date=date(2024, 7, 25), description="London visit")
        
        service.add_memory(memory1)
        service.add_memory(memory2)
        
        all_memories = service.list_memories()
        
        assert len(all_memories) == 2
        assert all_memories[0].id in ["list-1", "list-2"]
        assert all_memories[1].id in ["list-1", "list-2"]

    def test_storage_backup_cleanup(self, tmp_path):
        """Maintains reasonable number of backup files."""
        storage_path = tmp_path / "test-storage"
        service = StorageService(storage_path, max_backups=3)
        
        # Create multiple saves to generate backups
        for i in range(5):
            memory = Memory(
                id=f"backup-test-{i}",
                location=f"Location {i}",
                date=date(2024, 7, 20 + i),
                description=f"Description {i}"
            )
            service.add_memory(memory)
        
        # Should have at most 3 backup files
        backup_files = list(service.backups_dir.glob("memories-*.json"))
        assert len(backup_files) <= 3