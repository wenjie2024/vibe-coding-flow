# Vibe-CLI 重构方案与多IDE支持计划

**版本**: v1.0
**日期**: 2026-01-18
**状态**: 待实施

---

# 第一部分：代码重构详细方案

## 1. 重构目标

### 1.1 核心目标
- 将单文件 `vibe.py` (507行) 拆分为模块化结构
- 引入抽象层，分离关注点
- 提高代码可测试性和可维护性
- 为多IDE支持打下架构基础

### 1.2 设计原则
- **单一职责**: 每个模块只负责一个功能域
- **开闭原则**: 对扩展开放，对修改关闭
- **依赖倒置**: 依赖抽象而非具体实现
- **接口隔离**: 为不同IDE提供统一接口

---

## 2. 目标架构设计

### 2.1 目录结构

```
vibe-coding-flow/
├── vibe/                           # 主包目录
│   ├── __init__.py                 # 版本信息和公开API
│   ├── __main__.py                 # 入口点 (python -m vibe)
│   │
│   ├── cli/                        # CLI 层
│   │   ├── __init__.py
│   │   ├── app.py                  # Typer 应用主入口
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── create.py           # create 命令
│   │   │   ├── plan.py             # plan 命令
│   │   │   └── setup.py            # setup 命令
│   │   └── console.py              # Rich console 封装
│   │
│   ├── agents/                     # Agent 层（四角色）
│   │   ├── __init__.py
│   │   ├── base.py                 # 抽象基类 BaseAgent
│   │   ├── analyst.py              # 需求分析师
│   │   ├── architect.py            # 系统架构师
│   │   ├── injector.py             # 运维专家 (DevOps)
│   │   └── project_manager.py      # 项目经理
│   │
│   ├── core/                       # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── pipeline.py             # 流水线编排器
│   │   ├── project.py              # 项目生成器
│   │   └── stack_detector.py       # 技术栈检测器
│   │
│   ├── adapters/                   # IDE 适配器层（新增）
│   │   ├── __init__.py
│   │   ├── base.py                 # 抽象适配器接口
│   │   ├── antigravity.py          # Google Antigravity 适配器
│   │   ├── claude_code.py          # Claude Code 适配器
│   │   ├── cursor.py               # Cursor 适配器
│   │   └── registry.py             # 适配器注册表
│   │
│   ├── templates/                  # 模板处理层
│   │   ├── __init__.py
│   │   ├── loader.py               # 模板加载器
│   │   ├── renderer.py             # 模板渲染器
│   │   └── validators.py           # 模板验证器
│   │
│   ├── llm/                        # LLM 集成层
│   │   ├── __init__.py
│   │   ├── client.py               # LLM 客户端封装
│   │   ├── parser.py               # 响应解析器
│   │   └── prompts.py              # Prompt 构建器
│   │
│   ├── config/                     # 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py             # 全局配置类
│   │   ├── paths.py                # 路径常量
│   │   └── schema.py               # 配置验证 Schema
│   │
│   └── utils/                      # 工具函数
│       ├── __init__.py
│       ├── files.py                # 文件操作
│       ├── git.py                  # Git 操作
│       └── platform.py             # 跨平台工具
│
├── templates/                      # 模板资源（保持不变）
│   ├── prompts/
│   ├── rules/
│   └── ...
│
├── tests/                          # 测试目录
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_agents.py
│   │   ├── test_pipeline.py
│   │   ├── test_adapters.py
│   │   └── test_templates.py
│   └── integration/
│       ├── test_create_command.py
│       └── test_plan_command.py
│
├── vibe.py                         # 向后兼容入口（调用 vibe.cli）
├── pyproject.toml                  # 现代包管理
├── requirements.txt
└── requirements-dev.txt
```

### 2.2 核心类设计

#### 2.2.1 Agent 抽象基类

