"""
Template Loader for Vibe-CLI.
"""
from pathlib import Path
from typing import Optional
from vibe.cli.console import console


class TemplateLoader:
    """
    Loads and manages template files.
    """

    def __init__(self, templates_dir: Path):
        """
        Initialize the loader with a templates directory.
        
        Args:
            templates_dir: Path to the templates directory.
        """
        self.templates_dir = templates_dir

    def load(self, filename: str, subfolder: Optional[str] = None) -> str:
        """
        Load a template file.
        
        Args:
            filename: Name of the template file.
            subfolder: Optional subfolder within templates dir.
        
        Returns:
            The template content as a string.
        
        Raises:
            FileNotFoundError: If template doesn't exist.
        """
        if subfolder:
            path = self.templates_dir / subfolder / filename
        else:
            path = self.templates_dir / filename

        if not path.exists():
            raise FileNotFoundError(f"Template not found: {path}")

        return path.read_text(encoding="utf-8")

    def load_prompt(self, filename: str) -> str:
        """Load a prompt template."""
        return self.load(filename, "prompts")

    def load_rule(self, filename: str) -> str:
        """Load a rule template."""
        return self.load(filename, "rules")

    def render(self, template: str, **kwargs) -> str:
        """
        Render a template with variable substitution.
        
        Args:
            template: Template string with {{variable}} placeholders.
            **kwargs: Variables to substitute.
        
        Returns:
            Rendered template string.
        """
        result = template
        for key, value in kwargs.items():
            placeholder = "{{" + key + "}}"
            result = result.replace(placeholder, str(value))
        return result
