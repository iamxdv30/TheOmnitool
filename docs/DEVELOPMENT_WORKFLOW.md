# Development Workflow Guide

## Complete Development → Staging → Production Pipeline

This guide covers the enhanced workflow with tool_access synchronization, verification checks, and safe migration practices.

---

## Overview of Changes

### What's New (After Enhancement)
1. **Tool access permissions sync across environments** (solves "User A excluded" problem)
2. **Post-deployment verification** (catches migration issues early)
3. **Optional production data sync to staging** (realistic testing)
4. **Automated backup before deployments**
5. **Fixed sync_tools.py** (handles renames and deletions correctly)

### What Stayed the Same
- Schema migrations via Flask-Migrate (Alembic)
- Tool definitions in sync_tools.py (DEFINED_TOOLS)
- Manual PR for production deployment
- Git-based deployment via CI/CD

---

## Daily Development Workflow

### Scenario 1: Add a New Tool with Custom Permissions

**Example**: Add "Invoice Generator" tool, grant to all users EXCEPT user_a

#### Step 1: Define the Tool (Local Development)

Edit `sync_tools.py` and add to DEFINED_TOOLS:

```python
DEFINED_TOOLS = [
    # ... existing tools ...
    {
        "name": "Invoice Generator",
        "description": "Generate PDF invoices",
        "route": "/invoice_generator",
        "is_default": False,  # Not auto-assigned to new users
        "is_active": True
    }
]
```

#### Step 2: Create Tool in Local Database

```bash
python sync_tools.py
```

**Expected Output**:
```
Creating new tool: Invoice Generator
Tool Synchronization Completed.
```

#### Step 3: Grant Access via Admin UI

1. Start local app: `python main.py`
2. Login as admin → **User Management**
3. Grant "Invoice Generator" to all users EXCEPT user_a
4. Verify in local app that user_a cannot see the tool

#### Step 4: Export Tool Access Permissions

```bash
python scripts/export_tool_access.py --env local
```

**Expected Output**:
```
[SUCCESS] Successfully exported 18 grants to data/tool_access_exports/local_tool_access.json
```

**What this does**: Captures the exact permission state (all users except user_a have access) to version-controlled JSON

#### Step 5: Verify Locally

```bash
python scripts/verify_migration.py --env local
```

**Expected**: All checks pass (or warnings only, no failures)

#### Step 6: Commit and Push to Development Branch

```bash
git add sync_tools.py data/tool_access_exports/local_tool_access.json
git commit -m "feat(tools): Add Invoice Generator with custom permissions"
git push origin development
```

#### Step 7: Automated CI/CD (GitHub Actions)

**What happens automatically**:

1. **Tests run** (pytest)
2. **Staging backup** created
3. **Optional**: Production data synced to staging (if enabled)
4. **Code deployed** to Heroku staging
5. **Config vars updated**
6. **Database migrations run**:
   - `python migrate_db.py` (runs Flask-Migrate + sync_tools.py)
7. **Tool access imported**:
   - `heroku run python scripts/import_tool_access.py --source data/tool_access_exports/local_tool_access.json --mode merge`
8. **Verification runs**:
   - `heroku run python scripts/verify_migration.py --env staging`

