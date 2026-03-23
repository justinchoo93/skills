#!/usr/bin/env python3
"""Shared helpers for the codex-loop skill."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
from pathlib import Path
from typing import Any, Dict, List


INTERVAL_PATTERN = re.compile(r"^(?P<value>\d+)(?P<unit>[smhd])$")
CRON_BEGIN = "# BEGIN CODEX_LOOP_DISPATCHER"
CRON_END = "# END CODEX_LOOP_DISPATCHER"


def state_home() -> Path:
    override = os.environ.get("CODEX_LOOP_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".codex-loop"


def jobs_dir() -> Path:
    return state_home() / "jobs"


def logs_dir() -> Path:
    return state_home() / "logs"


def locks_dir() -> Path:
    return state_home() / "locks"


def output_dir() -> Path:
    return state_home() / "output"


def ensure_dirs() -> None:
    for path in (jobs_dir(), logs_dir(), locks_dir(), output_dir()):
        path.mkdir(parents=True, exist_ok=True)


def utc_now() -> datetime:
    return datetime.now(UTC)


def isoformat_z(dt: datetime) -> str:
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_isoformat_z(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def parse_interval(raw: str) -> int:
    match = INTERVAL_PATTERN.match(raw)
    if not match:
        raise ValueError("interval must look like 5m, 15m, 1h, or 1d")

    value = int(match.group("value"))
    unit = match.group("unit")
    multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
    return value * multiplier


def job_file(job_id: str) -> Path:
    return jobs_dir() / f"{job_id}.json"


def load_job(job_id: str) -> Dict[str, Any]:
    with job_file(job_id).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_job(job: Dict[str, Any]) -> None:
    ensure_dirs()
    path = job_file(job["id"])
    with path.open("w", encoding="utf-8") as handle:
        json.dump(job, handle, indent=2, sort_keys=True)
        handle.write("\n")


def iter_jobs() -> List[Dict[str, Any]]:
    ensure_dirs()
    jobs = []
    for path in sorted(jobs_dir().glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            jobs.append(json.load(handle))
    return jobs


def codex_path() -> str:
    path = shutil.which("codex")
    if not path:
        raise RuntimeError("could not find `codex` on PATH")
    return path


def current_session_id() -> str | None:
    value = os.environ.get("CODEX_THREAD_ID")
    return value or None


def cron_dispatcher_entry() -> str:
    ensure_dirs()
    python_path = sys.executable
    dispatcher_path = Path(__file__).with_name("execute_due_jobs.py")
    dispatcher_log = logs_dir() / "dispatcher.log"
    return "\n".join(
        [
            CRON_BEGIN,
            "PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            f"HOME={Path.home()}",
            f"CODEX_LOOP_HOME={state_home()}",
            f'* * * * * {python_path} {dispatcher_path} >> {dispatcher_log} 2>&1',
            CRON_END,
        ]
    )


def current_crontab() -> str:
    result = subprocess.run(
        ["crontab", "-l"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return result.stdout
    stderr = (result.stderr or "").lower()
    if "no crontab for" in stderr:
        return ""
    raise RuntimeError(result.stderr.strip() or "failed to read crontab")


def strip_dispatcher_block(contents: str) -> str:
    lines = contents.splitlines()
    output: List[str] = []
    skipping = False

    for line in lines:
        if line.strip() == CRON_BEGIN:
            skipping = True
            continue
        if line.strip() == CRON_END:
            skipping = False
            continue
        if not skipping:
            output.append(line)

    stripped = "\n".join(output).strip()
    return f"{stripped}\n" if stripped else ""


def write_crontab(contents: str) -> None:
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as handle:
        handle.write(contents)
        temp_path = handle.name
    try:
        subprocess.run(["crontab", temp_path], check=True)
    finally:
        Path(temp_path).unlink(missing_ok=True)


def ensure_dispatcher_installed(*, dry_run: bool = False) -> str:
    existing = strip_dispatcher_block(current_crontab())
    dispatcher = cron_dispatcher_entry().strip()
    combined = f"{existing}{dispatcher}\n"
    if not dry_run:
        write_crontab(combined)
    return combined


def maybe_remove_dispatcher(*, dry_run: bool = False) -> str:
    ensure_dirs()
    if any(jobs_dir().glob("*.json")):
        return current_crontab()

    cleaned = strip_dispatcher_block(current_crontab())
    if not dry_run:
        write_crontab(cleaned)
    return cleaned


def append_job_log(job: Dict[str, Any], text: str) -> None:
    ensure_dirs()
    path = Path(job["log_path"])
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def lock_is_stale(lock_path: Path, *, max_age_hours: int = 24) -> bool:
    if not lock_path.exists():
        return False
    age = utc_now() - datetime.fromtimestamp(lock_path.stat().st_mtime, UTC)
    return age > timedelta(hours=max_age_hours)
