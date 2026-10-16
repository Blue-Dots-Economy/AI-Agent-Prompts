---
name: port-feature
description: Carry a feature, rule, step or fix that already works in one voice bot into another bot, rewritten for the target bot's own variables, tools, persona and callers rather than copied, then mirrored to every language of the target. Use when someone says "do the same in DKB", "give Maya the consent step KKB has", "port this to the Purple Dots bot", "apply this fix to the other bots too", "reuse this feature in <bot>", or wants something from one bot extended to others, in any project.
---

# Port Feature

**What it changes:** the conversation prompts of one **target** bot (its master and every mirror),
plus the target's `CHANGELOG.md` and, when needed, `raya/divergences.json`. One target at a time.

**Use something else for:** a change that exists nowhere yet (`/update-prompt`), the same change
across the languages of one bot (`/update-prompt` mirrors it), a new language (`/translate-prompt`).

**Fast path:**
1. Read the feature in the source's master file; list the variables, tools and lines it uses.
2. Map each to the target (`reference/agent-schemas.md`); stop and ask on any hard gap.
3. Prepare the target exactly as `/update-prompt` does: open issues, reconcile with live, snapshot,
   `/sync-check`, baseline checks.
4. Rewrite the feature for the target's callers, place it, mirror it to every language.
5. Changelog with `Ported from:`, divergence entry if partial, deploy, one call per target variant.

## Procedure

1. **Identify** the source bot, the feature (a section, rule, spoken behaviour or flow step) and the
   target bot. Read the feature in the source's master file in full, and check the source's
   `CHANGELOG.md` for whether it was ever proven by a call. Porting an unproven feature ports an
   unproven feature: say so.
2. **Map the schema gap** using `reference/agent-schemas.md` (re-check the target's real prompt;
   the file says how). For each variable, tool and payload field the feature uses:
   - a direct equivalent → remap the name (KKB `recommendations[].job_id` → DKB `${job_id}`);
   - no equivalent → **flag it and pause**. Never invent a variable, tool or payload field. Legacy
     and Signals variants of one bot have different tools; check which you target.
3. **Prepare the target** with `/update-prompt` section 1 (open issues, reconcile every target of the
   family with live, `bash scripts/prompt-version.sh save <target-folder> pre-port-<slug> "<why>"`,
   `/sync-check`, baseline `language_checks.py` and `prompt_size.py check`). A port adds text, so
   the size check matters (D116).
4. **Re-domain** the content for the target's callers and persona (a seeker-facing line becomes an
   employer-facing one for DKB; feminine forms for Maya). Keep the logic; change only what the domain
   requires. Rules in English; only spoken lines in the call's language. Never carry the source's
   spoken lines over unchanged.
5. **Place it** in the matching section of the target's **master** file
   (`../update-prompt/reference/prompt-anatomy.md`). If the target lacks that section, add it where
   the taxonomy puts it.
6. **Mirror** to every other language of the target's family with `/update-prompt` section 3
   (classify, mirror, re-run the checks, read the diff). If the target has other families (inbound,
   Signals, Slim) that need the feature, port to each as its own step.
7. **Record:**
   - `CHANGELOG.md` of the **target**, with a `**Ported from:** <source bot>` line and
     **DEPLOYED, NOT VERIFIED** until called.
   - `raya/divergences.json` entry if the port deliberately skips some languages of the family
     (schema: `../sync-check/reference/n-language-parity.md` → "5. Registry").
   - An entry in `../prompt-analyser/reference/bug-patterns.md` only if the port fixes a bug the
     analyser does not already describe (root `CLAUDE.md` → "Bug-fix feedback loop").
8. **Deploy and prove** with `/update-prompt` section 5: deploy each target with
   `scripts/raya_deploy.py` after approval, then `/voice-test` a scenario that exercises the ported
   feature on **each** target variant, and check the target's normal flow still completes. Inbound
   variants are testable (`/voice-test` → Inbound bots). One call id per variant; until then, DEPLOYED, NOT
   VERIFIED.
9. **Report** in plain words: what the target bot now does, the remapping used (a small table), any
   gaps flagged, the changed lines (before → after) and the call ids. End with what is still open.

## Notes

- **Maya:** porting INTO Maya is an explicit request, unlike the KKB→Maya flag-and-ask in
  `/update-prompt`. Still never overwrite Maya's divergences (root `CLAUDE.md` → "Maya rule").
- **TRRAIN** has only `get_profile`: any feature that writes data cannot be ported to it as is.
- Surgical edits only: the smallest footprint in the target, every other line preserved.
