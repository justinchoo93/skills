#!/usr/bin/env python3
"""List codex-loop jobs."""

from __future__ import annotations

from common import iter_jobs


def main() -> int:
    jobs = iter_jobs()
    if not jobs:
        print("no codex-loop jobs found")
        return 0

    print("job_id\tkind\tinterval\tstatus\tnext_run_at\tname")
    for job in jobs:
        print(
            "\t".join(
                [
                    job["id"],
                    job["kind"],
                    job["interval"],
                    job.get("last_status", "scheduled"),
                    job["next_run_at"],
                    job["name"],
                ]
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
