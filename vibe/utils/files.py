import sys
from pathlib import Path
from vibe.cli.console import console

def read_template(filename: str, folder: Path) -> str:
    path = folder / filename
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Template not found: {path}")
        sys.exit(1)
