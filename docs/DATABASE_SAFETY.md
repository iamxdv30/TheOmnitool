# Database Safety System

## Overview

This document explains the comprehensive database safety system implemented to prevent data loss, corruption, and silent failures.

## Why This Was Built

### The Problem
Recently, the database appeared "wiped out" with no tables. Investigation revealed:
- Database file existed but was **never initialized** (empty, no tables)
- Migration file had invalid placeholder values
- Migration configuration errors prevented proper initialization
- App started successfully despite broken database
- No automatic backups
- No way to detect the issue until users tried to log in

### The Root Cause
The database was NOT actually wiped by code. It simply was never properly initialized due to:
1. ❌ Migration file with `down_revision='previous_revision_id'` placeholder
2. ❌ Migration designed to ALTER tables (not CREATE from scratch)
3. ❌ Duplicate `render_as_batch` configuration causing TypeError
4. ❌ No validation on app startup
5. ❌ Silent failures with no error reporting

## The Solution: 4-Layer Defense

### Layer 1: Prevention
**Stop bad things from happening**

#### Database Validation on Startup
- File: `main.py` (lines 170-172)
- Checks database exists and has required tables
- Logs clear warnings if schema is invalid
- Uses: `utils/db_safety.py::validate_database_on_startup()`

```python
# SAFETY: Validate database on startup
from utils.db_safety import validate_database_on_startup
validate_database_on_startup(app)
```

**What it does:**
- Checks if database file exists
- Validates all critical tables exist (users, tools, tool_access)
- Counts rows in each table
- Logs health status on every startup

**Example output:**
```
✓ Database health check passed: {'users': 5, 'tools': 4, 'tool_access': 17}
Database status: Database is healthy
```

Or if broken:
```
✗ Database schema invalid! Missing tables: users, tools
DATABASE HEALTH CHECK FAILED: Schema invalid
Run 'python migrate_db.py' to initialize the database
```

#### Migration Validation
- File: `migrate_db.py` (completely rewritten)
- Validates database state before running migrations
- Better error messages with troubleshooting steps
- Exits with error code to fail CI/CD if migration fails

### Layer 2: Protection
**Minimize damage if something goes wrong**

#### Automatic Backups
- File: `migrate_db.py` (lines 64-73)
- Creates backup BEFORE every migration runs
- Only for SQLite (PostgreSQL has its own backup systems)

**Backup process:**
```python
if is_sqlite and DatabaseSafety.database_exists():
    logger.info("[SAFETY] Creating pre-migration backup...")
    success, result = DatabaseSafety.create_backup(backup_reason="pre_migration")
```

**Backup locations:**
- `zzDumpfiles/SQLite Database Backup/users.db` - Latest backup (always)
- `zzDumpfiles/SQLite Database Backup/users.db.backup_pre_migration_20260113_070532` - Timestamped

**What gets backed up:**
- Entire database file
- All tables and data
- Schema and indexes

#### Database Safety Utilities
- File: `utils/db_safety.py`
- Centralized safety operations module

**Key functions:**
- `validate_schema()` - Check if all critical tables exist
- `get_table_counts()` - Get row counts for monitoring
- `create_backup()` - Create timestamped backup
- `get_health_status()` - Comprehensive health check
- `initialize_if_needed()` - Auto-initialize if needed

### Layer 3: Detection
**Know when something is wrong**

#### Health Check Endpoints
- File: `routes/health_routes.py`
- Provides real-time database status monitoring

**Available endpoints:**

1. **GET /health** - Comprehensive health check
   ```bash
   curl http://localhost:5000/health
   ```

   Response:
   ```json
   {
     "status": "healthy",
     "database": {
       "exists": true,
       "schema_valid": true,
       "missing_tables": [],
       "table_counts": {
         "users": 5,
         "tools": 4,
         "tool_access": 17
       }
     },
     "checks": {
       "database_exists": "✓",
       "schema_valid": "✓",
       "has_users": "✓",
       "has_tools": "✓"
     },
     "message": "All systems operational"
   }
   ```

   If broken:
   ```json
   {
     "status": "critical",
     "database": {
       "exists": false,
       "schema_valid": false,
       "missing_tables": ["users", "tools", "tool_access"]
     },
     "message": "Database file does not exist - run migrate_db.py"
   }
   ```

2. **GET /health/ping** - Simple uptime check
   ```bash
   curl http://localhost:5000/health/ping
   ```

   Response: `{"status": "ok", "message": "pong"}`

3. **GET /health/database** - Detailed database stats
   ```bash
   curl http://localhost:5000/health/database
   ```

**Use cases:**
- CI/CD smoke tests
- Load balancer health checks
- Monitoring systems (Datadog, New Relic, etc.)
- Manual debugging

### Layer 4: Recovery
**Fix things when they break**

#### Restore from Backup
- File: `restore_backup.py`
- Restores database from latest backup
- Handles schema differences between backup and current version
- Creates backup before restoration

