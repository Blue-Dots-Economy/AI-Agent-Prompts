# Signals DPG Migration Guide

**How to migrate a Raya voice bot from the ONEST/dhiway backend to the EkStep
Signals DPGs, and make it stable.**

This is the playbook distilled from migrating the **KKB Kannada Signals clone**
(`33037201-78ce-405d-b509-a3b6934e20f1`) end to end. Every fact here is grounded
in real API calls and live Raya transcripts — not assumptions. Use it to port the
remaining bots (KKB Hi/Kn, DKB Hi/Kn, Maya) onto Signals.

> **Scope.** This covers (A) the three Signals API endpoints and their gotchas,
> (B) the Raya tool-config swap, (C) the prompt restructure that made the bot
> stable, and (D) a step-by-step migration checklist. Prompt *content* edits still
> go through `/update-prompt`; this guide is the integration + stabilisation layer.

---

## 0. TL;DR — what changed and why it matters

Migrating to Signals is **two** jobs, and the second is the hard one:

1. **Swap the 3 tools** (`get_profile`, `create_profile`, `apply_job`) from ONEST
   endpoints to Signals endpoints. Mechanical — see §B.
2. **Restructure the conversation flow** so it is reliable on the Signals data
   model. Signals introduces a **draft vs live** profile lifecycle and a
   **mandatory consent** step that the old ONEST flow never had. The bot must
   fetch first, branch on the *result* (not on an input hint), reuse what the
   profile already has, and take consent before it can apply. Getting this wrong
   produced every bug we hit: fetch not firing, name spoken from memory, apply
   with an empty id, age/gender re-asked, consent skipped. See §C.

**The single biggest lesson:** *replace forking with a get_profile-driven flow.*
A `new_seeker` yes/no fork is fragile and mis-routes. Always fetch silently, then
branch on what comes back. This one change removed a whole class of bugs.

---

## A. The Signals API

**Base URL (dev):** `https://signals.bluedotseconomy.org`
**Auth headers (every request):**

```
x-api-key:        <SIGNALS_API_KEY>          # secret — never commit; lives in the Raya tool header / git-ignored env
x-acting-org-id:  org_cdce36e6-6a38-4c2c-b264-c581dc8c62e2
Content-Type:     application/json           # on POST
```

Owner: **Srivatsa (Sankethika)** — escalate API/schema questions to him.

The data model: a **participant** (`user_id`) owns up to **5 profile items**
(`item_id`). A seeker profile is `item_type: "profile_1.0"`; a job posting is
`item_type: "job_posting_1.0"`. A profile has a **`lifecycle_status`**: `"draft"`
(incomplete — cannot be applied with) or `"live"` (consented + complete — ready).

### A.1 `get_profile` — fetch (GET)

```
GET /api/v1/admin/participant?phone_number=91XXXXXXXXXX
```

- `phone_number` is **10 digits prefixed with `91`, no `+`** (a leading `+` is also
  accepted, but standardise on `91` + digits).
- **Response** (profile found):
  ```jsonc
  {
    "user_id": "8e99c637-...",                         // the participant (owner) id
    "user_consent": { "terms_accepted": false, "privacy_accepted": false, "has_age": false },
    "items": [
      {
        "item_id": "2d1510d6-...",                     // the PROFILE id
        "lifecycle_status": "draft",                   // "draft" | "live"  ← decides readiness
        "profile_consent_accepted": false,
        "item_state": {
          "age": "25", "name": "…", "phone": "9199…", "gender": "Male",
          "location": "Bengaluru, Karnataka", "languageSpoken": ["Kannada"],
          "workExperience": "Worked before",
          "natureOfJobsInterestedIn": "Full-time",
          "nameOfJobRolesInterestedIn": "Data Entry Operator"
        }
      }
    ]
  }
  ```
