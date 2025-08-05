# Travel Memory Journal

A local macOS CLI application that helps travelers capture, organize, and easily recall their travel memories with minimal effort. Built with Python, featuring automatic tag extraction and intelligent memory organization.

## Features

- **Quick Memory Capture**: Add memories in under 30 seconds with interactive or quick modes
- **Automatic Tag Extraction**: Rule-based NLP engine extracts meaningful tags from natural language descriptions
- **Local-First**: All data stored locally with no cloud dependencies for complete privacy
- **Rich CLI Experience**: Beautiful terminal interface with progress indicators and formatted displays
- **Smart Organization**: Chronological sorting, tag-based filtering, and memory analytics
- **Data Safety**: Atomic file operations with automatic timestamped backups

## Quick Start

```bash
# Install dependencies
uv sync

# Add your first memory (interactive mode)
uv run ai-journaling-assistant add-memory

# Quick capture
uv run ai-journaling-assistant add-memory -l "Tokyo, Japan" -d "today" --description "Amazing ramen in Shibuya"

# Browse your memories
uv run ai-journaling-assistant list-memories

# Find your top memory (most tags)
uv run ai-journaling-assistant top-memory
```

## Available Commands

- `add-memory` - 📝 Capture new travel memories (interactive & quick modes)
- `list-memories` - 📋 Browse your memory collection chronologically  
- `process-memory` - 🏷️ Extract tags from memory descriptions using NLP
- `top-memory` - 🏆 Find your memory with the most tags

## Example Usage

### Adding a Memory
```bash
# Interactive mode with guided prompts
$ uv run ai-journaling-assistant add-memory
🌍 Let's add a new travel memory!

📍 Where were you? Paris, France
📅 What date was this? 2024-07-15
📝 Tell me about this memory: Amazing day exploring the Louvre museum, saw the Mona Lisa, then had incredible wine and cheese at a local bistro
🏷️ Want to add tags manually? n

✨ Processing your memory for automatic tags...
🎯 Found tags: museum, art, culture, wine, food, restaurant
💾 Memory saved successfully! ID: abc123
```

### Automatic Tag Extraction
The system automatically extracts relevant tags from your descriptions using travel-specific categories:

**Input:**
```
Today I visited Paris, went to a restaurant, had coffee, some good wine from Beaujolais, 
visited the Louvre, saw the Mona Lisa, then went skiing and shopping at the local market.
```

**Output:**
```json
{
    "food": ["restaurant", "coffee", "wine", "beaujolais"],
    "culture": ["louvre", "art"],
    "outdoor": ["skiing"],
    "shopping": ["market", "shopping"]
}
```

## Architecture

The application follows a clean layered architecture:

```
CLI Layer (cli.py) → Services Layer (services.py) → Storage Layer (storage.py) → Models (models.py)
                   ↓
            NLP Processing (tag_extraction.py) + Configuration (config.py)
```

### Key Design Decisions
- **Local JSON Storage**: Single file with atomic operations and automated backups
- **Rule-Based NLP**: 130+ travel keywords across 8 categories for tag extraction
- **Load-Once Caching**: Entire dataset cached in memory for fast operations
- **Rich Terminal UI**: Beautiful formatting with progress indicators and emoji feedback

## Development

```bash
# Run tests (currently 109/110 passing)
uv run pytest

# Code quality checks
uv run ruff check .
uv run mypy src/

# Test coverage
uv run coverage run && uv run coverage report
```

## Data Storage

Your memories are stored locally in `~/.travel-memory-journal/`:
- `memories.json` - Primary memory storage
- `backups/` - Automatic timestamped backups (keeps last 5)

## Tag Categories

The system recognizes 8 travel-specific categories:
- **Food**: restaurant, cafe, coffee, wine, cuisine, dining
- **Culture**: museum, temple, art, architecture, history, festival
- **Outdoor**: hiking, beach, mountain, nature, photography
- **Transport**: flight, train, bus, taxi, walking
- **Accommodation**: hotel, hostel, airbnb, resort
- **Shopping**: market, mall, souvenir, boutique
- **Entertainment**: nightlife, music, show, festival
- **Experience**: amazing, beautiful, relaxing, exciting

## Project Status

- **Sprint 1**: ✅ **COMPLETED** - Core functionality with advanced features
- **Sprint 2**: 🚧 **IN PROGRESS** - Enhanced search and memory management  
- **Sprint 3**: 📋 **PLANNED** - Production readiness and scale optimization

## Requirements

- Python 3.12+
- macOS (designed for local-first usage)
- uv package manager