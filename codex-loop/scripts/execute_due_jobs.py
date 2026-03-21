#!/usr/bin/env python3
"""Cron dispatcher for codex-loop jobs."""

from __future__ import annotations

import subprocess
import sys
from datetime import timedelta
from pathlib import Path

from common import append_job_log, iter_jobs, isoformat_z, parse_isoformat_z, save_job, utc_now


def main() -> int:
    now = utc_now()
    runner = Path(__file__).with_name("execute_job.py")

    for job in iter_jobs():
        if not job.get("enabled", True):
            continue

        if parse_isoformat_z(job["next_run_at"]) > now:
            continue

        job["next_run_at"] = isoformat_z(now + timedelta(seconds=job["interval_seconds"]))
        save_job(job)
        append_job_log(job, f"\n[{isoformat_z(now)}] dispatcher scheduled run\n")

        subprocess.Popen(
            [sys.executable, str(runner), "--job-id", job["id"]],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
