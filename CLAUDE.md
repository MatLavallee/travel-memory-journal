# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Travel Memory Journal CLI application that helps users capture, organize, and recall travel memories using local JSON storage with automatic tag extraction. The MVP is designed for rapid memory capture (< 30 seconds) with intelligent organization through rule-based NLP.

## Development Commands

### Core Development Workflow
```bash
# Install dependencies and set up environment
uv sync

# Run the application (see available commands)
uv run ai-journaling-assistant --help

# Test the app with sample memory
uv run ai-journaling-assistant add-memory -l "Paris, France" -d "today" --description "Amazing day at the Louvre"

# Run all tests (current status: 109/110 passing)
uv run pytest

# Run specific test file
uv run pytest tests/test_services.py

# Run single test method
uv run pytest tests/test_cli_commands.py::TestCLIErrorHandling::test_cli_helpful_error_messages -v

# Code quality checks
uv run ruff check .
uv run ruff format .
uv run mypy src/

# Test coverage report
uv run coverage run && uv run coverage report && uv run coverage xml
```

### Available CLI Commands (Sprint 1 Complete)
- `add-memory` - Capture new memories (interactive & quick modes)
- `list-memories` - Browse chronological memory collection
- `process-memory` - Extract tags from descriptions via NLP
- `top-memory` - Find memory with most tags

## Architecture Overview

### Layered Architecture Pattern
```
CLI Layer (cli.py) → Services Layer (services.py) → Storage Layer (storage.py) → Models (models.py)
                   ↓
            NLP Processing (tag_extraction.py) + Configuration (config.py)
```

**Key Architectural Decisions:**
- **ADR-0001**: Local JSON storage (single `memories.json` file) with atomic operations
- **ADR-0002**: Rule-based tag extraction using travel-specific keyword dictionaries
- **ADR-0003**: Single file storage with automated timestamped backups
- **ADR-0004**: Load-once full cache strategy for 1000+ memories
- **ADR-0005**: Basic Pydantic validation with user-friendly error messages
- **ADR-0006**: Verb-noun CLI command structure with interactive + quick modes

### Core Components

**Models (`models.py`)**:
- `Memory`: Pydantic model with id, location, date, description, tags, timestamps
- `MemoryCollection`: Container with metadata and collection operations
- UUID-based memory identification with automatic timestamp management

**Storage (`storage.py`)**:
- `StorageService`: Atomic JSON file operations with backup strategy
- Follows single-file storage pattern (`~/.travel-memory-journal/memories.json`)
- Automatic backup creation before writes, cleanup keeps last 5 backups
- Error handling with automatic backup restoration on corruption

**Services (`services.py`)**:
- `MemoryService`: Business logic orchestration layer
- CRUD operations with automatic tag processing
- Search capabilities by text and location (backend ready for Sprint 2)
- Memory analytics and tag processing workflows
- **Known Issue**: Tag deduplication logic duplicated 3 times (needs refactoring)

**Tag Extraction (`tag_extraction.py`)**:
- `TagExtractor`: Rule-based NLP engine with 8 travel categories
- 130+ keywords across food, culture, outdoor, transport, accommodation, shopping, entertainment, experience
- Linguistic variation handling (plurals, verb forms) with regex patterns
- Context-aware categorization for travel-specific content

**CLI (`cli.py`)**:
- Rich terminal UI with Typer framework
- Interactive mode (guided prompts) + Quick mode (command flags)
- Progress indicators, emoji feedback, formatted table displays
- **Known Issue**: Error handling pattern duplicated 4 times across commands (needs decorator)

**Configuration (`config.py`)**:
- `AppConfig`: Centralized settings with Pydantic validation
- `get_tag_categories()`: Travel keyword dictionaries (8 categories, 130+ terms)
- Storage path management with automatic directory creation

## Development Context

### Current Sprint Status
- **Sprint 1**: ✅ COMPLETED (exceeded scope - delivered Sprint 2 features early)
- **Sprint 2**: 🚧 IN PROGRESS (enhanced search/discovery, memory management)
- **Sprint 3**: 📋 PLANNED (production readiness, scale optimization)

### Test Coverage Standards
Maintain >95% test coverage with comprehensive scenarios:
- Happy path flows, error conditions, edge cases
- CLI interactive mode testing with CliRunner
- Service layer integration testing with mocking
- **Current Status**: 109/110 tests passing (99.1% success rate)
- **Failing Test**: `test_cli_helpful_error_messages` (EOF handling in interactive mode)

### Code Quality Patterns

**Service Layer Pattern**:
- CLI commands are thin wrappers around `MemoryService`
- Business logic lives in services, not CLI handlers
- Services handle validation and error cases

**Error Handling Strategy**:
- Pydantic validation with user-friendly messages
- Consistent CLI error formatting with emoji indicators
- Graceful degradation with clear recovery instructions

**Data Flow Pattern**:
1. CLI input validation → 2. Service orchestration → 3. Tag extraction → 4. Storage persistence → 5. Response formatting

## Critical Issues to Address Before New Development

### URGENT: DRY Violations (from Sprint 1 Code Review)
1. **Tag deduplication logic**: Duplicated 3 times in `services.py` (lines 57-69, 142-154)
2. **CLI error handling**: Duplicated 4 times across commands - needs decorator pattern
3. **Storage abstraction leak**: `process_memory_tags` manipulates `MemoryCollection` internals

### Sprint 2 Development Notes
- Backend search methods already implemented in `MemoryService`
- Missing CLI commands: `search-memories`, `show-memory`, `edit-memory`, `delete-memory`
- Focus on exposing existing functionality through CLI rather than building new backend services

## Storage Location
- Primary: `~/.travel-memory-journal/memories.json`
- Backups: `~/.travel-memory-journal/backups/memories-YYYY-MM-DD-HH-MM-SS.json`
- Configuration: `~/.travel-memory-journal/config.json` (if needed)