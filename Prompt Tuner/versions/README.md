# Prompt Version Snapshots

Local version history for the voice-agent prompts, so a last-stable copy is always one
command away — **without** relying on git commits/pushes (we don't push every change instantly).

Managed by [`scripts/prompt-version.sh`](../scripts/prompt-version.sh); see the `/prompt-version`
skill for full docs.

## Layout

```
versions/
  README.md                 ← this file (tracked)
  <Agent>/
    HISTORY.md               ← human-readable log of snapshots (tracked)
    <stamp>__<label>/        ← full snapshot of the agent's prompt files (git-ignored)
```

`<Agent>` ∈ `KKB | DKB | Maya`. Each snapshot copies every `*.md` in the agent's dir
except `CHANGELOG.md`.

## Quick use (from repo root)

```
scripts/prompt-version.sh save    Maya stable-2026-07-15 "verified good on live calls"
scripts/prompt-version.sh list    Maya
scripts/prompt-version.sh diff    Maya stable-2026-07-15
scripts/prompt-version.sh restore Maya stable-2026-07-15   # auto-saves current first
```

## Two layers ("Both")

- **File snapshots** (this folder) — instant, git-independent rollback. Bodies are git-ignored;
  `HISTORY.md` logs are tracked so the record survives in git.
- **Git tags** — durable, shareable markers on committed stable points
  (e.g. `baseline-2026-07-15`). Create with `scripts/prompt-version.sh tag <agent> <label>`
  or a repo-wide `git tag -a`.
