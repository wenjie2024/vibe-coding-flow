import os
from pathlib import Path
from .paths import PACKAGE_ROOT

class Settings:
    @staticmethod
    def resolve_config_paths():
        """Resolves config paths for LLMClient."""
        # Adjust for package structure: PACKAGE_ROOT is 'vibe/', so parent is repo root
        repo_root = PACKAGE_ROOT.parent
        
        # Using relative paths for this specific workspace setup (legacy compat)
        try:
            user_config = str((repo_root / "../my-llm-sdk/config.yaml").resolve())
            project_config = str((repo_root / "../my-llm-sdk/llm.project.yaml").resolve())
        except Exception:
             # Fallback if cannot resolve relative paths
             user_config = "config.yaml"
             project_config = "llm.project.yaml"
        
        if os.path.exists("./config.yaml"):
           user_config = "./config.yaml"
        if os.path.exists("./llm.project.yaml"):
           project_config = "./llm.project.yaml"
    
        return user_config, project_config
