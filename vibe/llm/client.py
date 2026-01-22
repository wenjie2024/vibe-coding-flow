"""
LLM Client wrapper for Vibe-CLI.
"""
import sys
from vibe.cli.console import console
from vibe.config.settings import Settings

# Try to import my_llm_sdk, handle failure gracefully
_LLMClient = None

def _ensure_llm_client():
    global _LLMClient
    if _LLMClient is not None:
        return

    try:
        from my_llm_sdk.client import LLMClient as _Client
        _LLMClient = _Client
    except ImportError as e1:
        try:
            import os
            from vibe.config.paths import PACKAGE_ROOT
            repo_root = PACKAGE_ROOT.parent
            sys.path.append(os.path.abspath(str(repo_root / "../my-llm-sdk")))
            from src.client import LLMClient as _Client
            _LLMClient = _Client
        except ImportError as e2:
            console.print("[bold red]Error:[/bold red] my_llm_sdk not found.")
            console.print(f"Import Error 1: {e1}")
            console.print(f"Import Error 2: {e2}")
            console.print("Tip: Run `pip install my-llm-sdk`")
            sys.exit(1)


def call_llm(prompt_text: str, step_name: str) -> str:
    """
    Calls the LLM with the given prompt.
    
    Args:
        prompt_text: The prompt to send to the LLM.
        step_name: A human-readable name for logging purposes.
    
    Returns:
        The LLM response as a string.
    """
    _ensure_llm_client()
    console.print(f"[yellow]⏳ {step_name} is thinking...[/yellow]")
    user_conf, proj_conf = Settings.resolve_config_paths()
    try:
        client = _LLMClient(user_config_path=user_conf, project_config_path=proj_conf)
        response = client.generate(prompt=prompt_text)
        return response
    except Exception as e:
        console.print(f"[bold red]❌ LLM Error:[/bold red] {e}")
        sys.exit(1)
