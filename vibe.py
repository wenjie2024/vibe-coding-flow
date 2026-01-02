#!/usr/bin/env python3
import os
import sys
import typer
import re
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()
app = typer.Typer(help="Vibe-CLI: Intelligent Project Bootstrapper")

# Try to import my_llm_sdk, handle failure gracefully
try:
    # Priority 1: Try importing from installed package (e.g. pip install -e .)
    from my_llm_sdk.client import LLMClient
except ImportError as e1:
    try:
        # Priority 2: Try importing from src (legacy/local dev)
        # Add parent directory to path to find src if running from repo root
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../my-llm-sdk")))
        from src.client import LLMClient
    except ImportError as e2:
        console.print("[bold red]Error:[/bold red] my_llm_sdk not found. Please ensure it is installed.")
        console.print(f"Debug Info: Checked sys.path: {sys.path}")
        console.print(f"Import Error 1: {e1}")
        console.print(f"Import Error 2: {e2}")
        console.print("Tip: Run `pip install git+https://github.com/NoneSeniorEngineer/my-llm-sdk.git` or activate the correct conda environment (doc).")
        sys.exit(1)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
PROMPTS_DIR = os.path.join(TEMPLATES_DIR, "prompts")
RULES_DIR = os.path.join(TEMPLATES_DIR, "rules")

def resolve_config_paths():
    """Resolves config paths for LLMClient."""
    # Using relative paths for this specific workspace setup
    user_config = os.path.abspath(os.path.join(BASE_DIR, "../my-llm-sdk/config.yaml"))
    project_config = os.path.abspath(os.path.join(BASE_DIR, "../my-llm-sdk/llm.project.yaml"))
    
    if os.path.exists("./config.yaml"):
       user_config = "./config.yaml"
    if os.path.exists("./llm.project.yaml"):
       project_config = "./llm.project.yaml"

    return user_config, project_config

