import os
import sys
import typer
import re
import shutil
import subprocess
import time
from pathlib import Path
from rich.panel import Panel
from rich.prompt import Prompt

from vibe.cli.console import console
from vibe.config.paths import TEMPLATES_DIR, PROMPTS_DIR, RULES_DIR
from vibe.config.settings import Settings
from vibe.utils.files import read_template

# Adapter Imports
import vibe.core.adapters.antigravity
import vibe.core.adapters.claude
import vibe.core.adapters.cursor
from vibe.core.scaffolding import build_rule_bundle, apply_write_plan
from vibe.core.adapter_registry import AdapterRegistry

app = typer.Typer(help="Vibe-CLI: Intelligent Project Bootstrapper")

# Try to import my_llm_sdk, handle failure gracefully
try:
    # Priority 1: Try importing from installed package (e.g. pip install -e .)
    from my_llm_sdk.client import LLMClient
except ImportError as e1:
    try:
        # Priority 2: Try importing from src (legacy/local dev)
        # Add parent directory to path to find src if running from repo root
        # Adjust for new package structure: repo root is 2 levels up from here (vibe/cli/app.py -> vibe/cli -> vibe -> repo)
        # Actually PACKAGE_ROOT.parent is repo root.
        from vibe.config.paths import PACKAGE_ROOT
        repo_root = PACKAGE_ROOT.parent
        sys.path.append(os.path.abspath(str(repo_root / "../my-llm-sdk")))
        from src.client import LLMClient
    except ImportError as e2:
        console.print("[bold red]Error:[/bold red] my_llm_sdk not found. Please ensure it is installed.")
        console.print(f"Debug Info: Checked sys.path: {sys.path}")
        console.print(f"Import Error 1: {e1}")
        console.print(f"Import Error 2: {e2}")
        console.print("Tip: Run `pip install git+https://github.com/wenjie2024/my-llm-sdk.git` or activate the correct conda environment (doc).")
        sys.exit(1)

def call_llm(prompt_text: str, step_name: str) -> str:
    if os.environ.get("VIBE_MOCK_LLM") == "1":
        console.print(f"[magenta]🔮 Mocking LLM response for {step_name}[/magenta]")
        return "|||FILE: productContext.md|||# Mock Goal\nGoal\n|||END_FILE|||\n" \
               "|||FILE: systemPatterns.md|||# Mock Architecture\nArch\n|||END_FILE|||\n" \
               "|||FILE: activeContext.md|||# Mock Task\nTask\n|||END_FILE|||"

    console.print(f"[yellow]⏳ {step_name} is thinking...[/yellow]")
    user_conf, proj_conf = Settings.resolve_config_paths()
    try:
        client = LLMClient(user_config_path=user_conf, project_config_path=proj_conf)
        response = client.generate(prompt=prompt_text)
        return response
    except Exception as e:
        console.print(f"[bold red]❌ LLM Error:[/bold red] {e}")
        # For dev benefit, if mock allowed but not set, strict fail. 
        # But if error happens, maybe fallback to mock? No, that's confusing.
        sys.exit(1)

def extract_file_content(response: str, filename: str) -> str:
    """Extracts content between |||FILE: filename||| and |||END_FILE|||"""
    pattern = re.compile(rf"\|\|\|FILE: {re.escape(filename)}\|\|\|(.*?)\|\|\|END_FILE\|\|\|", re.DOTALL)
    match = pattern.search(response)
    if match:
        return match.group(1).strip()
    return ""

