# Software Design Document: Travel Memory Journal

## Overview
- **Purpose**: A local macOS application that helps travelers capture, organize, and easily recall their travel memories with minimal effort and zero cloud dependencies.
- **Stakeholders**: Travel enthusiasts, digital nomads, and occasional travelers who want to preserve meaningful travel experiences.
- **Key Requirements**: 
  - Performance: App launch < 3 seconds, memory search < 2 seconds, UI responsiveness < 100ms
  - Scalability: Handle 1000+ memories per user efficiently
  - Security: Local-only storage with no external data transmission
  - Usability: Memory addition in < 30 seconds, first memory added within 5 minutes

## System Architecture

### High-Level Design
```
CLI Interface (Typer) ’ Business Logic Layer ’ Data Access Layer ’ Local JSON Storage
                    “
            NLP Processing ’ Tag Extraction ’ Memory Analysis
```

### Core Components

#### CLI Layer (Typer Framework)
- **Commands**: 
  - `add-memory`: Capture new travel memories with location, date, description, tags
  - `list-memories`: Display chronological list of all memories
  - `process-memory`: Extract structured tags from natural language descriptions
  - `top-memory`: Identify memory with most tags
- **Input Validation**: Pydantic models for data validation
- **User Experience**: Interactive prompts, progress indicators, formatted output

#### Business Logic Layer
- **Memory Service**: Core CRUD operations for travel memories
- **NLP Service**: Natural language processing for tag extraction from descriptions
- **Analytics Service**: Memory analysis, ranking, and insights
- **Validation Service**: Data integrity and business rule enforcement

#### Data Layer
- **Storage Strategy**: Local JSON files for simplicity and zero dependencies
- **Data Models**: Pydantic models for type safety and validation
- **File Management**: Atomic writes, backup strategies, error recovery
- **Performance**: In-memory caching for frequently accessed data

#### Integration Layer
- **Local AI/NLP**: Tag extraction from natural language descriptions
- **File System**: Local storage management and data persistence
- **Error Handling**: Comprehensive error recovery and user feedback

### Data Architecture

#### Core Entities
```python
class Memory(BaseModel):
    id: str
    location: str
    date: datetime
    description: str
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

class MemoryCollection(BaseModel):
    memories: List[Memory]
    metadata: Dict[str, Any]
```

#### Storage Strategy
- **Primary Storage**: Single JSON file (`memories.json`) for all user memories
- **Backup Strategy**: Timestamped backup files on each write operation
- **Data Integrity**: JSON schema validation, atomic file operations
- **Performance**: In-memory loading with lazy persistence

#### Data Flow
1. **Input**: User provides memory details via CLI
2. **Validation**: Pydantic models validate and sanitize input
3. **Processing**: NLP service extracts tags from description
4. **Storage**: Memory persisted to local JSON file
5. **Retrieval**: In-memory cache serves read operations

#### Backup & Recovery
- **Backup Strategy**: Automatic backup before each write operation
- **Recovery**: Restore from most recent valid backup on corruption
- **Data Protection**: File permissions restrict access to user only

## Key Architectural Decisions Required

### Infrastructure Decisions
- [x] **Deployment Platform**: Local macOS application (no deployment needed)
- [x] **Package Management**: uv + pyproject.toml for dependency management
- [x] **Task Runner**: Poe the Poet for development workflows
- [x] **Distribution**: Local installation via pip or standalone executable

### Application Decisions  
- [x] **CLI Framework**: Typer for intuitive command-line interface
- [x] **Data Validation**: Pydantic for robust data models and validation
- [x] **Storage**: Local JSON files for simplicity and zero dependencies
- [x] **NLP Processing**: Local text processing for tag extraction (no external APIs)

### Development Decisions
- [x] **Testing Framework**: pytest + pytest-mock + coverage for comprehensive testing
- [x] **Code Quality**: ruff + mypy + sqlfluff for linting and type checking
- [x] **Project Structure**: Standard Python package structure with src/ layout
- [ ] **NLP Implementation**: Choose between rule-based parsing vs. local ML model

