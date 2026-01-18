"""
Claude Code IDE Adapter for Vibe-CLI.
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from vibe.adapters.base import IDEAdapter


class ClaudeCodeAdapter(IDEAdapter):
    """
    Adapter for Claude Code IDE.
    Uses CLAUDE.md at project root and .claude/ directory for settings.
    """

    @property
    def name(self) -> str:
        return "claude-code"

    @property
    def rules_dir_name(self) -> str:
        return ".claude"

    @property
    def global_rules_filename(self) -> str:
        return "CLAUDE.md"

    def get_rules_directory(self, project_dir: Path) -> Path:
        return project_dir / ".claude"

    def get_global_rules_path(self) -> Path:
        return Path.home() / ".claude" / "CLAUDE.md"

    def write_rules(self, project_dir: Path, rules: Dict[str, str]) -> None:
        """
        Claude Code uses a single CLAUDE.md file at project root.
        Also stores individual rules in .claude/rules/ for reference.
        """
        claude_dir = self.get_rules_directory(project_dir)
        claude_dir.mkdir(parents=True, exist_ok=True)

        # Merge all rules into single CLAUDE.md
        combined_content = self._merge_rules(rules)
        (project_dir / "CLAUDE.md").write_text(combined_content, encoding="utf-8")

        # Also save individual files for reference
        rules_subdir = claude_dir / "rules"
        rules_subdir.mkdir(exist_ok=True)
        for filename, content in rules.items():
            (rules_subdir / filename).write_text(content, encoding="utf-8")

    def _merge_rules(self, rules: Dict[str, str]) -> str:
        """Merge multiple rule files into a single CLAUDE.md format."""
        sections = []

        # Priority order for rules
        priority_order = [
            "00_project_context.md",
            "00a_project_environment.md",
            "00b_llm_integration.md",
            "01_workflow_plan_first.md",
        ]

        # Header
        sections.append("# CLAUDE.md (PROJECT RULES)\n")
        sections.append("This file contains all project rules for Claude Code.\n")
        sections.append("---\n")

        # Add priority rules first
        for rule_name in priority_order:
            if rule_name in rules:
                title = rule_name.replace(".md", "").replace("_", " ").title()
                sections.append(f"\n## {title}\n")
                sections.append(rules[rule_name])
                sections.append("\n---\n")

        # Add stack rules
        for rule_name, content in rules.items():
            if rule_name.startswith("02_stack_"):
                sections.append(f"\n## Tech Stack: {rule_name}\n")
                sections.append(content)
                sections.append("\n---\n")

        # Add remaining rules
        for rule_name, content in rules.items():
            if rule_name not in priority_order and not rule_name.startswith("02_stack_"):
                sections.append(f"\n## {rule_name}\n")
                sections.append(content)
                sections.append("\n---\n")

        return "\n".join(sections)

    def write_config(self, project_dir: Path, config: Dict[str, Any]) -> None:
        """Write Claude Code specific configuration (settings.local.json)."""
        claude_dir = self.get_rules_directory(project_dir)
        claude_dir.mkdir(parents=True, exist_ok=True)

        settings = {
            "permissions": {
                "allow": config.get("allowed_commands", []),
                "deny": config.get("denied_commands", [])
            }
        }

        settings_path = claude_dir / "settings.local.json"
        settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")

    def get_supported_features(self) -> List[str]:
        return ["rules", "context", "plan_workflow", "permissions", "mcp_servers"]

    def generate_mcp_config(self, project_dir: Path, servers: List[Dict]) -> None:
        """Generate MCP server configuration (Claude Code specific feature)."""
        claude_dir = self.get_rules_directory(project_dir)
        claude_dir.mkdir(parents=True, exist_ok=True)

        mcp_config = {"mcpServers": servers}
        (claude_dir / "mcp.json").write_text(
            json.dumps(mcp_config, indent=2),
            encoding="utf-8"
        )
