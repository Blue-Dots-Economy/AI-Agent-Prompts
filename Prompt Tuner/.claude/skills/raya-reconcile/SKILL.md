---
name: raya-reconcile
description: Before editing a live voice agent, check whether the prompt running on Raya matches the repo, and if not, who is ahead. Normal path is the API (`raya_deploy.py diff`, then `pull` when live is ahead); the browser path pulls the live prompt from the Raya console to a file when the API read is empty or unstable. Never deploys and never edits prompt content: the only write is adopting the live prompt into the repo when live is ahead. Use before any fix on a Raya agent, or when the user asks "is the live bot the same as the repo?", "did someone edit the bot on the console?", "who is ahead, live or repo?", "pull the live prompt", "reconcile <bot>", or wants a repo-vs-Raya sync map of all bots.
---

# Raya reconcile (repo ↔ live)

**What it produces:** for each target, one verdict, `IN SYNC` or `DRIFT` with who is ahead, and when live
is ahead, the live prompt adopted into the repo and committed BEFORE anyone edits it. Only the verdict
and the diff reach the conversation, never the whole prompt.

**Why:** the team edits some agents directly on the Raya console (most importantly the real job
inventory / `job_id`s on inbound bots). Editing and deploying a repo file that is behind live overwrites
that content; this is how the real Maya Inbound inventory was once replaced with placeholders and every
`apply_job` failed.

**Fast path (API, works for most conversation prompts):**
```bash
python3 scripts/raya_deploy.py diff <target>          # "in sync", or "DRIFTED" + unified diff (remote → local)
python3 scripts/raya_deploy.py pull <target> --dry-run   # live is ahead: preview adopting live into the repo
python3 scripts/raya_deploy.py pull <target>          # adopt it (snapshots the repo file first), then commit
```
Use the browser path below only when the API read is empty, unstable, or fails.

## Prerequisites

- `raya/.env` with `RAYA_BASE_URL` and `RAYA_API_TOKEN` (git-ignored). A target with `"account"` in
  `raya/agents.json` uses that account's token (`RAYA_API_TOKEN__<ACCOUNT>`); a 404 "not found on account"
  means the bot lives on another account.
- Target ids, files and uuids come from `raya/agents.json`: `python3 scripts/raya_deploy.py targets`
  (local, no network). Targets marked unmapped there have no live agent yet and cannot be reconciled.
- Browser path only: Claude in Chrome, logged into `console.getraya.app`.

## Procedure (per target)

1. **Resolve the target**: `python3 scripts/raya_deploy.py targets`. A selector can be a target id, a
   file path, or `agent[:lang][:dir]`; `diff` takes `--all` for every deployable target.
2. **Diff over the API**: `python3 scripts/raya_deploy.py diff <target>`. Blank lines at the start and
   end are ignored (the console adds one), so `in sync` means the content matches.
   - **Read a DRIFTED result before trusting it.** If the "remote" side is empty, or is the default
     `You are a helpful assistant`, the GET failed to return the prompt; that is not drift. Switch to
     the browser path.
   - `python3 scripts/raya_deploy.py status` gives a one-line `in-sync | drifted | unmapped |
     missing-file | unreachable` per deployable target: the quick sync map.
3. **Decide who is ahead** from the diff (`-` lines are live only, `+` lines are repo only):
   - **In sync**: nothing to reconcile; go to the edit.
   - **Repo ahead** (repo = live + fixes not yet deployed, and nothing in live is missing from the repo):
     the repo wins; make the new fix on top and deploy the repo.
   - **Raya ahead** (live has content the repo lacks): adopt live FIRST, step 4.
   - **Both changed**: adopt live first (step 4), then re-apply the repo-only changes on top through
     `/update-prompt`. Never deploy over live-only content.
4. **Adopt live into the repo**: `python3 scripts/raya_deploy.py pull <target> --dry-run` to preview,
   then without `--dry-run`. `pull` requires two agreeing GETs, refuses the empty or default prompt and
   any read smaller than half the repo file (or 2 KB), warns if live also carries placeholder `job_id`s,
   and snapshots the repo file before writing. Review `git diff`, commit the reconciliation on its own,
   then make the fix. If `pull` refuses ("GET is UNSTABLE", "no prompt"), use the browser path.
   If the target is a mirror, run `/sync-check` after adopting it: a console edit made in one language
   is drift for the others.

## Browser path (when the API read is empty or unstable)

**Token rule: never print or return the full prompt into the conversation** (it can be 70 KB or more).
Route it to a file and diff on disk.

**a. Quick check without downloading (sha compare).** Hash the repo file the way the script compares it:
```bash
python3 -c "import hashlib,sys;t=open(sys.argv[1],encoding='utf-8').read().replace('\r\n','\n').strip('\n');print(len(t.encode()),hashlib.sha256(t.encode()).hexdigest())" "<repo file>"
```
Open `https://console.getraya.app/agents/<uuid>` (Instructions tab) and run in the page:
```js
(async () => {
  const cms=[...document.querySelectorAll('.CodeMirror')].map(e=>e.CodeMirror).filter(Boolean);
  const v=cms.sort((a,b)=>b.getValue().length-a.getValue().length)[0].getValue()   // instructions = longest editor
          .replace(/\r\n/g,'\n').replace(/^\n+|\n+$/g,'');
  const h=[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(v)))]
          .map(b=>b.toString(16).padStart(2,'0')).join('');
  return {bytes:new TextEncoder().encode(v).length, sha256:h};
})()
```
Same sha256: IN SYNC, stop. Different: download and diff (b).

**b. Download and diff.** On the same page run:
```js
(() => {
  const cms=[...document.querySelectorAll('.CodeMirror')].map(e=>e.CodeMirror).filter(Boolean);
  const v=cms.sort((a,b)=>b.getValue().length-a.getValue().length)[0].getValue();
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([v],{type:'text/markdown'}));
  a.download='raya-live-<TARGET>.md';        // put the target id here, e.g. raya-live-maya-hi-out.md
  document.body.appendChild(a); a.click(); a.remove();
  return {len:v.length};
})()
```
The editor is EasyMDE / CodeMirror holding raw markdown, so the download is byte-exact. Then:
```bash
python3 scripts/raya_deploy.py reconcile <target>     # local only; newest ~/Downloads/raya-live-<target>*.md, or --live <path>
```
It prints `VERDICT: IN SYNC`, or `VERDICT: DRIFT` with line counts and the diff (`-` live only, `+` repo
only). Decide who is ahead as in step 3. If Raya is ahead, snapshot first
(`scripts/prompt-version.sh save <agent> pre-reconcile-<target> "adopt live"`), copy the download over the
repo file, review `git diff`, commit, and only then make the fix.

## Then

Make the fix on the reconciled base with `/update-prompt` (or `/port-feature`), and deploy with
`python3 scripts/raya_deploy.py deploy <target>`, which verifies the saved prompt against the update
response. Never deploy by editing the agent in the Raya console: it skips the guards, can clobber
console-only content, and its Save can report an error on success.

## Report to the user

One line per target, in plain words: "the live bot matches the repo", "someone changed the live bot on
the console (N lines, e.g. the job list); I copied it into the repo before changing anything", or "the
repo has fixes not yet live". No prompt text beyond the few changed lines.
