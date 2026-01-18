"""
Pipeline Orchestrator for Vibe-CLI.
"""
from dataclasses import dataclass
from typing import List, Optional, Callable, Any
from vibe.agents.base import BaseAgent, AgentResult


@dataclass
class PipelineStage:
    """Represents a single stage in the pipeline."""
    agent: BaseAgent
    on_complete: Optional[Callable[[AgentResult], None]] = None
    interactive: bool = False


class Pipeline:
    """
    Four-role pipeline orchestrator.
    Executes agents in sequence, passing context between stages.
    """

    def __init__(self, stages: List[PipelineStage]):
        """
        Initialize the pipeline with stages.
        
        Args:
            stages: List of PipelineStage objects defining the execution order.
        """
        self.stages = stages
        self.results: List[AgentResult] = []

    def run(
        self,
        initial_context: dict,
        interactive_callback: Optional[Callable[[AgentResult], str]] = None
    ) -> List[AgentResult]:
        """
        Execute the pipeline.
        
        Args:
            initial_context: Starting context dictionary.
            interactive_callback: Optional callback for interactive stages.
                                  Called with AgentResult, should return updated content.
        
        Returns:
            List of AgentResult objects from all stages.
        """
        context = initial_context.copy()
        self.results = []

        for stage in self.stages:
            result = stage.agent.execute(context)
            self.results.append(result)

            # Update context for next stage
            # Use output filename (without .md) as key
            context_key = stage.agent.output_filename.replace(".md", "")
            context[context_key] = result.content
            
            # Also store with common names for compatibility
            if stage.agent.output_filename == "productContext.md":
                context["product_context"] = result.content
            elif stage.agent.output_filename == "systemPatterns.md":
                context["system_patterns"] = result.content

            # Execute completion callback
            if stage.on_complete:
                stage.on_complete(result)

            # Handle interactive mode
            if stage.interactive and interactive_callback:
                updated_content = interactive_callback(result)
                result.content = updated_content
                context[context_key] = updated_content
                if stage.agent.output_filename == "productContext.md":
                    context["product_context"] = updated_content
                elif stage.agent.output_filename == "systemPatterns.md":
                    context["system_patterns"] = updated_content

        return self.results

    def get_result(self, filename: str) -> Optional[AgentResult]:
        """
        Get a specific result by output filename.
        
        Args:
            filename: The output filename to look for.
        
        Returns:
            The AgentResult if found, None otherwise.
        """
        for result in self.results:
            if result.filename == filename:
                return result
        return None
