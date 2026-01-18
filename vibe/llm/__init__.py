"""
Vibe-CLI LLM Module.
"""
from vibe.llm.client import call_llm
from vibe.llm.parser import extract_file_content

__all__ = [
    "call_llm",
    "extract_file_content",
]
