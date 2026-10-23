# Prompt Tuner — the end-to-end workflow

**The operating map.** If you have just been handed this repo with no verbal handover, read this
file top to bottom once, then keep it open. It tells you what the repo does, which skill to run for
any situation you will actually face, and which laws you may never break.

Read alongside it:
- `CLAUDE.md` (repo root) — **the law.** House rules, path map, testing tiers, deploy rules.
- `docs/MULTI-PROJECT-ROADMAP.md` — the spec of record for the multi-project move (gaps G1–G8).
- `.claude/skills/update-prompt/reference/prompt-anatomy.md` — the AGNOSTIC / SPECIFIC / MIXED
  taxonomy every language decision depends on.

---

## 0. Day one — set this up before you run anything

Nothing that touches Raya — §3 onward — works until this is done, and the failure does not explain
itself: `raya_testcall.py`, `raya_testrun.py` and `raya_call.py` open `raya/.env` unguarded at
import, so with no `.env` the first live-test command you try dies on a bare `FileNotFoundError`
traceback. (`raya_deploy.py` is the polite one: it falls back to environment variables and then
tells you which key is empty.)

**1. Credentials.** `cp raya/.env.example raya/.env`, then fill in:

| Key | Where it comes from |
|---|---|
| `RAYA_BASE_URL` | **LitWiz Labs** — the Raya REST base URL including any version prefix, no trailing slash |
| `RAYA_API_TOKEN` | **LitWiz Labs** — a secret; the scripts never print it |
| `RAYA_ENV` | **`prod`** — see the next point |

**2. `RAYA_ENV=prod` is the only usable value.** `raya/.env.example` ships `staging`, but
`raya/agents.json` holds **no staging uuids at all** — all 18 conversation targets have a `prod`
uuid and an empty `staging` one. With `RAYA_ENV=staging` every target reports `unmapped`, you can
neither `status` nor `deploy` anything, and nothing on screen tells you why. There is no staging
fleet to point at.

**3. `raya/.env` and `secrets/` are git-ignored and must never be committed** — nor pasted into a
transcript, an issue or a digest. Same for Raya `*.tools*.json` snapshots (§7: one leaked to a
public repo and had to be purged from history).

**4. Prove the setup works, in this order:**

```bash
cd "/Users/parthbansal/EkStep/Prompt Tuner"
python3 scripts/raya_deploy.py targets        # local, no network — the manifest parses + files exist
python3 scripts/raya_deploy.py status --all   # network — proves the token AND RAYA_ENV
```

`targets` failing is your checkout or the manifest. `status --all` reporting `unmapped` for
everything is `RAYA_ENV`. `unreachable` is the base URL or the token.

**5. Python.** Python 3, **standard library only**, for all four Raya scripts (`raya_deploy.py`,
`raya_testcall.py`, `raya_testrun.py`, `raya_call.py`) and bash for `prompt-version.sh` — no
`pip install` to place a call or a deploy. Two exceptions, needed only for their own jobs:
`scripts/gsheets.py` needs `cryptography` (it signs the service-account JWT itself), and
`raya/regression/send_digest.py` imports `google-auth` / `google-api-python-client` lazily inside
its Gmail-API and service-account senders.

**6. A Raya console login** (`console.getraya.app`) — request one from LitWiz Labs. `raya_deploy.py
deploy` PATCHes **`instructions` only**: creating an agent and setting its `language_id` /
`voice_id` can *only* be done in the console. Without console access you cannot stand up a new bot
or a new language, however good the prompt file is.

**7. The other credential stores, only when you need them.** Tier-3 digest / GitHub Actions
secrets: `raya/regression/README.md`. The Google Sheets service account for `scripts/gsheets.py`:
decode it as `CLAUDE.md` (repo root) describes, into git-ignored `secrets/gsheets-sa.json`.

---

## 1. Start here

### What this repo is

The Prompt Tuner is the **maintenance rail for live voice-AI agents**. It does not host the bots —
they run on **Raya Voice AI** (LitWiz Labs). This repo holds each bot's **system prompts** as
markdown files, plus the tooling and the discipline to change them safely:

- iterate a prompt from real feedback and real bugs, surgically;
- keep every language variant of a bot in sync;
- deploy a prompt to its live agent by API PATCH, verified by read-back;
- **test the bot ourselves** — a "tester" agent role-plays a caller, a real phone call is placed,
  and the transcript is graded against checklists;
- take a bot into **new Indic languages** as it is actually spoken;
- and keep a **standing daily regression** running in the cloud so drift is caught while nobody
  is looking.

It now serves **multiple BlueDot-team projects**, not one:

| Project | Bots | Languages today | Notes |
|---|---|---|---|
| **Blue Dots** | KKB (job-matching, seeker), DKB (employer job capture), Maya (campus recruitment) | Hindi (master), Kannada; Maya Hindi-only | two backends: Signals DPG and legacy Dhiway |
| **Purple Dots** | the disability rail | going multi-Indic | accessibility is a first-class grading concern |
| _next_ | whatever arrives | anything | never assume three bots and two languages |

### The 60-second mental model

```
one BOT  ──has──▶ one or more VARIANTS  = (language × direction × backend)
                  each variant = 1 prompt FILE + 1 live Raya AGENT + 1 target id in raya/agents.json
```

Five facts that explain almost every rule in this repo:

1. **A prompt is a live production artifact.** Editing a file is editing a phone call that a real
   person will receive. Hence: surgical edits, snapshots, gated deploys.
2. **A bot's languages are one MASTER + N MIRRORS.** The master leads. Language-**agnostic**
   content (flow, tools, payloads, `${variables}`) is copied byte-identically to every mirror;
   only the **spoken lines** are re-authored per language. Two languages is the special case,
   not the model.
3. **Instructions are always in English.** In every prompt file, in every language, every rule /
   heading / condition is English. The **only** target-language text is what the bot literally
   speaks. A rule written in Hindi/Kannada/Telugu is a bug.
4. **The live agent can be AHEAD of the repo.** People edit the Raya console directly (real job
   inventory lives there). So you reconcile before you edit, or you clobber production.
5. **Nothing is "done" until a real call proves it** — per variant, never extrapolated.

### What a "skill" is

Everything in this repo is done by invoking a **skill** — `/onboard`, `/update-prompt`,
`/voice-test`, … They live in `.claude/skills/<name>/SKILL.md`, with deeper reference material in
`.claude/skills/<name>/reference/`. A skill is a procedure with guardrails; running the right one
is how the house rules get enforced for you instead of remembered by you.

**Never hand-edit a prompt file.** Route every content change through `/update-prompt` (or
`/port-feature` for cross-bot, `/translate-prompt` for a new language). Those skills enforce the
sync rule, the English-instructions rule, the snapshot, the changelog and the analyser update.

---

## 2. Repo map

