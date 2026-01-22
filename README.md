# Vibe-CLI 2.0

**Vibe-CLI** 是一个“项目启动器（Bootstrapper）”：把你的需求（一句话或详细文档），自动变成一个**可直接开始 Vibe Coding 的 IDE 工程**。

它解决的不是“写代码”，而是 **Day 0 环境与上下文的摩擦**：当你第一次用 Cursor / VSCode / Antigravity 打开项目时，AI Agent 看到的是一个已经准备好的工程——**环境可复现、规则可执行、计划可跟随**。

> **目标**：用最少步骤获得 “开箱即用的 Vibe Coding 环境”
> **结果**：`SETUP_GUIDE_ZH.md + preflight.py + Rules + Context` 一次生成，项目可立即进入开发状态 ✅

---

## 🚀 Quick Start：3 分钟跑通 Vibe 环境

> **核心流程**：安装依赖 → 创建项目 (选 IDE) → 按指南 Setup + 自检

### 1. 安装 Vibe CLI
```bash
# 在 vibe-coding-flow 根目录
pip install -r requirements.txt
python -m my_llm_sdk.cli init  # 初始化 API Key 配置
```

### 2. 创建项目 (Generate)

使用 `vibe create` 命令生成项目骨架。支持通过 `--ide` 参数适配不同的 AI 工具。

**场景 A：交互式创建 (推荐)**
```bash
# 默认生成 Antigravity 配置
python vibe.py create my-project --prompt "写一个贪吃蛇游戏" -i

# 生成 Cursor 配置
python vibe.py create my-project --prompt "写一个贪吃蛇游戏" -i --ide cursor
```

**场景 B：基于需求文档 (复杂项目)**
```bash
# 生成 Claude Code 配置
python vibe.py create my-project --promptfile requirements.md -i --ide claude
```

> **IDE 选项**: `--ide antigravity` (默认), `--ide claude`, `--ide cursor`

### 3. Setup & Verify (进入项目)
```bash
cd my-project
# 1. 按 SETUP_GUIDE_ZH.md 完成环境配置 (新建 Conda 环境等)
# 2. 运行自检
python preflight.py
```
**当 `preflight.py` 全绿 ✅，你就可以开始 Vibe Coding 了。**

---

## ✅ 核心产出 (What You Get)

Vibe 为每个项目生成四类“必需品”，解决从需求到编码的“最后一公里”问题：

### 1. 通用基础 (Common)
无论使用哪个 IDE，都会生成：
*   **`.context/` (项目记忆库)**:
    *   `productContext.md`: 需求与用户故事 (PRD)。
    *   `systemPatterns.md`: 架构决策与技术栈。
    *   `activeContext.md`: 当前任务状态与计划指针。
*   **`SETUP_GUIDE_ZH.md`**: 环境搭建保姆级教程。
*   **`NEXT_STEPS.md`**: 初始化后的操作指引 (New)。
*   **`preflight.py`**: 环境完整性自检脚本。

### 2. IDE 专属配置 (IDE Specific)
Vibe 根据 `--ide` 参数生成不同的规则结构：

#### 🤖 Antigravity (Gemini)
```text
my-project/
├── .agent/
│   ├── rules/                  # 行为准则
│   │   ├── 00_project_context.md
│   │   └── ...
│   └── skills/                 # Project Skills (脚本)
│       ├── doc-maintainer/
│       └── ...
└── task.md                     # 任务指针文件
```

#### 🟣 Claude Code
```text
my-project/
├── CLAUDE.md                   # 核心规则文件 (单一入口)
├── .claude/
│   ├── settings.json           # 权限配置
│   ├── mcp.json                # MCP 工具链
│   └── skills/                 # Project Skills (脚本)
│       └── ...
└── .gitignore                  # 忽略本地配置
```

#### � Cursor
```text
my-project/
├── .cursor/
│   ├── rules/
│   │   ├── 00_core.mdc         # 核心上下文规则
│   │   └── 90_skills.mdc       # 技能索引规则
│   └── skills/                 # Project Skills (脚本)
│       └── ...
└── ...
```

---

## 🧰 Project Skills (内置技能)

Vibe 2.0 自动注入经过 AI 优化的技能包（Skill Packs）。这些技能遵循 Claude 官方规范，**跨 IDE 通用**：

| Skill | 描述 | 调用位置 |
| :--- | :--- | :--- |
| **doc-maintainer** | 自动分析代码变更并同步文档（README/PRD） | `.agent/skills`, `.claude/skills`, `.cursor/skills` (视 IDE 而定) |
| **lint_autofix** | Python 代码风格自动检测与修复 | 同上 |
| **test_generator** | 基于代码 AST 自动生成 Pytest 测试桩 | 同上 |
| **my-llm-sdk** | 包含 SDK API Cheatsheet 与使用指南 (In-Context Learning) | 自动安装到 `.agent/skills` |

> **Usage**: AI Agent 可直接调用这些脚本。例如：*"Run test generator on src/api.py"*

---

## 🧭 标准工作流 (The Vibe Way)

Vibe 强制执行 **“Plan -> Code -> Verify -> Sync”** 的闭环：

### Step 1. Plan
在动手前，AI 必须在 `/plan/` 目录下生成计划文件（如 `plan_phase1.md`），明确目标与验证步骤。

### Step 2. Code
AI 依据规则 (`.agent/rules` 或 `CLAUDE.md`) 编写代码，严格遵守 `my_llm_sdk` 等项目约束。

### Step 3. Verify
执行测试或验证指令。

### Step 4. Sync (Exit Criteria)
**[关键]** 在标记任务完成前，必须运行 `doc-maintainer` 技能。
> Command: `python <SKILLS_DIR>/doc-maintainer/scripts/analyze.py --since HEAD~1`

这确保了文档（README/架构图）永远不会滞后于代码。

---

## 🏗️ 系统架构

Vibe-CLI 采用 **线性流水线 (Linear Pipeline)** 架构，由四个角色分别产出关键文件：
1.  **Analyst** → `.context/productContext.md`
2.  **Architect** → `.context/systemPatterns.md`
3.  **DevOps** → `SETUP_GUIDE`, `preflight.py`, `Rules/Skills`
4.  **Project Manager** → `.context/activeContext.md`

---

## 📅 Roadmap

*   [x] **Core Scaffolding**: 完整的上下文生成 (Product/System/Active Context).
*   [x] **Preflight Checks**: 环境自检脚本.
*   [x] **Multi-IDE Adapters**: 支持 Antigravity, Claude, Cursor 的原生规则生成.
*   [x] **Project Skills**: 集成 doc-maintainer, lint-autofix 等自动化技能.
*   [x] **Standardization**: 强制统一 LLM SDK (`my-llm-sdk`) 与 Plan-First 工作流.

---

## 📄 License

本项目采用 **Apache License 2.0** 协议开源。详情请见 [LICENSE](LICENSE) 文件。
