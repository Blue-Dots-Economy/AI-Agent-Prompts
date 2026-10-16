# Prompt Tuner

System prompts for three production voice AI agents, plus the tooling to iterate on them
safely. This repo is **self-contained**: clone it, open it in Claude Code, and everything
(prompts, skills, version history, bug-pattern catalog) works with no external dependencies.

The job of anyone working here is to **iterate on these prompts from feedback/bugs while keeping
the language variants in sync**. A wording change in one language that does not land in its twin
is a regression. Read [`CLAUDE.md`](CLAUDE.md) first — it is the operating manual and takes
precedence over everything here.

## The agents

| Agent | What it is | Languages |
|---|---|---|
| **KKB** — *काम की बात* | Government job-matching agent for workers/seekers | Hindi + Kannada (+ inbound) |
| **DKB** — *धंधे की बात* | Employer/MSME job posting & verification agent | Hindi + Kannada (+ inbound) |
| **Maya** — *माया* | Campus-recruitment spinoff of KKB for UP graduates | Hindi only (+ inbound) |

Each agent has three prompt types:
- a **conversation prompt** — one file per language (the live voice script);
- a **memory prompt** — one language-agnostic file; updates per-caller memory JSON after each call;
- an **output prompt** — one language-agnostic file; extracts structured call variables from a transcript.

**Outbound** agents are called by the system (bot dials the user). **Inbound** variants are for the
user calling in: the intro changes, input variables are dropped, the new-vs-returning fork is decided
by the `get_profile` result, and (for seeker agents) the job list is a hardcoded in-prompt inventory.

## File map

| Agent | Hindi | Kannada | Inbound | Memory | Output |
|---|---|---|---|---|---|
| KKB | `KKB/KKB Placeholder Hindi.md` | `KKB/KKB Placeholder Kannada.md` | `KKB/KKB Placeholder Inbound.md` + `…Inbound Kannada.md` | `KKB/KKB Memory.md` | `KKB/KKB Output.md` |
| DKB | `DKB/DKB Hindi.md` | `DKB/DKB Kannada.md` | `DKB/DKB Inbound Hindi.md` + `…Inbound Kannada.md` | `DKB/DKB Memory.md` | `DKB/DKB Output.md` |
| Maya | `Maya/Maya Hindi.md` | — | `Maya/Maya Inbound.md` | `Maya/Maya Memory.md` | `Maya/Maya Output.md` |

Each agent folder also has a `CHANGELOG.md` — every prompt edit is logged there.

## Core principle: agnostic vs language-specific

Every conversation prompt mixes two kinds of content, and **every edit must be classified before it is
mirrored** across languages:
- **Language-agnostic** — call-flow logic, phase/step structure, variable names, tool-call rules and
  JSON payloads, conditions/routing, safety checks, section skeleton → **copied verbatim** across languages.
- **Language-specific** — spoken scripts, examples, number-to-word spellings, script rules (Devanagari
  vs Kannada), culturally-adapted phrases → **translated and adapted**.

Hindi is the **source of truth**; changes are made there first, then mirrored to Kannada. The full
section-by-section taxonomy is in `.claude/skills/update-prompt/reference/prompt-anatomy.md`.

## Skills (`.claude/skills/`)

Repeatable workflows, invoked in Claude Code as `/<name>`:

| Skill | Purpose |
|---|---|
| `/update-prompt` | Apply a feedback item / bug fix to a conversation prompt; edit Hindi, mirror to Kannada. Auto-snapshots first and runs `/sync-check`. |
| `/sync-check` | Audit whether an agent's Hindi and Kannada prompts have drifted; reconcile. |
| `/port-feature` | Carry a feature from one agent to another (e.g. KKB → Maya), re-domained to the target. |
| `/update-memory` | Create/edit an agent's memory prompt. |
| `/update-output` | Create/edit an agent's output prompt. |
| `/prompt-analyser` | Pre-flight, read-only audit of a prompt for latent gaps / bug-prone patterns. |
| `/prompt-version` | Save / list / diff / restore version snapshots (see below). |

The **bug-pattern catalog** — every failure class learned from past bugs, with detection heuristics —
lives in `.claude/skills/prompt-analyser/reference/bug-patterns.md`, with required-section checklists in
`section-checklists.md`. Fixing a bug is not done until the analyser is taught to catch it (see `CLAUDE.md`
→ "Bug-fix feedback loop").

## Version history

A local, git-independent rollback safety net so you can always return to a last-stable prompt without
relying on commits/pushes. Managed by [`scripts/prompt-version.sh`](scripts/prompt-version.sh):

```bash
scripts/prompt-version.sh save    KKB stable-2026-07-16 "verified good on live calls"
scripts/prompt-version.sh list    KKB
scripts/prompt-version.sh diff    KKB stable-2026-07-16
scripts/prompt-version.sh restore KKB stable-2026-07-16   # auto-snapshots current first
```

Snapshots live under `versions/<Agent>/` (bodies git-ignored — a local safety net; the per-agent
`HISTORY.md` logs are tracked). `/update-prompt` auto-snapshots before every edit. Durable, shareable
stable points are also marked with git tags.

## Working here

1. Read [`CLAUDE.md`](CLAUDE.md) — the operating manual (surgical-edit rules, sync rule, changelog rule,
   the Maya flag-and-ask rule, the memory-injection block requirement).
2. To change an agent, use the matching skill above (not raw edits) — they enforce the sync + changelog +
   feedback-loop conventions.
3. These prompts run **live voice agents**. Every edit must be **surgical**: the smallest change that
   accomplishes the task, preserving spoken lines, variable names, tool names, and JSON payloads exactly.

## Repository layout

```
CLAUDE.md            ← operating manual (read first)
README.md            ← this file
KKB/  DKB/  Maya/     ← per-agent prompts + CHANGELOG.md
scripts/             ← prompt-version.sh (version-history tool)
versions/            ← version snapshots (bodies git-ignored) + per-agent HISTORY.md
.claude/skills/      ← the repo's skills + their reference/ files
```
