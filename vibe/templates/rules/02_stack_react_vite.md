---
description: React Vite Best Practices
globs: *.jsx, *.tsx, *.js, *.ts
---

# Rule 02: React (Vite) Best Practices

## Code Style
- Use `ESLint` + `Prettier`.
- Functional Components + Hooks (No Class Components).

## Architecture
- **Feature-based structure**: `src/features/Auth`, `src/features/Dashboard`.
- **Components**: `src/components/ui` (Basic), `src/components/layout`.
- **State**: Use Context API for simple global state, or Zustand/Redux for complex.
- **Hooks**: Custom hooks for logic reuse `src/hooks`.

## Testing
- `Vitest` + `React Testing Library`.

## Performance
- Use `React.memo`, `useMemo`, `useCallback` judiciously.
- Code splitting with `React.lazy`.
