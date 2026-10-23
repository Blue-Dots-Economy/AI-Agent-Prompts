---
name: update-prompt
description: Change what a voice bot says or does by editing its conversation prompt, on the master language first and then every other language the bot speaks (read from raya/agents.json), with rules copied exactly and spoken lines re-authored per language. Use when someone reports a bug ("the bot said X, it should say Y", "the bot skipped the consent question", "fix this in the prompt"), gives feedback on a bot's behaviour, or wants a rule, line or step added, removed or changed, for any bot in any project (Blue Dots, Purple Dots, others). Also creates a new conversation prompt from scratch.
---

# Update Prompt

**What it changes:** one bot's **conversation prompt**, in every language of that bot, plus its
`CHANGELOG.md`, the analyser's bug list (for bug fixes) and, when needed, `raya/divergences.json`.

**Use something else for:** the memory prompt (`/update-memory`), the post-call output prompt
(`/update-output`), a new language (`/translate-prompt`), moving a feature between bots
(`/port-feature`), shrinking a prompt (`/slim-prompt`), rolling back (`/prompt-version`).

**Fast path:**
1. Read the open-issues list; get the call that shows the bug (no transcript, no fix).
2. Reconcile every target of the family with live, snapshot, run `/sync-check`, take a baseline of
   the language and size checks.
3. Decide: wording gap, or a rule the model already has and does not follow.
4. Edit the master, classify the change, mirror it to every language, re-run the checks.
5. Changelog (DEPLOYED, NOT VERIFIED until called), divergence entry if partial, analyser entry if a bug.
6. Deploy each target with `scripts/raya_deploy.py`, then one call per fix per variant.
7. Report in plain words with the changed lines and the call ids.

Rules this skill relies on and does not repeat: root `CLAUDE.md` → "Surgical edits only", "Core
principle: agnostic vs language-specific", "Sync rule", "Maya rule", "Testing is mandatory", "How
to report back". The section taxonomy is `reference/prompt-anatomy.md`.

## 0. Which files, which languages

- A bot's files are its **sync families** in `raya/agents.json`: same `agent`, same `direction`,
  same backend (legacy or Signals). Print them with the snippet in
  `../sync-check/reference/n-language-parity.md` → "1. Resolving the family". Each family has one
  **master** (same file, "Master language") and N mirrors, one per other `language` code. A family
  with one language (Maya today) has nothing to mirror.
- **Other families of the same bot** (inbound vs outbound, legacy vs Signals, a Slim variant) are
  not mirrors, but they often carry the same text and the same bug. Grep them for the line you are
  changing. Where the bug is present, apply the change to that family too, through this same
  procedure (its own master first). Where it is deliberately not applied, say so in the report.
- Never take the bot list or language list from this file or from filenames.

## 1. Before editing

1. **Open issues.** Read the bot's open-issues list (the tracker sheet, or the issue table in
   `raya/intake/<bot-id>.md` when `/onboard` created one). Know what is already open; group issues
   by cause, one fix per cause (`/bug-fix` → "Four habits").
2. **Ground it.** Pull the real call and its input args. If the inputs were wrong, the backend
   failed, or no call reproduces it, do not edit: say "the prompt is fine, the inputs were wrong" (or
   ask for the call id). Root `CLAUDE.md` → "Feedback-loop operating sequence".
3. **Reconcile with live, for every target you will touch.**
   `python3 scripts/raya_deploy.py diff <target-id>`. If live is ahead, adopt it with
   `python3 scripts/raya_deploy.py pull <target-id>` and commit that before editing. If GET is
   empty or flaky, use `/raya-reconcile`. Never edit a file that is behind live.
4. **Snapshot.** `bash scripts/prompt-version.sh save <bot-folder> pre-<slug> "<why>"` (the folder
   name, e.g. `KKB`, `KKB-Slim`, `TRRAIN`; it snapshots every prompt in that folder).
5. **Sync first.** Run `/sync-check` on the family. Reconcile any unregistered drift before adding
   a new change.
6. **Baseline the checks** (so you can tell new failures from old ones), for each mirror:
   ```bash
   python3 scripts/language_checks.py "<master.md>" "<mirror.md>" --lang <iso> --target <mirror-target-id>
   python3 scripts/prompt_size.py check "<file.md>" --target <target-id>
   ```
   Add `--src <iso>` to `language_checks.py` when the master is not Hindi.

## 2. Decide what kind of fix it is

- **Wording gap:** the rule is missing, ambiguous, or contradicted by another line or an example.
  Fix the text. First grep the bot's wrong words verbatim against the whole prompt: a hit in a
  worked example is the cause (analyser D50); fix the example.
- **Following-instructions problem:** the rule is already clear and the model does not keep it.
  Before any remedy, run D1-D3 (count how often the right branch ever happened, split by input,
  read the guard): root `CLAUDE.md` → "FIRST localize the cause". A clean split by input means it
  is a condition bug, not disobedience.
- **Three-call rule:** if a fix does not hold across three calls, stop adding text. Change the
  mechanism (the ladder in root `CLAUDE.md`: remove the wrong option rather than forbid it; move a
  constraint into the tool schema only when the model cannot fake the value, D91/D95) or escalate
  with the call ids. Never write a third wording of a guard that already failed twice.
- **Before editing a section, list what it touches:** `python3 scripts/prompt_map.py impact <file>
  --section "<title>"` (rules that point at it, values it writes and their readers, the same part in
  every language, and with `--sheet` the test rows to re-run), and `prompt_map.py rules-about <file>
  <term>` for the rules already about the thing you are changing: scope or replace one before adding one.
