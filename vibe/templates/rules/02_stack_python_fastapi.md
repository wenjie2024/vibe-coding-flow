---
description: Python FastAPI Best Practices
globs: *.py
---

# Rule 02: Python FastAPI Best Practices

## Code Style
- Use `black` for formatting.
- Use `isort` for import sorting.
- Use strict type hints (`typing.List`, `typing.Optional`, etc. or standard `list`, `dict` in Python 3.9+).

## Architecture
- **Routers**: Split routes into `app/routers/`.
- **Schemas**: Use Pydantic models in `app/schemas/`.
- **Models**: Database models in `app/models/`.
- **CRUD**: specific DB operations in `app/crud/`.

## Testing
- Use `pytest`.
- Create tests in `tests/` directory.

## Error Handling
- Use global exception handlers in `main.py`.
- Custom exceptions should inherit from detailed base classes.
