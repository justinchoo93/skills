# AGENTS.md Template

Use this as a starting point. Delete sections that are not supported by the repo, and replace placeholders with verified commands and rules.

## Root file

```md
# AGENTS.md

## Scope
- Apply these rules repo-wide unless a deeper `AGENTS.md` overrides them.

## Quick commands
- Install: `<exact command>`
- Dev server: `<exact command>`
- Tests: `<exact command>`
- Lint: `<exact command>`
- Typecheck: `<exact command>`
- Build: `<exact command>`

## Repo map
- `<path>/`: `<why it matters>`
- `<path>/`: `<why it matters>`

## Conventions
- `<repo-specific rule>`
- `<repo-specific rule>`

## Boundaries
- `<ask-first rule>`
- `<do-not-edit rule>`

## Done when
- `<verification rule>`
- `<verification rule>`

## Local overrides
- `<subdir>/AGENTS.md` contains `<scope>`
```

## Nested file

```md
# AGENTS.md

## Scope
- Apply these rules only within `<subdir>/`.

## Commands
- Tests: `<exact command>`
- Lint: `<exact command>`

## Local conventions
- `<subdir-specific rule>`

## Boundaries
- `<subdir-specific constraint>`

## Done when
- `<subdir-specific verification>`
```

## Sibling CLAUDE.md

```md
@AGENTS.md
```
