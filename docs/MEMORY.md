# Development Memory & Learnings

## PostgreSQL Migration (2026-02-05)

### Issue Encountered
**Problem**: System environment variables (`DATABASE_URL`, `DATABASE_URL_LOCAL`) were overriding `.env` file settings, causing malformed database connection strings.

**Symptom**:
- Error: `could not translate host name "172530@localhost" to address`
- The malformed URL: `postgresql://postgres:iamxdv@172530@localhost/omnitool`
- Expected URL: `postgresql://omnitool:omnitool_dev@localhost:5432/omnitool_dev`

**Root Cause**:
- Windows system environment variables take precedence over `.env` file
- `python-dotenv` doesn't override existing environment variables by default
- Restarting terminal is NOT enough - must restart entire IDE

**Solution**:
1. Delete system environment variables via Windows System Properties (`sysdm.cpl` → Environment Variables)
2. Restart VSCode completely (not just terminal)
3. Verify with: `python -c "import os; print(os.environ.get('DATABASE_URL', 'NOT SET'))"`

### Migration Workflow Success

**Correct sequence for SQLite → Docker PostgreSQL migration:**

1. **Export SQLite data** (optional but recommended):
   ```bash
   python scripts/migrate_sqlite_to_postgres.py --export
   ```

2. **Ensure Docker PostgreSQL is running**:
   ```bash
   docker ps --filter "name=omnitool-postgres"
   ```

3. **Create PostgreSQL schema** (empty tables):
   ```bash
   python migrate_db.py
   ```

4. **Import data to PostgreSQL**:
   ```bash
   python scripts/migrate_sqlite_to_postgres.py --import
   ```

5. **Verify migration**:
   ```bash
   python scripts/migrate_sqlite_to_postgres.py --verify
   ```

**Key Learnings**:
- `migrate_db.py` = Schema migration (creates tables/columns via Alembic)
- `scripts/migrate_sqlite_to_postgres.py` = Data migration (moves records between databases)
- Schema must exist BEFORE importing data
- Missing `psycopg2-binary` package will cause `No module named 'psycopg2'` error

### Dependencies Added
- `psycopg2-binary==2.9.11` - PostgreSQL adapter for Python (required for SQLAlchemy + PostgreSQL)

### Environment Variable Hierarchy
1. **System environment variables** (highest priority - can override everything)
2. **User environment variables**
3. **IDE/Shell session variables**
4. **`.env` file** (lowest priority - only used if not already set)

**Recommendation**: Never set `DATABASE_URL` as system/user environment variable in development. Let `.env` file handle it.

## Best Practices Established

### Database Development
- ✅ Use Docker PostgreSQL for local dev (matches staging/production)
- ✅ Keep `USE_DOCKER_DB=true` in `.env`
- ✅ Avoid SQLite for development (causes migration issues due to behavioral differences)
- ✅ Always run `migrate_db.py` before importing data

### Migration Safety
- ✅ Always export data before major changes
- ✅ Verify migration with `--verify` flag
- ✅ Check Docker container status before migrations
- ✅ Use JSON backups for PostgreSQL (more portable than binary dumps)

### Common Gotchas
- Environment variables persist across terminal restarts - must restart IDE
- Malformed DATABASE_URL often comes from system environment variables
- Port `:5432` is required in PostgreSQL connection strings
- Special characters in passwords must be URL-encoded (e.g., `@` → `%40`)
