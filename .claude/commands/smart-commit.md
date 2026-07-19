---
name: smart-commit
description: Analyze changes, generate detailed commit message, commit and push
---

You are tasked with comprehensively analyzing all uncommitted changes, generating a detailed commit message, committing, pushing, and optionally updating related project files. This command is **codebase-agnostic** — it works on any project by dynamically discovering the repository context.

---

## Phase 0: Discovery

Before analyzing changes, discover the repository context. Do NOT assume any particular project structure.

### 0A. Repository Context

```bash
git status
git diff
git diff --staged
git log --oneline -10
git branch --show-current
git remote -v
```

### 0B. Detect Project Files

Scan the project root for files that may need updating alongside the commit:

**Changelog files** (check if any exist):
- `CHANGELOG.md`, `CHANGELOG`, `CHANGES.md`, `HISTORY.md`
- `changelog.md`, `changes.md`

**Readme files** (check if any exist):
- `README.md`, `README`, `README.rst`, `readme.md`

**Version files** (check if any exist):
- `VERSION`, `version.txt`, `version.py`
- Check `package.json` → `"version"` field
- Check `pyproject.toml` → `[project] version`
- Check `setup.py`, `setup.cfg` → `version=`
- Check `Cargo.toml` → `version =`

**Sensitive file patterns** (NEVER commit these):
- `.env`, `.env.*` (except `.env.example`)
- `*credentials*`, `*secret*`, `*token*` (config files with real values)
- `*.key`, `*.pem`, `*.p12`
- `id_rsa`, `id_ed25519`
- Database files: `*.db`, `*.sqlite`, `*.sqlite3`

Record what exists — these inform later phases.

---

## Phase 1: Comprehensive Change Analysis

### 1A. Categorize Every Changed File

For each modified/added/deleted file, determine:

- **Change type**: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`, `perf`, `build`, `ci`
- **Scope**: Which component/area it belongs to (e.g., `auth`, `api`, `frontend`, `db`, `config`)
- **Impact**: Breaking change? New dependency? Migration needed?

### 1B. Group Related Changes

Cluster files that belong to the same logical change:
- A new API endpoint + its test + its frontend consumer = one logical feature
- A model change + migration + service update = one logical change
- Config-only changes = separate from feature changes

### 1C. Assess Commit Strategy

**Single commit** if:
- All changes relate to one logical feature/fix/refactor
- Changes span multiple files but serve one purpose

**Multiple commits** — ask the user if:
- Changes are clearly unrelated (e.g., a bug fix + a new feature + docs cleanup)
- Suggest logical groupings and let the user decide
- If user says "just commit everything", proceed with a single commit

---

## Phase 2: Generate Commit Message

### Format

Follow [Conventional Commits](https://www.conventionalcommits.org/) format, adapted to match the project's existing commit style (from `git log`):

```
<type>(<scope>): <short summary>

<detailed description — the "why" and high-level "what">

- <specific change 1>
- <specific change 2>
- <specific change 3>

<footer — breaking changes, issue refs, etc.>
```

### Rules

- **Short summary**: Max 72 chars, imperative mood ("add" not "added", "fix" not "fixed")
- **Scope**: Derive from the affected area. Use broad scopes for cross-cutting changes (`app`, `system`, `stack`)
- **Description**: Explain WHY the change was made, not just what changed. What problem does it solve?
- **Bullet points**: Be specific — reference file paths, function names, components. Group by sub-area if many changes
- **Breaking changes**: Prefix with `BREAKING CHANGE:` in the footer
- **Issue references**: Include `Closes #123` or `Fixes #456` if referenced in branch name or recent context
- **Match project style**: If recent commits use emoji prefixes, lowercase types, or a different convention — match it

### Type Reference

| Type | When to use |
|------|------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code restructuring without behavior change |
| `docs` | Documentation only |
| `style` | Formatting, whitespace, missing semicolons (no logic change) |
| `test` | Adding or fixing tests |
| `chore` | Maintenance, dependency updates, config changes |
| `perf` | Performance improvement |
| `build` | Build system or external dependency changes |
| `ci` | CI/CD pipeline changes |

### Multi-Scope Changes

When changes span multiple areas:
- Use the **primary** scope in the header: `feat(auth): add OAuth2 login with Google`
- List secondary areas in bullet points:
  ```
  - Add OAuth2 routes in routes/auth_routes.py
  - Create Google OAuth provider in services/oauth_service.py
  - Add login button to frontend/src/app/(auth)/login/page.tsx
  - Update environment configuration with OAuth credentials
  ```

---

## Phase 3: Stage and Commit

### 3A. Stage Files

- Stage all relevant changed files by name (prefer explicit `git add <file>` over `git add -A`)
- **NEVER stage** files matching sensitive patterns from Phase 0B
- If sensitive files are detected in the diff, **warn the user** and skip them
- If `.gitignore` additions are part of the changes, stage those first

### 3B. Commit

Create the commit using HEREDOC format for proper message formatting:

