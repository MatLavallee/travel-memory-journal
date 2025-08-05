"""Travel Memory Journal storage service."""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from pydantic import ValidationError

from ai_journaling_assistant.models import Memory, MemoryCollection


class StorageService:
    """Local JSON storage service for travel memories.
    
    Handles atomic file operations, backup creation, and data persistence
    following ADR-0001 (Local JSON storage) and ADR-0003 (Single file storage).
    """
    
    def __init__(self, storage_path: Path, max_backups: int = 5):
        """Initialize storage service with directory setup.
        
        Args:
            storage_path: Directory path for storing memories.
            max_backups: Maximum number of backup files to retain.
        """
        self.storage_path = Path(storage_path).resolve()
        self.max_backups = max_backups
        self.memories_file = self.storage_path / "memories.json"
        self.backups_dir = self.storage_path / "backups"
        
        # Create directory structure
        self._setup_directories()
    
    def _setup_directories(self) -> None:
        """Create storage directory structure if it doesn't exist."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(exist_ok=True)
    
    def load_memories(self) -> MemoryCollection:
        """Load all memories from JSON file with error handling.
        
        Returns:
            MemoryCollection with all stored memories.
            
        Raises:
            ValueError: If JSON is corrupted or data format is invalid.
        """
        if not self.memories_file.exists():
            return MemoryCollection()
        
        try:
            with open(self.memories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return MemoryCollection(**data)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.memories_file}: {e}")
        except ValidationError as e:
            raise ValueError(f"Data validation error: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load memories: {e}")
    
    def save_memories(self, collection: MemoryCollection) -> None:
        """Save memories with atomic write operations and backup.
        
        Args:
            collection: MemoryCollection to persist.
            
        Raises:
            PermissionError: If file cannot be written due to permissions.
        """
        # Create backup of existing file
        if self.memories_file.exists():
            self._create_backup()
        
        # Prepare data for serialization
        data = {
            "memories": [memory.model_dump(mode='json') for memory in collection.memories],
            "metadata": collection.metadata.copy()
        }
        data["metadata"]["updated_at"] = datetime.now().isoformat()
        
        # Atomic write using temporary file
        temp_file = self.memories_file.with_suffix('.tmp')
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            # Atomic rename (atomic on most filesystems)
            temp_file.rename(self.memories_file)
            
        except PermissionError:
            # Clean up temp file on permission error
            if temp_file.exists():
                temp_file.unlink()
            raise PermissionError(f"Permission denied writing to {self.memories_file}")
        except Exception as e:
            # Clean up temp file on any other error
            if temp_file.exists():
                temp_file.unlink()
            raise e
        
        # Clean up old backups
        self._cleanup_backups()
    
    def _create_backup(self) -> None:
        """Create timestamped backup of current memories file."""
        if not self.memories_file.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_file = self.backups_dir / f"memories-{timestamp}.json"
        
        shutil.copy2(self.memories_file, backup_file)
    
    def _cleanup_backups(self) -> None:
        """Remove old backup files, keeping only max_backups most recent."""
        backup_files = list(self.backups_dir.glob("memories-*.json"))
        backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # Remove excess backup files
        for old_backup in backup_files[self.max_backups:]:
            old_backup.unlink()
    
    def add_memory(self, memory: Memory) -> None:
        """Add single memory to collection and persist.
        
        Args:
            memory: Memory instance to add.
        """
        collection = self.load_memories()
        collection.add_memory(memory)
        self.save_memories(collection)
    
    def get_memory_by_id(self, memory_id: str) -> Optional[Memory]:
        """Retrieve specific memory by ID.
        
        Args:
            memory_id: Unique identifier for the memory.
            
        Returns:
            Memory instance if found, None otherwise.
        """
        collection = self.load_memories()
        return collection.get_memory_by_id(memory_id)
    
    def list_memories(self) -> List[Memory]:
        """Return all memories.
        
        Returns:
            List of all Memory instances.
        """
        collection = self.load_memories()
        return collection.memories