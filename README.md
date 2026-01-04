# Vibe-CLI 2.0

**Vibe-CLI** 是一个“项目启动器（Bootstrapper）”：把你的需求（一句话或详细文档），自动变成一个**可直接开始 Vibe Coding 的 IDE 工程**。

它解决的不是“写代码”，而是 **Day 0 环境与上下文的摩擦**：当你第一次用 Cursor / VSCode / Antigravity 打开项目时，AI Agent 看到的是一个已经准备好的工程——**环境可复现、规则可执行、计划可跟随**。

> **目标**：用最少步骤获得 “开箱即用的 Vibe Coding 环境”
> **结果**：`SETUP_GUIDE_ZH.md + preflight.py + .agent/rules + .context/` 一次生成，项目可立即进入开发状态 ✅

---

## ✅ 你会得到什么（核心产出）
 
Vibe-CLI 会为每个新项目生成四样“必需品”，让你**不再手动搭环境/写规则/写计划**：

1. **环境搭建指南**：`SETUP_GUIDE_ZH.md`
   手把手把 Conda + SDK + 项目变量配置到位（不靠口口相传）
2. **环境自检脚本**：`preflight.py`
   一键检测：Python/Conda/依赖/SDK/配置是否齐全，确保“能跑再开工”
3. **AI 行为规则**：`.agent/rules/`
   强制 AI 遵守项目规范（例如：必须走 `my_llm_sdk`、禁止直连厂商 SDK 等）
4. **项目记忆库**：`.context/`
   PRD / 架构 / 当前计划，确保 AI 在 IDE 里“有上下文地持续工作”

--- 

## 🚀 Quick Start：3 分钟跑通 Vibe 环境（推荐路径）

> 你只需要做三件事：安装依赖 → 创建项目 → 按指南 setup + 自检全绿

### 1) 全局配置 (Global Rules) - [Antigravity 用户必读]

在开始使用 Vibe-CLI 之前，建议先配置 Antigravity 的全局规则文件 (`GEMINI.md`)。这能确保所有 Antigravity 会话都遵循您的基础偏好（如语言、角色设定等）。

请将本仓库 `templates/` 目录下的 `GEMINI.md` (或 `GEMINI_CN.md` 仅供参考) 复制到您用户主目录下的 `.gemini` 文件夹中：

*   **Windows**:
    *   `%USERPROFILE%\.gemini\GEMINI.md`
    *   (例如: `C:\Users\YourName\.gemini\GEMINI.md`)
*   **macOS / Linux**:
    *   `~/.gemini/GEMINI.md`
    *   (例如: `/Users/YourName/.gemini/GEMINI.md`)