**View Progress**:
- GitHub Actions tab: [https://github.com/XDV-TheBulwarksProject/MyTools/actions](https://github.com/XDV-TheBulwarksProject/MyTools/actions)

#### Step 8: Manual QA on Staging

```bash
# Open staging app
heroku open -a omnitool-by-xdv-staging

# Check logs if needed
heroku logs --tail -a omnitool-by-xdv-staging
```

**Verify**:
- ✅ Invoice Generator appears in all users' dashboards EXCEPT user_a
- ✅ user_a cannot see the tool
- ✅ Tool functionality works correctly

#### Step 9: Deploy to Production (Manual)

**Option A: Create Pull Request**

```bash
# From development branch, create PR to main
git checkout main
git pull origin main
git merge development
git push origin main
```

GitHub Actions will automatically deploy to production (if deploy_production.yml is active)

**Option B: Manual Heroku Deploy** (if production workflow not yet active)

```bash
# Backup production first
heroku pg:backups:capture -a omnitool-by-xdv

# Deploy
git push heroku main:main --force

# Run migrations
heroku run python migrate_db.py -a omnitool-by-xdv

# Import tool access
heroku run python scripts/import_tool_access.py \
  --source data/tool_access_exports/local_tool_access.json \
  --mode merge \
  -a omnitool-by-xdv

# Verify
heroku run python scripts/verify_migration.py --env production -a omnitool-by-xdv
```

#### Step 10: Monitor Production

```bash
heroku logs --tail -a omnitool-by-xdv
```

---

### Scenario 2: Rename a Tool

**Example**: Rename "Email Templates management" → "Email Templates"

#### Step 1: Update DEFINED_TOOLS

Edit `sync_tools.py`:

```python
DEFINED_TOOLS = [
    # ... other tools ...
    {
        "name": "Email Templates",  # NEW NAME
        "description": "Create and manage email templates",
        "route": "/email_templates",
        "is_default": True,
        "is_active": True
    }
]
```

#### Step 2: Add Deprecation Mapping

Edit `sync_tools.py`:

```python
DEPRECATED_TOOLS = {
    # ... existing mappings ...
    "Email Templates management": "Email Templates"  # Old -> New
}
```

#### Step 3: Run Sync Locally

```bash
python sync_tools.py
```

**What happens**:
1. Migrates all tool_access records from old name to new name
2. Deletes old tool
3. Creates new tool with correct name

#### Step 4: Export and Commit

```bash
python scripts/export_tool_access.py --env local
git add sync_tools.py data/tool_access_exports/local_tool_access.json
git commit -m "refactor(tools): Rename Email Templates management to Email Templates"
git push origin development
```

**CI/CD handles the rest** (same as Scenario 1)

---

### Scenario 3: Delete a Tool

**Example**: Remove "Old Calculator" tool completely

#### Step 1: Remove from DEFINED_TOOLS

Edit `sync_tools.py` and DELETE the tool definition:

```python
DEFINED_TOOLS = [
    # ... other tools ...
    # "Old Calculator" removed
]
```

#### Step 2: Add to DEPRECATED_TOOLS (with None target)

```python
DEPRECATED_TOOLS = {
    # ... existing mappings ...
    "Old Calculator": None  # Delete without migration
}
```

#### Step 3: Run Sync Locally

```bash
python sync_tools.py
```

**What happens**:
1. All tool_access records for "Old Calculator" are deleted
2. Tool is removed from database

#### Step 4: Export and Commit

```bash
python scripts/export_tool_access.py --env local
git add sync_tools.py data/tool_access_exports/local_tool_access.json
git commit -m "chore(tools): Remove deprecated Old Calculator tool"
git push origin development
```

---

### Scenario 4: Schema Change (Add Column to User Table)

**Example**: Add `phone_number` column to users table

#### Step 1: Update Model

Edit `model/users.py`:

```python
class User(db.Model):
    # ... existing columns ...
    phone_number = db.Column(db.String(20), nullable=True)
```

#### Step 2: Create Migration

```bash
flask db migrate -m "Add phone_number to users"
```

**Review the migration** in `migrations/versions/` to ensure it's correct

#### Step 3: Apply Locally

```bash
flask db upgrade
```

#### Step 4: Test Locally

Verify the column exists:

```bash
python -c "from model import User; from main import create_app; app = create_app(); app.app_context().push(); print(User.__table__.columns.keys())"
```

#### Step 5: Commit and Push

```bash
git add model/users.py migrations/versions/
git commit -m "feat(users): Add phone_number field"
git push origin development
```

**CI/CD runs migrations automatically** via `migrate_db.py`

---

## CI/CD Pipeline Details

### Staging Deployment (`.github/workflows/deploy.yml`)

**Triggered by**: Push to `development` branch

**Steps Performed**:

1. **Checkout code**
2. **Set up Python 3.13**
3. **Install dependencies**
4. **Run tests** (`pytest`)
5. **Backup staging database**
6. **Optional: Sync production data to staging** (commented out, requires Standard tier)
7. **Deploy to Heroku staging**
8. **Update config vars**
9. **Run database migrations** (`migrate_db.py` → runs Flask-Migrate + sync_tools.py)
10. **Import tool access** (from `local_tool_access.json`)
11. **Verify migration** (`verify_migration.py`)

**Estimated Time**: 2-3 minutes

### Production Deployment (`.github/workflows/deploy_production.yml`)

**Status**: ✅ ACTIVE (Priority 3 complete)

**Triggered by**:
- PR merge to `main` branch (requires PR approval)
- Manual workflow dispatch (from GitHub Actions UI)

**Safety Features**:
1. **Manual approval gate** (GitHub Environment protection)
2. **Production backup before any changes** (automatic)
3. **Pre-rollback safety net** (backup before rollback)
4. **Smoke tests after deployment** (catches issues immediately)
5. **Verification checks** (8 comprehensive checks)
6. **Merge mode only** (never overwrites existing permissions)
7. **Automatic cleanup** (keeps last 10 backups)

**Steps Performed**:
1. **Safety gate**: Verify PR was merged (not just closed)
2. **Checkout main branch** (always from main)
3. **Production deployment notice** (commit, actor, timestamp logged)
4. **Backup production database** (CRITICAL - cannot be skipped by default)
5. **Deploy code to Heroku**
6. **Update config vars**
7. **Run database migrations** (`migrate_db.py` → Flask-Migrate + sync_tools.py)
8. **Import tool access** (merge mode only, from tested dev export)
9. **Verify migration** (`verify_migration.py` - fails deployment if checks fail)
10. **Run smoke tests** (`smoke_tests.py` - validates app is functional)
11. **Cleanup old backups** (keep last 10)
12. **Deployment summary** (success/failure with rollback instructions)

**Estimated Time**: 5-8 minutes (includes backup, deployment, verification, smoke tests)

---

## Script Reference

### `sync_tools.py`

**Purpose**: Synchronize tool definitions from code to database

**When to run**:
- After adding/removing/renaming tools in DEFINED_TOOLS
- Automatically runs as part of `migrate_db.py`

**Usage**:
```bash
python sync_tools.py
```

**What it does**:
1. Handles deprecation FIRST (migrates tool_access, deletes old tools)
2. Creates/updates tools from DEFINED_TOOLS
3. Never deletes tools not in DEPRECATED_TOOLS (safe by default)

---

### `scripts/export_tool_access.py`

**Purpose**: Export tool_access permissions to version-controlled JSON

**When to run**: After granting/revoking tool access in admin UI

**Usage**:
```bash
python scripts/export_tool_access.py --env local
python scripts/export_tool_access.py --env local --output custom_path.json
```

**Output**: `data/tool_access_exports/local_tool_access.json`

**Commit this file to git** to sync permissions across environments

---

### `scripts/import_tool_access.py`

**Purpose**: Import tool_access permissions from JSON export

**When to run**:
- Manually to sync permissions to staging/production
- Automatically in CI/CD

**Usage**:
```bash
# Dry-run (preview changes)
python scripts/import_tool_access.py \
  --source data/tool_access_exports/local_tool_access.json \
  --mode merge \
  --dry-run

# Apply changes (merge mode - safe, default)
python scripts/import_tool_access.py \
  --source data/tool_access_exports/local_tool_access.json \
  --mode merge

# Overwrite mode (dangerous - requires confirmation)
python scripts/import_tool_access.py \
  --source data/tool_access_exports/local_tool_access.json \
  --mode overwrite \
  --confirm
```

**Modes**:
- **merge** (default): Adds new grants, preserves existing, never deletes
- **overwrite**: Deletes all existing grants, replaces with export (destructive)

**Safety**: Merge mode is idempotent (safe to run multiple times)

---

### `scripts/verify_migration.py`

**Purpose**: Post-deployment health checks

**When to run**: After migrations (automatically in CI/CD)

**Usage**:
```bash
python scripts/verify_migration.py --env local
python scripts/verify_migration.py --env staging --verbose
heroku run python scripts/verify_migration.py --env production -a omnitool-by-xdv
```

**Checks**:
1. Database connectivity
2. Schema version (Alembic)
3. Tool definitions match DEFINED_TOOLS
4. No orphaned tool_access (invalid tools)
5. No orphaned tool_access (invalid users)
6. Default tools assigned to all users
7. Table counts
8. Application imports correctly

**Exit Codes**:
- 0: All checks passed (warnings allowed)
- 1: Critical check failed

---

### `scripts/sync_data_prod_to_staging.py`

**Purpose**: Refresh staging database with production data

**When to run**: Before testing major changes (optional)

**Usage**:
```bash
# Dry-run
python scripts/sync_data_prod_to_staging.py --dry-run

# Execute
python scripts/sync_data_prod_to_staging.py

# Check follower status
python scripts/sync_data_prod_to_staging.py --check-status
```

**Requirements**: Heroku Postgres Standard tier ($50+/month) for follower support

**What it does**:
1. Backs up staging database
2. Creates follower from production
3. Waits for sync (typically 1-5 minutes)
4. Unfollows (detaches from production)
5. Promotes follower to staging's DATABASE_URL
6. Verifies data integrity

**When enabled in CI/CD**: Staging always tests against production-like data

---

### `scripts/rollback_migration.py` (Priority 3)

**Purpose**: Emergency database restoration from backups

**When to run**: After failed migrations or to undo deployment

**Usage**:
```bash
# Rollback staging to latest backup
python scripts/rollback_migration.py --env staging

# Rollback production to specific backup
python scripts/rollback_migration.py --env production --backup b123

# Rollback local from file
python scripts/rollback_migration.py --env local --file data/backups/users_20260112.db

# Dry-run mode (preview without executing)
python scripts/rollback_migration.py --env production --backup b123 --dry-run
```

**Safety Features**:
1. Creates pre-rollback backup (safety net)
2. Validates backup exists before restore
3. Production requires explicit confirmation ("ROLLBACK PRODUCTION")
4. Verifies database accessibility after restoration
5. Transaction-safe operations

**Exit Codes**:
- 0: Rollback successful
- 1: Rollback failed (error logged)

---

### `tests/smoke_tests.py` (Priority 3)

**Purpose**: Post-deployment health checks (fast, critical tests)

**When to run**:
- Automatically after staging/production deployment (in CI/CD)
- Manually after manual deployments

**Usage**:
```bash
# Test staging
python tests/smoke_tests.py --url https://omnitool-by-xdv-staging.herokuapp.com

# Test production
python tests/smoke_tests.py --url https://omnitool-by-xdv.herokuapp.com

# Test local
python tests/smoke_tests.py --url http://localhost:5000
```

**Tests Performed** (< 30 seconds total):
1. Homepage loads (200 OK)
2. Login page loads (200 OK)
3. Health endpoint (if exists)
4. Static assets load (CSS, JS)
5. Database connectivity
6. No recent 5xx errors

**Exit Codes**:
- 0: All smoke tests passed
- 1: One or more tests failed (deployment may have issues)

---

## Safety and Rollback

### Pre-Deployment Safety

1. **Always test locally first** before pushing to staging
2. **Run verification** locally: `python scripts/verify_migration.py --env local`
3. **Use dry-run** for import operations: `--dry-run` flag
4. **Commit tool_access exports** to git for audit trail

### Automatic Protections

1. **Database backups** before every staging/production deployment
2. **Transaction rollback** on any error (atomic operations)
3. **Merge mode default** (never deletes data accidentally)
4. **Idempotent scripts** (safe to re-run)

### Manual Rollback (If Needed)

#### Option 1: Use Rollback Script (Recommended)

```bash
# Rollback staging to latest backup
python scripts/rollback_migration.py --env staging

# Rollback production to specific backup (requires confirmation)
python scripts/rollback_migration.py --env production --backup b123

# Dry-run first to preview
python scripts/rollback_migration.py --env production --backup b123 --dry-run
```

**What it does**:
- Creates safety net backup before rollback
- Validates backup exists
- Restores database from backup
- Verifies restoration success
- Provides clear rollback instructions

#### Option 2: Manual Heroku Restore

```bash
# List available backups
heroku pg:backups -a omnitool-by-xdv

# Restore specific backup
heroku pg:backups:restore b123 DATABASE_URL -a omnitool-by-xdv --confirm omnitool-by-xdv
```

#### Option 3: Rollback Schema Migration Only

```bash
# Local
flask db downgrade

# Staging
heroku run flask db downgrade -a omnitool-by-xdv-staging

# Production
heroku run flask db downgrade -a omnitool-by-xdv
```

**Note**: This only rolls back schema changes, not data changes.

#### Option 4: Rollback Code Deployment Only

```bash
# Heroku rollback to previous release
heroku releases:rollback -a omnitool-by-xdv
```

**Note**: This only rolls back code, not database changes.

---

## Troubleshooting

### Tool Access Not Syncing to Staging

**Symptom**: User A excluded in dev, but has access in staging

**Diagnosis**:
```bash
# Check what's in staging
heroku run python scripts/export_tool_access.py --env staging --output /tmp/staging_export.json -a omnitool-by-xdv-staging
heroku run cat /tmp/staging_export.json -a omnitool-by-xdv-staging
```

**Fix**:
```bash
# Re-import from local export
heroku run python scripts/import_tool_access.py \
  --source data/tool_access_exports/local_tool_access.json \
  --mode merge \
  -a omnitool-by-xdv-staging
```

---

### Tool Name Mismatch

**Symptom**: Verification shows "Missing: Tool A. Extra: Tool B"

**Diagnosis**: Tool was renamed but deprecation mapping missing

**Fix**:
1. Add to DEPRECATED_TOOLS: `"Tool B": "Tool A"`
2. Run `python sync_tools.py` locally
3. Export and commit: `python scripts/export_tool_access.py --env local`
4. Push to development branch

---

### Orphaned Tool Access Records

**Symptom**: Verification shows "Orphaned tool_access records"

**Diagnosis**: Tool was deleted but access records remain

**Fix**:
1. Add to DEPRECATED_TOOLS: `"Deleted Tool": None`
2. Run `python sync_tools.py` locally
3. Re-export: `python scripts/export_tool_access.py --env local`

---

### Migration Fails on Staging

**Symptom**: CI/CD shows migration error

**Diagnosis**: Check GitHub Actions logs for specific error

**Fix**:
1. **Schema error**: Fix migration file, commit, push
2. **Data error**: Check tool definitions match database
3. **Timeout**: Increase Heroku dyno size or run manually

**Manual intervention**:
```bash
# SSH into Heroku
heroku run bash -a omnitool-by-xdv-staging

# Check database state
python -c "from model import Tool; from main import create_app; app = create_app(); app.app_context().push(); tools = Tool.query.all(); [print(t.name) for t in tools]"

# Run migration manually
python migrate_db.py
```

---

## Production Deployment Checklist

### Pre-Deployment (Before Creating PR to Main)

- [ ] **All tests pass in CI/CD** (check GitHub Actions)
- [ ] **Staging deployment successful** (green checkmark in GitHub Actions)
- [ ] **Manual QA completed on staging**
  - Login as admin: https://omnitool-by-xdv-staging.herokuapp.com
  - Test new features/changes
  - Verify tool access permissions are correct
- [ ] **Verification passed**: `heroku run python scripts/verify_migration.py --env staging -a omnitool-by-xdv-staging`
- [ ] **Smoke tests passed** (automatic in CI/CD, or run manually)
- [ ] **No critical errors in staging logs**: `heroku logs --tail -a omnitool-by-xdv-staging`
- [ ] **Tool access export committed to git** (`data/tool_access_exports/local_tool_access.json` or `dev_tool_access.json`)

### Production Deployment (PR to Main)

1. **Create PR**: `development` → `main`
2. **Request approval** from team member (if configured)
3. **Merge PR** (triggers production deployment automatically)
4. **Monitor deployment** in GitHub Actions (5-8 minutes)
5. **Automatic checks performed**:
   - ✅ Production backup created
   - ✅ Code deployed
   - ✅ Migrations run
   - ✅ Tool access imported (merge mode)
   - ✅ Verification checks passed
   - ✅ Smoke tests passed
6. **Manual verification** (after deployment):
   - Open production: https://omnitool-by-xdv.herokuapp.com
   - Login as admin and verify changes
   - Check logs: `heroku logs --tail -a omnitool-by-xdv`

### Post-Deployment

- [ ] **Verify production application is functional**
- [ ] **Check production logs for errors** (first 10 minutes)
- [ ] **Monitor user reports** (if applicable)
- [ ] **Document any issues** in GitHub Issues

### Emergency Rollback (If Issues Found)

```bash
# Option 1: Use rollback script (recommended)
python scripts/rollback_migration.py --env production

# Option 2: Heroku restore from backup
heroku pg:backups:restore DATABASE_URL -a omnitool-by-xdv --confirm omnitool-by-xdv

# Option 3: Heroku code rollback
heroku releases:rollback -a omnitool-by-xdv
```

---

## FAQ

### Q: Do I need to run export_tool_access.py every time I make a code change?

**A**: No, only when you grant/revoke tool access in admin UI. Schema changes and tool definitions don't require export.

### Q: What if I forget to export tool_access before pushing?

**A**: The deployment will succeed, but staging won't have your permission changes. Run export locally, commit, push again.

### Q: Can I test the import_tool_access.py script safely?

**A**: Yes! Use `--dry-run` flag to preview changes without committing.

### Q: What happens if sync_tools.py deletes a tool I'm still using?

**A**: sync_tools.py only deletes tools listed in DEPRECATED_TOOLS. Tools not in DEFINED_TOOLS but also not in DEPRECATED_TOOLS are ignored (safe).

### Q: How do I sync production data to staging without Heroku Standard tier?

**A**: Alternative approach:
1. Export production data: `heroku run python scripts/export_tool_access.py --env production`
2. Import to staging: `heroku run python scripts/import_tool_access.py --source ...`

(This only syncs tool_access, not full database. Full database sync requires follower or pg:copy)

### Q: Is this production-ready?

**A**: Yes! All priority tasks are complete:
- ✅ **Priority 1 & 2**: Tool access export/import, verification, CI/CD integration, sync_tools.py fixed
- ✅ **Priority 3**: Production workflow, rollback script, smoke tests

**Production deployment is fully automated and safe** with multiple layers of protection.

---

### Q: How do I enable GitHub Environment protection for production?

**A**: To add manual approval gate for production deployments:

1. Go to GitHub repository → **Settings** → **Environments**
2. Create environment named **"production"**
3. Enable **"Required reviewers"**
4. Add team members who can approve production deployments
5. Save

Now all production deployments require manual approval before proceeding.

---

### Q: What happens if smoke tests fail after production deployment?

**A**: The deployment workflow will:
1. ❌ Mark deployment as failed
2. ⚠️  Log error details and rollback instructions
3. 🚨 Notify via GitHub Actions failure status

**You should**:
1. Check production status: `heroku open -a omnitool-by-xdv`
2. Review logs: `heroku logs --tail -a omnitool-by-xdv`
3. Decide: Fix forward or rollback
4. If rolling back: `python scripts/rollback_migration.py --env production`

---

## Optional Enhancements (Future)

1. **Enable Heroku Preboot** for zero-downtime deployments
   - Requires Heroku Performance tier ($250+/month)
   - Spins up new dynos before shutting down old ones

2. **Add Discord/Slack notifications** for deployment status
   - Requires webhook URL in GitHub Secrets
   - Uncomment notification step in `deploy_production.yml`

3. **Enable Heroku Review Apps** for PR previews
   - Automatically creates preview app for each PR
   - Allows testing before merging to staging

---

## Summary: What Changed?

### Before (Old Workflow)
- ❌ Only schema changes synced
- ❌ Tool access permissions environment-specific
- ❌ No verification after deployment
- ❌ No automatic backups before staging deployment

### After (New Workflow)
- ✅ Tool access permissions sync via version-controlled JSON
- ✅ Post-deployment verification catches issues
- ✅ Automatic backup before deployments
- ✅ Fixed sync_tools.py (handles renames/deletions correctly)
- ✅ Optional production data sync to staging
- ✅ Clear rollback procedures

**Your problem is solved**: User A excluded from Tool X in dev → correctly excluded in staging/production