**Usage:**
```bash
python restore_backup.py
```

**What it does:**
1. Backs up current database (before restoration)
2. Connects to backup database
3. Restores users, admins, tool access, email templates
4. Handles schema differences automatically
5. Validates restoration success

## How This Prevents Future Issues

### Scenario: Empty Database After Migration Failure

**Without Safety System:**
- Migration fails silently
- App starts with empty database
- Users can't log in
- No indication of what's wrong
- Data appears "wiped"

**With Safety System:**
1. ✅ **Backup created** before migration attempt
2. ✅ **Migration fails** with clear error message
3. ✅ **App startup logs** show database is invalid
4. ✅ **/health endpoint** returns 503 Service Unavailable
5. ✅ **Clear recovery steps** in error message
6. ✅ **Backup available** to restore from immediately

### Scenario: Invalid Migration File

**Without Safety System:**
- TypeError: duplicate keyword argument
- Cryptic stack trace
- No clear solution

**With Safety System:**
- Migration fails fast with clear error
- Troubleshooting steps provided:
  ```
  1. Check migrations/versions/ for invalid migration files
  2. Ensure down_revision values are valid
  3. Run 'flask db history' to see migration chain
  4. Check database connectivity
  ```
- Backup already created
- Easy rollback: `python restore_backup.py`

## Monitoring and Alerts

### For Development
Check health on startup:
```bash
python main.py
# Logs will show: "✓ Database health check passed"
```

### For Production
Add to your monitoring system:
```bash
# Check every 5 minutes
*/5 * * * * curl -f https://your-app.herokuapp.com/health || alert_team
```

### For CI/CD
Add to deployment workflow:
```yaml
- name: Health Check
  run: |
    response=$(curl -s http://localhost:5000/health)
    status=$(echo $response | jq -r '.status')
    if [ "$status" != "healthy" ]; then
      echo "Health check failed: $response"
      exit 1
    fi
```

## Backup Strategy

### Automatic Backups
- **When:** Before every migration
- **Where:** `zzDumpfiles/SQLite Database Backup/`
- **Format:** `users.db.backup_pre_migration_YYYYMMDD_HHMMSS`
- **Retention:** Manual cleanup (keep 7 days recommended)

### Manual Backups
```bash
# Using db_safety utilities
python -c "from utils.db_safety import DatabaseSafety; DatabaseSafety.create_backup(backup_reason='manual')"

# Or simple file copy
cp instance/users.db zzDumpfiles/SQLite\ Database\ Backup/users.db.manual_$(date +%Y%m%d_%H%M%S)
```

### Backup Locations
1. **Primary backup** (latest): `zzDumpfiles/SQLite Database Backup/users.db`
2. **Pre-migration backups**: `zzDumpfiles/SQLite Database Backup/users.db.backup_pre_migration_*`
3. **Pre-restore backups**: `instance/users.db.before_restore_*`

## Troubleshooting Guide

### Problem: "Database file does not exist"
**Solution:**
```bash
python migrate_db.py
```

### Problem: "Schema invalid - missing tables"
**Solution:**
```bash
python migrate_db.py  # Will create tables
```

### Problem: "Data lost or corrupted"
**Solution:**
```bash
python restore_backup.py  # Restores from latest backup
```

### Problem: "Migration failed"
**What happened:** Backup was created automatically

**Solution:**
```bash
# Option 1: Fix the migration and try again
# Check error message for specific issue
python migrate_db.py

# Option 2: Restore from backup
python restore_backup.py
```

### Problem: "/health returns 503"
**Meaning:** Database is not healthy

**Check the response:**
```bash
curl http://localhost:5000/health | jq
```

**Follow the message** - it will tell you exactly what's wrong

## Best Practices

### For Developers
1. Always test migrations locally first
2. Check `/health` after migrations
3. Keep backups for at least 7 days
4. Run `python migrate_db.py` not `flask db upgrade` (for automatic backups)

### For Production
1. Use PostgreSQL (better reliability)
2. Monitor `/health` endpoint continuously
3. Set up alerts on health check failures
4. Use Heroku's database backups

### For CI/CD
1. Run smoke tests that check `/health`
2. Fail deployment if health check fails
3. Keep migration logs
4. Test restore procedure regularly

## Summary

The database safety system provides **4 layers of protection**:

1. **Prevention** - Validate before problems occur
2. **Protection** - Automatic backups before risky operations
3. **Detection** - Health endpoints to know when something's wrong
4. **Recovery** - Easy restoration from backups

**Key Commands:**
```bash
# Check health
curl http://localhost:5000/health

# Run migration (with backup)
python migrate_db.py

# Restore from backup
python restore_backup.py
```

**Result:** Database issues are now:
- ✅ Prevented by validation
- ✅ Protected by automatic backups
- ✅ Detected by health checks
- ✅ Recoverable with one command

This system ensures that what happened (empty database, unclear errors, no backup) **cannot happen again**.
