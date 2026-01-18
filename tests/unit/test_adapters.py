"""
Unit tests for Adapters.
"""
import pytest
from vibe.adapters import AdapterRegistry, AntigravityAdapter, ClaudeCodeAdapter
from vibe.adapters.registry import IDENotSupportedError

def test_registry_get():
    adapter = AdapterRegistry.get("antigravity")
    assert isinstance(adapter, AntigravityAdapter)
    
    adapter = AdapterRegistry.get("gemini")  # Alias
    assert isinstance(adapter, AntigravityAdapter)
    
    adapter = AdapterRegistry.get("claude-code")
    assert isinstance(adapter, ClaudeCodeAdapter)

def test_registry_invalid():
    with pytest.raises(IDENotSupportedError):
        AdapterRegistry.get("invalid-ide")

def test_claude_merge_rules():
    adapter = ClaudeCodeAdapter()
    rules = {
        "00_project_context.md": "# Context",
        "01_workflow.md": "# Workflow"
    }
    
    merged = adapter._merge_rules(rules)
    
    assert "# CLAUDE.md" in merged
    assert "## 00 Project Context" in merged
    assert "# Context" in merged
    assert "# Workflow" in merged
