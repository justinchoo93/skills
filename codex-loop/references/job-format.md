# Job Format

The scheduler stores state under `~/.codex-loop` by default. Override with `CODEX_LOOP_HOME` for tests.

## Layout

```text
~/.codex-loop/
  jobs/
    <job_id>.json
  logs/
    dispatcher.log
    <job_id>.log
  locks/
    <job_id>.lock
  output/
    <job_id>.last-message.txt
```

## Job JSON

Each job file looks like:

```json
{
  "id": "c9c6f6db0a12",
  "name": "check the deploy status",
  "kind": "codex-prompt",
  "interval": "5m",
  "interval_seconds": 300,
  "cwd": "/Users/justin/Documents/code/gf-ecom",
  "enabled": true,
  "created_at": "2026-03-18T17:00:00Z",
  "next_run_at": "2026-03-18T17:05:00Z",
  "last_run_at": null,
  "last_finished_at": null,
  "last_exit_code": null,
  "last_status": "scheduled",
  "log_path": "/Users/justin/.codex-loop/logs/c9c6f6db0a12.log",
  "last_message_path": "/Users/justin/.codex-loop/output/c9c6f6db0a12.last-message.txt",
  "lock_path": "/Users/justin/.codex-loop/locks/c9c6f6db0a12.lock",
  "prompt": "check the deploy status and summarize anything new",
  "codex_path": "/opt/homebrew/bin/codex",
  "execution_strategy": "resume",
  "session_id": "019cf751-c874-7211-9ebe-797b5a8ab9b7",
  "sandbox": "read-only",
  "search": false,
  "skip_git_repo_check": false
}
```

For prompt jobs:
- `execution_strategy: "resume"` means `codex exec resume <session_id> ...`
- `execution_strategy: "fresh"` means a new `codex exec ...` run is started instead
- `session_id` is captured automatically from `CODEX_THREAD_ID` when the job is created inside a live Codex session, or can be set explicitly with `--session-id`
- fresh jobs keep the old `--sandbox` and `--search` behavior; resume jobs prioritize session reuse and currently do not add a separate search toggle

Shell jobs replace the prompt fields with:

```json
{
  "kind": "shell-command",
  "command": "bundle exec rspec spec/models/user_spec.rb"
}
```

## Cron backend

The cron backend installs one managed block:

```cron
# BEGIN CODEX_LOOP_DISPATCHER
PATH=...
HOME=...
CODEX_LOOP_HOME=...
* * * * * /usr/bin/python3 .../execute_due_jobs.py >> .../dispatcher.log 2>&1
# END CODEX_LOOP_DISPATCHER
```

It is intentionally a single dispatcher entry, not one crontab line per job.
