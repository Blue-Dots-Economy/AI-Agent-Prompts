# Two data-side blockers found in production traffic — 2026-09-04

Neither is a prompt bug. Both are currently experienced by real callers as the bot saying something
useless or wrong, and neither can be fixed in the prompt.

---

## 1. `age: 18` looks like a default, and the Signals API blocks applies for minors

**What happens.** `apply_job` returns `422 MINOR_ACTION_CHANNEL_BLOCKED` — *"This participant is a
minor; actions for minors must be completed in the app and can't be performed via this channel."*
The caller is then told "technical issue", and because the bot cannot read the error reason (see
`ESCALATION-litwiz.md` §2) it goes on to offer more jobs, every one of which fails identically. On
`a5547492` the caller sat through two full apply attempts, both blocked, both reported as a technical
fault.

**Why it looks like a data default, not real ages.** 13 occurrences across 2026-09-01→04, all on
profiles whose stored `age` is exactly **18**. Three unrelated inbound callers the same day —
`b48f70fb`, `2d8b7cb1`, `a5547492` — all carry `age: 18`. On `af52d37c` the stored age was 18 and the
caller said on the call that she is 28. A real 18-year-old is also not a minor, so either the stored
value is a placeholder or the backend's minor test is not reading age at all (there is no
`dateOfBirth` on these profiles).

**The ask.** Confirm what populates `age` on profile creation, and whether the minor check reads
`age` or a DOB we are not sending. If 18 is a default fill, every caller carrying it is permanently
unable to apply by phone and we are telling them it is a glitch.

---

## 2. The campaign is sending full postal addresses in `location`

**What happens.** 272 of today's outbound calls were dialled with a `location` argument holding a
complete postal address rather than a city — e.g.

    183, Maharajpur, Sahibabad Industrial Area, Ghaziabad, Uttar Pradesh - 201010 Ghaziabad
    ( Municipal Corporation ), Tehsil- Ghaziabaad, District- Ghaziabad, Uttar Pradesh, Pin Code-201010

**Two consequences.**
1. The prompt's job is to read that location back for confirmation. A 200-character address is not
   speakable, so the bot either has to reduce it to a city itself or fall back to asking openly —
   which is the very complaint that produced tracker rows 106/108. (The prompts now say to speak only
   the town/city part, which mitigates it; it does not fix the input.)
2. Every location detector we have matches the argument against the job cities, so an address that
   *contains* "Ghaziabad" scores as "no job in this location". 271 of today's `C MISMATCH NOT NAMED`
   findings are that, not bot behaviour. It hides real findings in noise.

Stored profile locations have the same shape — `b48f70fb`'s profile location is
`VILL-MURARI TAND KAKO, PO-BHADSARA,PS-PALI,DIST-JEHANABAD,PIN-804418`.

**The ask.** Send `location` as the city (or city + locality) that the matching actually uses, and
keep the full address in a separate field if it is needed downstream. If the address is all that
exists, say so and we will do the reduction on our side deliberately rather than incidentally.

---

## 3. Not a blocker, but worth knowing: stale campaign job ids

`TARGET_ITEM_NOT_FOUND` fired 20 times in the same window. Those are `job_id`s that were live when the
campaign was built and are not live now. `${recommendations}` should be built from current job ids at
send time; a caller who agrees to apply to a job that no longer exists is told the apply failed.

---

## 4. The recommendation array carries duplicate postings

`morejobs-22` — a real campaign payload captured as a fixture — holds **22 entries with only 18
distinct role+company pairs**. "Crew Member - McDonald's / MacDonalds" appears **five** times:

| job_id | location | salary |
|---|---|---|
| `b256308a` | Main, Grand Trunk Road, Nehru Nagar, 201001, Ghaziabad | 13000 - 15000 |
| `af81c643` | Raj Nagar Extension, 201003, Ghaziabad | 13000 - 15000 |
| `c9857e06` | Padmana Naidu Marg, Indirapuram, 201014, Ghaziabad | 13000 - 15000 |
| `d0864e33` | 9, PVR, Indirapuram, 201014, Ghaziabad | 13000 - 15000 |
| `699304e1` | 9, PVR, Indirapuram, 201014, Ghaziabad | 13000 - 15000 |

