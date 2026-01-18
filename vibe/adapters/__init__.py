"""
Vibe-CLI Adapters Module.
"""
from vibe.adapters.base import IDEAdapter
from vibe.adapters.antigravity import AntigravityAdapter
from vibe.adapters.claude_code import ClaudeCodeAdapter
from vibe.adapters.cursor import CursorAdapter
from vibe.adapters.registry import AdapterRegistry, IDENotSupportedError

__all__ = [
    "IDEAdapter",
    "AntigravityAdapter",
    "ClaudeCodeAdapter",
    "CursorAdapter",
    "AdapterRegistry",
    "IDENotSupportedError",
]
