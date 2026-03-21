---
name: codex-loop
description: Create, list, cancel, and inspect recurring local jobs backed by a cron dispatcher. Use this when the user wants Claude-like looping behavior in Codex for prompts or shell commands, such as checking a build every 5 minutes, watching a PR, or running a repeated local task.
---

# Codex Loop

## Overview

This skill manages recurring local jobs for Codex. It creates a single cron-backed dispatcher and stores per-job state in `~/.codex-loop`, so future skills can schedule work without mutating one crontab entry per job.

## When to use it

Use this skill when the user wants any of these:
- a recurring local prompt loop like "run this every 5m"
- a scheduler primitive that another skill can build on
- a local watcher that should keep running after the current Codex turn ends
- create/list/cancel recurring jobs without editing crontab manually

Do not use this skill for:
- pipeline-specific logic
- GitHub- or Bitbucket-specific API polling
- notifications, unless another skill explicitly layers that on top

## Backend model

This skill uses:
- one cron dispatcher entry, installed once
- per-job JSON state under `~/.codex-loop/jobs`
- per-job logs under `~/.codex-loop/logs`

The dispatcher runs every minute and launches due jobs. Jobs can be:
- `codex-prompt` jobs, which run `codex exec` or `codex exec resume`
- `shell-command` jobs, which run `zsh -lc`

For format details, read [references/job-format.md](references/job-format.md).

## Core workflow

The intended UX is Claude-like:

- create a loop with `$codex-loop 5m check the deploy`
- inspect active loops with `$codex-loop list`
- stop one with `$codex-loop cancel <job_id>`
- read its output with `$codex-loop logs <job_id>`

The backing entrypoint is:

```bash
python3 ~/.codex/skills/codex-loop/scripts/loop.py ...
```

### Create a recurring job

For a Codex prompt loop:

```bash
python3 ~/.codex/skills/codex-loop/scripts/loop.py \
  5m \
  "check the deploy status and summarize anything new"
```

For a plain shell command:

```bash
python3 ~/.codex/skills/codex-loop/scripts/loop.py \
  15m \
  --command "bundle exec rspec spec/models/user_spec.rb"
```

Important defaults:
- prompt jobs created inside a live Codex session capture `CODEX_THREAD_ID` automatically and prefer `codex exec resume <session_id> ...`
- prompt jobs created outside a live Codex session fall back to fresh `codex exec -a never -s read-only`
- jobs default to the current working directory unless `--cwd` is passed
- the first run happens on the next dispatcher tick
- the cron dispatcher is installed automatically unless `--no-install-backend` is passed

Optional prompt-job override:

```bash
python3 ~/.codex/skills/codex-loop/scripts/loop.py \
  5m \
  --session-id 019cf751-c874-7211-9ebe-797b5a8ab9b7 \
  "use \$bitbucket-pipeline-watch for PR 813 in this repo"
```

This is the intended chaining model for future watcher skills: `codex-loop` schedules the prompt, and the prompt itself can invoke another skill.

### List jobs

```bash
python3 ~/.codex/skills/codex-loop/scripts/loop.py list
```

### Cancel a job

```bash
python3 ~/.codex/skills/codex-loop/scripts/loop.py cancel <job_id>
```

If the cancelled job is the last active job, the dispatcher cron entry is removed.

### Inspect logs

```bash
python3 ~/.codex/skills/codex-loop/scripts/loop.py logs <job_id>
```

## How Codex should use this skill

When the user asks for loop behavior, prefer this translation:
- user: `$codex-loop 5m check PR 813`
- run:
  ```bash
  python3 ~/.codex/skills/codex-loop/scripts/loop.py 5m "check PR 813"
  ```

For management requests:
- "show my loops" -> `loop.py list`
- "cancel that loop" -> `loop.py cancel <job_id>`
- "show the last output" -> `loop.py logs <job_id>`

## Safe operating assumptions

- Prefer `codex-prompt` jobs for read-only monitoring or summarization work.
- Prefer creating prompt jobs from inside the Codex session whose context you want to reuse.
- Prefer `shell-command` jobs for deterministic wrappers or future watcher scripts.
- If a job is still running when it becomes due again, the next due tick is skipped rather than overlapped.
- This skill is local-machine automation only. It does not promise server-side durability.
- Resume jobs depend on the captured session id remaining valid. If that session disappears, recreate the job.

## Validation

When changing this skill:
- run the skill validator
- smoke test create/list/cancel with `CODEX_LOOP_HOME=$(mktemp -d)`
- use `--no-install-backend` in tests to avoid touching the real crontab
