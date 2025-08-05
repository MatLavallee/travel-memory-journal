"""Travel Memory Journal application services."""

from pathlib import Path
from datetime import date
from typing import List, Optional, Dict, Any
from collections import Counter

from ai_journaling_assistant.models import Memory, create_memory_id
from ai_journaling_assistant.storage import StorageService
from ai_journaling_assistant.tag_extraction import TagExtractor


class MemoryService:
    """High-level service for managing travel memories.
    
    Orchestrates storage, tag extraction, and business logic
    to provide a complete memory management experience.
    """
    
    def __init__(self, storage_path: Path, max_backups: int = 5):
        """Initialize memory service with dependencies.
        
        Args:
            storage_path: Directory path for storing memories.
            max_backups: Maximum number of backup files to retain.
        """
        self.storage = StorageService(storage_path, max_backups)
        self.tag_extractor = TagExtractor()
    
    def add_memory(
        self,
        location: str,
        date: date,
        description: str,
        manual_tags: Optional[List[str]] = None
    ) -> str:
        """Add new memory with automatic tag extraction.
        
        Args:
            location: Where the memory took place.
            date: When the memory occurred.
            description: Detailed description of the memory.
            manual_tags: Optional manually specified tags.
            
        Returns:
            Unique ID of the created memory.
            
        Raises:
            ValueError: If memory data validation fails.
        """
        # Generate unique ID
        memory_id = create_memory_id()
        
        # Extract tags from description
        auto_tags = self.tag_extractor.extract_tags(description)
        
        # Combine manual and auto tags, removing duplicates
        all_tags = []
        if manual_tags:
            all_tags.extend(manual_tags)
        all_tags.extend(auto_tags)
        
        # Remove duplicates while preserving order
        unique_tags = []
        seen = set()
        for tag in all_tags:
            if tag not in seen:
                unique_tags.append(tag)
                seen.add(tag)
        
        # Create memory object
        memory = Memory(
            id=memory_id,
            location=location,
            date=date,
            description=description,
            tags=unique_tags
        )
        
        # Store memory
        self.storage.add_memory(memory)
        
        return memory_id
    
    def get_memory_by_id(self, memory_id: str) -> Optional[Memory]:
        """Retrieve specific memory by ID.
        
        Args:
            memory_id: Unique identifier for the memory.
            
        Returns:
            Memory instance if found, None otherwise.
        """
        return self.storage.get_memory_by_id(memory_id)
    
    def list_memories(
        self,
        limit: Optional[int] = None,
        tag_filter: Optional[List[str]] = None
    ) -> List[Memory]:
        """List memories with optional filtering and limiting.
        
        Args:
            limit: Maximum number of memories to return.
            tag_filter: Filter memories that contain any of these tags.
            
        Returns:
            List of Memory instances, sorted chronologically.
        """
        memories = self.storage.list_memories()
        
        # Sort chronologically (oldest first)
        memories.sort(key=lambda m: m.date)
        
        # Apply tag filter if specified
        if tag_filter:
            filtered_memories = []
            for memory in memories:
                if any(tag in memory.tags for tag in tag_filter):
                    filtered_memories.append(memory)
            memories = filtered_memories
        
        # Apply limit if specified
        if limit:
            memories = memories[:limit]
        
        return memories
    
    def process_memory_tags(self, memory_id: str) -> Optional[Memory]:
        """Extract and update tags for existing memory.
        
        Args:
            memory_id: ID of memory to process tags for.
            
        Returns:
            Updated Memory instance, or None if not found.
        """
        memory = self.storage.get_memory_by_id(memory_id)
        if not memory:
            return None
        
        # Extract new tags
        auto_tags = self.tag_extractor.extract_tags(memory.description)
        
        # Combine existing and new tags
        all_tags = list(memory.tags) + auto_tags
        
        # Remove duplicates while preserving order
        unique_tags = []
        seen = set()
        for tag in all_tags:
            if tag not in seen:
                unique_tags.append(tag)
                seen.add(tag)
        
        # Update memory tags
        memory.tags = unique_tags
        
        # Save updated memory
        collection = self.storage.load_memories()
        for i, stored_memory in enumerate(collection.memories):
            if stored_memory.id == memory_id:
                collection.memories[i] = memory
                break
        
        self.storage.save_memories(collection)
        
        return memory
    
    def process_all_untagged_memories(self, min_tags: int = 2) -> int:
        """Process all memories with insufficient tags.
        
        Args:
            min_tags: Minimum number of tags required to skip processing.
            
        Returns:
            Number of memories processed.
        """
        memories = self.storage.list_memories()
        processed_count = 0
        
        for memory in memories:
            if len(memory.tags) < min_tags:
                self.process_memory_tags(memory.id)
                processed_count += 1
        
        return processed_count
    
    def get_top_memory(self) -> Optional[Memory]:
        """Find memory with the most tags.
        
        Returns:
            Memory with highest tag count, or None if no memories exist.
        """
        memories = self.storage.list_memories()
        if not memories:
            return None
        
        # Find memory with most tags
        top_memory = max(memories, key=lambda m: len(m.tags))
        return top_memory
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get statistics about the memory collection.
        
        Returns:
            Dictionary with collection statistics.
        """
        memories = self.storage.list_memories()
        
        if not memories:
            return {
                "total_memories": 0,
                "total_tags": 0,
                "most_common_tags": [],
                "locations_visited": [],
                "date_range": None
            }
        
        # Collect all tags
        all_tags = []
        for memory in memories:
            all_tags.extend(memory.tags)
        
        # Count tag frequencies
        tag_counter = Counter(all_tags)
        most_common_tags = tag_counter.most_common(10)
        
        # Collect unique locations
        locations = list(set(memory.location for memory in memories))
        
        # Find date range
        dates = [memory.date for memory in memories]
        date_range = {
            "earliest": min(dates),
            "latest": max(dates)
        }
        
        return {
            "total_memories": len(memories),
            "total_tags": len(all_tags),
            "unique_tags": len(set(all_tags)),
            "most_common_tags": most_common_tags,
            "locations_visited": locations,
            "date_range": date_range
        }
    
    def search_memories(self, query: str) -> List[Memory]:
        """Search memories by text in description.
        
        Args:
            query: Search term to look for in descriptions.
            
        Returns:
            List of memories matching the search query.
        """
        memories = self.storage.list_memories()
        query_lower = query.lower()
        
        matching_memories = []
        for memory in memories:
            if query_lower in memory.description.lower():
                matching_memories.append(memory)
        
        return matching_memories
    
    def search_memories_by_location(self, location_query: str) -> List[Memory]:
        """Search memories by location.
        
        Args:
            location_query: Location term to search for.
            
        Returns:
            List of memories with matching locations.
        """
        memories = self.storage.list_memories()
        query_lower = location_query.lower()
        
        matching_memories = []
        for memory in memories:
            if query_lower in memory.location.lower():
                matching_memories.append(memory)
        
        return matching_memories