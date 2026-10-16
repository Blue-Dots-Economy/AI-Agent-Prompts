# Output Prompt Anatomy

An output prompt is a **language-agnostic** extraction spec: it reads a finished call
transcript and emits a structured object of call variables. The call may be in any
language; extracted text uses the speaker's words and `final_summary` is always **English**.
One output prompt per bot (no language twin), pushed separately to each of the bot's live
agents. `DKB/DKB Output.md` and `KKB/KKB Output.md` are the reference implementations. Two
valid layouts:

- **Phase style (DKB):** organized by call **phase** (Phase 1 Freshness → Phase 2 Details → Phase 3
  New Job → Phase 4 Insights → Summary), each phase listing its fields with allowed values.
- **Numbered-list style (KKB, KKB-Slim, Maya, TRRAIN):** a numbered list of fields, each with
  name, description and allowed values, followed by a full **EXAMPLE OUTPUT** JSON and a
  **Rules** block.

Either layout is fine; match the one the agent already uses.

## Field types

- **Enum field**: fixed value set, e.g. `job_status`: Active / Closed / Unverified / N/A;
  `call_answered`: Yes / No. List every allowed value with a one-line meaning.
- **Free-text value field**: captured as the speaker stated it; blank/`"NA"` if not mentioned.
- **Count field**: integer (e.g. `applications_count`, `fields_updated`); `0` if none.
- **Array-of-objects field**: e.g. `jobs_recommended`/`jobs_applied`; each object a complete
  record (do not flatten to strings). Failure arrays add a `failure_reason`.
- **`final_summary`**: 2–3 sentences, plain English, factual, no opinions/speculation.

## Extraction rules (always include)

- Never infer or assume: extract only what was explicitly stated by the user.
- If unclear or the call dropped before a field could be confirmed, leave blank / use the
  agent's "unverified" sentinel.
- Use the **user's** words, not the bot's, to fill fields.
- Sentinels: `"NA"` for absent strings, `[]` for empty arrays, `0` for empty counts (don't mix them up).
- Mutually-exclusive arrays stay mutually exclusive (a job is applied OR failed, never both).
- Never hallucinate names, salaries, or contact details: only what's in the transcript/recommendations.
- `final_summary` is always English regardless of call language.
- Some fields must always be filled (e.g. DKB `job_status`): state which.
- Tool-outcome fields (`jobs_applied`, `applications_count`) follow the tool results in the
  transcript, never what the bot claimed aloud.

## Per-bot notes

Read the file for its exact fields; these notes say what is distinctive.

- **DKB:** phase-based; `job_status` always filled. Phase 4 (talent insights) belongs to the legacy
  agents; the Signals agents have no insights tool.
- **KKB:** numbered list + EXAMPLE OUTPUT; job arrays carry `{job_id, role, company_name,
  company_location, salary_offered, qualification_required}` (+ `failure_reason` on failures);
  `unbacked_apply_claim` flags a bot that said "applied" with no successful `apply_job`;
  `drop_reason` is seeker behaviour only, not technical failures.
- **KKB-Slim:** its own file (diverged from KKB's on 2026-09-23): KKB's core plus location
  (`preferred_location`, `pin_code`, `nearest_landmark`, `home_area`), services
  (`services_pitched`, `service_interest`, `service_offered`) and job-fetch fields.
- **Maya:** KKB's core for students plus `college_confirmed`, `experience_captured`,
  `hr_contact_shared`, `benefits_mentioned`, `consent_status`, `service_provider_pitched` /
  `service_provider_interest`. The MPL fields were removed on 2026-10-12.
- **TRRAIN:** offer-call fields: `audio_check_confirmed`, `right_person`,
  `remembered_application`, `trrain_pitched`, `trrain_interest` (+ `callback_slot`,
  `interest_evidence`), `offer_repeated`, `partner_named`, `promised_outcome`, `do_not_call`.
  The last four are compliance checks on the bot itself.

## Common edits

- **Add a captured variable:** add the field (name + values/description) and, in the numbered
  layout, add it to the EXAMPLE OUTPUT JSON and the Rules block. Insert with a letter suffix
  (`12a`) instead of renumbering.
- **Change an enum's values:** update the allowed-value list for that field.
- **Tighten extraction behavior:** edit the Rules block.
- **Example values:** keep them plainly illustrative; a value in EXAMPLE OUTPUT is copied into real
  reports when the call has no evidence (analyser D50).