```
Prompt Tuner/
├── CLAUDE.md                    THE LAW — read first, every session
├── KKB/  DKB/  Maya/            one folder per BOT (bot-named, at the repo root, never nested)
│   ├── <Bot> <Language>.md      conversation prompt: one file per language (+ variant tokens)
│   ├── <Bot> Memory.md          memory prompt — language-agnostic, English output
│   ├── <Bot> Output.md          output prompt — extracts call variables from the transcript
│   └── CHANGELOG.md             every edit appends an entry here. No exceptions.
├── .claude/skills/              the 14 skills (see the decision table in §4)
│   ├── update-prompt/reference/prompt-anatomy.md        AGNOSTIC/SPECIFIC/MIXED taxonomy
│   ├── prompt-analyser/reference/bug-patterns.md        the learned failure classes (families A–G)
│   ├── prompt-analyser/reference/section-checklists.md  what a prompt of each kind must contain
│   ├── voice-test/reference/checklists/generic.md       13 sections, graded on EVERY bot
│   ├── voice-test/reference/checklists/{kkb,dkb,maya}.md  per-bot grading items
│   ├── translate-prompt/reference/language-matrix.md    12 Indic languages: script, register, TTS
│   ├── generate-test-cases/reference/test-case-taxonomy.md  case families, assertions, JSON schema
│   ├── sync-check/reference/n-language-parity.md        master + N mirrors, the 5 passes
│   └── port-feature/reference/agent-schemas.md          per-bot variables/tools/persona
├── scripts/
│   ├── raya_deploy.py           targets | list | verify | diff | status | deploy | reconcile | pull
│   ├── raya_testcall.py         persona | lang | call | whoami   (drives the tester agent)
│   ├── raya_testrun.py          fire ONE test call + poll + dump the graded transcript
│   ├── raya_call.py             read past calls/transcripts (incl. tool_calls arguments)
│   ├── prompt-version.sh        save | list | diff | restore | tag  (snapshot store)
│   ├── build_fleet_manifest.py  emit raya/regression/fleet.json rows from the suite's own fleet
│   └── gsheets.py               read/write the Consolidated Feedback Tracker
├── raya/
│   ├── agents.json              THE deploy manifest — 25 targets; id, file, language, uuid, guard
│   ├── divergences.json         owner-approved deliberate language divergences (sync-check reads it)
│   ├── endpoints.json           the profiles: conversation | memory | output
│   ├── deploy-history.md        every deploy, appended
│   ├── personas/                tester personas, `<lang>-<behaviour>.md` (hi/kn only today)
│   ├── snapshots/               live-prompt backups taken by deploy
│   ├── regression/              Tier-3 standing check (suite, digest, reports, open items)
│   ├── intake/                  `/onboard` summaries            (created on first use)
│   ├── testcases/               `/generate-test-cases` manifests (manifests created on first use;
│   │                            `args/example.json` is the committed `agent_args` shape reference)
│   └── translations/            `/translate-prompt` QA records   (created on first use)
├── versions/                    prompt snapshots per bot (bodies git-ignored; HISTORY.md tracked)
├── docs/                        this file + the roadmap + the Signals migration guide
├── .github/workflows/regression.yml   the daily cloud cron (Tier 3)
├── README.md                    short public-facing overview (CLAUDE.md is the law, not this)
├── Purple Dots — Prompt Gap Analysis.md   a prior read-only analyser pass on the Purple Dots
│                                Hindi prompt: 11 prioritised findings. Read before re-auditing it.
├── OVERNIGHT-SUMMARY-2026-07-27.md   one-off run log, kept for provenance
├── reports/                     one-off exported reports (xlsx)
├── voice-harness/               earlier standalone call-verification harness, pre-`raya_testrun.py`
├── control-center/              local dashboard app (backend + frontend + its own sqlite db)
├── deck/                        the Prompt Tuner explainer deck (HTML) + its notes
├── scratchpad/  scratchpad_*    git-ignored scratch at the root; never cite as a source
└── secrets/  raya/.env          git-ignored credentials. Never commit. Never print.
```

Folders that **must not** change shape: bot folders are bot-named and live at depth 1.
`scripts/prompt-version.sh` snapshots `<Bot>/*.md` at depth 1 and
`raya/regression/static_regression.py` joins `REPO/<agent_dir>/<filename>`. Nesting a bot under a
project directory silently breaks both.

---

## 3. The end-to-end path

### The flow

```
   ┌────────────────────────────────────────────────────────────────────────────────┐
   │  A NEW BOT ARRIVES                                                             │
   └────────────────────────────────────────────────────────────────────────────────┘
                │
        ┌───────▼────────┐   project · what it does · audience + ACCESS NEEDS · languages
        │   /onboard     │   + master · the prompt(s) · Raya uuids + DIDs · tools/APIs ·
        │  (intake)      │   test cases · ISSUES as records with ids  →  raya/intake/<bot-id>.md
        └───────┬────────┘
                │  ── /onboard Step 2 does NOT wait: it REPRODUCES each reported issue
                │     on a real call first (needs only the Raya uuid + a DID, not registration)
        ┌───────▼────────┐   per issue-id → repro-confirmed | no-repro |
        │  /voice-test   │   not-a-prompt-bug: data-input | backend | runtime-adherence
        │   (repro)      │   ── PUSH BACK HERE. Sometimes there is no bug.
        └───────┬────────┘
                │
        ┌───────▼────────┐   folder + prompt files + CHANGELOG · project-aware path map in
        │ /register-bot  │   CLAUDE.md · raya/agents.json target(s) with HAND-COPIED uuids ·
        │  (bookkeeping) │   raya/regression/fleet.json entry.   Writes no prose. Deploys nothing.
        └───────┬────────┘
                │
        ┌───────▼─────────┐  read-only pre-flight against the learned bug patterns (bug-patterns.md)
        │ /prompt-analyser│  + the missing-critical-section checklists.  FLAGS, never fixes.
        └───────┬─────────┘
                │
        ┌───────▼──────────────┐  cases derived from: the flow · the tools · the audience ·
        │ /generate-test-cases │  the reported issues · the bug patterns  →
        └───────┬──────────────┘  raya/testcases/<bot-id>.{md,json} + personas + <bot>.md checklist
                │
        ┌───────▼────────┐   tester agent role-plays the caller; the bot under test DIALS it;
        │  /voice-test   │   grade both legs vs generic.md + <bot>.md.  SMOKE SET FIRST.
        └───────┬────────┘
                │
         confirmed PROMPT gap?  ──no──▶  say so out loud: inputs were wrong / backend /
                │                        runtime-adherence → escalate, make NO edit
                │ yes
   ┌────────────▼──────────────────────┐  /sync-check (auto) → snapshot → reconcile vs live →
   │ /update-prompt  or /port-feature  │  surgical edit on the MASTER → mirror to every mirror →
   └────────────┬──────────────────────┘  CHANGELOG → (bug ⇒ teach /prompt-analyser)
                │
        ┌───────▼────────────────────────────┐  verify → diff → deploy
        │ scripts/raya_deploy.py deploy <id> │  = snapshot · GET backup · name guard · diff ·
        └───────┬────────────────────────────┘    confirm · PATCH · READ-BACK byte-compare
                │
        ┌───────▼────────┐   Tier 1 fix verification  +  Tier 2 blast radius,
        │  /voice-test   │   ON EVERY AFFECTED VARIANT INDEPENDENTLY
        └───────┬────────┘
                │
                ├──────────────────────────────┬─────────────────────────────────┐
                │                              │                                 │
   ┌────────────▼──────────┐      ┌────────────▼───────────┐        ┌────────────▼──────────┐
   │  /translate-prompt    │      │  /sync-check           │        │  Tier 3: DAILY CLOUD  │
   │  language expansion   │      │  parity audit, N langs │        │  static suite + email │
   │  → loops back through │      │  + divergence registry │        │  digest (GitHub cron) │
   │  register/deploy/test │      └────────────────────────┘        └───────────────────────┘
   └───────────────────────┘
```

Corrections this diagram makes to `docs/MULTI-PROJECT-ROADMAP.md` §4, based on what the skills
actually say:

- **Reproduction happens inside `/onboard`**, before registration — its Step 2 fires repro calls
  and classifies every issue-id. The harness scripts take Raya uuids directly, so a bot does not
  need to be registered to be *tested*; it needs to be registered to be *deployed* and to be
  picked up by other skills.
- **`/generate-test-cases` hard-requires registration.** If the bot is missing from
  `raya/agents.json` / `raya/regression/fleet.json` it stops and sends you back to
  `/register-bot` — a manifest of unresolvable target ids is worse than no manifest.
- **`/translate-prompt` is not a terminal box.** It internally calls `/register-bot` (variant
  path), `/sync-check`, the deploy script and `/voice-test`, and it writes a per-language QA
  record. Language expansion re-enters the pipeline; it does not end it.
- **`/sync-check` is now master + N mirrors** and consults `raya/divergences.json`, so an
  owner-approved difference is reported as EXPECTED rather than "fixed" as drift.