- **Empty** (new caller): `items: []` (and/or `user_id: null`).
- **`items` can hold MULTIPLE profiles** (up to 5 per user) in no guaranteed order — a
  stale `draft` and a `live` one can both be present, draft possibly first. **Do NOT read
  `items[0]` blindly.** Select by lifecycle (see §C.4).
- **What the prompt reads:** `profile_id =` the **live item's** `item_id` (the first item
  with `lifecycle_status: "live"`, not necessarily `items[0]`); `acting_as_user_id =`
  top-level `user_id`; readiness `=` "does any item have `lifecycle_status: "live"`?";
  known fields from the selected item's `item_state.*`. **Warning:** participant-level
  `user_consent` can be all-`true` while a specific item is still `draft` — readiness is
  the ITEM's `lifecycle_status`, never `user_consent`.

### A.2 `create_profile` — save / go live (POST)

```
POST /api/v1/admin/participant
```

Creates a NEW profile if no `item_id` is supplied; the same endpoint updates when an
`item_id` is included. **To create a LIVE profile you MUST send two things** (this was
the `PROFILE_NOT_LIVE` root cause):

1. A top-level **`age`** (string or int), and
2. A **`compliance`** array with all three consents `true`.

The old ONEST-style `terms_accepted` / `privacy_accepted` booleans are **deprecated
and ignored** — they do not make a profile live. Live payload template (as deployed):

```jsonc
{
  "age": "{{age}}", "name": "{{name}}",
  "domain": "seeker", "channel": "voice", "network": "blue_dot",
  "item_type": "profile_1.0",
  "compliance": [
    { "key": "user_terms",       "value": true },
    { "key": "user_privacy",     "value": true },
    { "key": "profile_creation", "value": true }
  ],
  "item_state": {
    "age": "{{age}}", "name": "{{name}}", "phone": "91{{phone}}", "gender": "{{gender}}",
    "location": "{{location}}", "languageSpoken": ["Kannada"],
    "workExperience": "{{workExperience}}",
    "natureOfJobsInterestedIn": "Full-time",
    "nameOfJobRolesInterestedIn": "{{role}}"
  },
  "phone_number": "+91{{phone}}"
}
```

- **LLM-supplied params:** `age`, `name`, `phone` (10-digit), `gender`, `role`,
  `location`, `workExperience`. Everything else is fixed in the template.
- **Response:** the saved item; `lifecycle_status` should now be `"live"`.
- **Localise `languageSpoken`** per bot: `["Kannada"]` for KKB-Kn, `["Hindi"]` for
  Hi bots, etc.

### A.2b Consent on an EXISTING profile — `record_consent` (verified 2026-09-09)

The same endpoint updates when an `item_id` is supplied, and an update **may carry the `compliance`
array** — that is how consent is recorded for a caller who already has a profile:

```jsonc
POST /api/v1/admin/participant
{
  "item_id": "<live seeker item_id>", "item_type": "profile_1.0",
  "domain": "seeker", "channel": "voice", "network": "blue_dot",
  "age": <known>, "name": "<known>", "phone_number": "+91XXXXXXXXXX",
  "compliance": [
    { "key": "user_terms",       "value": true },
    { "key": "user_privacy",     "value": true },
    { "key": "profile_creation", "value": true }
  ],
  "item_state": { "age": <known>, "name": "<known>", "phone": "91XXXXXXXXXX" }
}
```

Curl-grounded facts:

| probe | result |
|---|---|
| update POST with `compliance` all-true | **200**; the `item_state` merge keeps every other field |
| update POST with `compliance` `false` | **400 `CONSENT_DECLINED`** — *"consent cannot be declined — omit a key to skip it"* |
| `create_profile` on a participant with 5 seeker profiles | **409 `PROFILE_LIMIT_REACHED`** — *"maximum of 5 seeker profile(s) allowed"* |

Two consequences worth planning around:

- **Consent is write-once-true.** It can never be un-set through the API, so a false-flag fixture
  **cannot be manufactured** — and since a compliance-less item is necessarily `draft`, the state
  "live profile + a false consent flag" cannot be constructed from our side at all. Testing the
  false branch of a consent gate needs a record provisioned by the data team.
