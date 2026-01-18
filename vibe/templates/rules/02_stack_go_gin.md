---
description: Go Gin Best Practices
globs: *.go
---

# Rule 02: Go (Gin) Best Practices

## Code Style
- Standard `gofmt` / `goimports`.
- Follow "Effective Go".

## Architecture
- **Standard Layout**: `cmd/`, `internal/`, `pkg/`, `api/`.
- **Handlers**: HTTP layer (`internal/handlers`).
- **Service**: Business logic (`internal/service`).
- **Repository**: Data access (`internal/repository`).
- **Configuration**: Use `viper` or standard environment variables.

## Testing
- Use standard `testing` package + `testify`.
- Table-driven tests.

## Error Handling
- Return errors explicitly (no panics).
- Wrap errors with context.
