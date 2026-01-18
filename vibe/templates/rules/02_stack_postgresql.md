---
description: PostgreSQL Best Practices
globs: *.sql, *.py, *.go
---

# Rule 02: PostgreSQL Best Practices

## Connection Management
- **Pooling**: ALWAYS use a connection pool (e.g., `PgBouncer`, `SQLAlchemy` pool, `pgxpool`).
- **Timeouts**: Set `connect_timeout`, `statement_timeout` to prevent hanging queries.

## Schema Design
- **Keys**: Use `UUID` (v7 preferred for sorting) or `BIGINT` for primary keys.
- **Constraints**: Enforce data integrity at DB level (`NOT NULL`, `FOREIGN KEY`, `CHECK`).
- **Indexes**:
  - Index foreign keys.
  - Use `GIN` for JSONB.
  - Use Partial Indexes (`WHERE ...`) for specific query patterns.

## Performance
- **Explain**: Use `EXPLAIN ANALYZE` to verify query performance.
- **JSONB**: Prefer structured tables over JSONB unless schema is truly dynamic.
- **Batching**: Use batch inserts/updates (`COPY` or bulk insert) even for small batches.

## Security
- **Least Privilege**: Application user should NOT be superuser/owner.
- **SSL**: Enforce `sslmode=verify-full` in production.
