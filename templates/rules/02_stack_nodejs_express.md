---
description: Node.js Express Best Practices
globs: *.js, *.ts
---

# Rule 02: Node.js Express Best Practices

## Code Style
- Use `ESLint` + `Prettier`.
- Recommend TypeScript for type safety.

## Architecture
- **Layered Architecture**: Controller -> Service -> Data Access (DAO/Repository).
- **Controllers**: Handle HTTP requests/responses only.
- **Services**: Contain business logic.
- **Middlewares**: Use for cross-cutting concerns (Auth, Logging, Validation).

## Testing
- Use `Jest` or `Mocha`.
- Supertest for integration tests.

## Error Handling
- Use a central error handling middleware.
- Extend `Error` class for AppError.
