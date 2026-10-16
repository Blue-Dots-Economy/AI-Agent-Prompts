# Agent Schemas

Per-bot input variables, tools, persona and audience. `/port-feature` uses it to **re-domain** a
feature (variable and tool names are remapped to the target's schema, never copied from the
source); `/update-prompt` uses it when scaffolding a new prompt.

**The prompt files are the source of truth; this file is a summary.** Last checked against every
conversation prompt in the root `CLAUDE.md` path map on 2026-10-14. Before relying on an entry,
re-check the files you will touch:

```bash
f="<Bot>/<file>.md"
grep -o '\${[a-zA-Z_]*}' "$f" | sort -u                      # input variables
grep -n '^#\+ .*\(Tool\|get_\|create_\|update_\|apply_\|record_\)' "$f"   # tool sections
```

A tool name that appears in a prompt only inside "never call X" is not a tool of that bot.
Bots not listed here (Purple Dots, any new project): read their Input Variables and tool sections,
then add an entry when the bot is registered (`/register-bot`).

---

## KKB: seeker job-matching (Blue Dots)

- **Persona:** *काम की बात / ಕೆಲಸದ ಮಾತು*, a city-administration job line.
- **Audience:** job seekers (ITI graduates, daily-wage workers, women returning to work, displaced
  workers, persons with disability, proxy callers).
