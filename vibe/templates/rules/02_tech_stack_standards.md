# Rule 02: Tech Stack Standards

## Core Principle: Standardize & Simplify
Use the project's standard libraries and tools. Do not invent new wheels or introduce external dependencies unless absolutely necessary.

## 1. LLM Integration
**Constraint**: You MUST use `my-llm-sdk` for all LLM interactions.
- **Do NOT** use `openai`, `anthropic`, or `google-generativeai` libraries directly.
- **Do NOT** implement custom HTTP requests for LLM APIs.

### SDK Mini-Reference (my-llm-sdk)

> **Context**: Efficient, unified LLM client with budget tracking and proxy bypass for China regions.

#### A. Initialization
Always use the Singleton-like pattern or simple instantiation. Config is loaded automatically from `llm.project.yaml` or `config.yaml`.

```python
from my_llm_sdk.client import LLMClient
from my_llm_sdk.schemas import ContentInput

# Initialize client (auto-loads config)
client = LLMClient()
```

#### B. Generation (Sync & Async)
Supports Text, Image, and Multimodal inputs.

**Standard Text Generation**:
```python
# Simple text
response = client.generate(prompt="Explain quantum physics in 50 words.")
print(response) # Returns string content directly
```

**Async Support**:
```python
response = await client.generate_async(prompt="Hello")
```

**JSON Output (if model supports)**:
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

# Note: Check model capability for JSON mode first
response = client.generate(
    prompt="Generate a user",
    config={"response_mime_type": "application/json"}
)
```

#### C. Streaming
Always provide visual feedback for long-running tasks.

```python
stream = client.stream(prompt="Write a long story...")
for event in stream:
    if event.delta:
        print(event.delta, end="", flush=True)
```

## 2. Environment Variables
- **Constraint**: Do NOT hardcode API keys.
- **Source**: Keys are managed via `config.yaml` or Environment Variables (`GEMINI_API_KEY`, etc.).
- **Code Access**: The SDK handles auth automatically. You usually do not need to read `os.environ` manualy for keys.

## 3. Best Practices
- **Error Handling**: Wrap LLM calls in `try...except` to catch `RuntimeError` (API errors) or `ConfigurationError`.
- **Budget**: The SDK tracks tokens automatically. No manual logging needed.