- **This must NOT go into `update_profile`.** Its payload template is fixed, so a `compliance` array
  inside it would assert consent on every gender/location/role write, asked or not. It belongs in a
  separate tool called only after the caller says yes — `raya/toolspecs/record_consent.json`, added
  with `scripts/raya_tooladd.py`.

**What `get_profile` actually returns** (probed live, same date): `{ user_id, user_consent, items }`,
with `user_consent = { terms_accepted, privacy_accepted, has_age }` at the participant level and a
`profile_consent_accepted` boolean on each item. Apply consent has no stored flag at all — it rides
in `apply_job`'s payload as `consent: { version: 1, acknowledged: true }`, per action.

### A.3 `apply_job` — submit application (POST)

```
POST /api/v1/action/perform
```

Payload template (as deployed — note: **no `requirements_snapshot`**, see A.4):

```jsonc
{
  "action_type": "apply",
  "consent": { "acknowledged": true, "version": 1 },
  "source_item": { "item_id": "{{profile_id}}", "item_type": "profile_1.0",
                   "item_domain": "seeker",   "item_network": "blue_dot" },
  "target_item": { "item_id": "{{job_id}}",    "item_type": "job_posting_1.0",
                   "item_domain": "provider",  "item_network": "blue_dot",
                   "item_instance_url": "https://signals.bluedotseconomy.org" },
  "acting_as_user_id": "{{acting_as_user_id}}"
}
```

- **LLM-supplied params:** `job_id` (the job's `job_posting_1.0` item_id, full
  hyphenated UUID — never strip hyphens → else 404), `profile_id` (the seeker
  `item_id` from get_profile/create_profile), `acting_as_user_id` (the top-level
  `user_id`, the profile OWNER — **distinct from `profile_id`**).
- **Success:** HTTP **201**, body `{ results:[{action_id,…}], summary:{succeeded,failed} }`.
- The source profile MUST be **live** — applying with a `draft` profile fails
  (`PROFILE_NOT_LIVE`). This is why the flow must create-with-consent before apply.

### A.4 The `requirements_snapshot` trap (READ THIS)

The `action/perform` schema historically **required** a `requirements_snapshot`
field that had to be **exactly `{}`** (an empty object). Verified by direct curl:

| `requirements_snapshot` sent | Result |
|---|---|
| omitted / `null` | **400** `"expected record, received undefined/null"` |
| `{}` (empty) | **201** ✓ — the only success |
| `{"anything": …}` (any key) | **422** `"must NOT have additional properties"` |

The problem: **Raya's `payload_template` renderer drops empty-object literals `{}`**
at send time, so `"requirements_snapshot": {}` arrived as `undefined` → 400. And a
non-empty object is rejected by the API. A whole-value placeholder
(`"{{requirements_snapshot}}"` + the model passing `{}`) **also failed** — Raya
still dropped it. So the field is unsendable from Raya.

**Resolution:** the API team is making `requirements_snapshot` **optional** (default
`{}` when absent). Once that lands, **omit the field entirely** — which is the current
deployed state (it was removed from the `apply_job` payload + params). Until the
backend change ships, apply will 400; that is a **backend dependency, not a prompt
bug** — do not try to fix it in prose.

> **General lesson:** if a Signals field must be an empty object and Raya 400s with
> "expected record, received undefined", it's Raya pruning `{}`. Prove the API's real
> constraint with curl, then either omit (if the API allows) or get a server-side
> default — never pad with a dummy key (the API rejects extra properties).

---

## B. The Raya tool-config swap

Tool HTTP configs live on the agent object at `tools.llm_tools[]`. Each tool =
`{ type, function:{name, parameters, description}, api_details:{url, header, method, payload_template?} }`.
The **PATCH API round-trips `tools` byte-identically and does NOT wipe `instructions`** —
so you can swap tools programmatically.