Four of the five are genuinely different branches, which is fine — but the **last two are identical in
company, role, location and salary** and differ only by `job_id`. The same pattern appears on
"Customer Support Executive / CY FUTURE" (two Noida entries).

The bot is instructed to walk the array in order and never skip, so on call `4982c225` the caller
heard "क्रू मेंबर - मैकडॉनल्ड्स, तेरह हज़ार से पंद्रह हज़ार" up to five times, twice with nothing to
tell the two apart. **The ask:** de-duplicate exact role+company+location+salary matches before
building `${recommendations}`. Distinct branches are worth listing separately; two rows for the same
vacancy are not.

Also note the company name is spelled **three different ways** across those five rows —
`MacDonalds`, `McDonald's` — which the bot has to speak, so it says the brand differently depending on
which row it is reading.


---

## 5. Send a cleaned `location_spoken` argument (added 2026-09-08)

**The ask:** alongside `location`, send a second argument — `location_spoken` — containing the same
place with **every digit removed and the words already in the call's script** (Devanagari for Hindi,
Kannada for Kannada). The prompt would then read it verbatim.

**Why the prompt cannot do this itself — three failures, three wordings.** The caller-place slot in
the location sentence carries two instructions that cannot both be obeyed: "this is a literal
substituted token, there is nothing to resolve" (added because six calls resolved it to the
profile's stale city) and "convert it first — drop the digits, write it in Devanagari" (added for
the PIN and Latin leaks). Reading it literally leaks the raw value; trying to convert it makes the
model reach for a place it already knows in Devanagari.

| call | `location` sent | spoken | |
|---|---|---|---|
| `a899617e` | `Muradnagar, 110045` | "मुराद नगर, ११००४५" | PIN as a quantity |
| `7b841e6b` | `Sarjapur, 110045` | "Sarjapur, 110045" | raw, Latin + PIN |
| `a5ba6894` | `10987, Sarhanpur` | "10987, Sarhanpur" | raw, after the fix |
| `1450f797` | `Sarjapur, 110045` | "गाज़ियाबाद" | **wrong place** — the jobs' city |

Reading a substituted token verbatim is the one thing this prompt does reliably. Give it a token
that is already sayable and the whole class disappears.

**What the values actually look like** (from the calls above and the 272 with postal addresses):
`Muradnagar, 110045` · `Sarjapur, 110045` · `10987, Sarhanpur` · `9, PVR, Indirapuram, 201014,
Ghaziabad`. So the cleaning is: drop every digit-only fragment, drop house/plot numbers, keep the
locality and city. That is a few lines where the argument is assembled, and it is the same
transformation we are currently asking a language model to perform on every call.

**Separately, and cheaper:** `location` values that are a bare PIN, a state name, or campaign
metadata (`"Call status: not_dialled"`) should not be sent at all — the prompt already treats them
as empty, so sending them only creates the risk of one being read aloud.

### Sharper diagnosis, added after four more calls

The substituted place is not arbitrary. Of the four substitutions now on record, **three named
साहिबाबाद and one गाज़ियाबाद — and both are entries in the prompt's Canonical Location Spellings
list**:

| call | bot | `location` sent | spoken |
|---|---|---|---|
| `1450f797` | fat | `Sarjapur, 110045` | गाज़ियाबाद |
| `8eb83bc2` | slim | `Sarjapur, 110045` | साहिबाबाद |
| `f90a0b97` | slim | `Sarjapur, 110045` | साहिबाबाद |
| `fa9a16c0` | fat | `Sarjapur, 110045` | साहिबाबाद |

