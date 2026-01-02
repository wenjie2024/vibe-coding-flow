# 项目环境配置指南 (Project Setup Guide)

本指南将帮助您配置本项目运行所需的环境，确保符合 **Rule 00a** 和 **Rule 00b** 的规范。

## 1. 准备工作
- 已安装 **Miniconda** 或 **Anaconda**。

## 2. 基础设施配置 (一次性 / 每个项目)

我们使用 **Conda 环境变量 (Conda Environment Variables)** 来安全地定位 SDK，避免修改系统级设置。

### 步骤 2.1: 创建并激活环境
打开终端 (Windows 推荐使用 Powershell)，运行以下命令：

```bash
```bash
# 创建环境 (请将 <your_conda_env> 替换为您想要的名称)
conda create -n <your_conda_env> python=3.10 -y

# 激活环境
conda activate <your_conda_env>
```

> **⚠️ 关键提示**: 项目初始化时 `.context/project_env.yaml` 默认预填了 `conda_env: {{project_name}}`。
> 如果您使用了不同的环境名称，**必须**手动修改该文件，使其与您真实创建的环境保持一致！

### 步骤 2.2: 安装 SDK 与依赖
由于 SDK 尚未发布到 PyPI，请直接从 GitHub 安装：

```bash
# 1. 安装 my-llm-sdk
pip install git+https://github.com/NoneSeniorEngineer/my-llm-sdk.git

# 2. 安装项目其他依赖
# pip install -r requirements.txt
```

### 步骤 2.4: SDK 初始化
如果您尚未全局配置过 SDK，请执行初始化。

```bash
python -m my_llm_sdk.cli init
```

**操作说明:**
- 此命令是**交互式**的。
- 此时您需要配置 **Providers** (例如 OpenAI, Google, Azure, 或本地 Ollama)。
- 请提前准备好您的 **API Key (密钥)** 和 **Base URL (接口地址)**。
- 初始化完成后，会自动在您的用户目录下生成 `config.yaml` 配置文件。

## 3. 配置验证

### 步骤 3.1: 检查 `.context/project_env.yaml`
确保项目根目录下存在此文件，且内容与您的设置一致：

```yaml
conda_env: {{project_name}}           # 必须与您的 conda 环境名一致
```

## 4. 预检 (Preflight Check)

运行以下命令进行自检。如果通过，您就可以开始从容编码了！

```bash
# 一键运行环境体检:
conda run -n <your_conda_env> python preflight.py
```

✅ **成功标志**:
- 所有检查项显示绿色 [green]✅[/green]
- 这里的 LLM Connectivity 显示 "Connectivity Success!"