- **Second failed fix on the same issue: stop and read the prompt cold** before touching it again.
  Run `/prompt-analyser` in a fresh subagent with no history (its step 0) and
  `python3 scripts/prompt_structure.py <file>`. A rule the bot "will not follow" is often a rule it
  never reaches: a step number or cross-reference that sends it somewhere else (D125). On Orange Dots
  hours of added rules did nothing; a fresh read found the numbering in minutes.
- **After every edit that adds, removes, renumbers or renames a section**, run
  `python3 scripts/prompt_structure.py <file>` on every language you touched: 0 FAIL before deploy.
- **Size:** every added line costs budget, and past a bot's limit it stops calling tools with no
  error (D116). Prefer deleting or replacing a line over adding one.

## 3. Edit, classify, mirror

1. **Edit the master.** Read the section in the master and in each mirror first. Smallest change,
   in the surrounding style. Instructions in English; only spoken lines in the call's language.
2. **Classify** with `reference/prompt-anatomy.md`: AGNOSTIC (copied byte-identical), SPECIFIC
   (re-authored per language), MIXED (copy the rule, re-author the quoted speech).
3. **Mirror to every language** of the family. SPECIFIC lines are re-authored to the
   `/translate-prompt` standard: everyday words from `raya/translations/lexicon.json`, that
   language's gender rule, numbers as words, pinned place names, matching the existing section's
   phrasing. Never paste master-language text into a mirror.
4. **Re-run the checks** from step 1.6. A FAIL that was not in the baseline blocks the deploy (a
   rule that now names the wrong language, a digit in a spoken line, a changed payload value). A
   size BLOCK means slim the master first (`/slim-prompt`).
5. **Maya gate (KKB changes).** If a KKB change touches logic Maya shares, stop and ask whether to
   apply it to Maya. If yes, apply it without touching Maya's divergences (root `CLAUDE.md` →
   "Maya rule"; the MPL offer listed there was removed on 2026-10-12, see `Maya/CHANGELOG.md`).
6. **Read the diff.** It must contain only the intended change, in every file.

## 4. Record

1. **Changelog:** append to `<Bot>/CHANGELOG.md` (format in root `CLAUDE.md` → "Changelog rule"),
   one entry per bot touched. Untested changes say **DEPLOYED, NOT VERIFIED** in the entry.
2. **Divergence (only if the change does not land in every language of the family):** add or update
   the entry in `raya/divergences.json` in the same change, using the schema in
   `../sync-check/reference/n-language-parity.md` → "5. Registry". Without it the next
   `/sync-check` "fixes" the difference away.
3. **Analyser (bug fixes only):** add or sharpen the pattern in
   `../prompt-analyser/reference/bug-patterns.md` (symptom, root cause, detection heuristic, fix
   direction, source bot + date), and `section-checklists.md` if a section must always exist.

## 5. Deploy and prove

1. **Deploy each target:** `python3 scripts/raya_deploy.py deploy <target-id> --dry-run`, show the
   diff, then deploy after the user approves (`--yes` only after that approval). The script
   snapshots, checks the name guard and size limit, and verifies the PATCH response. That proves the
   prompt shipped, not that the bot behaves.
2. **Test, three tiers** (root `CLAUDE.md` → "The three testing tiers"), with `/voice-test`:
   - Tier 1: the exact failing scenario, on **each** changed variant (each language, each
     direction, each bot). One call id per fix per variant; never extrapolate from one language.
   - Tier 2: the neighbours of the change (the same section, the mirrored lines, any tool payload
     touched, the whole flow still completes).
   - Tier 3: the standing daily check in `raya/regression/` covers the long tail; it does not
     replace tiers 1 and 2.
   - **Inbound bots are testable:** give the inbound agent an integer `out_did` and dial the tester
     (`/voice-test` → Inbound bots). Inbound test data goes on the tester's own number.
3. If a result is mixed, the fix is not finished: go back to section 2. "Intermittent" is not a
   result. On a regression, `/prompt-version` restore, then redeploy.

## 6. Report (plain words)

Shape from root `CLAUDE.md` → "How to report back": Fixed (call id + the line that proves it),
Failed / still open, New bugs, Next. For each fix: one sentence on what the bot did wrong, one on
what it does now, and the changed prompt lines (before → after, a few lines, master and each
mirror for MIXED changes). Name the open issues this closes and end with what is still open from
before. Every fix without a call id is reported as DEPLOYED, NOT VERIFIED.

## Creating a new conversation prompt

- **New language for an existing bot:** `/translate-prompt`, not this skill.
- **New bot from a supplied prompt:** `/register-bot` files it verbatim as the baseline.
- **New prompt written from scratch:** scaffold from `reference/prompt-anatomy.md`, take the
  variables, tools and persona from `../port-feature/reference/agent-schemas.md` (add the bot there),
  include the memory block if the bot has memory (root `CLAUDE.md` → "Memory injection block"),
  register it with `/register-bot`, then add languages with `/translate-prompt`.

## Guardrails

- The master leads; a mirror never leads.
- Never localize a `${variable}`, tool name, payload field or fixed param; never translate AGNOSTIC
  text; never write rule prose in the call's language.
- When unsure whether a line is AGNOSTIC or SPECIFIC, check the anatomy, then ask.
