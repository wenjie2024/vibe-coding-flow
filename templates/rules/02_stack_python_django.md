---
description: Python Django Best Practices
globs: *.py
---

# Rule 02: Python Django Best Practices

## Code Style
- Use `black` for formatting.
- Use `isort` for import sorting.
- Use strict type hints where possible.

## Architecture
- Follow standard Django app structure.
- **Models**: Fat models, thin views. Use managers for complex queries.
- **Views**: Prefer Class-Based Views (CBVs) or DRF ViewSets.
- **Services**: Extract complex business logic into `services.py` or `selectors.py`.
- **Settings**: Split settings into `base.py`, `dev.py`, `prod.py`.

## Testing
- Use `pytest-django`.
- Use `factory_boy` for model factories.

## Error Handling
- Use DRF's custom exception handler if using REST Framework.
