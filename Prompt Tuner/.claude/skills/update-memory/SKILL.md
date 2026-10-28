---
name: update-memory
description: Create or change a voice bot's memory prompt, the English-only instruction that updates what the bot remembers about each caller after every call (fed back into the next call as contact_memory). Use when someone says "the bot should remember X", "it forgot the caller applied last time", "add a field to memory", "rename or remove a memory field", "change the memory summary", "turn on memory for <bot>", or a bug traces to what was or was not stored between calls, for any bot in any project. One memory prompt per bot, shared by all its languages.
---

# Update Memory

**What it changes:** one bot's memory prompt (`<Bot>/<Bot> Memory.md`, path map in root
`CLAUDE.md`), its `CHANGELOG.md`, and, when memory is first enabled, the memory block in each of
the bot's conversation prompts. The file is language-agnostic (all output values in English), so
there is no language twin to mirror.

**Fast path:**
1. Ground it in a real call (what was said, what the next call shows it remembered).
2. Compare the repo file with the live memory prompt on every agent of the bot; save any live copy
   that differs; snapshot the folder.
3. Edit: Entity Map and Output JSON schema always change together.
4. Changelog (DEPLOYED, NOT VERIFIED), analyser entry if a bug.
5. Deploy to every agent that carries it; prove with a two-call test on the tester number.

Reference: `reference/memory-anatomy.md` (required sections, flat entity map, layers, per-bot notes).
`DKB/DKB Memory.md` is the reference implementation. Bots with a memory file today: KKB (also used
by KKB-Slim), DKB, Maya, TRRAIN; check the path map for others.

## 1. Before editing

1. **Ground it.** No change without a real call: the transcript that should have produced the
   memory, and the next call showing what the bot did with it. Remember that the stored memory
   itself cannot be read back from the platform (`/voice-test` → 6d), so the evidence is behaviour.
