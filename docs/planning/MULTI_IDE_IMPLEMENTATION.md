# 多 IDE 支持设计与实施方案

根据你的问题，基于 Vibe Coding Flow 的架构，以下是针对 Antigravity, Claude Code, Cursor 三种 IDE 的详细设计思考。

下面是针对 **Antigravity / Claude Code / Cursor** 整理的一套精简、直接的项目初始化做法，不再区分复杂的 Local/Shared 层级，每个 IDE 只关注最核心的配置文件。

---

## 1) Google Antigravity

**核心逻辑**：基于 `.agent/` 目录进行细粒度管理。

### 项目骨架
*   **Rules**: 放在 `<root>/.agent/rules/`。
*   **Skills**: 放在 `<root>/.agent/skills/`（项目专用工具）。
*   **Task**: 根目录的 `task.md`（Agent 执行进度的显式记忆）。

### 目录树示例
```text
<repo>/
├── .agent/
│   ├─ rules/           # 项目规范与约束
│   │  ├─ stack.md
│   │  └─ workflow.md
│   └─ skills/          # 项目专用 Python Skills
│      └─ my_tool/
│         └─ SKILL.md
└── task.md             # 任务进度跟踪 (Agent 自动读写)
```

---

## 2) Claude Code（Anthropic）

**核心逻辑**：聚合上下文到 `CLAUDE.md`，并通过 `.claude/` 存储扩展配置。

### 项目骨架
*   **CLAUDE.md**: 唯一的规则聚合文件。包含构建指令、代码风格、以及“读取 `.context/` 目录”的强制指令。
*   **settings.json**: 项目**共享**配置（进 git）。
    *   **Schema**: 使用 `permissions` 对象控制命令权限，而非 `autoRun`。
    *   **Example**:
        ```json
        {
          "permissions": {
            "allow": ["bash", "git status", "npm test"],
            "ask": ["git push"],
            "deny": ["rm -rf /"]
          }
        }
        ```
