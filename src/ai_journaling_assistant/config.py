"""Travel Memory Journal configuration management."""

import copy
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel


class AppConfig(BaseModel):
    """Application configuration with default values."""
    
    storage_dir: Path
    backup_count: int = 5
    max_memories: int = 10000
    version: str = "1.0"


def get_app_config(storage_dir: Optional[Path] = None) -> AppConfig:
    """Get application configuration with defaults.
    
    Args:
        storage_dir: Custom storage directory path. Defaults to ~/.travel-memory-journal
        
    Returns:
        AppConfig instance with application settings.
    """
    if storage_dir is None:
        storage_dir = Path.home() / ".travel-memory-journal"
    
    return AppConfig(storage_dir=storage_dir)


def get_storage_path(storage_dir: Path) -> Path:
    """Create and return storage directory path.
    
    Creates the storage directory and required subdirectories
    if they don't exist.
    
    Args:
        storage_dir: Path where memories will be stored.
        
    Returns:
        Absolute path to storage directory.
        
    Raises:
        PermissionError: If directory cannot be created due to permissions.
    """
    # Convert to absolute path
    storage_dir = storage_dir.resolve()
    
    try:
        # Create main storage directory
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backups subdirectory
        backups_dir = storage_dir / "backups"
        backups_dir.mkdir(exist_ok=True)
        
    except PermissionError:
        raise PermissionError(f"Cannot create storage directory: {storage_dir}")
    
    return storage_dir


def get_tag_categories() -> Dict[str, List[str]]:
    """Get travel-specific tag categories and keywords.
    
    Returns:
        Dictionary mapping category names to lists of keywords.
        Returns a copy to prevent accidental modification.
    """
    categories = {
        "food": [
            "restaurant", "cafe", "coffee", "wine", "beer", "tasting",
            "market", "street food", "cuisine", "cooking", "bakery",
            "bar", "pub", "brewery", "vineyard", "dining", "lunch",
            "dinner", "breakfast", "snack", "local food", "specialty"
        ],
        "culture": [
            "museum", "temple", "church", "art", "architecture", "history",
            "monument", "palace", "castle", "gallery", "exhibition",
            "cultural", "heritage", "traditional", "festival", "ceremony",
            "performance", "theater", "music", "dance", "sculpture",
            "painting", "historic"
        ],
        "outdoor": [
            "hiking", "beach", "mountain", "nature", "park", "forest",
            "lake", "river", "ocean", "trail", "camping", "climbing",
            "swimming", "surfing", "kayaking", "cycling", "walking",
            "trekking", "wildlife", "scenic", "viewpoint", "sunrise",
            "sunset", "photography"
        ],
        "transport": [
            "flight", "train", "bus", "taxi", "metro", "subway",
            "ferry", "boat", "car", "rental", "uber", "lyft",
            "walking", "cycling", "scooter", "rickshaw", "tram",
            "cable car", "funicular", "helicopter", "transfer"
        ],
        "accommodation": [
            "hotel", "hostel", "airbnb", "resort", "guesthouse",
            "bed and breakfast", "camping", "glamping", "motel",
            "inn", "lodge", "villa", "apartment", "homestay",
            "boutique", "luxury", "budget", "booking", "check-in",
            "room", "suite"
        ],
        "shopping": [
            "market", "mall", "store", "shop", "boutique", "souvenir",
            "gift", "local", "craft", "handmade", "antique",
            "vintage", "fashion", "clothing", "jewelry", "art",
            "books", "spices", "textiles", "bargaining", "purchase"
        ],
        "entertainment": [
            "nightlife", "club", "bar", "live music", "concert",
            "show", "casino", "games", "sports", "event",
            "party", "dancing", "karaoke", "comedy", "cinema",
            "theater", "amusement park", "theme park", "festival"
        ],
        "experience": [
            "amazing", "beautiful", "incredible", "stunning", "awesome",
            "wonderful", "fantastic", "memorable", "unique", "special",
            "relaxing", "exciting", "adventurous", "peaceful", "romantic",
            "fun", "interesting", "inspiring", "breathtaking", "unforgettable"
        ]
    }
    
    # Return a deep copy to prevent modification
    return copy.deepcopy(categories)