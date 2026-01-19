from vibe.core.adapter_interface import BaseAdapter, RuleBundle, WritePlan
from vibe.core.adapter_registry import AdapterRegistry

@AdapterRegistry.register("cursor")
class CursorAdapter(BaseAdapter):
    """
    Adapter for Cursor IDE.
    Generates .cursor/rules/*.mdc files for granular rule application.
    Also supports legacy .cursorrules via optional flag check? 
    (Flags are not passed to project() yet, so strictly MDC for now)
    """
    
    def project(self, rule_bundle: RuleBundle) -> WritePlan:
        plan = WritePlan()
        
        # 1. Core Rule (.mdc)
        # We put general context here.
        # Cursor suggests globs.
        
        core_mdc = (
            "---\n"
            "description: Core Project Context & Workflow\n"
            "globs: *\n"
            "---\n\n"
            "# Core Context\n\n"
            "## 1. Project Goal\n"
            "Read `.context/productContext.md` for requirements.\n\n"
            "## 2. Architecture\n"
            "Read `.context/systemPatterns.md` for architectural patterns.\n\n"
            "## 3. Workflow\n"
            f"{rule_bundle.rules.get('01_workflow.md', '')}\n"
        )
        plan.files[".cursor/rules/00_core.mdc"] = core_mdc
        
        # 2. Tech Stack Rule (.mdc)
        # We try to infer glob from the stack rule if possible, or just default to *
        # For now, simplistic approach:
        stack_content = rule_bundle.rules.get("02_stack.md", "")
        stack_mdc = (
            "---\n"
            "description: Tech Stack Standards\n"
            "globs: *.py, *.js, *.ts, *.jsx, *.tsx, *.go, *.rs\n"
            "---\n\n"
            f"{stack_content}\n"
        )
        plan.files[".cursor/rules/02_stack.mdc"] = stack_mdc

        # 3. Project Skills
        # We place them in .cursor/skills/ and add a rule telling Cursor about them
        skills_summary = []
        for skill_name, skill_files in rule_bundle.skills.items():
            base_path = Path(".cursor/skills") / skill_name
            for rel_path, content in skill_files.items():
                target_path = (base_path / rel_path).as_posix()
                plan.files[target_path] = content
            
            skills_summary.append(f"- **{skill_name}**: Located at `{base_path.as_posix()}/SKILL.md`")
            
        if skills_summary:
            skills_mdc = (
                "---\n"
                "description: Available Project Skills & Tools\n"
                "globs: *\n"
                "---\n\n"
                "# Project Skills\n\n"
                "You have access to the following specialized skills. "
                "Read the `SKILL.md` in the respective directories for usage instructions.\n\n"
                + "\n".join(skills_summary)
            )
            plan.files[".cursor/rules/90_skills.mdc"] = skills_mdc

        return plan