```python
# vibe/agents/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentResult:
    """Agent 执行结果"""
    content: str
    filename: str
    success: bool
    raw_response: Optional[str] = None
    error: Optional[str] = None

class BaseAgent(ABC):
    """Agent 抽象基类"""

    def __init__(self, llm_client, template_loader):
        self.llm = llm_client
        self.templates = template_loader

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent 名称"""
        pass

    @property
    @abstractmethod
    def template_name(self) -> str:
        """使用的模板文件名"""
        pass

    @property
    @abstractmethod
    def output_filename(self) -> str:
        """输出文件名"""
        pass

    @abstractmethod
    def build_prompt(self, context: dict) -> str:
        """构建 Prompt"""
        pass

    def execute(self, context: dict) -> AgentResult:
        """执行 Agent 任务"""
        prompt = self.build_prompt(context)
        response = self.llm.generate(prompt, step_name=self.name)
        content = self._parse_response(response)

        return AgentResult(
            content=content or response,
            filename=self.output_filename,
            success=bool(content),
            raw_response=response
        )

    def _parse_response(self, response: str) -> Optional[str]:
        """解析 LLM 响应，提取文件内容"""
        from vibe.llm.parser import extract_file_content
        return extract_file_content(response, self.output_filename)
```

#### 2.2.2 IDE 适配器接口

```python
# vibe/adapters/base.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any

class IDEAdapter(ABC):
    """IDE 适配器抽象基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """IDE 名称"""
        pass

    @property
    @abstractmethod
    def rules_dir_name(self) -> str:
        """规则目录名 (如 .agent/rules, .claude)"""
        pass

    @property
    @abstractmethod
    def global_rules_filename(self) -> str:
        """全局规则文件名 (如 GEMINI.md, CLAUDE.md)"""
        pass

    @abstractmethod
    def get_rules_directory(self, project_dir: Path) -> Path:
        """获取项目规则目录路径"""
        pass

    @abstractmethod
    def get_global_rules_path(self) -> Path:
        """获取用户全局规则文件路径"""
        pass

    @abstractmethod
    def write_rules(self, project_dir: Path, rules: Dict[str, str]) -> None:
        """写入规则文件到项目"""
        pass

    @abstractmethod
    def write_config(self, project_dir: Path, config: Dict[str, Any]) -> None:
        """写入 IDE 特定配置"""
        pass

    @abstractmethod
    def get_supported_features(self) -> List[str]:
        """返回该 IDE 支持的特性列表"""
        pass
```

#### 2.2.3 流水线编排器

```python
# vibe/core/pipeline.py
from dataclasses import dataclass
from typing import List, Optional, Callable
from vibe.agents.base import BaseAgent, AgentResult

@dataclass
class PipelineStage:
    """流水线阶段"""
    agent: BaseAgent
    on_complete: Optional[Callable[[AgentResult], None]] = None
    interactive: bool = False

class Pipeline:
    """四角色流水线编排器"""

    def __init__(self, stages: List[PipelineStage]):
        self.stages = stages
        self.results: List[AgentResult] = []

    def run(self, initial_context: dict, interactive_callback=None) -> List[AgentResult]:
        """执行流水线"""
        context = initial_context.copy()

        for stage in self.stages:
            result = stage.agent.execute(context)
            self.results.append(result)

            # 更新上下文供下一阶段使用
            context[stage.agent.output_filename] = result.content

            if stage.on_complete:
                stage.on_complete(result)

            if stage.interactive and interactive_callback:
                # 交互模式：让用户编辑后重新加载
                result.content = interactive_callback(result)
                context[stage.agent.output_filename] = result.content

        return self.results
```

---

## 3. 重构步骤（渐进式）

### Phase 1: 基础架构 (Week 1)

| 步骤 | 任务 | 验证方式 |
|------|------|----------|
| 1.1 | 创建包结构和 `__init__.py` | `python -c "import vibe"` 成功 |
| 1.2 | 迁移配置常量到 `config/paths.py` | 所有路径引用正常 |
| 1.3 | 提取 `console.py` (Rich 封装) | 彩色输出正常 |
| 1.4 | 保留 `vibe.py` 作为向后兼容入口 | `python vibe.py create` 仍可用 |

