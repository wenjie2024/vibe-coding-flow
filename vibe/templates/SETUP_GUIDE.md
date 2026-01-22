# Project Setup Guide

This guide will help you set up the environment required to run this project, ensuring compliance with **Rule 00a** and **Rule 00b**.

## 1. Prerequisites
- **Miniconda** or **Anaconda** installed.
- **Miniconda** or **Anaconda** installed.

## 2. Infrastructure Setup (One-Time / Per Project)

We use **Conda Environment Variables** to safely locate the SDK without modifying your system settings.

### Step 2.1: Create & Activate Environment
Open your terminal (Powershell recommended on Windows) and run:

```bash
```bash
# Create environment (Replace <your_conda_env> with your desired name)
conda create -n <your_conda_env> python=3.10 -y

# Activate it
conda activate <your_conda_env>
```

> **⚠️ CRITICAL**: The `project_env.yaml` is generated with `conda_env: {{project_name}}` by default.
> If you chose a different name (e.g. `my_env`), you **MUST** edit `.context/project_env.yaml` to match!

### Step 2.2: Install SDK & Dependencies
Since the SDK is not yet on PyPI, install it directly from GitHub:

```bash
# 1. Install my-llm-sdk
pip install my-llm-sdk

# 2. Install other project dependencies
# pip install -r requirements.txt
```

### Step 2.4: SDK Initialization
Initialize the SDK configuration if you haven't done so globally.

```bash
python -m my_llm_sdk.cli init
```

**What to expect:**
- This command is **interactive**.
- You will be asked to configure **Providers** (e.g., OpenAI, Google, Azure).
- Have your **API Keys** and **Endpoint URLs** ready.
- It will create a `config.yaml` in your user home directory (e.g. `~/.my-llm-sdk/config.yaml`).

## 3. Configuration Verification

### Step 3.1: Check `.context/project_env.yaml`
Ensure this file exists in the project root and matches your setup:

```yaml
conda_env: {{project_name}}           # Must match your conda env name
```

## 4. Preflight Check (Self-Test)

Run this command to verify everything is working. If this passes, you are ready to code!

```bash
# Verify everything in one go:
conda run -n <your_conda_env> python preflight.py
```

✅ **Success Condition**:
- All checks pass with [green]✅[/green]
- LLM Connectivity confirms "Connectivity Success!"
