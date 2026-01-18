"""
Pytest configuration and fixtures.
"""
import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
import sys

# Add package root to path
sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture
def mock_llm_client():
    """Mock LLM Client."""
    client = Mock()
    client.generate.return_value = """
|||FILE: productContext.md|||
# Test Context
## Goal
Test Goal
|||END_FILE|||
"""
    return client

@pytest.fixture
def temp_project_dir(tmp_path):
    """Temporary project directory."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    return project_dir

@pytest.fixture
def mock_template_loader():
    """Mock Template Loader."""
    loader = Mock()
    loader.load_prompt.return_value = "Test Prompt: {{user_request}}"
    loader.load_rule.return_value = "# Test Rule"
    return loader