**How to swap (per tool):**
1. `GET /api/agent/{id}` → grab `tools`.
2. **Snapshot** it first (git-ignored — it contains the live API key in headers).
3. Replace `api_details.url`, `api_details.header` (add `x-api-key` + `x-acting-org-id`),
   `api_details.method`, and `api_details.payload_template` with the Signals shapes (§A).
4. Set `function.parameters` to the minimal LLM-supplied set (see §A per tool).
5. `PATCH /api/agent/{id}` with `{"tools": {...}}`. Read back and verify.

Reference script pattern (used this session): `GET` → mutate the one tool → `PATCH {"tools": …}` → `GET` and assert.

**`payload_template` behaviour — confirmed:**
- Interpolates `{{param}}` from the model's function args.
- **Keeps** non-empty nested objects, literal arrays (`["Kannada"]`), booleans
  (`true`), strings, and `"91{{phone}}"`-style string concatenations.
- **Drops** empty-object literals `{}` (the A.4 trap).
- Scalar `{{param}}` inside a string → a string. (Whole-value object substitution is
  unreliable — treat placeholders as strings.)

**`agent_args` (the input-variable list) is NOT PATCHable** — the API rejects it
("unrecognized key"). It is **auto-derived from the `${...}` variables in the prompt
`instructions`** on deploy. So to remove an input variable (e.g. `new_seeker`),
delete every `${new_seeker}` reference from the prompt and redeploy — `agent_args`
updates itself. (Confirmed: removing `${new_seeker}` from the prompt dropped it from
`agent_args` on the next deploy.)

**`hold_message` is a platform-injected universal parameter** — Raya adds it to
*every* tool call and **speaks it** as a latency filler. It is NOT in your tool
schema and NOT in your prompt, so a bug where a "silent" fetch talks will not show up
in a prompt grep. Control it from the prompt (see §C.6).

**Deploy prompts** with `scripts/raya_deploy.py deploy <target> --yes` (snapshot →
GET → name-guard → PATCH instructions → read-back verify). Reconcile before editing;
never deploy a prompt behind live. Record the agent uuid in `raya/agents.json`.

---

## C. The prompt restructure (what makes it stable)

These are the fixes that took the clone from "every call broke somewhere" to a clean
flow. Each is a reusable pattern — apply all of them to every bot you migrate.

### C.1 Get_profile-driven flow — DELETE the fork

**Symptom it fixes:** the `new_seeker=yes/no` fork mis-routed — fired `get_profile`
on a new seeker, or skipped it on a returning one. Forking is inherently fragile.

**Pattern:** there is **no branch variable**. After the greeting, the FIRST action is
**always** a silent `get_profile`. Then branch on the **result**:
- `items` non-empty → returning caller (use it).
- `items` empty → new caller (gather basics).

Remove `${new_seeker}` entirely (prompt refs + it auto-drops from `agent_args`).

### C.2 `${contact_memory}` is NOT a fetch

**Symptom it fixes:** the bot greeted the caller by name and stated their role from
the injected memory block, and **never called `get_profile`** — then applied with a
memory-sourced id and skipped consent.

**Pattern:** hard rule — the caller's name, role, ids, and readiness may be spoken
**only after the `get_profile` tool has actually returned in THIS call**. Memory is
background context for warmth in later turns; it never substitutes for the fetch and
never drives the opening. Reinforce at the fetch mandate: *"reading `${contact_memory}`
is NOT a fetch."*

### C.3 Smooth opener → then fetch

**Pattern:** one fixed neutral opener on every call — greeting + a single "are you
looking for a job?" question. No name, no saved role, no resume line in the opening
turn. After the caller answers, silently fetch, then greet by name if found. This
also stops the "unnatural start" where the bot blurts a name/stall before any
conversation.

### C.4 Lifecycle readiness gate — select the LIVE item, not `items[0]`

