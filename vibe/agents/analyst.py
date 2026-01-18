"""
Analyst Agent - Requirement Analysis.
"""
from vibe.agents.base import BaseAgent
from vibe.config.paths import PROMPTS_DIR
from vibe.utils.files import read_template


class AnalystAgent(BaseAgent):
    """
    Analyst Agent (需求分析师).
    Analyzes user requirements and produces productContext.md.
    """

    @property
    def name(self) -> str:
        return "需求分析师 (Analyst)"

    @property
    def template_name(self) -> str:
        return "analyst.md"

    @property
    def output_filename(self) -> str:
        return "productContext.md"

    def build_prompt(self, context: dict) -> str:
        template = read_template(self.template_name, PROMPTS_DIR)
        return template.replace("{{user_request}}", context.get("user_request", ""))
