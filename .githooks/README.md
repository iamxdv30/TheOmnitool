# Git Hooks

This directory contains optional Git hooks for the Omnitool project.

## Available Hooks

### `pre-push.sample` - Database Backup Before Push

Creates a JSON backup of the database before each `git push`. This helps prevent data loss if a deployment causes migration issues.

**To Enable:**

```bash
# 1. Rename to remove .sample extension
mv .githooks/pre-push.sample .githooks/pre-push

# 2. Make it executable (Linux/Mac only)
chmod +x .githooks/pre-push

# 3. Configure Git to use this hooks directory
git config core.hooksPath .githooks
```

**To Disable Temporarily:**

```bash
# Skip the hook for a single push
git push --no-verify
```

**To Disable Permanently:**

```bash
# Remove the hook or rename it back to .sample
mv .githooks/pre-push .githooks/pre-push.sample
```

## Backup Location

All pre-push backups are stored in: `data/backups/pre_push_*.json`

## Cleanup

Old backups can accumulate. To clean up:

```bash
# Keep only the last 10 backups
ls -t data/backups/pre_push_*.json | tail -n +11 | xargs rm -f
```