## Performance & Scalability

### Expected Load
- **User Base**: Single user per installation
- **Data Volume**: 1000+ memories per user (average 1KB per memory = 1MB total)
- **Usage Pattern**: Burst writes during/after travel, occasional browsing

### Scaling Strategy
- **Data Loading**: Lazy loading with in-memory caching
- **Search Performance**: Simple linear search for MVP, indexing for future iterations
- **Memory Management**: Efficient JSON serialization/deserialization
- **File I/O**: Batched writes, atomic operations

### Performance Targets
- **App Launch**: < 3 seconds (load and validate memory file)
- **Memory Search**: < 2 seconds (scan all memories and return results)
- **UI Responsiveness**: < 100ms (CLI command processing)
- **Memory Addition**: < 30 seconds (including tag extraction)

### Bottleneck Analysis
- **Potential Bottlenecks**:
  - JSON file size growth with 1000+ memories
  - Tag extraction processing time for long descriptions
  - File I/O operations on slower storage devices
- **Mitigation Strategies**:
  - Streaming JSON parsing for large datasets
  - Async processing for NLP operations
  - SSD storage recommendations

## Security & Compliance

### Authentication
- **Local Access**: File system permissions restrict access to user account
- **No Network**: Zero network access eliminates remote authentication needs
- **Session Management**: Not applicable for local CLI application

### Authorization
- **Access Control**: Operating system file permissions
- **Data Isolation**: Each user's data stored in their home directory
- **Permission Model**: Read/write access only for owning user

### Data Protection
- **Encryption**: File system level encryption (FileVault on macOS)
- **Privacy**: No external data transmission, local-only processing
- **Data Retention**: User controls all data lifecycle decisions
- **Compliance**: GDPR compliant by design (local-only, user-controlled)

## Implementation Priorities

### Phase 1: MVP (< 1 hour)
1. **Core Data Model**: Memory and MemoryCollection Pydantic models
2. **Basic CLI**: Add memory, list memories commands
3. **Local Storage**: JSON file read/write operations
4. **Simple Tag Extraction**: Basic keyword extraction from descriptions

### Phase 2: Enhanced Features
1. **Advanced NLP**: Improved tag extraction with categorization
2. **Memory Analytics**: Top memory identification, statistics
3. **Search & Filter**: Query memories by date, location, tags
4. **Data Management**: Import/export, backup/restore functionality

### Phase 3: Polish & Performance
1. **Performance Optimization**: Caching, indexing, async operations
2. **Error Handling**: Comprehensive error recovery and user feedback
3. **User Experience**: Rich CLI formatting, progress indicators
4. **Testing**: Comprehensive test coverage and CI/CD setup

## Architectural Decision Records (ADRs) Needed

1. **ADR-001**: Local JSON vs SQLite for data storage
2. **ADR-002**: Rule-based vs ML-based tag extraction approach
3. **ADR-003**: Single file vs multiple files for memory storage
4. **ADR-004**: In-memory caching strategy and cache invalidation
5. **ADR-005**: Error handling and recovery mechanisms for corrupted data
6. **ADR-006**: CLI command structure and user interaction patterns

## Risk Assessment

### Technical Risks
- **Data Loss Risk**: File corruption or accidental deletion
  - *Mitigation*: Automatic backups, atomic writes, data validation
- **Performance Risk**: Slowdown with large datasets
  - *Mitigation*: Performance monitoring, lazy loading, optimization strategies
- **NLP Quality Risk**: Poor tag extraction accuracy
  - *Mitigation*: Iterative improvement, user feedback, manual tag override

### Business Risks
- **User Adoption**: Complex CLI interface may deter casual users
  - *Mitigation*: Intuitive commands, helpful documentation, examples
- **Feature Scope**: Over-engineering for MVP timeline
  - *Mitigation*: Strict MVP focus, feature prioritization, time-boxing

This architecture balances simplicity with functionality, ensuring rapid MVP delivery while providing a foundation for future enhancements.