### The walkthrough

1. **`/onboard` — intake.** One friendly question at a time. Captures the **project**, what the
   bot does, **who the callers are and any access needs**, every language + which is **master**,
   the prompt(s), the platform + Raya uuid(s)/DID(s), the tools/APIs and their **fixed params**,
   the test scenarios + success criteria, and — the most valuable output — the **issues as
   structured records** with stable ids (`<bot-key>-i<NN>`, e.g. `pd-i01`), each with symptom /
   where (target ids) / trigger / expected / actual / call-ref / severity / status. Saved to
   `raya/intake/<bot-id>.md` from the template at
   `.claude/skills/onboard/reference/intake-template.md`. `/onboard` edits nothing.
2. **Reproduce before you believe (still inside `/onboard`, via `/voice-test`).** For each
   issue-id, in severity order: try the supplied call transcript first (free), else place a repro
   call. Read the call's **input `agent_args`** as well as the transcript. Then classify honestly:
   `repro-confirmed` / `no-repro` / `not-a-prompt-bug: data-input | backend | runtime-adherence`.
   This step is where "no fix without a transcript" is actually honoured.
3. **`/register-bot` — make the bot operable.** Creates `<Bot>/` with one conversation file per
   language (master's content pasted **verbatim**; no empty stubs for languages that have no
   content yet), the `CHANGELOG.md`, the project-aware path-map rows in `CLAUDE.md` (additive
   only), the `raya/agents.json` target rows, and the `raya/regression/fleet.json` entry. The
   uuid is **hand-copied** from `python3 scripts/raya_deploy.py list`, matched by live agent
   **name** — never inferred from a filename. Registration writes no prose and deploys nothing.
4. **`/prompt-analyser` — pre-flight.** Read-only. Walks every pattern in
   `.claude/skills/prompt-analyser/reference/bug-patterns.md` (families A flow, B repetition,
   C tools/payloads, D language/script/voice, E examples/consent, F cross-language pointer,
   G templating — 67 as of 2026-08-05; it grows on every bug fix, so count it from the file rather
   than quoting a number) plus the per-use-case critical-section checklists, and
   flags. Its confirmed findings are the highest-value input to the test suite and to the first
   round of fixes. It never edits.
5. **`/generate-test-cases` — the bot's own suite.** Derives cases from five sources (intake,
   registration, the prompt itself, the live tool schemas, the learned patterns) into six
   families: `F` flow/branch, `T` tool contract, `A` audience behaviour, `R` reported-issue
   repro (1:1 with issue-ids, never merged), `G` pattern guard, `X` accessibility (emitted for
   **every** bot). Emits `raya/testcases/<bot-id>.md` + `.json`, personas at
   `raya/personas/<lang>-<behaviour>.md`, and the bot checklist at
   `.claude/skills/voice-test/reference/checklists/<bot-slug>.md`. Every case carries observable
   pass/fail detection — `tool_fired(…)`, `tool_arg(…) matches …`, `spoken_once(…)`,
   `call_output.<field> == …`. "Looks right" is not detection.
6. **`/voice-test` — live agent-to-agent calls.** The tester agent (**"Testing Agent- Blue Dots"**,
   uuid `f60e0899-aa3a-4be7-9b4f-0296bd28ef48`, DID `911204404272` (confirm with `raya_testcall.py whoami`: DIDs get rebound), 5-min cap) is
   PATCHed with a persona; the **bot under test dials it**; both legs are graded against
   `generic.md` (13 sections, every bot) plus the bot's own checklist. Run the **smoke set**
   (≤6 cases per variant) before anything else.
7. **Fix — `/update-prompt` (or `/port-feature`).** Only for confirmed prompt gaps. The skill
   auto-runs `/sync-check`, snapshots (`scripts/prompt-version.sh save`), reconciles against live
   (`raya_deploy.py diff`, `pull` if live is ahead), edits the **master** language, classifies the
   change AGNOSTIC / SPECIFIC / MIXED, mirrors to every mirror language, appends the
   `CHANGELOG.md` entry citing the issue-id, and — for a **bug** — teaches
   `/prompt-analyser` the new pattern.
8. **Deploy.** `python3 scripts/raya_deploy.py verify <id>` → `diff <id>` → `deploy <id>`.
   `deploy` is the only write path: snapshot → GET backup → `expected_name_contains` guard →
   diff → human confirm → PATCH → **read-back byte-compare**. It refuses any prompt still
   carrying placeholder `job_id`s or a `[PLACEHOLDER SAMPLE DATA]` flag. Append to
   `raya/deploy-history.md`.
9. **Re-verify — all three tiers, every variant.** Tier 1: the exact reported failure is gone, in
   a real transcript. Tier 2: the neighbours still work — same section, the shared agnostic logic,
   the mirrored sibling language/bot, the tool payload touched. Tier 3: the standing daily check.
   Never collapse Tier 1 and Tier 2 into one happy-path call.
10. **Language expansion — `/translate-prompt`.** Master file → a new Indic language, re-authored
    (never translated), with the spoken-form machinery re-derived natively, two QA gates
    (monolingual read, then round-trip meaning), a QA record at
    `raya/translations/<bot-id>-<iso>.md`, a new Raya agent registered via `/register-bot`, a
    deploy, and an independent `/voice-test` in that language with a native-language persona.
11. **Standing net — Tier 3.** The daily cloud run and its email digest (see §6).

### `agent_args` — the inputs the bot receives

Every live test call needs an `agent_args` JSON file — the third argument to
`scripts/raya_testrun.py`. It is the **campaign's per-call inputs**: one key per `${variable}` the
prompt interpolates (the caller's name, the recommendations list, the memory blob, the campaign
flags). At runtime the platform sends the same dict; the file is how you reproduce a real call's
inputs by hand. You cannot place a meaningful test call without one.

- **The shape to copy** is the commented example at `raya/testcases/args/example.json`. Per-bot
  files live beside it as `raya/testcases/args/<target-id>-<scenario>.json`.
- **Deriving one for a bot you don't know:** read a known-good live call —
  `python3 scripts/raya_call.py <agent_uuid> 20` prints the call's `agent_args` alongside the
  transcript and the `tool_calls` arguments — and copy its keys. If the bot has never run, get the
  campaign's `agent_args` mapping from whoever runs the campaign. Do not invent keys: an unbound
  `${variable}` renders literally into the spoken script.
- **`${contact_phone}` is not yours to set.** It binds to the number the bot dialled — the tester's
  DID — not to anything in the args (§8). Provision the backend record you want under that DID.
- **The tester leg receives no `agent_args` at all.** Its scenario comes only from the persona
  PATCHed onto it, which is why live tests are serial (§8).
- Reading the args is half of "push back before fixing": the classification
  `not-a-prompt-bug: data-input` is only provable from the args a real call actually received.

---

## 4. Decision table — "I want to ___ → run ___"