So the mechanism is not simply "two competing instructions" — it is that **the canonical list acts
as an attractor.** The conversion step says *"Use Canonical Location Spellings for a place on that
list. A place NOT on the list is converted exactly the same way."* With the list sitting immediately
below, list-membership becomes the salient operation, and a value that is not on it gets mapped
**to** a member rather than converted on its own terms. The off-list clause is read as "find the
nearest listed place", which is exactly what a Ghaziabad-locality list makes easy.

That predicts the failure will keep happening for any locality outside the list, on either prompt
size, which is what the four calls show. It also gives one more prompt-only thing worth trying
before the upstream change: state that **the list is a spelling table, never a menu** — if a value is
not on it you still say that value, never a list member. That is not another wording of the same
guard; it names the attractor the guard never mentioned. It is queued as the next experiment on the
slim A/B bot rather than applied to live traffic.

### Correction, same day — the substitution half of this is not a production rate

The four "spoke a different place" calls quoted above (`1450f797`, `8eb83bc2`, `f90a0b97`,
`fa9a16c0`) and six more found later are **all harness dials on the tester DID**, whose stored
profile carries `location: "Sahibabad, Ghaziabad, India"` while the fixture sends
`"Sarjapur, 110045"`. Split by caller over 449 calls since 01-09: **real callers 3 RAW, 0
SUBSTITUTED; harness 10 SUBSTITUTED, 0 RAW.** The substitution is a genuine precedence weakness that
reproduces whenever the profile and the argument disagree — but it has not been seen on a real
caller, and it was wrong of me to quote it as a caller-facing rate.

**The ask below is unchanged and rests on the RAW calls, which ARE real callers** — `a899617e`,
`7b841e6b` and `a5ba6894`, the last of them after the fix, with `location: "10987, Sarhanpur"`
(digits first, a shape the prompt's worked examples do not cover). A `location_spoken` argument that
is already digit-free and already in the call's script removes that class entirely.


---

### Update 2026-09-09 — both prompt-side mechanisms have now been tried and both failed

This ask is no longer a nice-to-have. Two structurally different prompt fixes were built and
tested live, and each failed in its own way, for the same underlying reason: the sentence needs the
value **transformed**, and every way of getting the value into the sentence defeats one half of that.

| mechanism | live result |
|---|---|
| **bracket slot** `[जगह]` / `[ಜಾಗ]` — model resolves it from `${location}` | the model reaches for the FETCHED PROFILE instead. `2bf465d9`, `8976c120` (both sent `location: Hubli`) and `15434ef6` (`Hubballi, 580020`) all spoke "ಕೊರಮಂಗಲ", the profile's city. Three failures. |
| **literal `${location}` token embedded in the spoken sentence** — the platform substitutes it, so there is nothing for the model to choose | the model reads the substituted value VERBATIM, pin code included. `a9039634` spoke "ಸರ್ಜಾಪುರ, 110045" — right place, raw digits. |

The two are mutually exclusive. A bracket the model fills is a bracket the model can fill wrongly;
a pre-substituted token is a string the model will read as-is. The prompt currently uses the literal
token (because a wrong PLACE is worse than a spoken pin code) and states the digit-drop rule as
forcefully as prose allows — "**DELETE** every digit. Deleted, not rewritten" — and `a9039634` still
read the digits, 7 minutes after that wording went live.

Per our own escalation ladder we will not add a third wording. **What we need is one field:**

    location_spoken: "सरजापुर"          // or "ಸರ್ಜಾಪುರ" for a Kannada campaign

Already in the target script, digits and postal codes already stripped, no locality/city/state
tail. The prompt then speaks it with no transformation step at all, which is the only version of
this that cannot fail. Keep sending `location` as-is for tool payloads and matching; this is purely
the sayable form.

Related: §2 (full postal addresses arriving in `location`) is the same root problem seen from the
data side.

## 6. Pass `${location}` on INBOUND too, populated from the caller's stored profile (added 2026-09-08)

**The ask:** inbound agents currently receive no `location` argument. Send one, filled from the
caller's own stored `item_state.location`, so the confirm line reads a substituted token instead of
requiring the model to recall what a tool result said several turns earlier.

**Why this is rung 5 and not another prompt edit.** The rule "if you hold a location, CONFIRM it,
never ask openly" is present in all six inbound prompts and has been rewritten four times, each time
with the previous failure's call ids attached (`bbdb6eaf`, `5a3aef43`, `0358c875`, then `2d8b7cb1`
as a post-fix recurrence). Measured over the cached calls: **of 10 calls where the profile held a
real location and the bot asked an area question, 9 asked it OPENLY without confirming what we
already had.**

