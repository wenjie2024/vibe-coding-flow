import sys
import os
import yaml
from pathlib import Path

# Force UTF-8 output for Windows Console to support emojis
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass
    # Also ensure Python writes UTF-8 to the buffer
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_check(name):
    print(f"\n{CYAN}{BOLD}🔍 {name}{RESET}")

def success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def failure(msg):
    print(f"{RED}❌ {msg}{RESET}")

def warning(msg):
    print(f"{YELLOW}⚠️ {msg}{RESET}")

def check_conda_env():
    """Check 1: Verify we are running in the correct Conda environment."""
    print_check("Check 1: Conda Environment")
    
    # Read expected env name from project_env.yaml
    expected_env = None
    try:
        with open(".context/project_env.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            expected_env = config.get("conda_env")
    except Exception as e:
        failure(f"Failed to read .context/project_env.yaml: {e}")
        return False

    current_prefix = sys.prefix.replace("\\", "/") # Normalize for comparison
    
    # Heuristic check: typical conda env path contains the env name
    if expected_env and expected_env in current_prefix:
        success(f"Running in '{expected_env}' ({sys.prefix})")
        return True
    else:
        # Fallback: maybe the active environment variable is set
        active_env = os.environ.get("CONDA_DEFAULT_ENV")
        if active_env == expected_env:
             success(f"Active Conda Env: '{active_env}'")
             return True
             
        failure(f"Environment Mismatch!")
        print(f"   Expected to contain: '{expected_env}'")
        print(f"   Actual sys.prefix:   '{sys.prefix}'")
        print(f"   Actual CONDA_DEFAULT_ENV: '{active_env}'")
        print(f"   👉 Tip: Run `conda activate {expected_env}`")
        return False

def check_sdk_install():
    """Check 2: Verify my-llm-sdk is installed and accessible."""
    print_check("Check 2: SDK Installation")
    try:
        import my_llm_sdk
        success(f"SDK Found: {my_llm_sdk.__file__}")
        return True
    except ImportError:
        failure("my-llm-sdk not found!")
        print("   👉 Tip: Run `pip install git+https://github.com/NoneSeniorEngineer/my-llm-sdk.git`")
        return False

def check_user_config():
    """Check 3: Verify user configuration exists."""
    print_check("Check 3: SDK Configuration")
    
    # Check 1: Local config (in project root)
    local_config = Path.cwd() / "config.yaml"
    if local_config.exists():
        success(f"Config found (Local): {local_config}")
        return True

    # Check 2: Global config (in home dir)
    home = Path.home()
    global_config = home / ".my-llm-sdk" / "config.yaml"
    
    if global_config.exists():
        success(f"Config found (Global): {global_config}")
        return True
    
    failure(f"SDK Config not found (Run 'init' first)")
    print(f"   Checked local:  {local_config}")
    print(f"   Checked global: {global_config}")
    print("   👉 Tip: Run `python -m my_llm_sdk.cli init` to create it.")
    return False

def check_llm_connectivity():
    """Check 4: Test LLM Connectivity (Optional)."""
    print_check("Check 4: LLM Connectivity (Ping)")
    
    try:
        from my_llm_sdk.client import LLMClient
        client = LLMClient()
        
        # 'gemini-2.5-flash' or 'default' alias
        model = "gemini-2.5-flash" 
        print(f"   Sending ping to model: {YELLOW}{model}{RESET}...")
        
        response_text = ""
        stream = client.stream("Hello, say 'OK' if you can hear me.", model_alias=model)
        for chunk in stream:
            if hasattr(chunk, 'content'):
                 response_text += chunk.content
            else:
                 response_text += str(chunk)
                 
        success("Connectivity Success!")
        print(f"   Response: {response_text.strip()}")
        return True
        
    except Exception as e:
        failure(f"LLM Connection Failed: {e}")
        print("   👉 Tip: Check your API Keys or Network Connection.")
        return False

if __name__ == "__main__":
    print(f"{BOLD}🚀 Project Preflight Check{RESET}")
    
    checks = [
        check_conda_env(),
        check_sdk_install(),
        check_user_config(),
        # We run connectivity check last
    ]
    
    if all(checks[:3]):
        # Only run LLM check if infra is okay
        check_llm_connectivity()
    
    print("\nPreflight complete.")