| Situation | Run this | Notes / first command |
|---|---|---|
| A brand-new bot or project has arrived | **`/onboard`** → **`/register-bot`** | Intake first; registration is the mechanical follow-up. Then `/prompt-analyser` → `/generate-test-cases` → `/voice-test`. |
| A bot we already work on, and I need the context | `CLAUDE.md`'s path map → `python3 scripts/raya_deploy.py targets \| grep -i <bot>` → the bot's `CHANGELOG.md` (last 5 entries) → `raya_deploy.py status <id>` and `diff <id>` → `python3 scripts/raya_call.py <uuid> 5` for recent real calls | Branch A of `/onboard` resolves which target ids they mean. **`/load-context` is a skill of the surrounding Obsidian vault (`/Users/parthbansal/EkStep/.claude/skills/`), NOT of this repo** — unavailable if you only have the Prompt Tuner; use the commands at left instead. |
| The bot must speak a language it doesn't speak yet | **`/translate-prompt`** | Master → new language, re-authored + new Raya agent. **Not** `/sync-check` — that mirrors an existing change, this creates a language. |
| Will the translated prompt be too big for the bot? | `python3 scripts/prompt_size.py project <master> --lang <iso> --target <id>` | Too big fails silently: fluent calls, no tool calls. Limits are per bot, from evidence in `raya/agents.json`. Slim the master, never one language. |
| Is this translation actually right? (no Hindi left, rules untranslated, Goodbye, digits, everyday words, gender, insulting words) | `python3 scripts/language_checks.py <master> <mirror> --lang <iso>` | The "Prompt" rows of the language-testing sheet, mechanical. FAIL blocks deploy. The "Call" rows need a live call and a native listener. |
| "Which part of the prompt made the bot say that?" / "What else will this change affect?" | `python3 scripts/prompt_map.py locate <prompt> --call <uuid>` / `impact <prompt> --section "<title>" [--sheet rows.json]` | Built fresh from the prompt each time. `locate` finds the first wrong turn's section; `impact` is the Tier 2 list. See `/bug-fix` → "The prompt map". |
| A fix has failed twice / "the bot will not follow the rule" | Cold read: **`/prompt-analyser`** in a fresh subagent + `python3 scripts/prompt_structure.py <file>` | Often the rule is never reached: a step reference points at the wrong step (D125). Fix the pointer, not the rule. |
| Keep fixing and testing unattended until the sheet passes | `/goal <condition provable from printed output>, or stop after N turns` (see `/bug-fix`) | The checker reads only what Claude prints; it starts no subagents. Every rule still applies. |
| A team's copy of the tuner is behind this repo | **`/upgrade`** in the copy (`scripts/tuner_upgrade.py status / plan / apply`) | Three-way merge per file; bot folders, agents.json, intake, test cases never touched; conflicts set aside to resolve. |
| Copy an agent to another Raya account | `python3 scripts/raya_clone_agent.py copy-plan <id or uuid> "<name>" --dst-account <acct> --lang <iso>`, then `copy` | Needs `RAYA_API_TOKEN__<ACCT>` and the account's voice pair in `raya/voices.json`; phone numbers are not carried; check the tools' keys. |
| Someone gave me a test sheet: "run these, N calls each, fill in the results" | **`/voice-test`** → *Run a test sheet* (`scripts/testcase_sheet.py pull / result / add-bug`) | Read through the service account; a new bug becomes a new row. |
| An existing change must reach the other languages | **`/sync-check`** (then `/update-prompt` to reconcile) | Master leads; mirrors never lead. |
| Languages have drifted / "did that fix land everywhere?" | **`/sync-check`** | Reports a per-language matrix; consults `raya/divergences.json` first. |
| A bug was reported (informally, by a person) | **`/voice-test`** to reproduce → **`/update-prompt`** | No fix without a transcript. Classify before editing. |
| Bugs were reported in the tracker sheet | **`/bug-fix`** | Runs the fixed sequence and writes `Fixed for UAT` back to `All Issues`. |
| A feature must move from one bot to another | **`/port-feature`** | Re-domains to the target's variables/tools/persona — never a verbatim copy. |
| A prompt needs auditing before it goes live | **`/prompt-analyser`** | Read-only; flags, does not fix. Route findings to `/update-prompt`. |
| This bot has no test suite / no checklist | **`/generate-test-cases`** | Requires the bot to be registered first. Delivers a tester-ready Google Sheet in the house layout (`scripts/testcase_sheet.py`), with a safety case and a language tab per language. |
| I need to prove issue `pd-i02` is fixed | **`/voice-test`** with the `R` case for that id | Tier 1 = re-run exactly that case, per affected variant. |
| A change broke something — roll it back | **`/prompt-version`** | `scripts/prompt-version.sh list <Bot>` → `restore <Bot> <label>` → re-deploy. `restore` snapshots the current state first. |
| I'm about to do something risky | **`/prompt-version`** | `scripts/prompt-version.sh save <Bot> pre-<change> "<why>"`. Cheap. Always. |
| Live may be ahead of the repo | `python3 scripts/raya_deploy.py diff <id>`; `pull <id>` if so | If GET is flaky/empty, use **`/raya-reconcile`** (browser pull to a file, diff on disk). Mandatory before every edit. |
| Deploy a prompt to its live agent | `python3 scripts/raya_deploy.py deploy <id>` | Gated, name-guarded, read-back-verified. Never edit the live console instead. |
| The daily digest flagged something | Read `raya/regression/latest-report.md` / `.json` → confirm on a **real call** → `/update-prompt` | A static finding alone is **not** a licence to fix (see `/bug-fix`: a static "gap" that 40 calls never reproduced). |
| A call outcome / variable isn't being captured | **`/update-output`** | One language-agnostic output prompt per bot; extracts call variables from the finished transcript. |
| The bot should remember the caller between calls | **`/update-memory`** | One language-agnostic memory prompt per bot; it also owns the verbatim memory-injection block in every conversation prompt. |
| A skill failed because the bot isn't in the path map / `agents.json` | **`/register-bot`** | Don't guess target ids; register them. |
| I need to read what actually happened on a call | `python3 scripts/raya_call.py <agent_uuid>` | Prints `tool_calls.function.arguments` + linked results + `agent_args`. A `content`-only reader hides every payload bug. |

Skills that **never** edit a prompt: `/prompt-analyser`, `/generate-test-cases`, `/sync-check`
(audit mode), `/raya-reconcile`, `/register-bot`, `/onboard`, `/voice-test`.
Skills that **do**: `/update-prompt`, `/port-feature`, `/translate-prompt`, `/update-memory`,
`/update-output`, `/slim-prompt`. (`/sync-check` only reports; a lagging language is brought up through
`/update-prompt`.)

---

## 5. Three worked scenarios

### (a) A brand-new bot from a new project — Purple Dots, the disability rail

The bot phones people with disabilities and connects them to services and enablers. It exists as
a Hindi prompt and a live Raya agent; it is not registered here yet — but it is not unknown to the
repo either: a prior read-only analyser pass on its Hindi prompt sits at the repo root as
`Purple Dots — Prompt Gap Analysis.md`, and two of its findings are already in the pattern catalog.

1. **`/onboard`.** Record `project: purple-dots`. Ask what the bot does, then — gently, as
   audience understanding, never as a diagnosis — **how the callers want to be spoken to**:
   pace, patience with silence, repeat-on-request, short turns, no free-form-only questions.
   Write down whatever they say; "nothing special" is a valid answer. **The bot never raises,
   names or asks about anyone's disability** — access needs constrain *how* it speaks, never
   *what* it talks about. Collect languages (`hi` master; `ta`, `te`, `mr` wanted), the prompt
   file, the Raya uuid + DID, the tools (`get_profile`, …) with their fixed params, the success
   criteria, and each complaint as an issue record: `pd-i01`, `pd-i02`, … Save to
   `raya/intake/pd-hi-out.md`.
2. **Reproduce each issue first.** Load a persona onto the tester, fire a call per issue-id per
   affected variant:
   ```bash
   cd "/Users/parthbansal/EkStep/Prompt Tuner"
   python3 scripts/raya_testcall.py persona f60e0899-aa3a-4be7-9b4f-0296bd28ef48 raya/personas/hi-repro-pd-i01.md
   python3 scripts/raya_testcall.py lang    f60e0899-aa3a-4be7-9b4f-0296bd28ef48 hi
   python3 scripts/raya_testrun.py <pd_hindi_agent_uuid> 1204404272 raya/testcases/args/pd-hi-out-new.json \
           f60e0899-aa3a-4be7-9b4f-0296bd28ef48 "repro-pd-i01-pd-hi-out"
   ```
   That third argument is the `agent_args` file — write it before you fire, copying the shape from
   `raya/testcases/args/example.json` (see §3, *`agent_args` — the inputs the bot receives*).
   Read the transcript **and** the `agent_args`. Classify each id. Expect some to come back
   `not-a-prompt-bug: data-input` — say so out loud and make no edit.
