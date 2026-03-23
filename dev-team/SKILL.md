---
name: dev-team
description: /dev-team — Implement a task with a 3-agent team (Implementer, Reviewer, QA). Takes GitHub issues or inline descriptions through the full lifecycle from acceptance criteria to merged code.
---

# /dev-team — Implement a task with a 3-agent team

You are orchestrating a development team of three agents: **Implementer**, **Reviewer**, and **QA**. Your job is to take a task through the full lifecycle from acceptance criteria to merged code.

## Input

The user provides either:
- A GitHub issue number: `/dev-team #42`
- An inline task description: `/dev-team "add rate limiting to the API"`
- Multiple tasks: `/dev-team #42 #43 #44` (run in parallel if no dependencies)

The argument is: $ARGUMENTS

## Phase 0: Gather & Refine Acceptance Criteria

**This phase is a hard prerequisite. Do NOT proceed to implementation without clear, testable ACs.**

If the input is a GitHub issue, fetch it:
```
gh issue view <number> --json title,body
```

Extract the acceptance criteria from the issue body. If the input is inline text, use it directly.

**Evaluate the ACs.** Every AC must be:
1. **Specific** — describes an observable behavior, not a vague goal
2. **Testable** — has a concrete verification command (pytest, bash, build command)
3. **Independent** — can be verified in isolation

If ANY AC is vague, missing a verification command, or the task has no ACs at all:
- Present what you have to the user
- Ask targeted questions to fill gaps (use AskUserQuestion)
- Propose concrete ACs with verification commands
- Get user approval before proceeding

**Output of Phase 0:** A numbered list of ACs, each with a verification command. Confirm with the user.

## Phase 1: Create Worktree

Create an isolated worktree for this task:

```
Branch naming: feat/<short-descriptive-name>
```

Use the Agent tool with `isolation: "worktree"` for the Implementer in Phase 2. The worktree is created automatically.

## Phase 2: Implement

Spawn an **Implementer** agent (Agent tool, `isolation: "worktree"`) with a prompt containing:
- The full task description
- All acceptance criteria with verification commands
- List of dependencies already on main (what to import/reuse)
- Instruction to write code + tests, commit frequently, run tests before finishing

The Implementer agent must:
1. Read relevant existing code on main to understand patterns and conventions
2. Write implementation + tests following TDD
3. Run all verification commands from the ACs
4. Commit with descriptive messages
5. Return: summary of what was built, files created/modified, test results

## Phase 3: Review

Spawn a **Reviewer** agent with the worktree path. The Reviewer checks:
- Code quality, readability, naming
- Correct use of existing patterns/utilities from main (no reinventing)
- No security issues (injection, secrets in code, etc.)
- Tests are meaningful (not trivially passing)
- No unnecessary complexity (KISS, YAGNI)

The Reviewer returns either:
- **PASS** — code is ready for QA
- **ISSUES** — a numbered list of specific, actionable problems with file:line references

If ISSUES: do NOT proceed to QA. Go directly to Phase 5 (Loop).

## Phase 4: QA (Hard Gate)

Spawn a **QA** agent with the worktree path. The QA agent:
1. Reads each AC from Phase 0
2. Runs the EXACT verification command for each AC
3. For each AC, records: **PASS** (with evidence) or **FAIL** (with error output)

**ALL ACs must pass. This is a hard gate — no exceptions, no partial credit.**

The QA agent returns a checklist:
```
AC 1: [PASS/FAIL] — <evidence>
AC 2: [PASS/FAIL] — <evidence>
...
VERDICT: ALL PASS / X of Y FAILED
```

If ALL PASS: proceed to Phase 6 (Merge).
If ANY FAIL: proceed to Phase 5 (Loop).

## Phase 5: Loop (Max 3 Cycles)

Collect feedback from the Reviewer (if ISSUES) and/or QA (if FAILs). Send the Implementer agent back into the same worktree with:

- The specific issues/failures
- The error output from failed verification commands
- Instruction to fix ONLY the reported issues (no scope creep)

Then re-run Review (Phase 3) and QA (Phase 4).

**Track the cycle count.** After 3 failed cycles:
1. **STOP** — do not attempt further fixes
2. Report to the user:
   - Which ACs are still failing and why
   - What was attempted in each cycle
   - The worktree path (preserved for manual inspection)
3. Ask the user how to proceed

## Phase 6: Merge to Main

Once QA passes:

1. In the worktree, rebase onto latest main:
   ```
   git rebase main
   ```
2. If rebase conflicts: resolve them, then re-run QA to verify nothing broke
3. On main, fast-forward merge:
   ```
   git merge --ff-only <branch-name>
   ```
4. Run the full test suite on main:
   ```
   uv run pytest tests/ -q
   ```
5. If full suite passes: cleanup worktree and branch
6. If full suite fails: stop and report the regression to the user

## Phase 7: Cleanup

- Remove the worktree: `git worktree remove <path> --force`
- Delete the feature branch: `git branch -D <branch-name>`
- Prune: `git worktree prune`
- Report final status to the user:
  - Task completed
  - Tests passing (count)
  - Commits merged
  - Cycle count (1 = first try, 2+ = had to loop)

## Parallel Execution

If multiple tasks are provided (`/dev-team #42 #43 #44`):
1. Check dependencies between them — if independent, run all in parallel
2. If there are dependencies, batch them (merge dependees first)
3. Each task gets its own worktree and full Implement→Review→QA cycle
4. Merge in dependency order (or any order if independent)
5. After each merge, rebase remaining worktrees onto new main

## Key Principles

- **ACs are the contract.** Everything flows from them. Vague ACs = bad code.
- **QA is the hard gate.** No shortcuts, no "close enough." Every AC passes or the cycle repeats.
- **Reviewers don't rewrite.** They identify problems. Implementers fix them.
- **Worktrees are disposable.** If things go sideways after 3 cycles, the user still has a clean main.
- **The loop is the safety net.** Most tasks pass on cycle 1. The loop exists for edge cases, not as the normal path.
