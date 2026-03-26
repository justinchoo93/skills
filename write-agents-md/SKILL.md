---
name: write-agents-md
description: Create or refresh repository AGENTS.md files and required sibling CLAUDE.md pointers. Use when asked to add, rewrite, audit, or split AGENTS.md instructions for a repo, package, or subdirectory, including cases where Codex should derive exact commands, conventions, boundaries, and verification steps from the codebase.
---

# Write AGENTS.md

Inspect the repo and write a small operating manual for coding agents. Keep it specific, verifiable, and scoped to instructions an agent is unlikely to infer reliably from the code alone.

Read [references/template.md](references/template.md) when you want a starting structure. Adapt it to the repo; do not keep placeholder sections that the repo does not support.

## Workflow

1. Inspect the repo before writing.

   Start by locating:
   - existing `AGENTS.md` and `CLAUDE.md` files
   - root docs such as `README*`, `CONTRIBUTING*`, and `docs/`
   - build/test manifests such as `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, `justfile`, and CI workflows

   Prefer exact commands such as:

   ```bash
   rg --files -g 'AGENTS.md' -g 'CLAUDE.md' -g 'README*' -g 'CONTRIBUTING*' -g 'package.json' -g 'pyproject.toml' -g 'Cargo.toml' -g 'go.mod' -g 'Makefile' -g 'justfile' -g '.github/workflows/*'
   ```

2. Decide the scope.

   Write a root `AGENTS.md` for repo-wide defaults.
   Add nested `AGENTS.md` files only when a subdirectory has materially different commands, constraints, or workflows.
   Keep specialized rules close to the code they govern.

3. Gather only non-obvious, repo-specific instructions.

   Extract:
   - exact install, dev, test, lint, typecheck, and build commands
   - local directory conventions and ownership boundaries
   - generated-file rules, dependency rules, migration rules, and ask-first constraints
   - what "done" means for this repo and how to verify it

   If a policy is not supported by repo evidence, omit it. Do not invent commands or rules.

4. Write the file in a compact, operational format.

   For a root file, prefer this section order:
   - purpose or scope
   - quick commands
   - repo map
   - conventions
   - boundaries or ask-first rules
   - done when or verification
   - local overrides

   Keep the root file roughly one page. In most repos that means about 100-200 lines, not a long handbook.

5. Create the required sibling `CLAUDE.md`.

   Whenever you create an `AGENTS.md` in any directory, create or update `CLAUDE.md` in the same directory.

   `CLAUDE.md` must contain exactly:

   ```md
   @AGENTS.md
   ```

   Do not add any extra text.

6. Verify the result.

   Check that:
   - every command in `AGENTS.md` exists in the repo and is spelled exactly
   - the file contains repo-specific guidance, not generic advice
   - long or rare workflows are linked or pushed into nested `AGENTS.md` files instead of bloating the root file
   - every new `AGENTS.md` has a sibling `CLAUDE.md`

## What To Include

- Exact runnable commands near the top.
- Path-level conventions that are easy to miss.
- Clear boundaries such as "ask before adding dependencies" or "do not edit generated files".
- Concrete completion criteria and verification steps.
- Pointers to nested `AGENTS.md` files when subtrees have local overrides.

## What To Exclude

- README content copied into `AGENTS.md`.
- Generic advice such as "write clean code" or "be careful".
- Long architecture tours unless they are required to avoid repeated mistakes.
- Rare workflows that belong in dedicated docs.
- Unverified assumptions about team policy.

## Writing Rules

- Prefer short sections and flat bullets.
- Use exact file paths, commands, and tool names.
- Prefer examples over abstract guidance when style or output shape matters.
- State constraints as direct instructions.
- Update an existing `AGENTS.md` in place when it is already present and mostly correct; do not churn wording without a reason.

## Good Patterns

Prefer specific entries such as:

- Run `pnpm test`
- Run `pnpm lint`
- Do not edit `sdk/generated/`
- Public API changes require docs under `docs/api/`

Avoid vague entries such as:

- Run tests before finishing
- Keep files organized
- Follow project conventions

## Final Response

In the final message:
- list the `AGENTS.md` and `CLAUDE.md` files created or updated
- mention the main repo signals used to derive the instructions
- call out any important gaps you could not verify from the repo