### Phase 2: 核心抽象 (Week 2)

| 步骤 | 任务 | 验证方式 |
|------|------|----------|
| 2.1 | 实现 `BaseAgent` 抽象类 | 单元测试通过 |
| 2.2 | 迁移 `call_llm()` 到 `llm/client.py` | LLM 调用正常 |
| 2.3 | 迁移 `extract_file_content()` 到 `llm/parser.py` | 解析测试通过 |
| 2.4 | 实现四个具体 Agent 类 | 各 Agent 可独立运行 |

### Phase 3: 命令重构 (Week 3)

| 步骤 | 任务 | 验证方式 |
|------|------|----------|
| 3.1 | 创建 `Pipeline` 编排器 | 流水线测试通过 |
| 3.2 | 重构 `create` 命令使用 Pipeline | `create` 命令正常 |
| 3.3 | 重构 `plan` 命令 | `plan` 命令正常 |
| 3.4 | 实现模板加载器 | 模板读取测试通过 |

### Phase 4: IDE 适配器 (Week 4)

| 步骤 | 任务 | 验证方式 |
|------|------|----------|
| 4.1 | 实现 `IDEAdapter` 接口 | 接口定义完整 |
| 4.2 | 实现 Antigravity 适配器 | 向后兼容验证 |
| 4.3 | 实现 Claude Code 适配器 | Claude 规则生成正确 |
| 4.4 | 实现适配器注册表 | 多 IDE 切换正常 |

---

## 4. 重构注意事项

### 4.1 向后兼容性

```python
# vibe.py (保留作为入口)
"""
向后兼容入口点。
推荐使用: python -m vibe create ...
"""
import warnings
from vibe.cli.app import app

if __name__ == "__main__":
    warnings.warn(
        "直接运行 vibe.py 已弃用，请使用 'python -m vibe' 或 'vibe' 命令",
        DeprecationWarning
    )
    app()
```

### 4.2 配置迁移策略

```python
# vibe/config/settings.py
from pathlib import Path
from typing import Optional
import os

class Settings:
    """统一配置管理"""

    # 目录常量
    BASE_DIR = Path(__file__).parent.parent.parent
    TEMPLATES_DIR = BASE_DIR / "templates"
    PROMPTS_DIR = TEMPLATES_DIR / "prompts"
    RULES_DIR = TEMPLATES_DIR / "rules"

    # 文件名常量（消除魔法字符串）
    PRODUCT_CONTEXT = "productContext.md"
    SYSTEM_PATTERNS = "systemPatterns.md"
    ACTIVE_CONTEXT = "activeContext.md"
    PROJECT_ENV = "project_env.yaml"

    # IDE 相关
    DEFAULT_IDE = "antigravity"

    @classmethod
    def get_user_config_path(cls) -> Path:
        """获取用户配置路径"""
        if os.path.exists("./config.yaml"):
            return Path("./config.yaml")
        return Path.home() / ".my-llm-sdk" / "config.yaml"
```

### 4.3 测试策略

```python
# tests/conftest.py
import pytest
from pathlib import Path
from unittest.mock import Mock

@pytest.fixture
def mock_llm_client():
    """Mock LLM 客户端"""
    client = Mock()
    client.generate.return_value = """
|||FILE: productContext.md|||
# 测试产品上下文
## 项目目标
测试目标
|||END_FILE|||
"""
    return client

@pytest.fixture
def temp_project_dir(tmp_path):
    """临时项目目录"""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    return project_dir

@pytest.fixture
def sample_context():
    """示例上下文"""
    return {
        "user_request": "创建一个 TODO 应用",
        "project_name": "test-project"
    }
```

### 4.4 错误处理改进

