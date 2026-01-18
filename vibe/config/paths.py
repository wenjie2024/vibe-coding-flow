from pathlib import Path

# Package root (vibe/)
PACKAGE_ROOT = Path(__file__).parent.parent

# Templates directories
TEMPLATES_DIR = PACKAGE_ROOT / "templates"
PROMPTS_DIR = TEMPLATES_DIR / "prompts"
RULES_DIR = TEMPLATES_DIR / "rules"
SCRIPTS_DIR = TEMPLATES_DIR / "scripts"
