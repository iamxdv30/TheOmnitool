---
name: sync-docs
description: Update CLAUDE.md with recent changes
---

You are tasked with updating the `.claude/CLAUDE.md` file to reflect recent changes in the codebase. This command should be run whenever there are significant changes that affect how future Claude Code instances should operate in this repository.

## What to Check and Update

Analyze the following aspects of the codebase and update CLAUDE.md accordingly:

### 1. Project Metadata
- Check `README.md` for version changes
- Check `CHANGELOG.md` for new features or changes
- Check `VERSION` file if it exists
- Update the "Project Overview" section if version or description changed

### 2. Dependencies
- Read `requirements.txt` to detect new or removed packages
- If Flask extensions changed, update relevant sections (e.g., new Flask-X package)
- If testing libraries changed, update the "Testing" section

### 3. File Structure Changes
- Use Glob to scan for:
  - New route files in `routes/`
  - New model files in `model/`
  - New JavaScript files in `static/js/`
  - New templates in `templates/` or `Tools/templates/`
- Update "Routes Structure", "Frontend Architecture", or "Model Architecture" sections if new files were added

### 4. Database Migrations
- Check `migrations/versions/` for new migration files
- If recent migrations exist, mention them or update migration guidance

### 5. Configuration Changes
- Check `main.py` for new configuration in `create_app()`
- Check for new environment variables in `.env` usage
- Update "Environment Configuration" section if needed

### 6. New Tools or Features
- Check `tool_management.py` for new tools added
- Check `model/tools.py` for schema changes
- Update "Tool Access System" if default tools changed

### 7. Architecture Changes
- Review recent changes to `model/` files for new design patterns
- Check if new blueprints were registered in `main.py`
- Update "Design Patterns in Use" or "Architecture" sections

### 8. Testing Changes
- Check `tests/conftest.py` for new fixtures
- Look for new test files in `tests/`
- Update "Testing" section with new fixtures or patterns

### 9. Development Commands
- Check for new npm/pip scripts
- Check for new management commands (like `tool_management.py` additions)
- Update "Development Commands" section

## Process

1. **Scan for changes**: Use Git to identify recently modified files, or glob through the entire codebase
2. **Read key files**: Focus on `README.md`, `CHANGELOG.md`, `requirements.txt`, `main.py`, and any recently modified files
3. **Identify updates needed**: Compare current CLAUDE.md content with actual codebase state
4. **Update CLAUDE.md**: Make targeted edits to keep it accurate and concise
5. **Preserve structure**: Keep the existing organization and only update relevant sections
6. **Stay concise**: Don't add unnecessary information; focus on what helps future Claude instances

## Example Triggers for Updates

Run this command when:
- New Python packages installed/uninstalled (`requirements.txt` changed)
- New routes, models, or blueprints added
- Database migrations created
- New tools added to the system
- Architecture refactored (e.g., new design patterns)
- New JavaScript modules created
- Testing infrastructure changed
- Development workflow commands added
- Version number updated
- Major features added (check CHANGELOG.md)

## Output

After updating CLAUDE.md, provide a brief summary of what was changed, such as:
- "Updated version to 1.4.1"
- "Added new Admin Dashboard features to CLAUDE.md"
- "Updated dependencies section with new Flask extensions"
- "No changes needed - CLAUDE.md is up to date"
