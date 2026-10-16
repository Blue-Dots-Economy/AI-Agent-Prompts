# DKB → Signals: provider-side discovery (Phase 2)

DKB is the EMPLOYER/provider bot (posts + verifies jobs). On Signals it uses the provider domain.
Curl-verified against dev host `https://signals.bluedotseconomy.org` (2026-07-31). Owner: Srivatsa.

## create_job → POST /api/v1/admin/participant  (domain=provider, item_type=job_posting_1.0)
Same endpoint as the seeker create, different domain/item_type. To mint a job item, send a non-empty
`item_state` with the ALLOWED fields (an empty item_state creates the participant but NO item).

Body shape (compliance array + top-level name/phone like the seeker create):
```jsonc
{
  "domain": "provider", "channel": "voice", "network": "blue_dot", "item_type": "job_posting_1.0",
  "compliance": [ {"key":"user_terms","value":true}, {"key":"user_privacy","value":true}, {"key":"profile_creation","value":true} ],
  "name": "<employer/company name>",           // company name lives HERE (top-level), NOT in item_state
  "phone_number": "+91<employer phone>",
  "item_state": {
    "title": "<job title>", "role": "<role>", "natureOfJob": "Full-time",
    "positions": "<n>", "jobProviderLocation": "<location>",
    "lastRoleHeld": "...", "hiringManagerName": "...", "hiringManagerEmail": "..."
  }
}
```

### ALLOWED item_state fields (curl-confirmed 200 + item created)
`title`, `role`, `natureOfJob`, `positions`, `jobProviderLocation`, `lastRoleHeld`, `hiringManagerName`, `hiringManagerEmail`.

### REJECTED (400 INVALID_ITEM_STATE — "must NOT have additional properties")
`companyName`/`orgName` (use top-level `name`), `location` (use `jobProviderLocation`), `jobTitle`/`nameOfJobRole`/`nameOfJobRolesInterestedIn` (use `title`/`role`), `salaryMin`/`salaryMax`/`stipendMin`/`stipendMax`/`taskRateMin`/`taskRateMax`, `workExperienceYears`, `minQualificationSchool`/`minEducationalInstitute`/`candidateExperienceType`, `qualification`/`salary`/`experience`/`skills`/`jobDescription`/`benefits`/`languageRequired`.

**STRUCTURAL CHANGE (flag for DKB migration):** SALARY, STIPEND, TASK-RATE, QUALIFICATION, EXPERIENCE-years,
EDUCATIONAL-institute have **no Signals job_posting slot** — DKB currently captures these; on Signals they
are dropped from the stored item (like the seeker's dropped salary). DKB flow must stop persisting them (may
still collect for conversation) OR Srivatsa extends the schema. There may be more allowed fields (e.g. a
description under another name) — confirm the full job_posting_1.0 schema with Srivatsa before production.

## update_job → same endpoint with an `item_id` (updates the item). verify/get_talent_insights → NOT YET mapped (probe next).
## Open: seeded test job item `7dd04186-e832-48c4-830e-d9bfefd53e82` (title=Data Entry Operator) under test employer user_id 3bb0ecb5.