**Symptom it fixes:** a returning caller with more than one profile — `get_profile`
returned `[{draft}, {live}]` — and the bot applied to `items[0]` (the draft) →
`422 PROFILE_NOT_LIVE`, even though a live profile was right there at `items[1]`.

**Pattern:** don't branch on `items[0]`; **scan all `items` and select by lifecycle:**
- **READY** → **any** item has `lifecycle_status: "live"` → use that live item's
  `item_id` as `profile_id` + top-level `user_id` as `acting_as_user_id` → `apply_job`
  **alone**. No create, no consent, no age/gender re-ask. **Ignore any stale `draft` in
  the same response — never apply to a draft while a live item exists.**
- **NOT READY** → **no** item is live (all `draft`, or `items` empty) → collect only
  genuinely-missing fields → consent → `create_profile` (mints a live profile) →
  **then, as a separate step**, `apply_job` on the new item.

Point every downstream rule (HARD GUARD, apply preconditions, age/gender reuse) at the
*selected* item, not `items[0]`. (`items[0]` stays correct for the `create_profile`
*response*, which returns a single new item.) Note: `create_profile` without an
`item_id` mints a NEW profile each time rather than flipping an existing draft, so users
accumulate items — which is exactly why selecting the live one matters.

### C.5 Consent gate — HARD BLOCK, and "draft ≠ consented"

**Symptom it fixes:** on a draft profile the bot fired `create_profile` with no
consent ask (it assumed "a profile was found" meant consent existed).

**Pattern:** `create_profile` must NOT fire until the consent question has been asked
and answered **yes** in this call. **A found `draft` profile has NOT consented — that
is *why* it's draft** (`user_consent` is false). So consent is asked on BOTH the
new-caller and draft paths. On decline → do not create/apply → graceful hang-up +
record `consent_status = Declined` (add this output variable). One spoken consent
line, plain language, once per call. This satisfies Srivatsa's rule that every create
records consent + age.

### C.6 Silence the fetch/create — `hold_message` + no acknowledgement

**Symptom it fixes:** the "silent" fetch talked — "ಒಂದು ನಿಮಿಷ, ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು
ನೋಡುತ್ತಿದ್ದೇನೆ" then "ನಿಮ್ಮ ಮಾಹಿತಿ ಸಿಕ್ತು" ("profile fetched"). Two sources:
1. The platform **`hold_message`** filler on the tool call (model wrote a
   fetch-revealing sentence into it).
2. A prompt line instructing an "I got your info" acknowledgement.

**Pattern:**
- Set `hold_message` for `get_profile`/`create_profile` to a **neutral hold** that
  reveals nothing — e.g. "ಒಂದು ನಿಮಿಷ" / "one moment" (owner preference; empty is also
  fine). NEVER a "looking up your profile / creating your profile" line. Only
  `apply_job` carries a real spoken bridge line.
- Remove any "profile fetched / I got your info" acknowledgement. The returning-caller
  turn greets by name and goes straight to the role check — the caller must never hear
  that a lookup happened, in either branch.
- **Scope caveat:** if you ban a filler phrase (e.g. "no stall in the opening"), scope
  that ban to the spoken opening turn so it doesn't also forbid the `hold_message`
  value on the later tool call.

### C.7 Reuse what the profile already has — don't re-ask

**Symptom it fixes:** a draft profile already had `age` AND `gender` (and name,
location, experience), yet the bot re-asked age + gender because the create path was
framed as "new caller → collect everything."

