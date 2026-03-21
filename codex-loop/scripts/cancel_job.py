#!/usr/bin/env python3
"""Cancel a codex-loop job."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import job_file, load_job, maybe_remove_dispatcher


def main() -> int:
    parser = argparse.ArgumentParser(description="Cancel a codex-loop job")
    parser.add_argument("--job-id", required=True, help="Job ID from list_jobs.py")
    args = parser.parse_args()

    job = load_job(args.job_id)
    job_path = job_file(args.job_id)
    job_path.unlink(missing_ok=True)

    lock_path = Path(job["lock_path"])
    lock_path.unlink(missing_ok=True)

    maybe_remove_dispatcher()

    print(f"cancelled job {args.job_id}")
    print(f"  name: {job['name']}")
    print(f"  log retained at: {job['log_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
