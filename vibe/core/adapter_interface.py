from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class RuleBundle:
    """
    Core bundle of rules and content generated from Vibe templates (IDE-agnostic).
    These are the 'raw materials' that Adapters will project into IDE-specific formats.
    """
    # Map of standard Vibe rule names to their rendered content
    # e.g., "00_project_context.md" -> "... content ..."
    rules: Dict[str, str] = field(default_factory=dict)
    
    # Map of script names to their content
    # e.g., "inspect_sdk.py" -> "print('hello')"
    scripts: Dict[str, str] = field(default_factory=dict)

    # Map of skill name to its internal files
    # e.g., "doc-maintainer" -> {
    #    "SKILL.md": "...",
    #    "scripts/analyze.py": "..."
    # }
    skills: Dict[str, Dict[str, str]] = field(default_factory=dict)

@dataclass
class WritePlan:
    """
    A plan describing what files to write for a specific IDE.
    Designed to be executed by a safe I/O handler.
    """
    # Map of relative paths (from project root) to file content
    # e.g., ".cursor/rules/core.mdc" -> "..."
    #       "CLAUDE.md" -> "..."
    files: Dict[str, str] = field(default_factory=dict)
    
    # List of files that should be backed up if they exist and are about to be overwritten
    # implied by the keys in 'files', but explicit control can be useful.
    # For now, the execution engine handles backup for ANY overwrite.

class BaseAdapter(ABC):
    """
    Abstract base class for IDE adapters.
    """
    
    @abstractmethod
    def project(self, rule_bundle: RuleBundle) -> WritePlan:
        """
        Project the agnostic rule bundle into an IDE-specific write plan.
        
        Args:
            rule_bundle: The standard set of Vibe rules.
            
        Returns:
            WritePlan: A dictionary of file paths and contents to be written.
        """
        pass
