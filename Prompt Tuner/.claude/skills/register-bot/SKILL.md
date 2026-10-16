---
name: register-bot
description: File a NEW bot (or a new language or direction of an existing bot) into the Prompt Tuner so every skill and script can find it. Creates the bot's folder, prompt files and CHANGELOG, adds it to the path map in the root CLAUDE.md, writes its raya/agents.json target(s) with Raya ids copied by hand, regenerates the regression fleet, records its voice pair and open-issues list, then runs /prompt-analyser and /generate-test-cases automatically. Use right after /onboard, or when someone says "add this bot to the tuner", "register the new bot", "set up Orange Dots", "wire up Purple Dots", "add a Tamil version", "make this bot deployable", or a skill fails because a bot is not in the path map or agents.json.
---

# Register Bot: make a new bot findable by every tool

**What it produces:** the bot's folder with its prompt files and `CHANGELOG.md`; path-map rows in the
root `CLAUDE.md`; one `raya/agents.json` target per language and direction; a regenerated
`raya/regression/fleet.json`; its language and voice pair in `raya/voices.json`; its open-issues list
at `raya/intake/<bot-id>.md`. Then it runs `/prompt-analyser` and `/generate-test-cases` (which
delivers the test-case Google Sheet).

**When:** after `/onboard`, or when `/translate-prompt` adds a language (the *variant* path).

**Fast path:** recon (1) → files (2) → path map (3) → `agents.json` (4, 5) → fleet (6) → voices, size,
open issues (7) → verify (8) → hand-offs (9).

**It writes no prompt prose and deploys nothing.** Prompt content comes from the customer (pasted
verbatim), `/update-prompt` or `/translate-prompt`. Deploy is `scripts/raya_deploy.py deploy`, later and
separately. Assume N projects, N bots, N languages: never hard-code a bot list or a language pair.

**Talking to the user:** this is bookkeeping, so do not narrate it. Ask only for what is missing from
the intake, in plain words; report in the short format at the end of step 8.

---

## Inputs (from `raya/intake/<bot-id>.md`; ask only for what is missing, never guess)

| Input | Example | Used for |
|---|---|---|
| Project | `orange-dots` / Orange Dots | `project` field; fleet project |
| Bot folder name | `Orange Dots` | folder, file names, `agent` |
| Languages, master first | `hi` (master), `mr` | one file and one target per language |
| Directions | outbound, inbound, or both | one target per language per direction |
| Prompts present | conversation / + memory / + output | which files; memory-block check |
| Backend tag | `signals` or none | `signals: true` on the target |
| Raya name + uuid per agent | from `raya_deploy.py list` | `raya_name`, `raya_agent_id`, name guard |
| Public-facing? | yes | safety-interrupt check (step 9) |

No Raya presence yet is fine: register with empty uuids and `deploy: false` (see *Not on Raya*).

---

## Procedure

### 1. Recon (read-only)

Read the root `CLAUDE.md` *File path map*, the whole of `raya/agents.json` (match its shape and key
order), and one existing `<Bot>/CHANGELOG.md`. Then:

```bash
cd "/Users/parthbansal/EkStep/Prompt Tuner"
python3 scripts/raya_deploy.py targets | grep -i "<bot>"   # already a target?
ls -d "<Bot>" 2>/dev/null; grep -n "<Bot>" CLAUDE.md      # folder / path-map row already there?
```

If any of it exists this is a **variant addition**: add only the missing files and rows; leave every
existing row untouched.

### 2. Folder and files

Folders are bot-named at the repo root; the project is metadata, not a folder level
(`scripts/prompt-version.sh` and `static_regression.py` both assume `<Bot>/<file>.md`).

```
<Bot>/
  <Bot> <Language>.md          # one per language, master first; language as its English name
  <Bot> Inbound <Language>.md  # only if inbound has its own prompt
  <Bot> Memory.md              # optional
  <Bot> Output.md              # optional
  CHANGELOG.md                 # always
```

Append a variant token after the language when there is one (`<Bot> Hindi Signals.md`).

