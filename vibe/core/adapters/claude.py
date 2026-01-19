import json
from pathlib import Path
from vibe.core.adapter_interface import BaseAdapter, RuleBundle, WritePlan

from vibe.core.adapter_registry import AdapterRegistry

@AdapterRegistry.register("claude")
class ClaudeAdapter(BaseAdapter):
    """
    Adapter for Anthropic's Claude Code.
    Aggregates rules into CLAUDE.md and manages .claude/ configuration.
    """
    
    def project(self, rule_bundle: RuleBundle) -> WritePlan:
        plan = WritePlan()
        
        # 1. Aggregate CLAUDE.md
        claude_content = [
            "# CLAUDE.md - Project Rules",
            "",
            "## Core Context (MUST READ)",
            "- **Active Context**: Read `.context/activeContext.md` to understand current task status.",
            "- **Product Context**: Read `.context/productContext.md` for requirements.",
            "- **System Architecture**: Read `.context/systemPatterns.md` for tech stack.",
            "",
            "## Workflow",
            rule_bundle.rules.get("01_workflow.md", "").replace("{{SKILLS_DIR}}", ".claude/skills"),
            "",
            "## Tech Stack",
            rule_bundle.rules.get("02_stack.md", "").replace("{{SKILLS_DIR}}", ".claude/skills"), # Normalized key
            "",
            "## Output Format",
            rule_bundle.rules.get("03_output_format.md", "").replace("{{SKILLS_DIR}}", ".claude/skills"),
            "",
            "## Environment & LLM",
            rule_bundle.rules.get("00a_project_environment.md", "").replace("{{SKILLS_DIR}}", ".claude/skills"),
            rule_bundle.rules.get("00b_llm_integration.md", "").replace("{{SKILLS_DIR}}", ".claude/skills"),
        ]
        
        # Clean up empty lines or None
        claude_content = [line for line in claude_content if line is not None]
        plan.files["CLAUDE.md"] = "\n".join(claude_content)
        
        # 2. Settings (Shared)
        # Represents the Vibe-managed baseline permissions
        settings = {
            "permissions": {
                "allow": [
                    "bash", 
                    "git status", 
                    "git diff", 
                    "git log", 
                    "ls", 
                    "cat", 
                    "grep", 
                    "find"
                ]
            }
        }
        plan.files[".claude/settings.json"] = json.dumps(settings, indent=2)
        
        # 3. MCP Config
        # Standard toolset
        mcp_config = {
            "mcpServers": {
                "filesystem": { 
                    "command": "npx", 
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "."] 
                },
                "git": { 
                    "command": "npx", 
                    "args": ["-y", "@modelcontextprotocol/server-git", "."] 
                }
            }
        }
        plan.files[".claude/mcp.json"] = json.dumps(mcp_config, indent=2)
        
        
        # 4. Skills (Step C Implementation)
        skills_summary = []
        for script_name, content in rule_bundle.scripts.items():
             # For Claude, we place scripts in .claude/skills/ to keep root clean
             # They can be run via `python .claude/skills/xxx.py`
             skill_path = f".claude/skills/{script_name}"
             plan.files[skill_path] = content
             skills_summary.append(f"- **{script_name}**: (Located at `{skill_path}`)")

        # 5. Project Skills (New Standard Structure)
        for skill_name, skill_files in rule_bundle.skills.items():
            base_path = Path(".claude/skills") / skill_name
            for rel_path, content in skill_files.items():
                target_path = (base_path / rel_path).as_posix()
                plan.files[target_path] = content
            
            # Add to summary
            skills_summary.append(f"- **{skill_name}**: Located at `{base_path.as_posix()}/`")

        # Append Skills to CLAUDE.md if any
        if skills_summary:
            claude_content.append("")
            claude_content.append("## Skills / Scripts")
            claude_content.extend(skills_summary)
            # Re-join content to update file
            plan.files["CLAUDE.md"] = "\n".join(claude_content)

        # 5. .gitignore
        # Ensure local config is ignored
        plan.files[".gitignore"] = (
            "# Claude Code Local Override\n"
            ".claude/settings.local.json\n"
            ".claude/mcp.local.json\n"
        )
        
        return plan
