---
description: Critical execution rules for maintaining environment consistency and valid paths.
---
# Rule 00a: Project Runtime Environment & Infrastructure

This rule is the **FOUNDATION** of this project. You must strictly adhere to these execution patterns to ensure stability across Windows and macOS/Linux.

## 0. Project Root Gate (MUST)
You MUST run commands from the project root where `.context/project_env.yaml` exists.

- macOS/Linux:
  ```bash
  test -f .context/project_env.yaml
  ```
- Windows PowerShell:
  ```powershell
  Test-Path .context/project_env.yaml
  ```

If this check fails, STOP and `cd` to the correct directory.

## 1. Source of Truth: `.context/project_env.yaml`
Before running any command, you MUST check `.context/project_env.yaml` for:
- `conda_env`: The name of the Conda environment to use.
- `sdk_path_env_var`: The environment variable name for the SDK path (e.g., `MY_LLM_SDK_PATH`).

**Constraint**: `<ENV_NAME>` MUST be exactly the value of `conda_env` from `.context/project_env.yaml`. Never guess it.

## 2. Mandatory Execution Pattern: `conda run`
**NEVER** assume an environment is active. **ALWAYS** explicitly bind the command to the environment.

- **❌ Forbidden:**
  ```bash
  python vibe.py              # Do NOT do this
  pip install -r requirements.txt # Do NOT do this
  pytest                      # Do NOT do this
  ```

- **✅ Required:**
  ```bash
  # Powershell/Bash compatible
  conda run -n <ENV_NAME> python vibe.py
  conda run -n <ENV_NAME> pip install -r requirements.txt
  conda run -n <ENV_NAME> pytest
  ```

> **Windows Powershell Tip**: If `conda run` causes quoting issues with complex arguments, use `conda run -n <ENV_NAME> --no-capture-output python script.py`.

## 3. Preflight Checks (Before Execution)
Before executing a new sequence of commands, verify your context:

0.  **Conda Availability**:
    If `conda` is not available (command not found) or `conda run` fails, STOP and ask the user to fix Conda installation/initialization.

1.  **Environment Connectivity**:
    Run:
    ```bash
    conda run -n <ENV_NAME> python -c "import sys; print(sys.executable); print(sys.prefix)"
    ```
    The command MUST be executed via `conda run -n <ENV_NAME>`. If you cannot prove the interpreter/prefix comes from this env, STOP.

2.  **SDK Availability**:
    The env var name MUST come from `sdk_path_env_var` in `.context/project_env.yaml`. Do NOT hardcode `MY_LLM_SDK_PATH`.
    Verify that this environment variable is set in your current shell/system.
    *   If not set: You cannot run the code. Ask the user to set it.
    *   If set: Ensure it points to a valid directory.

## 4. Environment Management
- If the environment does not exist, STOP and ask the user for permission to create it using `environment.yml` or `requirements.txt`.
- Do not install packages into `base` or the system Python.

---
**Enforcement**: If you cannot verify strict environment isolation, **STOP** and ask the user for help.