```python
# vibe/core/exceptions.py
class VibeError(Exception):
    """Vibe-CLI 基础异常"""
    pass

class TemplateNotFoundError(VibeError):
    """模板未找到"""
    def __init__(self, template_name: str):
        self.template_name = template_name
        super().__init__(f"模板未找到: {template_name}")

class LLMResponseParseError(VibeError):
    """LLM 响应解析失败"""
    def __init__(self, filename: str, raw_response: str):
        self.filename = filename
        self.raw_response = raw_response
        super().__init__(f"无法从响应中解析 {filename}")

class IDENotSupportedError(VibeError):
    """不支持的 IDE"""
    def __init__(self, ide_name: str, supported: list):
        self.ide_name = ide_name
        self.supported = supported
        super().__init__(f"不支持的 IDE: {ide_name}。支持的 IDE: {supported}")
```

---

# 第二部分：多IDE支持方案

## 1. 当前状态分析

### 1.1 Antigravity 专用设计

| 组件 | 当前设计 | 耦合程度 |
|------|----------|----------|
| 规则目录 | `.agent/rules/` | 硬编码 |
| 全局规则 | `GEMINI.md` → `~/.gemini/` | 硬编码 |
| 配置格式 | Markdown 规则文件 | 低耦合 |

### 1.2 目标 IDE 对比

| 特性 | Antigravity | Claude Code | Cursor |
|------|-------------|-------------|--------|
| 规则目录 | `.agent/rules/` | `.claude/` | `.cursorrules` 或 `.cursor/` |
| 全局规则文件 | `~/.gemini/GEMINI.md` | `~/.claude/CLAUDE.md` | `~/.cursor/rules.md` |
| 项目规则文件 | 多个 `.md` 文件 | `CLAUDE.md` + `settings.json` | `.cursorrules` |
| 配置格式 | Markdown | Markdown + JSON | Markdown |
| 权限系统 | 无 | `settings.json` allow/deny | 无 |

---

## 2. 多IDE适配器设计

### 2.1 适配器实现

#### Antigravity 适配器

```python
# vibe/adapters/antigravity.py
from pathlib import Path
from typing import Dict, List, Any
from .base import IDEAdapter

class AntigravityAdapter(IDEAdapter):
    """Google Antigravity IDE 适配器"""

    @property
    def name(self) -> str:
        return "antigravity"

    @property
    def rules_dir_name(self) -> str:
        return ".agent/rules"

    @property
    def global_rules_filename(self) -> str:
        return "GEMINI.md"

    def get_rules_directory(self, project_dir: Path) -> Path:
        return project_dir / ".agent" / "rules"

    def get_global_rules_path(self) -> Path:
        return Path.home() / ".gemini" / "GEMINI.md"

    def write_rules(self, project_dir: Path, rules: Dict[str, str]) -> None:
        rules_dir = self.get_rules_directory(project_dir)
        rules_dir.mkdir(parents=True, exist_ok=True)

        for filename, content in rules.items():
            (rules_dir / filename).write_text(content, encoding="utf-8")

    def write_config(self, project_dir: Path, config: Dict[str, Any]) -> None:
        # Antigravity 不需要额外配置文件
        pass

    def get_supported_features(self) -> List[str]:
        return ["rules", "context", "plan_workflow"]
```

#### Claude Code 适配器

