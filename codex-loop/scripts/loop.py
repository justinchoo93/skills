#!/usr/bin/env python3
"""Claude-like wrapper entrypoint for codex-loop."""

from __future__ import annotations

import argparse
import sys

from cancel_job import main as cancel_main
from create_job import main as create_main
from list_jobs import main as list_main
from show_log import main as log_main


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create or manage recurring codex-loop jobs",
        usage=(
            "loop.py <interval> <prompt>\n"
            "       loop.py <interval> --command <shell command>\n"
            "       loop.py list\n"
            "       loop.py cancel <job_id>\n"
            "       loop.py logs <job_id>"
        ),
    )
    parser.add_argument("target", nargs="?", help="Interval for create, or subcommand")
    parser.add_argument("rest", nargs="*", help="Prompt text or subcommand args")
    parser.add_argument("--command", help="Create a shell-command job instead of a codex prompt job")
    parser.add_argument("--cwd", help="Working directory for the job")
    parser.add_argument("--name", help="Optional job name")
    parser.add_argument("--session-id", help="Codex session/thread id to resume for prompt jobs")
    parser.add_argument("--sandbox", default="read-only", help="Codex sandbox mode for prompt jobs")
    parser.add_argument("--search", action="store_true", help="Enable Codex web search for prompt jobs")
    parser.add_argument("--skip-git-repo-check", action="store_true")
    parser.add_argument("--no-install-backend", action="store_true")
    return parser


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()

    if not args.target:
        parser.error("expected an interval or subcommand")

    if args.target in {"list", "ls"}:
        return list_main()

    if args.target in {"cancel", "rm"}:
        if len(args.rest) != 1:
            parser.error("cancel expects exactly one job_id")
        sys.argv = ["cancel_job.py", "--job-id", args.rest[0]]
        return cancel_main()

    if args.target in {"logs", "log"}:
        if len(args.rest) != 1:
            parser.error("logs expects exactly one job_id")
        sys.argv = ["show_log.py", "--job-id", args.rest[0]]
        return log_main()

    interval = args.target
    if args.command:
        prompt_parts = []
    else:
        prompt_parts = args.rest

    if not args.command and not prompt_parts:
        parser.error("create mode expects a prompt or --command")

    create_argv = ["create_job.py", "--interval", interval]
    if args.cwd:
        create_argv.extend(["--cwd", args.cwd])
    if args.name:
        create_argv.extend(["--name", args.name])
    if args.session_id:
        create_argv.extend(["--session-id", args.session_id])
    if args.no_install_backend:
        create_argv.append("--no-install-backend")

    if args.command:
        create_argv.extend(["--command", args.command])
    else:
        create_argv.extend(["--sandbox", args.sandbox])
        if args.search:
            create_argv.append("--search")
        if args.skip_git_repo_check:
            create_argv.append("--skip-git-repo-check")
        create_argv.extend(["--prompt", " ".join(prompt_parts)])

    sys.argv = create_argv
    return create_main()


if __name__ == "__main__":
    raise SystemExit(main())
