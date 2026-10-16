---
name: update-output
description: Create or change a voice bot's output prompt (the post-call report), the language-agnostic spec that turns a finished call into structured fields such as call answered, jobs applied, drop reason, interest and an English summary. Use when someone says "capture X from every call", "add a field to the call report", "the report says applied but nothing was applied", "drop_reason is wrong", "change the allowed values of a field", "the call output is empty or wrong", or wants an output prompt for a bot that has none, for any bot in any project. One output prompt per bot (KKB-Slim has its own), shared by all its languages.
---

# Update Output

**What it changes:** one bot's output prompt (path map in root `CLAUDE.md`) and its
`CHANGELOG.md`. The file is language-agnostic: extracted text uses the speaker's words and
`final_summary` is English, so there is no language twin to mirror.

**Fast path:**
1. Ground it in a real call: its transcript and the `call_output` it produced.
2. Compare the repo file with the live output prompt on every agent that carries it; save any live
   copy that differs; snapshot the folder.
3. Edit the field list, and the EXAMPLE OUTPUT and Rules where the layout has them.
4. Changelog (DEPLOYED, NOT VERIFIED), analyser entry if a bug.
5. Deploy to every agent; prove with a real call's `call_output`.

Reference: `reference/output-anatomy.md` (the two layouts, field types, extraction rules, per-bot
notes). Bots with an output prompt today: KKB, KKB-Slim (its own file), DKB, Maya, TRRAIN.

## 1. Before editing

1. **Ground it.** Pull a call where the field came out wrong (or is missing): the transcript, the
   tool results and the `call_output` on the call record. If the transcript itself is wrong, that is
   a conversation-prompt bug (`/update-prompt`), not an output bug.
2. **Find every agent that carries this output prompt:** every conversation target of the bot in
   `raya/agents.json` (all languages, directions and backends). KKB's file is not on the KKB-Slim
   agents, which use `KKB-Slim/KKB Slim Output.md`. TRRAIN has its own `kind: output` rows.
3. **Compare with live, per agent** (read-only without `--yes`):
   ```bash
   python3 scripts/raya_side_prompt.py output <conversation-target-id> "<Bot>/<Bot> Output.md"
   ```
   For a `kind: output` row with an agent id, `python3 scripts/raya_deploy.py diff <output-target-id>`
   works too. If live differs on any agent (live output prompts have run ahead of the repo before,
   and some agents carry extra fields), save the live copy with the snippet in
   `../update-memory/SKILL.md` step 1.3 (`F=output_instructions`) into
   `raya/live-snapshots/<target>.output_instructions.pre-<slug>.md`, and settle which is right with
   the user **before** editing.
4. **Snapshot the repo:** `bash scripts/prompt-version.sh save <Bot-folder> pre-<slug> "<why>"`.

## 2. Edit (update)

1. Note which layout the file uses (phase-based or numbered field list).
2. Apply the change:
   - **New field:** add it with its name, meaning and allowed values. In a numbered list, insert
     with a letter suffix (`12a`) rather than renumbering. Add it to the EXAMPLE OUTPUT JSON and the
     Rules block where they exist.
   - **Enum change:** update that field's allowed-value list (and the example, if it shows it).
   - **Extraction change:** edit the Rules block, or the field's own definition.
3. Keep the extraction rules: never infer; use the speaker's words; `"NA"` / `[]` / `0` sentinels;
   mutually exclusive arrays stay exclusive; no invented names or salaries; English `final_summary`.
4. **Example values become outputs** (analyser D50). A value shown in EXAMPLE OUTPUT will be copied
   into real reports when the call gives no evidence. Keep example values plainly illustrative, and
   do not add a metric the model can only guess (a `call_direction` field was backed out of KKB-Slim
   for this reason; read such facts from the call record instead).
5. Tool-outcome fields (`jobs_applied`, `applications_count`) must follow the tool results in the
   transcript, not what the bot claimed aloud.

## 2b. Create (a bot with no output prompt)

1. Pick the layout of the closest bot (numbered field list + EXAMPLE OUTPUT + Rules is the default;
   DKB uses phases).
2. Start from that bot's file and re-domain the fields to the new bot's call.
3. Keep the full extraction Rules block. Create the file at the path-map location (add the
   path-map row through `/register-bot` if the bot has none).

## 3. Record

- `<Bot>/CHANGELOG.md`, with **DEPLOYED, NOT VERIFIED** until a call proves it.
- Bug fixes only: teach the analyser (`../prompt-analyser/reference/bug-patterns.md`), per root
  `CLAUDE.md` → "Bug-fix feedback loop".

## 4. Deploy

Ask before pushing; show the field changes first.
- **TRRAIN** (its own `kind: output` rows with agent ids):
  `python3 scripts/raya_deploy.py deploy <output-target-id> --dry-run`, then without `--dry-run`
  (`--yes` only after approval). It snapshots, verifies and logs to `raya/deploy-history.md`.
- **Every other bot:** the `kkb-output`, `dkb-output` and `maya-output` rows have no agent id and
  cannot be deployed with `raya_deploy.py`. Use
  `python3 scripts/raya_side_prompt.py output <conversation-target-id> "<file>" --yes`, once per
  agent from step 1.2. It PATCHes `output_instructions` and verifies against the PATCH response and
  a fresh GET. It does **not** snapshot, check size, or write `raya/deploy-history.md`: the step 1.3
  live copy is the rollback, and the changelog lists each agent pushed.

## 5. Prove it

Deploy proves the text shipped. Proof is a real call placed after the deploy on the **tester
number** (or a real production call, read-only), whose `call_output` shows the changed field with
the right value, and whose other fields did not regress. `call_output` arrives some time after the
transcript: poll until it exists (`/voice-test`, platform reality 14). Name the call id and the field
value. Do it on each agent type that carries the prompt (each language, direction, backend); inbound
bots are testable (`/voice-test` → Inbound bots). Running a transcript through the prompt by hand is a static
check, never proof. Until called: DEPLOYED, NOT VERIFIED. On a regression, push the saved live copy
back and `/prompt-version` restore the repo.

Report in plain words: what the call report now captures, the fields changed (before → after), the
agents pushed, and the call ids or DEPLOYED, NOT VERIFIED.

## Guardrails

- Surgical edits only; preserve every other field, rule and line.
- `final_summary` is always English.
- Sentinels stay consistent: `"NA"` strings, `[]` arrays, `0` counts.
- Array-of-objects fields stay full objects; never flatten them to strings.
