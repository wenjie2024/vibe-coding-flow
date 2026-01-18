"""
Architect Agent - System Design.
"""
from vibe.agents.base import BaseAgent
from vibe.config.paths import PROMPTS_DIR
from vibe.utils.files import read_template


class ArchitectAgent(BaseAgent):
    """
    Architect Agent (系统架构师).
    Designs system architecture and produces systemPatterns.md.
    """

    @property
    def name(self) -> str:
        return "系统架构师 (Architect)"

    @property
    def template_name(self) -> str:
        return "architect.md"

    @property
    def output_filename(self) -> str:
        return "systemPatterns.md"

    def build_prompt(self, context: dict) -> str:
        template = read_template(self.template_name, PROMPTS_DIR)
        prompt = template.replace("{{user_request}}", context.get("user_request", ""))
        prompt = prompt.replace("{{product_context}}", context.get("product_context", ""))
        return prompt