```bash
git commit -m "$(cat <<'EOF'
<commit message here>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

### 3C. Verify

```bash
git status
git log --oneline -1
```

If pre-commit hooks fail:
- Show the hook output
- Fix the issues the hook identified (lint errors, formatting, etc.)
- Re-stage the fixed files
- Create a **NEW** commit (do NOT amend — the previous commit didn't happen)
- If hooks modify files automatically (e.g., formatters), re-stage and create a NEW commit

---

## Phase 4: Push

```bash
git push
```

If no upstream is set:
```bash
git push -u origin <current-branch>
```

If push fails due to remote changes:
- **Do NOT force push**
- Inform the user and suggest `git pull --rebase` first
- Let the user decide how to proceed

---

## Phase 5: Conditional Updates (Only If Applicable)

These steps are **conditional** — only execute them if the relevant files exist AND the changes warrant an update.

### 5A. Update CHANGELOG (Only if file exists AND changes are user-facing)

**Skip if:**
- No changelog file exists in the project
- Changes are internal-only (refactors, CI fixes, dev tooling, test-only changes)
- Changes are trivial (typo fixes, comment updates, formatting)

**Execute if:**
- A changelog file exists AND changes include new features, bug fixes, breaking changes, deprecations, or security fixes

**How to update:**
1. Read the existing changelog to understand its format (Keep a Changelog, custom, etc.)
2. Match the existing format exactly (heading levels, date format, category names, bullet style)
3. Add a new entry at the TOP of the changelog (below the header), using the next logical version or `[Unreleased]`
4. Categorize changes using the changelog's existing categories. Common patterns:
   - Keep a Changelog: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`
   - Emoji-style: Categories with emoji prefixes (match what's already there)
   - Flat: Simple bullet list under version heading
5. Write entries from the USER's perspective, not the developer's:
   - Good: "Add bulk export for user data"
   - Bad: "Refactor export_service.py to support batch operations"
6. Include the date in whatever format the file already uses

**Version bumping logic:**
- If changes include breaking changes → suggest major version bump
- If changes include new features → suggest minor version bump
- If changes are fixes only → suggest patch version bump
- If an `[Unreleased]` section pattern is used, add there instead of creating a new version

### 5B. Update README (Only if file exists AND specific triggers match)

**Skip if:**
- No readme file exists
- Changes don't affect anything the README documents

**Execute if the changes affect ANY of these (and the README documents them):**
- Installation steps or prerequisites changed
- New CLI commands or scripts added that are documented in README
- Version badge needs updating (if README has version badges)
- New major feature added that the README's feature list covers
- API endpoints changed that the README documents
- Environment variables changed that the README references
- Build/deploy process changed that the README describes

**How to update:**
1. Read the full README to understand what it covers
2. Only update the specific sections affected by the changes
3. Do NOT add new sections unless explicitly needed
4. Match the existing writing style and formatting
5. If the README has a version badge, update the version number

### 5C. Update Version Files (Only if version bump is warranted)

**Skip if:**
- No version files exist
- Changes don't warrant a version bump (internal refactors, CI changes, test-only)

**Execute if:**
- A new feature, fix, or breaking change is being released
- The changelog was updated with a new version number

**How to update:**
- Update ALL version files consistently (VERSION, package.json, pyproject.toml, etc.)
- Ensure the same version number appears everywhere

### 5D. Commit Updates (If any files were updated in 5A-5C)

If any project files were updated:

```bash
git add <updated files>
git commit -m "$(cat <<'EOF'
docs: update changelog and project metadata for <version>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
git push
```

---

## Phase 6: PR Message Generation

After pushing, generate a pull request description that can be used when creating a PR.

### When to Generate

Always generate the PR message and display it. The user can use it immediately or save it for later.

### Format

```markdown
## Summary
<1-3 sentences explaining the overall purpose of the changes on this branch>

## Changes
<Grouped bullet points of what changed, organized by area/component>

### [Area 1]
- Change description
- Change description

### [Area 2]
- Change description

## Breaking Changes
<List any breaking changes, or "None" if there are none>

## Test Plan
- [ ] <How to verify the changes work>
- [ ] <Edge cases to test>
- [ ] <Regression areas to check>

## Notes
<Any additional context, deployment steps, migration requirements, or caveats>
```

### Rules

- **Derive from ALL commits on the branch**, not just the latest commit. Run `git log main..HEAD --oneline` (or equivalent base branch) to see all commits
- **Write for reviewers** — explain the "why" more than the "what"
- **Group changes logically**, not by file
- **Test plan should be actionable** — specific steps, not vague "test it works"
- **Include deployment notes** if there are migrations, env var changes, or infrastructure updates

### Output

Display the PR message in a code block so the user can copy it. Also mention:
```
To create the PR now, run:
gh pr create --title "<suggested title>" --body "<body>"
```

---

## Edge Cases

### No Changes to Commit
- Report "No changes to commit"
- Do NOT create an empty commit

### Merge Conflicts
- Do NOT attempt to commit
- Show the conflicted files
- Inform the user to resolve conflicts first

### Detached HEAD
- Warn the user
- Suggest creating a branch first

### Large Diffs (50+ files)
- Summarize by directory/area rather than listing every file
- Group changes into logical categories
- Ask the user if they want to split into multiple commits

### Binary Files
- Note them in the commit message but don't try to describe their content
- Warn if large binaries (>5MB) are being committed

---

## Output Summary

After completion, provide a concise summary:

```
## Commit Summary

**Branch:** <branch-name>
**Commit:** <short hash> <commit message first line>
**Files:** <count> files changed (<insertions>+, <deletions>-)
**Push:** Success / Failed (reason)

**Updated:** CHANGELOG.md ✓ | README.md — (no update needed) | VERSION — (no update needed)

**PR Message:** Generated below (copy when ready to create PR)
```
