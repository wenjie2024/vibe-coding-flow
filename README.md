# Vibe-CLI 2.0

**Vibe-CLI** 是一个“项目启动器（Bootstrapper）”：把你的一句话需求，自动变成一个**可直接开始 Vibe Coding 的 IDE 工程**。

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

### 1) 安装

```bash
# 在 vibe-coding-flow 根目录
pip install -r requirements.txt

# 初始化 SDK 配置（必做：创建/检查当前目录 config.yaml，用于 API Key）
python -m my_llm_sdk.cli init
```

### 2) 创建项目（生成“可 Vibe Coding 的工程骨架”）

```bash
python vibe.py create <PROJECT_PATH> --prompt "你的想法" --interactive
```

* `--interactive (-i)`：强烈推荐。用于回答“待确认事项”，避免 AI 误设范围。

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
python vibe.py create <PROJECT_PATH> --prompt "你的想法" --interactive
```

### Step 2. Plan（生成 Phase 1 的执行计划）

```bash
python vibe.py plan <PROJECT_PATH>
```

### Step 3. Setup（按指南搭环境 + 自检确保可用）

进入项目目录后，按 `SETUP_GUIDE_ZH.md` 完成：

1. 创建 Conda 环境
2. 安装 SDK（`pip install git+https://github.com/NoneSeniorEngineer/my-llm-sdk.git`）
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

## 🔍 常见问题（FAQ）

**Q: 为什么要 `preflight.py`？**
A: 因为 Vibe Coding 的第一原则是：**能跑再写**。`preflight.py` 把环境问题前置，一次解决，避免你在 IDE 里让 AI “边写边炸”。

**Q: 为什么需要 `.agent/rules/`？**
A: 它确保 AI 在 IDE 里不会“随手乱来”，例如禁止直接调用 OpenAI/Gemini SDK，统一走 `my_llm_sdk`，从而让工程保持一致和可维护。

---

## 📄 License

本项目采用 **Apache License 2.0** 协议开源。详情请见 [LICENSE](LICENSE) 文件。
