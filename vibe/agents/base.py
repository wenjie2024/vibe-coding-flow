"""
Agent Base Classes for Vibe-CLI.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from vibe.llm.client import call_llm
from vibe.llm.parser import extract_file_content


@dataclass
class AgentResult:
    """Result from an Agent execution."""
    content: str
    filename: str
    success: bool
    raw_response: Optional[str] = None
    error: Optional[str] = None


class BaseAgent(ABC):
    """Abstract base class for all Agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the agent."""
        pass

    @property
    @abstractmethod
    def template_name(self) -> str:
        """Name of the prompt template file (e.g., 'analyst.md')."""
        pass

    @property
    @abstractmethod
    def output_filename(self) -> str:
        """Name of the output file this agent produces (e.g., 'productContext.md')."""
        pass

    @abstractmethod
    def build_prompt(self, context: dict) -> str:
        """
        Build the prompt string from template and context.
        
        Args:
            context: Dictionary containing variables like user_request, product_context, etc.
        
        Returns:
            The fully constructed prompt string.
        """
        pass

    def execute(self, context: dict) -> AgentResult:
        """
        Execute the agent's task.
        
        Args:
            context: Dictionary containing variables needed for prompt building.
        
        Returns:
            AgentResult containing the extracted content and metadata.
        """
        try:
            prompt = self.build_prompt(context)
            raw_response = call_llm(prompt, self.name)
            content = extract_file_content(raw_response, self.output_filename)

            if content:
                return AgentResult(
                    content=content,
                    filename=self.output_filename,
                    success=True,
                    raw_response=raw_response
                )
            else:
                # Fallback: use raw response if parsing fails
                return AgentResult(
                    content=raw_response,
                    filename=self.output_filename,
                    success=False,
                    raw_response=raw_response,
                    error=f"Could not parse {self.output_filename} from response"
                )
        except Exception as e:
            return AgentResult(
                content="",
                filename=self.output_filename,
                success=False,
                error=str(e)
            )