| bot | open asks on a known location |
|---|---|
| `kkb-kn-in-signals` | 4 |
| `kkb-hi-in-signals` | 2 |
| `dkb-kn-signals`, `kkb-hi-in`, `kkb-kn-out` | 1 each |

Examples: `6570a566` (today) held `Dharwad` and asked "ನೀವು ಯಾವ ಏರಿಯಾದಲ್ಲಿ ಕೆಲಸ ಹುಡುಕ್ತಾ ಇದೀರಾ?", so the
caller supplied "ಹುಬ್ಬಳಿ ಧಾರವಾಡ" — a fact we were holding. `05a4b394` held `Kundgol`, `be84007a` held
`Hubballi`, `5076af4a` held `Bailahongala`, `1c3b4fe7` held `Sahibabad, Ghaziabad`.

**Why the prompt cannot fix it.** The rule requires the model to remember, at the moment it composes
an area question, a value it read in a tool result several turns earlier. Every rule in these prompts
that reliably holds is instead **checkable against the turn being composed** — the apply-success
positional rule ("is there a fresh apply_job result in this turn?"), the Turn-B landmark check ("is
the text `nearest_landmark` present in the context block?"). A cross-turn recall has no such handle,
which is the same reason the ordinal running count fails on 58% of multi-batch calls (analyser D76).

**Contrast that with what works.** On the OUTBOUND bots the caller's place arrives as `${location}`
and is read out of a substituted token. Over 449 calls, real callers produced **zero** cases of the
bot naming a place other than the one it was given. The mechanism difference is not the wording —
it is whether the value is in the sentence or in the model's memory.

**Severity, stated honestly:** this is an irritation, not a falsehood. The caller is asked something
we already know and usually answers it consistently, so nothing untrue is said. It is worth fixing
because re-asking a fact we hold is the most annoying thing this bot does, and because the fix is
cheap on your side and impossible on ours.

---

# Added 2026-09-09, REVISED 2026-09-10 — consent testing is now unblocked; one ask remains

## 3. WITHDRAWN — we can fixture consent states ourselves after all

The 2026-09-09 version of this section asked you to provision a record with `terms_accepted` /
`privacy_accepted` false, because we believed the caller's identity was pinned to the dialled tester
DID. **That was our error and the ask is withdrawn.** `contact_phone` passed in a call's
`agent_args` DOES reach the model, so we can build any profile state on a throwaway number via the
admin API and point the bot at it. Verified end-to-end on calls `e0e7bbc2` and `f796df13`.

What we learned about consent while doing it, recorded here because it constrains the data model and
is worth your team knowing:

| probe | result |
|---|---|
| create with `compliance` omitted | 200 — user + profile created with **zero consent rows**: `user_consent` terms/privacy **false**, item `draft`, `profile_consent_accepted` **false** |
| create with `compliance` = `user_terms` only | **400 `USER_LEVEL_INCOMPLETE`** — *"user_terms and user_privacy must be sent together"* |
| create with `user_terms` + `user_privacy`, no `profile_creation` | 200 — participant flags true, item `draft`, `profile_consent_accepted` **false** |
| any `compliance` value sent as `false` | **400 `CONSENT_DECLINED`** — *"consent cannot be declined — omit a key to skip it"* |
| update (POST with `item_id`) carrying `compliance` all-true, against a **draft** | 200 — consent recorded **and the item becomes `live`** |

Two consequences we have built around: consent is **write-once-true**, and since compliance-all-true
is what makes an item live, **"a live profile with a false consent flag" cannot exist** — every
false-flag state is necessarily a `draft`. Our bot now repairs that state with an update carrying the
compliance array (a `record_consent` tool) rather than `create_profile`, which was minting a second
live profile and orphaning the first.

**One question still for you:** is an update carrying `compliance` the sanctioned way to record
consent for an existing caller, or is there an endpoint intended for it? We are relying on the
create/update-same-endpoint behaviour documented in §A.2.

## 4. WITHDRAWN — the tester DID's 5-profile cap no longer blocks us

`create_profile` on `+917946350285` still returns `409 PROFILE_LIMIT_REACHED` (max 5 seeker
profiles, and there is no DELETE route on `/api/v1/admin/participant` — `404 Route not found`), but
we no longer need that participant for new-caller tests: we point `contact_phone` at a fresh number
instead. Freeing those 5 stale profiles would still be tidy, and a DELETE route would help us clean
up our own test records, but neither is blocking.

## 5. WITHDRAWN — we can now get a successful `apply_job`, and we no longer need test inventory

**Resolved on our side, 2026-09-23. Please ignore the ask below; it is kept for context.** The cause
was our fixtures, not your data: we were applying to `job_id`s pasted into `${recommendations}`
months ago. Now that the bot fetches jobs live through `signals-search` (`get_recommended_jobs` /
`get_jobs`), every `job_id` it applies with is by construction a currently-live posting. Successful
applies, all on `gzb-signals`: **`511171cf`**, **`6dc1a058`**, **`45490ef6`** and **`28704be3`**
(inbound). Everything downstream of a successful apply — the post-apply questions, the profile
write-back and the closing read-back — has now run in a real call. **No action needed from you.**

The original text follows.

---

Every apply in testing fails at the target, not the source:

- `TARGET_ITEM_NOT_FOUND` — the `job_id`s in our fixtures no longer exist. On the Kannada bot they
  additionally belong to the wrong instance (our fixtures carry `gzb-signals` ids; that bot reads
  `dharwad-signals`).
- We tried minting our own job posting to apply to: `POST /admin/participant` with
  `domain: provider`, `item_type: job_posting_1.0` + `compliance` all-true returns 200 but the item
  stays **`draft`**, and applying to it fails `PROFILE_NOT_LIVE` — *"target_item is not live"*.
  Adding `hiringManagerName`/`Email` does not change it; other fields are rejected as additional
  properties. So a job posting evidently goes live by some step we cannot reach through this API.

**The ask:** either (a) a handful of currently-live `job_posting_1.0` item ids per instance
(`gzb-signals` and `dharwad-signals`) that we can keep in fixtures, or (b) tell us what makes a job
posting live so we can mint our own test inventory. Until one of those exists, **nothing downstream
of a successful apply is testable** — the post-apply questions, the profile-completion write-backs
and the closing read-back have never run in a test, on any bot.

---

# Added 2026-09-23 — the participant consent block was renamed, and there is still no consent date

## 6. `user_consent` → `compliance`: an unannounced response-shape change broke a live gate

`GET /api/v1/admin/participant` used to return, at the top level:

```jsonc
"user_consent": { "terms_accepted": true, "privacy_accepted": true, "has_age": true }
```

As of **2026-09-22** it returns instead:

```jsonc
"compliance": [ { "key": "user_terms",   "value": true },
                { "key": "user_privacy", "value": true },
                { "key": "has_age",      "value": true } ]
```

and `user_consent` is gone (reads as absent). Verified the same day across four numbers on **both**
instances (`gzb-signals` and `dharwad-signals`), so this is a platform-wide change, not per-tenant.

**What it cost us.** Our consent gate reads those flags and — correctly — treats a missing flag as
"consent not given". So from the moment of the rename, every caller with a profile was being read the
full terms disclosure again, including people who had consented days earlier. The prompts are fixed,
but the class of failure is worth naming: **a renamed field in this response silently changes what
citizens hear on a live call.** A heads-up before a response-shape change, or a deprecation window
where both keys are returned, would have avoided it entirely.

**The ask:** tell us before the shape of this response changes again, and where practical keep the old
key alongside the new one for a release.

## 7. Still no consent TIMESTAMP — the annual refresh cannot be built

The owner's T&C script requires re-asking for terms when they were accepted **more than 12 months
ago**. That is not implementable against this API: the `compliance` rows carry a boolean and nothing
else, and an item's `created_at` / `updated_at` is when the profile record changed, not when consent
was given. Using the profile dates as a proxy would re-ask people who consented last week and skip
people who consented two years ago, so we have deliberately not done it.

**The ask:** expose the date each consent row was written — e.g. `{"key":"user_terms","value":true,
"accepted_at":"2025-08-14T…"}`. Until then the annual refresh is shipped as flag-based only, and
anyone whose flags are true will never be re-asked however old their acceptance is.

## 8. `create_profile` cannot create an account from name + phone alone

The script's Part 1 tells the caller "an account will be created using your name and phone number",
then Part 2 saves the details. The API refuses that order: a create carrying `compliance` without an
age returns **400 `AGE_REQUIRED` — "age is required with consent on this domain"**. So consent cannot
be recorded until an age is known, and the account genuinely does not exist at the moment Part 1 is
spoken. We therefore do not tell the caller their account is created at that point.

**The ask (optional, product call):** if the intent is a real name+phone account at first contact,
consent needs to be writable without an age. Otherwise the script's Part 1 wording should stop
implying the account exists at that moment.

---

# Added 2026-09-23 (later) — moving the bot onto the jobs + services APIs: what blocks quality

Context: the KKB Slim Hindi bot no longer receives a curated `${recommendations}` array from the
campaign. It now fetches jobs itself (`signals-search` anchor + textSearch) and services
(`fetch_local`, `item_domain: service_provider`). That works — but the raw inventory is in much worse
shape than the curated list was, and three things below directly limit what the bot can say.
**All figures measured on 2026-09-23 across all 1258 live `job_posting_1.0` items on gzb-signals.**

## 9. 70% of live jobs have a role the bot cannot say aloud

| role value | count |
|---|---|
| `na` | 726 |
| `Any` | 67 |
| `Any | Helper`, `Any | Sales`, `Any | Crew Member - McDonald's`, … (pipe-joined) | ~80 |
| blank / null | 2 |
| **total unusable** | **875 of 1258 (69.6%)** |

The bot now drops these rows before speaking, so callers never hear them — but it means a search that
returns 5 rows often yields 1–2 offerable jobs, and an anchor on a profile whose role is `Any` returns
rows literally named `"Any | Anyrrr"`. **The ask:** clean or retire the `na`/`Any` rows, and stop the
pipe-concatenation at the source. Until then the effective inventory is ~383 jobs, not 1258.

## 10. `jobProviderLocation` is masked on 99.9% of jobs, so the bot cannot tell a caller where a job is

`jobProviderLocation` comes back as `"G***"` on 1257 of 1258 rows — on `fetch_local` **and** on
`signals-search`, **with** `x-api-key` + `x-acting-org-id`. Consequences we have had to ship:
- The location sentence no longer names the jobs' city (the clause was deleted — it asserted a fact
  we no longer have, and the only value the model could substitute is the caller's own city).
- When a caller asks where a job is, the bot must say it does not know. On a live call today a caller
  asked exactly that.
- `fetch_local` **silently ignores** a `jobProviderLocation` filter — filtering on it returns all 1258
  rows rather than an error, which is worse than failing loudly.

**The ask:** unmask the employer work city for the voice-bot service credential. This is an employer's
work location, not personal PII; proximity is the whole premise of the campaign, and right now the bot
is the only party in the flow that cannot see it.

## 11. Search has no relevance floor — it always returns rows, however wrong

`POST /signals-search/v1/search` returns a full page for any query:

| query | top rows | top score |
|---|---|---|
| `electrician` | Electrician ×3 | 0.691 |
| `data entry operator` | Data Entry Operator ×2 | 0.666 |
| `nurse` | `na`, `na`, `na` | 0.499 |
| `teacher` | `Driver`, `na`, `na` | 0.540 |
| `xyzzy nonsense query` | `na`, `ITI (Other)` | 0.434 |

So a non-empty result is not evidence we hold that work, and the bot has to judge every row itself.
**The ask:** a `minScore` parameter, or omit rows below a floor. A relevance cut-off in the API is
worth more than any prompt rule we can write, because the prompt is guessing at a threshold
(empirically ~0.55–0.58) that only you can set properly.

## 12. Smaller things found while testing

- **90% of jobs have no salary** (1127 of 1258 lack `salaryMin`). The bot says salary only when the
  row carries one, so most jobs are announced as role + company alone.
- **Geo search returns `distanceMeters: 0` for every row** — five different jobs, all `0m`, from a
  point 25km away. Jobs do carry real `item_locations` lat/lng, so the distance calculation looks
  wrong. Untrusted and unused by the bot for now.
- **Service contact details are masked** (`contactPhoneNumber: "7***"`, `contactEmail: "s***@…"`), so
  the bot cannot give a caller a service's number — it says our team will connect them. If the intent
  is for seekers to contact services directly, these need unmasking.
- **One service row is test data** ("Temp - PS", `costToBeneficiary: Free`, serves MSMEs only). The bot
  skips MSME-only rows, but it would be cleaner not to have it live.
- `natureOfJob` is `"Not Available"` on a large share of rows.

---

## 13. PLEASE DELETE — four seeker records on gzb-signals that should not exist (2026-09-23)

There is no DELETE route on `/api/v1/admin/participant` (`404 Route not found`), so we cannot remove
these ourselves. All are **live** seeker profiles, so they can surface in employer-side searches.

| user / item | phone | how it got there |
|---|---|---|
| user `b2683040-9490-4858-b63b-f8383636ba7e`, item `6c340287-a80f-4468-9643-86f177ea5a4d` | `91918888888790` | **A bot bug, not a test.** The bot doubled the country code on `update_profile`; your endpoint finds-or-creates by phone, so it created a new user. Call `482ea2e2`. Duplicate of a real test profile named Ramesh. |
| item `391aa220…` | `918888777101` | our geocoding probe, name "Geo Probe" |
| item `8c2c4568…` | `918888777102` | our geocoding probe, name "Geo Probe" |
| item `5a681768…` | `918888777103` | our geocoding probe, name "Geo Probe" |

**Also worth knowing — this is a class, not a one-off.** Because `POST /admin/participant` creates
rather than fails when the phone is not found, any malformed phone from any client silently makes a
new person. We have fixed the cause on one bot and have seven more to fix. **A cheap backend guard
would stop the whole class:** reject a `phone_number` that starts with `9191` and is longer than 12
digits, or reject an update carrying an `item_id` whose owner's phone differs from the one sent
(today that returns `403` only *after* the phantom has already been created by an earlier write).

## 14. For information — you already geocode, and it works

Not an ask; recording it because it changed our plan. We were about to add Google's geocoding API to
turn caller locations into coordinates. Testing showed **your backend already geocodes the profile's
`location` string** into `item_locations` on every write, and does it well:

| `location` written | resolved to |
|---|---|
| `Ghaziabad, Uttar Pradesh, India` | Ghaziabad city centre `(28.6699, 77.4544)` |
| `Muradnagar, Ghaziabad, Uttar Pradesh, India` | Muradnagar — **12.4 km** away, correct |
| `Muradnagar Bus Stand, Muradnagar, Ghaziabad, Uttar Pradesh 201206, India` | a further ~140 m |

So the job on our side is only to send a more specific `location` string — no external service. One
question: **which geocoder is behind it, and does it have a quota we could exhaust?** If every call
starts writing a location, your geocoding volume goes up by roughly the call volume.