- **Master file: paste the customer's prompt verbatim.** No reformatting, re-wrapping or reordering; it
  is the baseline every later diff is read against.
- **No empty stub files.** An empty file passes `targets --check` and a deploy of it would blank a live
  agent. A language gets a file and a target only once it has real content (`/translate-prompt` makes
  the others).
- **Memory prompt present?** Every conversation prompt must carry the memory block verbatim (root
  `CLAUDE.md` → *Memory injection block*). If one lacks it, do not patch it here: route to `/update-memory`.
- **Instructions written in Hindi/Kannada/other** in the pasted prompt are a bug: flag it for
  `/update-prompt`, do not fix it silently.
- **`CHANGELOG.md`**: copy the header format from an existing one and add:
  ```
  ## YYYY-MM-DD: Registered <Bot> in the Prompt Tuner
  - **Feedback/bug:** n/a, new bot registration (project: <project>)
  - **Change:** created <Bot>/ with <n> conversation prompt(s) (<languages>, master: <lang>), <memory/output?>;
    path-map rows, raya/agents.json target(s) <ids>, fleet regenerated, voices.json pair(s).
  - **Files:** <every file created or edited>
  ```

### 3. Root `CLAUDE.md` path map (additive only)

Never reword, reflow, reorder or delete an existing row, heading or rule; ask first if one seems wrong.
The existing table is wide (one column per language: KKB, DKB, Maya, KKB-Slim, TRRAIN today; read it,
don't trust this list). The first time a non-Blue-Dots project is registered:

1. Insert a `### Projects` index under the `## File path map` intro line
   (`| Project | Bots | Languages (master first) | Notes |`), with one sentence: *"Blue Dots keeps the
   wide table; every new project uses the long form, one row per bot and language. `raya/agents.json`
   is the machine source of truth; this map is the human index."*
2. Put the existing wide table, byte-identical, under `### Blue Dots: file paths`.
3. Append `### <Project>: file paths` in long form:
   `| Bot | Language | Conversation prompt | Memory | Output |`, one row per bot and language, master
   marked `hi (master)`.

Later bots of the same project just add rows.

### 4. `raya/agents.json` targets

**One entry per conversation prompt, per language, per direction, per variant.** Append to the end of
`targets`; touch nothing else. Required keys, in the file's order:

```json
{
  "id": "od-hi-out",
  "file": "Orange Dots/Orange Dots Hindi.md",
  "agent": "Orange Dots",
  "language": "hi",
  "direction": "outbound",
  "kind": "conversation",
  "profile": "conversation",
  "expected_name_contains": ["Orange Dots", "Hindi"],
  "raya_name": "Orange Dots Hindi",
  "raya_agent_id": { "prod": "", "staging": "" },
  "deploy": false,
  "project": "orange-dots"
}
```

- **`id`**: `<bot-key>-<iso>-<out|in>[-<variant>]`, lowercase, unique, permanent (reports, deploy
  history, the fleet and test cases all join on it; renaming orphans them).
- **`agent`** must equal the folder name: `raya_deploy.py deploy` snapshots by calling
  `prompt-version.sh save <agent>`, which resolves folders, so a mismatch snapshots the wrong bot or
  blocks the deploy.
- **`language`** is the ISO code (`hi`, `kn`, `mr`, `te`, `ta`, …); `"xx"` only for post-call prompts.
- **`profile`** must exist in `raya/endpoints.json` (`conversation` | `memory` | `output`).
- **`expected_name_contains`**: bot token AND language/variant token, so a Hindi prompt can never land
  on the Marathi agent. Tighten it once you see the real names from `list`.
- **`deploy: false` until the uuid is in hand**; flip to `true` in the same edit that pastes the uuid.
- **Optional keys** (add when true, never guess): `project` (record it; note no script reads it yet,
  see the report notes); `master: true` on the master target when the master is not Hindi (the static
  suite reads it); `signals: true` for a Signals-backend bot (drives the backend checks); `account` when
  the agent lives on a second Raya account (its key goes in `raya/.env` as `RAYA_API_TOKEN__<ACCOUNT>`);
  `max_prompt_bytes`, `proven_prompt_bytes`, `size_evidence` (step 7); `_note` when an entry needs
  explaining (clone source, repurposed uuid).
- **Memory / output prompts** get their own entries (`kind`/`profile` `memory`/`output`). Not separately
  deployable: `language: "xx"`, `direction: "postcall"`, `deploy: false` (copy `kkb-memory`). Deployed on
  the bot's own agent: reuse that agent's uuid (copy `trrain-hi-memory`, or `maya-out-memory` for a
  direction-scoped one).
- Validate: `python3 -c "import json;json.load(open('raya/agents.json'));print('ok')"`

### 5. The uuid rule (absolute)

**The Raya uuid is copied by hand from `python3 scripts/raya_deploy.py list` (prints `<uuid>  <name>`),
matched by the live agent's name. Never infer it from a file name, folder or another entry.**
`KKB/KKB Placeholder Inbound.md` is the Hindi inbound bot and `Maya/Maya Inbound.md` names no language
at all: name-guessing ships a prompt onto the wrong live agent. The tool uses the env matching
`RAYA_ENV` in `raya/.env`. Two similar names: stop and ask. Blank is safe; wrong is not.

### 6. Regression fleet (`raya/regression/fleet.json`)

The daily static suite (`raya/regression/static_regression.py`, run in the cloud each morning) reads
its bots straight from `raya/agents.json`: every `kind: conversation`, `deploy: true` target whose file
exists. So a `deploy: true` bot is checked from the next run; a `deploy: false` bot is not checked yet.

`fleet.json` is **generated; never hand-edit it**:

```bash
python3 scripts/build_fleet_manifest.py --print | head -40   # preview, writes nothing
python3 scripts/build_fleet_manifest.py                      # write raya/regression/fleet.json
python3 scripts/build_fleet_manifest.py --check              # "fleet.json current (N bots)"
```

Expected warnings for a new project today, until the script fixes in the report notes land:
`bot folder '<Bot>' has no project mapping in PROJECTS` (the builder's own project table, not the
`project` field), and, for a `deploy: false` target, `NOT covered by the daily suite`. Report them; do
not edit the scripts here. Check also that the new bot's `label`/`blurb` make sense to a reader: the
suite's `AGENT_BLURB` and backend wording are still keyed by known bot folders.

### 7. Voice pair, size and open-issues list

- **Voice pair:** `python3 scripts/raya_testcall.py whoami <uuid>` prints `language_id` and `voice_id`.
  If the language is not yet in `raya/voices.json` under the bot's account, add it with `source` (agent
  name + uuid prefix) and date. No pair available: ask LitWiz; never test a language on another
  language's voice.
