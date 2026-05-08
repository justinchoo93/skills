---
name: dev-team
description: /dev-team — Implement a task with a 4-agent team (Planner, Implementer, Reviewer, QA). Takes GitHub issues or inline descriptions through the full lifecycle from acceptance criteria to merged code.
---

# /dev-team — Implement a task with a 4-agent team

You are orchestrating a development team of four agents: **Planner**, **Implementer**, **Reviewer**, and **QA**. Your job is to take a task through the full lifecycle from acceptance criteria to merged code.

## Input

The user provides either:
- A GitHub issue number: `/dev-team #42`
- An inline task description: `/dev-team "add rate limiting to the API"`
- Multiple tasks: `/dev-team #42 #43 #44` (run in parallel if no dependencies)

The argument is: $ARGUMENTS

If the input is a GitHub issue, fetch it before Phase 1:
```
gh issue view <number> --json title,body
```

## Phase 0: Create Worktree

Create an isolated worktree for this task before any agent runs. All subsequent phases (Plan, Implement, Review, QA) operate inside this worktree.

```
Branch naming: feat/<short-descriptive-name>
```

Spawn the Planner in Phase 1 with `isolation: "worktree"` so the Agent tool creates the worktree automatically. Capture the returned worktree path and reuse it for every subsequent agent in this task.

## Phase 1: Plan (Planner Agent)

**This phase is a hard prerequisite. Do NOT proceed to implementation without a comprehensive plan and clear, testable ACs.**

