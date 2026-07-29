---
name: sync-docs
description: Update CLAUDE.md with recent changes
---

You are tasked with syncing all AI context files in this repository to reflect the current state of the codebase. This command is **codebase-agnostic** — it works on any project by dynamically discovering the tech stack, file structure, and AI context files.

---

## Phase 0: Discovery (Codebase-Agnostic)

Before doing anything project-specific, **discover** the codebase you're working in. Do NOT assume any particular tech stack, framework, or file structure.

### 0A. Identify the Primary AI Context File

The **primary context file** is the source of truth. Search for it in this priority order:

1. `CLAUDE.md` (root) — Claude Code context
2. `.claude/CLAUDE.md` — Claude Code context (alternate location)
3. `AGENTS.md` — Generic agent context
4. `CODEX.md` — OpenAI Codex context
5. `COPILOT.md` — GitHub Copilot context

If none exist, report that no primary context file was found and stop.

### 0B. Discover Companion AI Context Files

Scan the project root for **other AI context files** that should be kept in sync with the primary file. Common patterns:

```
Glob for: *.md (root only)
```

Look for files whose purpose is providing context to an AI agent:
- `Gemini.md` — Google Gemini context
- `COPILOT.md` — GitHub Copilot context
- `CURSOR.md` or `.cursorrules` — Cursor IDE context
- `CODEX.md` — OpenAI Codex context
- `AGENTS.md` — Generic agent context
- `WINDSURF.md` or `.windsurfrules` — Windsurf context
- `AIDER.md` or `.aider.conf.yml` — Aider context
- `CLINE.md` or `.clinerules` — Cline context
- `CONTINUE.md` or `.continue/config.json` — Continue.dev context
- `DEVIN.md` — Devin context
- Any `*.md` file at root that contains AI agent instructions (read first 20 lines to check)

Also check these directories for rule files:
- `.windsurf/rules/` — Windsurf rule files
- `.cursor/rules/` — Cursor rule files
- `.github/copilot-instructions.md` — GitHub Copilot instructions

Record all discovered files as **companion files** to update after the primary file.

### 0C. Discover the Tech Stack

Detect the project's technology by scanning for marker files. Do NOT hardcode — discover dynamically:

**Language & Runtime:**
| Marker File | Detected Stack |
|---|---|
| `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile` | Python |
| `package.json` | Node.js / JavaScript / TypeScript |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `pom.xml`, `build.gradle` | Java |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `*.csproj`, `*.sln` | C# / .NET |

**Framework Detection (read the detected package manifest):**
- Python: Check `requirements.txt` or `pyproject.toml` for Flask, Django, FastAPI, etc.
- Node.js: Check `package.json` dependencies for Next.js, React, Vue, Angular, Express, etc.
- Read the entry point file to confirm (e.g., `main.py`, `app.py`, `index.ts`, `server.js`)

**Database Detection:**
- Check for `docker-compose.yml`, `Dockerfile`, ORM config files
- Check for `migrations/`, `prisma/`, `drizzle/`, `alembic/` directories
- Check `.env` or `.env.example` for `DATABASE_URL` patterns

**Frontend Detection:**
- Check for `frontend/`, `client/`, `web/`, `app/` subdirectories with their own `package.json`
- Check for `static/`, `public/`, `assets/` directories
- Check for template engines (`templates/`, `views/`)

**Testing Detection:**
- Check for `tests/`, `test/`, `__tests__/`, `spec/` directories
- Check for `pytest.ini`, `jest.config.*`, `vitest.config.*`, `.mocharc.*`
- Check `package.json` scripts for test commands

**CI/CD Detection:**
- `.github/workflows/` — GitHub Actions
- `.gitlab-ci.yml` — GitLab CI
- `Jenkinsfile` — Jenkins
- `.circleci/` — CircleCI
- `bitbucket-pipelines.yml` — Bitbucket Pipelines

**Deployment Detection:**
- `Procfile` — Heroku
- `vercel.json` — Vercel
- `netlify.toml` — Netlify
- `fly.toml` — Fly.io
- `Dockerfile` / `docker-compose.yml` — Docker
- `serverless.yml` — Serverless Framework
- `terraform/`, `*.tf` — Terraform

### 0D. Discover the File Structure

Map the project structure dynamically:

```bash
# Get top-level directory structure
ls -la (root)

# Get source directories
Glob for: src/**/ or app/**/ or lib/**/
```

Identify these categories by what actually exists:
- **Entry points**: Main application files
- **Models/Schema**: Database models, types, schemas
- **Routes/Controllers**: API endpoints, page routes
- **Services/Logic**: Business logic layer
- **Configuration**: Config files, environment
- **Scripts**: Utility/management scripts
- **Tests**: Test files and fixtures
- **Documentation**: Doc files
- **Static assets**: CSS, JS, images
- **Infrastructure**: CI/CD, Docker, deployment

---

## Phase 1: Change Detection

Determine what changed since the last sync:

```bash
# Recent commits (last 10)
git log --oneline -10

# Files changed since last sync (compare against main branch)
git diff --name-only main...HEAD

# Files modified in the last 7 days
git log --since="7 days ago" --name-only --pretty=format:""

# Unstaged/untracked changes
git status --short
```

