# ADR-0005: Error Handling and Recovery Mechanisms

**Status**: Accepted
**Date**: 2025-08-05
**Context**: Travel Memory Journal requires simple, reliable error handling for input validation and file operations while maintaining MVP simplicity.

## Problem Statement
How should we handle input validation errors and basic file I/O failures to provide clear user feedback without overcomplicating the MVP implementation?

## Decision Drivers
- **Business Requirements**: Clear error messages, reliable data validation
- **Technical Constraints**: Local JSON storage, Pydantic validation, MVP timeline
- **Team Constraints**: Simple implementation, rapid development
- **Non-Functional Requirements**: User-friendly error messages, data integrity

## Options Considered

### Option 1: Basic Pydantic Validation with Simple Error Handling (Recommended)
**Pros**:
- Leverages Pydantic's built-in validation capabilities
- Simple implementation perfect for MVP timeline
- Clear, actionable error messages
- Automatic data type validation and coercion
- Easy to test and debug

**Cons**:
- No automatic recovery mechanisms
- Basic file I/O error handling
- Users must fix validation errors manually

**Implementation Effort**: S (Small)
**Operational Complexity**: Low

### Option 2: Layered Defense with Backup Recovery
**Pros**:
- Multiple layers of protection prevent data loss
- Automatic recovery capabilities

**Cons**:
- Significant complexity increase
- Additional storage overhead
- Overkill for MVP requirements

**Why Not Chosen**: Too complex for MVP scope and timeline requirements

### Option 3: Database-Style Transaction Logs
**Pros**:
- Maximum data integrity guarantees

**Cons**:
- Massive complexity increase
- Conflicts with JSON storage approach

**Why Not Chosen**: Far too complex for our simple use case

## Decision
We will implement **Basic Pydantic Validation with Simple Error Handling**.

**Rationale**: This approach provides reliable data validation and clear error feedback while maintaining the simplicity required for rapid MVP development. Pydantic handles the heavy lifting of data validation automatically.

## Consequences
**Positive**:
- Fast development and implementation
- Reliable data validation using proven Pydantic framework
- Clear, actionable error messages for users
- Simple debugging and testing
- Automatic type coercion where appropriate

**Negative**:
- Basic error recovery (no automatic backups)
- Users must manually fix validation errors
- Simple file I/O error handling

**Implementation Notes**:
- Use Pydantic models for all data validation
- Provide clear error messages with examples
- Handle common file I/O errors gracefully
- Focus on preventing errors rather than complex recovery

## Error Handling Implementation

### Input Validation with Pydantic
```python
from pydantic import BaseModel, ValidationError
from datetime import datetime
from typing import List

class Memory(BaseModel):
    id: str
    location: str
    date: datetime
    description: str
    tags: List[str] = []

def create_memory(user_input: dict) -> Memory:
    try:
        return Memory(**user_input)
    except ValidationError as e:
        raise ValueError(f"Invalid memory data: {format_validation_errors(e)}")

def format_validation_errors(e: ValidationError) -> str:
    """Convert Pydantic errors to user-friendly messages"""
    messages = []
    for error in e.errors():
        field = error['loc'][0]
        msg = error['msg']
        messages.append(f"{field}: {msg}")
    return "; ".join(messages)
```

### File I/O Error Handling
```python
import json
from pathlib import Path

def save_memories(memories: MemoryCollection, file_path: Path) -> None:
    try:
        with open(file_path, 'w') as f:
            json.dump(memories.dict(), f, indent=2)
    except PermissionError:
        raise IOError(f"Permission denied writing to {file_path}")
    except OSError as e:
        raise IOError(f"Failed to write file: {e}")

def load_memories(file_path: Path) -> MemoryCollection:
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return MemoryCollection(**data)
    except FileNotFoundError:
        return MemoryCollection(memories=[])
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")
    except ValidationError as e:
        raise ValueError(f"Invalid data format: {format_validation_errors(e)}")
```

## Error Types and Messages

### Validation Errors
- **Date Format**: "Date must be in YYYY-MM-DD format (e.g., 2024-07-15)"
- **Missing Location**: "Location is required (e.g., 'Paris, France')"
- **Empty Description**: "Description cannot be empty"

### File Errors
- **Permission Denied**: "Cannot write to file. Check file permissions."
- **Disk Full**: "Not enough disk space to save memory."
- **Corrupted File**: "Memory file is corrupted. Starting with empty collection."

### User-Friendly Error Display
```
❌ Error adding memory:
   • Date: Invalid date format. Use YYYY-MM-DD (e.g., 2024-07-15)
   • Location: This field is required

💡 Example:
   travel-journal add-memory -l "Tokyo, Japan" -d "2024-07-15" --description "Amazing sushi"
```