*   **mcp.json**: MCP 服务器配置（连接外部工具）。
*   **skills/**: `.claude/skills/` 存放项目脚本，供 Claude 通过 Terminal 直接运行。

### 配置策略
*   **Vibe 行为**: 仅生成 `.claude/settings.json`（Shared）。
*   **Claude 行为**: 运行过程中会自动生成 `.claude/settings.local.json`（存储个人信任状态、会话历史）。
*   **Git 策略**: `vibe create` 生成的 `.gitignore` 必须包含 `.claude/settings.local.json`，确保个人状态不污染仓库。

### 目录树示例
```text
<repo>/
├── CLAUDE.md            # 项目主入口规则 (由 Vibe 聚合生成)
├── .gitignore           # 包含 .claude/settings.local.json
└── .claude/
   ├─ settings.json      # 基本设置 (Shared Rule)
   ├─ mcp.json           # MCP 工具链配置
   └─ skills/            # 项目级脚本工具 (e.g., db_init.py)
```

---

## 3) Cursor

**核心逻辑**：使用标准 `.cursor/rules/` 架构。

### 项目骨架
*   **Rules**: 放在 `.cursor/rules/` 下，采用 `.mdc` 格式（支持自动触发条件）。
*   **Vibe 策略**: 将核心规则分散为 `core.mdc`, `frontend.mdc` 等，提高匹配精度。

### 目录树示例
```text
<repo>/
└── .cursor/
    └─ rules/
       ├─ core.mdc       # 基础架构与 Vibe 流程约束
       └─ tech_stack.mdc # 技术栈规范
```

---

## 一句话落地建议

*   **Antigravity**：放 **`.agent/rules/` + `.agent/skills/`**。
*   **Claude Code**：放 **`CLAUDE.md` + `.claude/`**（含 settings, mcp, skills）。
*   **Cursor**：放 **`.cursor/rules/*.mdc`**。

Vibe 将负责把 `.context/` 里的“真值”同步到上述各个 IDE 的特定位置。不再搞 `local` 覆盖，保持结构扁平化。

[1]: https://antigravity.google/docs/rules-workflows?utm_source=chatgpt.com "Rules / Workflows"
[2]: https://antigravity.google/docs/skills?utm_source=chatgpt.com "Agent Skills - Google Antigravity Documentation"
[3]: https://codelabs.developers.google.com/getting-started-with-antigravity-skills?hl=en&utm_source=chatgpt.com "Getting Started with Skills in Google Antigravity"
[4]: https://code.claude.com/docs/en/settings "Claude Code settings - Claude Code Docs"
[5]: https://cursor.com/docs/context/rules?utm_source=chatgpt.com "Rules | Cursor Docs"
[6]: https://github.com/digitalchild/cursor-best-practices?utm_source=chatgpt.com "digitalchild/cursor-best-practices: Best practices when using Cursor the AI editor."

## 4. 代码修改方案 (How to Modify)

目前的 `vibe` 代码库中，`adapters/` 目录已经包含了基础的适配器类，但 `cli/app.py` 尚未启用它们。

### 4.1 核心修改点

你需要修改 `vibe/cli/app.py` 中的 `create` 命令，从"硬编码 Antigravity 逻辑" 转变为 "使用 AdapterRegistry"。

**修改前 (当前代码)**:
```python
# vibe/cli/app.py
rules_dir = project_dir / ".agent" / "rules"  # 硬编码!
os.makedirs(rules_dir, exist_ok=True)
# ... 手动写入一个个文件 ...
```

**修改后 (目标代码)**:
```python
# 1. 引入 Registry
from vibe.adapters.registry import AdapterRegistry

# 2. 获取参数 (需在 create 函数添加 --ide 参数)
ide: str = typer.Option("antigravity", "--ide", help="Target IDE")

# 3. 获取适配器
adapter = AdapterRegistry.get(ide)

# 4. 准备规则字典 (内存中)
rules = {
    "00a_project_environment.md": rule_00a_content,
    "02_stack.md": rule_02_content,
    ...
}

# 5. 委托适配器写入
adapter.write_rules(project_dir, rules)
adapter.write_config(project_dir, config)
```

### 4.2 核心修改方案 (Adapter Pattern)

你需要修改 `vibe/cli/app.py` 中的 `create` 命令，引入 **"Logic/IO Separation"** 的适配器模式。

**Target Architecture (三段式):**

```python
# 1. Build Logic (Pure Function)
# 根据 stack/prompt 构建统一的规则包 (无论 IDE 是谁)
rule_bundle = build_rule_bundle(context_dict, tech_stack)

# 2. Projection Logic (Pure Function)
# 将规则包投影为特定 IDE 的写入计划 (WritePlan: {path: content})
# --ide cursor -> 生成 .cursor/rules/*.mdc
# --ide claude -> 生成 CLAUDE.md + settings.json
adapter = AdapterRegistry.get(ide)
write_plan = adapter.project(project_root, rule_bundle)

# 3. Execution (Side Effects / IO)
# 执行写入，处理 safe/force/backup 逻辑
apply_write_plan(write_plan, mode="safe") 
```

### 4.3 验证计划

1.  **Antigravity 测试**: 生成项目，检查 `.agent/rules` 是否存在且内容指向 `.context/`。
2.  **Claude 测试**: 生成项目，检查 `CLAUDE.md` 头部是否含 "Read .context/activeContext.md" 指令，且 `settings.json` 包含 `permissions` 对象。
3.  **Cursor 测试**:
    *   检查 `.cursor/rules/00_core.mdc` 是否存在且 Glob 正确。
    *   （注：`.cursorrules` 仅在显式指定 legacy 模式时生成，常规验证不检查）

---

## 5. Functional Spec: Automated Scaffolding (自动化脚手架)

本节细化 **"One-Command Scaffolding"** 的具体实现规格，作为开发指南。

### 5.1 CLI 交互设计 (The Interface)

用户通过统一的 CLI 命令生成项目骨架。

**Command Syntax:**
```bash
vibe create <project_name> --ide <target_ide> [--prompt <description>]
```

**Parameters:**
*   `--ide antigravity` (默认): 生成 Google Antigravity 标准结构（`.agent/`）。
*   `--ide claude`: 生成 Claude Code 扁平化结构（`CLAUDE.md`, `.claude/`）。
*   `--ide cursor`: 生成 Cursor 规则结构（`.cursor/rules/`）。
*   `--ide all`: 生成兼容所有 IDE 的全量结构（适合混合开发团队）。

---

### 5.2 生成逻辑 (The Logic)

Vibe 遵循 **"Source of Truth (内核) -> Projections (投影)"** 的生成范式。

#### Phase 1: Core Context Generation (不论 IDE)
任何项目初始化时，首先生成 Vibe 标准内核 `ProjectContext`。
*   **Target**: `<project_root>/.context/`
*   **Artifacts**:
    *   `productContext.md`: 存放 PRD、用户故事（由 `--prompt` 转换生成）。
    *   `systemPatterns.md`: 存放架构决策、技术栈规范。
    *   `activeContext.md`: 存放当前任务状态 (初始为空)。

#### Phase 2: Adapter Execution (IDE 特定)
根据 `--ide` 参数，调用对应的 `IDEAdapter` 将内核投影为该 IDE 能理解的配置。

| Target IDE | Adapter Action | File Generation Details |
| :--- | :--- | :--- |
| **Antigravity** | **Copy & Ref** | 生成标准的 `.agent/rules/` 和 `.agent/skills/`。<br>重点：`00_context.md` 必须是指向 `.context/` 的指针。 |
| **Claude Code** | **Aggregate** | 生成聚合的 `CLAUDE.md`。<br>生成共享配置 `.claude/settings.json` (含权限分级)。<br>生成 `.gitignore` 忽略 local 文件。 |
| **Cursor** | **Distribute** | **默认**: 生成 `.cursor/rules/*.mdc` (00_core, 10_backend)。<br>**Legacy**: 仅在覆盖开关打开时生成 `.cursorrules`。 |

---

### 5.3 模板系统规格 (Templates)

所有 IDE 的配置文件**严禁硬编码**在 Python 代码中，必须使用 Jinja2 模板管理。

**Directory Structure:**
```text
vibe/templates/
├── common/                 # 通用内容 (Shared)
│   ├── product_context.md.j2
│   └── active_context.md.j2
│
├── antigravity/            # Antigravity 专用
│   ├── rules/
│   │   └── default_rule.md.j2
│   └── task.md.j2
│
├── claude/                 # Claude Code 专用
│   ├── CLAUDE.md.j2        # 聚合模板
│   └── mcp.json.j2
│
└── cursor/                 # Cursor 专用
    └── rules/
        └── rule.mdc.j2
```

### 5.4 "Global Check" 逻辑 (Non-intrusive)

CLI **不应修改** 用户的全局环境（避免侵入性），但应在初始化的最后一步**具备检测能力**并给出建议。

1.  **Check**: 检查 `~/.claude/settings.json` 或 `~/.gemini/...` 是否存在。
2.  **Suggest**: 如果缺失，在 CLI 输出中打印：
    > 💡 **Tip**: 检测到您尚未配置全局 Claude 设置，建议运行 `vibe init-global` 以获得最佳体验。

---

### 5.5 Skills Management Strategy (技能统一化)

为解决跨 IDE 执行不一致问题，采用 **"One Script, Multiple Callers"** 策略。

*   **Core Logic**: 所有真实的工具脚本统一落位到 `<root>/scripts/` (e.g., `scripts/db_reset.py`)。
*   **IDE Wrappers**:
    *   **Antigravity**: `.agent/skills/db/run.py` -> `subprocess.call(["python", "scripts/db_reset.py"])`
    *   **Claude**: 提示用户 "Run `python scripts/db_reset.py`" 或通过 MCP 允许执行该路径。
    *   **Cursor**: 在 `.mdc` 中指引用户 "Execute `python scripts/db_reset.py` to reset db"。

这样维护成本最低，逻辑只会写一份。

#### 1. Global Skills (通用能力)
这些是跨项目的通用能力（如 Web Search, General Research）。

*   **策略**: **"Lazy Check + One-time Init" (懒检测 + 一次性初始化)**
    *   **New Command**: 引入 `vibe init` 命令，专门负责初始化用户全局环境。
        *   功能：将 `vibe/lib/global/` 下的 Skills 和 Rules 部署到用户的 `~/.gemini`, `~/.claude` 等目录。
        *   时机：用户首次安装 Vibe 后运行一次即可。
    *   **Lazy Check**: 在 `vibe create` 运行时，快速检测全局环境是否就绪（例如检查 `~/.gemini/skills/browser-tools` 是否存在）。
        *   **如果缺失**: 仅打印警告提示 "⚠️ Global skills missing. Run `vibe init` to install."，**不自动阻断**项目创建，也不静默修改用户环境。

#### 2. Project Skills (项目上下文能力)
这些是与当前项目业务逻辑强绑定的能力（如 "Reset Local DB", "Deploy to Staging"）。

*   **分类 A: Static Utilities (静态工具)**
    *   *定义*: 通用但必须放在项目内的工具 (e.g., `git_smart_commit`)。
    *   *动作*: 直接 Copy。从 `vibe/lib/local/skills/` 复制到项目 `.agent/skills/` 或 `.claude/skills/`。

*   **分类 B: Dynamic Context (动态上下文工具)**
    *   *定义*: 依赖项目配置的工具 (e.g., `db_client` 需要连接字符串，`api_tester` 需要 Base URL)。
    *   *动作*: **Template Rendering**。
    *   *流程*:
        1.  读取 `vibe/templates/skills/db_client.py.j2`
        2.  注入变量 (e.g., `{{ db_type }}`, `{{ port }}`)
        3.  生成可执行脚本 `scripts/db_client.py`

#### 3. IDE 差异化实现 (Implementation Details)

由于各 IDE 对 Skill 支持方式不同，Vibe 需做适配：

| Feature | **Antigravity** | **Claude Code** | **Cursor** |
| :--- | :--- | :--- | :--- |
| **Global Skills** | Copy to `~/.gemini/skills/` | Suggest adding to `~/.claude/mcp.json` | N/A (依赖 VSCode 插件) |
| **Project Skills** | Generate `SKILL.md` + Scripts in `.agent/skills/` | Generate Scripts in `.claude/skills/` + CLI Instructions | Generate `.mdc` referring to `./scripts/` |
| **Execution** | Native Support (Agent 自动调用) | Prompt Guidance ("Run python .claude/skills/xxx") | User Manual Invocation |

### 5.6 Technical Considerations (权限与路径)

在实现 Global Init 功能时，必须严格遵守以下技术约束，以确保跨平台兼容性：

1.  **权限边界 (User Context)**
    *   `vibe init` 和 IDE 均以**用户身份**运行，天然拥有读写 User Home (`~`) 的权限。
    *   **严禁**尝试读写系统级目录（如 `C:\Windows`, `/usr/bin`），这会导致权限错误。

2.  **Windows 路径适配**
    *   **问题**: `~/.gemini` 在 Windows 上对应 `C:\Users\<Name>\.gemini`。
    *   **解决方案**: 代码中**严禁硬编码**路径分隔符（`/` 或 `\`）。
    *   **Implementation**: 必须使用 Python `pathlib`:
        ```python
        from pathlib import Path
        user_home = Path.home()
        gemini_skills = user_home / ".gemini" / "antigravity" / "skills"
        ```

3.  **文件锁定 (File Locking)**
    *   **场景**: 如果 IDE 正在运行，可能会锁定某些配置文件，导致 `vibe init` 写入失败（常见于 Windows）。
    *   **防御**: 文件写入操作需包裹在 `try-except PermissionError` 块中。
    *   **提示**: 捕获错误后，友善提示用户："Permission denied. Please close your IDE and try again."

### 5.7 Template Stitching Strategy (模块化拼装策略)

Vibe 的规则生成不是简单的“文件复制”，而是基于 **"Fragments (积木) + Context (蓝图)"** 的动态拼装系统。

#### 1. 规则文件清单 (Antigravity 示例)

Antigravity 采用编号文件系统，能够清晰地管理规则优先级。

| Target File | Pattern Type | Logic Description |
| :--- | :--- | :--- |
| `00_project_context.md` | **Pointer (指针)** | **Static Template**。<br>不直接包含内容，而是指向 `.context/productContext.md`，避免信息孤岛。 |
| `01_workflow.md` | **Fixed (固定)** | **Static Template**。<br>包含 Vibe 的标准 SOP (Plan -> Act -> Verify)，几乎所有项目都通用。 |
| `02_stack.md` | **Dynamic (动态)** | **Composition (拼装)**。<br>根据识别到的技术栈（如 Python, React），从 `lib/fragments/stack/` 读取对应片段拼接而成。<br>*Logic: `join([python.md, react.md])`* |
| `03_conventions.md` | **Dynamic (动态)** | **Composition (拼装)**。<br>包含 Code Style, Naming Convention 等细节。<br>*Logic: `join([pep8.md, google_style.md])`* |

#### 2. Fragment Library (积木库设计)

我们需要构建一个细粒度的积木库：
```text
vibe/lib/fragments/
├── stack/
│   ├── python.md        # Python specific patterns
│   ├── typescript.md    # TS/Node patterns
│   └── react.md         # React component rules
└── style/
    ├── python_pep8.md   # PEP8 enforcement
    └── google_ts.md     # Google TS Style Guide
```

#### 3. Stitching Logic (拼装算法伪代码)

在 `vibe generate` 阶段，Adapter 会执行以下逻辑：

```python
def generate_stack_rules(tech_stack: List[str]) -> str:
    """
    Example: tech_stack = ["python", "fastapi"]
    """
    fragments = []
    
    # 1. Load fragments
    for tech in tech_stack:
        fragment_path = f"vibe/lib/fragments/stack/{tech}.md"
        if os.path.exists(fragment_path):
            fragments.append(load_text(fragment_path))
            
    # 2. Add header
    header = "# Technology Stack Guidelines\n\n"
    
    # 3. Stitch with separators
    body = "\n\n---\n\n".join(fragments)
    
    return header + body
```

对于 **Claude Code**，虽然它只有一个 `CLAUDE.md`，逻辑也是一样的：它是所有规则（Workflow + Stack + Conventions）的**终极聚合体**。

### 5.8 Defining Critical Implementation Details (关键落地细节)

基于深度评审，本节定义了防止开发踩坑的关键契约。

#### 1. Cursor Adapter Strategy (Cursor 适配策略)
*   **Legacy Handling**: 默认**不生成** `.cursorrules`。
    *   增加 `--cursor-legacy` 开关，仅当用户显式要求时才生成该兜底文件。
    *   **MDC Schema (规范)**:
        *   `00_core.mdc`: Glob `*` (Repo级通用规则 + 指向 `.context/`)
        *   `10_backend.mdc`: Glob `**/*.py` (Python相关)
        *   `10_frontend.mdc`: Glob `frontend/**` (JS/Vue/React相关)

#### 2. Antigravity Skill Pack Spec (Skill 包规范)
明确 Skill 不仅仅是文档，而是 **"Doc + Executable"** 的组合。
*   **Path**: `.agent/skills/<skill_name>/`
*   **Structure**:
    *   `SKILL.md`: 给 Agent 看的说明书 (Interface Def)。
    *   `run.py` (or `.sh`): 真正执行逻辑的入口。
    *   `schema.json` (Optional): 参数校验。

#### 3. Defensive Configuration (防御性配置)
针对 Claude Code 的 `settings.json`：
*   **Strategy**: **Safe Merge**。
*   如果文件不存在 -> 写入。
*   如果文件存在 -> 读取 -> 合并 `permissions.allow` 列表 -> 写回。

#### 4. Adapter Interface Design (适配器接口设计)
将逻辑与 IO 分离，确保可测试性。
```python
# 1. Core Logic (Pure Function)
def build_rule_bundle(context: ProjectContext) -> RuleBundle: ...

# 2. Projection Logic (Pure Function)
def project_for_antigravity(bundle: RuleBundle) -> WritePlan: ...

# 3. Execution (IO)
def apply_write_plan(plan: WritePlan, mode: str = "safe"): ...
```

#### 5. Overwrite Strategy (覆写策略)
*   **Default**: `safe` Mode (不覆盖已存在文件，仅打印 Diff 提示)。
*   **Flag**: `--force` Mode (强制覆盖，但先备份到 `.vibe/backup/`)。

#### 6. Single Source of Truth (SSOT)
*   **Decision**: `.context/activeContext.md` 是唯一的 SSOT。
*   `task.md` (Antigravity): 降级为 **Pointer File**。它不存储每一步的详细状态，而是引用 `.context/activeContext.md`，或由 Vibe 自动同步内容。

---

### 5.9 Implementation Roadmap (落地路径)

#### Step A: Core Infrastructure (PR #1)
1.  实现 `AdapterRegistry` 和基础 `BaseAdapter`。
2.  实现 `AntigravityAdapter` (将现有硬编码逻辑迁移)。
3.  实现 `build_rule_bundle` 纯函数逻辑。
4.  E2E Test: 验证目录生成和文件存在性。

#### Step B: Claude & Robustness (PR #2)
1.  实现 `ClaudeAdapter` (聚合 `CLAUDE.md`)。
2.  实现 `settings.json` 的 Merge 逻辑。
3.  增加 `--dry-run` 和 `--force` 参数支持。

#### Step C: Cursor & Advanced Skills (PR #3)
1.  实现 `CursorAdapter` (MDC 生成与拆分)。
2.  实现 Skill Pack 生成逻辑 (Jinja2 渲染动态脚本)。
3.  完善测试矩阵 (Content Assertion & Idempotency)。

---

### 5.10 Final Spec Addendums (最终定稿补充)

为确保实现无歧义，针对 Review 建议补充以下技术契约。

#### 1. Cursor MDC Implementation Detail
为确保 `.mdc` 规则被正确识别：
*   **Format**: 直接生成 XML-like 前缀或 `.mdc` header 语法（取决于 Cursor 最新支持）。
    *   *Default*: Frontmatter 风格。
        ```markdown
        ---
        description: Core Rules
        globs: *
        ---
        # Rule Content ...
        ```
*   **Merge Strategy (合并策略)**:
    *   **Append Only**: 当多个 `.mdc` 同时命中（如 `00_core.mdc` 和 `10_backend.mdc`），IDE 会将它们的内容拼接。
    *   **Order**: 依赖文件名顺序 (`00_` < `10_` < `90_`)。Vibe 生成的文件名必须严格遵循此排序。

#### 2. Claude Safe Merge Contract
针对 `settings.json` 和 `mcp.json` 的合并逻辑：
*   **Namespace Protection**: 仅对 Vibe 管理的 Block 进行 Merge，不触碰用户自定义字段。
*   **Schema Mismatch**:
    *   如果 JSON 解析失败或根对象类型不对（如数组 vs 对象），**跳过 Merge**。
    *   **Alert**: 打印 "⚠️ Unknown schema detected in settings.json. Skipping auto-merge."

#### 3. `--ide all` Projection Principle
*   **Definition**: 多投影并存，而非合并覆盖。
*   **Action**: 同时生成 `.agent/`, `.claude/`, `.cursor/`.
*   **Constraint**: 所有投影**严禁复制** `.context/` 里的内容，必须使用 **Pointer (引用)**。
    *   Antigravity: `Read .context/activeContext.md`
    *   Claude: `Read .context/activeContext.md` in `CLAUDE.md` header
    *   Cursor: `Refer to .context/activeContext.md` in `00_core.mdc`
*   **Benefits**: 确保 SSOT 唯一性，避免多处内容漂移。

#### 4. Definitions of Done (DoD) for PRs

*   **PR #1 (Core & Antigravity)**:
    *   [ ] `vibe create --ide antigravity` 输出结果的 Snapshot 与旧版一致（无回归）。
    *   [ ] 代码中包含 `RuleBundle`, `WritePlan`, `apply_write_plan(safe)`.
    *   [ ] CLI 支持 `--dry-run` 并打印 Plan 概览。

*   **PR #2 (Claude & Safety)**:
    *   [ ] `CLAUDE.md` 包含指向 SSOT 的指令块（Content Assertion）。
    *   [ ] `settings.json` 实现 Safe Merge (追加 `permissions.allow` 且去重)。
    *   [ ] `.gitignore` 自动包含 `.claude/settings.local.json`。

*   **PR #3 (Cursor & Skills)**:
    *   [ ] 生成 `.cursor/rules/*.mdc`，且包含正确的 globs Frontmatter。
    *   [ ] 验证 Safe Mode 下重复生成不修改已存在文件 (Idempotency)。
    *   [ ] 实现 Skill Scripts 统一落位到 `./scripts/`，各 IDE Adapter 仅生成 Wrapper 或引用。

---

## 6. 下一步计划 (Action Items)

1.  **Start Implementation**: 按照上述 Defined Roadmap 开始 PR #1 的开发。