```python
# vibe/adapters/claude_code.py
from pathlib import Path
from typing import Dict, List, Any
import json
from .base import IDEAdapter

class ClaudeCodeAdapter(IDEAdapter):
    """Claude Code IDE 适配器"""

    @property
    def name(self) -> str:
        return "claude-code"

    @property
    def rules_dir_name(self) -> str:
        return ".claude"

    @property
    def global_rules_filename(self) -> str:
        return "CLAUDE.md"

    def get_rules_directory(self, project_dir: Path) -> Path:
        return project_dir / ".claude"

    def get_global_rules_path(self) -> Path:
        return Path.home() / ".claude" / "CLAUDE.md"

    def write_rules(self, project_dir: Path, rules: Dict[str, str]) -> None:
        """
        Claude Code 使用单一 CLAUDE.md 文件
        需要将多个规则合并为一个文件
        """
        claude_dir = self.get_rules_directory(project_dir)
        claude_dir.mkdir(parents=True, exist_ok=True)

        # 合并所有规则到单一文件
        combined_content = self._merge_rules(rules)
        (project_dir / "CLAUDE.md").write_text(combined_content, encoding="utf-8")

        # 同时保存分离的规则文件（可选，便于管理）
        rules_subdir = claude_dir / "rules"
        rules_subdir.mkdir(exist_ok=True)
        for filename, content in rules.items():
            (rules_subdir / filename).write_text(content, encoding="utf-8")

    def _merge_rules(self, rules: Dict[str, str]) -> str:
        """合并规则文件为 Claude Code 格式"""
        sections = []

        # 定义规则优先级和分组
        priority_order = [
            "00_project_context.md",
            "00a_project_environment.md",
            "00b_llm_integration.md",
            "01_workflow_plan_first.md",
        ]

        # 添加头部
        sections.append("# CLAUDE.md (PROJECT RULES)\n")
        sections.append("This file contains all project rules for Claude Code.\n")
        sections.append("---\n")

        # 按优先级添加规则
        for rule_name in priority_order:
            if rule_name in rules:
                sections.append(f"\n## {rule_name.replace('.md', '').replace('_', ' ').title()}\n")
                sections.append(rules[rule_name])
                sections.append("\n---\n")

        # 添加技术栈规则
        for rule_name, content in rules.items():
            if rule_name.startswith("02_stack_"):
                sections.append(f"\n## Tech Stack: {rule_name}\n")
                sections.append(content)
                sections.append("\n---\n")

        # 添加其他规则
        for rule_name, content in rules.items():
            if rule_name not in priority_order and not rule_name.startswith("02_stack_"):
                sections.append(f"\n## {rule_name}\n")
                sections.append(content)
                sections.append("\n---\n")

        return "\n".join(sections)

    def write_config(self, project_dir: Path, config: Dict[str, Any]) -> None:
        """写入 Claude Code 特定配置"""
        claude_dir = self.get_rules_directory(project_dir)
        claude_dir.mkdir(parents=True, exist_ok=True)

        settings = {
            "permissions": {
                "allow": config.get("allowed_commands", []),
                "deny": config.get("denied_commands", [])
            }
        }

        settings_path = claude_dir / "settings.local.json"
        settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")

    def get_supported_features(self) -> List[str]:
        return ["rules", "context", "plan_workflow", "permissions", "mcp_servers"]

    def generate_mcp_config(self, project_dir: Path, servers: List[Dict]) -> None:
        """生成 MCP 服务器配置（Claude Code 特有）"""
        claude_dir = self.get_rules_directory(project_dir)
        mcp_config = {"mcpServers": servers}

        (claude_dir / "mcp.json").write_text(
            json.dumps(mcp_config, indent=2),
            encoding="utf-8"
        )
```

#### Cursor 适配器

