"""
Vibe-CLI Agents Module.
"""
from vibe.agents.base import BaseAgent, AgentResult
from vibe.agents.analyst import AnalystAgent
from vibe.agents.architect import ArchitectAgent
from vibe.agents.project_manager import ProjectManagerAgent
from vibe.agents.injector import InjectorAgent

__all__ = [
    "BaseAgent",
    "AgentResult",
    "AnalystAgent",
    "ArchitectAgent",
    "ProjectManagerAgent",
    "InjectorAgent",
]