- **Size:** `wc -c "<file>"` per conversation prompt; run
  `python3 scripts/prompt_size.py check "<file>" --target <id>`. After the first live call that proves
  the bot's tools fire, record `proven_prompt_bytes` and `size_evidence` (call id + date) on the target;
  a call where tools stopped firing at a given size sets `max_prompt_bytes` (analyser D116).
- **Open-issues list:** make sure `raya/intake/<bot-id>.md` exists with its issue table (from
  `/onboard`; if there was no intake, create it from `../onboard/reference/intake-template.md` with an
  empty table). Every later fixing or testing session reads it first and updates it last.

### 8. Verify (not registered until the target resolves)

```bash
cd "/Users/parthbansal/EkStep/Prompt Tuner"
python3 -c "import json;[json.load(open(f)) for f in ('raya/agents.json','raya/voices.json','raya/regression/fleet.json')];print('json ok')"
python3 scripts/raya_deploy.py targets | grep -i "<bot>"   # one row per variant, file? = ok
python3 scripts/raya_deploy.py targets --check            # "OK: every deploy:true target's file exists."
python3 scripts/build_fleet_manifest.py --check
bash scripts/prompt-version.sh list "<Bot>"               # "== <Bot> ==" ((no snapshots) is fine)
# once a uuid is set and deploy is true (read-only):
python3 scripts/raya_deploy.py status <target-id>         # unmapped | in-sync | drifted | missing-file | unreachable
python3 scripts/raya_deploy.py diff   <target-id>         # repo ahead is normal for a new bot
python3 raya/regression/static_regression.py              # rewrites latest-report.*; new bot appears, no other new failures
```