```python
# vibe/adapters/cursor.py
from pathlib import Path
from typing import Dict, List, Any
from .base import IDEAdapter

class CursorAdapter(IDEAdapter):
    """Cursor IDE 适配器"""

    @property
    def name(self) -> str:
        return "cursor"

    @property
    def rules_dir_name(self) -> str:
        return ".cursor"

    @property
    def global_rules_filename(self) -> str:
        return ".cursorrules"

    def get_rules_directory(self, project_dir: Path) -> Path:
        return project_dir / ".cursor"

    def get_global_rules_path(self) -> Path:
        return Path.home() / ".cursor" / "rules.md"

    def write_rules(self, project_dir: Path, rules: Dict[str, str]) -> None:
        """Cursor 使用 .cursorrules 文件"""
        # 合并为单一文件
        combined = self._merge_rules_for_cursor(rules)
        (project_dir / ".cursorrules").write_text(combined, encoding="utf-8")

        # 同时保存到 .cursor 目录（可选）
        cursor_dir = self.get_rules_directory(project_dir)
        cursor_dir.mkdir(exist_ok=True)
        for filename, content in rules.items():
            (cursor_dir / filename).write_text(content, encoding="utf-8")

    def _merge_rules_for_cursor(self, rules: Dict[str, str]) -> str:
        """合并规则为 Cursor 格式"""
        sections = ["# Project Rules for Cursor\n"]

        for rule_name, content in sorted(rules.items()):
            # 移除 YAML frontmatter
            clean_content = self._remove_frontmatter(content)
            sections.append(f"\n## {rule_name}\n")
            sections.append(clean_content)

        return "\n".join(sections)

    def _remove_frontmatter(self, content: str) -> str:
        """移除 Markdown 文件的 YAML frontmatter"""
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content

    def write_config(self, project_dir: Path, config: Dict[str, Any]) -> None:
        # Cursor 不需要额外配置
        pass

    def get_supported_features(self) -> List[str]:
        return ["rules", "context"]
```

### 2.2 适配器注册表

```python
# vibe/adapters/registry.py
from typing import Dict, Type, Optional
from .base import IDEAdapter
from .antigravity import AntigravityAdapter
from .claude_code import ClaudeCodeAdapter
from .cursor import CursorAdapter

class AdapterRegistry:
    """IDE 适配器注册表"""

    _adapters: Dict[str, Type[IDEAdapter]] = {
        "antigravity": AntigravityAdapter,
        "claude-code": ClaudeCodeAdapter,
        "cursor": CursorAdapter,
    }

    # 别名映射
    _aliases: Dict[str, str] = {
        "gemini": "antigravity",
        "claude": "claude-code",
        "vscode": "cursor",  # Cursor 基于 VSCode
    }

    @classmethod
    def get(cls, ide_name: str) -> IDEAdapter:
        """获取适配器实例"""
        normalized = ide_name.lower().strip()

        # 检查别名
        if normalized in cls._aliases:
            normalized = cls._aliases[normalized]

        if normalized not in cls._adapters:
            supported = list(cls._adapters.keys())
            raise IDENotSupportedError(ide_name, supported)

        return cls._adapters[normalized]()

    @classmethod
    def list_supported(cls) -> list:
        """列出所有支持的 IDE"""
        return list(cls._adapters.keys())

    @classmethod
    def register(cls, name: str, adapter_class: Type[IDEAdapter]) -> None:
        """注册自定义适配器"""
        cls._adapters[name.lower()] = adapter_class
```

---

## 3. CLI 接口更新

### 3.1 添加 `--ide` 参数

```python
# vibe/cli/commands/create.py
import typer
from vibe.adapters.registry import AdapterRegistry

@app.command()
def create(
    project_path: str = typer.Argument(...),
    prompt: str = typer.Option(None),
    promptfile: str = typer.Option(None, "--promptfile"),
    interactive: bool = typer.Option(False, "-i", "--interactive"),
    no_plan: bool = typer.Option(False, "--no-plan"),
    ide: str = typer.Option(
        "antigravity",
        "--ide",
        help="目标 IDE (antigravity, claude-code, cursor)",
        show_default=True
    ),
    all_ides: bool = typer.Option(
        False,
        "--all-ides",
        help="为所有支持的 IDE 生成规则"
    ),
):
    """创建新的 AI-Ready 项目"""

    if all_ides:
        adapters = [AdapterRegistry.get(name) for name in AdapterRegistry.list_supported()]
    else:
        adapters = [AdapterRegistry.get(ide)]

    # ... 项目创建逻辑 ...

    for adapter in adapters:
        console.print(f"[dim]生成 {adapter.name} 规则...[/dim]")
        adapter.write_rules(project_dir, rules)
        adapter.write_config(project_dir, config)
```