@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite existing config"),
):
    """
    Initialize global configuration for Vibe CLI (Antigravity/Claude).
    """
    console.print(Panel("[bold blue]Vibe-CLI Global Setup[/bold blue]", expand=False))
    
    ide_choice = Prompt.ask(
        "Which IDE do you use primarily?",
        choices=["antigravity", "claude", "all"],
        default="antigravity"
    )
    
    # Resolve Paths
    from vibe.config.paths import PACKAGE_ROOT
    global_assets = PACKAGE_ROOT / "lib" / "global"
    
    if not global_assets.exists():
        console.print(f"[bold red]Error:[/bold red] Global assets not found at {global_assets}")
        raise typer.Exit(1)

    # --- Antigravity Setup ---
    if ide_choice in ["antigravity", "all"]:
        home = Path.home()
        gemini_root = home / ".gemini"
        gemini_root.mkdir(exist_ok=True)
        
        # 1. GEMINI.md (Defaulting to English/Standard)
        target_gemini = gemini_root / "GEMINI.md"
        source_gemini = global_assets / "GEMINI_EN.md"
        
        if target_gemini.exists() and not force:
            should_overwrite = typer.confirm(f"Found existing {target_gemini}. Overwrite?", default=False)
        else:
            should_overwrite = True
            
        if should_overwrite:
            if target_gemini.exists():
                # Perform backup before overwrite
                backup_gemini = target_gemini.with_suffix(f".bak.{int(time.time())}")
                shutil.copy(target_gemini, backup_gemini)
                console.print(f"[dim]📜 Existing config backed up to: {backup_gemini}[/dim]")
            
            if source_gemini.exists():
                shutil.copy(source_gemini, target_gemini)
                console.print(f"[green]✅ Copied Global Rules (English) to: {target_gemini}[/green]")
            else:
                 # Fallback to older naming if needed, but here we expect GEMINI_EN.md
                 console.print(f"[red]❌ Source {source_gemini} not found.[/red]")

            # Tip for Chinese User
            console.print(f"[dim]💡 Tip: If you prefer the Chinese version, manually copy:[/dim]")
            console.print(f"[dim]   cp {global_assets / 'GEMINI_CN.md'} {target_gemini}[/dim]")
        else:
            console.print(f"[dim]Skipped {target_gemini}[/dim]")

        # 2. Skills
        target_skills = gemini_root / "skills"
        source_skills = global_assets / "skills"
        
        if target_skills.exists() and not force:
            should_overwrite_skills = typer.confirm(f"Found existing skills at {target_skills}. Overwrite/Merge?", default=False)
        else:
            should_overwrite_skills = True
            
        if should_overwrite_skills:
            if target_skills.exists():
                # Perform backup before overwrite/merge
                backup_skills = target_skills.parent / f"skills.bak.{int(time.time())}"
                shutil.copytree(target_skills, backup_skills)
                console.print(f"[dim]📜 Existing skills backed up to: {backup_skills}[/dim]")
            
            shutil.copytree(source_skills, target_skills, dirs_exist_ok=True)
            console.print(f"[green]✅ Installed Global Skills to: {target_skills}[/green]")
        else:
            console.print(f"[dim]Skipped Skills installation[/dim]")

    # --- Claude Setup ---
    if ide_choice in ["claude", "all"]:
        console.print("\n[bold yellow]ℹ️  Claude Code Setup[/bold yellow]")
        console.print("Claude Code uses project-level configuration mostly.")
        console.print(f"Global templates are available at: [bold]{global_assets}[/bold]")
        console.print(f"Recommended versions:")
        console.print(f"  • Chinese: [dim]{global_assets / 'CLAUDE_CN.md'}[/dim]")
        console.print(f"  • English: [dim]{global_assets / 'CLAUDE_EN.md'}[/dim]")
        console.print("You can copy these files to your project roots as `CLAUDE.md`.")

def _check_global_config(ide: str):
    """Checks if global config is set up for the chosen IDE."""
    home = Path.home()
    if ide == "antigravity":
        gemini_rules = home / ".gemini" / "GEMINI.md"
        if not gemini_rules.exists():
            console.print(Panel(
                "[bold yellow]⚠️  Global Rules Not Found[/bold yellow]\n\n"
                f"We couldn't find [bold]{gemini_rules}[/bold].\n"
                "Antigravity might not behave as expected (e.g., wrong language).\n\n"
                "👉 [bold]Recommendation:[/bold] Run `python -m vibe init` to set it up.",
                title="Configuration Check"
            ))

