#!/usr/bin/env python3
"""Create a codex-loop recurring job."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path

from common import (
    codex_path,
    current_session_id,
    ensure_dispatcher_installed,
    ensure_dirs,
    isoformat_z,
    jobs_dir,
    logs_dir,
    output_dir,
    parse_interval,
    save_job,
    state_home,
    utc_now,
)


def build_job_id(seed: str) -> str:
    return hashlib.sha1(f"{seed}-{isoformat_z(utc_now())}".encode("utf-8")).hexdigest()[:12]


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a recurring local job for codex-loop")
    parser.add_argument("--interval", required=True, help="Interval like 5m, 15m, 1h, 1d")
    parser.add_argument("--cwd", default=os.getcwd(), help="Working directory for the job")
    parser.add_argument("--name", help="Optional human-readable job name")
    parser.add_argument("--sandbox", default="read-only", help="Codex sandbox mode for prompt jobs")
    parser.add_argument("--search", action="store_true", help="Enable Codex web search for prompt jobs")
    parser.add_argument("--session-id", help="Codex session/thread id to resume for prompt jobs")
    parser.add_argument(
        "--skip-git-repo-check",
        action="store_true",
        help="Pass --skip-git-repo-check to codex exec for prompt jobs",
    )
    parser.add_argument(
        "--no-install-backend",
        action="store_true",
        help="Do not install/update the cron dispatcher",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prompt", help="Prompt to run with codex exec")
    group.add_argument("--command", help="Shell command to run with zsh -lc")

    args = parser.parse_args()

    ensure_dirs()
    interval_seconds = parse_interval(args.interval)
    name = args.name or (args.prompt or args.command or "job").strip()[:80]
    job_id = build_job_id(name)
    now = utc_now()
    job_kind = "codex-prompt" if args.prompt else "shell-command"

    job = {
        "id": job_id,
        "name": name,
        "kind": job_kind,
        "interval": args.interval,
        "interval_seconds": interval_seconds,
        "cwd": str(Path(args.cwd).expanduser().resolve()),
        "enabled": True,
        "created_at": isoformat_z(now),
        "next_run_at": isoformat_z(now),
        "last_run_at": None,
        "last_finished_at": None,
        "last_exit_code": None,
        "last_status": "scheduled",
        "log_path": str((logs_dir() / f"{job_id}.log").resolve()),
        "last_message_path": str((output_dir() / f"{job_id}.last-message.txt").resolve()),
        "lock_path": str((state_home() / "locks" / f"{job_id}.lock").resolve()),
    }

    if args.prompt:
        session_id = args.session_id or current_session_id()
        execution_strategy = "resume" if session_id else "fresh"
        job.update(
            {
                "prompt": args.prompt,
                "codex_path": codex_path(),
                "execution_strategy": execution_strategy,
                "session_id": session_id,
                "sandbox": args.sandbox,
                "search": args.search,
                "skip_git_repo_check": args.skip_git_repo_check,
            }
        )
    else:
        job["command"] = args.command

    save_job(job)

    if not args.no_install_backend:
        ensure_dispatcher_installed()

    print(f"created job {job_id}")
    print(f"  name: {name}")
    print(f"  kind: {job_kind}")
    print(f"  interval: {args.interval}")
    print(f"  cwd: {job['cwd']}")
    print(f"  state dir: {jobs_dir()}")
    print(f"  log: {job['log_path']}")
    if args.prompt:
        print(f"  execution strategy: {job['execution_strategy']}")
        if job["session_id"]:
            print(f"  session id: {job['session_id']}")
        else:
            print("  session id: none (fresh codex exec fallback)")
    print(f"  backend installed: {not args.no_install_backend}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