### 3.2 使用示例

```bash
# 生成 Antigravity 项目（默认）
python -m vibe create my-project --prompt "TODO App"

# 生成 Claude Code 项目
python -m vibe create my-project --prompt "TODO App" --ide claude-code

# 生成 Cursor 项目
python -m vibe create my-project --prompt "TODO App" --ide cursor

# 同时为所有 IDE 生成规则
python -m vibe create my-project --prompt "TODO App" --all-ides
```

---

## 4. 模板系统更新

### 4.1 全局规则模板

```
templates/
├── global_rules/                   # 新增：全局规则模板
│   ├── GEMINI.md                   # Antigravity
│   ├── CLAUDE.md                   # Claude Code (新增)
│   └── CURSORRULES.md              # Cursor (新增)
│
├── prompts/                        # 保持不变
└── rules/                          # 保持不变
```

### 4.2 Claude Code 全局规则模板

```markdown
# templates/global_rules/CLAUDE.md

# CLAUDE.md (GLOBAL RULES)

## 1. 核心角色与语言
- **角色**: 作为 **高级软件工程师** 在 IDE/Agent 工作流中运行
- **技术栈策略**: 不要假设技术栈，根据工作区/项目规则和仓库"真实来源"文件做决策
- **用户语言**: 所有面向用户的解释必须使用**简体中文**，除非用户明确要求其他语言

## 2. 沟通风格
- **结论先行**: 先提供推荐的操作/解决方案，然后再解释
- **实用性**: 优先可执行步骤、具体示例和精确命令
- **无 AI 元对话**: 不要提及模型身份、知识截止日期或"作为 AI..."

## 3. 代码输出规则
- **禁止懒惰代码**: 不要在代码中使用占位符（如 `// ... existing code ...`）
- **完整上下文**: 编辑时输出完整的函数/类/部分，确保 Apply 可以安全工作
- **遵循约定**: 遵循现有的 lint/format 规则

## 4. 安全边界
- **风险警告**: 如果更改具有破坏性（删除/批量重命名/重大重构），明确指出风险并请求确认
- **秘密保护**: 永远不要输出或提交 secrets/API keys/tokens

## 5. 验证与交付
- **自检**: 确保代码语法完整且原则上可运行/编译
- **提供验证步骤**: 提供具体命令来测试/lint/build
```

---

## 5. 生成项目结构对比

### 5.1 Antigravity 项目

```
my-project/
├── .agent/
│   └── rules/
│       ├── 00_project_context.md
│       ├── 00a_project_environment.md
│       ├── 00b_llm_integration.md
│       ├── 01_workflow_plan_first.md
│       ├── 02_stack_python_fastapi.md
│       └── 03_output_format.md
├── .context/
│   ├── productContext.md
│   ├── systemPatterns.md
│   └── activeContext.md
├── plan/
└── ...
```

### 5.2 Claude Code 项目

```
my-project/
├── CLAUDE.md                       # 合并的项目规则
├── .claude/
│   ├── settings.local.json         # 权限配置
│   ├── mcp.json                    # MCP 服务器配置（可选）
│   └── rules/                      # 分离的规则文件（备份）
│       ├── 00_project_context.md
│       └── ...
├── .context/
│   ├── productContext.md
│   ├── systemPatterns.md
│   └── activeContext.md
├── plan/
└── ...
```

### 5.3 Cursor 项目

```
my-project/
├── .cursorrules                    # 合并的项目规则
├── .cursor/
│   ├── 00_project_context.md
│   └── ...
├── .context/
│   ├── productContext.md
│   ├── systemPatterns.md
│   └── activeContext.md
├── plan/
└── ...
```

---

## 6. 迁移指南

### 6.1 从 Antigravity 迁移到 Claude Code

```bash
# 使用 Vibe-CLI 迁移（计划功能）
python -m vibe migrate my-project --from antigravity --to claude-code

