#!/usr/bin/env python3
"""Show the current log for a codex-loop job."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import load_job


def main() -> int:
    parser = argparse.ArgumentParser(description="Show the log for a codex-loop job")
    parser.add_argument("--job-id", required=True)
    args = parser.parse_args()

    job = load_job(args.job_id)
    log_path = Path(job["log_path"])

    if not log_path.exists():
        print(f"no log file found for job {args.job_id}")
        return 0

    print(log_path.read_text(encoding="utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
