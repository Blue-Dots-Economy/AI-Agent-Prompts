# Memory Prompt Anatomy

A memory prompt is a **language-agnostic** instruction set: it reads the prior memory JSON
plus the latest conversation and emits an updated memory JSON. All output values are in
**English**, regardless of conversation language. There is one memory prompt per bot (no
language twin), pushed separately to each of the bot's live agents. `DKB/DKB Memory.md` is the complete reference implementation.

## Required sections (in order)

1. **Role**: "You are a memory updater for <Agent> (<full name>). Review the latest
   conversation between the <user type> and the agent and update the <user> memory."
2. **Goal**: produce a COMPLETE updated memory JSON in the same schema, plus three derived fields:
   - `recent_changes`: list of what changed this turn (only changed fields)
   - `last_conversation_summary`: 2–3 lines, memory-relevant facts of the latest call
   - `overall_conversation_summary`: 4–5 lines, cumulative journey; no filler like "owner dropped after greeting"
   - Rule: only change fields with explicit evidence; preserve all others exactly.
3. **Inputs**: `${old_memory}` (existing JSON) and `${conversation}` (latest call).
4. **Language rule (IMPORTANT)**: conversation may be any language; **all memory output
   values MUST be English**; translate non-English statements; keep proper nouns
   (people/companies/places) in standard English spelling.
5. **Entity Map**: flat, 1-level JSON keys only (no nested layer objects). Values are
   strings/numbers/booleans/arrays of strings (avoid arrays of objects). Where enums/brackets
   exist, store the bracket in the main field and the precise value in a parallel `*_exact`
   field. Organize the keys into labeled layers (see below).
6. **Update rules**: update only on clear direct evidence; keep old value when
   ambiguous/hypothetical/conflicting; prefer the most recent explicit correction; never
   invent/infer; valid JSON only, no markdown/commentary; no keys beyond the schema.
7. **recent_changes rules**: JSON array of `{field, from, to, evidence}`; entry only for
   changed fields; `[]` if nothing changed.
8. **last_conversation_summary rules**: 2–3 lines, English, refer to the user as "You",
   memory-relevant only; fixed fallback string if nothing relevant.
9. **overall_conversation_summary rules**: 4–5 lines, English, cumulative, journey-focused;
   exclude call drops / greeting-only sessions.
10. **Output JSON schema**: the exact flat schema, every field present, ending with
    `recent_changes`, `last_conversation_summary`, `overall_conversation_summary`.

## Entity-map layers

Adapt the layer contents to the bot's domain; keep the layered shape. Layer names vary by bot
(BUSINESS, PROFILE, APPLICATION, OFFER, CONTACT PREFERENCE); what matters is the shape.

- **IDENTITY LAYER:** who they are. Primary key = phone number. (DKB: `business_id`,
  `owner_name`, `business_name`, location, `language_preference`, `digital_literacy`.)
- **DOMAIN LAYER:** what they are or run. (DKB "BUSINESS LAYER": sector, product, size. KKB and
  Maya "PROFILE LAYER": role sought, qualification, experience, skills.)
- **CONSTRAINT LAYER:** what limits choices (budget, urgency, location flexibility, preferences).
  For a seeker: desired salary, commute radius, shift constraints.
- **JOURNEY LAYER:** what they have tried. For a seeker: options shown, applications, outcomes.
- **CURRENT SESSION LAYER:** where they are now (`session_count`, incremented by 1; routing mode,
  last action, drop-off reason).

## Per-bot notes

Every Blue Dots bot has a memory prompt; read the file for its exact fields.

- **DKB:** employer memory. The reference implementation.
- **KKB:** seeker memory (identity with `profile_id` and district-level location only, profile,
  constraints, journey, session). Also used by the KKB-Slim agents. `jobs_applied` is appended from
  a successful `apply_job` tool result, and the conversation prompt's already-applied pre-check
  reads it: keep that field's name and meaning in step with the conversation prompt.
- **Maya:** KKB seeker memory plus campus fields such as `hr_contact_shared`. The MPL fields were
  removed on 2026-10-12. `last_options_presented` stores a count and a date, never the jobs
  themselves (stored jobs were offered as live inventory on `a4f378b9`).
- **TRRAIN:** follow-up memory with APPLICATION (`applied_job_role`, `remembered_application`,
  `right_person`), OFFER (`trrain_pitched`, `trrain_interest`, `trrain_pitch_count`, objections),
  CONTACT PREFERENCE (`do_not_call`, `preferred_callback_time`, `last_call_outcome`) and SESSION
  layers.
- **A new bot:** start from DKB's file and re-domain; record the bot's own notes here.

## Common edits

- **Add/rename/retire a field:** edit the Entity Map description AND the Output JSON schema
  (keep them identical). Note enum changes in both places.
- **Change an enum's allowed values:** update the bracketed list in the Entity Map line.
- **Adjust summary length/voice rules:** edit the relevant `*_summary rules` section only.
- **A field another prompt reads** (the conversation prompt's pre-check, the output prompt): change
  all readers in the same change, or the reader silently stops matching.
