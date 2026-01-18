"""
LLM Response Parser for Vibe-CLI.
"""
import re
from typing import Optional


def extract_file_content(response: str, filename: str) -> Optional[str]:
    """
    Extracts content between |||FILE: filename||| and |||END_FILE|||.
    
    Args:
        response: The raw LLM response string.
        filename: The filename to extract (e.g., "productContext.md").
    
    Returns:
        The extracted content, or None if not found.
    """
    pattern = re.compile(
        rf"\|\|\|FILE: {re.escape(filename)}\|\|\|(.*?)\|\|\|END_FILE\|\|\|",
        re.DOTALL
    )
    match = pattern.search(response)
    if match:
        return match.group(1).strip()
    return None