3. **`/register-bot`.** Creates `Purple Dots/Purple Dots Hindi.md` (customer prompt pasted
   verbatim) + `Purple Dots/CHANGELOG.md`; adds the `### Projects` index and a
   `### Purple Dots — file paths` long-form table to `CLAUDE.md` (additive; the Blue Dots table
   stays byte-identical); appends the `pd-hi-out` target to `raya/agents.json` with the uuid
   hand-copied from `raya_deploy.py list` and `expected_name_contains: ["Purple", "Hindi"]`;
   creates `raya/regression/fleet.json` — generate the existing rows with
   `python3 scripts/build_fleet_manifest.py` (it derives all **18** conversation prompts the daily
   suite checks today, so nothing is dropped by hand-transcription), review the diff, then append
   `pd-hi-out`. Verify:
   ```bash
   python3 -c "import json;json.load(open('raya/agents.json'));json.load(open('raya/regression/fleet.json'));print('json ok')"
   python3 scripts/raya_deploy.py targets | grep -i purple
   python3 scripts/raya_deploy.py targets --check
   python3 raya/regression/static_regression.py     # pre-existing findings, PLUS one new critical
                                                    # coverage finding: pd-hi-out is a live target
                                                    # the suite is not checking yet (see step 7)
   ```
   Also do two things registration flags but does not do. First, teach
   `resolve_agent()` in `scripts/prompt-version.sh` the new bot — it accepts only `kkb | dkb | maya`
   and **lowercases its argument**, so the folder name `Purple Dots` arrives as `purple dots`
   *with a space*; the case must cover it, e.g.
   `"purple dots"|purple-dots|pd) echo "Purple Dots" ;;` (also add `Purple Dots` to `cmd_list`'s
   default agent list). Without it you cannot snapshot the bot — and `raya_deploy.py deploy`
   refuses to push without a snapshot. Second, add a Purple Dots entry to
   `.claude/skills/port-feature/reference/agent-schemas.md` (or `/update-prompt` and
   `/port-feature` cannot re-domain anything to it).
4. **`/prompt-analyser`** on `Purple Dots/Purple Dots Hindi.md`. **Read
   `Purple Dots — Prompt Gap Analysis.md` (repo root) first** — a prior read-only analyser pass with
   11 prioritised findings already exists. Re-run `/prompt-analyser` only to confirm those against
   the current *live* prompt and to fold in anything new, and reconcile its findings with the intake
   issue records rather than re-deriving them from scratch. The Purple Dots prompt has already
   contributed patterns A2 and A3 to the catalog (skip-ahead pressure with no backpressure;
   overlapping phases conflated) — expect those to reappear.
5. **`/generate-test-cases`** for `pd-hi-out`. The `X` accessibility family is emitted for every
   bot; the durable items (pacing, silence tolerance, repeat-on-request, never talking over the
   caller, a companion answering on the caller's behalf, never making the disability the subject
   of the call) belong in **`generic.md`** so the whole fleet inherits them — the skill proposes
   that promotion and **asks before editing `generic.md`**, because that file grades every bot.
6. **`/voice-test`** the smoke set (≤6 cases) on `pd-hi-out`, grade, then work the fixes through
   `/update-prompt` → deploy → Tier 1 + Tier 2. Then §5(b) for each new language.
7. **The daily net picks it up by itself:** `static_regression.py` reads every `deploy: true`
   conversation target in `raya/agents.json`, in every language, so the new bot is in the next
   morning's email. Check it appears there.

### (b) Taking an existing bot into a new Indic language — Purple Dots → Telugu

1. **Fix the scope and the register.** Bot, master file, target language + ISO (`te`), direction,
   and **the region and audience** — Telangana vs Coastal Andhra changes the variety, the
   greeting, the honorifics and the example place names. Ask; do not default it silently.
2. **Reconcile, then snapshot** — in this order, before reading the master for content:
   ```bash
   python3 scripts/raya_deploy.py diff pd-hi-out      # is LIVE ahead of the repo master?
   python3 scripts/raya_deploy.py pull pd-hi-out      # only if it is
   scripts/prompt-version.sh save "Purple Dots" pre-2026-08-05-te-translation "translating to Telugu"
   ```
   Cloning a stale master bakes the staleness into a whole new language for as long as it lives.
3. **Build the classification ledger** — `grep -n '^#\{1,4\} ' "Purple Dots/Purple Dots Hindi.md"`,
   then tag **every** section AGNOSTIC / SPECIFIC / MIXED against `prompt-anatomy.md`. No line
   gets written before this table exists.
4. **Copy the AGNOSTIC spine byte-identically**, then prove it mechanically:
   ```bash
   diff <(grep '^#\{1,4\} ' "Purple Dots/Purple Dots Hindi.md") \
        <(grep '^#\{1,4\} ' "Purple Dots/Purple Dots Telugu.md")        # expect empty
   diff <(grep -ohE '\$\{[A-Za-z0-9_]+\}' "Purple Dots/Purple Dots Hindi.md"  | sort -u) \
        <(grep -ohE '\$\{[A-Za-z0-9_]+\}' "Purple Dots/Purple Dots Telugu.md" | sort -u)   # expect empty
   ```
   Use the case-mixed character class, not `\${[a-z_]*}`: the narrow form silently misses camelCase
   inputs like `${phoneNumber}` (real, in five DKB prompts) and then reports a parity it never
   checked.
5. **Re-author the spoken content** — for each line, state in English what the turn must
   accomplish, then write what a real Telugu speaker on a phone call would say. Keep the length
   budget. Prefer the everyday loanword (`అప్లై`) over the bookish form (`దరఖాస్తు`) — that is
   pattern D1, the commonest literal-translation tell. Avoid the literary register nobody speaks.
6. **Re-derive the spoken-form machinery natively** — numbers as words, money, per-unit rates
   ("per day", never "/"), dates, day-part times, phone digits, `@` and `.`, abbreviations,
   honorific particle (`అండి`), greeting/farewell, AI + recording disclosure, hold filler,
   read-back, ASR confusion pairs, prohibited phrases, **canonical place spellings** (D26), tone
   markers. **None of it transfers** from Hindi or Kannada. Never emit native-script digits.
7. **Two QA gates, in order.** Gate 1: read **only** the new file — "would a real speaker say this,
   out loud, on a phone call, to this caller?" A file with zero flags on its first read has not
   been read properly. Gate 2: open the master and back-translate every line to English, judging
   **meaning** — a lost disclosure, a changed condition, a softened refusal, a dropped cap, a
   changed number is a **fix**, not a note. Then re-run Gate 1 on anything you rewrote.
8. **`/sync-check`** the bot — it must come out clean before deploy. A deliberate,
   owner-approved difference goes into `raya/divergences.json`, not into an unexplained diff.
9. **Stand up the NEW agent** (a new language = a new agent), via `/register-bot`'s variant path.
   Then the part registration does **not** cover:
   ```bash
   python3 scripts/raya_testcall.py whoami <new_agent_uuid>   # name / language_id / voice_id / DIDs
   ```
   A cloned agent usually still carries the **master's** `language_id`/`voice_id` — that is the
   classic "the file looks perfect, the call sounds broken" failure. Fix it on the Raya console
   (`deploy` PATCHes `instructions` only). Add the `te` pair to the `LANG` dict near the top of
   `scripts/raya_testcall.py` or the tester cannot speak Telugu. If Raya has no Telugu voice,
   live testing is **blocked** — say so and mark VERIFY-PENDING; never test in another language.
10. **Deploy** (`verify` → `diff` → `deploy`), then **`/voice-test` in Telugu with a Telugu
    persona** (`raya/personas/te-*.md` — English instruction header, Telugu spoken lines, Telugu
    person and place names). Grade `generic.md` §8 hard: script purity, numbers/money/phone as
    words, canonical place spellings identical on every mention, correct voice, nothing bookish,
    voice-gender agreement, tool payloads **unchanged** and Latin-valued.
