---
inclusion: always
---

## Code Principles

- Prioritize simplicity: use the most basic approach, avoid complexity
- Follow DRY principle: never repeat code blocks
- Keep code minimal and concise
- Update existing files rather than creating new ones unless explicitly requested
- Test code before committing to ensure it works

## Python Standards

- Use `python3` (specifically Python 3.13 for applications)
- Create virtual environment named `.venv`
- Maintain `requirements.txt` for all dependencies

## Project Structure

- `/tests` - all test files
- `/scripts` - all scripts
- `/docs` - all documentation
- `/backups` - all backups
- `/reference` - reference material

## File Operations

- Never delete files without listing them first and getting approval
- Delete temporary test files after completion
- Maintain `changelog.md` in reverse chronological order (YYYY-MM-DD format, latest at top)

## Git Workflow

- Always work in a new branch (required for specs)
- Never push to live or production
- Follow Conventional Commits specification with format:

```
<type>[optional scope]: <description>

[optional body]

🤖 Assisted by Kiro
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`

Commit message rules:

- Use imperative mood ("add" not "added")
- Capitalize subject line, no ending period
- Limit subject to 50 characters
- Separate body with blank line, wrap at 72 characters
- Explain what and why, not how
