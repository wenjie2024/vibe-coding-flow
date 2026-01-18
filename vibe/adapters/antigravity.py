"""
Antigravity (Google) IDE Adapter for Vibe-CLI.
"""
from pathlib import Path
from typing import Dict, List, Any
from vibe.adapters.base import IDEAdapter


class AntigravityAdapter(IDEAdapter):
    """
    Adapter for Google Antigravity IDE.
    Uses .agent/rules/ directory structure and GEMINI.md global rules.
    """

    @property
    def name(self) -> str:
        return "antigravity"

    @property
    def rules_dir_name(self) -> str:
        return ".agent/rules"

    @property
    def global_rules_filename(self) -> str:
        return "GEMINI.md"

    def get_rules_directory(self, project_dir: Path) -> Path:
        return project_dir / ".agent" / "rules"

    def get_global_rules_path(self) -> Path:
        return Path.home() / ".gemini" / "GEMINI.md"

    def write_rules(self, project_dir: Path, rules: Dict[str, str]) -> None:
        """Write individual rule files to .agent/rules/"""
        rules_dir = self.get_rules_directory(project_dir)
        rules_dir.mkdir(parents=True, exist_ok=True)

        for filename, content in rules.items():
            (rules_dir / filename).write_text(content, encoding="utf-8")

    def write_config(self, project_dir: Path, config: Dict[str, Any]) -> None:
        """Antigravity doesn't require additional config files."""
        pass

    def get_supported_features(self) -> List[str]:
        return ["rules", "context", "plan_workflow"]
