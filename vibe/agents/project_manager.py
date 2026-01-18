"""
Project Manager Agent - Task Planning.
"""
from vibe.agents.base import BaseAgent
from vibe.config.paths import PROMPTS_DIR
from vibe.utils.files import read_template


class ProjectManagerAgent(BaseAgent):
    """
    Project Manager Agent (项目经理).
    Plans next steps and produces activeContext.md.
    """

    @property
    def name(self) -> str:
        return "项目经理 (Project Manager)"

    @property
    def template_name(self) -> str:
        return "project_manager.md"

    @property
    def output_filename(self) -> str:
        return "activeContext.md"

    def build_prompt(self, context: dict) -> str:
        template = read_template(self.template_name, PROMPTS_DIR)
        prompt = template.replace("{{product_context}}", context.get("product_context", ""))
        prompt = prompt.replace("{{system_patterns}}", context.get("system_patterns", ""))
        return prompt
