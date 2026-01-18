"""
IDE Adapter Base Class for Vibe-CLI.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any


class IDEAdapter(ABC):
    """
    Abstract base class for IDE adapters.
    Each adapter knows how to generate project rules for a specific IDE.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the IDE."""
        pass

    @property
    @abstractmethod
    def rules_dir_name(self) -> str:
        """
        Name of the rules directory within the project.
        e.g., '.agent/rules' for Antigravity, '.claude' for Claude Code.
        """
        pass

    @property
    @abstractmethod
    def global_rules_filename(self) -> str:
        """
        Name of the global rules file.
        e.g., 'GEMINI.md' for Antigravity, 'CLAUDE.md' for Claude Code.
        """
        pass

    @abstractmethod
    def get_rules_directory(self, project_dir: Path) -> Path:
        """Get the full path to the rules directory within the project."""
        pass

    @abstractmethod
    def get_global_rules_path(self) -> Path:
        """Get the path to the user's global rules file."""
        pass

    @abstractmethod
    def write_rules(self, project_dir: Path, rules: Dict[str, str]) -> None:
        """
        Write rules files to the project.
        
        Args:
            project_dir: Path to the project root.
            rules: Dictionary mapping filename to content.
        """
        pass

    @abstractmethod
    def write_config(self, project_dir: Path, config: Dict[str, Any]) -> None:
        """
        Write IDE-specific configuration files.
        
        Args:
            project_dir: Path to the project root.
            config: Configuration dictionary.
        """
        pass

    @abstractmethod
    def get_supported_features(self) -> List[str]:
        """Return list of features supported by this IDE adapter."""
        pass
