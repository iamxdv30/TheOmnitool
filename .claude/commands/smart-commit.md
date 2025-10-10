---
name: smart-commit
description: Analyze changes, generate detailed commit message, commit and push
---

You are tasked with comprehensively analyzing all uncommitted changes in the codebase, generating a detailed and meaningful git commit message, committing the changes, and pushing to the current branch.

## Process

### 1. Analyze Current State
First, gather comprehensive information about the repository state:

- Run `git status` to see all modified, added, and deleted files
- Run `git diff` to see unstaged changes in detail
- Run `git diff --staged` to see staged changes
- Run `git log --oneline -10` to understand recent commit message style
- Run `git branch --show-current` to identify the current branch

### 2. Comprehensive Change Analysis
Analyze the changes to understand:

- **Type of changes**: New feature, bug fix, refactor, docs, style, test, chore, etc.
- **Affected components**: Which parts of the codebase were modified (models, routes, frontend, templates, etc.)
- **Scope and impact**: How significant are the changes? Do they affect multiple areas?
- **Related files**: Group related changes together for better understanding
- **Breaking changes**: Identify any potentially breaking changes

### 3. Generate Detailed Commit Message
Create a commit message following this structure:

```
<type>(<scope>): <short summary>

<detailed description>

- <bullet point 1>
- <bullet point 2>
- <bullet point 3>

<additional notes if needed>

```

**Type options**: feat, fix, refactor, docs, style, test, chore, perf, build, ci

**Guidelines**:
- **Short summary**: Max 72 characters, imperative mood ("add" not "added")
- **Detailed description**: Explain the "why" and "what" at a high level
- **Bullet points**: List specific changes, enhancements, or fixes
- **Be specific**: Reference file paths, function names, or components when relevant
- **Match project style**: Follow the pattern from recent commits

### 4. Stage and Commit
- Stage all relevant files with `git add`
- **DO NOT stage** sensitive files (.env, credentials, secrets)
- Warn if sensitive files are detected
- Create commit with the generated message using HEREDOC format
- Verify commit succeeded with `git status`

### 5. Push to Branch
- Push commits to the current branch using `git push`
- If the branch has no upstream, use `git push -u origin <branch-name>`
- Report the final status and any warnings

## Special Considerations

### Multiple Related Changes
If changes span multiple areas (e.g., backend + frontend + docs):
- Use a broader scope like `app` or `system`
- List all affected areas in bullet points
- Example: `feat(app): add user role management feature`

### Sequential Commits
If changes are too diverse and should be separate commits:
- Ask the user if they want to split into multiple commits
- Suggest logical groupings

### Sensitive Files
Never commit:
- `.env` files
- Files containing API keys, tokens, passwords
- `credentials.json` or similar
- Database files (`.db`, `.sqlite`)

Warn the user and skip these files.

### Commit Message Examples

**Example 1 - Feature Addition**:
```
feat(admin): add bulk user management and role assignment

Implement comprehensive bulk operations for admin dashboard including
user selection, role changes, and tool access management.

- Add checkbox selection for multiple users
- Implement bulk role change functionality
- Add bulk tool access grant/revoke
- Create confirmation modals for bulk operations
- Update admin dashboard UI with bulk action buttons

```

**Example 2 - Bug Fix**:
```
fix(auth): resolve session timeout issue on password reset

Fixed critical bug where password reset tokens were expiring
prematurely due to incorrect session configuration.

- Update token expiration logic in auth_routes.py:245
- Fix session handling in password reset flow
- Add proper error messages for expired tokens
- Update tests to cover token expiration scenarios

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Example 3 - Refactor**:
```
refactor(models): restructure user hierarchy with design patterns

Refactor model architecture to use Factory and Strategy patterns
for better maintainability and extensibility.

- Split monolithic user model into modular files
- Implement UserFactory for role-based user creation
- Add Strategy pattern for password hashing
- Update imports across all routes and tests
- Maintain backward compatibility with existing code

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Edge Cases

### No Changes to Commit
If `git status` shows no changes:
- Report "No changes to commit"
- Do not create an empty commit
- Exit gracefully

### Merge Conflicts
If there are merge conflicts:
- Do not attempt to commit
- Inform user to resolve conflicts first
- Show conflicted files

### Pre-commit Hooks
If commit fails due to pre-commit hooks:
- Show the hook output
- If hooks modified files, verify it's safe to amend
- Amend commit if safe, otherwise create new commit

## Output Summary

After successful completion, provide:
1. Summary of files committed (count and key files)
2. The commit message used
3. Confirmation of push success
4. Current branch name and status
5. Any warnings or issues encountered
