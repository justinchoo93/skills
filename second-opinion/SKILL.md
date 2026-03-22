---
name: second-opinion
description: Get a second opinion from another AI agent on the current conversation. Consults codex, claude, or gemini headlessly with full context. Use when you or the user want to cross-check an approach, verify a suggestion, or get an independent perspective. Usage (Claude Code) - /second-opinion [agent] [question]
---

# Second Opinion — Cross-Agent Consultation

You are being asked to consult another AI agent for a second opinion on the current conversation.

## Determine Your Identity

First, determine which agent you are:
- If you are **Claude** (Anthropic's Claude Code), your default consultation target is `codex`.
- If you are **Codex** (OpenAI's Codex CLI), your default consultation target is `claude`.
- If you are **Gemini** (Google's Gemini CLI), your default consultation target is `codex`.

You MUST NOT invoke yourself. If the user asks you to consult yourself, warn them and suggest a different agent.

## Parse the Request

Determine which agent to consult and what question to ask.

**If invoked as a Claude Code slash command**, the user's input is: `$ARGUMENTS`

**If invoked contextually** (e.g., as a Codex skill or Gemini skill), extract the target agent and question from the user's most recent message.

Parse rules:
- If the first word matches a known agent name (`codex`, `claude`, `gemini`) and it's NOT your own identity, use that agent and treat the rest as the question.
- If the first word is NOT a known agent name, use your default consultation target and treat the entire input as the question.
- If no question is provided, formulate one based on the most recent point of discussion.

## Step 0: Safety Check — Working Directory Scope

Check whether the current working directory is overly broad:
```bash
pwd
git rev-parse --show-toplevel 2>/dev/null
```

- If inside a git repo, use `git rev-parse --show-toplevel` as the working directory for the agent (not cwd).
- If cwd is the user's home directory (`~` or `/Users/*` with no project structure) and NOT inside a git repo, **warn the user** that the agent will have access to the entire home directory and ask if they want to proceed. If they do, continue. If not, abort.

## Step 1: Create Temp Files

Create secure temp files using `mktemp` (not fixed paths):
```bash
CONTEXT_FILE=$(mktemp /tmp/second-opinion-ctx-XXXXXX.md)
RESPONSE_FILE=$(mktemp /tmp/second-opinion-rsp-XXXXXX.md)
chmod 600 "$CONTEXT_FILE" "$RESPONSE_FILE"
```

Store these paths for use in subsequent steps.

## Step 2: Build Context Document

Write the context briefing to the temp context file. This is the most important step — the other agent has ZERO context about your conversation, so you must reconstruct it completely.

Focus on **artifacts and facts**, not prose narration. The goal is high-signal evidence, not a story.

Structure the document as:

```markdown
# Second Opinion Request

## Working Directory
[Project root path and brief description if known]

## Facts
[Bullet list of key decisions, constraints, and current state. Be factual, not narrative.]

## Relevant Artifacts
[Include actual code snippets, file contents, diffs, error messages, or command output that are central to the discussion. Use fenced code blocks with filenames. This is the most important section — raw artifacts > paraphrased summaries.]

## Alternatives Considered
[What other approaches were discussed and why they were accepted or rejected]

## Open Questions
[Unresolved concerns, trade-offs being weighed, things that feel uncertain]

## Question
[The specific question to answer. Be precise about what kind of feedback is wanted.]

## Instructions
You are being consulted for a second opinion. Another AI agent has been working with the user and wants your independent perspective. Please:
1. Evaluate the approach, code, or decision described above
2. Point out any issues, risks, or things that were missed
3. Suggest alternatives if you see better approaches
4. Be direct and specific — the user wants honest technical judgment, not validation

Do NOT modify any files. This is a review only.
```

Be accurate. Include enough raw artifacts that the reviewer can form their own judgment rather than relying on your characterization.

## Step 3: Invoke the Agent

### If target agent is `codex`:

First check if the working directory is a git repo:
```bash
git -C "$WORK_DIR" rev-parse --is-inside-work-tree 2>/dev/null
```

Then run (use 5-minute timeout):
```bash
codex exec \
  -s read-only \
  --ephemeral \
  -o "$RESPONSE_FILE" \
  [--skip-git-repo-check if NOT in a git repo] \
  -C "$WORK_DIR" \
  - < "$CONTEXT_FILE"
```

### If target agent is `claude`:

Run (use 5-minute timeout):
```bash
claude -p \
  --permission-mode default \
  --model sonnet \
  --no-session-persistence \
  --allowedTools "Read,Glob,Grep" \
  < "$CONTEXT_FILE" > "$RESPONSE_FILE"
```

### If target agent is `gemini`:

First check if gemini CLI is installed:
```bash
which gemini 2>/dev/null
```

If not installed, tell the user: "Gemini CLI is not installed." and stop. Do not guess the install command — check `gemini --help` or the official docs first.

If installed, check `gemini --help` to determine the correct headless invocation flags, then run with the context file piped via stdin and output captured to the response file.

## Step 4: Present the Response

Read the response file and present it formatted as:

---
**[Agent Name] says:**

[The agent's response, presented verbatim]

---

Do NOT add your own commentary, rebuttal, or opinion unless the user explicitly asks for it. The whole point is an independent perspective — let it stand on its own.

## Step 5: Clean Up

Always clean up temp files, even if earlier steps failed:
```bash
rm -f "$CONTEXT_FILE" "$RESPONSE_FILE"
```

## Error Handling

- If the agent CLI is not installed, tell the user and stop.
- If the agent fails or times out, show the error output and suggest the user try again or try a different agent.
- If the agent produces empty output, report that and suggest trying with a more specific question.
- If temp file cleanup fails, warn the user to manually remove files from `/tmp/second-opinion-*`.