Spawn a **Planner** agent (Agent tool, `isolation: "worktree"`) with:
- The task description (issue body or inline text)
- The original input form (issue # or inline) so it can decide whether to fetch additional context

**The Planner must think the hardest.** Instruct it explicitly to use deep, deliberate reasoning — this is the highest-leverage phase, and shallow planning compounds into bad implementation.

The Planner's job:
1. **Gather context.** Read existing code in the worktree to understand patterns, conventions, related modules, and what already exists that can be reused. Do not skim — understand.
2. **Refine or author acceptance criteria.** Every AC must be:
   - **An observable user behavior** — describes what a user can see, do, or experience. Frame ACs around the intended user journey, not implementation details.
   - **Testable from the user's perspective** — verifiable by exercising the product the way a user would (clicking buttons, navigating pages, hitting endpoints), not by inspecting internal state.
   - **Independent** — can be verified in isolation.

   **Bad AC:** "Run unit tests for the add-machine module."
   **Good AC:** "User clicks the 'Add Machine' button on the dashboard; the Add Machine modal opens and is visible with name/serial fields and a Save button."

   **Bad AC:** "Validation logic returns false on empty input."
   **Good AC:** "User submits the form with the name field empty; an inline error 'Name is required' appears below the field and the form does not submit."

3. **Enumerate edge cases.** Empty states, error states, race conditions, permissions, network failures, large inputs, concurrency, accessibility paths — anything a user could plausibly hit. List them explicitly so they become ACs or known non-goals.
4. **Produce a comprehensive implementation plan.** File-level changes, new modules, data flow, integration points, dependencies on existing code, and the order of operations. The Implementer will follow this plan.
5. **Ask clarifying questions** (use AskUserQuestion) if there are gaps in the brief, ambiguous requirements, or unclear intent. Better to surface a question now than guess wrong and burn a loop cycle later. Do NOT ask the user to approve the finished plan — only ask when something is genuinely unclear.

**Output of Phase 1:**
- A numbered list of ACs (each an observable user behavior).
- A list of edge cases considered (handled / out-of-scope, with reasoning).
- A concrete implementation plan with file paths and steps.

## Phase 2: Implement

Spawn an **Implementer** agent in the same worktree with a prompt containing:
- The task description
- The Planner's full output: ACs, edge cases, implementation plan
- List of existing utilities/patterns on main to reuse (from Planner context-gathering)
- Instruction to write code + tests, commit frequently
- Instruction to run **only targeted tests** relevant to the changes (the specific test files / test cases covering the modified code) — not the full suite. The full suite runs at merge time.
- **Instruction to invoke the `andrej-karpathy-skills:karpathy-guidelines` skill before writing any code, and to follow it throughout implementation** (surface assumptions, simplest viable solution, surgical changes, no speculative abstractions, verifiable success criteria)

The Implementer agent must:
1. Invoke the `andrej-karpathy-skills:karpathy-guidelines` skill at the start of the task and apply it to every implementation decision
2. Follow the Planner's implementation plan; deviate only with clear justification
3. Write implementation + tests following TDD
4. Run only targeted tests for the changed code before finishing
5. Commit with descriptive messages
6. Return: summary of what was built, files created/modified, targeted test results, and a brief note on any Karpathy-guideline tradeoffs (e.g. assumptions surfaced, simpler alternatives considered) or deviations from the plan

## Phase 3: Review

Spawn a **Reviewer** agent with the worktree path. The Reviewer checks:
- Code quality, readability, naming
- **Performance** — unnecessary loops, N+1 queries, blocking I/O on hot paths, memory or allocation hot spots, anything that will scale poorly
- Correct use of existing patterns/utilities from main (no reinventing)
- No security issues (injection, secrets in code, etc.)
- Tests are meaningful (not trivially passing)
- No unnecessary complexity (KISS, YAGNI)

The Reviewer returns either:
- **PASS** — code is ready for QA
- **ISSUES** — a numbered list of specific, actionable problems with file:line references

If ISSUES: do NOT proceed to QA. Go directly to Phase 5 (Loop).

## Phase 4: QA (Hard Gate)

Spawn a **QA** agent with the worktree path. The QA agent verifies each AC **from the actual user's standpoint** — not by reading code, not by running unit tests, but by exercising the product the way a user would.

The QA agent:
1. Reads each AC from Phase 1
2. For each AC, drives the product end-to-end using the appropriate user-facing tool:
   - **Web UI ACs:** use `playwright-cli` skill or another browser-automation tool to click, type, navigate, and observe rendered output (including screenshots when useful as evidence)
   - **HTTP API ACs:** issue real requests via `curl` / equivalent, inspect responses
   - **CLI ACs:** invoke the actual CLI binary and inspect output and exit codes
3. For each AC, records: **PASS** (with evidence — screenshot path, response body, observed output) or **FAIL** (with what was observed vs. expected)

Unit/integration tests are NOT sufficient evidence here. The QA gate is about whether the user-visible behavior matches the AC.

**ALL ACs must pass. This is a hard gate — no exceptions, no partial credit.**

The QA agent returns a checklist:
```
AC 1: [PASS/FAIL] — <user-observable evidence>
AC 2: [PASS/FAIL] — <user-observable evidence>
...
VERDICT: ALL PASS / X of Y FAILED
```

If ALL PASS: proceed to Phase 6 (Merge).
If ANY FAIL: proceed to Phase 5 (Loop).

## Phase 5: Loop (Max 3 Cycles)

Collect feedback from the Reviewer (if ISSUES) and/or QA (if FAILs). Send the Implementer agent back into the same worktree with:

- The specific issues/failures
- The observed-vs-expected evidence from QA
- Instruction to fix ONLY the reported issues (no scope creep)
- Instruction to re-invoke the `andrej-karpathy-skills:karpathy-guidelines` skill and apply it to the fix (surgical change, no speculative refactors)

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
- If the task originated from a GitHub issue (the original `/dev-team` argument was `#<number>`), close it with a comment linking to the merge commit:
  ```
  gh issue close <number> --comment "Resolved in $(git rev-parse HEAD) on main."
  ```
  Skip this step for inline tasks. If the close fails (already closed, missing permissions), report it but do not treat it as a task failure.
- Report final status to the user:
  - Task completed
  - Tests passing (count)
  - Commits merged
  - Cycle count (1 = first try, 2+ = had to loop)
  - Issue closed (if applicable)

## Parallel Execution

If multiple tasks are provided (`/dev-team #42 #43 #44`):
1. Check dependencies between them — if independent, run all in parallel
2. If there are dependencies, batch them (merge dependees first)
3. Each task gets its own worktree and full Plan→Implement→Review→QA cycle
4. Merge in dependency order (or any order if independent)
5. After each merge, rebase remaining worktrees onto new main

## Key Principles

- **The Planner thinks hardest.** Shallow planning is the most expensive mistake — every loop cycle downstream costs more than another minute of thinking up front.
- **ACs are user behaviors.** If you can't watch a user do it, it's not an AC.
- **QA is the hard gate.** Verified from the user's seat — clicks, requests, output. No "the unit tests pass" shortcuts.
- **Reviewers don't rewrite.** They identify problems. Implementers fix them.
- **Worktrees are disposable.** If things go sideways after 3 cycles, the user still has a clean main.
- **The loop is the safety net.** Most tasks pass on cycle 1. The loop exists for edge cases, not as the normal path.
