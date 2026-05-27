---
name: exec-plan
description: Author, implement, or revise an ExecPlan (execution plan) — a self-contained, living design document a coding agent or novice can follow to deliver a working, observable feature or system change. Use when asked to write/draft/scope an ExecPlan or execution plan, to plan a complex feature or significant refactor before coding, or to implement/continue/revise an existing ExecPlan.
---

# ExecPlan

An ExecPlan is a design document that a coding agent — or a complete novice with only the current working tree and this one file — can follow to deliver a working feature or system change. It is **self-contained, self-sufficient, novice-guiding, and outcome-focused**. That is the bar.

Treat the reader as a beginner to the repository: they have only the working tree and the single ExecPlan file. There is no memory of prior plans and no external context.

## First: defer to a project-local PLANS.md

Before doing anything, check whether the current repository defines its own ExecPlan conventions:

- Look for `docs/PLANS.md`, `PLANS.md`, or a path referenced from `AGENTS.md`/`CLAUDE.md`.
- If one exists, **it is the source of truth** — read it in full and follow it to the letter. The embedded methodology in this skill is a generic fallback; the project's own doc wins on every conflict (skeleton, section names, file location, naming).
- Also detect where plans live and how they are named (e.g. `docs/exec_plans/YYYY-MM-DD-<slug>.md`). Match the existing convention rather than inventing one. If none exists, default to `docs/exec_plans/YYYY-MM-DD-<short-kebab-slug>.md`.

If no project doc exists, use the canonical methodology in [references/methodology.md](references/methodology.md). Read it in full before writing — do not work from memory of these bullet points.

## The three modes

You will be in one of three modes. Identify which from the request.

### Writing a new ExecPlan

1. Read the project's PLANS.md (or the methodology reference) **in full**.
2. Research the actual repo deeply: read the source, search for the files and symbols you will touch, run the project/tests to understand current behavior. Embed what you learn in the plan in your own words — never point to external blogs or other plans.
3. Start from the skeleton in [references/skeleton.md](references/skeleton.md) and flesh it out. Keep every required living section: `Progress`, `Surprises & Discoveries`, `Decision Log`, `Outcomes & Retrospective`.
4. Anchor on **observable outcomes**: what the user can do after the change, the exact commands to run, and the output they should see. Acceptance is verifiable behavior, not internal attributes.
5. Resolve ambiguity inside the plan and explain why you chose that path. Do not outsource decisions to the reader.
6. Write to the detected location with the dated filename convention.

### Implementing / continuing an ExecPlan

1. Read the plan top to bottom. Re-read PLANS.md if it is not fresh in context.
2. Do **not** stop to ask for "next steps" — proceed to the next milestone autonomously, resolving ambiguities as you go.
3. Keep the plan current as a living document: update `Progress` at every stopping point (split a task into "done" / "remaining" if partial), log decisions in `Decision Log`, capture unexpected behavior in `Surprises & Discoveries` with short evidence (test output is ideal).
4. Commit frequently.
5. Each milestone must be independently verifiable. Run the tests/commands the plan specifies and confirm the observable acceptance before moving on.
6. At completion of a major task or the whole plan, write an `Outcomes & Retrospective` entry comparing the result to the original purpose.

### Revising / discussing an ExecPlan

1. Record the decision and its rationale in `Decision Log` so it is unambiguous *why* the change was made.
2. Propagate the change comprehensively across **all** sections, including the living-document sections.
3. Ensure the plan still reads start-to-finish as a self-contained document — someone must be able to restart from only this file.
4. Add a dated note at the bottom describing the change and the reason.

## Non-negotiables (do not violate, even under the project doc)

- **Self-contained**: all knowledge and instructions a novice needs are *in the file*. Define every term of art in plain language the first time it appears, and name where it manifests in the repo. No "as defined previously" / "see the architecture doc".
- **Living document**: revise it as progress is made and decisions land; each revision stays self-contained.
- **Demonstrably working**: it must produce observable behavior, not code that compiles but does nothing meaningful. Show how to prove it (end-to-end scenario, CLI invocation, HTTP transcript, or a test that fails before and passes after).
- **Idempotent and safe**: steps can be re-run without damage; risky/destructive steps include retry, backup, or rollback paths.
- **Prose-first**: write in sentences, not lists. Checklists are allowed *only* in `Progress` (where they are mandatory). Tables and long enumerations only when brevity would otherwise obscure meaning.

## Formatting envelope

- When the `.md` file's content **is only** the ExecPlan (the normal case for a file in `docs/exec_plans/`), write the markdown directly — **omit** the outer triple backticks.
- When embedding an ExecPlan inside a larger document or a chat reply, wrap it in exactly one ``` fenced block labeled `md`. Do **not** nest triple-backtick fences inside it — show commands, diffs, and transcripts as **indented** blocks so you never prematurely close the fence.
- Two newlines after every heading. Use `#`/`##` levels and correct ordered/unordered list syntax.
- Use timestamped checkboxes in `Progress` (e.g. `- [x] (2025-10-01 13:00Z) ...`) so rate of progress is visible.

See [references/methodology.md](references/methodology.md) for the complete rules and rationale, and [references/skeleton.md](references/skeleton.md) for the ready-to-fill structure.
