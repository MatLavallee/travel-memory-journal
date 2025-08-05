"""Travel Memory Journal CLI application."""

from functools import wraps
from pathlib import Path
from datetime import date, datetime
from typing import Optional, List

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from ai_journaling_assistant.config import get_app_config
from ai_journaling_assistant.services import MemoryService
from ai_journaling_assistant.models import create_memory_id

# Create the main Typer app
app = typer.Typer(
    name="travel-journal",
    help="🌍 Travel Memory Journal - Capture and relive your adventures",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()


# User messaging constants
NO_MEMORIES_MESSAGE = "📝 [yellow]No memories found. Add your first memory with:[/yellow]"
ADD_MEMORY_HINT = "   [dim]travel-journal add-memory[/dim]"


def show_no_memories_message() -> None:
    """Display consistent no memories found message."""
    rprint(NO_MEMORIES_MESSAGE)
    rprint(ADD_MEMORY_HINT)


def handle_cli_errors(func):
    """Decorator for consistent CLI error handling across commands."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except typer.Exit:
            # Re-raise typer.Exit without modification - it's intentional
            raise
        except ValueError as e:
            rprint(f"❌ [red]Validation error: {e}[/red]")
            raise typer.Exit(1)
        except PermissionError as e:
            rprint(f"❌ [red]Permission error: {e}[/red]")
            rprint("💡 [yellow]Check that you have write access to the storage directory[/yellow]")
            raise typer.Exit(1)
        except Exception as e:
            rprint(f"❌ [red]Unexpected error: {e}[/red]")
            raise typer.Exit(1)
    return wrapper


def get_memory_service() -> MemoryService:
    """Get configured memory service instance."""
    config = get_app_config()
    return MemoryService(config.storage_dir)


def parse_date_input(date_str: str) -> date:
    """Parse date input with support for 'today' shortcut.
    
    Args:
        date_str: Date string in YYYY-MM-DD format or 'today'.
        
    Returns:
        Parsed date object.
        
    Raises:
        ValueError: If date format is invalid.
    """
    if date_str.lower() == "today":
        return date.today()
    
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: '{date_str}'. Use YYYY-MM-DD or 'today'")


def parse_tags_input(tags_str: str) -> List[str]:
    """Parse comma-separated tags string.
    
    Args:
        tags_str: Comma-separated tags string.
        
    Returns:
        List of cleaned tag strings.
    """
    if not tags_str:
        return []
    
    return [tag.strip() for tag in tags_str.split(",") if tag.strip()]


@app.command()
@handle_cli_errors
def add_memory(
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Where this memory happened"),
    date_str: Optional[str] = typer.Option(None, "--date", "-d", help="When this happened (YYYY-MM-DD or 'today')"),
    description: Optional[str] = typer.Option(None, "--description", help="Describe your memory"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Manual tags (comma-separated)")
) -> None:
    """📝 Add a new travel memory to your collection.
    
    Examples:
      # Interactive mode (great for beginners)
      travel-journal add-memory
      
      # Quick capture
      travel-journal add-memory -l "Tokyo" -d "today" --description "Amazing ramen in Shibuya"
      
      # With manual tags
      travel-journal add-memory -l "Barcelona" -d "2024-06-15" --description "Gaudi architecture tour" --tags "architecture,culture,walking"
    """
    service = get_memory_service()
    
    # Interactive mode if missing required parameters
    if not all([location, date_str, description]):
        rprint("🌍 [bold blue]Let's add a new travel memory![/bold blue]\n")
        
        if not location:
            location = Prompt.ask("📍 Where were you?", default="")
            if not location.strip():
                rprint("❌ [red]Location is required[/red]")
                raise typer.Exit(1)
        
        if not date_str:
            date_str = Prompt.ask("📅 What date was this?", default="today")
        
        if not description:
            description = Prompt.ask("📝 Tell me about this memory")
            if not description.strip():
                rprint("❌ [red]Description is required[/red]")
                raise typer.Exit(1)
        
        if not tags:
            if Confirm.ask("🏷️  Want to add tags manually?", default=False):
                tags = Prompt.ask("Enter tags (comma-separated)", default="")
    
    # Parse and validate inputs
    try:
        memory_date = parse_date_input(date_str)
    except ValueError as e:
        rprint(f"❌ [red]Invalid date format: {e}[/red]")
        rprint("💡 [yellow]Try: '2024-07-15' (YYYY-MM-DD) or 'today'[/yellow]")
        raise typer.Exit(1)
    
    manual_tags = parse_tags_input(tags) if tags else None
    
    # Show processing indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("✨ Processing your memory for automatic tags...", total=None)
        
        # Add memory with service
        memory_id = service.add_memory(
            location=location.strip(),
            date=memory_date,
            description=description.strip(),
            manual_tags=manual_tags
        )
    
    # Get the saved memory to show extracted tags
    saved_memory = service.get_memory_by_id(memory_id)
    
    rprint("✅ [green]Memory saved successfully![/green]")
    rprint(f"🎯 [blue]Found tags:[/blue] {', '.join(saved_memory.tags) if saved_memory.tags else 'None'}")
    rprint(f"💾 [dim]Memory ID: {memory_id}[/dim]")


@app.command()
@handle_cli_errors
def list_memories(
    limit: Optional[int] = typer.Option(None, "--limit", help="Maximum number of memories to show")
) -> None:
    """📋 Browse your memory collection in chronological order.
    
    Examples:
      # Show all memories
      travel-journal list-memories
      
      # Show only recent 10 memories
      travel-journal list-memories --limit 10
    """
    service = get_memory_service()
    memories = service.list_memories(limit=limit)
    
    if not memories:
        show_no_memories_message()
        return
    
    # Create table for displaying memories
    table = Table(title="🌍 Your Travel Memories", show_header=True, header_style="bold blue")
    table.add_column("Date", style="cyan", width=12)
    table.add_column("Location", style="green", width=25)
    table.add_column("Description", style="white", width=40)
    table.add_column("Tags", style="yellow", width=20)
    
    for memory in memories:
        # Truncate long descriptions
        desc = memory.description
        if len(desc) > 40:
            desc = desc[:37] + "..."
        
        # Format tags
        tags_str = ", ".join(memory.tags[:3])  # Show first 3 tags
        if len(memory.tags) > 3:
            tags_str += f" (+{len(memory.tags) - 3})"
        
        table.add_row(
            memory.date.strftime("%Y-%m-%d"),
            memory.location,
            desc,
            tags_str or "[dim]no tags[/dim]"
        )
    
    console.print(table)
    rprint(f"\n📊 [dim]Showing {len(memories)} memories[/dim]")


@app.command()
@handle_cli_errors
def process_memory(
    memory_id: Optional[str] = typer.Argument(None, help="Memory ID to process"),
    all_memories: bool = typer.Option(False, "--all", help="Process all memories with insufficient tags")
) -> None:
    """🏷️ Extract tags from memory descriptions.
    
    Examples:
      # Process specific memory
      travel-journal process-memory abc123
      
      # Process all untagged memories
      travel-journal process-memory --all
    """
    service = get_memory_service()
    
    if all_memories:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("🔄 Processing memories for tags...", total=None)
            processed_count = service.process_all_untagged_memories()
        
        rprint(f"✅ [green]Processed {processed_count} memories[/green]")
        
    elif memory_id:
        updated_memory = service.process_memory_tags(memory_id)
        if updated_memory:
            rprint(f"✅ [green]Updated memory tags[/green]")
            rprint(f"🎯 [blue]Tags:[/blue] {', '.join(updated_memory.tags)}")
        else:
            rprint(f"❌ [red]Memory not found: {memory_id}[/red]")
            raise typer.Exit(1)
    else:
        rprint("❌ [red]Please specify a memory ID or use --all[/red]")
        raise typer.Exit(1)


@app.command()
@handle_cli_errors
def top_memory() -> None:
    """🏆 Find your memory with the most tags.
    
    Examples:
      travel-journal top-memory
    """
    service = get_memory_service()
    top_mem = service.get_top_memory()
    
    if not top_mem:
        show_no_memories_message()
        return
    
    rprint("🏆 [bold yellow]Your Top Memory (Most Tagged)[/bold yellow]\n")
    
    # Create detailed display for top memory
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="cyan", width=12)
    table.add_column("Value", style="white")
    
    table.add_row("📅 Date:", top_mem.date.strftime("%Y-%m-%d"))
    table.add_row("📍 Location:", top_mem.location)
    table.add_row("📝 Description:", top_mem.description)
    table.add_row("🏷️ Tags:", ", ".join(top_mem.tags) if top_mem.tags else "None")
    table.add_row("📊 Tag Count:", str(len(top_mem.tags)))
    
    console.print(table)


if __name__ == "__main__":
    app()