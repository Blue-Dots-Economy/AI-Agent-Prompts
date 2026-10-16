# Prompt Tuner → multi-project roadmap

**Recorded 2026-08-04** from the owner's brief. This is the spec of record for turning the Prompt
Tuner from a 3-bot / 2-language tool into a **reusable rail any BlueDot-team project can adopt**,
and for handing it to a third person without a verbal handover.

---

## 1. Context — what is changing

The Prompt Tuner currently serves **three bots** (KKB, DKB, Maya) in **two languages**
(Hindi, Kannada) on **one platform** (Raya) across two backends (Signals DPG, legacy Dhiway).

It is now being adopted by **other projects inside the BlueDot team**. First up: **Purple Dots** —
a bot rail for **people with disabilities**. Planned work on it:

- convert that bot into **multiple Indic languages**
- add new features to it
- run `/prompt-analyser` over it
- put it under the same testing + standing-regression net as the existing bots

This means the repo must stop assuming "three known bots, Hindi↔Kannada" and start being
**project- and language-agnostic**.

---

## 2. Requested new capabilities (the owner's four asks)

### 2.1 Language translator skill — `/translate-prompt` (NEW)
Take a bot's prompt that exists in one language and produce a version in **another Indic
language**, then stand up the **new agent** for it.

Hard requirements from the brief:
- **Not literal translation.** The output must read as the language is *actually spoken* — real
  idiom, natural register for the audience, not a dictionary rendering of the source.
- **Pronunciation / spoken-form correctness.** Whatever machinery the current prompts use to make
  speech come out right — TTS number-to-word spellings, script rules, transliteration choices,
  Kanglish-style code-mixing, tone markers — must be **carried forward and re-derived for each new
  language**, not copied from the source language.
- Scale target: **as many Indic languages as possible** — Hindi, Kannada, Telugu, Malayalam, Tamil,
  Marathi, Bengali, Gujarati, Punjabi, Odia, Assamese, Urdu.
- Must preserve everything language-**agnostic** byte-identically (call flow, tool names, JSON
  payloads, variable names, section skeleton) — the existing agnostic/specific taxonomy governs.

### 2.2 Onboarding — `/onboard` (EXTEND, do not rebuild)
`/onboard` already exists and already: explains the offer, collects the bot's purpose, languages,
**the user's current prompt**, platform + uuids, tools/APIs, test cases, and **known bugs**, then
produces an intake summary and hands off. Extensions required:

- accept the customer's **current prompt version** as the starting artifact (already partly there)
- keep asking for **remaining context / open questions** conversationally
- capture the **issues they want fixed** as *structured, individually testable items* (not prose)
- **immediately drive a test of those specific issues** — reproduce each before any fix
- be **multi-project and multi-language** aware (not KKB/DKB/Maya + Hi/Kn hard-coded)
- hand off to the new `/generate-test-cases` and `/translate-prompt` skills

### 2.3 Test-case generator skill — `/generate-test-cases` (NEW)
Once a bot is onboarded, generate **custom test cases for that specific bot**, on top of the
**generic** suite every bot already runs. Must produce, per bot:
- scenario list derived from the bot's own flow, audience, tools and reported issues
- a tester **persona** file per scenario (`raya/personas/`)
- a **bot-specific checklist** (`.claude/skills/voice-test/reference/checklists/<bot>.md`)
- explicit **pass/fail detection** for each case (what in the transcript / tool_calls proves it)
- must slot into the end-to-end workflow, not sit beside it

### 2.4 End-to-end workflow + fill the gaps
Document how every skill is called from onboarding onward, find missing pieces, and **add skills
for the gaps** so the whole thing can be handed to a third person.

---

## 3. Structural gaps the multi-project move exposes

These are not in the owner's list but block it. Found by auditing the repo on 2026-08-04.

