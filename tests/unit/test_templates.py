"""
Unit tests for TemplateLoader.
"""
import pytest
from pathlib import Path
from vibe.templates.loader import TemplateLoader

def test_loader_init(tmp_path):
    loader = TemplateLoader(tmp_path)
    assert loader.templates_dir == tmp_path

def test_load_success(tmp_path):
    # Setup dummy template
    (tmp_path / "test.md").write_text("content", encoding="utf-8")
    
    loader = TemplateLoader(tmp_path)
    content = loader.load("test.md")
    assert content == "content"

def test_load_subfolder(tmp_path):
    # Setup dummy subfolder
    sub = tmp_path / "prompts"
    sub.mkdir()
    (sub / "test.md").write_text("prompt content", encoding="utf-8")
    
    loader = TemplateLoader(tmp_path)
    content = loader.load("test.md", "prompts")
    assert content == "prompt content"
    
    # Helper method
    content2 = loader.load_prompt("test.md")
    assert content2 == "prompt content"

def test_load_not_found(tmp_path):
    loader = TemplateLoader(tmp_path)
    with pytest.raises(FileNotFoundError):
        loader.load("nonexistent.md")

def test_render():
    loader = TemplateLoader(Path("."))
    template = "Hello {{name}}!"
    rendered = loader.render(template, name="World")
    assert rendered == "Hello World!"