2. **Find every agent that carries this memory.** One memory file is pushed separately to each live
   agent: every conversation target of the bot in `raya/agents.json` (all languages, directions and
   backends; KKB's file also on the KKB-Slim agents). Some bots also have their own `kind: memory`
   rows (Maya, TRRAIN).
3. **Compare with live, per agent** (read-only without `--yes`):
   ```bash
   python3 scripts/raya_side_prompt.py memory <conversation-target-id> "<Bot>/<Bot> Memory.md"
   ```
   It prints the live and local size and hash. For a `kind: memory` row,
   `python3 scripts/raya_deploy.py diff <memory-target-id>` works too. If live differs from the repo
   on any agent, someone may have changed it on the console: save that live copy and settle which
   is right with the user **before** editing. To save it (read-only GET):
   ```bash
   T=<conversation-target-id>; F=memory_instructions; SLUG=<change-slug>
   python3 -c "
   import sys, json; sys.path.insert(0, 'scripts'); import raya_side_prompt as r
   t = next(x for x in json.load(open('raya/agents.json'))['targets'] if x['id'] == sys.argv[1])
   s, a = r.raya('/api/agent/' + t['raya_agent_id'][r.ENV]); a = a.get('data', a)
   open(sys.argv[3], 'w', encoding='utf-8').write(a.get(sys.argv[2]) or '')
   " "$T" "$F" "raya/live-snapshots/$T.$F.pre-$SLUG.md"
   ```
4. **Snapshot the repo:** `bash scripts/prompt-version.sh save <Bot-folder> pre-<slug> "<why>"`.

## 2. Edit (update)

1. Identify the change: new, renamed or retired field; enum change; update-rule or summary change.
2. Apply it. **The Entity Map and the Output JSON schema list the same fields:** add, rename or
   retire in both; update enum lists in the Entity Map line.
3. Keep the invariants: flat 1-level keys, English-only values, `*_exact` companions for bracketed
   enums, the three derived fields (`recent_changes`, `last_conversation_summary`,
   `overall_conversation_summary`), and the update rules.
4. If the conversation prompt reads a memory field (a pre-check, an opening line), check the field
   name and meaning still match what that prompt expects, in every language file.
5. Example values in the memory prompt can leak into calls (a sample role and company in Maya's
   memory were offered to a caller on `a4f378b9`). Keep examples neutral.

## 2b. Create (a bot with no memory prompt)

1. Start from `DKB/DKB Memory.md`; re-domain the Role line and the layers per
   `reference/memory-anatomy.md`.
2. Write every required section in order, ending with the exact Output JSON schema.
3. Make sure it backs whatever the conversation prompt expects from memory.
4. Create the file at the path-map location (add the path-map row through `/register-bot` if the
   bot has none).
5. **Memory block:** every conversation prompt of the bot, in every language, must contain the
   three-line block from root `CLAUDE.md` → "Memory injection block", verbatim. Check:
   ```bash
   python3 - <Bot> <<'PY'
   import json, sys
   block = "### Contact context\nHere is the caller context:\n{${contact_memory}}"
   for t in json.load(open("raya/agents.json"))["targets"]:
       if t["agent"] == sys.argv[1] and t["kind"] == "conversation":
           ok = block in open(t["file"], encoding="utf-8").read()
           print("OK     " if ok else "MISSING", t["id"], t["file"])
   PY
   ```
   Adding the block to a conversation prompt is a conversation-prompt edit: do it through
   `/update-prompt` (snapshot, mirror, changelog, deploy) in the same change.

## 3. Record

- `<Bot>/CHANGELOG.md`: the memory change, and any conversation files that got the block. Untested
  changes say **DEPLOYED, NOT VERIFIED**.
- Bug fixes only: teach the analyser (`../prompt-analyser/reference/bug-patterns.md`), per root
  `CLAUDE.md` → "Bug-fix feedback loop".

## 4. Deploy

Ask before pushing; show the user the before/after field list first.
- **Bot with its own `kind: memory` rows** (Maya, TRRAIN today):
  `python3 scripts/raya_deploy.py deploy <memory-target-id> --dry-run`, then without `--dry-run`
  (`--yes` only after approval). It snapshots, verifies the response, sets `memory_enabled`, and
  logs to `raya/deploy-history.md`.
- **Every other agent** (KKB, DKB, the Maya Signals agents, KKB-Slim):
  `python3 scripts/raya_side_prompt.py memory <conversation-target-id> "<file>" --yes`, once per
  agent from step 1.2. It PATCHes `memory_instructions` and `memory_enabled`, and verifies against
  the PATCH response and a fresh GET. It does **not** snapshot, check size, or write
  `raya/deploy-history.md`: the step 1.3 live copy is the rollback, and the changelog entry lists
  each agent pushed.

## 5. Prove it

Deploy proves the text shipped, not that memory works. Proof is behaviour across two calls on the
**tester number** (never a real caller's number): call 1 produces the fact, call 2 shows the bot
using it (or no longer using a retired field). Name both call ids and the line in call 2 that shows
it. `scripts/raya_memory_test.py run <bot> --fact …` does exactly this and grades it per detail
(`/voice-test` → Memory test); run its `check` first. Do this on each agent type that carries the memory (outbound and inbound, each language, each
backend); inbound bots are testable (`/voice-test` → Inbound bots, and the inbound bot looks up the tester's
own number). Running a transcript through the memory prompt by hand is a useful static check, never
proof. Until called: DEPLOYED, NOT VERIFIED. On a regression, push the saved live copy back and
`/prompt-version` restore the repo.

Report in plain words: what the bot will now remember, the fields changed (before → after), the
agents pushed, and the call ids or DEPLOYED, NOT VERIFIED.

## Guardrails

- Surgical edits only; preserve every other field, rule and line.
- Output values are always English; keep the Language rule section.
- No nested objects and no arrays of objects in the entity map.
