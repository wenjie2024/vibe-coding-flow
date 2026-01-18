---
description: Standards for LLM integration, forbidding direct vendor SDK usage.
---
# Rule 00b: LLM Integration Standards

This rule governs all AI/LLM capability integration code.

## 1. The ONLY Valid Entry Point
You **MUST** use the `my_llm_sdk` for all LLM interactions.

- **✅ Correct:**
  ```python
  from my_llm_sdk.client import LLMClient
  
  client = LLMClient()
  text = client.generate("Hello", model_alias="gemini-2.5-flash")
  ```
  *Configuration MUST be initialized via `python -m my_llm_sdk.cli init` and loaded by SDK config mechanism (e.g. `llm.project.yaml` found in structure).*

- **❌ PROHIBITED:**
  ```python
  import openai
  import google.generativeai
  import dashscope
  from langchain_openai import ChatOpenAI
  # Do not use HTTP requests to call LLM APIs directly
  ```

## 2. Model Configuration
- **NEVER** hardcode vendor model IDs (e.g., `gpt-4`, `gemini-1.5-pro`) in your business logic.
- **ALWAYS** use `model_alias` that is defined in the SDK project registry/config (e.g., `llm.project.yaml`).

> **Constraint**: If using `default/fast/complex`, they MUST be defined in `llm.project.yaml` (registry/mapping). Otherwise use explicit aliases like `gemini-2.5-flash` that are supported by the SDK.

## 3. Recommended Patterns
- **Streaming**: Prefer `client.stream()` for user-facing interactions to reduce perceived latency.
- **Async**: Use `client.generate_async()` for batch processing or background tasks.
- **Budgeting**: Budgeting MUST be enforced by my-llm-sdk via its configuration files (e.g., `config.yaml` / `llm.project.yaml`). Do not implement budget checks in business code.

## 4. Usage/Cost Accounting (MUST)
If you need token/cost/provider/model/latency, you MUST use `full_response=True` and read from the SDK’s structured response.

```python
response = client.generate("Prompt", full_response=True)
print(f"Cost: {response.cost}, Tokens: {response.usage.total_tokens}")
```

## 5. Wrapper Policy
You MAY wrap `LLMClient` in a thin project helper (e.g., `llm.py`), but the wrapper MUST only call my-llm-sdk and MUST NOT import vendor SDKs.

---
**Enforcement**: Any code violating these imports or patterns must be rejected during review.
