"""Travel Memory Journal data models."""

import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, field_validator


def create_memory_id() -> str:
    """Generate unique ID for new memory.
    
    Returns:
        Unique UUID string for memory identification.
    """
    return str(uuid.uuid4())


class Memory(BaseModel):
    """Travel memory with location, date, description and tags.
    
    Represents a single travel experience with validation
    for required fields and automatic timestamp management.
    """
    
    id: str
    location: str
    date: date
    description: str
    tags: List[str] = []
    created_at: datetime = None
    updated_at: datetime = None
    
    def __init__(self, **data):
        """Initialize memory with automatic timestamps."""
        if 'created_at' not in data or data['created_at'] is None:
            data['created_at'] = datetime.now()
        if 'updated_at' not in data or data['updated_at'] is None:
            data['updated_at'] = datetime.now()
        super().__init__(**data)
    
    @field_validator('description')
    @classmethod
    def description_must_not_be_empty(cls, v: str) -> str:
        """Ensure description is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()
    
    @field_validator('location')
    @classmethod
    def location_must_not_be_empty(cls, v: str) -> str:
        """Ensure location is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Location cannot be empty')
        return v.strip()


class MemoryCollection(BaseModel):
    """Collection of travel memories with metadata.
    
    Container for all user memories with automatic
    metadata tracking and collection operations.
    """
    
    memories: List[Memory] = []
    metadata: Dict[str, Any] = {}
    
    def __init__(self, **data):
        """Initialize collection and update metadata."""
        super().__init__(**data)
        if not self.metadata:
            self.metadata = {
                "version": "1.0",
                "created_at": datetime.now(),
                "total_memories": len(self.memories)
            }
        else:
            self.metadata["total_memories"] = len(self.memories)
    
    def add_memory(self, memory: Memory) -> None:
        """Add memory to collection and update metadata.
        
        Args:
            memory: Memory instance to add to collection.
        """
        self.memories.append(memory)
        self.metadata["total_memories"] = len(self.memories)
        self.metadata["updated_at"] = datetime.now()
    
    def get_memory_by_id(self, memory_id: str) -> Optional[Memory]:
        """Retrieve memory by ID from collection.
        
        Args:
            memory_id: Unique identifier for the memory.
            
        Returns:
            Memory instance if found, None otherwise.
        """
        for memory in self.memories:
            if memory.id == memory_id:
                return memory
        return None