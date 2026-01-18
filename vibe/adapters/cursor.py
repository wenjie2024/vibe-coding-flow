"""
Cursor IDE Adapter for Vibe-CLI.
"""
from pathlib import Path
from typing import Dict, List, Any
from vibe.adapters.base import IDEAdapter


class CursorAdapter(IDEAdapter):
    """
    Adapter for Cursor IDE.
    Uses .cursorrules file at project root.
    """

    @property
    def name(self) -> str:
        return "cursor"

    @property
    def rules_dir_name(self) -> str:
        return ".cursor"

    @property
    def global_rules_filename(self) -> str:
        return ".cursorrules"

    def get_rules_directory(self, project_dir: Path) -> Path:
        return project_dir / ".cursor"

    def get_global_rules_path(self) -> Path:
        return Path.home() / ".cursor" / "rules.md"

    def write_rules(self, project_dir: Path, rules: Dict[str, str]) -> None:
        """
        Cursor uses a single .cursorrules file at project root.
        Also stores individual rules in .cursor/ for reference.
        """
        # Merge rules into single .cursorrules file
        combined = self._merge_rules_for_cursor(rules)
        (project_dir / ".cursorrules").write_text(combined, encoding="utf-8")

        # Also save to .cursor directory for reference
        cursor_dir = self.get_rules_directory(project_dir)
        cursor_dir.mkdir(exist_ok=True)
        for filename, content in rules.items():
            (cursor_dir / filename).write_text(content, encoding="utf-8")

    def _merge_rules_for_cursor(self, rules: Dict[str, str]) -> str:
        """Merge rules into Cursor format."""
        sections = ["# Project Rules for Cursor\n"]

        for rule_name, content in sorted(rules.items()):
            # Remove YAML frontmatter if present
            clean_content = self._remove_frontmatter(content)
            sections.append(f"\n## {rule_name}\n")
            sections.append(clean_content)

        return "\n".join(sections)

    def _remove_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from markdown content."""
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content

    def write_config(self, project_dir: Path, config: Dict[str, Any]) -> None:
        """Cursor doesn't require additional config files."""
        pass

    def get_supported_features(self) -> List[str]:
        return ["rules", "context"]