> **Note**: 这是 Antigravity 的 [Global Rules](https://antigravity.google/docs/rules-workflows?utm_source=chatgpt.com) 配置，对所有项目生效。Vibe-CLI 生成的 `.agent/rules` 是项目级规则，优先级更高。

### 2) 安装

```bash
# 在 vibe-coding-flow 根目录
pip install -r requirements.txt

# 初始化 SDK 配置（必做：创建/检查当前目录 config.yaml，用于 API Key）
python -m my_llm_sdk.cli init
```

### 2) 创建项目（生成“可 Vibe Coding 的工程骨架”）

**方式一：一句话需求（适合简单项目）**
```bash
python vibe.py create <PROJECT_PATH> --prompt "你的想法" --interactive
```

**方式 B：详细需求模板**
```bash
python vibe.py create my-project --promptfile requirements.md -i
```
> 如果 `requirements.md` 不存在，会自动生成包含 15 个章节的需求模板。建议配合 `-i` 使用，即使文档再全，最后的人工确认也是“不翻车”的关键。

* `--interactive (-i)`：建议默认开启，用于确认需求和技术栈。
* `python vibe.py plan my-project`：创建后运行，生成第一阶段计划。即使使用了详细模板，交互模式仍能让你在 AI 生成 PRD 后进行最后的锁定与微调。
* `--promptfile`：支持结构化需求输入，包含目标、用户故事、验收标准等深度上下文。支持与 `-i` 模式叠加使用。

### 3) 一键把环境跑到全绿 ✅（进入项目目录）

```bash
cd <PROJECT_PATH>
# 按 SETUP_GUIDE_ZH.md 操作完成环境配置（通常只需 conda create 和 pip install git+...）
python preflight.py
```

当 `preflight.py` 全绿后，你已经拥有一个“AI-Ready + 可复现”的 Vibe Coding 工程。

---

## 🧭 标准工作流（The Vibe Way）

### Step 1. Create（生成上下文 + 环境骨架）

```bash
# 方式 A：直接输入
python vibe.py create <PROJECT_PATH> --prompt "你的想法" --interactive

# 方式 B：使用需求模板（推荐复杂项目）
python vibe.py create <PROJECT_PATH> --promptfile requirements.md -i
```

### Step 2. Plan（生成 Phase 1 的执行计划）

```bash
python vibe.py plan <PROJECT_PATH>
```

### Step 3. Setup（按指南搭环境 + 自检确保可用）

进入项目目录后，按 `SETUP_GUIDE_ZH.md` 完成：

1. 创建 Conda 环境
2. 安装 SDK（`pip install git+https://github.com/wenjie2024/my-llm-sdk.git`）
3. 初始化 SDK（如果尚未配置过）
4. 运行自检：`python preflight.py` 全绿 ✅

### Step 4. Code（在 IDE 中按计划推进）

```bash
code .
```

在 IDE Chat 输入：
**`Start Phase 1, follow activeContext.md`**

---

## 🏗️ 系统架构（为什么它能“零摩擦”）

Vibe-CLI 采用**线性流水线（Linear Pipeline）**，由四个角色分别产出“能直接开工”的关键文件：

1. **Analyst（需求分析师）** → `.context/productContext.md`
2. **Architect（系统架构师）** → `.context/systemPatterns.md`
3. **DevOps Engineer（运维专家）** → `SETUP_GUIDE_ZH.md`, `preflight.py`, `.agent/rules/`
4. **Project Manager（项目经理）** → `.context/activeContext.md`

重点在 DevOps 这一段：**把“环境一致性”变成可执行文档 + 可验证脚本**，而不是口头约定。

---

## 📂 生成的项目结构（AI 打开 IDE 看到的就是这个）

```text
my-project/
├── .agent/
│   └── rules/                      # [核心] AI 行为准则（可执行的“工程纪律”）
│       ├── 00_project_context.md   # 项目摘要（给 AI 快速进入状态）
│       ├── 00a_project_environment # 环境运行规则（强制 conda run 等）
│       ├── 00b_llm_integration     # LLM 调用规则（必须走 my_llm_sdk）
│       └── ...
├── .context/                       # [核心] 项目记忆库（AI 的“长期上下文”）
│   ├── productContext.md           # 需求文档（PRD）
│   ├── systemPatterns.md           # 架构文档（含 Critical Rules）
│   ├── activeContext.md            # 当前计划（Phase / 任务拆解）
│   └── project_env.yaml            # 环境配置（用于一致性/复现）
├── SETUP_GUIDE_ZH.md               # [关键] 环境搭建保姆级教程
├── preflight.py                    # [关键] 环境自检脚本（跑通再开工）
└── README.md
```

---

## 4. 标准化工作流 (Vibe Coding Best Practices)

为了保证 AI 编码的质量和可维护性，Vibe-CLI 强制执行 **“先计划，后动手”** 的工作流：

### 1) 强制计划目录
所有新创建的项目都包含一个 `plan/` 目录。在进行任何非琐碎的功能开发或版本更新前，AI 代理会按照 `.agent/rules/01_workflow_plan_first.md` 的规定，在此目录下生成并保存计划文件。

### 2) 命名规范
*   **重大阶段**: `plan_phase1.md`, `plan_phase2.md` ...
*   **功能/版本更新**: `plan_v1.0_Login.md`, `plan_v1.1_OAuth.md` ...
*   **迭代微调**: `plan_v1.11_Fix_Redirection.md` (针对 v1.1 的小改动)

### 3) 为什么这么做？
*   **思想钢印**: 强制 AI 在动手前理清逻辑，减少“幻觉”和低级错误。
*   **可回溯性**: 所有的架构决策和实施路径都有案可查。
*   **协作一致性**: 即使切换不同的 AI 代理或人工介入，也能根据 `plan/` 快速接手上下文。

---

## 🔍 常见问题（FAQ）

**Q: 为什么要 `preflight.py`？**
A: 因为 Vibe Coding 的第一原则是：**能跑再写**。`preflight.py` 把环境问题前置，一次解决，避免你在 IDE 里让 AI “边写边炸”。

**Q: 为什么需要 `.agent/rules/`？**
A: 它确保 AI 在 IDE 里不会“随手乱来”，例如禁止直接调用 OpenAI/Gemini SDK，统一走 `my_llm_sdk`，从而让工程保持一致和可维护。

---

## 📄 License

本项目采用 **Apache License 2.0** 协议开源。详情请见 [LICENSE](LICENSE) 文件。
