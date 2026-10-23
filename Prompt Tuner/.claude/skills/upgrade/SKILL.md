---
name: upgrade
description: Bring this copy of the Prompt Tuner up to date with the parent tuner repo (github.com/parthekstep/Prompt-Tuner, branch control-center) without touching this copy's own bots. Pulls the newest skills, scripts, checklists and docs with a three-way merge per file, keeps every local change, never touches bot folders, agents.json, intake, test cases or secrets, and hands back any file where both sides changed the same lines. Use when someone says "/upgrade", "upgrade the prompt tuner", "pull the latest tuner", "get the new skills", "sync with the parent tuner", "update the skills from the main repo", "my tuner copy is behind", or after Parth announces a tuner update. Run it once in each copy (Purple Dots, Orange Dots, any other).
---

# /upgrade: pull the parent tuner's latest into this copy

Teams run their own copy of the tuner. A fix made in the parent never reaches a copy on its own, and
copying files by hand loses either the parent's fixes or the copy's own changes. This skill does it
safely, with `scripts/tuner_upgrade.py`.

**What changes:** the shared machinery (skills, scripts, checklists, the language data, the docs).
**What never changes:** this copy's bots and its own records (bot folders, `raya/agents.json`,
`raya/divergences.json`, `raya/intake/`, `raya/testcases/`, `raya/personas/`, `raya/.env`, `secrets/`,
reports, snapshots). `CLAUDE.md`, `.gitignore` and `raya/voices.json` are merged: this copy's own lines
(its path map, its accounts) stay, the parent's new rules come in.

## Fast path

1. Make sure the work in this copy is saved: `git status` clean, or commit what is there first.
2. If this copy does not have `scripts/tuner_upgrade.py` yet (first upgrade), fetch just that file
   from the parent and save it to `scripts/` (one file, read-only download from the public repo:
   `https://raw.githubusercontent.com/parthekstep/Prompt-Tuner/control-center/scripts/tuner_upgrade.py`).
3. `python3 scripts/tuner_upgrade.py status`: what the parent changed since this copy last synced.
4. `python3 scripts/tuner_upgrade.py plan`: what will happen to each file. Tell the user in two or three
   lines: how many files update, how many merge, anything that looks surprising.
5. `python3 scripts/tuner_upgrade.py apply`.
6. Resolve any conflicts (below), then run `apply` again until it reports **0 conflicts**.
7. Check: `python3 -m py_compile scripts/*.py raya/regression/*.py`, then
   `python3 raya/regression/static_regression.py` if this copy has bots registered. Read the new
   `docs/FEEDBACK-*.md` or the parent's latest commit messages and tell the user, in plain words, the two
   or three changes that matter most for their bots.
8. Commit in this copy: "Tuner upgraded to <parent commit>". Push only if this copy's own rules say so.

If the script says **"This IS the parent tuner"**, you are in the parent: there is nothing to pull.
Copies pull from here.

## Conflicts

A conflict means this copy and the parent both changed the same lines of a file. The copy's file is left
exactly as it was; the merged version, with `<<<<<<< this copy` / `=======` / `>>>>>>> parent` markers,
is in `.tuner-upgrade/conflicts/<path>`.

Resolve each one by reading both sides, never by picking one wholesale:
- Start from the **parent's** text (it carries fixes the copy has not seen).
- Re-apply what this copy added on purpose: a rule for its own bot, a local process note, an account
  detail. If a local addition contradicts a new parent rule, ask the user which stands.
- Write the result to the real file, delete the conflict file, and run `apply` again. The sync point in
  `.tuner-upstream.json` only moves forward once there are no conflicts left.
- A conflict in a skill the copy changed a lot is a hint the change belongs in the parent. Offer to send
  it back to Parth so the next upgrade does not conflict again.

## How it decides (so you can explain it)

For each shared file it compares three versions: the one both sides last shared (the base), this copy's,
and the parent's latest. Parent unchanged since the base: keep the copy's. Copy unchanged: take the
parent's. Both changed: merge line by line; overlapping changes become a conflict. A file the parent
deleted is only deleted with `--allow-deletes`. The base is the commit recorded in `.tuner-upstream.json`
at the last sync; on a first sync the script finds it (the parent commit closest to this copy's files)
and prints how close it was. Options: `--repo` / `--branch` for a different parent (for example a future
Blue Dots organisation copy), `--base <commit>` to override the base when the guess is wrong.

## Guardrails

- Never run `apply` with unsaved work in the copy; the user must be able to `git diff` exactly what the
  upgrade changed.
- Never edit a bot prompt here. An upgrade can bring new checks that flag the copy's prompts; report those
  findings and route fixes through `/update-prompt` as usual.
- Never copy `raya/.env`, `secrets/` or a `*.tools*.json` snapshot between repos.
- Report in plain words (root `CLAUDE.md` → "How to report back"): what came in, what needed a decision,
  what to try next.