| # | Gap | Where | Resolution |
|---|---|---|---|
| G1 | Path map hard-codes 3 bots | root `CLAUDE.md` | make per-project; `/register-bot` maintains it |
| G2 | No executable "add a new bot/project" step — only prose inside `/onboard` | `.claude/skills/onboard` | **NEW `/register-bot`** skill |
| G3 | `/sync-check` assumes exactly **two** languages (Hindi↔Kannada) | `.claude/skills/sync-check` | **EXTEND to N languages**, master + N mirrors |
| G4 | Daily regression suite hard-codes its fleet list and Hi/Kn parity | `raya/regression/static_regression.py` | **PARTLY DONE 2026-08-05:** the list was missing 2 LIVE bots (`dkb-hi-in`, `dkb-kn-in`) so they went unchecked while the digest said "16 bots" — added (now 18), plus a **coverage self-check** that emits a CRITICAL finding if any live deploy target is unchecked, and `scripts/build_fleet_manifest.py` generates `raya/regression/fleet.json`. REMAINING: make the suite *read* the manifest, and N-language parity |
| G5 | Tester personas exist only for `hi`/`kn` | `raya/personas/` | `/generate-test-cases` emits per-language personas |
| G6 | Voice-test checklists exist only for `{kkb,dkb,maya}` | `voice-test/reference/checklists/` | `/generate-test-cases` seeds a new bot's checklist |
| G7 | Digest bot labels assume KKB/DKB/Maya families | `raya/regression/*.py`, `open-items.json` | derive labels from the fleet manifest (G4) |
| G8 | Accessibility is a first-class concern for Purple Dots and has no checklist | new | **DONE 2026-08-05:** `## 14. Accessibility & access needs` added to `voice-test/reference/checklists/generic.md` — 7 fleet-wide items (pace, one-question-per-turn, silence-as-needs-time, repeat-on-request, no talking over, completes for non-default-speed callers, proxy/hand-over, no condescension) |

**G8 note.** Purple Dots serves people with disabilities. That has real prompt consequences —
pacing, patience/silence tolerance, repetition-on-request, screen-reader-free interaction, not
assuming the caller can hear/speak/respond at a default speed, and never making disability the
identity of the call. These belong in the **generic** checklist, not a per-bot one.

---

## 4. Target end-to-end flow (what a third person follows)

```
       ┌──────────────┐
       │  /onboard    │  intake: purpose, languages, prompt, platform, tools,
       └──────┬───────┘  test cases, ISSUES (structured) → intake summary
              │
       ┌──────▼─────────┐
       │ /register-bot  │  scaffold folder + files, path map, agents.json target,
       └──────┬─────────┘  CHANGELOG, fleet manifest entry
              │
       ┌──────▼──────────┐
       │/prompt-analyser │  read-only pre-flight audit vs learned bug patterns (67 as of 2026-08-05)
       └──────┬──────────┘
              │
       ┌──────▼────────────────┐
       │ /generate-test-cases  │  custom scenarios → personas + bot checklist
       └──────┬────────────────┘
              │
       ┌──────▼───────┐
       │ /voice-test  │  agent-to-agent live calls; reproduce each reported issue
       └──────┬───────┘
              │  confirmed prompt gap?
       ┌──────▼──────────────────────────┐
       │ /update-prompt (or /port-feature)│  snapshot → reconcile → surgical edit
       └──────┬──────────────────────────┘  → mirror languages → changelog → analyser
              │
       ┌──────▼──────────────┐
       │ raya_deploy.py      │  API PATCH + read-back verify
       └──────┬──────────────┘
              │
       ┌──────▼───────┐
       │ /voice-test  │  Tier 1 fix verification + Tier 2 blast radius, EVERY variant
       └──────┬───────┘
              │
       ┌──────▼──────────────┐      ┌──────────────────────┐
       │ /translate-prompt   │      │ daily standing check │  Tier 3, cloud cron,
       │ (language expansion)│      │ + digest email       │  6 check classes × every bot
       └─────────────────────┘      └──────────────────────┘
```

Supporting skills, called as needed: `/sync-check` (language parity), `/prompt-version`
(snapshot/rollback), `/raya-reconcile` (never clobber live), `/bug-fix` (tracker-driven loop),
`/update-memory`, `/update-output`.

---

## 5. Build order

1. `/translate-prompt` (NEW) — unblocks the Purple Dots multi-language ask
2. `/generate-test-cases` (NEW) — unblocks per-bot testing for any new bot
3. `/register-bot` (NEW) — G2
4. `/onboard` (EXTEND) — multi-project, structured issues, new hand-offs
5. `/sync-check` (EXTEND) — G3, N languages
6. `docs/WORKFLOW.md` — the third-person handover document
7. *(follow-up, code not skill)* config-driven regression fleet manifest — G4, G7

---

## 6. Non-negotiables that carry over to every new project

These already govern this repo and must not be diluted by multi-project use:

- **Surgical edits only** — smallest change; preserve spoken lines, variables, tool names, payloads.
- **Instructions in English; only spoken lines in the target language.**
- **Language sync** — master language leads; agnostic content verbatim, spoken content adapted.
- **No fix without a transcript** — never edit off a report or a hunch.
- **Push back before fixing** — data/input errors and backend faults are not prompt bugs.
- **Test every variant independently — never extrapolate** across language/direction/bot.
- **The three testing tiers** — fix verification → blast radius → daily standing check.
- **Reconcile before edit; snapshot before deploy.**
- **Every edit → CHANGELOG; every bug fix → `/prompt-analyser` pattern.**