# 手动迁移步骤
# 1. 合并 .agent/rules/*.md 到 CLAUDE.md
# 2. 创建 .claude/settings.local.json
# 3. 保留 .context/ 目录（通用）
```

### 6.2 全局规则迁移

| 从 | 到 | 操作 |
|----|----|------|
| `~/.gemini/GEMINI.md` | `~/.claude/CLAUDE.md` | 内容格式调整后复制 |
| `~/.gemini/GEMINI.md` | `~/.cursor/rules.md` | 内容格式调整后复制 |

---

## 7. 实施计划

### Phase 1: 基础适配器 (Week 4)
- [ ] 实现 `IDEAdapter` 抽象接口
- [ ] 完成 `AntigravityAdapter` 实现
- [ ] 添加 `--ide` CLI 参数

### Phase 2: Claude Code 支持 (Week 5)
- [ ] 实现 `ClaudeCodeAdapter`
- [ ] 创建 `CLAUDE.md` 全局规则模板
- [ ] 测试规则合并逻辑
- [ ] 实现 `settings.local.json` 生成

### Phase 3: Cursor 支持 (Week 6)
- [ ] 实现 `CursorAdapter`
- [ ] 创建 `.cursorrules` 模板
- [ ] 测试兼容性

### Phase 4: 高级功能 (Week 7-8)
- [ ] 实现 `--all-ides` 选项
- [ ] 添加 `migrate` 命令
- [ ] 编写文档和示例
- [ ] 集成测试

---

## 8. 注意事项与风险

### 8.1 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 各 IDE 规则格式变更 | 高 | 版本化适配器，关注上游更新 |
| 规则合并导致内容丢失 | 中 | 保留原始分离文件作为备份 |
| 跨平台路径问题 | 中 | 使用 `pathlib`，充分测试 |

### 8.2 兼容性保证

1. **向后兼容**: 默认仍生成 Antigravity 格式
2. **可选迁移**: 不强制用户迁移现有项目
3. **文档完善**: 提供详细的 IDE 差异说明

### 8.3 测试策略

```python
# tests/unit/test_adapters.py
import pytest
from vibe.adapters import AntigravityAdapter, ClaudeCodeAdapter, CursorAdapter

@pytest.mark.parametrize("adapter_class", [
    AntigravityAdapter,
    ClaudeCodeAdapter,
    CursorAdapter,
])
def test_adapter_interface(adapter_class, temp_project_dir):
    """验证所有适配器实现完整接口"""
    adapter = adapter_class()

    assert adapter.name
    assert adapter.rules_dir_name
    assert adapter.global_rules_filename

    rules_dir = adapter.get_rules_directory(temp_project_dir)
    assert isinstance(rules_dir, Path)

def test_claude_code_rules_merge():
    """测试 Claude Code 规则合并"""
    adapter = ClaudeCodeAdapter()
    rules = {
        "00_project_context.md": "# Context",
        "01_workflow.md": "# Workflow",
    }

    merged = adapter._merge_rules(rules)

    assert "# Context" in merged
    assert "# Workflow" in merged
    assert merged.startswith("# CLAUDE.md")
```

---

## 9. 总结

本方案提供了：

1. **代码重构方案**：
   - 将单文件拆分为模块化结构
   - 引入 Agent 抽象、Pipeline 编排、IDE 适配器等设计模式
   - 渐进式迁移策略，保证向后兼容

2. **多 IDE 支持方案**：
   - 设计统一的 `IDEAdapter` 接口
   - 实现 Antigravity、Claude Code、Cursor 三种适配器
   - 支持规则格式转换和合并
   - 提供迁移工具和文档

**预计总工时**: 6-8 周
**优先级**: 重构 > Claude Code 支持 > Cursor 支持

---

*文档版本: v1.0 | 最后更新: 2026-01-18*