- **Variants:** Hindi + Kannada; outbound and inbound; legacy and Signals backend (8 prompts).
- **Input variables:** `${contact_phone}`, `${country_code}` (tool calls only, never spoken),
  `${recommendations}` (JSON pool of jobs, each `job_id, role, company, qualification, salary,
  vacancy, location`), `${contact_memory}`. Outbound only: `${contact_name}`, `${location}`
  (the caller's location on record, read back for confirmation). There is no `${new_seeker}`
  any more: the profile fetch decides new vs returning.
- **Tools:** `get_profile`, `create_profile`, `apply_job`, `update_profile`; Signals variants add
  `record_consent`. Never `get_jobs` (the jobs arrive in `${recommendations}`).

## KKB-Slim: compressed KKB Signals (Blue Dots, A/B)

- **Persona and audience:** as KKB. Hindi + Kannada, Signals, outbound agents; one prompt covers
  both directions (there is no `${call_direction}`).
- **Input variables:** `${contact_name}`, `${contact_phone}`, `${country_code}`, `${location}`,
  `${contact_memory}`. No `${recommendations}`: it fetches jobs itself.
- **Tools:** `get_profile`, `create_profile`, `update_profile`, `apply_job`,
  `get_recommended_jobs(profile_id)`, `get_jobs`, `get_services`, `record_consent_new`,
  `record_consent`.
- Own output prompt (`KKB-Slim/KKB Slim Output.md`); shares KKB's memory prompt. Not a mirror of
  the KKB Signals prompts.

## DKB: MSME employer job verification and capture (Blue Dots)

- **Persona:** *धंधे की बात (Dhandhe Ki Baat)*, calling employers about their job postings.
- **Audience:** MSME business owners / employers.
- **Variants:** Hindi + Kannada; legacy outbound and inbound; Signals outbound (6 prompts).
- **Input variables** (the employer's existing posting; "Not Available" = missing):
  `${company_name}`, `${job_role}`, `${num_vacancies}`, `${job_id}` (never spoken), `${city}`,
  `${salary}`, `${location}`, `${qualification}`, `${work_experience}`,
  `${work_experience_years}`, `${contact_memory}`. Phone: `${phoneNumber}` on outbound,
  `${contact_phone}` + `${country_code}` on inbound. Legacy outbound also has `${contact_name}`.
- **Tools, legacy:** `get_talent_insights`, `update_job_status`, `update_job_details`,
  `create_job`. Fixed params, never changed: `sourceService: "ONESTAGENT"`, `eventType`
  (`"UPDATE_JOB"` on updates, `"JOB"` on create), `app_instance: "up-postjob"` (create_job).
- **Tools, Signals:** `create_job` and `update_job` only (same participant endpoint, `update_job`
  adds `item_id`), employer phone as `"phone_number": "+91${phoneNumber}"`. No talent-insights tool
  and no status tool. The ONEST fixed params must NOT be sent (the API rejects them). `item_state`
  stores only `title, role, natureOfJob, positions, jobProviderLocation, lastRoleHeld,
  hiringManagerName, hiringManagerEmail`; salary and qualification are collected but not stored.

## Maya: campus recruitment, a KKB spinoff (Blue Dots)

- **Persona:** *माया, [college_name] की ओर से*, campus recruitment for graduates in UP. NOT
  government. Feminine voice.
- **Audience:** college students and recent graduates (fresher-heavy).
- **Variants:** Hindi only; outbound and inbound; legacy and Signals (4 prompts).
- **Input variables:** `${college_name}` (spoken once in the intro; if empty, introduce as माया
  with no institution), `${contact_phone}`, `${country_code}`, `${recommendations}` (a loosely
  ordered pool of up to ~30 jobs to rank: KKB's fields plus optional `hr_contact`, shared only after
  a successful apply, and `benefits`, surfaced in the deep dive only), `${contact_memory}`.
  Outbound only: `${contact_name}`, `${location}`.
- **Tools:** as KKB (`get_profile`, `create_profile`, `apply_job`, `update_profile`; Signals adds
  `record_consent`).
- **Divergences to preserve:** root `CLAUDE.md` → "Maya rule" (college identity, `${college_name}`,
  `hr_contact`/`benefits`, Experience Capture, HR-number sharing, feminine voice). The MPL offer was
  removed on 2026-10-12.

## TRRAIN: follow-up support-service offer (Blue Dots)

- **Persona:** the काम की बात line calling back seekers who already applied; one offer per call,
  under two minutes. Names the partner as "ट्रेन ट्रस्ट" / "ಟ್ರೇನ್ ಟ್ರಸ್ಟ್" (the only partner that may be named).
- **Audience:** seekers who applied to a job. **Variants:** Hindi + Kannada, outbound only.
- **Input variables:** `${contact_name}`, `${contact_phone}`, `${country_code}`,
  `${contact_memory}`, `${applied_job_role}`, `${applied_job_company}` (company only if the seeker
  asks which job).
- **Tools:** `get_profile` only. It cannot fetch jobs, apply, create or update anything.
- Own memory and output prompts, each deployed per agent.

---

## Re-domaining cheatsheet

| Concept | KKB / KKB-Slim | DKB | Maya | TRRAIN |
|---|---|---|---|---|
| Person on the call | seeker | business owner / employer | student / graduate | seeker who applied |
| Phone variable | `${contact_phone}` | `${phoneNumber}` (out), `${contact_phone}` (in) | `${contact_phone}` | `${contact_phone}` |
| Job data source | `${recommendations}` (Slim: `get_recommended_jobs` / `get_jobs`) | `${job_role}` etc. (their own posting) | `${recommendations}` (+ `hr_contact` / `benefits`) | `${applied_job_role}` / `${applied_job_company}` |
| Job id | `recommendations[].job_id` (Slim: from the fetch result) | `${job_id}` | `recommendations[].job_id` | none |
| Primary action | `apply_job` | legacy `update_job_*` / `create_job`; Signals `update_job` / `create_job` | `apply_job` | capture interest (no write tool) |
| Consent tool | Signals: `record_consent` (Slim also `record_consent_new`) | none | Signals: `record_consent` | none |
| Insight / services tool | Slim: `get_services` | legacy: `get_talent_insights` | none | none |

**Rules when porting:**
- A variable, tool or payload field with no equivalent in the target is a **hard gap**: flag it to
  the user; never invent one. A feature that needs a write tool cannot be ported to TRRAIN as is.
- Legacy and Signals variants of the same bot have different tools; check which one you target.
- Adapt the persona and voice to the target audience (a seeker reassurance becomes an employer one
  for DKB; feminine forms for Maya).
- Place the ported content per `../../update-prompt/reference/prompt-anatomy.md`.