@app.command()
def create(
    project_path: str = typer.Argument(..., help="Path to the new project (e.g., 'my-app' or '../my-app')"),
    prompt: str = typer.Option(None, help="一句话需求描述"),
    promptfile: str = typer.Option(None, "--promptfile", help="从文件读取详细需求"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="启用交互模式以手动完善需求"),
    no_plan: bool = typer.Option(False, "--no-plan", help="跳过自动生成实施计划"),
    ide: str = typer.Option("antigravity", help="Target IDE: antigravity, claude, cursor"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without writing"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
    cursor_legacy: bool = typer.Option(False, "--cursor-legacy", help="Generate legacy .cursorrules (Cursor only)"),
):
    """
    Starts a new AI-Ready project from a prompt.
    """
    # Check Global Config First
    _check_global_config(ide)

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
                f"[bold cyan]python -m vibe create {project_path} --promptfile {promptfile}[/bold cyan]",
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
        console.print("[dim]示例：python -m vibe create my-project --prompt \"你的想法\"[/dim]")
        console.print("[dim]或者：python -m vibe create my-project --promptfile requirements.md[/dim]")
        raise typer.Exit(code=1)
    
    console.print(Panel.fit(f"[bold blue]Welcome to Vibe-CLI 2.0 (Refactored)[/bold blue]\nInitializing project: [green]{project_name}[/green]\nLocation: [dim]{project_dir}[/dim]"))

    if project_dir.exists():
        if (project_dir / ".context").exists():
            console.print(f"[bold red]Error:[/bold red] Directory {project_dir} is already a Vibe project (contains .context).")
            raise typer.Exit(code=1)
        console.print(f"[yellow]⚠️  注意: 目标文件夹 {project_dir} 已存在，将在此进行初始化。[/yellow]")
    else:
        project_dir.mkdir(parents=True, exist_ok=True)

    # Create plan directory with .gitkeep
    plan_dir = project_dir / "plan"
    plan_dir.mkdir(exist_ok=True)
    (plan_dir / ".gitkeep").touch()

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
    architect_prompt = architect_template.replace("{{user_request}}", user_request).replace("{{product_context}}", product_context)
    
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

    # --- Step 3: Scaffolding Phase 1 (Core Context) ---
    console.print(f"\n[bold white]🔨 Initializing Core Context for {project_name}...[/bold white]")
    
    setup_guide_content = read_template("SETUP_GUIDE.md", TEMPLATES_DIR)
    setup_guide_zh_content = read_template("SETUP_GUIDE_ZH.md", TEMPLATES_DIR)
    preflight_content = read_template("preflight.py", TEMPLATES_DIR)

    if not dry_run:
        os.makedirs(project_dir, exist_ok=True)
        context_dir = project_dir / ".context"
        os.makedirs(context_dir, exist_ok=True)

        # Write productContext
        with open(context_dir / "productContext.md", "w", encoding="utf-8") as f:
            f.write(product_context)

        # Write systemPatterns (with Critical Rules injection)
        critical_rules = "\n## 🛡️ Vibe Critical Rules\n1. Follow the workflow in `01_workflow.md`.\n2. Respect IDE-specific rules.\n"
        system_patterns_final = system_patterns + critical_rules
        
        with open(context_dir / "systemPatterns.md", "w", encoding="utf-8") as f:
            f.write(system_patterns_final)
            
        # Write project_env.yaml
        with open(context_dir / "project_env.yaml", "w", encoding="utf-8") as f:
            f.write(f"conda_env: {project_name}\n")
            
        # Write setup guides
        with open(project_dir / "SETUP_GUIDE.md", "w", encoding="utf-8") as f:
            f.write(setup_guide_content.replace("{{project_name}}", project_name))
            
        with open(project_dir / "SETUP_GUIDE_ZH.md", "w", encoding="utf-8") as f:
            f.write(setup_guide_zh_content.replace("{{project_name}}", project_name))
            
        with open(project_dir / "preflight.py", "w", encoding="utf-8") as f:
            f.write(preflight_content)
    else:
        console.print("[yellow]DRY RUN: Skipping Core Context creation[/yellow]")

    # --- Step 4: Scaffolding Phase 2 (IDE Projection) ---
    console.print(f"[bold white]🎨 Projecting configuration for IDE: {ide}...[/bold white]")
    
    # 1. Build Bundle
    context_data = {
        "product_context": product_context,
        "system_patterns": system_patterns,
    }
    
    try:
        rule_bundle = build_rule_bundle(context_data)
        
        # 2. Get Adapter
        adapter = AdapterRegistry.get(ide)
        
        # 3. Project
        write_plan = adapter.project(rule_bundle)
        
        # 4. Apply
        apply_write_plan(write_plan, project_dir, mode="force" if force else "safe", dry_run=dry_run)
        
        # Pass cursor_legacy param if applicable (To be implemented in Step C)
        # currently project() signature doesn't support extra args, 
        # we might need to pass it via constructor or context.
        # For now, simplistic implementation for Antigravity (Step A).
        
    except Exception as e:
        console.print(f"[bold red]Adapter Error (Did you install the right adapter?):[/bold red] {e}")
        # raise typer.Exit(code=1) # Don't exit yet, let dry run finish or debug

        

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
    try:
        subprocess.run(["git", "init"], cwd=project_dir, check=True, capture_output=True)
    except Exception as e:
        console.print(f"[yellow]⚠️  Git 初始化失败 (非致命错误): {e}[/yellow]")

    # --- Step 5: Auto-Plan ---
    if not no_plan:
        _run_plan_logic(project_dir)

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

1. [bold cyan]进入项目[/bold cyan]:
   cd {display_path}

2. [bold cyan]规划与开发流程[/bold cyan]:
   项目已预设 [bold]plan/[/bold] 目录。在每个开发阶段（Phase）开始前，
   AI 代理将遵循 [bold]01_workflow_plan_first.md[/bold] 规则，
   在此目录下生成详细的实施计划（如 `plan_phase1.md`）。

3. [bold cyan]环境准备 (必做)[/bold cyan]:
   请打开 [bold]SETUP_GUIDE_ZH.md[/bold] 按照指引完成环境配置。
   (Conda 环境创建 -> 安装依赖 -> 预检通过)

3. [bold cyan]启动 AI 编程[/bold cyan]:
   code .
   (在 IDE 中输入: [dim]"Start Phase 1, follow activeContext.md"[/dim])
"""
    console.print(Panel(success_msg, title="Success", expand=False))

def _run_plan_logic(project_path: Path):
    """
    Internal logic for generating planning roadmap.
    """
    context_dir = project_path / ".context"
    
    if not context_dir.exists():
        console.print(f"[bold red]错误:[/bold red] 未找到 .context 目录。")
        return

    product_context_path = context_dir / "productContext.md"
    system_patterns_path = context_dir / "systemPatterns.md"
    
    if not product_context_path.exists() or not system_patterns_path.exists():
        console.print("[bold red]错误:[/bold red] 缺少 productContext.md 或 systemPatterns.md。")
        return

    # Read Context
    try:
        product_context = product_context_path.read_text(encoding="utf-8")
        system_patterns = system_patterns_path.read_text(encoding="utf-8")
    except Exception as e:
         console.print(f"[bold red]读取失败:[/bold red] {e}")
         return

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

@app.command()
def plan(
    project_dir: str = typer.Argument(".", help="项目目录路径"),
):
    """
    生成下一阶段的实施计划 (activeContext.md)。
    """
    _run_plan_logic(Path(project_dir))

if __name__ == "__main__":
    app()