11. **Write the QA record** `raya/translations/pd-hi-out-te.md` — `<bot-id>-<iso>.md`, the naming
    convention from §3 step 10 — append the `CHANGELOG.md` entry, confirm the fleet-manifest row,
    and either name your **native reviewer** or mark the language
    **VERIFY-PENDING**. Gates 1 and 2 are the author's own work — neither is a native speaker.

### (c) A bug reported on a live bot in production

Report: *"KKB Kannada Signals asks the caller for their phone number twice."*

1. **Ground it in a real call — before anything else.**
   ```bash
   python3 scripts/raya_call.py <kkb_kn_signals_uuid> 20
   ```
   Read the offending turns **and** `agent_args` **and** the assistant turns'
   `tool_calls.function.arguments`. If no recent call reproduces it, **do not fix** — ask for the
   reproducing call uuid, or place a repro call with `/voice-test`.
2. **Classify — push back before fixing.** Genuine prompt gap → fix. Values in the wrong field /
   malformed args / mis-mapped campaign args → *"the prompt is fine, the inputs were wrong"*, no
   edit. Backend 4xx/5xx, placeholder inventory, region-specific endpoint behaviour → escalate.
   The model ignoring an instruction the prompt already states clearly → **runtime adherence**:
   the lever is a tool-schema change (e.g. a `required` param), **not more prose** — piling on
   prose has already caused a regression here (D25).
3. **Reconcile, then snapshot.**
   ```bash
   python3 scripts/raya_deploy.py diff kkb-kn-signals     # live can be AHEAD (real job inventory)
   python3 scripts/raya_deploy.py pull kkb-kn-signals     # only if it is; review the git diff
   scripts/prompt-version.sh save KKB pre-2026-08-05-phone-doubling "double phone ask, kn signals"
   ```
4. **`/update-prompt`.** It runs `/sync-check` first. Edit the **master** (Hindi), classify the
   change, mirror to Kannada (AGNOSTIC byte-identical, spoken lines adapted). If the change
   touches logic Maya inherits, **stop and ask** before touching Maya (the Maya flag-and-ask rule).
   Append the `KKB/CHANGELOG.md` entry. Because this is a **bug**, also add or sharpen the entry
   in `.claude/skills/prompt-analyser/reference/bug-patterns.md` — symptom → root cause →
   **detection heuristic** → fix direction → source + date — and update
   `section-checklists.md` if it implies a section that must always exist.
5. **Deploy** each affected target: `verify` → `diff` → `deploy`, read-back verified, appended to
   `raya/deploy-history.md`.
6. **Tier 1 + Tier 2, per variant.** Voice-test the exact repro on **Kannada AND Hindi**,
   **outbound AND inbound** — every variant that received the mirrored edit. Then the blast
   radius: the same section, the shared agnostic logic, the sibling that got the mirror, and the
   tool payload touched. "Kannada passed so Hindi is fine" is the recipe-for-disaster rule.
7. **Close the loop.** If it came from the tracker, flip the sheet row to **`Fixed for UAT`** on
   deploy (never leave a deployed fix `Open`); backend/runtime → `Flagged - Backend Issue`;
   no-repro → keep `Open` + request the call. `Fixed for UAT` ≠ *confirmed* — only a **post-deploy**
   transcript per variant makes it `verified`.
8. **On any regression:** `scripts/prompt-version.sh restore KKB <pre-fix-label>` → re-deploy.

---

## 6. The standing quality net (Tier 3)

**What runs.** `.github/workflows/regression.yml` — a **GitHub Actions** cron, `7 1 * * *`
(nominally ~06:37 IST). It runs on GitHub's infrastructure, so it **survives the developer's
machine being off** — which is the whole point, and which neither of the local schedulers can do.
GitHub's shared cron queue delays scheduled runs (observed arrival ~04:20–04:40 UTC, i.e. up to
~3.5 h late): treat it as "each morning", never as a guaranteed clock time. There is also a
`workflow_dispatch` button for a manual run.

**What it checks.** `python3 raya/regression/static_regression.py` reads **every deployable
conversation prompt listed in `raya/agents.json`** (22 today), in every language, and self-checks
coverage: any `kind: conversation`, `deploy: true` target the suite is not reading raises
a **critical** coverage finding instead of vanishing silently. That check exists because it
happened — `dkb-hi-in` and `dkb-kn-in` were absent from the list until 2026-08-05 and the digest
reported "16 bots" as if that were the whole fleet. The suite then applies the failure classes we
have actually been burned by, tuned for precision because a noisy daily email is worse than none:

- **cross-backend leakage** — a Signals prompt carrying a Dhiway contract token, or vice versa;
- **phone-doubling** — the `+91${contact_phone}` / `91${contact_phone}` templates that make the
  model double the country code (the CD6 class);
- **memory-injection block** — the verbatim `{${contact_memory}}` must be present;
- **enum drift** — the byte-exact Signals Phase-2 enums; a wrong enum 400s the write;
- **missing sections** — Graceful Exit; seeker bots need `get_profile`; DKB needs `create_job`;
- **language sync parity** — today a crude Hindi↔Kannada header-skeleton comparison.

Runtime ~6 s. **No run ever places a phone call.**

