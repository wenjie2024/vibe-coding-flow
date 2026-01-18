"""
Integration tests for CLI Interactive Mode.
"""
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from vibe.cli.app import app
from pathlib import Path

runner = CliRunner()

@pytest.fixture
def mock_llm_utils():
    with patch("vibe.cli.app.call_llm") as mock_call, \
         patch("vibe.cli.app.extract_file_content") as mock_extract:
        
        # Setup default mock responses
        mock_call.return_value = "LLM Response"
        
        def extract_side_effect(response, filename):
            if filename == "productContext.md":
                return "# Product Context\nTest Content"
            if filename == "systemPatterns.md":
                return "# System Patterns\nStack: Python FastAPI"
            if filename == "activeContext.md":
                return "# Active Context\nPlan"
            return ""
            
        mock_extract.side_effect = extract_side_effect
        yield mock_call, mock_extract

def test_create_interactive_happy_path(tmp_path, mock_llm_utils):
    """
    Test 'create --interactive' with standard 'y' confirmations.
    Simulates:
    1. Confirm to continue after Analyst phase (interactive pause).
    2. Confirm 'y' for Tech Stack review.
    """
    project_dir = tmp_path / "interactive_project"
    
    # Input sequence:
    # 1. "y" (Enter) for "准备好继续了吗？" (Typer confirm)
    # 2. "y" (Enter) for "是否接受此技术栈方案？" (Rich Prompt)
    user_input = "y\ny\n"
    
    result = runner.invoke(app, ["create", str(project_dir), "--prompt", "test app", "--interactive"], input=user_input)
    
    # Debug output if fails
    print(result.stdout)
    
    assert result.exit_code == 0
    assert "交互模式 (Interactive Mode)" in result.stdout
    assert "技术栈评审 (Vibe Review)" in result.stdout
    assert "技术栈方案已确认" in result.stdout
    
    # Verify files created
    assert (project_dir / ".context/productContext.md").exists()
    assert (project_dir / ".context/systemPatterns.md").exists()

def test_create_interactive_regen(tmp_path, mock_llm_utils):
    """
    Test 'create' with 'regen' option in Tech Stack review.
    Simulates:
    1. Confirm to continue after Analyst phase.
    2. Input 'regen' for Tech Stack review.
    3. Input 'Use Django' for extra instruction.
    """
    project_dir = tmp_path / "regen_project"
    
    # Input sequence:
    # 1. "y" for pause
    # 2. "regen" for review choice
    # 3. "Use Django" for extra instruction
    user_input = "y\nregen\nUse Django\n"
    
    result = runner.invoke(app, ["create", str(project_dir), "--prompt", "test app", "--interactive"], input=user_input)
    
    assert result.exit_code == 0
    assert "正在根据新指令重新生成架构" in result.stdout
    assert "架构已重新生成" in result.stdout
