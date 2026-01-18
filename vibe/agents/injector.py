"""
Injector (DevOps) Agent - Environment Setup.
This agent doesn't use LLM, it selects and injects rule templates.
"""
from pathlib import Path
from typing import Dict, Optional
from vibe.cli.console import console
from vibe.config.paths import RULES_DIR, TEMPLATES_DIR
from vibe.utils.files import read_template


class InjectorAgent:
    """
    Injector Agent (运维专家).
    Selects appropriate tech stack rules based on system patterns.
    Does not call LLM - purely rule-based.
    """

    # Mapping of keywords to rule template files
    STACK_RULES_MAPPING = {
        "django": "02_stack_python_django.md",
        "node": "02_stack_nodejs_express.md",
        "express": "02_stack_nodejs_express.md",
        "react": "02_stack_react_vite.md",
        "vite": "02_stack_react_vite.md",
        "go": "02_stack_go_gin.md",
        "gin": "02_stack_go_gin.md",
        "telegram": "02_stack_telegram_bot.md",
        "bot": "02_stack_telegram_bot.md",
        "postgres": "02_stack_postgresql.md",
    }
    
    DEFAULT_STACK_RULE = "02_stack_python_fastapi.md"

    @property
    def name(self) -> str:
        return "运维专家 (Injector)"

    def detect_stack_rule(self, system_patterns: str) -> str:
        """
        Detects the appropriate stack rule based on keywords in system_patterns.
        
        Args:
            system_patterns: The content of systemPatterns.md.
        
        Returns:
            The filename of the selected stack rule template.
        """
        patterns_lower = system_patterns.lower()
        
        for keyword, template_name in self.STACK_RULES_MAPPING.items():
            if keyword in patterns_lower:
                return template_name
        
        return self.DEFAULT_STACK_RULE

    def load_rules(self, system_patterns: str) -> Dict[str, str]:
        """
        Loads all rule templates based on the detected stack.
        
        Args:
            system_patterns: The content of systemPatterns.md.
        
        Returns:
            Dictionary mapping rule filename to content.
        """
        rules = {}
        
        # Fixed rules (always included)
        fixed_rules = [
            "00a_project_environment.md",
            "00b_llm_integration.md",
            "01_workflow_plan_first.md",
            "03_output_format.md",
        ]
        
        for rule_name in fixed_rules:
            try:
                rules[rule_name] = read_template(rule_name, RULES_DIR)
            except SystemExit:
                console.print(f"[yellow]⚠️  Rule {rule_name} not found, skipping.[/yellow]")
        
        # Dynamic stack rule
        stack_rule_name = self.detect_stack_rule(system_patterns)
        try:
            rules[stack_rule_name] = read_template(stack_rule_name, RULES_DIR)
            console.print(f"[dim]ℹ️  已选择规则集: {stack_rule_name}[/dim]")
        except SystemExit:
            console.print(f"[yellow]⚠️  Stack rule {stack_rule_name} not found, using default.[/yellow]")
            rules[self.DEFAULT_STACK_RULE] = read_template(self.DEFAULT_STACK_RULE, RULES_DIR)
        
        return rules

    def load_setup_templates(self, project_name: str) -> Dict[str, str]:
        """
        Loads setup guide templates with project name substitution.
        
        Args:
            project_name: The name of the project.
        
        Returns:
            Dictionary mapping template filename to rendered content.
        """
        templates = {}
        
        template_files = [
            ("SETUP_GUIDE.md", True),      # (filename, needs_substitution)
            ("SETUP_GUIDE_ZH.md", True),
            ("preflight.py", False),
        ]
        
        for filename, needs_sub in template_files:
            try:
                content = read_template(filename, TEMPLATES_DIR)
                if needs_sub:
                    content = content.replace("{{project_name}}", project_name)
                templates[filename] = content
            except SystemExit:
                console.print(f"[yellow]⚠️  Template {filename} not found.[/yellow]")
        
        return templates
