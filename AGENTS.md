# Skills Repository

Personal collection of Claude Code and Codex skills.

## Structure

Each subdirectory contains a skill with a `SKILL.md` defining its behavior.

## Adding a New Skill

Any skill added to this repo **must** be symlinked into the tool-specific skill directories. Default to **both** unless the user specifically says otherwise:

```sh
ln -s "$(pwd)/<skill-name>" ~/.claude/skills/<skill-name>
ln -s "$(pwd)/<skill-name>" ~/.codex/skills/<skill-name>
```
