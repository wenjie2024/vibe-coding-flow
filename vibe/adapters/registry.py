"""
IDE Adapter Registry for Vibe-CLI.
"""
from typing import Dict, Type
from vibe.adapters.base import IDEAdapter
from vibe.adapters.antigravity import AntigravityAdapter
from vibe.adapters.claude_code import ClaudeCodeAdapter
from vibe.adapters.cursor import CursorAdapter


class IDENotSupportedError(Exception):
    """Raised when an unsupported IDE is requested."""
    def __init__(self, ide_name: str, supported: list):
        self.ide_name = ide_name
        self.supported = supported
        super().__init__(f"Unsupported IDE: {ide_name}. Supported IDEs: {supported}")


class AdapterRegistry:
    """
    Registry for IDE adapters.
    Provides factory method to get adapter instances by name.
    """

    _adapters: Dict[str, Type[IDEAdapter]] = {
        "antigravity": AntigravityAdapter,
        "claude-code": ClaudeCodeAdapter,
        "cursor": CursorAdapter,
    }

    # Alias mappings
    _aliases: Dict[str, str] = {
        "gemini": "antigravity",
        "claude": "claude-code",
        "vscode": "cursor",  # Cursor is based on VSCode
    }

    @classmethod
    def get(cls, ide_name: str) -> IDEAdapter:
        """
        Get an adapter instance by IDE name.
        
        Args:
            ide_name: Name of the IDE (case-insensitive).
        
        Returns:
            An instance of the corresponding adapter.
        
        Raises:
            IDENotSupportedError: If the IDE is not supported.
        """
        normalized = ide_name.lower().strip()

        # Check aliases
        if normalized in cls._aliases:
            normalized = cls._aliases[normalized]

        if normalized not in cls._adapters:
            supported = list(cls._adapters.keys())
            raise IDENotSupportedError(ide_name, supported)

        return cls._adapters[normalized]()

    @classmethod
    def list_supported(cls) -> list:
        """List all supported IDE names."""
        return list(cls._adapters.keys())

    @classmethod
    def register(cls, name: str, adapter_class: Type[IDEAdapter]) -> None:
        """
        Register a custom adapter.
        
        Args:
            name: Name to register the adapter under.
            adapter_class: The adapter class to register.
        """
        cls._adapters[name.lower()] = adapter_class
