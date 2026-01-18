"""
Unit tests for Agents.
"""
import pytest
from unittest.mock import patch, Mock
from vibe.agents.analyst import AnalystAgent
from vibe.agents.base import AgentResult

class TestAnalystAgent:
    def test_initialization(self):
        agent = AnalystAgent()
        assert agent.name == "需求分析师 (Analyst)"
        assert agent.template_name == "analyst.md"
        assert agent.output_filename == "productContext.md"

    @patch("vibe.agents.base.call_llm")
    @patch("vibe.agents.analyst.read_template")
    def test_execute_success(self, mock_read, mock_call_llm):
        # Setup mocks
        mock_read.return_value = "Template {{user_request}}"
        mock_call_llm.return_value = """
|||FILE: productContext.md|||
# Content
|||END_FILE|||
"""
        
        agent = AnalystAgent()
        result = agent.execute({"user_request": "test"})
        
        assert isinstance(result, AgentResult)
        assert result.success is True
        assert result.content == "# Content"
        assert result.filename == "productContext.md"

    @patch("vibe.agents.base.call_llm")
    @patch("vibe.agents.analyst.read_template")
    def test_execute_parsing_failure(self, mock_read, mock_call_llm):
        # Setup mocks
        mock_read.return_value = "Template"
        mock_call_llm.return_value = "Raw content without markers"
        
        agent = AnalystAgent()
        result = agent.execute({"user_request": "test"})
        
        # Should fallback to raw content but marked as success=False in strict mode,
        # or handle based on logic. Let's check current BaseAgent logic.
        # BaseAgent returns success=False if parsing fails.
        
        assert result.success is False
        assert result.content == "Raw content without markers"
        assert "Could not parse" in result.error