**Pattern:** before asking anything, re-read `items[0].item_state`. **Every field
present there is KNOWN and reused verbatim by `create_profile`** — never re-ask it.
A draft with age + gender filled needs NEITHER re-asked → go straight to consent. Lock
known fields for the whole call (don't reset between multiple applies). Ask only
genuinely-missing fields, one at a time.

### C.8 Ranking — relevance filter, never pad

**Symptom it fixes:** a confirmed data-entry seeker was shown an EV-charging-technician
job *first*, with a customer-support role as filler, because the rule always tried to
show three.

**Pattern:** when the caller's role is known, build the batch from **only**
role-relevant jobs (same role + same-family variants), best-fit first. **Never pad to
N with unrelated roles** — 1 relevant job → show 1. Offer the rest only if the caller
asks for something else/more. If nothing matches, name what IS available or trigger
No-Match — don't invent.

### C.9 Never batch create → apply

**Pattern:** `create_profile` and `apply_job` must be **separate turns crossing a
tool-result boundary**. Emitting both in one batch means `apply_job` is built before
`create_profile` returns the new `profile_id` → apply sends an empty `profile_id`.
Create first → WAIT for the result → read its `item_id` → then apply. Never
`apply_job` with an empty `profile_id`; never call `get_profile` to obtain an id at
apply time.

---

## D. Migration checklist (per bot)

Run this order for each bot you move onto Signals:

1. **Register + reconcile.** Add the agent to `raya/agents.json`. `pull` its live
   prompt into the repo, commit. Never edit behind live.
2. **Snapshot** the agent's current `tools` JSON (git-ignored — has the API key).
3. **Swap the 3 tools** (§B) to the Signals endpoints/payloads (§A). Localise
   `languageSpoken` and any spoken defaults. PATCH `{"tools": …}`, read back.
4. **Ground the writes with curl** before trusting them: create-with-consent → assert
   `lifecycle: live` → apply → assert 201. Use a throwaway phone. (This is how every
   payload in §A was verified.)
5. **Restructure the prompt** (§C) via `/update-prompt`:
   - delete the fork / `${new_seeker}` (C.1);
   - memory-is-not-a-fetch guard (C.2);
   - smooth opener → fetch (C.3);
   - lifecycle readiness gate (C.4);
   - consent HARD BLOCK + draft≠consented (C.5);
   - silence fetch/create via `hold_message` + drop the acknowledgement (C.6);
   - reuse `item_state` fields (C.7);
   - ranking relevance filter (C.8);
   - never batch create→apply (C.9);
   - add the `consent_status` output variable.
6. **Deploy** the prompt (`raya_deploy.py deploy … --yes`). Confirm `agent_args` no
   longer lists `new_seeker` (auto-derived).
7. **Live test call** → pull the transcript (`scripts/raya_call.py <uuid> 1`, read the
   `tool_calls`, not just `content`). Verify: neutral opener → silent `get_profile`
   fires → correct branch → (new/draft) reuse-known-fields + consent + create →
   `apply_job` 201.
8. **Changelog + analyser.** Append to `<Agent>/CHANGELOG.md`; if a bug surfaced, add
   the pattern to `/prompt-analyser`. Commit + push.

### Verification is transcript-first
No fix without a real transcript. Read `tool_calls[].function.arguments` — many bugs
(empty `profile_id`, stripped `job_id` hyphens, `hold_message` narration, a fetch that
never fired) are invisible in the spoken `content` and only show in the tool args.

---

## E. Known open items / dependencies

- **`requirements_snapshot`** — removed from `apply_job`; apply will 400 until the API
  team (Srivatsa) ships the "optional / default `{}`" change. Backend dependency.
- **`job_id` inventory** — `apply_job.target_item.item_id` must be a real Signals
  `job_posting_1.0` item_id supplied via `${recommendations}`. If a bot's feed still
  carries ONEST ids, repoint the feed (data dependency, outside the prompt).
- **Profiles per user** — Signals allows up to 5 profiles per participant; avoid
  duplicate `create_profile` in one call (reuse the minted id for later applies).

---

*Source of truth: the KKB Kannada Signals clone (`33037201-…`) and its
`KKB/CHANGELOG.md` (2026-07-29 entries) + `/prompt-analyser` patterns D29–D36.
Every API behaviour here was curl-verified against the dev host and confirmed on live
Raya transcripts.*