**And that is the limit of it: Tier 3 has been static-only, so no *behaviour* is checked unattended.**
Every regression in the 2026-09-01→04 window — the inbound location ask, the already-applied branch
going silent, the fabricated apply success — reached us through a QA WhatsApp message, because the
daily job reads prompt TEXT and none of those faults are visible in the text. Two things were missing:
nothing ran the behaviour detectors unattended (see `raya/regression/README.md`, "Runtime checks are
NOT in the daily digest yet"), and **nothing generated the traffic they need to read.** A detector is
a reader; on a day when a bot takes no calls, it is unchecked however often the detector runs.

**`raya/overnight/overnight_sweep.py` is the behaviour half of Tier 3** — the thing you start before
going to bed:

```bash
python3 raya/overnight/overnight_sweep.py --hours 6     # dial, then grade, in a loop
python3 raya/overnight/overnight_sweep.py --dry-run     # print the 28-case queue, dial nothing
```

Phase A dials **all 18 testable bots** (28 cases, persona + fixture chosen per case to walk a part of
the flow that has actually broken); phase B then runs the static suite, `toolschema_parity.py`, every
runtime detector `--since` the sweep start, and `fab_rate.py --append` over exactly that traffic; then
it loops, so an intermittent fault reads as a rate instead of one lucky call. Output:
`raya/overnight/sweep-<date>/{calls.tsv, pass-N.txt, REPORT.md}`, with `REPORT.md` rewritten after
every pass so a night that ends early is still readable. It is serial on one tester DID (~2 h/pass)
and needs `raya/.env`, so it cannot move into the zero-secrets CI job.

**Where the output lives.** `raya/regression/latest-report.md` (human) and `latest-report.json`
(machine — its `critical` array drives the digest). Curated known issues live in
`raya/regression/open-items.json`, joined to bots by the exact label string
`<Agent> <Language> · <direction> · <Signals|legacy>`.

**The digest email.** Two independent paths: (1) on any critical finding the job **exits
non-zero**, so GitHub emails the repo owner and the run page carries the full digest; (2)
`build_digest.py` → `send_digest.py` sends a formatted HTML email — **live** via the Gmail API as
`parth@ekstepplus.org` (OAuth refresh token in repo secrets, `gmail.send` scope only, no admin
required), with Resend / SMTP / service-account fallbacks auto-detected from whichever secret is
present. Subject looks like `[Prompt Tuner] Daily regression — 0 critical, 0 major`. The digest is
written for a reader with **no context**: each finding names the bot in plain English and says why
it matters.

**What is NOT covered yet — say this out loud rather than implying coverage:**

- **The weekly live-call tier is not wired.** There is no live-call script in CI and the
  Raya/Signals keys are not in repo secrets (they are git-ignored locally by design). Until they
  are, the standing net is **static-only** — it reads prompt files and never exercises ASR, TTS,
  telephony or runtime tool adherence. When it is built it gets its own job at its own distinct
  cron time (a second cron on the same minute previously caused duplicate Monday emails).
- **The fleet comes from `raya/agents.json`.** `discover_prompts()` reads every `deploy: true`
  conversation target, with its language code, direction and backend, so a newly registered bot is
  checked the day it lands. `raya/regression/fleet.json` is generated from the same source
  (`python3 scripts/build_fleet_manifest.py`, `--check` in CI); never hand-edit it. Still hard-coded:
  the role labels (`SEEKER_AGENTS` / `AGENT_BLURB` in `static_regression.py`), and a bot without the
  `signals` flag is treated as the older Dhiway backend, so a bot on a new backend can get false
  findings until those are generalised. `deploy: false` targets are not checked.
- **Parity is per language but still counts headings.** `sync_parity()` compares the master with every
  mirror language listed for the bot (Hindi is master when present). It compares heading counts only and
  does not read `raya/divergences.json`; the deeper checks are `/sync-check` and
  `scripts/language_checks.py`.
- **A static finding is not a bug.** Tier 3 raises suspicion; a transcript confirms it. Do not
  fix off the digest alone.

---

## 7. The non-negotiables

These are laws, not preferences. Each exists because breaking it has already cost us something.

| Law | Why it exists |
|---|---|
| **Surgical edits only** — smallest possible change; preserve spoken lines, `${variables}`, tool names, JSON payloads and field names, fixed params, section structure. Prefer additive. | These prompts run live phone calls; a stray reformat can break the whole agent, and an incidental diff hides the real change from review. |
| **Instructions in English; only spoken lines in the target language** | It is what makes a master file and its mirrors share the *same* English instructions and differ only in quoted speech. A rule written in Hindi/Kannada/Telugu cannot be mirrored or audited — it is a bug. |
| **Never localize** a `${variable}`, a tool name, a JSON field, or a fixed param; never let target script into a tool argument, or Latin script into a spoken line | They are machine contracts, not words. Crossing the two is bug D3, and a localized param 400s the write. |
| **Language sync** — the master leads; AGNOSTIC content byte-identical to every mirror, spoken content adapted | A fix that lands in one language and not its siblings is a regression, not a partial win. |
| **No fix without a transcript** | A "plausible" static gap that 40 real calls never reproduced is an ungrounded change. Pull the call, read the turns *and* the `tool_calls` arguments, understand the root cause first. |
| **Push back before fixing** — data/input, backend and runtime-adherence faults are not prompt bugs | Editing to look responsive makes things worse: prose piled onto a runtime-adherence miss has already caused a live regression (D25). Say "the prompt is fine, the inputs were wrong" out loud. |
| **Test every variant independently — never extrapolate** | "It works for Hindi, so Kannada is fine" is the recipe-for-disaster rule. ASR, TTS and runtime adherence differ per language and per direction; a byte-identical mirrored edit can still land differently. |
| **The three testing tiers, in order** — (1) fix verification, (2) blast-radius regression, (3) daily standing check | Tier 2 is the one that catches "fixed X, silently broke Y". Never collapse tiers 1 and 2 into a single happy-path call. |
| **Reconcile before edit** | The live console can be AHEAD — the team maintains real job inventory there. Editing a repo file that is behind live clobbers production (a real inventory overwritten with placeholders → `apply_failed`). |
| **Snapshot before deploy** (`scripts/prompt-version.sh save`) | It makes every edit reversible in one command without depending on a git push. `restore` snapshots the current state first, so a rollback is itself reversible. |
| **Deploy only by the gated write path** — `raya_deploy.py deploy`, name-guarded, read-back-verified | Raya's GET read path is unreliable and a console Save can wipe a live prompt. Only a read-back byte-compare proves what is live. |
| **Every edit → `CHANGELOG.md`; every bug fix → `/prompt-analyser`** | The changelog records *what* changed; the analyser entry ensures the same failure class is **detected before it ships again**. That is how the repo compounds instead of relearning. |
| **A change is not DONE until tested** — untestable ⇒ best-available verification + explicit **VERIFY-PENDING** | "Deployed" is not "working". `Fixed for UAT` is not `verified`. Never claim done/confirmed on an untested change. |
| **Access needs are a design constraint, never the topic** | The bot's *behaviour* adapts — pacing, patience, repetition. The bot never raises, names or asks about anyone's disability. |
| **Never commit secrets or Raya tool-config snapshots** | `raya/.env` and `secrets/` are git-ignored for a reason, and Raya `*.tools*.json` snapshots embed live API keys — one leaked to a public repo and had to be purged from history (2026-08-02). Never commit tool snapshots. |
| **Never `git commit` or `git push` from a skill** — **one exception:** a `pull` that adopts LIVE content into the repo is committed by the owner **before** any edit | Show the diff; the owner commits. The exception is CLAUDE.md's reconcile-before-edit rule: if the adopted-from-live baseline is not committed first, it is indistinguishable from your own change in the diff, and the review cannot tell what you actually did. |

---

## 8. Known limits and gotchas

Things a newcomer otherwise learns by wasting a day.

**The live-call harness**

- **One tester agent ⇒ live tests are serial.** The tester holds **one persona at a time** (its
  prompt is PATCHed) and **receives no `agent_args`**, so you cannot select a scenario per call.
  Parallel calls do bridge, but only for the *same* scenario. Different scenarios in parallel
  would need one tester agent per scenario, each with its own inbound DID.
- **Call creation is rate-limited** — roughly 1 per ~13 s, then HTTP 429 with `retry_after`.
  Space fires ≥ ~15 s. Budget **~10–14 completed live calls per hour per tester**.
- **Telephony bridging is intermittent.** Some dials fail instantly (`Failure`/`Unanswered`,
  `dur=0`, no transcript). **This is flaky telephony, not a bug in your request** — retry the
  connect (the runner does, with a ~90 s cooldown). A **burst of rapid calls makes bridging
  worse**; spacing them out is the fix, not more retries.
- **`GET /api/call/{uuid}` lags** after a call — `Pending`, `dur=0` for a while before the
  transcript and `call_output` finalize. Keep polling; do not conclude "no transcript".
- **Omit `out_did`** on the trigger. Passing it explicitly produced `Unanswered`; omitting it
  connects.
- **The bot looks up the DIALED number.** `${contact_phone}` binds to `to_number` — i.e. the
  tester's DID, *not* whatever phone you put in `agent_args`. Provision the backend record you
  want under the tester DID. **Signals has no delete route**, so once a profile exists for that
  number it can never be "new" again — run your new-caller cases **first**.
- **Inbound bots are testable** (corrected 2026-09-02). PATCH the inbound agent with an integer
  `out_did` (a string returns 400), then `POST /api/call` with the inbound agent as `agent_id` and the
  tester's DID as `to_number`. The inbound bot looks up the caller's number, so prepare inbound test
  data on the tester's number.
- The tester's standing cap is **5 minutes** (bot agents are capped at 15 by the API).

**Raya platform**

- **Proof of a deploy is the PATCH read-back, never a later GET.** The GET reads most prompts now
  (that is how `diff` and `pull` work) but can still come back empty or partial: `diff` reports that as
  UNREADABLE, `pull` refuses unless two GETs agree, and `/raya-reconcile`'s browser path is the fallback.
- **The live console can be AHEAD of the repo.** Reconcile before every edit; `pull` and commit
  the reconciliation *before* you change anything.
- **Never edit the live agent in the console** as a deploy mechanism — it clobbers console-only
  content, and the Save POST can return 503 even on success.
- **Uuids are hand-copied, matched by live agent NAME.** Never inferred from a filename:
  `KKB/KKB Placeholder Inbound.md` is the **Hindi** inbound prompt, and `Maya/Maya Inbound.md`
  carries no language token at all. Tighten `expected_name_contains` to include the bot **and**
  the language/variant token — a guard of just `["KKB"]` will happily PATCH a Telugu prompt onto
  the Hindi agent.
- **A cloned agent keeps the source language's `language_id`/`voice_id`.** Run
  `raya_testcall.py whoami` before testing a new language, or a Hindi voice will read your Telugu
  script.
- **Runtime tool-adherence misses are not fixed with more prose.** If the prompt already mandates
  the behaviour clearly and the model ignores it, the lever is platform-side (tool-forcing, a
  `required` param) — see D25/D40. More prose has already backfired and been reverted.

**Repo scaffolding that lags the multi-project move**

- `scripts/prompt-version.sh` finds bot folders by itself (a top-level folder with a `CHANGELOG.md` and a
  prompt), so a new bot needs no script change. Its argument is matched case-insensitively, with `-`/`_`
  read as spaces.
- Language and voice ids live in `raya/voices.json`, per Raya account (`raya_testcall.py` reads it; set
  `RAYA_ACCOUNT` for a second account). A new language needs its pair recorded there, read with
  `python3 scripts/raya_testcall.py whoami <uuid>` from an agent that already runs that language. If no
  agent runs it yet, ask LitWiz for the pair; until then live testing in that language is BLOCKED: say so
  and mark the variant VERIFY-PENDING rather than testing on another language's voice.
- `raya/personas/` has `hi-*` and `kn-*` only; `voice-test/reference/checklists/` has `generic`,
  `kkb`, `dkb`, `maya` only. `/generate-test-cases` fills these gaps (G5/G6) per bot and language.
- `.claude/skills/port-feature/reference/agent-schemas.md` needs an entry for a new bot before
  `/update-prompt` or `/port-feature` can re-domain anything to it.
- `raya/intake/`, `raya/translations/` and `raya/regression/fleet.json` do not exist yet — the first
  run of the owning skill creates them. `raya/testcases/` exists only as `args/example.json` (the
  `agent_args` shape reference); the per-bot manifests are created on first use.
- The `CLAUDE.md` path map's wide form (one column per language) is **grandfathered for Blue Dots
  only**; every new project uses the long form (one row per bot × language) so it scales to N
  languages. `raya/agents.json` is the machine-readable source of truth; the map is the human index.

**Discipline traps**

- **A static or analyser finding is not a bug** until a transcript reproduces it.
- **Case ids and target ids are permanent.** Reports, `open-items.json`, deploy history, changelog
  lines and the fleet manifest all join on them; renaming orphans history.
- **One source of truth per fact.** Deploy identity → `raya/agents.json`. Fleet labels/roles →
  `raya/regression/fleet.json`. Test coverage → `raya/testcases/`. Join on the target id; never
  re-copy a field.
- **Do not edit `voice-test/reference/checklists/generic.md` without explicit approval** — it
  grades every bot in the fleet.
- **`raya/divergences.json` is not a licence to drift.** An entry is scoped to the listed sections,
  tokens and languages; everything in `still_must_match` is still audited, and a stale entry is
  reported as a registry gap rather than silently honoured.

### 8.x Platform facts learned by experiment (2026-08-10) — don't re-derive these

**Two job-source families — establish which one a bot is before you grade it (2026-08-12).** The
fleet's prompts split into two families that share the same flow but get their jobs from different
places, and confusing them produces both bad fixes and bad verdicts:

| Family | Job source | Real `agent_args` on a production call |
|---|---|---|
| Outbound / Signals (`kkb-hi-signals`, `kkb-kn-out`, `maya-hi-out`, …) | `${recommendations}` from the campaign | `recommendations`, `contact_name`, `contact_phone`, `country_code`, `contact_memory`, … |
| **Inbound** (`kkb-hi-in`, `kkb-kn-in`, `*-in-signals`, `maya-hi-in*`) | a **hardcoded Job Inventory in the prompt body** (real `job_id` uuids, 16+ jobs) | **only** `contact_memory`, `contact_phone`, `country_code` (+`college_name` on Maya) |

Consequences, both learned the hard way:
- **Never write a guard that references `${recommendations}` in an inbound prompt.** It has no such
  variable — the prompt says so itself — and the token makes Raya derive a phantom `agent_arg`, so
  whatever a caller or harness supplies gets interpolated into the middle of that section (see
  analyser **G6**, **G2**).
- **Never grade an inbound bot for hallucination by comparing its spoken jobs to the call's args.**
  It does not read them. Compare against the inventory in its prompt. Doing otherwise produced four
  false CRITICAL/FAIL verdicts in one sweep, including calling a `job_id` "fabricated" when it was
  line 262 of the bot's own prompt.
- A harness call to an inbound agent therefore does **not** reproduce production input. Send only the
  args production sends; extra args are ignored at best and misleading at worst.

**One tester DID means one shared profile history.** `get_profile` on the tester DID returns MULTIPLE
records (Ramesh, ಪ್ರಕಾಶ್, Aryan, ಸುಜಾತಾ, Parth Bansal, Prakash) because every persona has called
from it. A bot greeting the caller by a name the current persona never gave is usually **correct
behaviour reading a real profile record** — not a memory leak. Confirm against the tool result in the
transcript before calling it a defect.


**Creating an agent via the API works, but in two steps.** `POST /api/agent` requires only `name`;
everything else defaults (and the defaults are not what you want — `max_call_duration_mins` 60,
English `language_id`, `allow_interruption` false, `say_hello` true). It **rejects** three keys that
`PATCH` accepts: `memory_enabled`, `memory_instructions`, and `agent_args`. So: create with name +
instructions + output_instructions + language/voice/dids, then `PATCH` memory on.

**`agent_args` is not settable at all.** Raya *derives* it from the `${...}` tokens in
`instructions`. Two consequences: you never maintain it by hand, and **a literal `${...}` written as
an example inside a prompt becomes a phantom declared argument** (analyser **G2** — it happened on
both new TRRAIN agents the first time round).

**`say_hello` is the "agent speaks first" toggle, and the agent still speaks with it off.** Every
production transcript — before and after flipping it — begins with a synthetic `[user] 'hello'` seed
turn injected by the platform; that seed is what prompts the model to produce the first line. Verified
against live production calls plus a controlled A/B on a scratch agent. So turning `say_hello` off
does **not** risk dead air on an outbound call; what changes is only that the bot's first *generated*
line is whatever the prompt puts first. (Read that leading `[user] hello` as platform noise, never as
something the caller said.)

**`${contact_memory}` really is interpolated.** Proven directly: a scratch agent instructed to read
its own context block aloud spoke the memory JSON back verbatim. So if a memory-driven branch does not
fire, the cause is in the prompt, not the platform — check for a competing absolute (analyser **A9**)
before anything else.

**`${contact_phone}` binds to the number actually DIALLED, and not always with the country code.**
On the same tester DID, one bot's `get_profile` received `917946350285` and another's received
`7946350285` — the second returned no profile. Always make the prompt normalise: strip `+`/spaces,
prepend `91` only if 10 digits remain, never double an existing `91`.

**Parallel test calls to one tester cause 429s and kill bridging.** Three calls staggered 16s apart
all failed to bridge with repeated 429s; the same scenarios run sequentially with ~30s between them
connected. Run one call at a time. Separately, bridging is genuinely intermittent — a wave can lose
several calls in a row to `outcome=Failure, dur=0` with nothing wrong on either agent, so re-run
before concluding anything about a bot.

**Two test waves must never overlap.** A wave whose wait-loop watched only `raya_testrun.py` started
during a gap between another wave's calls and PATCHed the tester's persona out from under an
in-flight test. Have a wave wait on the other wave's *script* name too, not just the runner process.

