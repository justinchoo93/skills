---
name: exec-plan
description: Author, implement, or revise an ExecPlan (execution plan) — a self-contained, living design document a coding agent or novice can follow to deliver a working, observable feature or system change. Use when asked to write/draft/scope an ExecPlan or execution plan, to plan a complex feature or significant refactor before coding, or to implement/continue/revise an existing ExecPlan.
---

# ExecPlan

An ExecPlan is a design document that a coding agent — or a complete novice with only the current working tree and this one file — can follow to deliver a working, observable feature or system change. The bar is that it be **self-contained, self-sufficient, novice-guiding, and outcome-focused**: there is no memory of prior plans and no external context, so everything the reader needs lives in the file.

The full rules and rationale are in [references/methodology.md](references/methodology.md); the ready-to-fill structure is in [references/skeleton.md](references/skeleton.md). Read the methodology **in full** before authoring — do not work from memory of this page.

## First: defer to a project-local PLANS.md

Before doing anything, check whether the repository defines its own ExecPlan conventions:

- Look for `docs/PLANS.md`, `PLANS.md`, or a path referenced from `AGENTS.md`/`CLAUDE.md`.
- If one exists, **it is the source of truth** — read it in full and follow it to the letter, including its skeleton, section names, file location, and naming. The methodology reference is a generic fallback; the project's own doc wins on every conflict.
- Detect where plans live and how they are named (e.g. `docs/exec_plans/YYYY-MM-DD-<slug>.md`) and match it. If no convention exists, default to `docs/exec_plans/YYYY-MM-DD-<short-kebab-slug>.md`.

## Identify your mode

Determine which of these the request calls for, then follow the matching guidance in the methodology reference. In **every** mode, keep the four mandatory living sections current: `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective`.

- **Writing a new plan** — research the actual repo deeply (read the source, search the files and symbols you will touch, run the project/tests to learn current behavior), then fill out the skeleton in your own words. Anchor on observable outcomes, resolve ambiguity inside the plan, and write it to the detected location with the dated filename.
- **Implementing / continuing a plan** — read it top to bottom, then proceed to the next milestone autonomously; never stop to ask for "next steps." Update `Progress` at every stopping point (split partial work into done/remaining), verify each milestone's observable acceptance before moving on, and commit frequently.
- **Revising / discussing a plan** — record the decision and its rationale in the `Decision Log`, propagate the change across all sections (including the living ones), add a dated note at the bottom, and confirm the plan still reads start-to-finish from this file alone.
- **Researching an unknown** — when feasibility is uncertain, use explicit prototyping milestones (toy implementations, spikes) to validate the approach before committing to the full build. The methodology reference covers how to scope a prototype and decide whether to promote or discard it.
