from vibe.core.adapter_interface import BaseAdapter, RuleBundle, WritePlan
from vibe.core.adapter_registry import AdapterRegistry

@AdapterRegistry.register("antigravity")
class AntigravityAdapter(BaseAdapter):
    """
    Adapter for Google's Antigravity (Gemini) agent.
    Generates standard .agent/rules/ and a pointer-based task.md.
    """
    
    def project(self, rule_bundle: RuleBundle) -> WritePlan:
        plan = WritePlan()
        
        # 1. Standard Rules Projection
        # Map generic rule names to .agent/rules/ structure
        for rule_name, content in rule_bundle.rules.items():
            # e.g., "00_project_context.md" -> ".agent/rules/00_project_context.md"
            target_path = f".agent/rules/{rule_name}"
            plan.files[target_path] = content
            
        # 2. task.md (Pointer)
        # Antigravity uses task.md as a primary artifact. 
        # We initialize it to point to our Source of Truth.
        plan.files["task.md"] = (
            "<!-- Vibe Task Pointer -->\n"
            "# Current Task Status\n\n"
            "This project uses Vibe's unified context system.\n"
            "Please refer to and update: **[.context/activeContext.md](.context/activeContext.md)**\n\n"
            "- [ ] Initial setup verified\n"
        )
        
        # 3. Skills (Step C Implementation)
        for script_name, content in rule_bundle.scripts.items():
            skill_base = script_name.replace(".py", "")
            skill_dir = f".agent/skills/{skill_base}"
            
            # SKILL.md
            plan.files[f"{skill_dir}/SKILL.md"] = (
                "---\n"
                f"description: Skill wrapper for {skill_base}\n"
                "---\n\n"
                f"# {skill_base}\n"
                "Auto-generated skill wrapper.\n"
            )
            
            # run.py
            plan.files[f"{skill_dir}/run.py"] = content
        
        return plan