| Check | Pass | If not |
|---|---|---|
| `targets` | correct lang/dir, `file?` ok | fix the path; never create an empty file to satisfy it |
| `prompt-version.sh list` | resolves | `unknown agent`: folder lacks `CHANGELOG.md` + another `.md`; no snapshot means no deploy |
| `status` | `unmapped` while blank, then `in-sync`/`drifted` | `unreachable`: check `raya/.env` / `account`, not the manifest |
| `diff` | either direction | **live ahead**: `raya_deploy.py pull <id>` before any edit |
| static suite | same old findings plus the new bot's own | any other new failure: you touched something else; revert |

**Report** (short, plain): what was filed (files, target ids with uuid present or blank), anything still
TBD, warnings from step 6, and the next sentence they can type. Say **registered**, never "done" or
"working": nothing about behaviour is proven until a call is placed.

### 9. Hand-offs (run automatically, in order)

1. **`/prompt-analyser`** on the master prompt (read-only). For a public-facing bot, D121 (safety
   interrupt that works even mid-answer) must pass before go-live; a miss routes to `/update-prompt`.
2. **`/generate-test-cases`**: the test manifest (`raya/testcases/<bot-id>.md` / `.json`), personas per
   language, the bot's checklist, and the deliverable people use: **a Google Sheet in the house layout**
   linted by `scripts/testcase_sheet.py lint` (safety case and a language tab per language).
3. Offer **`/voice-test`** on the Smoke set: live calls, so confirm before dialling. Inbound targets are
   tested too (integer `out_did` on the inbound agent, then it dials the tester; `/voice-test` → Inbound bots).
4. If `/onboard` captured a digest email, remind the owner to add it to the `GMAIL_TO` secret.
5. A brand-new bot also needs an entry in `.claude/skills/port-feature/reference/agent-schemas.md`
   before `/update-prompt` or `/port-feature` can re-domain anything to it: flag it; `/update-prompt` owns it.

---

## Guardrails

- **Never deploys.** No `raya_deploy.py deploy` (not even `--dry-run`), no PATCH/POST, even if asked
  "and push it live": that is a separate, confirmed step after analysis and testing.
- **Write set:** the new bot's folder, `CLAUDE.md` (additive), `raya/agents.json` (appended entries),
  `raya/regression/fleet.json` (generated), `raya/voices.json` (new pairs), `raya/intake/<bot-id>.md`.
  Any other diff line is a mistake: revert it. Never edit another bot's prompt or the regression scripts.
- **Never invent a uuid**; never localize a `${variable}`, tool name or fixed param anywhere.
- **No empty prompt files, no placeholder inventory** (`deploy` refuses placeholder `job_id`s anyway).
- **Never commit `*.tools*.json` snapshots or secrets**; do not `git commit` or push from this skill.
  Show the diff and let the user commit (the repo is public and auto-pushes).
- **Proving behaviour comes later.** Registration is verified statically (step 8). Once prompt content
  changes, root `CLAUDE.md` → *Testing is mandatory* applies in full: a call id per fix, every language
  and direction tested on its own, inbound included.

### Not on Raya

Register with empty uuids and `deploy: false`, and tell the user plainly:
- **Works:** prompt improvements (`/update-prompt`), new languages (`/translate-prompt`), language
  checks (`/sync-check`), the prompt review (`/prompt-analyser`), test-case design and the Sheet
  (`/generate-test-cases`), snapshots and rollback (`prompt-version.sh`).
- **Does not work:** deploy, live/repo reconcile, test calls (`raya_testcall.py`, `raya_testrun.py`),
  reading call transcripts (`raya_call.py`), and today the daily static check too (it only covers
  `deploy: true` targets). With no transcripts we cannot fix bugs unless they send real transcripts.
