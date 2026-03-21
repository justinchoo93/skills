#!/usr/bin/env python3
"""Execute a single codex-loop job."""

from __future__ import annotations

import argparse
import os
import subprocess
from datetime import timedelta
from pathlib import Path

from common import (
    append_job_log,
    isoformat_z,
    load_job,
    lock_is_stale,
    parse_isoformat_z,
    save_job,
    utc_now,
)


def acquire_lock(lock_path: Path) -> bool:
    if lock_is_stale(lock_path):
        lock_path.unlink(missing_ok=True)

    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False

    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(str(os.getpid()))
    return True


def codex_command(job: dict) -> list[str]:
    if job.get("execution_strategy") == "resume":
        return codex_resume_command(job)
    return codex_fresh_command(job)


def codex_fresh_command(job: dict) -> list[str]:
    command = [
        job["codex_path"],
        "exec",
        "-C",
        job["cwd"],
        "-a",
        "never",
        "-s",
        job.get("sandbox", "read-only"),
        "-o",
        job["last_message_path"],
    ]
    if job.get("search"):
        command.append("--search")
    if job.get("skip_git_repo_check"):
        command.append("--skip-git-repo-check")
    command.append(job["prompt"])
    return command


def codex_resume_command(job: dict) -> list[str]:
    session_id = job.get("session_id")
    if not session_id:
        raise ValueError("resume strategy requires session_id")

    command = [
        job["codex_path"],
        "exec",
        "resume",
        session_id,
        "-o",
        job["last_message_path"],
    ]
    if job.get("skip_git_repo_check"):
        command.append("--skip-git-repo-check")
    command.append(job["prompt"])
    return command


def shell_command(job: dict) -> list[str]:
    return ["/bin/zsh", "-lc", job["command"]]


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute one codex-loop job")
    parser.add_argument("--job-id", required=True)
    args = parser.parse_args()

    job = load_job(args.job_id)
    lock_path = Path(job["lock_path"])
    now = utc_now()

    if not acquire_lock(lock_path):
        append_job_log(job, f"[{isoformat_z(now)}] skipped run because job is already running\n")
        job["last_status"] = "skipped_locked"
        job["next_run_at"] = isoformat_z(now + timedelta(seconds=job["interval_seconds"]))
        save_job(job)
        return 0

    try:
        command = codex_command(job) if job["kind"] == "codex-prompt" else shell_command(job)
        append_job_log(job, f"[{isoformat_z(now)}] starting run\n$ {' '.join(command)}\n")

        result = subprocess.run(
            command,
            cwd=job["cwd"],
            capture_output=True,
            text=True,
            check=False,
        )

        finished_at = utc_now()
        if result.stdout:
            append_job_log(job, result.stdout)
            if not result.stdout.endswith("\n"):
                append_job_log(job, "\n")
        if result.stderr:
            append_job_log(job, result.stderr)
            if not result.stderr.endswith("\n"):
                append_job_log(job, "\n")

        append_job_log(job, f"[{isoformat_z(finished_at)}] finished with exit code {result.returncode}\n")

        job["last_run_at"] = isoformat_z(now)
        job["last_finished_at"] = isoformat_z(finished_at)
        job["last_exit_code"] = result.returncode
        job["last_status"] = "success" if result.returncode == 0 else "failed"
        save_job(job)
        return result.returncode
    finally:
        lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
