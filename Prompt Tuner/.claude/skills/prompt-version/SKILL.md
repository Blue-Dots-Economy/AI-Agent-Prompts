---
name: prompt-version
description: Save, list, compare and restore snapshots of a bot's prompt files so a known-good version is one command away, without depending on git. Use when someone says "save a copy before I change this", "roll back the last change", "the fix broke the bot, undo it", "what changed since yesterday's version", "show me the snapshots", "mark this as stable", or before any risky edit, for any bot in the repo (every bot folder is found automatically).
---

# Prompt Version History

**What it does:** copies a bot folder's prompt files into `versions/<Bot>/<stamp>__<label>/` and
puts them back on request. All through `scripts/prompt-version.sh`, run from the repo root with
`bash`. It changes **repo files only**: restoring does not change what is live on Raya.

**Fast path:**
- Before an edit: `bash scripts/prompt-version.sh save <Bot> pre-<slug> "<why>"`
- To undo: `bash scripts/prompt-version.sh list <Bot>`, then `diff`, then `restore`, then redeploy.

## Commands

```
bash scripts/prompt-version.sh save    <Bot> <label> [note...]   # snapshot the folder now
bash scripts/prompt-version.sh list    [Bot]                     # list snapshots (all bots if omitted)
bash scripts/prompt-version.sh diff    <Bot> <label> [file]      # snapshot vs current files
bash scripts/prompt-version.sh restore <Bot> <label>             # put the snapshot back (saves current first)
bash scripts/prompt-version.sh tag     <Bot> <label> [note...]   # git tag on the last commit (see limits)
```

- `<Bot>` is a **top-level folder** that holds a `CHANGELOG.md` and at least one other `.md`
  file, e.g. `KKB`, `KKB-Slim`, `DKB`, `Maya`, `TRRAIN`. Folders are discovered, not hard-coded:
  matching ignores case and treats `-`/`_` as spaces, so `purple-dots` finds `Purple Dots`. An
  unknown name prints the list of known bots.
- `<label>`: a short kebab slug. `pre-<change>` for a rollback point, `stable-<date>` for a version
  a live call has proven.
- A snapshot copies **every** `.md` file at the top of the folder except `CHANGELOG.md`: all
  languages, directions, backends, and the memory and output prompts.
- The note lands in `versions/<Bot>/HISTORY.md` (tracked in git); snapshot bodies are git-ignored,
  so they exist only on the machine that made them.
- `scripts/raya_deploy.py deploy` takes its own snapshot (`pre-deploy-<target>-<stamp>`) before
  every push; `list` shows those too.

## Rolling back safely

1. `list <Bot>`, pick the label, then `diff <Bot> <label>` to see exactly what will change.
2. **`restore` puts back every file in the snapshot**, not just the one that broke. If other files
   in the folder changed since (another variant's fix, a memory edit), restoring undoes them too.
   To roll back one file, copy it alone from `versions/<Bot>/<stamp>__<label>/<file>` after checking
   `diff <Bot> <label> "<file>"`. Files created after the snapshot are left in place.
3. Restore saves the current state first (`pre-restore-<stamp>`), so the rollback is reversible.
4. **Redeploy** each affected target (`python3 scripts/raya_deploy.py deploy <target-id>`; for
   memory and output prompts, the deploy step in `/update-memory` or `/update-output`). Until then
   the live bot still runs the broken version.
5. Add a `CHANGELOG.md` entry saying what was rolled back and why. The rolled-back behaviour is
   DEPLOYED, NOT VERIFIED until a call shows it.

## Limits to know (tell the user when they bite)

- **`tag` fails on the default macOS bash** (3.2): it uses `${agent,,}`, which bash 3.2 rejects
  with "bad substitution", so no tag is made. Until the script is fixed, tag by hand:
  `git tag -a <bot-lowercase>-<label> -m "<note>"`. A tag marks the last commit, not uncommitted
  files.
- A snapshot covers the repo files only. Live-only content (a console edit, tool descriptions and
  schemas, memory or output prompts that differ per agent) is not in it: save live copies with
  `scripts/raya_deploy.py pull` or into `raya/live-snapshots/` (see `/update-memory`) before
  overwriting them.
- The folder is resolved from the deploy manifest's `agent` field when `raya_deploy.py` snapshots:
  a target whose `agent` does not match its folder snapshots the wrong folder.