Use this output to **prioritize** which areas need attention. Skip areas where no relevant files changed.

---

## Phase 2: Update the Primary Context File

Read the current primary context file (e.g., `CLAUDE.md`). For each section, compare what's documented against what actually exists in the codebase.

### What to Check (Guided by Discovery)

For each category discovered in Phase 0D, verify that the primary context file accurately documents:

1. **Project Metadata** — Version, name, description, current status
2. **Development Commands** — How to run, build, test, deploy
3. **Dependencies** — Key packages for each detected stack
4. **Architecture** — Entry points, patterns, directory structure
5. **Models/Schema** — Database models, their fields and relationships
6. **Routes/API** — All endpoint files and URL patterns
7. **Services/Logic** — Business logic layer files and patterns
8. **Frontend** — Pages, components, state management, hooks, API clients
9. **Configuration** — Environment variables, config files
10. **Database** — Migration files, backup/restore procedures
11. **Scripts** — Utility scripts and their purposes
12. **Testing** — Test files, fixtures, coverage info
13. **CI/CD** — Pipeline files and deployment flow
14. **Documentation** — Cross-references to detailed docs
15. **Common Gotchas** — Known pitfalls and workarounds

### Update Rules

- **Add** sections for newly discovered files/features not yet documented
- **Update** sections where file listings, commands, or descriptions are stale
- **Remove** references to files that no longer exist
- **Preserve** the existing document structure — don't restructure unless necessary
- **Stay concise** — Context files are loaded into every conversation; focus on what helps AI agents work effectively
- **Cross-reference** — Link to detailed docs rather than duplicating content
- **Verify accuracy** — Ensure file paths, commands, and field names are correct

---

## Phase 3: Sync Companion AI Context Files

After updating the primary file, sync all companion files discovered in Phase 0B.

### Sync Strategy

For each companion file:

1. **Read** the companion file to understand its current structure and style
2. **Compare** it against the updated primary file section by section
3. **Identify gaps** — Sections present in the primary file but missing or outdated in the companion
4. **Update** the companion file, preserving its unique formatting and style

### Sync Rules

- **The primary file (`CLAUDE.md`) is the source of truth.** All companion files should reflect the same information.
- **Preserve each file's native format.** `Gemini.md` may use different heading styles, bullet formats, or section organization than `CLAUDE.md`. Adapt the content to match the companion's style, don't force the primary file's format onto it.
- **Preserve file-specific sections.** If a companion file has unique sections (e.g., Gemini.md's "Common Issues & Troubleshooting" with step-by-step fix guides), keep them — just ensure the information is current.
- **Don't duplicate agent-specific instructions.** If `CLAUDE.md` has a "MCP Server Usage Guidelines" section specific to Claude, do NOT copy that into `Gemini.md`. Each file may have its own agent-specific configuration section — leave those untouched.
- **Sync these categories across all files:**
  - Project metadata (version, description, status)
  - Tech stack and dependencies
  - Architecture (models, routes, services, frontend structure)
  - Development commands (run, test, build, deploy)
  - Database management (migrations, backups, Docker setup)
  - Key features and workflows (RBAC, tool access, dashboard status)
  - Environment configuration
  - Common gotchas
  - Key files map
- **Skip these (agent-specific, do not sync):**
  - MCP server configurations
  - Agent-specific behavioral instructions
  - Tool-specific guidelines (e.g., Claude's tool usage rules)
  - IDE-specific settings

### Handling New Companion Files

If a new companion file is discovered that didn't exist before:
- Report it in the output
- Do NOT auto-generate content for it — just note its existence
- Let the user decide whether to populate it

### Handling Deleted Companion Files

If a previously known companion file no longer exists:
- Report it in the output
- Remove any cross-references to it from other files

---

## Phase 4: Verify and Report

### Pre-Report Checks

Before producing the summary:
- Verify all file paths mentioned in updated files actually exist
- Verify all commands mentioned are still valid
- Check that cross-references between files are consistent

### Output Format

Provide a structured summary:

```
## Sync Summary

### Primary File: [filename]
- [Section]: [What changed]
- [Section]: Already up to date

### Companion Files Synced:
- [filename]: [What was updated to align with primary]
- [filename]: Already in sync

### Companion Files Detected (Not Updated):
- [filename]: [Reason — e.g., "New file, needs manual setup"]

### Discovered Stack:
- Language: [detected]
- Framework: [detected]
- Frontend: [detected]
- Database: [detected]
- Deployment: [detected]

### Notes:
- [Any observations about inconsistencies, stale references, or things to watch]
```

---

## Example Triggers for Running This Command

Run this command when:
- Version number updated
- Dependencies added/removed (any package manager)
- New routes, endpoints, or pages added
- New models, fields, or relationships created
- New services or business logic added
- New frontend components, stores, or hooks created
- Database migrations created
- New scripts added
- CI/CD pipeline changes
- Testing infrastructure changes
- Architecture changes (new patterns, refactors)
- New documentation files added
- Development workflow changes (new commands, scripts)
- A new AI context file is added to the project