def read_template(filename: str, folder: str) -> str:
    path = os.path.join(folder, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Template not found: {path}")
        sys.exit(1)

def call_llm(prompt_text: str, step_name: str) -> str:
    console.print(f"[yellow]⏳ {step_name} is thinking...[/yellow]")
    user_conf, proj_conf = resolve_config_paths()
    try:
        client = LLMClient(user_config_path=user_conf, project_config_path=proj_conf)
        response = client.generate(prompt=prompt_text)
        return response
    except Exception as e:
        console.print(f"[bold red]❌ LLM Error:[/bold red] {e}")
        sys.exit(1)

def extract_file_content(response: str, filename: str) -> str:
    """Extracts content between |||FILE: filename||| and |||END_FILE|||"""
    pattern = re.compile(rf"\|\|\|FILE: {re.escape(filename)}\|\|\|(.*?)\|\|\|END_FILE\|\|\|", re.DOTALL)
    match = pattern.search(response)
    if match:
        return match.group(1).strip()
    return ""

@app.command()
def setup():
    """
    Placeholder for setup command.
    """
    console.print("[green]Setup command placeholder[/green]")

@app.command()
def create(
    project_path: str = typer.Argument(..., help="Path to the new project (e.g., 'my-app' or '../my-app')"),
    prompt: str = typer.Option(None, help="一句话需求描述"),
    promptfile: str = typer.Option(None, "--promptfile", help="从文件读取详细需求"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="启用交互模式以手动完善需求"),
):
    """
    Starts a new AI-Ready project from a prompt.
    """
    # Resolve path and name
    project_dir = Path(project_path).resolve()
    project_name = project_dir.name
    
    # --- Input Validation & Resolution ---
    user_request = None
    
    if promptfile:
        promptfile_path = Path(promptfile)
        if promptfile_path.exists():
            # Read from file
            user_request = promptfile_path.read_text(encoding="utf-8")
            console.print(f"[dim]📄 已从文件读取需求: {promptfile}[/dim]")
        else:
            # Auto-generate template
            promptfile_path.parent.mkdir(parents=True, exist_ok=True)
            template_content = read_template("REQUIREMENTS_TEMPLATE.md", TEMPLATES_DIR)
            with open(promptfile_path, "w", encoding="utf-8") as f:
                f.write(template_content)
            console.print(Panel(
                f"[bold yellow]📝 已生成需求模板：{promptfile}[/bold yellow]\n\n"
                f"请填写模板后重新运行以下命令：\n"
                f"[bold cyan]python vibe.py create {project_path} --promptfile {promptfile}[/bold cyan]",
                title="请先填写需求模板"
            ))
            raise typer.Exit(code=0)
    
    if prompt:
        if user_request:
            # Both provided: append prompt as summary
            user_request = f"# 摘要\n{prompt}\n\n---\n\n{user_request}"
        else:
            user_request = prompt
    
    if not user_request:
        console.print("[bold red]错误：[/bold red]请提供 --prompt 或 --promptfile 参数。")
        console.print("[dim]示例：python vibe.py create my-project --prompt \"你的想法\"[/dim]")
        console.print("[dim]或者：python vibe.py create my-project --promptfile requirements.md[/dim]")
        raise typer.Exit(code=1)
    
    console.print(Panel.fit(f"[bold blue]Welcome to Vibe-CLI 2.0[/bold blue]\nInitializing project: [green]{project_name}[/green]\nLocation: [dim]{project_dir}[/dim]"))

    if project_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Directory {project_dir} already exists.")
        raise typer.Exit(code=1)

    # --- Step 1: Analyst Agent ---
    console.print("\n[bold cyan]🤖 需求分析师 (Analyst):[/bold cyan] 正在分析需求...")
    analyst_template = read_template("analyst.md", PROMPTS_DIR)
    analyst_prompt = analyst_template.replace("{{user_request}}", user_request)
    
    analyst_response = call_llm(analyst_prompt, "需求分析师")
    product_context = extract_file_content(analyst_response, "productContext.md")
    
    if not product_context:
        # Fallback if parsing fails, just use the raw response (simplified for POC)
        console.print("[yellow]⚠️  无法严格解析 productContext.md，使用原始回复作为后备[/yellow]")
        product_context = analyst_response

    # Intermediate Save for Interactive Mode
    context_dir = project_dir / ".context"
    os.makedirs(context_dir, exist_ok=True)
    product_context_file = context_dir / "productContext.md"
    
    # We must write it now so user can edit it
    with open(product_context_file, "w", encoding="utf-8") as f:
        f.write(product_context)

    console.print("[green]✅ 需求分析完成。[/green]")

    # --- Step 1.5: Interactive Refinement ---
    if interactive:
        console.print(Panel(f"[bold yellow]⏸️  交互模式 (Interactive Mode)[/bold yellow]\n\n请编辑文件 [bold]{product_context_file}[/bold] 以完善需求。\n特别是回答 `❓ 待确认事项` 章节的问题。\n保存文件后，请按 [bold]回车键[/bold] 继续。"))
        typer.confirm("准备好继续了吗？", default=True)
        
        # Reload content
        console.print("[dim]🔄 正在重新加载 productContext.md...[/dim]")
        product_context = product_context_file.read_text(encoding="utf-8")
        console.print("[green]✅ 上下文已更新。[/green]")

    # --- Step 2: Architect Agent ---
    console.print("\n[bold magenta]🤖 系统架构师 (Architect):[/bold magenta] 正在设计架构...")
    architect_template = read_template("architect.md", PROMPTS_DIR)
    architect_prompt = architect_template.replace("{{user_request}}", prompt).replace("{{product_context}}", product_context)
    
    architect_response = call_llm(architect_prompt, "系统架构师")
    system_patterns = extract_file_content(architect_response, "systemPatterns.md")

    if not system_patterns:
        console.print("[yellow]⚠️  无法严格解析 systemPatterns.md，使用原始回复作为后备[/yellow]")
        system_patterns = architect_response
        
    console.print("[green]✅ 架构设计完成。[/green]")

    # --- Step 2.5: Interactive Tech Stack Review (Vibe Review) ---
    # Write systemPatterns.md early for user to review/edit
    system_patterns_file = context_dir / "systemPatterns.md"
    with open(system_patterns_file, "w", encoding="utf-8") as f:
        f.write(system_patterns)
    
    # Extract and display proposed tech stack summary
    console.print(Panel(
        f"[bold yellow]📋 技术栈评审 (Vibe Review)[/bold yellow]\n\n"
        f"架构方案已生成，请查看: [bold]{system_patterns_file}[/bold]\n\n"
        f"[dim]文件已保存，您可以：\n"
        f"  • 直接按回车接受当前方案\n"
        f"  • 输入 'edit' 打开文件手动修改后继续\n"
        f"  • 输入 'regen' 重新生成（需提供额外指令）[/dim]",
        title="[bold]Tech Stack Decision[/bold]"
    ))
    
    review_choice = Prompt.ask(
        "❓ 是否接受此技术栈方案？",
        choices=["y", "edit", "regen"],
        default="y"
    )
    
    if review_choice == "edit":
        console.print(f"[dim]请编辑文件: {system_patterns_file}[/dim]")
        console.print("[dim]保存后按回车继续...[/dim]")
        typer.confirm("编辑完成了吗？", default=True)
        # Reload content after user edit
        system_patterns = system_patterns_file.read_text(encoding="utf-8")
        console.print("[green]✅ 已加载您的修改。[/green]")
    elif review_choice == "regen":
        extra_instruction = Prompt.ask("请输入额外的架构指令 (如：'必须使用 MySQL')")
        console.print("[yellow]🔄 正在根据新指令重新生成架构...[/yellow]")
        architect_prompt_v2 = architect_prompt + f"\n\n# 用户追加指令\n{extra_instruction}"
        architect_response = call_llm(architect_prompt_v2, "系统架构师 (重新生成)")
        system_patterns = extract_file_content(architect_response, "systemPatterns.md")
        if not system_patterns:
            system_patterns = architect_response
        # Save regenerated version
        with open(system_patterns_file, "w", encoding="utf-8") as f:
            f.write(system_patterns)
        console.print("[green]✅ 架构已重新生成。[/green]")
    else:
        console.print("[green]✅ 技术栈方案已确认。[/green]")

    # --- Step 3: Injector (DevOps) ---
    console.print("\n[bold orange3]🤖 运维专家 (Injector):[/bold orange3] 正在准备开发环境...")
    
    # Define rules content
    # 00a Runtime Check
    rule_00a_content = read_template("00a_project_environment.md", RULES_DIR)
    # 00b LLM Rules
    rule_00b_content = read_template("00b_llm_integration.md", RULES_DIR)

    # 01 Workflow
    rule_01_content = read_template("01_workflow_plan_first.md", RULES_DIR)
    
    # 02 Stack (Dynamic Selection)
    rule_02_template_name = "02_stack_python_fastapi.md"  # Default
    
    # Simple heuristic to detect stack from systemPatterns
    sys_patterns_lower = system_patterns.lower()
    
    if "django" in sys_patterns_lower:
        rule_02_template_name = "02_stack_python_django.md"
    elif "node" in sys_patterns_lower or "express" in sys_patterns_lower:
        rule_02_template_name = "02_stack_nodejs_express.md"
    elif "react" in sys_patterns_lower or "vite" in sys_patterns_lower:
        rule_02_template_name = "02_stack_react_vite.md"
    elif "go" in sys_patterns_lower or "gin" in sys_patterns_lower:
        rule_02_template_name = "02_stack_go_gin.md"
    elif "telegram" in sys_patterns_lower or "bot" in sys_patterns_lower:
        rule_02_template_name = "02_stack_telegram_bot.md"
    elif "postgres" in sys_patterns_lower:
        rule_02_template_name = "02_stack_postgresql.md"
    # Add more heuristics as needed
    
    try:
        rule_02_content = read_template(rule_02_template_name, RULES_DIR)
    except SystemExit:
        # Fallback if specific template not found
        console.print(f"[yellow]⚠️  Template {rule_02_template_name} not found, using default FastAPI.[/yellow]")
        rule_02_template_name = "02_stack_python_fastapi.md"
        rule_02_content = read_template(rule_02_template_name, RULES_DIR)

    # 03 Output
    rule_03_content = read_template("03_output_format.md", RULES_DIR)
    
    # Setup Guide
    setup_guide_content = read_template("SETUP_GUIDE.md", TEMPLATES_DIR)
    setup_guide_zh_content = read_template("SETUP_GUIDE_ZH.md", TEMPLATES_DIR)
    preflight_content = read_template("preflight.py", TEMPLATES_DIR)
    
    console.print(f"[dim]ℹ️  已选择规则集: {rule_02_template_name}[/dim]")

    # --- Step 4: Scaffolding ---
    console.print(f"\n[bold white]🔨 正在初始化项目 {project_name}...[/bold white]")
    
    os.makedirs(project_dir, exist_ok=True)
    context_dir = project_dir / ".context"
    os.makedirs(context_dir, exist_ok=True)
    
    # New: Antigravity Rules Directory
    rules_dir = project_dir / ".agent" / "rules"
    os.makedirs(rules_dir, exist_ok=True)
    
    # Write artifacts
    with open(context_dir / "productContext.md", "w", encoding="utf-8") as f:
        f.write(product_context)
        
    # --- Step 4.5: Inject Critical Rules into systemPatterns.md ---
    # To force the Agent to respect Rule 00a, we append it directly to the System Prompt level context.
    critical_rules_section = f"""
## 🛡️ CRITICAL AGENT RULES (MUST FOLLOW)
1. **Mandatory Execution Pattern**: ALL commands must be run via `conda run -n {project_name} ...`.
   - ❌ FORBIDDEN: `python script.py` (Do not assume active env)
   - ✅ REQUIRED: `conda run -n {project_name} python script.py`
2. **Rule Consistency**: See `.agent/rules/00a_project_environment.md` for the authoritative source.
3. **LLM Usage**: MUST use `my-llm-sdk` as per `.agent/rules/00b_llm_integration.md`.
"""
    system_patterns += critical_rules_section

    with open(context_dir / "systemPatterns.md", "w", encoding="utf-8") as f:
        f.write(system_patterns)
        
    # Generate .context/project_env.yaml
    project_env_content = f"conda_env: {project_name}\n"
    with open(context_dir / "project_env.yaml", "w", encoding="utf-8") as f:
        f.write(project_env_content)
        
    # Generate SETUP_GUIDE.md (EN)
    setup_guide_final = setup_guide_content.replace("{{project_name}}", project_name)
    with open(project_dir / "SETUP_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(setup_guide_final)

    # Generate SETUP_GUIDE_ZH.md (CN)
    setup_guide_zh_final = setup_guide_zh_content.replace("{{project_name}}", project_name)
    with open(project_dir / "SETUP_GUIDE_ZH.md", "w", encoding="utf-8") as f:
        f.write(setup_guide_zh_final)
        
    # Generate preflight.py
    with open(project_dir / "preflight.py", "w", encoding="utf-8") as f:
        f.write(preflight_content)
        
    # Generate 00_project_context.md (Summary)
    console.print("[dim]正在生成 00_project_context.md (项目摘要)...[/dim]")
    # In a real implementation, this might use an LLM to summarize if too large.
    # For POC, we synthesize a structured summary.
    project_context_summary = f"""# Rule 00: Project Context (Summary)

## 1. Goal
(Extracted from productContext.md)
This project aims to build an AI-native application as defined in the product context.

## 2. Architecture
(Extracted from systemPatterns.md)
Please refer to the detailed architecture in `.context/systemPatterns.md`.

## 3. System Instructions
- **MUST READ**: `.context/productContext.md` for requirements.
- **MUST READ**: `.context/systemPatterns.md` for implementation details.
- **MUST READ**: `.context/activeContext.md` (if exists) for current tasks.

## 4. Constraints
- Code must be strict and production-ready.
- Follow the workflow in `01_workflow_plan_first.md`.
"""
    # Simply writing the synthesis for now. In production, we'd read the actual content to summarize.
    
    with open(rules_dir / "00_project_context.md", "w", encoding="utf-8") as f:
        f.write(project_context_summary)

    # Write Fixed Rules
    with open(rules_dir / "00a_project_environment.md", "w", encoding="utf-8") as f:
        f.write(rule_00a_content)

    with open(rules_dir / "00b_llm_integration.md", "w", encoding="utf-8") as f:
        f.write(rule_00b_content)

    with open(rules_dir / "01_workflow_plan_first.md", "w", encoding="utf-8") as f:
        f.write(rule_01_content)
        
    with open(rules_dir / rule_02_template_name, "w", encoding="utf-8") as f:
        f.write(rule_02_content)

    with open(rules_dir / "03_output_format.md", "w", encoding="utf-8") as f:
        f.write(rule_03_content)
        

    # Write README
    readme_content = f"""# {project_name}

## Active Rules 🛡️
The Agent MUST follow these rules located in `.agent/rules/`:
- **[00a] Environment**: `conda run -n {project_name}` is MANDATORY.
- **[00b] LLM**: Use `my_llm_sdk` only.
- **[01] Workflow**: Plan before coding.

## Project Context
Generated by Vibe-CLI.

- [Product Requirements](.context/productContext.md)
- [System Architecture](.context/systemPatterns.md)
"""
    with open(project_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Git init
    os.system(f"cd '{project_dir}' && git init > /dev/null 2>&1")

    # Calculate relative path for display
    try:
        display_path = os.path.relpath(project_dir, os.getcwd())
    except ValueError:
        display_path = str(project_dir)

    # Use single quotes if path contains spaces
    if " " in display_path:
        display_path = f"'{display_path}'"

    success_msg = f"""[bold green]✨ 项目初始化完成！[/bold green]

[bold yellow]👉 接下来请按顺序执行：[/bold yellow]

1. [bold cyan]生成实施计划[/bold cyan] (Roadmap):
   python vibe.py plan {display_path}

2. [bold cyan]进入项目[/bold cyan]:
   cd {display_path}

3. [bold cyan]环境准备 (必做)[/bold cyan]:
   请打开 [bold]SETUP_GUIDE_ZH.md[/bold] 按照指引完成环境配置。
   (Conda 环境创建 -> 安装依赖 -> 预检通过)

4. [bold cyan]启动 AI 编程[/bold cyan]:
   code .
   (在 IDE 中输入: [dim]"Start Phase 1, follow activeContext.md"[/dim])
"""
    console.print(Panel(success_msg, title="Success", expand=False))

@app.command()
def plan(
    project_dir: str = typer.Argument(".", help="项目目录路径"),
):
    """
    生成下一阶段的实施计划 (activeContext.md)。
    """
    project_path = Path(project_dir)
    context_dir = project_path / ".context"
    
    if not context_dir.exists():
        console.print(f"[bold red]错误:[/bold red] 在 {project_dir} 未找到 .context 目录。这是 Vibe 项目吗？")
        raise typer.Exit(code=1)

    product_context_path = context_dir / "productContext.md"
    system_patterns_path = context_dir / "systemPatterns.md"
    
    if not product_context_path.exists() or not system_patterns_path.exists():
        console.print("[bold red]错误:[/bold red] 缺少 productContext.md 或 systemPatterns.md。")
        raise typer.Exit(code=1)

    # Read Context
    try:
        product_context = product_context_path.read_text(encoding="utf-8")
        system_patterns = system_patterns_path.read_text(encoding="utf-8")
    except Exception as e:
         console.print(f"[bold red]读取日志错误:[/bold red] {e}")
         raise typer.Exit(code=1)

    # --- Project Manager Agent ---
    console.print("\n[bold green]🤖 项目经理 (Project Manager):[/bold green] 正在规划下一步...")
    
    pm_template = read_template("project_manager.md", PROMPTS_DIR)
    pm_prompt = pm_template.replace("{{product_context}}", product_context).replace("{{system_patterns}}", system_patterns)
    
    pm_response = call_llm(pm_prompt, "项目经理")
    active_context = extract_file_content(pm_response, "activeContext.md")
    
    if not active_context:
        console.print("[yellow]⚠️  无法严格解析 activeContext.md，使用原始回复作为后备[/yellow]")
        active_context = pm_response

    # Save Output
    output_path = context_dir / "activeContext.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(active_context)
        
    console.print(f"[green]✅ 路线图已更新: {output_path}[/green]")

if __name__ == "__main__":
    app()
