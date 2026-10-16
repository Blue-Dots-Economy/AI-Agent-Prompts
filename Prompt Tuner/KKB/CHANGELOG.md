# KKB Changelog

Every prompt edit to KKB is logged here. Entry format:

```
## YYYY-MM-DD — <short title>
- **Feedback/bug:** what prompted the change
- **Change:** what was changed
- **Files:** which files were touched
- **Ported from:** <source agent> (only for cross-agent ports)
```

## 2026-10-13 - Education and other-help values the backend accepts (Signals prompts)
- **Feedback/bug:** tracker r113: profile saves rejected with 400 `INVALID_ITEM_STATE` for `ITI / Other Vocational Trainings` and `Polytechnic / Diploma`; the live tool schema says `ITI` / `Diploma`.
- **Change:** the four KKB Signals prompts now quote `ITI` / `Diploma` and map `otherHelpNeeded` to the two values the API accepts. No other change. These agents carry no live traffic now (numbers moved to KKB Slim); kept correct so they never regress.
- **Files:** `KKB/KKB Placeholder Hindi Signals.md`, `KKB/KKB Placeholder Kannada Signals.md`, `KKB/KKB Placeholder Inbound Signals.md`, `KKB/KKB Placeholder Inbound Kannada Signals.md`. DEPLOYED, NOT VERIFIED (no traffic).

## 2026-09-23 — T&C Bot Prompt Script: account+terms (Part 1), save-details (Part 2), per-application disclosure (Part 3)

- **Feedback/request:** the owner's `T&C Bot Prompt Script` — a three-part consent flow. Part 1: an
  account/terms disclosure for a first-time user or an annual refresh, with five mandated elements.
  Part 2: explicit permission to save a new seeker's details. Part 3: a per-application disclosure
  naming the company and role, fired before every `apply_job`.
- **Change (Hindi master):**
  - **Part 1 — new section, decided off the `get_profile` result and spoken before any job talk.**
    Reads the participant `compliance` array (`user_terms`, `user_privacy`) plus the selected item's
    `profile_consent_accepted`; all three true → asks nothing and the call is unchanged; any false, or
    no profile at all → asks. Agree + live profile → silent `record_consent`; agree + draft/new →
    `create_profile` records it at Step 4. Decline → call ends, no account, no apply. Unclear → one
    re-ask, then treated as a decline. `record_consent` failure → do not proceed to job discovery.
    "अकाउंट" is permitted in this one line; the ban on "प्रोफाइल" still holds everywhere.
  - **Part 2 — replaced the old new-caller consent gate.** Permission to save name/age/education/
    experience, asked once after the Step-3.5 basics. Decline → jobs are still offered (browse-only,
    no `create_profile`, no `apply_job`); if they then ask to apply, the save is offered **once, at
    that moment** and never pre-announced. `create_profile` failure → say so, keep showing jobs.
  - **Part 3 — the mandatory pre-apply disclosure now names the selected job's company and role** and
    adds "वे आपसे सीधे संपर्क कर सकते हैं"; fires per application, twice for two jobs. Masked company →
    the line is spoken without it rather than reading a mask aloud. Refusal → "कोई बात नहीं। क्या मैं
    आपको दूसरी जॉब्स बताऊँ?", back to the list, not the end of the call. Success line now names the
    company.
- **Owner decisions (2026-09-22):** app = **Blue Dots**, organisation = **Ekstep Foundation** (spoken
  as ब्लू डॉट्स / एकस्टेप फाउंडेशन). Part 3's success line **keeps its conditional** and only adds the
  company name — "[company] आपसे संपर्क करेगी" was declined as an over-promise. Part 2 decline →
  offer the save once at the apply point.
- **Three items in the script NOT implemented as written, each for a grounded reason:**
  1. **The 12-month annual refresh is not computable.** The API returns no consent date — `compliance`
     rows are booleans, and an item's `created_at`/`updated_at` is when the profile changed, not when
     terms were accepted. Gated on the flags alone; needs a consent timestamp from the data team.
     Approximating it off profile dates would re-ask people who consented last week.
  2. **"Your account is created." is not spoken at Part 1.** `create_profile` with name+phone returns
     **400 `AGE_REQUIRED` — "age is required with consent on this domain"**, so nothing is written at
     that point; and on the returning path no account is *created* at all, it already existed. Replaced
     with a neutral acknowledgement; the write is asserted only where it happens.
  3. **The 18+/minor-block line is NOT added as a second failure row.** Apply Failure Handling allows
     exactly ONE row by design — with two, the model spoke both back to back (`b4e34994`, Hindi) and
     welded them into one sentence (`41a2c19d`, Kannada). Recommended instead as an error→line mapping
     in the `apply_job` tool description, the mechanism that took `ACTION_LIMIT_REACHED` from broken to
     9/9 (analyser D51/D52). Awaiting the go-ahead.
- **Tooling:** `record_consent` added to the `kkb-hi-signals` agent (`raya/toolspecs/record_consent.json`
  via `scripts/raya_tooladd.py`) — Part 1's live-profile arm calls it, and the agent did not have it.
- **Verification — KKB Hindi Signals, BOTH branches, VERIFIED:**
  - **`0d1cbd72`** — fixture `918888888773`, a draft item with `user_terms:false`, `user_privacy:false`,
    `profile_consent_accepted:false`. The bot spoke the full five-element disclosure (Blue Dots account
    from name+phone, the three purposes, one year, Ekstep Foundation, terms in the app), the caller
    agreed, `record_consent` fired on item `334e3684`, and the record read back **`live` with all three
    flags true**. Part 3 fired naming the job: "आपकी personal details काशी इन्फोटेक के साथ डेटा एंट्री
    ऑपरेटर के काम के लिए शेयर होंगी। वे आपसे सीधे संपर्क कर सकते हैं।" Part 1 correctly did NOT claim the
    account was created.
  - **`f0509869`** — all three flags true: **zero** terms/account lines, no consent tool, straight from
    `get_profile` to the role check. The silent path is intact; the gate does not false-fire.
  - **One defect found and fixed on `0d1cbd72`:** the bot prefixed the Part 3 disclosure with its own
    "क्या आप इसके लिए अप्लाई करना चाहेंगे?", putting two questions in one turn. Part 3 now states that it
    IS the question and may not be preceded by another apply question.
- **Files:** `KKB/KKB Placeholder Hindi Signals.md`, `raya/toolspecs/record_consent.json`

## 2026-09-23 — T&C script replicated across the Signals fleet; the Kannada mirror failed verification until its instructions were byte-synced

- **Request:** after verifying on KKB, replicate the T&C script across all Signals bots.
- **Applied to all six seeker Signals conversation prompts** — KKB Hindi/Kannada, KKB Hindi/Kannada
  Inbound, Maya Hindi/Inbound — plus the five-element disclosure on both KKB-Slim bots so the A/B
  arms behave alike. `record_consent` added to the five agents that lacked it. Part 1 is
  **byte-identical across all four Hindi files**; the Kannada files' English skeleton is byte-identical
  to the Hindi master, with only the quoted spoken lines differing.
- **Output prompts updated on all six agents.** `consent_status` was scoped to "the new-caller path"
  and said "NA for a returning caller" — exactly the caller the T&C flow now asks, which is why the
  master's first verified call returned `consent_status: None`. It now has Given / Declined /
  **Not Needed** / Failed / NA, plus a new `profile_save_consent` (Given / Declined / Given At Apply /
  NA) for Part 2. Live snapshots in `raya/live-snapshots/` refreshed.
- **KKB Kannada Signals — FAILED, then fixed and VERIFIED:**
  - **`7b5f6945` (FAIL):** the bot asked for consent in Kannada, the caller said "ಹೌದು ಒಪ್ಪಿಗೆ ಇದೆ", it
    answered "ಸರಿ, ಧನ್ಯವಾದ." — and **never called `record_consent`**. The record was checked: flags still
    false, item still draft. **A caller consented aloud and nothing was stored**, which is worse than
    not asking at all.
  - **Root cause: my own paraphrase.** The Kannada Part 1 had been written fresh with shortened English
    instructions instead of copied from the Hindi block that fires reliably. Rebuilt so the English is
    byte-identical to the Hindi master and only the spoken lines differ.
  - **`7a059554` (PASS):** `record_consent` fired, and the fixture flipped to `user_terms:true`,
    `user_privacy:true`, item **`live`**, `profile_consent_accepted:true`. 0/1 before the sync, 1/1 after.
  - **`1d7074e9` (PASS, all-true branch):** zero terms lines, no consent tool — correct silence.
  - **Lesson for the sync rule:** the "copy agnostic content verbatim" rule is not housekeeping. A
    paraphrase of the same instruction, in the mirror, changed whether a tool got called at all.
- **NEW DEFECT, open — the Kannada bot repeats its introduction.** On `7b5f6945` the intro was spoken
  **4 times** and on `7a059554` **twice**, with Part 1 bundled onto the re-spoken greeting instead of
  being its own turn. `get_profile` is firing in the audio-check turn rather than after the opening
  question, which is what collides. Comparable calls on 2026-09-09 spoke it once, so this is current
  and Kannada-specific. Part 1's own outcome is unaffected (the tool fires, the flags flip) but the
  caller hears the greeting twice. **Not fixed — deliberately not adding a third wording of a rule the
  prompt already states; the trigger is the early fetch and it needs its own root-cause pass.**
- **FABRICATED CONSENT on Maya Inbound — found, root-caused, fixed, re-verified.**
  - **`9df94781`:** the five-element disclosure was **never spoken**. The caller was asked only
    "क्या मैं अभी इस जॉब के लिए आपकी तरफ़ से अप्लाई कर दूँ?" and `record_consent` fired off that —
    writing terms + privacy + profile consent as `true` for someone who had never heard the terms.
  - **Rung-4 guard tried and FAILED.** A required `terms_check` enum was added to the tool
    (`disclosure-read-and-agreed-this-call` | `not-read`), modelled on `duplicate_check`. On the
    retest **`bdae75d6`** the disclosure was again never spoken and the model sent
    **`terms_check: "disclosure-read-and-agreed-this-call"`** — a false assertion. 2/2 fabricated.
    See analyser **D91**: a required parameter constrains what the model SAYS, not what it DID.
    `duplicate_check` works because its value is checkable from the turn being composed;
    "did you speak X earlier" is a self-report about a turn the model never took.
  - **Safe state first:** `record_consent` was REMOVED from the agent, so a skipped disclosure records
    nothing (the pre-feature status quo) rather than a false consent. Verified safe on **`7c24f130`**:
    no consent written, and no duplicate profile either.
  - **Real root cause: the router, not the wording.** The DECISIVE ROUTER numbers its turns and sends
    the model to the named branch headings; Part 1 sat BETWEEN the router and those headings, so the
    route passed over a section that was never entered. Part 1 is now **step 3 of the router itself**
    in all three inbound prompts. On **`7c24f130`** the disclosure was spoken, in its own turn.
  - **Re-verified with the tool restored — `1d76fdb2`:** disclosure spoken as its own turn,
    `record_consent` fired with a now-TRUTHFUL `terms_check`, flags flipped false→true, item `live`.
- **Turn-boundary rule — partially effective.** Added to all eight prompts after four of the first
  five bots welded the disclosure onto the greeting turn. It took on KKB Kannada Inbound
  (**`fe7864d1`**, clean and unbundled) and on Maya Inbound, but **NOT** on Maya Hindi outbound:
  **`341a6c5e`** read the disclosure and recorded consent correctly but still bundled it into the
  greeting. Deliberately NOT given a third wording — the underlying cause is the fetch running inside
  the greeting turn, a pre-existing violation this change only made visible. **Open.**
- **Verification status per variant — consent RECORDING, against a real false-flag record:**
  KKB Hindi ✅ `0d1cbd72` (+ all-true ✅ `f0509869`) · KKB Kannada ✅ `7a059554` (+ all-true ✅
  `1d7074e9`) · KKB Hindi Inbound ✅ `722b4131` · KKB Kannada Inbound ✅ `fe7864d1` · Maya Hindi ✅
  `3c3f8740`, `341a6c5e` · Maya Inbound ✅ `1d76fdb2`. **All six.**
  **Delivery quality (own turn vs bundled):** clean on KKB Hindi, KKB Kannada Inbound, Maya Inbound;
  **bundled on Maya Hindi (open)**; untested post-fix on KKB Hindi Inbound and KKB Kannada outbound.
  **KKB-Slim Hindi/Kannada — five-element line deployed, NOT VERIFIED.**
- **Files:** `KKB/KKB Placeholder Hindi Signals.md`, `KKB/KKB Placeholder Kannada Signals.md`,
  `KKB/KKB Placeholder Inbound Signals.md`, `KKB/KKB Placeholder Inbound Kannada Signals.md`,
  `Maya/Maya Hindi Signals.md`, `Maya/Maya Inbound Signals.md`,
  `KKB-Slim/KKB Slim Hindi Signals.md`, `KKB-Slim/KKB Slim Kannada Signals.md`,
  `raya/live-snapshots/*.output_instructions.md`

## 2026-09-23 — The backend renamed the participant consent block; both slim bots were reading a field that no longer exists

- **Found while grounding the T&C script, not reported.** `get_profile` used to return
  `user_consent: { terms_accepted, privacy_accepted, has_age }`. As of 2026-09-22 it returns
  **`compliance: [ {key:"user_terms",value:…}, {key:"user_privacy",value:…}, {key:"has_age",value:…} ]`**
  and the old key is gone. Verified across four numbers on both instances (gzb + dharwad).
- **Impact:** the slim bots' consent gate read `user_consent.terms_accepted`, and its own rule says
  missing/null counts as NOT given — so since the rename **every caller with a profile was being read
  the terms**, including fully consented ones. A silent live behaviour change caused by an upstream
  rename, not by a prompt edit.
- **Change:** both slim prompts now read the `compliance` array by `key`, treat an absent key as
  `false`, and carry the old name only as a note. Example C's context block updated to the new shape.
- **Also found:** a **live** profile with `user_terms: false` / `user_privacy: false` now exists
  (`91XXXXXX6073` on dharwad) — the state I had reported as impossible to construct. The migration
  produced it, so the `record_consent` path is testable for real.
- **Verification: VERIFY-PENDING** — deployed to both slim bots; the harness was down.
- **Files:** `KKB-Slim/KKB Slim Hindi Signals.md`, `KKB-Slim/KKB Slim Kannada Signals.md`

### 2026-09-07 (later) — the missing-job-data line had no precondition the model could check

- **Found while trying to verify the read-back, not reported.** Harness call `af627b9d`: one job was
  supplied (Field Marketing Executive, Vasundhara, Ghaziabad), the caller said she wanted Bengaluru
  only, and the bot answered **"अभी आपके लिए मुझे जॉब्स नहीं मिल रहीं"** — the *missing-job-data* line,
  i.e. "no jobs were supplied to this call". A job existed and had never been named to her.
- **Root cause:** there was **no line for "you want a city we have nothing in, and I still have a job
  to show you"**. Path L (location mismatch) is gated on every job having already been presented, which
  had not happened; the role-no-match line is about a role, not a place. With no rule for the case, the
  model reached for the nearest line that sounded close — and that line asserts something false about
  the array. Same structural shape as D66, D69 and D70: no rule for the case, so it inherits a wrong
  default.
- **Change:** the missing-job-data line now carries a precondition the model can check on the spot —
  **count the valid entries in `${recommendations}`; if the count is more than zero you may NOT say it,
  whatever the caller has just refused.** "No jobs were supplied" is a statement about the ARRAY, never
  about the caller's city or role. If jobs remain unnamed, name them; if all have been named and turned
  down for a place, that is the location-mismatch path. Applied to the 6 prompts that carry the line
  (the 4 KKB outbound + 2 Maya outbound; the inbound bots use a hardcoded inventory).
- **Verified `55a44edb`:** same fixture, same single job, and the bot said **"अभी के लिए मेरे पास यही एक
  जॉब थी। किस तरह का काम देख रहे हैं?"** instead — true, and it keeps the call open.
  `nojobs_integrity.py` reports no finding on it and still flags `af627b9d`.
- **A correction to something I nearly reported as a bug.** On `af627b9d` the bot said the caller's
  location was **बेंगलुरु** when the campaign sent `Muradnagar, 110045`, which looked like the
  profile-substitution bug the location sentence exists to prevent. It was not: at turn 6 the caller
  said *"बेंगलुरु में कहीं भी ठीक है मैडम"* out loud, and a city the caller states in THIS call is rank 1
  on the candidate list, ahead of the campaign value. The bot was right and the persona was simply a
  Bengaluru caller paired with a Ghaziabad fixture — my error, not the prompt's.

### 2026-09-07 — verification blocked: the tester DID can no longer produce a successful apply

The end-of-call read-back fix (previous entry) is still **DEPLOYED, NOT VERIFIED** after five attempts,
and the blocker is now identified precisely rather than guessed at.

`get_profile` on the tester DID returns **five** `profile_1.0` seeker items — `588a907f`, `5822b168`,
`2557ed02`, `0ee9e95a`, `0b84429b` — so which profile an apply goes out from varies per call. Across
every seeker bot's tester traffic, **15 of the 21 job_ids ever attempted are now blocked** (a prior
success, or `ACTION_LIMIT_REACHED`), and jobs my scan classed as never-attempted still come back
`ACTION_LIMIT_REACHED` (`e2658094` on both `1536830c` and `55a44edb`) — an active request can exist
between a profile and a job from activity that never appears in the call transcripts I can read.

The read-back only fires after a SUCCESSFUL apply, so on this number it is unreachable. Clearing it
needs one of:
- the data team clearing the tester profiles' applications (and ideally de-duplicating the five
  profiles down to one), or
- a second authorised test number — **not** a real user's, per the standing rule, or
- one real QA call, which is the cheapest of the three.

Recorded here rather than left as "flaky", because it is not flaky: it is a saturated fixture.

**Attempt 6 — the Kannada route, which should have worked and didn't.** The Ghaziabad saturation does
not apply to `kkb-kn-signals`: it runs on the Dharwad instance with a different profile set, and it
produced a genuine successful apply earlier the same evening (`e853e2c0`, action_id `4fbb97ec`). The
read-back fix is language-agnostic and is present in both Signals prompts, so verifying it there is
equally valid. Scanned all three Kannada seeker bots' tester traffic: 8 Dharwad job_ids blocked, **10
of 12 validated Dharwad jobs fresh**, and built `readback-kn.json` on `9b42e02f` (Mechanic, Channamma
Automotive, Rayapur, Hubballi) with `location: "Hubballi"`.

**Eight consecutive dial attempts across two runs never bridged** (`outcome=Failure`, `dur=0`, no
transcript) — the harness's known telephony flakiness on the single tester DID, after a full 7-minute
idle to recover the bridge rate. Nothing to do with the prompt or the fixture.

So the fixture problem is solved and the verification is now purely blocked on getting a call to
connect. The fixture is committed and ready: whoever next has a working line can run

    python3 scripts/raya_testcall.py lang <tester> kn
    python3 scripts/raya_testcall.py persona <tester> raya/personas/kn-force-apply.md
    python3 scripts/raya_testrun.py 33037201-78ce-405d-b509-a3b6934e20f1 7946350285 \
        raya/testcases/args/r3/readback-kn.json <tester> readback-kn

and the pass condition is one line: after the apply-success line and the service-provider reply, the
bot must read back name, age, gender, role, qualification and area, then ask "सब सही?" — in Kannada,
"ಎಲ್ಲಾ ಸರಿನಾ?".

### 2026-09-08 (night) — VERIFIED end-to-end on `6286926f`: five fixes at once, on a real successful apply

**The first genuine `apply_job` success on the tester's Dharwad profile** — `action_id`
`ec5a2416-e8ec-4fe2-9a6a-8dcde048f984`, `status: "success"` — which is what six earlier read-back
attempts had been blocked on (the Ghaziabad profile is saturated with `ACTION_LIMIT_REACHED`).
`kkb-kn-signals`, 2026-09-08 16:19 UTC, fixture `readback-kn.json`.

> ಒಂದ್ಸಲ ಕನ್ಫರ್ಮ್ ಮಾಡ್ತೀನಿ — ನಿಮ್ಮ ಹೆಸರು ಪಾರ್ಥ, ವಯಸ್ಸು **ಇಪ್ಪತ್ತಾರು**, **ಮಹಿಳೆ**, ಕೆಲಸ ಇನ್ಶೂರೆನ್ಸ್
> ಫೀಲ್ಡ್ ಏಜೆಂಟ್, ಓದು **ಹನ್ನೆರಡನೇ ತರಗತಿ**, ಏರಿಯಾ ಕೋರಮಂಗಲ — ಎಲ್ಲಾ ಸರಿನಾ?

**Five things proven in one call:**

| fix | proof in this call |
|---|---|
| **age in words** | `ವಯಸ್ಸು ಇಪ್ಪತ್ತಾರು` — 26 spelled out, not "26". This is the exact bot that said **"ವಯಸ್ಸು 38, Male"** on `08449995` |
| **gender in the target language** | `ಮಹಿಳೆ`, not `Female` |
| **qualification in words** | `ಹನ್ನೆರಡನೇ ತರಗತಿ`, not "12th" |
| **the read-back is LABELLED and covers all six fields** | name · age · gender · ಕೆಲಸ (role) · ಓದು (qualification) · ಏರಿಯಾ — closing the gap on `08a8ff4f`, which omitted role and qualification |
| **the Phase-2 bridge carries no duplicate claim** | the success line ran in the turn holding the real result, then the bridge said only *"ನಿಮ್ಮ ಮಾಹಿತಿ ಪೂರ್ಣವಾಗಿ ಇಡೋಕೆ…"* — no second "ಅಪ್ಲೈ ಆಗಿದೆ". First verification of this on Kannada |

Also correct on the same call: the location sentence spoke `Hubballi` as **ಹುಬ್ಬಳ್ಳಿ** (canonical
Kannada), the data-sharing line preceded the apply, and `update_profile` fired to persist. Every
detector clean — `spoken_form`, `bracket_leak`, `apply_result_integrity`.

**A false positive in my own detector, found by this call and fixed.** `location_said` flagged
ಹುಬ್ಬಳ್ಳಿ as a substitution: the campaign sends `"Hubballi"`, the canonical Kannada form's English
key in the detector was `"hubli"`, and `"hubli" not in "hubballi"`. So a **correct** conversion read
as a wrong place. Spelling aliases are now normalised before the comparison —
hubli/hubballi, dharwad/dharwar, bengaluru/bangalore, mysuru/mysore, ghaziabad/gaziabad,
muradnagar/murad nagar, koramangala/koramangla — with this call as self-test row 11.

### 2026-09-08 (night) — the confirm-first location rule fails 9 of 10 times. NO fifth wording written.

**Found by the standing suite.** `6570a566` and `fe3161c3` (both today, `kkb-kn-in-signals`, real
inbound callers): the fetched profile carried `Dharwad`, and the bot asked
**"ನೀವು ಯಾವ ಏರಿಯಾದಲ್ಲಿ ಕೆಲಸ ಹುಡುಕ್ತಾ ಇದೀರಾ?"** — the open area question — so the caller supplied
"ಹುಬ್ಬಳಿ ಧಾರವಾಡ", a fact we were already holding.

**Counted: of 10 cached calls where the profile held a real location and an area question was asked,
9 asked it openly.** `kkb-kn-in-signals` 4, `kkb-hi-in-signals` 2, and one each on `dkb-kn-signals`,
`kkb-hi-in`, `kkb-kn-out`. Held values that went unconfirmed: `Kundgol`, `Hubballi`,
`Bailahongala`, `Koramangala, Bengaluru`, `Sahibabad, Ghaziabad`, `BHOJPUR`, `Chikodi`.

**No prompt edit was made, and that is the finding.** The rule is present in all six inbound prompts
and has already been rewritten four times, each rewrite carrying the previous failure's call ids —
"Decide WHICH line to say BEFORE you speak", "the location you already hold comes first", "Only when
BOTH are empty", "The open ask is the LAST branch, not the default", citing `bbdb6eaf`, `5a3aef43`,
`0358c875`, and `2d8b7cb1` as a post-fix recurrence. CLAUDE.md forbids a third wording of a guard
that has failed twice; this would be the fifth.

**Why prose cannot hold it.** The rule asks the model to recall, while composing an area question, a
value it read in a tool result several turns earlier. **Every rule in these prompts that reliably
holds is checkable against the turn being composed** — "is there a fresh `apply_job` result in this
turn?", "is the text `nearest_landmark` present in the context block?" — and the two that fail
worst are both cross-turn recall: this one and the ordinal running count (58%, D76). By contrast the
OUTBOUND bots read the caller's place out of a substituted `${location}` token and produced **zero**
real-caller substitutions across 449 calls. The difference is not wording; it is whether the value is
in the sentence or in the model's memory.

**Escalated as `ESCALATION-data-team.md` §6:** pass `${location}` on inbound too, populated from the
caller's stored `item_state.location`, so the confirm line reads a token instead of a memory.

**Severity, honestly:** an irritation, not a falsehood. The caller is asked something we already know
and generally answers it consistently, so nothing untrue is said — unlike the two apply-claim bugs
found the same night. It is on the list because re-asking a fact we hold is the most annoying thing
this bot does, and because the fix is cheap upstream and unavailable to us.

### 2026-09-08 (night) — `apply_job` fired with no data-sharing disclosure on 18 of 105 calls, every one inbound or Maya

**Found by the standing suite, not reported.** On `73764d9d` (2026-09-08 13:56, `kkb-kn-in-signals`,
a real inbound caller) the caller said *"ಕೃಷ್ಣ ಇಂಡಸ್ಟ್ರಿ. ಎಲ್ಲದಕ್ಕೂ ಅಪ್ಲೈ ಮಾಡ್ರಿ"* — apply me to all of
them. The bot replied that it could only apply to one at a time, the caller said *"ಓಕೆ"*, and it
emitted `apply_job`. **The disclosure that applying shares the caller's details with the company was
never spoken.**

**Counted first, over 105 `apply_job` calls in the cache: 18 had no disclosure before them (17%).**
The distribution is the whole diagnosis:

| bot | violations |
|---|---|
| `kkb-hi-in-signals` | 8 |
| `maya-hi-in` | 5 |
| `maya-hi-out` | 2 |
| `kkb-hi-in`, `kkb-kn-in-signals`, `maya-hi-in-signals` | 1 each |
| **`kkb-hi-signals`, `kkb-kn-signals`** (outbound Signals) | **0** |

**The rule is not missing and not unclear.** It is present in 10 of 12 prompts — including every one
where it failed — it is titled "MANDATORY immediately before every `apply_job`", it says "no
`apply_job` call is permitted until this line has been spoken and answered", and it already names
the caller-picks-straight-off-the-list case with two call ids. It has now failed twice.

**What the split says.** Outbound walks list → deep dive → doubts → consent → apply, and reaches the
disclosure turn on its way. **An inbound caller says "apply me to this one" and the bot treats their
REQUEST as the disclosure** — which it is not: the caller asking to apply is not us telling them what
applying shares. Nor is the bot's own reply to it; on `73764d9d` the turn that got the "ಓಕೆ" was an
explanation about applying to one job at a time.

**Change — the check is now one the model can run against the turn it is composing**, which is the
property every rule in these prompts that actually holds turns out to share (the apply-success
positional rule holds; this prose gate did not): *"Before you emit `apply_job`, look at your own last
two spoken turns. If neither contains the words about details being shared with the company, you have
not disclosed it — do not emit the tool. Speak the line now and wait instead. That is a check you can
perform; remember whether you said it earlier is not."* Plus the two false-equivalences named
explicitly — the caller's request, and the bot's own reply to it.

**Files:** 10 KKB/Maya conversation prompts + the slim rewrite. The two legacy outbound prompts
(`KKB Placeholder Hindi.md`, `KKB Placeholder Kannada.md`) have the spoken line but no
"MANDATORY before every apply_job" section to attach it to; they have had 1 engaged call between them
since 2026-09-01 and are excluded from the `fix_presence` row for that reason — **noted as a real
gap, not fixed.** `fix_presence` row `disclosure-checked-on-the-turn`.

**A stronger fix exists and is an owner call.** `apply_job` already carries a REQUIRED
`duplicate_check` parameter, which is precedent: a constraint expressed in the tool schema is read at
the moment of use and is far stickier than a rules paragraph (CLAUDE.md ladder rung 4). A required
`disclosure_spoken` enum would make the tool uncallable without the assertion, and the assertion is
checkable against the transcript. I have not done it: it changes the live tool contract on 12
production bots, and a required parameter the model omits turns every apply into an error. That is
not a change to make unattended.

**Verification:** **DEPLOYED, NOT VERIFIED.** The reproducing shape is an inbound caller who asks to
apply before hearing about any single job — `raya/testcases/args/r3/inbound-probe.json` with a
persona that opens on "apply me to all of them". Inbound bots need the tester dialled IN, so this
needs a harness run rather than production traffic.

### 2026-09-08 (late, correction) — the location "substitutions" were my own test fixture. Zero real callers.

**I reported the location sentence naming the wrong place on 5 of 15 calls, then 8 of 16, and said
"nearly half of these callers were told something false about their own location". That was wrong.
Split by caller, over 449 calls since 2026-09-01:**

| | ABSENT | OK | RAW | SUBSTITUTED |
|---|---|---|---|---|
| **real callers** | 6 | 4 | **3** | **0** |
| harness dials | 1 | 20 | 0 | **10** |

**All ten substitutions are harness dials on the tester DID. Not one is a real caller.**

**Why my own harness manufactured them.** `get_profile` on the tester DID returns a profile carrying
`location: "Sahibabad, Ghaziabad, India"`. My fixture sends `location: "Sarjapur, 110045"`. So
**every harness dial creates a profile-versus-argument conflict** — which is precisely the condition
the precedence bug needs, and a condition real traffic rarely produces, because a campaign generally
targets people where their profile says they are. `input_coverage.py` had the identical flaw for the
identical reason a week ago; I fixed it there and did not think to look for it here.

**And my diagnosis was wrong on top of the rate.** I concluded the Canonical Location Spellings list
was acting as an "attractor" — the model picking a name off the list — because four of the calls said
साहिबाबाद and one गाज़ियाबाद, and both are list entries. **साहिबाबाद is also the tester profile's
stored city**, and गाज़ियाबाद is the city half of `"Sahibabad, Ghaziabad, India"`. I read the first
coincidence and missed the second. The actual mechanism is the one already documented and already
guarded: **the fetched profile's location beating `${location}`.**

**The experiment I ran on that diagnosis failed 0/3, correctly.** The slim prompt was given a rule
saying the canonical list is a spelling table and never a menu; all three dials still said साहिबाबाद,
because the model was not reading a list — it was reading the profile. **The rule has been reverted**
(slim back to 69,974 chars): a prompt carrying a plausible-sounding rule aimed at the wrong mechanism
is worse than one that carries nothing, because the next person reads it as ruled out.

**What survives, and it is narrow.** The RAW failures are real callers and the fix genuinely has not
landed for one shape: `a899617e` and `7b841e6b` (both pre-fix) and **`a5ba6894` (post-fix)**, whose
value was `10987, Sarhanpur` — digits FIRST, a shape no row of the worked table covers. So:

- **RAW on real callers: a genuine, current, single-shape bug.** One post-fix occurrence.
- **SUBSTITUTED: not observed on any real caller.** It is reproducible in the harness whenever the
  profile and the argument disagree, so it is a real precedence weakness worth fixing — but it is not
  a production rate and I should not have quoted it as one.
- The ABSENT calls remain all pre-gate.

**`location_said.py` now splits real callers from harness dials and prints them separately**, and its
pass line says so explicitly. Two of my own detectors produced inflated numbers today — this one and
its earlier caller-echo ordering bug — and in both cases I reported before splitting the data. The
detector self-tests catch logic errors; they cannot catch a confounded population. That needs the
question asked out loud every time: *who was actually on these calls?*

### 2026-09-08 (late) — the overnight suite found two more instances of the same class: the read-back's age/gender, and DKB's salary

**Found by `run_runtime_checks.sh` over 356 calls since 2026-09-06, not reported.** Both are the
point-of-use pattern again, and both were measured before anything was edited.

**1 — the read-back reads `age` and `gender` straight off the profile.** On `08449995`
(`kkb-kn-signals`) the confirmation line was **"ನಿಮ್ಮ ಹೆಸರು ಸಂತೋಷ್, ವಯಸ್ಸು 38, Male, ಕೆಲಸ ಕಸ್ಟಮರ್
ಸರ್ವಿಸ್ ಎಕ್ಸಿಕ್ಯೂಟಿವ್…"** — the age as an ASCII numeral and the gender as the stored English enum
value, inside a Kannada sentence. **8 of 28 read-backs carried a raw digit or an English enum.**

The prompts already require numbers in words and everything spoken in the target script, in the TTS
section. The read-back template — `उम्र [age], [gender]` / `ವಯಸ್ಸು [age], [gender]` — says nothing,
and `[age]`/`[gender]` are exactly the two slots whose values arrive as `38` and `Male`.
**Change:** the template now carries the conversion on its own line — the age in words, the gender in
Hindi/Kannada, never `38` or `Male`. Six Signals prompts.

**2 — DKB's posting recap speaks the salary in digits.** `सैलरी १२,०००`, `सैलरी 30,000`,
`सैलरी 2000` — **56 of 389 salary lines fleet-wide, almost all of them on this one template**
(`0eb3fc72`, `12dc1466`, `2c197514`, `46812a71`, `48a2fcf3`, `5596030a`, `adfe8052`, `b1b71d68`,
`b3e2de52`, `be2808cc` …). Interestingly `[num_vacancies]` on the same line usually DOES convert
("दो vacancies"), which is what a two-digit number does naturally and a five-digit one does not.
**Change:** the recap line now states that both arrive as digits and are spoken in words, with
`12000` → "बारह हज़ार" and `20000-25000` → "बीस हज़ार से पच्चीस हज़ार" worked through, and the Kannada
twin in Kannada. Four DKB prompts.

**Files:** 6 KKB/Maya Signals prompts (read-back), 4 DKB prompts (recap). Heading parity intact.
`fix_presence` rows `readback-age-gender-in-words` and `dkb-salary-in-words`. **DEPLOYED, NOT
VERIFIED** — the read-back needs a call that reaches the end of a successful apply, and DKB has had
no engaged traffic since 2026-09-04, so it needs a dial.

**This is the third and fourth instance of D71 found today, all of them the same shape:** the general
rule exists and sits far from the template that consumes the value. The company names, the
qualification label, the read-back's age and gender, and DKB's salary were all stated correctly
somewhere else in the prompt. TRRAIN, which states its one conversion on the line that speaks the
value, leaked nothing across 98 calls.

### 2026-09-08 (late) — the location sentence names the WRONG PLACE on a third of the calls it is spoken on; the company fix is verified

**The company-name fix is PROVEN, with a clean before/after.** Same fixture, same persona, twelve
minutes apart, the prompt differing only by the point-of-use edit:

| | call | spoke |
|---|---|---|
| before | `ea0477f4` 14:12 | "मार्केटिंग, **SARA ENTERPRISES** में" |
| after | `fa9a16c0` 14:24 | "**सारा एंटरप्राइज़ेज़** में मार्केटिंग की जॉब" |

Everything else on those two calls was held constant, so the edit is what changed it. That closes
the payload-name half of Khushboo's r5 item 1 on the Hindi Signals bot. The Kannada twin, the inbound
prompts and Maya carry the same edit and are **still unverified**.

**Two bugs in my own detectors, both found by hand-checking their output, both under-reporting.**
Recorded because the numbers I gave earlier today came out of them:
1. `extract_spec.py` paired quotes across the whole 220k file, so one stray unmatched quote shifted
   every pairing after it and three spoken lines present in the slim prompt were reported dropped.
   Now scans per block.
2. `location_said.py` had an ordering bug: it excused a substitution whenever the caller said that
   place anywhere in the call. The tester personas **repeat proper nouns back** to record what they
   heard — so the bot said साहिबाबाद, the caller echoed साहिबाबाद, and the exemption that exists for
   `af627b9d` (where the caller genuinely named her own city first) fired on the bot's own mistake.
   It now looks only at caller turns BEFORE the sentence. Self-test 10/10.

**With that fixed, today's location numbers are worse than I reported.** Of the 15 calls on 2026-09-08
where the sentence was spoken, across both the 219k prompt and the 69k rewrite:

| outcome | n | calls |
|---|---|---|
| OK | 8 | |
| **SUBSTITUTED — a different place named** | **5** | `1450f797`, `8eb83bc2`, `ea0477f4`, `f90a0b97`, `fa9a16c0` |
| RAW — the written value spoken as-is | 2 | `7b841e6b`, `a5ba6894` |

**Seven of fifteen wrong, and substitution is now the dominant mode.** Nearly half of these callers
were told something false about their own location.

**Sharper mechanism, and it is not "two competing instructions".** Four of the five substitutions
named **साहिबाबाद** and one गाज़ियाबाद — **both are entries in the prompt's own Canonical Location
Spellings list.** The conversion step says *"Use Canonical Location Spellings for a place on that
list; a place NOT on the list is converted exactly the same way"*, with the list immediately below.
List-membership becomes the salient operation and an off-list value gets mapped **to** a member. The
list is being read as a menu of places to choose from rather than a spelling table for names you
already have.

That predicts the failure recurs for any locality outside the list, at any prompt size — which is
what five calls across two prompts show. One more prompt-only thing is therefore worth trying before
the upstream field, and it is not another wording of the same guard: **say that the list is a spelling
table and never a menu — if a value is not on it you still say that value, never a list member.**
Queued as the next experiment on the slim A/B bot, not applied to live traffic.

### 2026-09-08 (evening) — payload company names spoken in Latin on BOTH prompts; the ordinal counter fails 58% of the time

**Found by the A/B harness, not reported.** Ten calls, five on the 219k prompt and five on the 69k
rewrite, same fixture and persona.

**1 — `[company]` and `[role]` were being read out of the payload in Latin, on both prompts.**
`ea0477f4` (fat) did it **five times in one call** — "मार्केटिंग, **SARA ENTERPRISES** में", "एक और
option है — फील्ड मार्केटिंग एग्जीक्यूटिव, **BayLink**", "टेली मार्केटिंग फीमेल, **GLOBAL CHEMICALS**".
Slim's `90658584` did it three times and `f90a0b97` spoke a salary in digits.

I first recorded this as a regression caused by the rewrite, because slim did it and fat had got it
right on `02c5f7f0`. **That was wrong and is corrected here:** `ea0477f4` is the fat prompt, on the
same fixture, failing worse. It is a shared bug.

**Root cause (D71 again).** The Devanagari-only rule is stated FIVE times in these prompts — the
Script Output Rule, the English-origin-words section, Named entities, Canonical Location Spellings,
and the location step — and in none of those places is it stated at **the line that consumes these
values**, which is the job-presentation format. That format says only "Speak the company name
([company]) for each option where present".

**Change:** the conversion is now stated at the point of use, inside the step-2 rules and the
deep-dive rules, with the exact values that failed worked through — "GLOBAL CHEMICALS" → "ग्लोबल
केमिकल्स", "SARA ENTERPRISES" → "सारा एंटरप्राइज़ेज़", "BayLink" → "बेलिंक", "QUESS CORP LTD." → "क्वेस
कॉर्प" — plus the off-list clause. 12 KKB/Maya prompts (Kannada twins in Kannada script) and the slim
prompt. Heading parity intact on all four language pairs. All deployed. `fix_presence` row
`company-converted-at-point-of-use`, 12 bots. **DEPLOYED, NOT VERIFIED** — a re-dial of both bots on
the same fixture is in flight.

**2 — the ordinal running count restarts on 58% of the calls that reach a second batch.** Counted
first, over 1,675 cached calls: 82 spoke an ordinal, 24 got past one batch, and **14 of those 24
restarted at पहला**. `5a1c0c77` ran पहला दूसरा तीसरा four times over. It happens inbound and
outbound, Hindi and Kannada, and on both the 219k and the 69k prompt in the same A/B run
(`09978532`, `4d6d4d02`).

The rule is already unambiguous — *"Ordinals run continuously across batches and NEVER restart"* —
so this is not a clarity problem. It asks the model to carry a counter across an unbounded number of
turns, and it cannot: unlike the positional rules that DO hold ("this line may only appear in a turn
containing a fresh apply_job result", checkable against the turn being composed), an ordinal that
depends on what was said three turns ago cannot be self-checked at the moment of speaking.

**No third wording was written** (analyser **D76**). The fix is to remove the cross-turn state, and
that changes spoken output, so it is an owner decision: either drop the numbering on later batches
and let selection happen by role and company — which the phonetic-confirmation rules already cover —
or make the numbering explicitly per-batch and re-anchor selection on the name. **The experiment
belongs on the slim A/B bot first**, which is what it is for.

### 2026-09-08 (evening) — the end-of-call read-back is VERIFIED, and the location numbers corrected

**Read-back: PROVEN on `08a8ff4f`** (2026-09-08 06:53 UTC, `maya-hi-signals`, post-deploy). Six
earlier attempts never reached the end of the flow. This one did, on real campaign traffic:

> "एक बार confirm कर लूँ — आपका नाम आर्यन, उम्र बाईस, पुरुष, एरिया साहिबाबाद — सब सही?"

It fired after a successful `apply_job`, after the service-provider offer was answered, which is
exactly the ordering the 2026-09-07 fix put in place — and it is the Phase-2-had-nothing case the
old trigger silently skipped. **Khushboo's r4 item 2 is closed.**
**One gap in it:** the template says to cover name, age, gender, role, qualification and area; this
call read name, age, gender and area and omitted **role and qualification**. Partial, so the
labelled-fields half of that rule is still unproven.

**Correction to this morning's location figures.** I reported "42% of location sentences wrong". That
number was inflated by a false positive in my own new detector: it looked for the two-slot sentence
on every KKB/Maya bot, but only the two KKB Signals prompts contain it — Maya and the KKB
outbound/inbound prompts ask about the area in their own words. Three calls (`08a8ff4f`,
`78ef362f`, `1b7fb500`) were reported as failures for not saying a sentence their prompt does not
have. `location_said.py` now reads its scope from the prompt files.

**Corrected, over 463 calls since 2026-09-01, on the 30 where the sentence was in play:**

| outcome | n | |
|---|---|---|
| OK — the argument's place words, converted | 19 | |
| ABSENT — jobs presented, sentence never spoken | 7 | **all seven are 2026-09-04, i.e. before the Step-2 gate** |
| RAW — the written value spoken as-is | 3 | `a899617e`, `7b841e6b` (both pre-fix), `a5ba6894` (post) |
| SUBSTITUTED — a different place named | 1 | `1450f797` (post) |

**So the two fixes have opposite verdicts, and I had them backwards this morning:**
- **The Step-2 location gate WORKS.** Seven skipped-sentence calls, every one before the gate
  shipped, none after. That closes Khushboo's r4 item 1.
- **The digit/script conversion does NOT.** One RAW and one SUBSTITUTED after it shipped. Retained
  as retracted; see the earlier entry today and `ESCALATION-data-team.md` §5.

**The same failure occurs on the 68k slim prompt** (`8eb83bc2` spoke साहिबाबाद for
`location: "Sarjapur, 110045"`) at the same rate as on the 219k one, so it is not caused by the
surrounding prose and shrinking the prompt cannot fix it. That is the strongest argument yet for the
upstream `location_spoken` field.

**New standing detector:** `raya/regression/location_said.py` — classifies the sentence as OK / RAW /
SUBSTITUTED / ABSENT / NA, scopes itself to the prompts that contain it, and self-tests 9/9 against
the real calls above, including `af627b9d`, where the caller named Bengaluru herself and it must NOT
be counted as a substitution.

### 2026-09-08 (later the same day) — RETRACTION: the location-sentence fix is NOT holding, and the slot is not prose-fixable

**I reported the PIN/Latin location fix as proven earlier today. That was premature.** Two calls
placed AFTER the 12:16 IST deploy show it failing in **both** directions, and a third pre-fix
wording had already failed, so this guard has now failed three times with three different wordings.

| call | UTC | `location` argument | what the bot said | failure |
|---|---|---|---|---|
| `a5ba6894` | 08:56 | `10987, Sarhanpur` | "लोकेशन **10987, Sarhanpur** है" | raw passthrough — digits AND Latin |
| `1450f797` | 12:34 | `Sarjapur, 110045` | "लोकेशन **गाज़ियाबाद** है" | substituted a DIFFERENT place — the jobs' city |

`1450f797` is the worse of the two. The sentence became "your job location is गाज़ियाबाद, and the
jobs are in गाज़ियाबाद, वसुंधरा and ग्रेटर नोएडा" — which is not merely ugly, it **hides the mismatch
the sentence exists to expose**: the caller was dialled about Sarjapur and never heard that.

**Root cause — two instructions on one slot, and the model can only obey one.** The block says both:
1. *"The first slot is the LITERAL TOKEN `${location}` … the platform substitutes it before you ever
   read this line — there is no resolution step and no opportunity to prefer the fetched profile."*
   (Added because SIX calls had resolved the slot to the profile's stored city.)
2. *"`${location}` arrives as a WRITTEN value … convert it FIRST — drop every digit, then write it in
   Devanagari."* (Added this morning for the PIN and Latin leaks.)

Rule 1 says the text in front of you is already correct and there is nothing to do. Rule 2 says
transform it. **Obeying 1 produces `a5ba6894`. Attempting 2 — "I must end up with a Devanagari place
name" — produces `1450f797`, because the nearest Devanagari place to hand is the jobs' city.** The
`10987, Sarhanpur` shape also sits outside every row of the worked table (digits FIRST, no city),
which is the same closed-list boundary as D71 one level down: the table taught place-then-PIN.

**No fourth wording was written.** CLAUDE.md forbids a third wording of a guard that has failed
twice, and this is the third failure. Escalated instead (see `ESCALATION-data-team.md` §5), with the
two mechanisms that would actually end it:

- **(a) Upstream, preferred.** Send a second argument — `location_spoken` — already stripped of
  digits and already in Devanagari, and let the prompt do the one thing it does reliably: read a
  substituted token verbatim. Rule 1 works; it is rule 2 that cannot be made to work in prose.
- **(b) Prompt-only fallback, an OWNER decision.** Drop the caller-place slot from the sentence and
  speak only the jobs' cities, which are read off array fields and have never been misread. That
  removes both failure modes at the cost of no longer confirming the caller's area aloud — which the
  prompt itself argues is worth having.

**Not applied to the A/B slim prompt either, deliberately** — changing this behaviour in the slim
bot would confound the size comparison with a behaviour change.

**Also found in the same sweep, both POST-deploy, both forbidden by the prompt already:**
- **The introduction was spoken TWICE** on `1450f797` and `9b844751` — the prompt's intro rules say
  it is "spoken ONCE per call and is NEVER repeated". 2 of the 8 scored calls.
- `1450f797` also bundled the location sentence and a job sentence into one turn, breaking the
  one-question-per-turn rule that the location block states twice.

**Honest status of this morning's work, per fix:**

| fix | status |
|---|---|
| Latin `Qualification:` label → `क्वालिफिकेशन:` | deployed; no post-deploy call has reached a deep dive yet — **NOT VERIFIED** |
| off-list branch in `## Named entities` | deployed — **NOT VERIFIED** |
| Maya sample tokens / `VMLG` | deployed — **NOT VERIFIED** |
| qualification-is-not-a-role | deployed — **NOT VERIFIED**, and the reported call was never located |
| DKB absent-`company_name` | deployed — **NOT VERIFIED** |
| location digits + script | **FAILING post-deploy — see above.** Retracted |

### 2026-09-08 — Khushboo r5: a stored value read out in its written form (four bugs, one mechanism)

**Reported.** (1) QA call **5035574**, KKB Hindi Signals: *"Bot is reading out the exact written
letters/words"* — "एक मिनट। सत्यजीत जी, आप अभी **बी०टेक०(ई०सी०एस)** का काम कर रहे हैं — क्या आप अभी भी
बी०टेक०(ई०सी०एस) की जॉब देख रहे हैं?" (2) QA call **5061404** = live `7b841e6b` (2026-09-08 06:19 UTC):
the PIN fix and the latency complaint *"not fixed, please check again"*.

**Root cause — one mechanism behind all of it, and it is not flakiness.** Every script/spelling rule
in these prompts is backed by a **closed list**. A value on the relevant list is converted; a value
absent from every list is emitted verbatim. Counted first (CLAUDE.md ladder rung 0): of the ten
location sentences spoken on `kkb-hi-signals` since 2026-09-04, the five spoken AFTER the 2026-09-07
PIN fix whose `${location}` was `"Muradnagar, 110045"` were all correct — PIN dropped, Devanagari —
and the one whose value was `"Sarjapur, 110045"` was passed straight through, Latin script and PIN
intact. Muradnagar is on Canonical Location Spellings. Sarjapur is not. Same prompt, same rule,
deterministic split. Three more instances of the same boundary, found while measuring:

| call | argument | what the caller heard | list it was off |
|---|---|---|---|
| `7b841e6b` | `location: "Sarjapur, 110045"` | "लोकेशन **Sarjapur, 110045** है" | Canonical Location Spellings |
| `1536830c` | `company: "SARA ENTERPRISES"` | "मार्केटिंग, **SARA ENTERPRISES** में" | no company list exists |
| `9d5e9848` | `company: "MAHARAJA ENGINEERING WORKS"` | said verbatim, plus "**Qualification:**" | no company list; the label is the prompt's own |
| `b6353cfb` | `college_name: "VMLG College"` | "मैं माया, **VMLG College** की ओर से" | Maya "Common conversions" (had LR, TPS, MMH) |

On each of those calls a value that WAS on a list came out right in the same breath — `7b841e6b`
said गाज़ियाबाद, `02c5f7f0` said "ग्लोबल केमिकल्स" out of `GLOBAL CHEMICALS`. So the rules were being
obeyed; everything outside the lists was not covered by them.

**Changes.**
- **The location sentence (2 KKB Signals prompts).** The paragraph opened with *"**Say the sentence as
  it arrives** — but speak only the PLACE WORDS in it"*: a pass-through permission first, the
  transformation as a caveat, and the Devanagari instruction eight lines later at the tail of the
  paragraph. The permission is **deleted** (ladder rung 3 — remove the wrong option, do not forbid the
  output) and replaced by an ordered precondition: *"a written value is not sayable. Convert it FIRST
  — drop every digit, then write it in Devanagari — and only then say the sentence."* An off-list place
  is stated in bold to be the ordinary case, not an exemption, and there is a four-row worked table
  including `Sarjapur, 110045` → सरजापुर.
- **The off-list branch (8 KKB + 4 Maya prompts).** `## Named entities` now says every list in the
  prompt is examples, never an allow-list, with the four failing values worked through. Maya's
  "Common conversions" gained `VMLG` and `VTU` — checked against production, `college_name` is
  **`VMLG College` on 345 of 460 cached campaign calls** and `LR College` on 111, so the value the
  majority of Maya's callers hear was the one on no list.
- **Maya's samples were teaching the pass-through (D74).** Both worked examples in Maya Hindi and Maya
  Hindi Signals read `> **Agent:** नमस्ते। मैं माया, **${college_name}** की ओर से…` — the agent
  demonstrated speaking the raw token — and their Context line was the tautology
  `**Context:** ${college_name} = ${college_name}.`, which establishes no value at all. Four rules said
  convert; two demonstrations said copy. The samples now use `LR College` → "एलआर कॉलेज" with a stage
  direction naming the substitution.
- **The Latin field label (8 Hindi prompts, 31 occurrences).** `Qualification: [qualification]।` sat
  inside the Step-3 spoken template and 3-5 sample conversations per file demonstrated saying it. The
  bot was reading the template correctly. Now `क्वालिफिकेशन:` — which is what the **Kannada twins
  already had** (`ಕ್ವಾಲಿಫಿಕೇಷನ್:`), so the Hindi files were behind their own mirrors.
- **A qualification is not a role (12 KKB/Maya prompts).** The role-usability closed set read *"a real
  trade — NOT 'Any', 'Not Available', empty, null, or garbled"*. `B.Tech(ECS)` is a well-formed,
  ungarbled string and none of those things, so every arm of the set said it was a usable role and the
  bot told the caller she currently *works as* a degree. Both enumerations in each file now carry the
  branch, routing to the existing UNKNOWN path (Step 1 Case B), with the counter-case spelled out: a
  job title that merely mentions a qualification ("Diploma Engineer", "B.Tech Trainee") IS a trade.

**Complaint 3, latency — measured this time, and it is not the prompt.** `hold_message` is supplied
on essentially every tool call and **is never played while the tool runs**: across **1,152 calls on all
18 bots, 348 of 348** tool calls carrying a `hold_message` had **no audio at all** between the tool
call and the tool result, and on the Signals subset the hold text instead appears at the START of the
assistant turn *after* the result (208 of 217). So the caller gets silence for the whole round-trip and
then hears "एक मिनट।" once the wait is already over. 189 of those silent round-trips are `get_profile`,
which fires at the top of every call — exactly where Khushboo reports the latency being "prominent...
at the start". This is a runtime behaviour, not a prose problem; escalated with the counts and call
ids. (Corroboration that the belief was already wrong: `DKB Hindi Signals` documents `hold_message`
must stay an EMPTY string because "the platform SPEAKS whatever is in it" — someone had noticed the
stray utterance and worked around it.)

**Files:** 16 conversation prompts — 8 KKB, 4 Maya, 4 DKB (see `Maya/CHANGELOG.md` and
`DKB/CHANGELOG.md` for their halves). All 16 deployed and read-back verified.

**Analyser:** new patterns **D71** (closed-list script rule), **D72** (field label spoken),
**D73** (emptiness test missing the absent-argument case), **D74** (a sample whose context defines a
variable tautologically and whose speech line shows the token). New standing detector
`raya/regression/spoken_form.py` (12/12 self-test, including two rows that exist because the FIRST
version of that detector allow-listed "not" and "available" and so passed the DKB placeholder bug
clean). Six new `fix_presence.py` rows; 22/22 present.

**Verification status.**
- **PROVEN:** _(pending — see below)_
- **DEPLOYED, NOT VERIFIED:** the location conversion on an off-list value, the off-list branch, the
  Maya sample fix, the qualification label, and the qualification-is-not-a-role branch. Fixtures are
  committed: `raya/testcases/args/r5/sarjapur-offlist.json` (Khushboo's exact failing value plus the
  12-job payload that also carries `SARA ENTERPRISES` and `MAHARAJA ENGINEERING WORKS`),
  `maya-vmlg-offlist.json` (the 345-call `VMLG College` value), `dkb-no-company-name.json`. Persona
  `raya/personas/hi-detail-then-apply.md` drives the deep dive so the company name and the
  qualification line are both spoken. First dial `23af46f3` reached the bot leg (dur=60, outcome
  Completed) with an **empty transcript** — the tester DID did not bridge.
- **NO REPRO for the reported call:** 5035574 could not be located through the Raya API. 1,675 calls
  were scanned across all 21 registered targets (400-deep on `kkb-hi-signals` and `maya-hi-signals`);
  no transcript contains the utterance, and of the 37 distinct profile `role` values seen, **none is a
  degree**. Raya lists **85** agents against the 21 in `raya/agents.json`, so the call is most likely
  on an unregistered agent. The prompt gap is real and verifiable statically, so the branch was added
  — but the reproducing call id is still needed to close it.

### 2026-09-07 — Khushboo r4: PIN read aloud as a quantity, location turn skipped, end-of-call read-back missing

**Reported (calls 5053389 = `8674462f`, 5054799 = `a899617e`, both `kkb-hi-signals`, both
`location: "Muradnagar, 110045"`):** (1) location not being asked; (2) at the end the bot used to
reiterate the details and ask the nearby location and didn't; (3) prominent latency after each turn at
the start. Second call: the location WAS asked but the PIN was spoken as a number.

- **Root cause 1 — the PIN.** `## Numbers` says "do not write digits in spoken Hindi output, write them
  in words" with cardinal examples; `## Phone number` had its own digit-by-digit exception; **a PIN code
  had no rule at all**, so it fell to the cardinal default and `११००४५` came out as a quantity. Behind
  that, the LOCATION SENTENCE deliberately says to speak `${location}` exactly as it arrives (that
  instruction fixed six calls that had resolved the slot to the profile's city instead), so the PIN was
  pushed through on purpose.
  **Fix:** the location sentence now speaks only the PLACE WORDS in `${location}` — every digit dropped,
  no PIN, no plot/house number — stated as a formatting reduction of the given value, not permission to
  choose a different place. Plus a new `## PIN / postal codes` section: an identifier is spoken digit by
  digit like a phone number, never as a quantity, and preferably not spoken at all.
  **Verified `36802370`:** "हमारे पास आपकी जॉब की लोकेशन **मुराद नगर** है" with
  `location: "Muradnagar, 110045"` in the arguments — no PIN spoken.
- **Root cause 2 — the location turn was optional on one path.** Case B carried a hard
  "**the location turn happens once per call on EVERY path** … do not skip"; **Case A had only a
  pointer** — "→ Then run the Location step below". `8674462f` took Case A (role confirmed off the
  profile), went role-confirm straight to jobs and never mentioned the location; `a899617e` twenty
  minutes later, same bot and same arguments, did say it. Same prompt, opposite behaviour — a missing
  gate, not model whim.
  **Fix:** a GATE at the top of **Step 2**, the chokepoint both paths must cross: no job may be named
  until the location sentence has been spoken this call (or deliberately skipped because
  `${contact_memory}` shows it was confirmed on an earlier call). Placed there rather than as a second
  copy of the rule in Case A.
  **Verified `36802370`, `6fe05a86`, `1536830c`:** location sentence spoken before any job on all three.
- **Root cause 3 — the end-of-call read-back was conditional on Phase 2 having work to do.** The rule
  read "*after the Phase-2 fields are captured*, read back ALL the details". Every Phase-2 question is
  "only if missing", and granular location is explicitly skipped when the location turn already captured
  an area — so on a caller whose profile is complete, Phase 2 asks nothing, nothing is "captured", and
  the read-back never fires. That is what Khushboo lost: the read-back is also the only place a stale
  stored location gets corrected (her profile says `Bengaluru, Karnataka, India`).
  **Fix:** the read-back now triggers after a SUCCESSFUL apply **whether or not Phase 2 had a single
  question to ask**, in all six Signals prompts. Also, Need Capture's reply routing no longer sends the
  call to Graceful Exit when an apply succeeded and Post-Application Info Gathering has not run.
  **DEPLOYED, NOT VERIFIED** — see below.
- **Found while testing, not reported: the no-match line named the profile's stale city.** The mandated
  line is "[role] की जॉब अभी नहीं है — लेकिन [kind], [kind] जैसी जॉब्स हैं" and **neither slot is a place**.
  On `6fe05a86` the bot composed its own sentence instead: **"अभी बेंगलुरु के लिए डेटा एंट्री या कंप्यूटर
  ऑपरेटर की जॉब्स उपलब्ध नहीं हैं"** — twice — where बेंगलुरु came off the fetched profile, minutes after
  it had correctly confirmed मुराद नगर and told the caller the jobs are in गाज़ियाबाद. Whether a role is
  in `${recommendations}` has nothing to do with the caller's city. **Fix:** that line's rules now state
  that neither slot is a place and no city may be added to it; the only places nameable aloud are the
  jobs' own cities in Step 2.
- **Complaint 3 (latency) — not reproducible or measurable from here, and not caused by the recent
  edits.** The Raya call API exposes only `call_start_time` / `call_end_time` / `call_duration`; the
  transcript turns carry no timestamps, so per-turn latency cannot be measured. What is measurable: the
  prompt is **239,932 bytes** now against **236,190** before the 2026-09-04 work (+1.6%), so the recent
  changes are not a step change. A 240 KB instruction set is re-read every turn and that is a chronic
  cost — the lever is consolidating the accumulated guard prose, which is real work and not a one-line
  fix. Flagged, not attempted.
- **Files:** the 4 KKB outbound prompts (PIN rule), the 2 KKB Signals prompts (Step-2 gate, digit-stripped
  location, no-place no-match clause), and all 6 Signals prompts + Need Capture routing in 12
  KKB/Maya prompts (read-back trigger).
- **Verification status, honestly:** the PIN fix and the location gate are proven by call ids above. The
  read-back / Phase-2 ordering is **NOT** proven. Three attempts (`36802370`, `6fe05a86`, `1536830c`)
  each failed to reach the end of the flow: the tester agent is capped at 5 minutes and the persona
  spent it, and the third call's apply returned `ACTION_LIMIT_REACHED` so the success-only path was
  unreachable. That needs either a real call or a persona that reaches apply inside two minutes.
- **Test-number hygiene finding:** `get_profile` on the tester DID now returns **five** `profile_1.0`
  seeker items (`588a907f`, `5822b168`, `2557ed02`, `0ee9e95a`, `0b84429b`). Duplicate profiles are
  accumulating on the test number, which makes `profile_id` selection ambiguous and makes
  `ACTION_LIMIT_REACHED` depend on which profile the apply happened to use. Worth a clean-up before the
  next test round.

### 2026-09-04 — Tracker sweep: row-1 already-applied was UNREACHABLE (row 103); inbound Example 2 demonstrated the open area ask (rows 106/108)

- **Feedback/bug:** Tracker `All Issues` review. Row 103 (KKB Hindi Signals, P1) "bot is saying
  technical issue instead of already applied". Rows 106/107 (KKB Inbound Signals, P1) location and
  consent — the location half recurred on live traffic AFTER the 2026-09-04 fix was called verified
  (`b48f70fb`, `2d8b7cb1`, both post-deploy).
- **Root cause (row 103) — two competing instructions, both added by earlier fixes.** Counted first
  (CLAUDE.md ladder rung 0): of 60 `apply_job` calls returning `ACTION_LIMIT_REACHED` across
  2026-09-03/04, **45 spoke the technical-issue line, 5 spoke an already-applied line, 10 spoke
  neither** — and after 2026-09-03 11:10 UTC it was **0 for 11**. Two causes:
  (a) commit `feb9405`'s evidence gate listed only two admissible kinds of evidence and then said
  "**Nothing else counts** … If neither 1 nor 2 holds, row 1 is FORBIDDEN" — omitting the error-text
  condition that the whole mapping depends on (analyser **D62**);
  (b) the THREE-DISTINCT-OUTCOMES table routed `duplicate_check: "not-applied-before"` + any error
  to row 2 unconditionally, "never by guessing at the error" — which also stopped it READING an
  error that names its own reason.
- **Change (row 103): ATTEMPTED, TESTED, AND REVERTED — the prompt is unchanged.** Both edits were
  made (item 3 added to the evidence list with the "neither 1 nor 2" arithmetic corrected; the table's
  error row split so a named `ACTION_LIMIT_REACHED` routed to row 1), deployed to all 12 bots, and
  tested. **They did not work and one of them regressed.** Harness call `row103-hi-postfix` (tester leg
  `ae2481e6`): `apply_job` returned `ACTION_LIMIT_REACHED` with the message "An active request already
  exists between these two profiles" and the bot still spoke the technical line. Then, on Kannada
  inbound `5f0d3671`, the error was `USER_NOT_FOUND` — nothing to do with duplicates — and the bot
  said **"your application for this job already exists"**: making row 1 reachable via a condition the
  model cannot evaluate simply moved the failure from "technical issue on a real duplicate" to
  "already applied on an unrelated error", which is the `c5a10922` harm the evidence gate exists to
  prevent. Both edits were reverted and all 12 bots redeployed to the pre-edit text; live read-back
  confirms the reverted content.
- **Row 103 is not prose-fixable — measured, not inferred.** Across all six Signals bots,
  2026-09-01→04, **133 tool errors carried a named `error` field and not one produced a line that
  distinguishes one error class from another**: `ACTION_LIMIT_REACHED` (95), `TARGET_ITEM_NOT_FOUND`
  (20), `MINOR_ACTION_CHANNEL_BLOCKED` (13), `SOURCE_ITEM_NOT_FOUND` (2), `INVALID_ITEM_STATE` (2),
  `PROFILE_LIMIT_REACHED` (1) — all the same generic failure line. Over the same window the model
  demonstrably reads *successful* tool results (it speaks names, roles and locations out of
  `get_profile` on every call), so the reason is not being ignored: it is not in what the model
  receives. Row 2's own definition — "an error with no reason you can read" — is therefore the correct
  branch on every failure, and the already-applied branch is unreachable by construction. Escalated in
  `raya/overnight/ESCALATION-litwiz.md` §2 with the table and the call ids; the only in-product path is
  richer `contact_memory.jobs_applied` (or an applications list on `get_profile`) so the PRE-tool
  duplicate check can match, which is the only route that has ever produced the line correctly.
- **Root cause (rows 106/108) — the sample outvoted the rule (analyser D63).** Every inbound prompt's
  *Example 2* is a returning caller whose fetched profile is described as carrying name, role, age and
  gender but **not** location, and its area turn shows the OPEN ask. The confirm-first rule (D61) is
  stated twice above it; the worked example is the thing the model followed.
- **Change (rows 106/108):** gave Example 2's fetched profile a location in all six inbound prompts and
  changed its area turn to the confirm line, with a stage direction naming the branch; mirrored the
  Hindi three-branch Case A structure to the two Kannada and two Maya inbound prompts (they still
  printed the open ask as a standalone script line under the rule — the exact shape D61 fixed); and
  added, to the confirm branch, that only the town/city part of a stored location is spoken — never a
  full postal address (`b48f70fb` carried `VILL-MURARI TAND KAKO, PO-BHADSARA,…PIN-804418`).
- **Files:** all 8 KKB conversation prompts (row-103 fix) and the 4 KKB inbound prompts (Example 2 +
  Case A + postal-address clause). `raya/regression/consent_before_apply.py` (the Kannada consent
  wording `ಪರ್ಸನಲ್ ಡೀಟೇಲ್ಸ್ ಕಂಪನಿ ಜೊತೆ ಶೇರ್` was missing from `SHARE`, producing a false CONSENT AFTER
  APPLY on `a5547492`; also now checks the earliest apply rather than comparing the first apply to a
  later consent line). Analyser: **D62**, **D63**.
- **Also fixed (found by this testing, not reported): `apply_job` sent `acting_as_user_id` equal to
  `profile_id`.** On `5f0d3671` the mandatory silent `get_profile` did not run — remembered context
  supplied the caller's name and profile id — and the model filled `acting_as_user_id` with the
  profile id, giving `USER_NOT_FOUND` and a lost application. The prose already said the two ids are
  distinct in eight places, so this went into the **tool schema** instead (escalation ladder rung 4):
  `apply_job`'s `acting_as_user_id` description on all six Signals bots now states that the value is
  the response's TOP-LEVEL `user_id`, is NEVER equal to `profile_id`, must be checked against it
  before the call is emitted, and does not exist at all unless a `get_profile`/`create_profile` result
  was seen in THIS call. `toolschema_parity.py` clean across all 12 bots.
  **Verified:** `537549c6` — `get_profile` ran, and `apply_job` sent `acting_as_user_id c3fc8471…`
  against `profile_id ffce36d8…`; no `USER_NOT_FOUND`.
- **Verification (per fix, with call ids):**
  - inbound location confirm, Hindi — `8235309e` ("आप गाज़ियाबाद के आसपास ही देखें?" on a Case-B call
    whose profile held `Vasundhara, Ghaziabad, India`; no open ask anywhere in the call).
  - inbound location confirm, Kannada — `537549c6` (confirmed Koramangala from the profile).
  - `acting_as_user_id` — `537549c6` (see above).
  - row 103 — **NOT FIXED, reverted, escalated.** `ae2481e6`/`row103-hi-postfix` and `5f0d3671`.
  - still open on the same platform gap: `537549c6`'s SECOND apply guessed the already-applied line on
    a different job's `ACTION_LIMIT_REACHED` with no evidence for it. Same root cause, both directions.

### 2026-09-01 — Khushboo r3: the location reconfirm was structurally unreachable; the already-applied line is NOT prose-fixable (proven); Muradnagar canonical

**Reported (WhatsApp, call ref 4989329 → live calls `5c67bd19` 07:16 and `90da81db` 07:50, both to XXXXXX6073):**
(1) "Location is not been confirmed — it asked where do you want to work despite giving proper input variable",
and no nearest-station/landmark probe was heard. (2) "It is still resorting to same fallback for already applied
jobs — technical issue, noted etc." (3) "Murad nagar pronunciation is wrong (add in the canonical section)."
(4) Kannada test jobs needed.

**Root cause 1 — the location reconfirmation could not be reached on the path both her calls took (analyser D51/D53).**
`#### Location state`, which holds the reconfirmation, the mismatch handling and the ladder, was nested INSIDE
`### Case A — you already know the target role`. Both of her calls went down **Case B** (the fetched profile's role
was the placeholder `Any` → treated as UNKNOWN), and Case B held only a *pointer* to "the Location reconfirmation
from Case A" while quoting the open UNKNOWN area lines inline. Standing in Case B, the model took the line that was
in front of it. Second contributor: the KNOWN branch had no state for **"known, but no job is in that place"** —
her input was `Delhi` and all 8 jobs were Ghaziabad — so the reconfirmation collided with the Hallucination Guard
(never name a place we hold no job in) and lost. That produced two *different* wrong behaviours on identical args:
`5c67bd19` asserted "आपके लिए दिल्ली में कुछ जॉब्स हैं" (false — no Delhi jobs), `90da81db` ignored the input and asked
openly. Third contributor: `Location precedence` ranked the fetched profile's `item_state.location` (a stale
`Bengaluru, Karnataka, India`) ABOVE the per-call campaign input, so the closing read-back told her "एरिया बेंगलुरु".
The station/landmark rungs correctly did NOT fire — they are rung 3 of a bounded ladder, reached only when the word
itself is unusable, and her city resolved fine.

**Root cause 2 — the "already applied" line is NOT reachable from the tool error, and now proven so (analyser D52).**
Scanned every `ACTION_LIMIT_REACHED` call across the fleet: **8 of 8** spoke the generic line, **0** spoke the
explicit one — `kkb-hi-signals` (`90da81db`, `21c428dc`, `dc3168ec`), `kkb-kn-signals` (`18b5e1b8`),
`kkb-kn-in-signals` (`d824912c`), `maya-hi-signals` (`96e72c85`, `9d82ac2c`, `3be8d3fb`) — including three calls
made AFTER the branch had been restructured into an explicit lookup table. Then the decisive test: the error→line
mapping was also put into the `apply_job` **tool description** (read at the moment of use, `scripts/raya_tooldesc.py`)
and live call `14f90f64` hit `ACTION_LIMIT_REACHED` and STILL spoke the generic line — **9 of 9**. This closes the
open question from 2026-08-25: the conversation model does **not** receive the HTTP error body; the
`__RAYA_TOOL_DEBUG__` block carrying `ACTION_LIMIT_REACHED` is not visible to it. Every prose iteration was
branching on a string that never arrives.

**Change — location (kkb-hi-signals only, registered divergence `kkb-hi-signals-location-capture`):**
- **Promoted** `Location state` out of Case A to a sibling `###` section that both paths must pass through, retitled
  "the ONE area turn, and it governs BOTH Case A and Case B". Case A and Case B now each hand off to it and hold no
  area wording of their own.
- **Removed the competing option:** Case B's inline open-ask bullets are gone; the block states that when the
  location is KNOWN the open UNKNOWN lines are **not available**, and that the turn is ONE question, its own turn,
  never appended to the pool-overview question with a "साथ ही…" clause (observed on `0decf61a`).
- **New third location state — LOCATION MISMATCH,** with its own mandatory truthful line naming both places:
  "आपके लिए [जगह] में अभी कोई जॉब नहीं है — जो जॉब्स हैं वो [शहर] में हैं। [शहर] में देखना चलेगा?" — plus the explicit note that
  this branch is what the Hallucination Guard REQUIRES, and that the plain reconfirmation is not an inventory claim.
- **Location precedence reordered:** caller's own words → **the location input** → the fetched profile's
  `item_state.location` → UNKNOWN, with the reason stated (the profile field is where they LIVE and goes stale).
- **`KKB Output.md`:** new `15c. input_location_had_jobs` (Yes/No/NA) so a campaign dialling a city we hold no
  inventory in shows up in reporting instead of in a QA message. Deployed to `kkb-hi-signals`'s `output_instructions`.

**Change — already applied (all 12 KKB/Maya conversation prompts):**
- **New `## Already applied — check BEFORE you call the tool`** in `apply_job Tool Call Rules`: derive the duplicate
  from what the bot actually HAS — this call's own `apply_job` history, and `jobs_applied` in `${contact_memory}`
  (matched on role + company, suffixes ignored) — say the explicit line, and do not call the tool at all. This is
  the only route to the line that does not depend on the invisible error string.
- **Restructured `Apply Failure Handling`** in the 11 prompts that had not yet had it: the two labelled cases become
  a two-row lookup keyed on *what you know*; the **false cause-claim is deleted entirely** in both languages
  (`"अभी हमारी तरफ़ से apply complete नहीं हो पाया — कोई तकनीकी दिक्कत है…"` and
  `"ಇನ್ನೂ ನಮ್ಮ ಕಡೆಯಿಂದ apply complete ಆಗಿಲ್ಲ — ಸ್ವಲ್ಪ technical ತೊಂದರೆ ಇದೆ…"`), replaced by lines that assert nothing
  (`"अभी इस जॉब में अप्लाई पूरा नहीं हो पाया…"` / `"ಈ ಜಾಬ್‌ಗೆ ಅಪ್ಲೈ ಇನ್ನೂ ಪೂರ್ತಿ ಆಗಿಲ್ಲ…"`). The
  second-consecutive-failure acknowledgement lost its cause-claim too.
- **Fixed two dangling labels** (analyser D51): the failure section's hard ban said "say the **Case A** line" and the
  turn-composition rule said "(Case A or Case B)" — labels that no longer existed there and that mean something
  ELSE in Step 1. The ban was inert, which is why the section's default line won every time.

**Change — found by testing, not reported:**
- **`Apply Success Handling`:** the success line is now forbidden on any call where `apply_job` did not succeed, in
  the turn that answers the Need Capture offer, and anywhere later. Call `14f90f64` told the caller
  "अभी इस जॉब में अप्लाई पूरा नहीं हो पाया" and then, two turns later, "अप्लाई हो गया है" — a direct contradiction.
- **`update_profile` rules:** never narrate an update that was not made. Call `0decf61a` said
  "मैंने उम्र 26 साल अपडेट कर दी है" with no `update_profile` call in the transcript — a hallucinated write.
- **Canonical Location Spellings:** `Muradnagar → मुराद नगर` (the space is deliberate — as one word the द+न cluster
  slurs), plus `Surajpur`, `Raj Nagar` (+ District Centre / RDC), `Govindpuram`, `Kavi Nagar`, `Shipra Mall`, `NH-9`,
  all classified as Ghaziabad localities; and a rule that a `"Locality, City"` job value is spoken as the locality
  alone, with campaign junk ("/ WFH – serving Ghaziabad") never read aloud.

**Verified by live call (Tier 1):**
- **Muradnagar** — `0decf61a` (10:25 UTC): bot spoke "मुराद नगर", `call_output.company_location: "मुराद नगर"`, and the
  tester's ASR heard it back as "मुरादनगर" — i.e. the audio resolves to the right town. **Parth/Khushboo should still
  confirm by ear; a TTS pronunciation cannot be verified from a transcript.**
- **The false cause-claim is gone on kkb-hi-signals** — `14f90f64` hit `ACTION_LIMIT_REACHED` and said the
  assertion-free line, not "तकनीकी दिक्कत".
- **Gender is asked once and persisted** — `5c67bd19`: `update_profile` sent `gender: "Female"`, API returned it on
  the item. (Khushboo's "is it auto detecting?" — no; nothing is inferred.)

**DEPLOYED, NOT VERIFIED (each needs its own call id before anyone writes "fixed"):**
- the promoted `Location state` block and the LOCATION MISMATCH line — deployed 10:33 UTC, after every test call
  above; round-2 calls were still running when this entry was written
- the duplicate pre-check from `${contact_memory}` — the mechanism that has to carry item 2
- the Apply-Success suppression and the no-hallucinated-write rule
- **all 11 propagated prompts** (kkb-hi-out, kkb-kn-out, kkb-hi-in, kkb-kn-in, kkb-hi-in-signals,
  kkb-kn-in-signals, kkb-kn-signals, maya-hi-out, maya-hi-signals, maya-hi-in, maya-hi-in-signals) — deployed with
  read-back OK, **none voice-tested**. Per the recipe-for-disaster rule these are 11 separate verifications.

**Escalation to LitWiz (now justified — ladder steps 1-4 exhausted):** ask that the tool error's `error`/`message`
fields be surfaced to the conversation model, or that a distinct tool result be returned per reason. Evidence: 9/9
`ACTION_LIMIT_REACHED` calls listed above, across 3 bots / 2 languages / 2 directions / 3 prompt structures, plus
`14f90f64` with the mapping in the tool description itself.

**Files:** `KKB/KKB Placeholder Hindi Signals.md`, `KKB/KKB Output.md`, and the 11 propagated prompts listed above;
`raya/divergences.json`; `raya/tooldesc/apply_job-already-applied.txt`
**New tooling:** `scripts/raya_tooldesc.py` (patch a tool's description only, verified by read-back),
`scripts/raya_side_prompt.py` (deploy memory/output instructions, which `raya_deploy.py` cannot),
`raya/testcases/args/handover/dharwad-test-recommendations{,-8}.json` (15 / 8 live Dharwad job ids for Kannada
testing — the 4 ids in `kkb-kn-signals-4jobs.json` are from the old instance and fail `SOURCE_ITEM_NOT_FOUND`,
call `03272636`), `raya/personas/hi-loc-then-apply.md`, `raya/personas/hi-pick-data-entry-apply.md`
**Analyser:** new **D51** (dangling branch label after a restructure), **D52** (a rule branching on a tool-error
string the model never receives), **D53** (an input echo-back suppressed by a guard about something else)

### 2026-08-25 (later) — D47 follow-up: the reason branch does NOT hold at runtime (VERIFY-PENDING)
- **Status:** the Case A / Case B branch is deployed on all 12 prompts but is **NOT verified working** — it was
  ignored on two consecutive live calls. Do not treat this defect as fixed.
- **v2 change:** moved the condition onto the base-failure-line label (`**Base failure line — CASE B ONLY (say
  once):** …`) and added a matching failure-turn hard ban, on the theory that the model reads that label and
  skipped the block above it. Deployed to all 12; live agents re-verified as carrying it.
- **Result:** live call `3be8d3fb` (v1) and a second maya-hi-signals call (v2) both hit
  `ACTION_LIMIT_REACHED` on job `b7513680` and both spoke "कोई तकनीकी दिक्कत है" anyway.
- **Open question (platform, not prompt):** whether the model receives the error reason at all. The tool result
  is `[Error: apply_job request failed (HTTP 422).]` plus a `__RAYA_TOOL_DEBUG__` block; if that block is not fed
  back, `ACTION_LIMIT_REACHED` and `TARGET_ITEM_NOT_FOUND` are both just "HTTP 422" to the model and no wording
  can branch on them. Needs one diagnostic call, then a LitWiz ask — not a third prose attempt (analyser D25).
- **Files:** the same 12 KKB/Maya conversation prompts; analyser **D47** updated with the failure evidence
- **New tooling:** `raya/regression/apply_outcomes.py` — runtime check over real calls that caught both failures
  automatically. Also surfaced that `HTTP 404 — Invalid or missing profile_id` is 16 of 23 fleet apply failures
  in two days (tracker row 84).

### 2026-08-28 (later) — location capture: live results, one fix, two VERIFY-PENDING items
- **Verified firing in real calls:** the R3 reconfirmation, the R1 location capture, the R2 kind-of-work capture, and the R4 landmark rung. The bot reaches the job list, and on a caller who wanted a city we hold nothing in (`b8666aaa`) it correctly said so plainly and named real jobs instead of inventing one.
- **FIXED after live evidence:** the reconfirmation was speaking the raw Latin location — "आप Ghaziabad के आसपास…" (call `428855a5`) — because the spoken template carried the `${location}` token directly. The token is now out of the spoken line (declaration + value-surface only, 3 → 2 occurrences) and the rule requires transliteration to the canonical Devanagari form before speaking. Redeployed; `location` is still a derived `agent_arg`.
- **CONFIRMED FIXED (call `5074cf52`):** the transliteration fix holds — Latin "Ghaziabad" is no longer spoken, the canonical गाज़ियाबाद is used with no nuqta variant, the reconfirmation still fires, and localities are voiced in Devanagari with numbers as words ("वैशाली, सेक्टर बासठ, या क्रॉसिंग्स रिपब्लिक के आसपास").
- **Residual (not blocking, logged):** the model PARAPHRASES the prescribed reconfirmation rather than reading it verbatim, and its paraphrase reintroduces the masculine honorific ("काम करना चाहेंगे" to a female caller) that the authored line was deliberately built to avoid. Same adherence class as D49 — the fix is not more wording.
- **VERIFY-PENDING 1 — the exhaustion gate does not hold.** Two prose attempts both failed live: the three-part GATE inside No-Match, then the same check moved onto the sentence above the spoken line. Calls `1aa8729b` (3 supplied / 1 named) and `b8666aaa` (5 supplied / 2 named) both fired the capture + no-relevant-jobs line with stock unread. Logged as analyser **D49**; treat as runtime adherence, NOT a wording gap, and do not re-word it a third time. **This is not a regression from this change** — a caller insisting on a city with no stock already satisfied the pre-existing subjective No-Match trigger; the feature makes it easier to reach and easier to see.
- **VERIFY-PENDING 2 — the R4 middle rungs are untestable on this harness.** The slow-repeat, station and finer-probe rungs never fired because a TTS tester agent cannot mumble: asked to be unintelligible it produces silence, and the prompt correctly does not escalate on silence (`0b7a8ef0` is `*No audio*` on every turn). These need a human tester or injected garbled ASR.
- **Test-harness limits found:** `contact_phone` is listed in `agent_args` but the platform overrides it with the dialled number, so fixture profiles cannot be selected per call — every test ran against the tester DID. 11 of 25 scenarios never bridged on the first pass.
- **Unrelated severe finding, NOT from this change:** on `a31e6cd2` with `recommendations: "[]"`, the bot named a job that was never supplied, called `apply_job` with a real Ghaziabad `job_id` absent from the array, got a 201, and told the caller they had applied. `contact_memory` is platform-injected and not visible in `agent_args`; memory contamination is the likely source. Needs its own investigation.
- **Files:** `KKB/KKB Placeholder Hindi Signals.md`; analyser **D49** added

### 2026-08-31 — Two bugs from call 924e611f fixed; root cause was the file's OWN worked examples
- **Feedback/bug (Khushboo, kkb-hi-signals, call `924e611f`):** four items. Two were correct behaviour — "treated me as a new seeker" (her history is on the OLD instance; she genuinely had no Ghaziabad profile) and "didn't ask gender" (gender is deliberately Phase-2, never a Phase-1 blocker). One was campaign data, not the bot: the apply failed `TARGET_ITEM_NOT_FOUND` because `${recommendations}` arrived **truncated at exactly 1023 chars** (analyser D42, identical signature to 2026-08-10) carrying **old-instance job_ids** that do not exist on Ghaziabad — so "already applied" would have been FALSE and the technical line was correct. The remaining item was real, plus one she did not spot.
- **THE ROOT CAUSE, and it reframes three earlier failed fixes:** the question the bot spoke at turn 31 is **byte-identical, including its `ठीक है।` prefix, to three SAMPLE CONVERSATION turns** (lines 1586/1646/1750) and is NOT the instruction at line 1256. The model copied a **demonstrated turn**, not a rule. Auditing the examples found: **5 of 6 closed an engaged call with `Goodbye` and no Need Capture offer**; **3 persisted bare Devanagari localities** as `location` (`पिंपरी, फेज़ वन` / `सातपुर` / `गोविंदपुरा`), which lines 1097 and 1180 explicitly forbid; and **none** asked for the caller's city at the Phase-1 gate. The file was showing the model the violation while telling it not to. **This is why D47 and D49 each survived two prose fixes — worked examples outrank prose guards.**
- **Bug A — `create_profile.location` borrowed a JOB's city.** Caller declined her area; the profile was written with `Bengaluru, Karnataka, India`, the work city of a job in the payload. Fixed with six levers, only one of which is prose: the `${recommendations}.location` gloss relabelled (it read "work location or city", near-synonymous with the caller field); a city-vs-locality resolution table so a station/landmark can legitimately become a city; the Phase-1 gate now asks for the **CITY** with a confirm-first variant; the payload rule replaced "don't use that one" with a **two-entry list to walk**; the Phase-2 area question scope-locked; and Example 1 now **demonstrates** the city turn. **Crux decision: clean record + no application, over wrong city + application.** The trade is false as posed — an empty `location` mints a `draft` that `apply_job` cannot use either, so a borrowed city buys only the appearance of an application, and the caller bears a permanent invisible cost so we can book a metric worth nothing.
- **Bug B — Need Capture never fired.** The wording was already comprehensive; the defect was POSITION (last, so first casualty of a drop). The offer now fires **inside the apply-failure turn**, the alternate-job line was rewritten from an announcement to a question (`इसमें अप्लाई करने की कोशिश करूँ?` — turn 43 ended on `कोशिश कर सकती हूँ।`, leaving nothing to answer at the highest-drop moment), and **B7 removed a standing rule that flatly forbade what the new instruction requires** — the exact contradiction shape that licensed D47/D49 to be ignored. Examples 1-4 now demonstrate the offer; 5 (distressed) and 6 (do-not-call) correctly still skip it.
- **VERIFIED LIVE:** call `6c69876d` forced `ACTION_LIMIT_REACHED` on an already-applied job. **D47 finally holds after failing twice** — the bot said the truthful "इस जॉब के लिए आपकी एप्लीकेशन पहले से लगी हुई है" and did NOT say "कोई तकनीकी दिक्कत है". **Fix B confirmed** — the Need Capture offer fired in the SAME turn as the failure line, `service_provider_pitched: Yes`. Confirmed again on `7ba6c80e`.
- **NOT VERIFIED — Fix A.** The harness cannot reach it: `contact_phone` is overridden by the dialled number, so every harness call uses the tester DID, which now has a live profile, so the new-caller city gate never triggers. Closed instead with a production detector, `raya/regression/location_integrity.py`, which flags any profile write whose `location` matches a job's city the caller never said aloud (script-aware Latin/Devanagari). Validated: it flags `924e611f` and nothing else across the other 4 calls.
- **NEW, still open:** Need Capture was ALSO skipped on a **successful** apply (`1cdc8438`, `service_provider_pitched: No`) — Fix B only covers the failure turn, so the majority happy path still drops it. And Phase 2 asked "आप male हैं या female?" **twice** on that call after the caller had answered. Both need their own fix.
- **Files:** `KKB/KKB Placeholder Hindi Signals.md` (22 ops, +10,279 chars, headings unchanged at 118); new `raya/regression/location_integrity.py`

### 2026-08-31 (later) — Khushboo round 2: fused technical line, skipped location turn, memory+output location
- **"Apply is failing on all calls" — it is NOT.** Call `16a6632e` (10:18 UTC) **applied successfully** with the real Ghaziabad job ids. Of her three calls: `3299ada4` got the OLD truncated 1023-char payload (old-instance ids, no apply attempted); `16a6632e` succeeded; `bd3e8fb7` failed `ACTION_LIMIT_REACHED` because she re-applied to the SAME job she had applied to three minutes earlier. So the blocker was the campaign's stale/truncated payload, and real job ids fix it.
- **D47 is INTERMITTENT, not fixed.** Both `6c69876d` (15:29 IST, passed — truthful "already applied" line) and `bd3e8fb7` (15:51 IST, failed — "तकनीकी दिक्कत") ran on the SAME deployed prompt with **byte-identical 490-char tool results both containing `ACTION_LIMIT_REACHED`**. Same rule, same data, opposite behaviour 22 minutes apart. This is runtime adherence and cannot be made deterministic by prose (see D25/D49/D50). Any further work here belongs at the platform or tool layer.
- **FIXED — the fused technical line after a service-provider YES.** On `bd3e8fb7` turn 21 the bot answered her "yes" correctly ("बहुत बढ़िया, हमारी टीम आपसे एक-दो दिन में संपर्क करेगी") and then appended the apply-failure loop-acknowledgement ("आज तकनीकी दिक्कत लग रही है — हम इसे ठीक करके आपको वापस बताएँगे।"), so she heard "technical problem" as the answer to agreeing to a service provider. That line is now scoped explicitly to a SECOND consecutive apply failure and FORBIDDEN in any turn answering Need Capture, in the closing turn, and on a call where only one apply failed.
- **FIXED — the location turn was skipped entirely.** `location: "Delhi"` was passed and her profile carried `Bengaluru`; neither was ever asked or confirmed. Cause: the location turn lived behind Case B's conditional "**If you still need the area**", and with a location already in hand the model concluded it did not need it. It is now unconditional on EVERY path — including the role-change path she took — and states that when a location is KNOWN the turn is a **confirmation, not an acquisition**, because a location never confirmed aloud is not confirmed.
- **FIXED — memory prompt (`KKB Memory.md`) had location fields but had never been told where location now comes from.** `preferred_location` now names all the new capture points (Step-1 turn, the ladder, a station/landmark answer, the mismatch capture), and forbids filling from the input variable, a job's location, or where they live. Added `home_location` (where they LIVE — a different fact that must never overwrite the preference) and `location_capture_outcome` (`Stated`/`Confirmed`/`Open`/`Refused`/`Unclear`) so the next call knows whether to confirm, ask afresh, or not push a caller who already refused.
- **FIXED — output prompt was filling `preferred_location` from the input.** `16a6632e` recorded `preferred_location: "Delhi"`, which was the call's input variable and never spoken by the caller. Added the explicit test: the words must have come out of the CALLER's mouth (agreeing to a place the bot named counts); a value equal to the input `location` that the caller never said is "NA".
- **Gender is NOT auto-detected.** On `16a6632e` it WAS asked aloud ("male हैं या female") but **never sent to any tool** — no `update_profile` ran, and her stored gender is still `None`. The call ended after the apply-success line before Phase 2 persisted anything.
- **STILL OPEN (own fix needed):** after a SUCCESSFUL apply the call closes before Phase 2 persists and before Need Capture is offered (`16a6632e`: `service_provider_pitched: No`, gender asked but unsaved). Fix B only covers the failure turn. Also open: Phase 2 asked gender twice on `1cdc8438`.
- **Files:** `KKB/KKB Placeholder Hindi Signals.md`, `KKB/KKB Memory.md`, `KKB/KKB Output.md` (all three deployed to the live agent; memory/output via `memory_instructions` / `output_instructions`)

### 2026-08-31 (round 3) — governance, deterministic fixes, testing rebuilt
- **Process failure acknowledged and fixed in the instructions.** Four changes were written up as "FIXED" with zero live calls. `CLAUDE.md` now carries **"The word 'fixed' requires a call id"** (N fixes owe N call ids; otherwise the label is DEPLOYED, NOT VERIFIED in changelog, commit AND user report) and **"'Intermittent' is not a result"** (a five-step ladder ending in a fix: grep the wrong output against the prompt per D50 → delete the competing instruction → **remove the wrong option rather than forbidding it** → move the decision into the tool schema → escalate only then, with both call ids; never write a third wording of a guard that failed twice). Same two steps added to `/update-prompt` as steps 11-12.
- **VERIFIED (8/8 calls) — Need Capture now fires**, `service_provider_pitched: Yes`, in the SAME turn as the apply result, on BOTH the success and failure paths: `db942d8e`, `b0a76b03`, `b6af8d05`, `cfb5416b`, `4f00dd95`, `43983693`, `81a9b704`, `9d0be846`. This closes the success-path gap found on `16a6632e`.
- **VERIFIED — the false cause-claim is eliminated.** The line "कोई तकनीकी दिक्कत है" was DELETED from the prompt rather than scoped; the fallback now asserts no cause. `raya/regression/apply_failure_wording.py` shows DIAGNOSED A CAUSE on `924e611f` (07:25), `7ba6c80e` (10:03) and `bd3e8fb7` (10:21), and **none after the fix** — `db942d8e` and `b0a76b03` are clean. The worst case is now a vague truth instead of a confident falsehood.
- **NOT VERIFIED — row 1 of the apply-failure lookup (the explicit "already applied" line).** 0 of 6 duplicate-apply calls spoke it; all said the truthful fallback instead. Four mechanisms were tried: branch-above-the-line, condition-on-the-label, remove-the-false-claim, and a worked example. The section was then restructured from two separately-labelled lines into ONE slot with a two-row lookup table (the "Base failure line" label no longer exists; the prompt got 2,073 chars SHORTER). **That restructure is untested** — and it cannot be tested on the harness: `contact_phone` is overridden by the dialled number, and the tester DID now carries FIVE live Ghaziabad profiles, so the bot picks a different one per call and a repeat apply becomes a new (profile, job) pair that never returns ACTION_LIMIT_REACHED. Closed with the production detector above instead.
- **FIXED (found statically by the rebuilt suite, no calls needed) — a MANDATED line broke the prompt's own hard ban.** The new-caller consent line said "आपकी **प्रोफाइल** बनानी होगी" while Profile Wording Rules bans that word in six variants; it was heard live on `dcf73898`. Now "आपकी जानकारी सेव करनी होगी". The only remaining instances of the word are the banned-examples list.
- **Testing rebuilt.** `/generate-test-cases` and `/voice-test` rewritten (570 and 521 lines) to DERIVE scenarios from the prompt rather than invent them. Measured for this bot: **683 distinct testable behaviours, 240 derived scenarios, ~25 previously run = 10.4% coverage** — the denominator is now printed in every run report so a thin suite is visible. Adds the mandatory D50 example audit as a static pre-call step, a grader contract that forbids the four false-result modes hit today (boilerplate flagged as machinery, missed Devanagari variants, Latin-vs-Devanagari comparison, ordinal call pairing), a fixture-hygiene protocol that VOIDS results contaminated by tester-profile drift, and a not-testable-by-voice section with an alternative check per item.
- **Fixture drift is now a documented hazard.** Three scenarios today produced meaningless results purely because the tester DID's stored profile had been rewritten by earlier calls (role drifted to "कंप्यूटर ऑपरेटर"; then five live profiles accumulated). Two were briefly mistaken for bot failures.
- **Files:** `CLAUDE.md`, `.claude/skills/update-prompt/SKILL.md`, `.claude/skills/generate-test-cases/SKILL.md`, `.claude/skills/voice-test/SKILL.md`, `KKB/KKB Placeholder Hindi Signals.md`, new `raya/regression/apply_failure_wording.py`, new persona `raya/personas/loc/hi-states-gender-early.md`

## 2026-08-28 — KKB Signals Hindi: location capture, reconfirmation and mismatch fallbacks (R1–R4)
- **Feedback/bug:** team decision after the investigation reports. Four asks, all on `kkb-hi-signals` only as a pilot: (R1) when a seeker says the offered jobs are too far, capture their preferred location — asking one level finer if they name only a broad city — and acknowledge it; (R2) the same when they are unhappy with the KIND of work; (R3) reconfirm a location we already hold rather than assuming it ("are you looking for jobs near X?"); (R4) when a place name cannot be transcribed, ask them to say it slowly, and offer nearest railway/metro station or nearest landmark as alternative anchors. Location becomes a new input variable, and must be settled BEFORE recommendations because the recommendations depend on it.
- **Change:** `${location}` declared as a sixth input variable with an explicit precedence order (caller's own words this call > fetched profile > campaign input > UNKNOWN) and an EMPTY-value list so sentinels are never spoken. R3 is implemented as a **wording variant of the area question Step 1 already asks** — not a new turn — so the happy path costs zero extra turns; a location the caller volunteered themselves is LOCKED and never echoed back. R4 is a **bounded three-turn escalation ladder** (reconfirm → one finer probe / slow-repeat → one proxy anchor, station or landmark) with a HARD CAP; "कहीं भी चलेगा" is a complete answer at any rung, and **every terminal state — captured, open, or failed — still routes to the job list**. A failed capture is explicitly barred from triggering No-Match, a callback line, or a close. R1/R2 live INSIDE both No-Match copies behind a three-part gate, so the existing HARD GUARD governs them and neither can fire while a single un-presented job remains; the acknowledgement is a PREFIX on the existing no-relevant-jobs line rather than a second callback promise. Fillers are clauses on existing turns, never turns of their own. All new spoken lines are built on `चाहिए` / imperatives and carry no caller-gender agreement (analyser D44).
- **Files:** `KKB/KKB Placeholder Hindi Signals.md` (20 surgical ops; +27,492 chars, heading count unchanged at 118 so Hindi/Kannada sync parity holds); `KKB/KKB Output.md` (new `preferred_location` + `preference_mismatch_reason`, deployed to this agent's `output_instructions` only); `raya/divergences.json` (`kkb-hi-signals-location-capture` registered so `/sync-check` does not read the pilot as Kannada lag); analyser **D48** added and **B3** extended with a gate-POSITION bullet.
- **Verified on deploy:** repo == live; derived `agent_args` is exactly the six expected keys with **zero phantom args**; all new blocks confirmed present in the live instructions; static regression unchanged from baseline (0 critical, 0 major, 1 pre-existing minor).
- **Scope guard:** Hindi Signals ONLY. Not ported to `kkb-kn-signals`, either inbound twin, or Maya — porting requires `/port-feature`, Kannada-script canonical spellings, an inbound-safe closing clause, and an independent live test per variant.

## 2026-08-28 — Signals production cutover: Ghaziabad (Hindi) / Dharwad (Kannada)
- **Feedback/bug:** the Signals platform split into two region instances — `gzb-signals.bluedotseconomy.org` for the Hindi bots and `dharwad-signals.bluedotseconomy.org` for the Kannada bots — each with its own API key and acting-org id. The new instances also validate item_state far more strictly than the old shared instance, so a straight URL/key swap would have broken every profile write.
- **Change:** tool-config cutover on all 10 Signals agents via the new `scripts/signals_cutover.py` (plan/apply/verify, idempotent). Per agent: base URL on every tool, `x-api-key` + `x-acting-org-id`, and the base URL embedded in `apply_job`'s `payload_template.target_item.item_instance_url`. Plus the validation fixes the new instances require, each confirmed against the live API: `age` and `positions` declared **integer** (Raya does whole-value typed substitution, so the declared param type is what controls the wire type); `otherHelpNeeded` declared **array**; `natureOfJobsInterestedIn` literal changed from `'Full-time'` to `['Full-time']`; `educationCategory` enum `'ITI / Other Vocational Trainings'`→`'ITI'` and `'Polytechnic / Diploma'`→`'Diploma'`; `otherHelpNeeded` enum replaced entirely with `'Skilling & Vocational Training'` / `'Other Support (Accommodation / Travel)'`; `title` dropped from the `job_posting_1.0` payload (now rejected as an additional property).
- **PROMPT change (this repo):** the three inbound Signals prompts carried a **hardcoded Job Inventory** whose `job_id`s belong to the OLD instance. Post-cutover every inbound apply failed `TARGET_ITEM_NOT_FOUND` — inbound callers could not apply to anything. Replaced each inventory with 4 live job ids from that bot's own instance (Ghaziabad for the two Hindi files, Dharwad for the Kannada one), keeping each file's language-specific `qualification` text. Verified live: the same scenario now reaches `ACTION_LIMIT_REACHED` (a real duplicate) instead of `TARGET_ITEM_NOT_FOUND`.
- **Files:** `KKB Placeholder Inbound Signals.md`, `KKB Placeholder Inbound Kannada Signals.md`, `Maya Inbound Signals.md`; `scripts/signals_cutover.py`; `raya/testcases/args/signals-prod/`
- **Testing:** 17 live calls across all 10 agents. Full write path proven end-to-end on `kkb-kn-signals` (`get_profile` empty → `create_profile` with integer age → `apply_job` → `status: success`). No agent contacted the wrong region on any call.

## 2026-08-25 — Apply failure messages now branch on the actual failure reason
- **Feedback/bug:** tracker r100 (KKB Hindi Signals, 25/08, P1) reported as "apply failed, no details collected or reiterated", plus a same-day retest reported as "API still failed" after a Signals API-key incident had been fixed. Root-caused against calls `bc7ef5b5` (10:26 IST) and `1e2fd2a2` (14:41 IST): neither was a technical failure. Both were `422 ACTION_LIMIT_REACHED` — "An active request already exists between these two profiles" — i.e. the seeker had **already applied** to that job (in `1e2fd2a2`, to the very job that applied successfully in `bc7ef5b5` four hours earlier). The bot spoke both as "कोई तकनीकी दिक्कत है" and promised to fix the problem and call back, so a correctly-refused duplicate was indistinguishable from an outage and was escalated as a P1 against the wrong team. r100/r101 were closed as *Rejected / Not an Issue*; this line is the one genuine defect they surfaced.
- **Change:** `Apply Failure Handling` now requires the reason to be read **before** anything is spoken, and splits into two cases. **Case A — the application already exists** (`ACTION_LIMIT_REACHED`, or any message saying an active/duplicate request already exists between the two profiles): say so truthfully, suppress the base failure line, no "तकनीकी दिक्कत", no apology, and no callback promise — close per Graceful Exit if no other job remains. **Case B — a genuine technical failure** (job does not exist, 4xx/5xx, timeout, no response): unchanged, uses the existing base failure line and next-step rules. Purely additive: 7 lines per file, nothing removed or reworded. The Case A spoken line is phrased to agree with the feminine noun एप्लीकेशन / ಅಪ್ಲಿಕೇಶನ್ rather than with the caller, so it is safe on a caller of any gender (analyser D44).
- **Files:** `KKB Placeholder Hindi.md`, `KKB Placeholder Kannada.md`, `KKB Placeholder Hindi Signals.md`, `KKB Placeholder Kannada Signals.md`, `KKB Placeholder Inbound.md`, `KKB Placeholder Inbound Kannada.md`, `KKB Placeholder Inbound Signals.md`, `KKB Placeholder Inbound Kannada Signals.md`; analyser pattern **D47** added

## 2026-08-24 — Tracker r96/r97/r98/r99: substantive service answer, returning-caller rollout, bounded name gate
- **Feedback/bug:** three tracker items, all P1, owner Parth. (r96/r97/r98 item 2) "Needs capture should be in details — rn upon asking it tells what kind of service this is": when a caller asked what the service provider actually is, the answer was a vague one-liner ("यह एक फ्री मदद है जो जॉब से जुड़ी गाइडेंस देती है") that tells them nothing they can decide on. (r96 item 1) The returning-caller callback was never rolled out to `kkb-hi-out` — verified absent (the one match in that file was an unrelated post-apply follow-up line). (r99, KKB Kannada Inbound, 24/08) "Missed asking details for new seekers, like location, name, gender, age" — grounded in call `6b420bac` (296s): the bot asked for the name **five times** in a row while the caller was asking about payment, then the caller hung up. No profile, no application. Across ~60 calls on that agent, `create_profile` fired **zero** times.
- **Change:** (1) The "what is this service?" answer now says what actually happens — the team talks to you, works out which work suits you, and can teach new skills through training/courses, at no cost — in all 8 KKB prompts, with the self-contradicting "answer in ONE sentence" instruction relaxed to "one or two short sentences" so the rule no longer fights its own script. (2) Ported the live-verified returning-caller callback block from `kkb-hi-signals` into `kkb-hi-out`, folded into the existing post-`get_profile` turn (never a separate turn — see analyser A10). (3) New **bounded asking** rule at the name HARD BLOCK: ask at most twice, answer the caller's own question first if they asked one, and if the second ask yields nothing, stop asking, say so plainly and close gracefully instead of looping.
- **Files:** all 8 KKB conversation prompts (service answer); `KKB Placeholder Hindi.md` (callback); `KKB Placeholder Hindi.md`, `KKB Placeholder Kannada.md`, `KKB Placeholder Inbound.md`, `KKB Placeholder Inbound Kannada.md` (bounded name gate)
- **Analyser:** new **B3** (unbounded re-ask on a hard-gated field dead-ends the call).

## 2026-08-12 — Inbound prompts: undo my wrong `${recommendations}` guards + never say "inventory" aloud
- **Feedback/bug:** two defects, both found while grading the fleet sweep. (1) **Self-inflicted:** yesterday's D43 (exhaust-the-list) and Need-Capture rollouts added three `${recommendations}` references to each inbound prompt — but the inbound bots have **no such variable**; their jobs come from the hardcoded **Job Inventory**, and the same files say so explicitly ("no seeker-specific or job input variables"). The prompts contradicted themselves, and because Raya derives `agent_args` from `${...}` tokens in the instructions, all four inbound agents had grown phantom `recommendations` / `contact_name` / `new_seeker` args — so any value a caller or test harness supplied was interpolated into the middle of the No-Match Fallback section. (2) **Machinery word spoken aloud:** on call `077ea55c` (kkb-kn-in) the bot told a real caller "ಈ **inventory**ನಲ್ಲಿ ಬೆಂಗಳೂರಿನ ಕೆಲಸಗಳು ಇಲ್ಲ" — twice. "Job Inventory" is an internal name and no rule forbade saying it.
- **Change:** (1) re-pointed all three guards at the **Job Inventory** (the D43 hard guard, the Need-Capture "no jobs to show" case, and the "never fire while jobs remain unshown" rule), and stripped `${}` from every *descriptive* mention of an absent variable so Raya stops deriving args from prose (`` `contact_name` ``, `` `new_seeker` ``, `` `recommendations` ``). Verified via the API that each agent's args are now exactly what production sends: `contact_memory`, `contact_phone`, `country_code`. (2) Added a never-say-aloud rule to the Hallucination Guard in all four inbound prompts, with a correct/incorrect spoken pair per language. No behavioural logic changed.
- **Files:** `KKB/KKB Placeholder Inbound.md`, `KKB/KKB Placeholder Inbound Kannada.md`, `KKB/KKB Placeholder Inbound Signals.md`, `KKB/KKB Placeholder Inbound Kannada Signals.md` (all four deployed)
- **Also corrected (no edit):** four "fabrication" verdicts from the sweep were **my grading error**, not bot defects — I compared spoken jobs against the call's `agent_args` on bots whose jobs are hardcoded in the prompt. `job_id 801dd2cf-…` is line 262 of the kkb-kn-in prompt; its inventory is entirely Hubballi/Dharwad, so "no Bengaluru jobs" was accurate. Analyser: **G6** (+ its verification corollary), **D45**.

## 2026-08-10 — Need Capture rolled out to the remaining KKB prompts (pilot verified first)
- **Feedback/bug:** Requested that the service-provider offer be piloted on the KKB Hindi bot, tested across scenarios, and only then replicated. That gate is now met.
- **Verified on the pilot before rolling out** (`KKB Placeholder Hindi Signals.md`, live calls): Path A + clear yes; Path A + clear no with **no second pitch**; Path B + ambiguous answer → Maybe (the undecided path, which originally produced NO offer at all and was fixed by making the block fire by default for any engaged call). `service_provider_pitched: "Yes"` / `service_provider_interest: "Yes"` confirmed present in the extracted `call_output`, not just the transcript.
- **Change:** Added the same `# Need Capture (ONE offer, immediately before Graceful Exit)` section to the other seven KKB conversation prompts — Hindi + Kannada, outbound + inbound, legacy + Signals — with the spoken lines translated into Kannada for the Kannada files (agnostic rules copied verbatim). Graceful Exit in each now checks whether the offer has been made before speaking the closing line. `KKB Output.md` deployed to all six live KKB agents so the two new fields are extracted everywhere the block now runs.
- **Files:** `KKB/KKB Placeholder Kannada Signals.md`, `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md`, `KKB/KKB Placeholder Inbound.md`, `KKB/KKB Placeholder Inbound Kannada.md`, `KKB/KKB Placeholder Inbound Signals.md`, `KKB/KKB Placeholder Inbound Kannada Signals.md`, `KKB/KKB Output.md`.
- **VERIFY-PENDING:** verified live on KKB Hindi Signals only. Every other variant owes its own live call — Kannada especially, since the spoken lines are new there. Telephony bridging succeeded on only 12 of 69 dial attempts during this session, which is why the per-variant sweep is not yet done rather than skipped.

## 2026-08-10 — Job flow ended with jobs still unshown ("discontinued after 2nd set")
- **Feedback/bug:** +91XXXXXX5910, 07/08/2026 18:52 — "Job flow discontinued after 2nd set of recommendations." Call `54e8b166` on **`kkb-kn-out`** (KKB Kannada legacy outbound, not Signals).
- **Root-caused against the args first — the inputs were FINE this time.** `recommendations` carried **8 valid jobs**, 1861 chars, parsed cleanly. This is a genuine prompt bug, not a data one.
- **What happened.** Set 1: Electrician. Caller asked for something else. Set 2: Fitter, CNC Operator, Mechanic. Caller said "ಬೇಡರೀ" (no). The bot then spoke the **No-Match Fallback** — "ನಿಮಗೆ relevant ಜಾಬ್‌ಗಳು ಈಗ ಕಾಣ್ತಿಲ್ಲ" — and hung up, **while four jobs it had never mentioned were still in the array**: Machine Operator, Assembly Trainee, Welder, Customer Service Executive. Four of eight shown; the caller was told nothing relevant existed.
- **Root cause.** No-Match Fallback triggers on "the user explicitly says none of the available jobs are relevant". A short "no" after a set satisfies that reading, and nothing in the prompt required the list to be exhausted first. So a set-level refusal was treated as a call-level rejection.
- **Change (agnostic logic, Hindi master → Kannada mirror, English rules copied verbatim):** a HARD GUARD on No-Match Fallback —
  - never declare No-Match while `${recommendations}` still holds jobs not yet presented on this call; present the next set instead (Step 2 format, up to three, best-fit first);
  - **a short "no" ends a SET, not the call** — treat it as a request for the next set while stock remains;
  - keep track across sets: never re-present a declined job, never restart from the top of the array;
  - both No-Match sections in each file carry the guard (the second points at it), since the fallback can be reached from either.
- **Files:** `KKB/KKB Placeholder Hindi.md` (master), `KKB/KKB Placeholder Kannada.md` (mirror). Both deployed.
- **VERIFY-PENDING:** not yet exercised on a live call. Needs a caller who declines successive sets against a multi-set inventory, confirming the bot works through the list and only closes when it is genuinely empty.

## 2026-08-10 — Truncated `${recommendations}` on KKB Kannada Signals ("no jobs recommended")
- **Feedback/bug:** Two calls to +91916…842 on KKB Kannada Signals — 11:02 (`bc961b88`) and 11:06 (`17a2e1e2`) — reported as "no jobs were recommended".
- **Root-caused against the input args FIRST, and the report is only half right.** The 11:06 call did show no jobs (`jobs_shown: "No"`) and its final assistant turn was **completely empty**. The 11:02 call DID present a job (`jobs_shown: "Yes"`) but ended mid-sentence while reading it out.
- **The real defect is in the DATA, not the prompt.** `agent_args.recommendations` arrived **truncated at exactly 1023 characters**, cut mid-value at `"qualification": "NSQF Refrigeration` — 4 `job_id`s but only 3 closing braces, so the JSON is unparseable. Unable to parse it, the bot improvised: on 11:02 it spoke a **"ಎಲೆಕ್ಟ್ರಿಷಿಯನ್" job that does not exist in the list** (scraped from the EV Charging Technician's qualification text "ITI/NSQF Electrician or Solar Technician"), and on 11:06 it produced nothing at all.
- **Scale — this is not two calls.** **20 of the last 40 calls on `kkb-kn-signals` carry the identical truncated payload**, while `kkb-hi-signals` parsed **39 of 39**. Not a platform field cap either: a 1907-char payload on the same agent parses fine. Something upstream is emitting a pre-truncated string for this campaign.
- **REVERTED — no prompt change stands.** The owner confirmed the campaign simply did not pass the full JSON. Per this repo's own rule ("when the inputs were wrong, say the prompt is fine and make no edit"), the hardening below was removed from both files and both agents were redeployed to their pre-edit content. **The prompt was never the problem and is unchanged.** Recorded here only so the reasoning is not re-derived later.
- **~~Change (prompt hardening — reverted):~~** had added to the Pre-check in both KKB Signals prompts —
  - use only the job entries that are COMPLETE; discard a final entry cut mid-value; never guess the missing part;
  - a partial delivery is NOT a missing-data case — if at least one complete entry survives, carry on with those (closing the call while usable jobs exist is the worse outcome); fall back only when ZERO complete entries remain;
  - **name only real `role` values** — never a trade inferred from a `qualification`, company name, or any other field (this is exactly what produced the phantom Electrician);
  - **never end a turn with nothing** — say the missing-data line and close rather than emitting silence.
- **Files:** none in the end — both files are byte-identical to their pre-report state; the two agents were redeployed to confirm it.
- **Analyser:** catalogued as **D42**, including the diagnostic that finds it in seconds — `json.loads()` the args before reading the transcript, and check `count('job_id') > count('}')`.
- **Left open for a separate decision (NOT acted on):** with the payload broken, the bot spoke an "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್" job that exists in no `role` field — it took the word from another job's `qualification` ("ITI/NSQF Electrician or Solar Technician"). A fabricated vacancy told to a real jobseeker is a dignity/trust issue that stands on its own merit, independent of the bad payload. Worth a one-line Hallucination Guard rule ("name only values from a `role` field, never a trade inferred from a qualification or company name") IF the owner wants it — but it is a separate call, not part of this report, and nothing was changed.

## 2026-08-10 — Audio-check intro turn, returning-caller callback line, and the Need Capture offer (KKB Hindi Signals pilot)

Three requested changes, piloted together on **KKB Hindi Signals outbound** (`kkb-hi-signals`) before any fleet rollout.

### 1. Audio-check intro (new Turn 1) + `say_hello` disabled
- **Feedback/bug:** The bot opened straight into the full नमस्ते introduction while the caller was still saying "hello, who is this?" — so the introduction was talked over and effectively lost. Requested: disable the platform's speak-first toggle and instead open with a short "hello, can you hear me?" in the call's language, moving the real introduction to after the caller confirms.
- **Change:** Added `## Turn 1 — Audio check` as the first thing said on every call: *"हैलो, मेरी आवाज़ आ रही है?"*, ending the turn there. Branches for confirm / cannot-hear (ONE slower repeat, then a polite close) / silence. The existing introduction became **Turn 2**, unchanged in content. `say_hello` set to **false** on the Raya agent.
- **Platform finding (grounded, not assumed):** every production transcript — before and after — begins with a synthetic `[user] 'hello'` seed turn injected by the platform, which is what prompts the agent to speak first. Verified against 5 live production calls plus a controlled A/B on a scratch agent. The bot therefore still opens reliably with `say_hello=false`; what changes is that its first *generated* line is now the audio check rather than the full introduction.

### 2. Returning-caller callback line from `${contact_memory}`
- **Feedback/bug:** Requested a customised opener for seekers called more than once — "we spoke a few days ago about …" — driven by `${contact_memory}`.
- **Change:** Turn 2 now chooses between a **default** opening and a **returning-caller** opening: *"नमस्ते। पिछली बार हमारी बात हुई थी — [topic]. आज आपके इलाके में कुछ नई जॉब्स…"*. Gated behind an explicit **returning-caller test** that requires positive evidence of a previous CONVERSATION (a call summary, a job shown or applied to, a recorded last action). Campaign metadata, "Not Available", the "No Old Memory" sentinel, a job list, and anything saying the caller has not been dialled all FAIL the test and take the default opening. Rules added: no name in this line (the name still comes only after `get_profile`), no invented recency (default "पिछली बार"; "कुछ दिन पहले" only when the memory carries a timeframe), no raw memory text spoken, one sentence.
- **Why the gate matters (grounded in real inputs):** on the live fleet `${contact_memory}` is NOT the memory-JSON schema. On `kkb-hi-out` every recent call carries campaign metadata of the shape `"Sector: Healthcare; Course: Home Health Aide; Call status: not_dialled (batch incomplete); Gender(inferred): Female"` — which explicitly says the person has **not been dialled**. On `maya-hi-out` it is mostly `"Not Available"`; on `kkb-hi-signals` it is absent on 27 of the last 30 calls. Without the evidence gate this feature would have told first-time callers that we had spoken before.
- **STATUS: NOT WORKING — do not treat this as delivered, and do not port it.** The branch never fired on any of four live calls whose `agent_args` carried a full memory record with `last_conversation_summary`. Four separate blocking rules were found and removed, each verified by its own live re-test:
  1. Opening Rule: "the call ALWAYS continues with the SAME neutral greeting" → rewritten as an explicit two-opening choice with the decision stated first. Re-test: still did not fire.
  2. The `${contact_memory}` caveat: "treat the caller as NOT-yet-fetched (**behave like a new caller until the tool result arrives**)" — the callback line is spoken BEFORE the fetch, so this told the model to act as if the caller were new at exactly the moment the branch should fire. Scoped to profile details. Re-test: still did not fire.
  3. **Frequency, not contradiction** (measured, not guessed): the default opening line appears **6 times** in the prompt (the spec plus five of the six sample conversations) against **2** for the returning line, and the tiebreaker "when in doubt, treat the caller as NEW" then resolved every uncertain case against the new branch. The four default-opening examples were qualified and the tiebreaker narrowed. Re-test: still did not fire.
  4. Profile Handling: **"branch on WHAT COMES BACK, never on an input variable"** — written long ago to kill a `new_seeker` mis-routing bug, and a categorical prohibition of the mechanism this branch depends on. Scoped to the profile decisions. Re-test: **still did not fire.**
- **ROOT CAUSE FOUND — it was never a prompt bug. Correcting the conclusion above.** A controlled A/B on a scratch agent, same prompt and same `agent_args` carrying a full memory record, changing only one field:
  - `memory_enabled = false` → the bot read the memory back verbatim: *"मेमोरी मिली। उसमें लिखा है: {"seeker_id": "917946350285", "role_sought": …}"*
  - `memory_enabled = true`  → *"मेमोरी खाली है।"* (memory is empty)
  **`memory_enabled=true` makes the PLATFORM own `${contact_memory}`: it injects its own stored memory for that caller and discards whatever the campaign passes in `agent_args`.** All six KKB agents had `memory_enabled=true` with `memory_instructions=NULL` — so the store was permanently empty and every call received an empty memory. The model was behaving correctly the whole time; the returning-caller test correctly failed because there genuinely was no memory. That also explains the production observation that `contact_memory` looked "absent on 27 of the last 30 calls".
  The invalid state is confirmed by the API itself, which now rejects it: `PATCH {"memory_enabled": true}` returns **`400 memory_instructions is required when memory_enabled is true`**. The KKB agents predate that constraint.
- **Fix applied:** `KKB/KKB Memory.md` deployed to all six KKB agents, so the already-enabled flag actually functions and a memory is written after each call. The feature can now only be tested the real way — two sequential calls to the same number, the first writing the memory and the second consuming it. The earlier method of passing memory through `agent_args` could never have worked on a memory-enabled agent.
- **✅ WORKING — attempt 7, via option 2 (fold the callback into the turn the model already speaks).** Verified live on call `OPT2`:
  *"एक मिनट। सुनीता जी, पिछली बार हमारी बात डेटा एंट्री के काम के बारे में हुई थी — मैं देख रही हूँ कि आप अभी डेटा एंट्री ऑपरेटर का काम कर रहे हैं, क्या आप अभी भी डेटा एंट्री ऑपरेटर की जॉब देख रहे हैं?"*
  Graded: name from the profile ✓ · callback references the previous CONVERSATION, not profile data ✓ · topic accurate to the stored memory (`role_sought`/`jobs_applied`/`last_conversation_summary` all say Data Entry Operator) and not invented ✓ · role check in the SAME turn ✓ · turn **ends on the role-confirm question** with no bundled second question ✓ · next turn correctly waits ✓ · no "आपकी जानकारी मिल गई", no raw memory spoken ✓.
  **What changed:** the callback stopped competing for the opening turn and became a clause inside the post-`get_profile` turn where the bot already greets by name and reflects the role back. Turn 2 went back to a single opening, identical for every caller, with an explicit note that a returning caller is acknowledged after the fetch. The `EMPTY vs CONTAINS` test moved with the clause, bound label-first at the decision (`contact_memory is: {${contact_memory}}`). Example 2 was realigned to the new shape so it stops teaching the old one (**E1**).
  **Why it worked when six attempts did not:** attempts 1–4 removed rules that forbade the branch, 5 removed repetition, 6 made the value easy to read — all of them still asked the model to speak a NEW turn that competed with an existing one. Option 7 extends a sentence the bot demonstrably wants to say (six transcripts show it personalising at exactly that point) instead of fighting it. See analyser **A10**.
  **Credit:** the owner proposed both the labelled-variable binding and this fold; the binding order was corrected to label-first per **G1**.
  **VERIFY-PENDING:** (a) the EMPTY case under the new shape — the tester number's store is now permanently rich, so a no-memory caller cannot be simulated on this bot without deleting the stored memory row from the console (an owner action, not mine); the safety property is well-evidenced from the six earlier calls where an empty/metadata memory produced no callback and no false claim. (b) rollout to the other KKB + Maya prompts, each needing its own live call.
- **STOPPING AFTER SIX ATTEMPTS — and the last transcript explains why none of them worked.** On the attempt-6 call the bot did NOT use the callback opening, but one turn later it said:
  *"एक मिनट। सुनीता जी, मैं देख रही हूँ कि आप अभी डेटा एंट्री ऑपरेटर का काम कर रही हैं — क्या आप अभी भी डेटा एंट्री ऑपरेटर की जॉब देख रही हैं?"*
  **It already acknowledges the returning caller — by first name, with her role — in the post-`get_profile` turn.** That behaviour has been in the prompt for months ("Greet by first name … flowing straight into the role check"). The new callback line asks for the same acknowledgement one turn EARLIER, from a different source. This is **functional duplication, not contradiction** — the model performs the acknowledgement once, at the place the prompt has always put it, and skips the earlier copy. No amount of rule-fixing in the opening section removes a competing behaviour that is *supposed* to be there.
  Everything upstream is proven working: memory stored (console, 5,329 entries, rich record for this bot+number), retrieved (the writer increments `session_count` 3→4, so it reads the prior value), and injected at runtime (verbatim probe: `ब्लॉक शुरू होता है: {"skills":[],"seeker_id"`). The six attempts, in order: the "ALWAYS the SAME greeting" absolute; the "behave like a new caller until the fetch" scope; the example-context qualification + tiebreaker; the "never branch on an input variable" prohibition; deleting the five verbatim default-opening repetitions; and a labelled binding at the decision point. Attempts 1–4 each removed a rule that *forbade* the branch, 5 removed repetition, 6 made the value easy to read. None addressed the duplication, because I did not see it until the last transcript.
- **RECOMMENDATION — a design decision, not another edit.** Two sensible options, both cheap:
  1. **Accept what the bot already does.** It greets a returning caller by name and reflects their role back in the turn after the fetch. That may already satisfy the original ask, and it has the advantage of being profile-verified rather than memory-derived. Delete the callback-opening section and the problem disappears.
  2. **Move the memory-based callback INTO that existing post-fetch turn** rather than competing for the opening. The model demonstrably wants to personalise there, so add the conversation reference to the line it already speaks — e.g. name + "पिछली बार हमारी बात [topic] के बारे में हुई थी" + the role check — instead of a separate earlier turn. This works with the model's behaviour instead of against it, and it is the only untried mechanism.
  Option 2 is the closer match to what was asked (a *conversation* reference, not a *profile* reference). Either way: **no more edits to the opening section** — that avenue is exhausted and six live calls say so.
- **Attempts 5 and 6 (2026-08-10, after the memory pipeline was proven healthy).** With storage confirmed by the console and injection confirmed by a corrected verbatim probe (`ब्लॉक शुरू होता है: {"skills":[],"seeker_id"`), the input is known good and the remaining problem is genuinely the prompt. Two things were done:
  - **Attempt 5 — finish the frequency fix properly.** Attempt 3 had measured the real bias (default opening 6 occurrences vs returning 2) but only annotated the example *contexts* and left all six verbatim repetitions in place, so the examples went on teaching the default by repetition. The five sample-conversation copies of the opening line are now replaced by a pointer — *"(the Turn-2 opening — DEFAULT here, because this caller's memory records no previous conversation…)"*. The default now appears **once** (the spec) against the returning line's **twice**: the bias is inverted, not merely footnoted. This is a **deletion** of competing text, which is why it does not contradict the "stop adding prose" conclusion.
  - **Attempt 6 — an explicit labelled binding at the decision point (owner's suggestion).** The decision block used to say "read the Contact context block above", asking the model to look thirty lines back at an unlabelled blob. It now prints the value **at** the decision, bound to its name: `contact_memory is: {${contact_memory}}`, followed by a plain binary test — EMPTY → default opening, CONTAINS a previous conversation → returning-caller opening, each with concrete markers (`last_conversation_summary` with real sentences, non-empty `jobs_applied`, a `last_action`, `session_count` ≥ 1).
    **Order matters here and the suggestion was adjusted for it.** The proposed shape was *"let {${contact_memory}} be contact_memory"* — value first, label last, which is precisely the **G1** anti-pattern that once broke Maya's `new_seeker` fork (`Consider ${new_seeker} as new_seeker` interpolating to "Consider no as new_seeker"). Written label-first, it interpolates cleanly to "contact_memory is: {…the real memory…}". That exact shape is already proven in this repo **today**: `applied_job_role is: ${applied_job_role}` fixed TRRAIN's job-title branch on the first attempt.
    The `### Contact context` injection block is untouched and still present verbatim, as `CLAUDE.md` requires — the binding was added at the decision point, not substituted for the block. `${contact_memory}` therefore interpolates twice, which is harmless and puts the data where the choice is made.
- **RETRACTION — the claim below that "the platform is not storing caller memory" was WRONG.** The Raya console at `console.getraya.app/memories` lists **5,329 stored memories**, including a detailed one for this exact bot and test number: `session_count: "4"`, `last_action: "Applied"`, `jobs_applied` with three entries, and a real `last_conversation_summary`. Storage works, and the seed calls did write it.
  My probe was the problem, not the platform. The echo prompt told the model to answer "मेमोरी खाली है" if the block *"says there is no old memory"* — and the scratch agent's own memory was a schema full of blank fields plus `"General conversation with no new job-search details shared."`. The model followed that instruction correctly. **A diagnostic that invites the model to judge its input is not a diagnostic** — it must echo verbatim and judge nothing. Re-running it that way.
  What remains true: the branch has not been seen firing. What is now known to be false: that there was nothing for it to fire on. The evidence below is kept as a record of the wrong turn, not as a finding.
- **~~FINAL STATUS after enabling memory fleet-wide: the platform is not storing caller memory at all.~~ (RETRACTED — see above.)** Owner confirmed the campaigns send nothing in that field, so memory was turned ON for all 18 live agents with each one's writer prompt deployed (see `raya/deploy-history.md`). Re-tested properly — and it still does not work. Three observations, in order of strength:
  1. **Seed-then-consume, 10-minute gap.** Call `def6f415` was a full substantive call — 161 s, 28 turns, an `apply_job` that succeeded, profile details gathered. Ten minutes later a second call to the same number opened with the DEFAULT greeting, as if the caller were new.
  2. **Direct echo probe on a fully valid configuration.** The scratch agent (memory ON + `KKB Memory.md` deployed + a prior call on that agent/number) was asked to read its own context block aloud. It said *"मेमोरी खाली है"* — empty.
  3. **The receiving end is proven fine.** The same probe with memory OFF read a campaign-supplied memory back verbatim. So injection works; storage does not.
  **Post-call processing itself is running** — the OUTPUT prompt produced a full 17-field `call_output` for that same seed call. It is specifically the memory that is never kept. There is also no endpoint to read a stored memory back (six plausible paths tried, all 404/500), so this cannot be diagnosed further from outside.
- **This is now a platform issue for LitWiz/Raya, not a prompt issue.** Everything on this side is correct and verified: flag on, writer prompt deployed, injection block present verbatim in all 20 prompts, two-call test method used. **Make no further prompt changes chasing this** — four rules were already rewritten before the real cause was understood.
- **The four contradictions removed above were all genuine and are kept** — they would each have blocked the branch once the memory started arriving. But none of them was the cause, and I was wrong to conclude runtime non-adherence.
- **Architectural note for whoever owns the campaign:** memory ownership is exclusive. Either the platform owns it (`memory_enabled=true` + a memory prompt deployed) or the campaign owns it (`memory_enabled=false`, value passed in `agent_args`). Enabling the flag on a bot whose campaign currently supplies `contact_memory` will silently start discarding that value.
- **It is safe to leave in place meanwhile.** The evidence gate works: on live calls carrying campaign metadata ("Call status: not_dialled") the bot correctly used the default opening and never claimed a prior conversation. The section is dormant, not harmful. All four fixes above are genuine improvements and were kept.
- Catalogued as analyser pattern **A9**, extended with the frequency check and the architectural-prohibition check, and with the warning to run the entire sweep before the next test rather than one fix per call.

### 3. Need Capture — one service-provider offer before Graceful Exit
- **Feedback/bug:** New requirement: capture seeker need by offering a service provider once per call, before goodbye.
- **Change:** Added `# Need Capture (ONE offer, immediately before Graceful Exit)` with Path A (applied, or declined for a CONCRETE reason) and Path B (confused / unsure / declined with no clear reason), answer handling → `service_provider_interest` = Yes / No / Maybe, and `service_provider_pitched`. Do-not-fire gates for do-not-call, disengagement, distress, and calls that never got past the greeting. Rules: one ask per call, never explain the service, never name TRRAIN or any partner, no jargon discovery questions, one-sentence clarification allowed if asked.
- **Adapted rather than pasted (as instructed):** the supplied text was rewritten from Latin script into Devanagari (KKB's Script Output Rule forbids Latin in spoken lines — "chances/service providers/interested/decide" → "चांस/सर्विस प्रोवाइडर/इंटरेस्टेड/डिसाइड"), and the "do not fire for calls under 30 seconds" condition was restated as something the model can actually judge (the bot has no clock): do not fire if the caller disengaged, refused, or the call never got past the audio check or greeting.

- **Files:** `KKB/KKB Placeholder Hindi Signals.md`, `KKB/KKB Output.md`, `raya/personas/hi-audiocheck-applies.md` (new), `raya/personas/hi-unsure-declines.md` (new), `raya/personas/hi-declines-concrete.md` (new), `raya/personas/hi-cannot-hear.md` (new), `.claude/skills/prompt-analyser/reference/bug-patterns.md` (A9, G2).
- **Output prompt:** added `service_provider_pitched` and `service_provider_interest`. **Reconciled first** — the LIVE `output_instructions` on `kkb-hi-signals` was AHEAD of the repo (it carried a `consent_status` field the repo lacked) and its example JSON had been corrupted into one collapsed line (`"seeker_name": "Rajesh Kumar, call_answered": "Yes, …`). Adopted `consent_status`, restored the well-formed example, then added the two new fields.

## 2026-08-07 — Split the bundled "any questions? / shall I apply?" turn (lost-candidate bug)
- **Feedback/bug:** Reported on two 2026-07-28 production calls on the Kannada outbound campaign (`KKB Placeholder- Kannada`): "Candidate said no doubts / no further questions — bot thought they don't want to apply. More clear flow while confirming is expected." VALIDATED against both transcripts: call `215fdd2d` (+91843…206, 16:50 IST) — caller said "ಜಾಬ್ ಇಂದಂತೂ ಅವಶ್ಯಕತೆ ಇದೆ" (I need a job right now), chose the Machine Operator role, then answered "ಇಲ್ಲ ಮೇಡಂ, ಏನು ಪ್ರಶ್ನೆ ಇಲ್ಲ" and was closed out with `jobs_applied: []`. Call `6ee05050` (+91814…956, 17:02 IST) — identical: chose Customer Service, said "ಇಲ್ಲ ರೀ ಮೇಡಂ, ಏನೂ ಇಲ್ಲ", closed with `jobs_applied: []`. Two willing candidates lost.
- **Root cause:** the job-detail spoken block ended with TWO distinct questions in ONE turn — "any other questions?" AND "shall I apply?". A caller answering the first produces a lone "no", which the model bound to the second and read as a refusal. This is prose ambiguity, not a tool-adherence miss: the prompt itself instructed the two-question turn.
- **Change:** structural, not more prose. (1) The spoken job-detail block now ends with ONLY the doubts question — Kannada "ಈ ಕೆಲಸದ ಬಗ್ಗೆ ಏನಾದರೂ ಕೇಳಬೇಕಾ?", Hindi "इस जॉब के बारे में कुछ पूछना है?" — and stops. (2) The consent/apply question moved to its own separate turn, carrying the unchanged data-share disclosure. (3) Three new English rules: never bundle the two questions; a negative to the doubts question is NOT a refusal but a green light to the consent turn; only an explicit refusal to the CONSENT question declines, and an unclear consent answer is re-asked once naming the action. The data-share disclosure wording, the tool payloads, the Phase-1 gates and every other spoken line are unchanged.
- **Note on reproduction:** the bug is PROBABILISTIC. The reported bot (`kkb-kn-out`) would not bridge across 12 harness dials, so it could not be live-reproduced; the Signals twin carrying the byte-identical line handled the same "no questions" answer CORRECTLY and applied. So the ambiguity does not fail every time — which is exactly why it was fixed structurally rather than left to chance on the apply step.
- **Files:** all 8 KKB seeker conversation prompts (Hindi + Kannada × outbound + inbound × Signals + legacy). Snapshot for rollback: `versions/KKB/2026-08-07_154826__pre-split-confirm-turn`.
- **Analyser:** new pattern **D41** (bundled doubts+commit question → negative misread as refusal).
- **Maya:** the identical bundled line exists in all 4 Maya prompts — flagged to the owner for the Maya gate, NOT yet applied.

## 2026-08-04 — KKB Kannada SIGNALS bots: introduce as "ಮಾಯಾ" (Maya)
- **Feedback/bug:** Feature request — the user wants the KKB Kannada bot to be called Maya and to state that name in its introduction. Until now all KKB bots identified only institutionally ("ನಗರ ಆಡಳಿತದ 'ಕೆಲಸದ ಮಾತು' ಉಪಕ್ರಮ") with no personal name.
- **Change:** Three surgical edits per file. (1) Persona line now names the agent — "You are **ಮಾಯಾ (Maya)**, the named voice of the **ಕೆಲಸದ ಮಾತು** initiative" — so it can also answer "who are you?" consistently mid-call. (2) The fixed opening line gains one short sentence, "ನಾನು ಮಾಯಾ.", inserted after "ನಮಸ್ಕಾರ." and before the existing institutional welcome (everything else in the greeting, incl. the recording disclosure and its position, is byte-identical). (3) **Contradiction fix — required, not cosmetic:** the intro-turn rule previously read "That institutional anchor is **the entire identity**", which directly contradicts adding a personal name; it now reads that the name **together with** the initiative is the whole identity, and adds an explicit guard that being named ಮಾಯಾ does not make the agent a private individual/agent/company rep. The "do NOT add ಗವರ್ನಮೆಂಟ್ / do NOT claim to be calling from the government" ban and the inbound "do NOT say I'm calling you" ban are preserved verbatim. A "say the name once, never repeat it in later turns" rule was added to prevent the repetition class we have hit before.
- **DELIBERATE DIVERGENCE (do not "fix" this as drift):** applied to the **Kannada Signals pair ONLY**, at the user's explicit instruction (2026-08-04). The Hindi Signals twins and BOTH legacy Kannada bots keep the institution-only intro with no personal name. So for this pair the greeting/persona is intentionally NOT mirrored to Hindi — the normal "Hindi is source of truth, mirror to Kannada" rule was consciously suspended for this one language-specific persona change. A future `/sync-check` will see an intro-line and persona-line difference between KKB Hindi Signals and KKB Kannada Signals: that is EXPECTED. Only the greeting text, the persona line and the intro-turn identity rules diverge; all call-flow logic, tools and payloads remain identical.
- **Naming note:** "Maya" is also the name of the separate Maya agent (Hindi-only, UP campus recruitment, `${college_name}`). These remain different agents with different prompts and uuids; the shared first name is intentional and has no functional coupling. When talking about "the Maya bot", disambiguate by agent/language.
- **Files:** `KKB/KKB Placeholder Kannada Signals.md`, `KKB/KKB Placeholder Inbound Kannada Signals.md` (targets `kkb-kn-signals` 33037201, `kkb-kn-in-signals` f38da775). Snapshot for rollback: `versions/KKB/2026-08-04_174256__pre-maya-name-kn-signals`.

## 2026-08-01 — Legacy inbound (Dhiway): restructure to the proven Signals inbound shape (structure only; Dhiway contract kept)
- **Feedback/bug:** The legacy Hindi INBOUND prompt (`KKB Placeholder Inbound.md`, agent b6222233, Dhiway/up-getjob backend) lagged the proven Signals inbound structure: a memory-driven "Introduction Priority Rule (Strict Override)" opener that resumed from `${contact_memory}` (a non-fetch) with `[Employer]`/`[City]` resume lines; a "आपकी जानकारी मिल गई" fetch-announcement; an `update_profile`-based Post-Application Info Gathering flow with the unstorable "काम कर रहे हैं या पढ़ाई?" question — but Dhiway has no `update_profile` (it 500s), so those writes were dead.
- **Change:** Rewrote to the Signals inbound STRUCTURE while keeping the Dhiway tool contract EXACTLY (no Signals tokens). Replaced the Strict-Override opener with the fixed neutral inbound welcome + memory-is-NOT-a-fetch guard + single Introduction Script; enforced the two-turn DECISIVE ROUTER (greet, then silent `get_profile` as the first action, no permission ask, no reveal — banned "आपकी जानकारी मिल गई"); added the Relevance-filter (never pad to three) rule; put the data-share disclosure on the deep-dive apply-consent line. Restructured Step 3.5 to the Dhiway model (returning caller gathers NOTHING → `apply_job` alone; new caller gathers name/role/location/age/gender/experience pre-apply → `create_profile` → `apply_job`); kept interview-readiness. REMOVED the `update_profile` tool section and the entire Post-Application Info Gathering flow, replacing them with a brief post-apply close (NO data write); added the explicit "tools are exactly three; no `update_profile`/`get_jobs`" note. Rewrote the sample conversations to the new flow. Kept the Dhiway contract verbatim: `get_profile` GET `phoneNumber:+91`, array response → `profile_id` = top-level `id`, `metadata.role`/`whatIHave.age`/`gender`/`name`; `create_profile` (`up-getjob` + `+91` phone + …) → use `profileId` UUID; `apply_job` `job_id`+`profile_id`. Job Inventory (17 real Dhiway job_ids) untouched. Grep-verified zero Signals tokens (item_state/lifecycle_status/educationCategory/phone_number/acting_as_user_id/user_id) and zero `update_profile`-as-a-tool (only absence statements remain). NOT deployed, NOT tested — VERIFY-PENDING.
- **Files:** `KKB/KKB Placeholder Inbound.md`

## 2026-08-01 — KKB Signals: capture the new seeker profile fields (educationCategory etc.) in Phase 2

- **Feedback/bug:** Signals extended the seeker `profile_1.0` `item_state` with the qualification/experience/help fields the bot previously had to skip (they used to 400 as unknown keys). Srivatsa confirmed the names via the live schema (`GET /api/v1/network/schemas`): `educationCategory` (+ conditional `schoolQualification`/`collegeQualification`/`itiTrade`/`itiTradeOther`/`itiInstitute`/`polytechnicDiploma`/`*Other`/`certificationDetails`), `workExperienceYearsConditional`, `nameOfLastRoleHeld`, `otherHelpNeeded`. (Email is NOT available on Signals — still not asked.)
- **Change:** (1) **Tools** — added the 15 new fields to `create_profile` + `update_profile` on all 4 KKB Signals agents (optional; payload prunes unset). (2) **Prompts** — extended Phase-2 (post-apply enrichment) in all 4 files to ask them, one per turn, only if missing: qualification (`educationCategory`) + ONE conditional follow-up (School→10th/12th; College→degree; ITI/Polytechnic→trade/branch + institute; Certification/Informal→free text), experience-years + last-role (only if `Worked before`/`Returning`), other-help (omit if none). Reversed the old "never ask qualification/…/email" line (kept the true exclusions: no "currently working/studying" field, no email). Softened the exact-count bridge (conditionals make N variable). Enum values are byte-exact English in the payload. **Split = all post-application** (Phase-1 stays minimal; time-to-apply unchanged) — user-approved.
- **API discovery/testing:** live schema fetched + all fields **write-tested** against `/api/v1/admin/participant` (200; bad enum → 400 INVALID_ITEM_STATE, so enums must be exact).
- **Files:** all 4 KKB Signals conversation prompts; agents 115b38a5, 33037201, 3f521174, f38da775 (tools + instructions re-deployed).
- **Test status:** VOICE-VERIFIED (KKB Hi outbound, call 0cea45dd) — the bot asked every new question and mapped to byte-exact enums (`educationCategory:"ITI / Other Vocational Trainings"`, `itiTrade:"Other"`+`itiTradeOther`, `itiInstitute`, `otherHelpNeeded:"Training"`). Persistence proven: the bot's exact Phase-2 payload POSTed with a correct phone → 200, all fields stored. (A 403 in the live call was self-inflicted test-data contamination — an API probe had written a wrong `item_state.phone` into the test profile, which the bot faithfully reused; fixed.) Kannada uses identical agnostic logic (enum-exact, statically verified). Also: bot-call max duration capped to 15 min by API; tester to 5 min.

## 2026-08-01 — KKB Signals: fix get_profile/create_profile phone double-91 prefix (CD6)

- **Feedback/bug:** live test (07699d53) showed `get_profile` sending `phone_number: "91917946350285"` — a doubled 91 (14 digits). The prompts templated the phone as `91${contact_phone}` and documented `${contact_phone}` as a 10-digit mobile, but the user confirmed production passes the **full 12-digit** number (91 + 10-digit). So `91${contact_phone}` doubled it → keys the profile to a junk number / wrong record (D17/D39).
- **Change:** across all 4 KKB Signals files (out Hi/Kn, in Hi/Kn) changed the literal `91${contact_phone}` → `${contact_phone}` (get_profile, create_profile, example stage-directions) and reworded every phone-format note to "`${contact_phone}` is already the full 12-digit number — pass it AS-IS; never prepend another `91`." (Same fix applied to Maya — see Maya/CHANGELOG.md.)
- **Files:** KKB Placeholder Hindi/Kannada Signals.md + Inbound Hindi/Kannada Signals.md; all 4 agents re-deployed.
- **Test status:** deployed; KKB Hi outbound re-test in progress (confirm single-prefix 12-digit phone + apply still succeeds). Analyser D17/D39 covers the class. Revert: git commit 7405bb7 (pre-CD6).

## 2026-08-01 — KKB Signals deep E2E pass: inbound inventory↔example consistency + sync-drift + are-you-AI + outbound-close

- **Feedback/bug:** (user) deep end-to-end test + fix of every Signals bug. Static audit (3 graders) + live tests surfaced: **(CD2, ship-blocker)** the inbound bots' hardcoded inventory was swapped to 4 real Signals jobs during the build, but the "What's available" line, role-synonym table, Case-B overview, canonical-locations and ALL example dialogues still described the OLD Ghaziabad/Noida retail-food set (McDonald's, Burger King, CY Future, Weavings, Cashier, Sales) — per analyser E1 the model copies examples over inventory → it would present jobs that don't exist (hallucination). Plus several Hi↔Kn sync drifts and two quality gaps (no are-you-AI responder; outbound-frame D5 leak in closings).
- **Change:**
  - **CD2 (inbound Hi+Kn):** rewrote "What's available", the role-synonym table, Case-B pool overview, canonical-location list, Role-family grouping, and all 5 example dialogues to reference ONLY the 4 real inventory jobs (Data Entry Operator/Kashi Infotech, Remote Customer Support/Rampur Technologies, EV Charging Technician/Yamuna Solar, AC Technician/Krishna Enterprises; Bengaluru/Remote). Inventory job_ids untouched. Each example's pedagogical point (silent fetch, live-item gate, decoupled create→apply, consent, no-match) preserved.
  - **Sync/correctness (KKB outbound Hi+Kn):** Kn Pre-check empty-`${recommendations}` fallback block added (parity); Kn Core-belief prose → English; Kn `update_profile` enum-reminder sentence added; Example-2 stopped persisting a non-schema `totalYearsOfExperience` (→ `workExperience` enum); top No-Match scaffolding normalised.
  - **Sync/correctness (KKB inbound Hi+Kn):** consent line "profile" word → "जानकारी/ಮಾಹಿತಿ" (Kn carve-out removed, D8); Hi Step-3 data-share clause added (parity); Kn `update_profile` hold → "ಒಂದು ಕ್ಷಣ"; Hi NOT-READY HARD BLOCK + update_profile example added (parity); Kn Core-belief → English; relevance-filter illustration unified; Kn intro fetch-mention removed.
  - **CD4 (all 4 KKB files):** added an honest "are you a real person / AI?" responder (English rule + in-language line).
  - **CD3 (KKB outbound Hi+Kn):** reworded 8 closings that invited the caller to "contact us" → outbound frame ("हमारी टीम आपसे फिर संपर्क करेगी" / Kn twin); do-not-call closings had the invite dropped (not substituted) to avoid contradicting the compliance promise.
- **Files:** KKB/KKB Placeholder Hindi Signals.md, KKB/KKB Placeholder Kannada Signals.md, KKB/KKB Placeholder Inbound Signals.md, KKB/KKB Placeholder Inbound Kannada Signals.md. All 4 agents re-deployed (115b38a5, 33037201, 3f521174, f38da775).
- **Test status:** deployed; live-test matrix in progress (outbound + inbound seeker apply + are-you-AI). Analyser E1 sharpened with the inventory-swap variant. Revert snapshots: raya/signals-expansion/e2e/snapshots/*.pre-e2e-fixes.md.

## 2026-07-31 — KKB Hindi + Kannada Inbound Signals (new bots, migrated to Signals DPG)

- **Feedback/bug:** migrate the KKB inbound bots (Hi+Kn) onto Signals as part of the Signals expansion; match the KKB Signals seeker bots' behavior with the inbound flow.
- **Change:** created `KKB/KKB Placeholder Inbound Signals.md` + `KKB/KKB Placeholder Inbound Kannada Signals.md` by re-domaining the kkb-signals structure onto the inbound base — 9 Signals patterns + Signals tool contract + inbound flow (welcome opener, hardcoded inventory, no government claim). Hardcoded inventory swapped to real Signals job_ids (b7513680/7dc7f10b/da32f92e/362b0ad9). Repurposed agents 3f521174 (Hi) + f38da775 (Kn, kn Signals tools). Hi build had dropped the interview-readiness Step 3.5 (ready_for_interview) — ported it back in + redeployed.
- **Files:** KKB Placeholder Inbound Signals.md, KKB Placeholder Inbound Kannada Signals.md (new); agents 3f521174, f38da775 repurposed.
- **Test status:** BOTH VOICE-VERIFIED end-to-end via the inbound-via-outbound harness (trigger inbound bot to call the tester). Hi call `1a8deec0`: inbound welcome, Signals get_profile, live-item select, real-inventory job (Data Entry/Kashi), apply_job -> 201 SUCCESS, Phase-2. Kn call `8d958447`: same, real-inventory job (Remote CSE/Rampur), apply_job -> 201 SUCCESS. Minor (Kn): post-apply update_profile doubled the 91 phone prefix (D39, cosmetic — apply already succeeded) — flag for a phone-format tighten.


## 2026-07-31 — KKB intro reword (drop government claim) + empty-recommendations callback fallback

- **Feedback/bug:** (1) Parth: the KKB intro still claimed "मैं गवर्नमेंट की तरफ से कॉल कर रही हूँ" — the caller identity should be the city-administration employment initiative, no "government" claim on top; also move the recording disclosure to the END of the intro turn and stop after one question. (2) Proactive safeguard (Parth): when NO job data is passed (`${recommendations}` empty/missing), the bot must not hallucinate a job list — say a short callback line instead. (Root of reported apply-fail `51c29350` was a USER input error — jobs sent in `contact_memory` not `${recommendations}` — NOT a bot bug; this fallback is the chosen safeguard, not a fix of that call.)
- **Change:** (Intro — outbound Hi/Kn + Signals Hi/Kn) all greeting variants re-anchored to "शहर प्रशासन की 'काम की बात' पहल" / "ನಗರ ಆಡಳಿತದ 'ಕೆಲಸದ ಮಾತು' ಉಪಕ್ರಮ"; the "मैं गवर्नमेंट की तरफ से…" / "ನಾನು ಗವರ್ನಮೆಂಟ್ ಕಡೆಯಿಂದ…" clause removed; recording disclosure moved to the END after the question; added an English "Intro-turn rules" block (identity anchor / no government claim; disclosure at end; end the turn after the disclosure and wait — one question only). Sample-conversation opening greetings updated to match (0 government-claim occurrences file-wide). (Fallback — all recommendations bots) added a "Missing-job-data fallback" at the recommendations pre-check / No-Match Fallback: empty/null/missing/unparseable `${recommendations}` -> say "अभी आपके लिए मुझे जॉब्स नहीं मिल रहीं — एक बार फिर से देखकर मैं आपको वापस कॉल करती हूँ।" / "ಸಧ್ಯಕ್ಕೆ ನಿಮಗೆ ಜಾಬ್‌ಗಳು ಸಿಗ್ತಿಲ್ಲ — ಇನ್ನೊಮ್ಮೆ ನೋಡಿ ನಾನು ನಿಮಗೆ ವಾಪಸ್ ಕಾಲ್ ಮಾಡ್ತೀನಿ." and close; never invent a job or apply with an example/invented `job_id`. Non-empty No-Match message (jobs present but none fit) unchanged.
- **Files:** KKB Placeholder Hindi.md, KKB Placeholder Kannada.md, KKB Placeholder Hindi Signals.md, KKB Placeholder Kannada Signals.md
- **Test status:** deployed + voice-tested (see session report); sync Hi<->Kn verified.


---

## 2026-07-30 — KKB outbound (Hi+Kn): REMOVE `new_seeker` → fetch-driven Profile Handling [overnight run, per Parth]
- **Feedback/bug:** kkb-kn-out new-caller apply failed (`082b21ea`: skipped create/apply + falsely claimed applied; `4e06fc31`: `apply_job` with EMPTY `profile_id` → 404). Root cause: the `${new_seeker}` flag vs reality mismatch — the DECISIVE ROUTER keyed the fetch on the flag, so `new_seeker="No"` + a caller with NO profile primed the "returning" path → apply with no `profile_id`. Parth directed: remove `new_seeker`, go fetch-driven like the inbound bots.
- **Change:** restructured "Profile Handling" to **ALWAYS call `get_profile` after the greeting and branch on its RESULT** (profile returned → returning caller; empty/declined → new caller). Removed the `${new_seeker}` input variable (confirmed dropped from both agents' agent_args), the yes/no router, and all 13 scattered `new_seeker` references (reworded to fetch-result terms; fixed 2 that falsely claimed `get_profile` is "never called" for new callers). Apply-router create_profile-FIRST→apply_job two-step is UNCHANGED. Hi/Kn kept in sync (symmetric diffs). Reviewed surgical.
- **Files:** `KKB/KKB Placeholder Hindi.md` + `KKB/KKB Placeholder Kannada.md` (DEPLOYED kkb-hi-out `da612923` + kkb-kn-out `87ab9108`; rollback snapshots `pre-deploy-kkb-hi-out-…` / `pre-deploy-kkb-kn-out-…` from this deploy). **VERIFY-PENDING:** the telephony was throttled by the night's testing and would not bridge; retrying with a longer cooldown. If verify shows a regression → restore the snapshot. High confidence (modeled on the working inbound bots; apply-router untouched).

## 2026-07-30 — KKB outbound (Hi+Kn): phone-malform fix — exactly-one-`+91` (ported from Maya) [overnight run]
- **Feedback/bug:** overnight retest (kkb-kn-out `fa530906` + `bz8fjqumk`) — `create_profile` sent a MALFORMED phone `+9197946350285` → HTTP 400 "Invalid Indian phone number format" → seeker not created, apply blocked. Root cause: kkb-out's phone rule (lines 776/817) only said "don't double-prefix" (weak), so the model mangled a `+91`-prefixed `${contact_phone}`. Maya's stronger rule (use as-is if already `+91`, only prepend to a bare 10-digit, never double/mangle) composes cleanly — Maya's phone was clean in the same harness (`baf836fe`).
- **Change:** ported Maya's exactly-one-`+91` rule to BOTH `get_profile` and `create_profile` phone rules in kkb-hi-out + kkb-kn-out.
- **Files:** `KKB/KKB Placeholder Hindi.md` + `KKB/KKB Placeholder Kannada.md` (DEPLOYED kkb-hi-out `da612923` + kkb-kn-out `87ab9108`). **Verify:** retest `082b21ea` — phone **FIXED + VERIFIED** (`get_profile` sent clean `+917946350285`, no more malform) + D34 hold neutral ✅.
- **⚠️ SEPARATE bug surfaced by the same retest (NOT the phone fix):** on the kkb-kn-out new-caller path the bot **skipped `create_profile` + `apply_job`** (called `get_profile` a 2nd time) and **falsely claimed "applied"** (`082b21ea`). The apply router prose (lines 379–389) is ALREADY correct + strong (create-first, no 2nd get_profile, no success-without-apply_job) → this is a **runtime tool-adherence glitch**, likely destabilized by conversational friction (the bot re-asked already-known fields → persona pushed back). Per D25 it is NOT prose-fixable; re-checking consistency (`bfai1a2ms`) → if consistent, → open-items + a platform/tool-schema backstop, not more prose.

## 2026-07-30 — KKB outbound (Hi+Kn): neutral `hold_message` (D34) [overnight run]
- **Feedback/bug:** overnight harness test (call `fa530906`, kkb-kn-out) — `get_profile`/`create_profile` `hold_message="ನಿಮ್ಮ ಮಾಹಿತಿ ಪರಿಶೀಲಿಸುತ್ತಿದ್ದೇನೆ"` spoken; "ನಿಮ್ಮ ಮಾಹಿತಿ ಸಿಕ್ತು" said even on an EMPTY fetch → the silent fetch is narrated (D34 ACTIVE). Tool-silence rule was prose-only, never named the `hold_message` param.
- **Change:** added a neutral-hold rule ("एक मिनट" / "ಒಂದು ನಿಮಿಷ" for `get_profile`/`create_profile`/`update_profile`). Ported from the Signals/inbound D34 fix.
- **Files:** `KKB/KKB Placeholder Hindi.md` (DEPLOYED kkb-hi-out, snapshot `…024527`) + `KKB/KKB Placeholder Kannada.md` (DEPLOYED kkb-kn-out, snapshot `…024528`). Verify: kkb-kn-out re-test pending.

## 2026-07-30 — KKB inbound: neutral `hold_message` (D34 — stop narrating the silent fetch) [overnight run]
- **Feedback/bug:** kkb-hi-in `get_profile` `hold_message` = "आपकी जानकारी निकल रही है" — the platform speaks `hold_message` aloud, so the fetch the prompt insists is silent gets announced (D34, ACTIVE). The tool-silence rule was prose-only and never named the `hold_message` param.
- **Change:** added a rule setting `hold_message` to the neutral "एक मिनट" for `get_profile`/`create_profile`/`update_profile` (only `apply_job` keeps a spoken bridge). Ported from the Signals D34 fix.
- **Files:** `KKB/KKB Placeholder Inbound.md` — **DEPLOYED kkb-hi-in** (snapshot `pre-deploy-kkb-hi-in-2026-07-30_003943`). Kn twin (`kkb-kn-in`) — **DEPLOYED** (same reconcile pass, snapshot `pre-deploy-kkb-kn-in-2026-07-30_004810`), Kannada neutral hold "ಒಂದು ನಿಮಿಷ". Verify-pending (inbound).

## 2026-07-30 — KKB inbound: new-caller apply-404 fix (D31 create→WAIT→apply, no batching) [overnight run]
- **Feedback/bug:** overnight test-harness static analysis + real transcripts (calls `5449910e`, `34f1f587`) — new INBOUND callers' `apply_job` fired with a fabricated/empty `profile_id` and NO `create_profile` → HTTP 404 "Invalid or missing profile_id"; apply broken for every new inbound caller. Root cause: the apply-sequence said "single turn / back to back / whole sequence", batching `create_profile`+`apply_job` so apply args were built before `create_profile` returned. (Control call `1fde1677` did create→apply correctly → success.)
- **Change:** rewrote the new-caller apply sequence to two steps crossing a tool-result boundary — `create_profile` FIRST → WAIT for its result → then as a SEPARATE step call `apply_job` with the returned `profile_id`; forbade same-turn create+apply and empty `profile_id`. Ported from the kkb-kn-out D31 fix (2026-07-27). Lines ~605 + ~1095.
- **Files:** `KKB/KKB Placeholder Inbound.md` — **DEPLOYED to kkb-hi-in** (`b6222233`, snapshot `pre-deploy-kkb-hi-in-2026-07-30_003534`). `KKB/KKB Placeholder Inbound Kannada.md` — **DEPLOYED to kkb-kn-in** (`4ac90bf1`, snapshot `pre-deploy-kkb-kn-in-2026-07-30_004810`) after reconciling: `pull` live (adopted the real Burger King/CIEL HR inventory the repo lacked) → committed the reconciliation → re-applied this D31 edit on top → deployed (post-deploy diff = 0 hunks). Live inventory preserved.
- **Verify:** INBOUND ⇒ not harness-testable (tester can't dial the bot). Hi = "deployed, verify pending" — needs a real inbound new-caller call. Analyser D31 already catalogs this; add kkb-hi-in + kkb-kn-in to its "Seen in" (resume).

## 2026-07-29 — KKB Signals bots (Kn + Hi): role-update offer on role-mismatch + 1:1 profile:user principle
- **Feedback (Parth, via agent-to-agent test harness, call `a0c24a1d`):** (1) when a returning caller with a live profile wants a DIFFERENT role than their stored one, the bot switched jobs + applied but never offered to update the stored role (profile stayed `role=Data Entry Operator` though the caller now wanted remote work). (2) profile:user should be treated as 1:1 — if more than one profile item exists, use only the active/live one.
- **Change (both Signals prompts, Profile Handling step 2 + Reading-the-response):** (1) added a **Role-update offer** to the "wants something different" branch — the bot names the stored role and offers once to update it: Hi "मैं देख रही हूँ कि अभी आपका role [old] है — क्या मैं इसे [new] कर दूँ?"; Kn "ನಾನು ನೋಡ್ತಿದ್ದೀನಿ, ಈಗ ನಿಮ್ಮ role [old] ಇದೆ — ಇದನ್ನ [new] ಗೆ ಬದಲಾಯಿಸ್ಲಾ?" → on yes `update_profile(role=new)`, on no leave it; proceed either way (live profile only; new/draft path sets role via `create_profile`). (2) added a clean "profile:user is 1:1 — use only the live profile, ignore the rest" principle atop the get_profile response-reading section (reinforces the D37 live-selection rule).
- **Files:** both Signals prompts (deployed to prod). Feature addition — no analyser entry (not a bug class).

## 2026-07-29 — KKB Signals bots (Kn + Hi): `location` required for `create_profile` (new-seeker apply PROFILE_NOT_LIVE)
- **Feedback/bug:** agent-to-agent harness test (call `fb1283cb`) — a NEW seeker completed the flow but `create_profile` ran WITHOUT `location` → profile created `draft` → `apply_job` failed `422 PROFILE_NOT_LIVE`. Curl-confirmed: create without `location` → `draft`; with `location` → `live` (gender irrelevant).
- **Change:** added `location` to the `create_profile` tool's `required` params on both Signals agents (a **tool-schema** fix via Raya PATCH, not a prompt-prose change — the Phase-1 prose gate already required location; this was a runtime tool-adherence miss, cf. analyser D25/D40). Also appended the "why" to the `location` param description. Instructions untouched.
- **Files:** Raya tool config (PATCH) on `kkb-hi-signals` + `kkb-kn-signals`; analyser `bug-patterns.md` (new D40).

## 2026-07-29 — KKB Signals bots (Kn + Hi): role-confirm wording (current occupation, not "looking for")
- **Feedback (Parth, call `51c6f63e` — which confirmed all round-3 fixes working: gender skipped when present, correct question count, single ack, one-field update, English values):** the intro role-confirm said "आप अभी [role] का काम देख रहे हैं — क्या आप इसी तरह की जॉब्स देख रहे हैं?" ("you are currently looking for [role] work…"). But the profile `role` is the caller's CURRENT occupation, not what they're seeking. Should be "you ARE a [role] — are you still looking for a [role] job?".
- **Change (both prompts, Profile Handling step 2):** reworded the role-confirm to treat `role` as the caller's current trade — Hi "मैं देख रही हूँ कि आप अभी [role] हैं — क्या आप अभी भी [role] की जॉब देख रहे हैं?"; Kn "ನಾನು ನೋಡ್ತಿದ್ದೀನಿ, ನೀವು ಈಗ [role] ಆಗಿದೀರಿ — ನಿಮಗೆ ಇನ್ನೂ [role] ಥರದ ಜಾಬ್ ಬೇಕಾ?" + an English note that `role` = current occupation, never phrase as "looking for [role]".
- **Files:** both Signals prompts (deployed).
- **Minor open (not yet fixed):** on `51c6f63e` the end-confirm read name/age/role/area but omitted gender though it was on the profile — the confirm rule already lists gender; watch for recurrence.

## 2026-07-29 — KKB Signals bots (Kn + Hi): Phase-2 decide-missing-first + correct count, drop working/studying, gender-skip, one-field updates, single ack
- **Feedback (Parth, call `ce59a84c`):** gender asked though the profile had it; "नोट कर रही हूँ" said twice; the location `update_profile` re-sent gender; Phase-2 dribbled ("दो बातें… एक और बात"); "working/studying" answer went nowhere. Suggested: decide the missing fields ONCE at `get_profile` and ask only those with a correct count.
- **Change (both prompts):** Phase-2 now **decides the question list up-front from the fetched profile** and asks only the MISSING additional fields — **gender ONLY if `item_state.gender` is absent** (skipped entirely if present), granular location always — then announces the **exact count once** and asks one per turn (no "one more"). **Removed the "working / studying" question** (no Signals profile field for it — asking discarded the answer). `update_profile` persist rule tightened to **ONE field per call** (don't re-send gender on the location update). **Double-ack fix:** update `hold_message` is now a NEUTRAL filler ("एक सेकंड" / "ಒಂದು ಕ್ಷಣ"), and the single "noted it down" ack is spoken once in the turn — never in both. Example 1 hold annotations updated to match.
- **Files:** both Signals prompts (deployed). No tool change this round.
- **Note to Parth:** the fields with no Signals API slot (highest qualification, college, exact years, last role, other help, email — plus "working/studying") are being escalated to Srivatsa for API support; until then they are not asked.
- **Analyser:** extends **D38/D39** (ask-only-missing + single-field updates); no new pattern id.

## 2026-07-29 — KKB Signals bots (Kn + Hi): update-persistence fixes (phone double-91, English-only payloads, gender skip, hold-once, eager-persist, labelled end-confirm)
- **Feedback (Parth, live call `7935ce5a` on the Hindi bot):** (1) no Phase-1 questions before apply → confirmed correct: it applied to the LIVE profile `300a4a0b` which already had every minimum-required field; (2) Hindi area line "जैसे कहीं भी चलेगा" was broken (empty `[area]` placeholders); (3) asked gender post-apply though the profile already had it; (4) said "नोट कर रही हूँ" twice; (6) sent `name`/`location` in Kannada/Devanagari script; (7) nothing persisted (working/studying, location); (8) called update before confirming; (9) end-confirm was a bare 3-field list.
- **Root cause (the big one — #3/#7):** `update_profile` was sent `phone:"91XXXXXX0249"` (the profile's stored **12-digit** phone) into a template that did `+91{{phone}}` → `+91919108790249` → API resolved a DIFFERENT user (`user_existed:false`, minted a new draft) then 403 `ITEM_NOT_OWNED_BY_USER` → **no field persisted all call**. Grounded via curl: update needs top-level name/age/phone; partial `item_state` merges; `phone_number` must be E.164 (no `+` → 400); off-enum/empty → 400.
- **Change (tools, both agents):** `create_profile` + `update_profile` `payload_template` phone now `"+{{phone}}"` / `item_state.phone` `"{{phone}}"` (was `"+91{{phone}}"`/`"91{{phone}}"`); `phone` param redefined as the **12-digit** `91 + ${contact_phone}` (per Parth: phone is always the 12-digit number). Eliminates the double-91.
- **Change (both prompts):** payload-value rules — phone = 12-digit (never the bare 10-digit); **all payload values (name/location/role) MUST be English/Latin** (transliterate spoken script → Latin; never send Devanagari/Kannada). Phase-2 gender: **skip if the fetched profile already has `item_state.gender`** (only ask if missing). `update_profile` "noting it down" line said **once** (it is the hold_message; don't repeat it as a spoken turn). **Persist eagerly** (call update right after each answer, don't wait for the end-confirm — caller may drop) **and re-persist on correction**. End confirmation now reads back **ALL** fields **labelled** (name, age, gender, role, location; not the phone). Hindi Case-A area line reworded to "किसी खास इलाके में काम देख रहे हैं, या कहीं भी चलेगा?" (Kn mirrored) so it no longer depends on empty `[area]` placeholders.
- **Files:** both Signals prompts (deployed) + tool configs on `33037201…` and `115b38a5…`.
- **Note (#7):** "working/studying" has no Signals profile field → it stays a call-output capture only (can't be written to the profile); with the phone fix, gender + location now persist via `update_profile`.
- **Analyser:** added **D39** (write fails / duplicate profile from a double-prefixed phone; + non-Latin payload values).

## 2026-07-29 — KKB Signals bots (Kn + Hi): schema-driven Phase-1/Phase-2 field capture + update_profile + enum enforcement + apply-consent line
- **Request (Parth):** (1) apply-consent must state personal details are shared with the company; (2) restructure info-gathering into schema-driven phases — Phase 1 = minimum-required fields validated/filled BEFORE apply (same set for new & returning; fill only gaps), Phase 2 = additional fields POST-apply (flag API-gap fields, move past); (3) persist each gathered field via `update_profile` (silent, "noting down" hold) + a light end-of-call confirmation; (4) enforce the schema dropdown enums (accept only allowed values). Source: `Jobs Signal Schemas Apr 2026.xlsx` ("Job Seeker Specs" Mandatory column).
- **Grounding (curl, dummy numbers):** create WITHOUT gender → still `live` + apply 201 (gender is non-mandatory per schema → moved to Phase 2). `update_profile` = same `POST /admin/participant` with `item_id` + top-level name/age/phone + PARTIAL `item_state` → MERGES (keeps other fields), stays live, no new profile; empty-string fields → 400; **off-enum values → 400 `INVALID_ITEM_STATE`** (API enforces `workExperience`/`gender`/`natureOfJobsInterestedIn` dropdowns).
- **Change (both prompts):** Step 3.5 reframed as **Phase 1 — Minimum Required** (Name, Age, Location, Work Experience, Role, Nature; validate all, fill only missing; gender REMOVED from the pre-apply gate). Post-Application reframed as **Phase 2** — ask Gender here now + working/studying + granular location; **flag & don't ask** the no-API-slot fields (qualification, college, exact-years, last-role, other-help, email) → `fields_not_captured`. `update_profile` rules rewritten to the Signals merge shape + "persist each field as gathered in EITHER phase" + a "noting it down" hold + a one-line end confirmation. Apply-consent line now says personal details will be shared with the company. Added the **enum-mapping block** (map spoken answers to the exact allowed values). Example 1 updated (gender → Phase 2, persist-after-each, end-confirm).
- **Change (both agents' tools):** `create_profile.gender` → optional; added a **`update_profile`** tool (item_id + name/age/phone + partial item_state); `workExperience`/`gender` param descriptions carry the allowed enums.
- **Files:** `KKB/KKB Placeholder Kannada Signals.md` + `KKB/KKB Placeholder Hindi Signals.md` (deployed to `33037201…` + `115b38a5`); tool configs on both agents.
- **Open item to verify on the test call:** whether Raya OMITS unfilled optional `update_profile` params (needed so a partial `item_state` doesn't send empty strings → 400). If it sends empties, switch the rule to "pass the full known item_state".
- **Analyser:** added **D38** (Signals dropdown fields must use the exact schema enum — off-enum values 400 `INVALID_ITEM_STATE`).

## 2026-07-29 — KKB Hindi Signals bot created (Hindi twin of the Kannada Signals clone)
- **Request:** Parth created a new Raya agent `115b38a5-42ef-4082-be69-84a871bb226a` ("KKB Placeholder- Hindi Signals API") and asked for it to be the Hindi version of the Kannada Signals clone — identical structure / new flow / new Signals APIs / all the fixes, differing ONLY in language, with the Hindi lifted from the production KKB Placeholder Hindi bot wherever a line already exists there.
- **Tools (Raya):** already Signals endpoints on the new agent; verified byte-identical to the Kannada clone's final state (compliance array, no `requirements_snapshot`) and flipped `create_profile.item_state.languageSpoken` → `["Hindi"]`. `agent_args` already clean (no `new_seeker`).
- **Prompt:** created `KKB/KKB Placeholder Hindi Signals.md` — structurally byte-identical to `KKB Placeholder Kannada Signals.md` (all English rules / flow / tool payloads / section skeleton copied verbatim), with every SPOKEN line rendered in Hindi. Recurring spoken lines (greeting, job-list formats, age/gender questions, deep-dive, no-match, TTS/number rules, prohibited-language, post-apply, graceful-exit) were LIFTED VERBATIM from the production KKB Placeholder Hindi bot; only Signals-new spoken content (consent ask, the `एक मिनट` hold, the rewritten Signals-flow example dialogue) was translated fresh in the काम की बात voice. Carries every stabilisation fix from the Kannada clone: get_profile-driven silent fetch, memory-is-not-a-fetch guard, neutral opener, lifecycle live-vs-draft readiness gate, **live-item selection (not `items[0]`)**, consent HARD BLOCK (draft ≠ consented), draft-field reuse, ranking relevance filter, `hold_message`, no `requirements_snapshot`, `consent_status` output var.
- **Verification:** automated English-parity check confirmed 1362/1362 lines, memory-injection block verbatim, all 110 section headers aligned, ZERO English drift outside the language-specific Language/Script-Rules zone, and ZERO leftover Kannada script (284 Devanagari lines). Deployed `75466c7f` → `115b38a5`.
- **Files:** `KKB/KKB Placeholder Hindi Signals.md` (new), `raya/agents.json` (added `kkb-hi-signals` target). No analyser change (feature build, not a bug fix).

## 2026-07-29 — KKB Kannada Signals clone: apply to the LIVE profile, not `items[0]` (multi-profile → PROFILE_NOT_LIVE)
- **Feedback/bug:** Parth test call `eaa3f2d1`: apply failed `422 PROFILE_NOT_LIVE: source_item is not live`. (The `requirements_snapshot` backend fix is confirmed working — this is a different, new failure.)
- **Root cause:** the caller has **multiple** Signals profiles — `get_profile` returned `items:[ {2d1510d6 draft}, {300a4a0b live} ]`. The prompt read **`items[0]`** (the stale `draft`) and applied to it → PROFILE_NOT_LIVE, even though a fully **live** profile sat at `items[1]`. Also confirmed via curl: `create_profile` (no `item_id`) mints a NEW live profile each call rather than flipping the existing draft, so a user accumulates draft + live items, and the draft can sit first. Participant-level `user_consent` can read all-`true` while a specific item is still `draft` — readiness is the ITEM's `lifecycle_status`, not `user_consent`.
- **Change (prompt):** rewrote "Reading the get_profile response" + the Pre-Apply readiness gate + HARD GUARD + apply preconditions to **select the profile by lifecycle, not by position**: scan ALL `items` — if ANY is `lifecycle_status: "live"`, use that live item's `item_id` as `profile_id` and apply directly (ignore any stale draft); only if NO item is live (all draft / empty) → `create_profile` (with consent) then apply. Added the explicit rule "never apply to a `draft` item while a live one exists" and "`user_consent: true` ≠ live". Field reuse (age/gender) now reads the selected item (live if present, else the draft).
- **Files:** `KKB/KKB Placeholder Kannada Signals.md` (deployed). Clone-only. Migration guide §A.1/§C.4 to be updated with the multi-profile selection rule.
- **Analyser:** added **D37** (multi-item `get_profile` — bot applied to `items[0]` draft while a live item existed → PROFILE_NOT_LIVE; select by lifecycle, not position).

## 2026-07-29 — KKB Kannada Signals clone: remove `new_seeker` input var + drop `requirements_snapshot` from apply + migration guide
- **Feedback/bug:** Parth: (1) `new_seeker` is dead — the flow always fetches, so remove it as an input variable; (2) the API team is making `requirements_snapshot` optional, so stop passing it (it was only ever `{}`, which Raya drops anyway); (3) write a migration guide capturing every stabilisation step to reuse when porting the other bots to Signals.
- **Change:** (1) removed all `${new_seeker}` references from the prompt (Input Variables + two flow disclaimers) — `agent_args` then auto-dropped `new_seeker` on deploy (it is derived from the prompt's `${...}` vars; the PATCH API rejects `agent_args` directly). (2) removed `requirements_snapshot` from `apply_job` — payload_template AND function params (property + required) — via a `{"tools": …}` PATCH. Apply will 400 until the backend default lands, then works with no further edits. (3) new **`docs/signals-migration-guide.md`** — Signals API details (endpoints/auth/payloads + the `requirements_snapshot`/`{}` trap, lifecycle draft-vs-live, compliance-for-live), the Raya tool-swap mechanics (payload_template behaviour, agent_args derivation, platform `hold_message`), the C.1–C.9 prompt-stabilisation patterns, and a per-bot migration checklist.
- **Files:** `KKB/KKB Placeholder Kannada Signals.md` (deployed), `apply_job` tool on `33037201…` (Raya PATCH), `docs/signals-migration-guide.md` (new). Clone-only.

## 2026-07-29 — KKB Kannada Signals clone (round 2): fetch narrated aloud + ranking padded with irrelevant jobs + draft profile re-asked fields & skipped consent
- **Feedback/bug:** Parth test call `2289c071` (opener + `get_profile` now working). Four issues: (1) the fetch was narrated — "ಸ್ವಲ್ಪ ಕಾಯಿರಿ, ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ನೋಡುತ್ತಿದ್ದೇನೆ" then "ನಿಮ್ಮ ಮಾಹಿತಿ ಸಿಕ್ತು" (must be silent for new AND returning callers); (2) ranking presented an **EV-charging-technician job FIRST** to a confirmed data-entry seeker and padded to 3 with unrelated roles; (3) the returning **draft** profile already had age=25 AND gender=Male, yet the bot **re-asked both**; (4) on the draft path it fired `create_profile` **without asking consent**.
- **Root causes:** (1) two sources — the platform-injected `hold_message` spoken filler on the `get_profile` tool call, AND the prompt's own "ನಿಮ್ಮ ಮಾಹಿತಿ ಸಿಕ್ತು" acknowledgement line. (2) the presentation rule ranked but never *filtered* — it always tried to show 3, so unrelated roles filled the slots and could even sort first. (3)+(4) the `draft`-profile case was handled inconsistently: the model treated the draft as "new → collect everything" (re-asking age/gender the draft already had) yet also as "found → already consented" (skipping the consent gate).
- **Change (prompt):** (1) new `hold_message` rule — a short NEUTRAL hold **"ಒಂದು ನಿಮಿಷ"** (one moment) for `get_profile` and `create_profile`, never a profile-revealing line (a generic "one moment" covers latency without announcing a lookup; only `apply_job` carries its own bridge line). *(Corrected from an initial "must be empty" — Parth wanted the neutral one-moment hold, not dead air; the three earlier bans on "ಒಂದು ನಿಮಿಷ" were reconciled so only profile-revealing lines stay banned.)* Removed the "ನಿಮ್ಮ ಮಾಹಿತಿ ಸಿಕ್ತು" acknowledgement everywhere → returning-caller opener now greets by name and goes straight to the role check, and "ಮಾಹಿತಿ ಸಿಕ್ತು"/"ಪ್ರೊಫೈಲ್ ಸಿಕ್ತು" are hard-banned in EVERY scenario. (2) added a **Relevance filter** to the Default Presentation Rule + Step 2 — when the role is known, present ONLY role-relevant jobs (same role + same-family), best-fit first, and NEVER pad to 3 with unrelated roles (1 relevant → show 1). (3) reframed the NOT-READY block to **reuse every `item_state` field the draft already carries** (age/gender/name/location/experience) — ask only genuinely-missing fields. (4) made the consent gate a **HARD BLOCK**: `create_profile` must not fire until consent is asked + granted this call; a found `draft` is NOT consented (that's why it's draft) — never skip the ask.
- **Files:** `KKB/KKB Placeholder Kannada Signals.md` (deployed `087e7f50`). Clone-only.
- **Note:** apply still 400s on `requirements_snapshot` even with the placeholder + model passing `{}` (Raya drops it) — confirmed backend-only; Parth has escalated the server-side default to the team.
- **Analyser:** added **D34** (platform `hold_message` narrates a "silent" tool call), **D35** (draft profile handled inconsistently — re-asks known fields and/or skips consent), **D36** (ranking pads to N with irrelevant-role jobs instead of filtering to relevant).

## 2026-07-29 — KKB Kannada Signals clone: memory-substitution killed the fetch (unnatural opener + get_profile never fired) + `requirements_snapshot` undefined on apply
- **Feedback/bug:** Parth test call `ebb05fd1` on the Signals clone: bot opened with "ಒಂದು ನಿಮಿಷ" (a stall) then immediately greeted "ಪಾರ್ಥ ಅವರೇ" by name + named the role — an unnatural start — and `get_profile` **never fired** (the ONLY tool call in the whole transcript was `apply_job`). It spoke the name/role/profile_id from `${contact_memory}`, so it skipped the fetch, skipped consent, and applied with a memory-sourced id. Separately, `apply_job` 400'd: `body/requirements_snapshot Invalid input: expected record, received undefined`.
- **Root cause (opening/fetch):** legacy "Introduction Priority Rule (Strict Override)" told the model *"if ANY usable prior context exists [in `${contact_memory}`], you MUST resume the previous journey"* + three memory-personalised greeting variants. This directly contradicted the get_profile-driven flow below it — the model resumed from memory and never called the fetch tool. Memory was being used as a substitute for `get_profile`.
- **Root cause (apply 400):** `apply_job`'s `payload_template` had `"requirements_snapshot": {}` (a literal empty object). Raya **prunes empty-object literals** at send time → the field arrived `undefined` → 400. Proven on the live Signals API: `{}` → 201 (the ONLY success); omitted/`null` → 400; any non-empty object (`{"message":"String"}`, `{matched:[]}`) → 422 "must NOT have additional properties". So the one value the API accepts is the one Raya won't transmit as a literal.
- **Change (prompt, AGNOSTIC opening logic):** replaced the memory-resume intro rules with a fixed **Opening Rule** — one neutral greeting + "are you looking for a job?" on EVERY call (no name / no saved role / no resume line / no stall line in the opening turn); added a hard guard that `${contact_memory}` is background context only, **not** a `get_profile` result — the name/role/readiness may be spoken only after the fetch tool actually returns THIS call; reinforced the fetch mandate that reading memory is NOT a fetch. Memory-injection block preserved verbatim.
- **Change (Raya tool config):** `apply_job.requirements_snapshot` switched from the literal `{}` (which Raya drops) to a whole-value placeholder `"{{requirements_snapshot}}"` + a new required `requirements_snapshot` param whose description forces exactly `{}` — a bare whole-value placeholder is substituted typed by many template engines (unlike an embedded one). Fallback if Raya stringifies it: Srivatsa defaults missing `requirements_snapshot` → `{}` server-side (1-line, curl-proven).
- **Files:** `KKB/KKB Placeholder Kannada Signals.md` (prompt, deployed `4f730d45`) + `apply_job` tool config on agent `33037201…` (Raya PATCH, snapshot `raya/snapshots/kkb-kn-signals.tools.pre-reqsnap.json`). Clone-only — no Hindi/base twin.
- **Analyser:** added **D32** (memory block used as a substitute for `get_profile` → premature name/role + fetch skipped) and **D33** (Raya prunes literal empty-object `{}` from `payload_template` → required object field arrives `undefined`).

## 2026-07-27 — KKB (base, Hi+Kn): new-caller apply — `apply_job` batched with `create_profile` → empty `profile_id` (apply fails)
- **Feedback/bug:** Parth: on the base KKB Kannada, a new-caller apply failed — the bot correctly called `create_profile`, but `apply_job` went out with no `profile_id`. Grounded in `kkb-kn-out` call `40c8e3db` (`new_seeker=Yes`): tools = `[create_profile, apply_job]`; `apply_job` args `{"job_id":"4d52479b…","profile_id":""}` — **empty** `profile_id`. (Returning-caller path `61d713a6` works: `get_profile` → `apply_job` with a real id.)
- **Root cause:** the apply-sequence prose told the model to run `create_profile` + `apply_job` "back to back" in "ONE clean sequence in a single turn" / "for the whole sequence" (Hindi lines 387, 889). So the model emitted BOTH tool calls in one batch, and `apply_job` was built BEFORE `create_profile`'s result (the `profileId`) existed → `profile_id=""`. The id only exists after `create_profile` responds.
- **Change (AGNOSTIC — English rule verbatim Hi↔Kn):** rewrote both lines so the new-caller apply is TWO steps: `create_profile` FIRST → WAIT for its result → then, as the NEXT action, read the `profile_id` from that result and call `apply_job` with it. Explicit: never emit `create_profile` + `apply_job` in the same turn/batch; never send `apply_job` with an empty `profile_id`. Returning-caller path (single `apply_job`) unchanged.
- **Files:** `KKB/KKB Placeholder Hindi.md` + `KKB Placeholder Kannada.md`. Deployed kkb-hi-out (`614e7c61`) + kkb-kn-out (`2944cf61`). Awaiting a post-deploy new-caller call to confirm.
- **Analyser:** added **D31** (new-caller create→apply batched in one turn → `apply_job` empty `profile_id`).
- **Flag:** Maya (out+in) and the Signals clone carry the same "single turn / back to back / whole sequence" apply language → same latent bug (Maya gate + Signals parked — port on approval).

## 2026-07-27 — NEW: "KKB Kannada Signals API" clone — swap 3 tools (ONEST → Signals) + prompt response-mapping
- **What:** Integrated the cloned agent **"KKB Placeholder- Kannada Signals API"** (`33037201-78ce-405d-b509-a3b6934e20f1`) with the EkStep **blue_dot Dev** Signals APIs (`https://signals.bluedotseconomy.org`), replacing its 3 ONEST/dhiway tools. The bot's spoken behavior/flow is unchanged; only the 3 tool endpoints + the response-reading prompt sections changed.
- **Tool configs** (live in the Raya agent's `tools.llm_tools[]`; PATCHed via the API — proven to round-trip byte-identical incl. per-field descriptions/types, without wiping `instructions`):
  - `get_profile` → `GET /api/v1/admin/participant` (headers `x-api-key` + `x-acting-org-id`); query `phone_number=91XXXXXXXXXX` (snake_case key required; `+` optional — sent without).
  - `create_profile` → `POST /api/v1/admin/participant` with a `payload_template` mapping name/phone/age/gender/role/workExperience/location into `{network:blue_dot, domain:seeker, item_type:profile_1.0, item_state{…}}`; `languageSpoken` hardcoded `["Kannada"]` (Signals requires a real array), `natureOfJobsInterestedIn` defaulted `"Full-time"`, terms/privacy/channel fixed.
  - `apply_job` → `POST /api/v1/action/perform` mapping `profile_id → source_item.item_id`, `job_id → target_item.item_id`, `acting_as_user_id → user_id` + hardcoded `action_type:apply`, item networks/domains/types, `consent{acknowledged:true, version:1}`.
- **Prompt** (`KKB/KKB Placeholder Kannada Signals.md` — pulled from live, surgically edited, deployed): rewrote **Reading the get_profile response** for the new `{user_id, items[]}` shape — `profile_id = items[0].item_id`, `acting_as_user_id = top-level user_id`, fields from `items[0].item_state.*` (`nameOfJobRolesInterestedIn`, `workExperience`, `natureOfJobsInterestedIn`, …); `create_profile` new field set (dropped `agentId`/salary/ITI/workHours); `apply_job` now passes `profile_id` + `acting_as_user_id` + verbatim `job_id` UUID; get_profile phone → `phone_number` 91XX (no `+`).
- **Grounded (direct curl to Signals Dev):** fetch `{user_id, items[]}` ✓; create HTTP 200 with the nested/typed body ✓; apply contract validated (only 422s: `MISSING_ACTING_AS_USER_ID` → so `acting_as_user_id` is REQUIRED and carried from the fetch/create `user_id`; and `PROFILE_NOT_LIVE`).
- **Files:** `KKB/KKB Placeholder Kannada Signals.md` (new), `raya/agents.json` (added `kkb-kn-signals` target). Signals secrets live only in the Raya tool headers — never committed.
- **OPEN (LitWiz):** `PROFILE_NOT_LIVE` — API-created seeker profiles aren't "live" and can't apply until published; blocks end-to-end apply verification. Escalate.
- **Flags:** `update_profile` prose remains but no `update_profile` tool is wired (out of the "3 APIs" scope); `natureOfJobsInterestedIn` defaulted to "Full-time"; `languageSpoken` hardcoded `["Kannada"]`; a live test call is still needed to confirm Raya interpolates the nested `payload_template` at runtime.

## 2026-07-27 — KKB (+Maya): apply_job stripped the job_id UUID hyphens → 404 "Job not found" (job_id-verbatim rule)
- **Feedback/bug:** Parth: "check most recent KKB inbound call — the job ID was invalid because the bot passed the job id without the dashes in between." Grounded in `kkb-hi-in` call `8ddcaa5a` (07-27 08:14, Parth's own number): `get_profile` fired and `profile_id` was a proper UUID (both prior fixes holding), but `apply_job` sent `job_id:"eab4805a7d5f4bf2b1a91fd34521550d"` — the 32-hex UUID with all four hyphens **stripped** → backend 404 `{"error":"Job not found"}`. The Job Inventory stores it correctly as `eab4805a-7d5f-4bf2-b1a9-1fd34521550d`; the model mangled it on emit. No existing rule required passing the `job_id` verbatim.
- **Change (AGNOSTIC — identical English rule across all languages):** in the `apply_job` payload rules (the "Use the `job_id` field…" line + the payload-field bullet), added: pass the `job_id` EXACTLY as it appears — a full hyphenated UUID (8-4-4-4-12), copy every character including all four hyphens, never strip/add/reformat; a hyphen-stripped 32-char run is rejected with "Job not found" (404).
- **Files:** KKB Placeholder Inbound Hi/Kn + Placeholder Hindi/Kannada (outbound) — propagated to ALL apply-capable KKB variants (identical latent gap; pure-additive). Deployed all 4, read-back verified. Also applied to Maya (see `Maya/CHANGELOG.md`). Awaiting post-deploy call.
- **Analyser:** added **D30** (apply_job strips UUID hyphens → "Job not found"; detection = read `tool_calls` args, flag a 32-char no-hyphen `job_id`; fix = job_id-verbatim rule). Sibling to D28.

## 2026-07-27 — KKB inbound: `get_profile` fired 0/8 — un-bundle greeting + fetch into TWO turns (greet, then fetch) (rows 15/42/65)
- **Feedback/bug:** Parth: "KKB inbound is still failing to call the get profile API — implement similar fix like we did for Maya; say the intro line, THEN fetch, so the flow is smooth." Grounded in 8 live `kkb-hi-in` calls (07-26/07-27): `get_profile` fired in **0 of 8** — every call the model SPOKE a fetch-narration ("एक मिनट, आपकी जानकारी निकल रही है" / "अभी आपकी जानकारी मिल रही है") but never emitted the tool call; in call `34f1f587` it then sent `apply_job` a fabricated UUID → 404. Root cause: the DECISIVE ROUTER said "fire `get_profile` SILENTLY in that same turn [as the greeting]" — bundling a spoken greeting + a silent tool call into ONE turn makes the model keep the speech (narrate) and drop the tool. Maya inbound greets on turn 1 and fires `get_profile` on turn 2 (a separate action) and works — that's the mechanism ported.
- **Change (AGNOSTIC — English rule verbatim H↔K; only the quoted forbidden-narration strings adapted):** restructured the greeting→fetch flow into TWO turns: (1) added a "the greeting is ONE turn ending in ONE question; wait; do NOT fetch here" beat after the greeting scripts; (2) rewrote the DECISIVE ROUTER to "greet first, then fetch (two separate turns)" — Turn 1 greeting only (no tool, no narration); Turn 2's FIRST action is a REAL, mandatory, tool-only `get_profile` call before answering the caller / any discovery / jobs ("NO conversation before it returns"); (3) replaced the "same turn" bundling rule with a clean-greeting rule + expanded the forbidden-narration ban to the actual observed strings (both greeting turn and fetch turn); (4) harmonized the get_profile Tool Call Rules "first action" line to "on your turn immediately after the greeting" so it can't read as turn-1. Deliberately NOT the D25 "silent/invisible" reframe (that regressed firing) — the fetch stays a loud mandatory tool call, just on its own turn. Smoother than Maya (Maya still prepends a fetch-narration; KKB now bans it).
- **Files:** `KKB/KKB Placeholder Inbound.md` (Hindi source), `KKB/KKB Placeholder Inbound Kannada.md` (mirrored). Deployed kkb-hi-in (sha 62967128) + kkb-kn-in (sha e1a58e0a), read-back verified in-sync. Awaiting post-deploy call to confirm firing.
- **Analyser:** added **D29** (greeting/fetch bundling → narrate-or-skip; fix = un-bundle into two turns) unifying B2↔D25↔D7; cross-referenced from B2 fix-direction, D25, and D7 "Seen in".
- **Maya:** NOT touched — its `get_profile` already fires (it's the reference). Flagged: Maya inbound has the same narration-prepend weirdness; can be smoothed with the same two-turn/clean-greeting fix if wanted (Maya's firing is historically fragile → flag-and-ask).

## 2026-07-27 — KKB + Maya: apply_job used numeric `id` instead of `profileId` UUID → 404 "Invalid or missing profile_id" (apply-fail root cause, rows 15/42/65)
- **Feedback/bug:** Grounded in Maya call 46d9f776 by reading the tool-call ARGS (not just results): create_profile returned `{'id': 5051, 'profileId': '2b51fd94-…'}`, then apply_job was sent `profile_id:"5051"` (the numeric top-level id) → backend 404 `{"error":"Invalid or missing profile_id"}`. This is a large share of the "apply failing" P1s (rows 15/42/65), previously mis-filed as pure backend.
- **Change:** In the apply_job payload rules (and the new-caller apply clause), specify that on the create_profile path the `profile_id` is the `profileId` UUID field — NEVER the numeric top-level `id`. (get_profile's top-level `id` already IS the UUID, so the returning-caller path was correct and unchanged.)
- **Files:** KKB Placeholder Hindi/Kannada.md + Inbound Hindi/Kannada.md, Maya Hindi.md + Maya Inbound.md (6 apply-path files; English rule identical across languages). Deployed all 6, verified in-sync. Awaiting post-deploy call.

## 2026-07-27 — KKB: port Maya's call-wide "Never Speak Tool Payloads Aloud" guard (row 70)
- **Feedback/bug:** Row 70 (payload spoken during profile creation) — confirmed occurred in Maya on 07-21. Maya already had a call-wide "NEVER SPEAK JSON ALOUD" hard guard; KKB had only the apply-turn one, leaving the create_profile-return moment exposed.
- **Change:** Added a call-wide "# Never Speak Tool Payloads Aloud (Critical — No Exceptions)" section to all 4 KKB files (before the Hallucination Guard) — no JSON/payload/field-names/id/profileId/job_id/metadata/raw tool result spoken at ANY point. Deployed, in-sync.

## 2026-07-27 — KKB inbound: apply-loop fix (row 68) — stop bridge re-speak on failure + no re-fire of same failed job
- **Feedback/bug:** Sheet row 68 (P1). Live call 4663a367 (2026-07-26): on a failed apply the bot re-spoke the apply bridge/hold ("...अप्लाई कर देती हूँ" / "एक बार apply कर देती हूँ") at the head of the failure message with no new tool call, and re-fired apply_job on the SAME already-failed job_id across repeat user requests.
- **Change:** Two additive guards in Apply Failure Handling: (1) failure message must begin DIRECTLY with the base failure line — never re-speak the bridge/hold on the failure turn; (2) a job that has already FAILED apply_job in this call is DONE — never re-fire apply_job for that same job_id, go straight to interest-noted/HR/alternate-job path.
- **Files:** KKB/KKB Placeholder Inbound.md + KKB/KKB Placeholder Inbound Kannada.md (English scaffolding identical; bridge examples translated). Deployed both, verified in-sync. NOTE: not yet live-confirmed — no post-deploy call traffic exists yet.
- **Ported to:** Maya (see Maya/CHANGELOG.md).

## 2026-07-27 — KKB Kannada: reconcile Ghaziabad canonical spelling (no-break follow-up)
- **Feedback/bug:** The Canonical Location Spellings section (added earlier 2026-07-27) set Ghaziabad canonical to ಗಾಜಿಯಾಬಾದ (no virama), but all ~15 sample dialogues use ಗಾಜಿಯಾಬಾದ್ (with virama U+0CCD) — the file violated its own new rule. Caught by a regression check.
- **Change:** Set the Kannada canonical for Ghaziabad to ಗಾಜಿಯಾಬಾದ್ (matches the dialogues) in both KKB Placeholder Kannada.md + KKB Placeholder Inbound Kannada.md. Deployed, verified in-sync.

## 2026-07-24 — KKB: Canonical Location Spellings section (city mispronunciation)
- **Feedback/bug:** Sheet rows 69 (KKB HE) & 71 (KKB Ghaziabad) — place names (Ghaziabad, Indirapuram, Mohan Nagar, Rajendra Nagar, Sector 5) mispronounced; team asked for a canonical-spelling section.
- **Change:** Added a "## Canonical Location Spellings" subsection under Language & Script Rules pinning the exact canonical spelling for each place and forbidding dynamic/phonetic transliteration (overrides general transliteration + phonetic-matching rules). Devanagari canonical forms in the Hindi files; Kannada-script forms in the Kannada files (matching each file's existing ಗಾಜಿಯಾಬಾದ/ಇಂದಿರಾಪುರಂ usage).
- **Files:** KKB/KKB Placeholder Hindi.md, KKB/KKB Placeholder Kannada.md, KKB/KKB Placeholder Inbound.md, KKB/KKB Placeholder Inbound Kannada.md. English scaffolding byte-identical across all 4; place spellings language-adapted.
- **Deploy:** Queued — Raya API (v1.getraya.app) was down at time of edit; deploy + live verification pending its recovery.

## 2026-07-23 — KKB inbound: ROLLED BACK the turn-1 fetch-narration structural fix (caused get_profile to stop firing)
- **Feedback/bug:** Live 2026-07-23 calls on b6222233 showed get_profile never firing → apply_job called with no fetched profile → apply failed (plus a separate backend HTTP 404 on the ONEST apply endpoint). The narration prepend also still occurred ("एक सेकंड। नमस्ते…").
- **Root cause:** The prior day's structural narration fix reframed the mandatory get_profile tool call as "silent / invisible / produces no speech / nothing to acknowledge / not a conversational turn" and paired it with "turn 1 is the greeting and NOTHING else." The model generalised this to mean the tool call itself was skippable and dropped it. The fix both failed its own goal (prepend persisted) and broke the core fetch→apply flow.
- **Change:** Restored the pre-fix snapshot (versions/KKB/2026-07-22_221958__pre-fetch-narration-structural), which keeps the strong "get_profile is your FIRST action" mandate without the de-emphasising language. Redeployed. This supersedes the prior "structural fix" entry.
- **Files:** KKB/KKB Placeholder Inbound.md, KKB/KKB Placeholder Inbound Kannada.md (reverted). Hindi b6222233 reverted + in-sync (sha 2ced8c59); Kannada 4ac90bf1 redeploy pending (Raya origin 520/521 outage — background retry).
- **Open:** (1) A live test call is needed to confirm get_profile fires again on the restored version. (2) The turn-1 narration prepend remains unsolved as a prompt problem — the durable fix is a Raya platform static-first-message / pre-call fetch automation, not more turn-1 instruction weight. (3) Backend: ONEST apply 404 + Raya origin instability to raise with LitWiz.

## 2026-07-22 — KKB inbound: structural fix for turn-1 fetch-narration prepend
- **Feedback/bug:** On a live b6222233 call (2026-07-22 16:45) the agent prepended fetch-narration before the greeting — "अभी आपकी जानकारी मिल रही है। नमस्ते…". 3rd recurrence; the two prior fixes banned specific phrases and the model invented a new synonym each time (whack-a-mole). Reconcile confirmed live==repo, so the phrase-ban was live and still failed.
- **Change:** Replaced the phrase-ban with a structural fix (validated by a 3-lens adversarial red-team before deploy): (1) whitelist turn 1 — entire first spoken output is EXACTLY one greeting variant, no token before/between/after; (2) reframe get_profile as a "silent background system action, not a conversational turn" (dropped the unverified "no dead air" claim); (3) category ban covering BEFORE/BETWEEN/AFTER positions + bare fillers, not a phrase list; (4) all-position causal stop; (5) positive exemplar of a correct turn 1; (6) subordinated the "FIRST action" framing in the DECISIVE ROUTER + get_profile rules to "silent background step, never spoken"; (7) scoped the "आपकी जानकारी मिल गई" acknowledgement to a LATER turn so it can't license turn-1 narration.
- **Files:** KKB/KKB Placeholder Inbound.md, KKB/KKB Placeholder Inbound Kannada.md (mirrored; English scaffolding byte-identical, spoken examples/exemplar adapted). Deployed b6222233 (sha 61162c10) + 4ac90bf1 (sha 9d98a31c), read-back verified.
- **Open:** Recommended durable fix — a Raya platform static/first-message field (deterministic opening) — pending LitWiz confirmation; instruction-only is probabilistic.

## 2026-07-22 — KKB inbound (Hi+Kn): greeting-first / silent get_profile — fix the source, revert the phrase-ban misdiagnosis
- **Feedback/bug:** On KKB inbound, after "hello" the bot prepended "ठीक है, मैं आपकी जानकारी देख लेती हूँ" before the greeting (grounded in a user-pasted 2026-07-22 4:59pm transcript). Root cause: the get_profile rule said "Deliver the greeting naturally **alongside it**" (alongside the silent fetch) — which invited a fetch-narration line to ride along with the greeting. (A first attempt that phrase-banned the narration line was a misdiagnosis — it banned a paraphrase without checking the transcript — and has been reverted.)
- **Change:** Fixed at source in both KKB inbound files — the FIRST spoken turn is now EXACTLY the greeting (nothing prepended); get_profile fires silently in the same turn; added an explicit ban on prepending any acknowledgement/fetch-mention before the greeting. Reverted the earlier phrase-ban bullet (symptom-level, superseded by the source fix). Maya inbound lacked the "alongside it" phrasing, so it never had this bug — a KKB-inbound-specific divergence. Deployed kkb-hi-in + kkb-kn-in (echo-verified).
- **Files:** KKB/KKB Placeholder Inbound.md, KKB/KKB Placeholder Inbound Kannada.md

## 2026-07-22 — KKB inbound (Hi+Kn): remove residual outbound permission-ask that contradicted the silent-fetch router
- **Feedback/bug:** Reported "old seeker can't fetch profile / new seeker asked to fetch" on KKB Inbound Hindi. The sheet's latest calls (2026-07-14) ran on an OLD version (outbound greeting "मैं गवर्नमेंट की तरफ़ से कॉल कर रही हूँ" + a permission ask + no get_profile-first router) — confirmed via a live GET that the CURRENT deployed version already has the inbound greeting + the get_profile-driven DECISIVE ROUTER. BUT the current prompt still carried a real internal contradiction: the Profile Wording Rules listed a "Permission ask (before get_profile)" spoken line and an "if the user declines the permission ask" clause — both leftovers from the outbound lineage — directly conflicting with the router's "you may NOT ask permission; get_profile runs silently first". That residue is the most likely trigger for the "new seeker asked to fetch" symptom in the current version.
- **Change:** Neutralized the residue in both KKB inbound files: replaced the "Permission ask (before get_profile)" spoken-line entry with an explicit "No permission ask on inbound — never ask '…बेसिक जानकारी देख सकती हूँ?'; get_profile is silent" note, and removed the "Same rule if the user declines the permission ask" clause. English identical across languages; only the quoted banned line differs (Hi/Kn). Deployed kkb-hi-in + kkb-kn-in (echo-verified). NOTE: Maya inbound carries the identical residual permission-ask line (flagged to the user; not changed here per scope).
- **Files:** KKB/KKB Placeholder Inbound.md, KKB/KKB Placeholder Inbound Kannada.md

## 2026-07-22 — KKB outbound (Hi+Kn): hallucinated apply — port APPLY-TURN INTEGRITY guard
- **Feedback/bug:** Reported on KKB Kannada; grounded in live call 8899d364 (new_seeker "No", returning caller): the bot said "ಅಪ್ಲೈ ಆಗಿದೆ" (applied) and even narrated "ನಿಮ್ಮ ಅರ್ಜಿ ಸಲ್ಲಿಸುತ್ತಿದ್ದೇನೆ" (submitting your application) but NEVER called apply_job (tools show only get_profile:RET); call_output recorded applied_to_job "Yes" — a hallucinated apply. Reported as Kannada-specific; investigation found NO functional Hi/Kn guard diff (the anti-hallucination guards were already in sync, and job_recommendations is a documented prose alias for ${recommendations}, not a broken variable). The real gap: KKB OUTBOUND (both languages) lacked the strongest APPLY-TURN INTEGRITY block that Maya + KKB inbound already carry; the weaker Kannada instruction-following surfaced it first (Hindi not immune).
- **Change:** Ported the APPLY-TURN INTEGRITY block into the apply_job Rules of KKB outbound Hi+Kn: never render a tool call/payload/JSON as speech; **never narrate the apply as if it is happening (no "submitting/sending your application" line — the only apply action is the apply_job tool call)**; create_profile success is not an application; the success line ("अप्लाई हो गया है" / "ಅಪ್ಲೈ ಆಗಿದೆ") requires a real apply_job success result that turn. English identical across languages; only the two quoted spoken examples differ. Deployed kkb-hi-out + kkb-kn-out (echo-verified).
- **Files:** KKB/KKB Placeholder Hindi.md, KKB/KKB Placeholder Kannada.md
- **Ported from:** Maya (2026-07-20 APPLY-TURN INTEGRITY)

## 2026-07-22 — KKB inbound (Hi+Kn): profile payload said out loud — port Maya's APPLY-TURN INTEGRITY guard
- **Feedback/bug:** Sheet row 45 — while creating the profile the KKB inbound bot read the raw payload/JSON out loud instead of a natural confirmation. KKB inbound had no explicit "never speak the payload/JSON" guard.
- **Change:** Ported Maya's APPLY-TURN INTEGRITY guard into the create_profile Tool Call Rules of both KKB inbound files: never write a tool call/payload as speech (a { or field name in spoken output is a hard failure; say only a natural confirmation while creating the profile); create_profile success is not an application; the apply success line requires a real apply_job success that turn. Pure-English clause, byte-identical Hindi & Kannada. Deployed kkb-hi-in + kkb-kn-in (echo-verified).
- **Files:** KKB/KKB Placeholder Inbound.md, KKB/KKB Placeholder Inbound Kannada.md
- **Ported from:** Maya (2026-07-20 APPLY-TURN INTEGRITY)

## 2026-07-22 — KKB (Hi+Kn) outbound: enforce experience collection for new callers (port Maya's D21 gate)
- **Feedback/bug:** Sheet rows 24/58 (KKB Ghaziabad) — bot does not ask experience for new callers. KKB's pre-apply gate hard-blocked only age+gender; experience was optional (soft inline), with no hard precondition at the create_profile call site.
- **Change:** Added a NEW-CALLER HARD BLOCK in Step 3.5 (name + experience must be collected before create_profile for new_seeker "yes" / no-fetched-profile callers; name uses ${contact_name} if present else asks; fresher/0 years counts as known) and a HARD PRECONDITION at the create_profile "MANDATORY FIRST STEP" call site (verify name/experience/age/gender before create_profile; never ask experience/age/gender AFTER create_profile ran). Hindi source-of-truth, mirrored verbatim to Kannada (English identical; only the quoted name-ask + experience question differ per language). Deployed kkb-hi-out + kkb-kn-out (echo-verified).
- **Files:** KKB/KKB Placeholder Hindi.md, KKB/KKB Placeholder Kannada.md
- **Ported from:** Maya (2026-07-20, the D21 new-caller 5-field collection gate)

## 2026-07-22 — KKB (Hi+Kn) outbound: apply-loop — bridge line said once (port Maya causal clause)
- **Feedback/bug:** Sheet rows 14/61 (KKB Kannada) — bot repeats "apply kr rhi hu" / "apply kar deti hu" 3-4 times before confirming or failing. KKB had only a flat "never repeat the bridge" prohibition, missing the causal mechanism.
- **Change:** Ported Maya's causal bridge clauses into KKB's "Conversational bridge before apply" Rules bullet and the Step 4 "Run the application as ONE clean sequence" paragraph: the bridge is NOT the application; the moment it is said, apply_job MUST be emitted the same turn; if about to say the bridge a second time, call apply_job instead — repeating it is never a stand-in for the tool call. Pure-English clause (no spoken line), byte-identical Hindi & Kannada. Deployed kkb-hi-out + kkb-kn-out (echo-verified). NOTE: same clause is latent in KKB inbound (Hi+Kn) — flagged for a separate pass, not done here.
- **Files:** KKB/KKB Placeholder Hindi.md, KKB/KKB Placeholder Kannada.md
- **Ported from:** Maya (2026-07-20 apply_job bridge rules)

## 2026-07-22 — KKB (Hi+Kn): forking broken — new_seeker not steering the branch; port Maya's value-surface fix
- **Feedback/bug:** Reported on KKB Kannada, confirmed in live kkb-kn-out calls (agent_args inspected): calls with new_seeker "Yes" fired get_profile (2026-07-21 09:44 and 07-20 15:50) — the "yes" path forbids get_profile. Same root cause found and fixed on Maya earlier: the DECISIVE ROUTER referenced ${new_seeker} only abstractly, so the model followed structural dominance instead of the actual value. KKB never received Maya's value-surfacing fix.
- **Change:** Ported the Maya fix to KKB's DECISIVE ROUTER (agnostic logic → applied to Hindi source-of-truth, mirrored verbatim to Kannada; only the one quoted spoken "no profile" line differs per language). The router now surfaces the interpolated value inline ("the new_seeker value for THIS call is: ${new_seeker}"), makes the NO branch (fetch) the safe default for any value that is "no"/blank/unclear/unsubstituted, orders NO-branch first, and adds "branch strictly on the value shown, never by habit". Deployed kkb-hi-out + kkb-kn-out (both echo-verified).
- **Files:** KKB/KKB Placeholder Hindi.md, KKB/KKB Placeholder Kannada.md
- **Ported from:** Maya (2026-07-20 new_seeker value-surface + default-to-fetch fix, analyser class D22)

## 2026-07-20 — KKB seeker gates round 2b: proxy carve-out + new-caller multi-apply
- **Feedback/bug:** Adversarial review of the round-2 age/gender-lock fix flagged two residual issues across all KKB seeker files. (1) The lock was absolute, so a proxy caller switching to a different candidate mid-call would carry the first person's age/gender onto the second. (2) A brand-new caller applying to a 2nd job in one call would re-run `create_profile` (duplicate profile) + re-ask name/experience.
- **Change:** (1) Scoped the lock to the SAME candidate — a proxy switching to a different person re-establishes age/gender. (2) Added a once-per-call `create_profile` guard — after the first mint, a later apply reuses the returned `profile_id` via `apply_job` only. (Analyser D9 refined, D11 added.)
- **Files:** KKB Placeholder Hindi.md, KKB Placeholder Kannada.md, KKB Placeholder Inbound.md, KKB Placeholder Inbound Kannada.md

## 2026-07-20 — KKB (out+in, H+K): richer Apply Failure Handling — don't dead-end a failed apply
- **Feedback/bug:** On `apply_failed` the bot just said "apply नहीं हुआ, retry or another option" and often dead-ended, leaving an interested seeker with nothing.
- **Change:** Replaced the one-line Apply Failure Handling in all 4 KKB seeker files with: own the failure (our-side, technical) + note interest, then exactly ONE recovery path — outbound (no `hr_contact`) offers ONE alternate job then a callback; inbound (has `hr_contact`) offers the HR contact first, else one alternate job, else a callback. Added hard bans (no over-apology / blaming the seeker / "call later" / looping to a third apply / speaking "profile") and a system-side logging note the bot never narrates. English identical within each language twin; spoken lines Hindi/Kannada. (Analyser D15.)
- **Files:** KKB Placeholder Hindi.md, KKB Placeholder Kannada.md, KKB Placeholder Inbound.md, KKB Placeholder Inbound Kannada.md

## 2026-07-20 — KKB matching: role synonym+family grouping, city anchor, interview-readiness
- **Feedback/bug:** Sheet rows 35 (role-synonym: "customer service" found no jobs though customer-support was in the pool), 21/23 (customer-service/sales/crew treated as separate buckets → false "no X jobs" + inconsistent categorisation), 37 (GZB seeker shown Noida/Meerut upfront → drop), 43 (feature: capture interview-readiness before apply).
- **Change:** (35+21/23) Added a combined role synonym + customer-facing-family matching rule to the outbound Default Presentation Rule and the inbound ranking rule (cashier kept distinct). (37) Added a city-anchor rule to all 4 KKB files — the stated city anchors the first batch, other cities only after / on-request / when-too-few (preference, not a hard filter). (43) Added an interview-readiness question in Step 3.5 (once per call, never blocks apply) + a new `ready_for_interview` output variable in KKB Output.md. (Analyser D12/D13 added; 43 is a feature — no analyser entry.)
- **Files:** KKB Placeholder Hindi.md, KKB Placeholder Kannada.md, KKB Placeholder Inbound.md, KKB Placeholder Inbound Kannada.md, KKB Output.md
- **Ported from:** KKB Inbound (the synonym rule, re-domained to `${recommendations}` for outbound)

## 2026-07-20 — Age/gender re-ask root cause: extract at read time across all profile records
- **Feedback/bug:** The raw `get_profile` dump for the test number showed the profile DOES carry age (`whatIHave.age`) and gender (`metadata.gender`), yet the bot still asked on the first apply — inconsistently (skipped one call, asked the next). Root cause: the number has many duplicate profile records with the fields scattered (the most-recent may be a placeholder while age/gender sit on another record), and the bot re-parsed the nested JSON at the apply gate — unreliable. The earlier "lock" declared the fields known but never forced extraction at read time.
- **Change:** At profile-read time, extract age and gender from the `get_profile` result across ALL returned records (a field is KNOWN if any record carries it) and commit them as known for the whole call — do not re-derive at the apply gate. Added to "Reading the get_profile response" in all KKB seeker files. (Analyser D9 sharpened.)
- **Files:** KKB Placeholder Hindi.md, KKB Placeholder Kannada.md, KKB Placeholder Inbound.md, KKB Placeholder Inbound Kannada.md

## 2026-07-20 — Age/gender lock persists across every apply (round 2, all KKB seeker gates)
- **Feedback/bug:** The round-1 profile re-check held on the first apply but was proven (on Maya Inbound) to fail on a SECOND apply in the same call — the skip was a per-gate re-derivation, not a persisted fact. Same weakness in all KKB seeker files.
- **Change:** Locked the profile's known fields (esp. age/gender) the moment `get_profile` returns — the lock does NOT reset between applications — and strengthened the HARD BLOCK so the KNOWN status persists across every apply in the call. (Analyser class D9 strengthened.)
- **Files:** KKB Placeholder Hindi.md, KKB Placeholder Kannada.md, KKB Placeholder Inbound.md, KKB Placeholder Inbound Kannada.md

## 2026-07-20 — Propagate age/gender profile re-check to all KKB seeker gates
- **Feedback/bug:** The "skip age/gender if the fetched profile already has them" rule was unreliable across all seeker bots (same weak instruction proven failing live on Maya Inbound) — the bot re-asked age/gender for a returning caller whose profile carried them.
- **Change:** Added an explicit profile RE-CHECK at the age/gender HARD BLOCK (the apply gate) in KKB out H+K and in H+K — before asking, re-read `metadata.whatIHave.age` / `metadata.gender`; a returning caller normally has both, so ask only genuinely-missing fields. (Analyser class D9.)
- **Files:** KKB Placeholder Hindi.md, KKB Placeholder Kannada.md, KKB Placeholder Inbound.md, KKB Placeholder Inbound Kannada.md

## 2026-07-19 — Profile Wording Rules: never speak "profile" aloud (say "जानकारी" / "ಮಾಹಿತಿ")
- **Feedback/bug:** The internal technical word "profile"/"प्रोफाइल"/"ಪ್ರೊಫೈಲ್" was leaking into caller-facing lines — the permission-ask ("…क्या मैं आपकी प्रोफाइल fetch कर सकती हूँ?"), the acknowledgement ("प्रोफ़ाइल मिल गई"), and several example dialogues. Callers don't understand it and it erodes trust.
- **Change:** Added a "Profile Wording Rules (CRITICAL — never speak 'profile' aloud)" section to all four KKB get_profile prompts, and reconciled every spoken/example line to warm non-technical wording — permission ask "मैं आपके लिए सही जॉब्स ढूंढने में मदद करना चाहती हूँ। क्या आपकी कुछ बेसिक जानकारी देख सकती हूँ?", acknowledgement "आपकी जानकारी मिल गई", post-apply bridge "…आपकी जानकारी पूरी रखने के लिए…". Kannada adapted (ಮಾಹಿತಿ, ನಿಮ್ಮ ಮಾಹಿತಿ ಸಿಕ್ತು). On empty fetch, never announce the miss; tool-call silence reinforced. Internal tool names + forbidden-list rules unchanged.
- **Files:** KKB Placeholder Hindi.md, KKB Placeholder Kannada.md, KKB Placeholder Inbound.md, KKB Placeholder Inbound Kannada.md

## 2026-07-18 — 17-Jul live-test batch: inbound fork gate, pool-overview on not-found, new-caller name+experience
- **Feedback/bug:** Consolidated Feedback Tracker 17-Jul calls, transcript-verified. (a) **Forking (rows 71/78):** the inbound `get_profile` fork was soft prose ("As your first action…"), so the bot skipped it when the caller volunteered a role/city, deferred it behind discovery, or replaced it with a hallucinated "क्या मैं आपकी प्रोफाइल fetch कर सकती हूँ?" permission-ask (calls 3fcf46bc, 7c3ebe21). Branch-on-result was already correct. (b) **Summary (row 80):** on the profile-not-found path the bot asked a bare "किस तरह का काम" with no pool overview (call 244a1b4f). (c) **Name+experience (row 72):** new callers weren't reliably asked name + experience before `create_profile`.
- **Change:** (a) Hard-gated the inbound `get_profile` as a DECISIVE ROUTER — no discovery/jobs/permission-ask before it returns; never skip when the caller volunteers a role/city. (b) Profile-not-found/decline path now routes to Step 1 Case B pool overview (names the `${recommendations}` kinds upfront). (c) Added a NEW-CALLER HARD BLOCK requiring name + experience before the apply sequence on the new-caller path.
- **Files:** KKB Placeholder Inbound.md, KKB Placeholder Inbound Kannada.md, KKB Placeholder Hindi.md, KKB Placeholder Kannada.md

## 2026-07-18 — Slash "/" spoken aloud in job/category labels (bug 65/73, cross-agent)
- **Feedback/bug:** Live 17-Jul calls (Consolidated Feedback Tracker rows 65 KKB-HE-Inbound / 73 KKB-placeholder-Inbound). TTS voiced the "/" symbol as "slash" while reading role/category labels ("सेल्स/मार्केटिंग", "कस्टमर सपोर्ट/बीपीओ", "कॉल सेंटर/वॉइस"). Inbound had no slash rule at all; outbound only a generic one-liner that didn't cover role/category labels.
- **Change:** Added/strengthened the "## Slash ( / ) symbol" TTS rule to explicitly ban voicing "/" and to cover role/category labels with concrete examples ("सेल्स/मार्केटिंग" → "सेल्स या मार्केटिंग"), keeping the per-form for rates. Kannada uses "ಅಥವಾ".
- **Files:** KKB Placeholder Hindi.md, KKB Placeholder Kannada.md, KKB Placeholder Inbound.md, KKB Placeholder Inbound Kannada.md

## 2026-07-16 — Fix new_seeker="yes" fork over-fire + role="Any" placeholder spoken as a real role
- **Feedback/bug:** Live KKB placeholder Hindi call. (1) **Fork over-fired the wrong way:** `new_seeker="yes"` (new caller) but the bot still asked "क्या मैं आपकी प्रोफाइल fetch कर सकती हूँ?" and called `get_profile` — the forceful "MANDATORY" wording on the `new_seeker="no"` branch bled onto the "yes" path (A1/E1). (2+3) **role="Any" spoken as a real role:** the fetched profile had `role="Any"` (a placeholder) and the bot said "मैं देख रही हूँ कि आप अभी **Any** का काम देख रही हैं — इसी तरह की जॉब्स?" — a Case-A role-confirm on a non-role, which also meant the pool-overview job summary was never given upfront.
- **Change (Hindi source, mirrored to Kannada; router/logic agnostic-verbatim, spoken quotes adapted):**
  - **Fork (outbound H+K):** added a **DECISIVE ROUTER** at the top of Profile Handling — check `new_seeker` FIRST; **"yes" → profile-permission question + `get_profile` FORBIDDEN** (a "yes" caller may have stale backend profiles — that is WHY not to fetch); "no" → the mandatory fetch. Stated the "no" MANDATORY wording applies ONLY to "no". (Inbound is get_profile-driven — no new_seeker, no router needed.)
  - **role="Any" (all four — outbound H+K + inbound H+K):** in "Reading the get_profile response" (role field) and "Using the fetched profile" (role-confirm + no-role bullet): a role of "Any" (case-insensitive), "Not Available", empty, null, or garbled is **NOT a usable role** — never spoken, never role-confirmed; treated as **UNKNOWN** → skip the role-confirm and go to **Step 1 Case B (pool overview)**, which surfaces the job-type summary upfront (fixes issues 2 and 3 together).
- **Files:** `KKB Placeholder Hindi.md`, `KKB Placeholder Kannada.md` (fork + role); `KKB Placeholder Inbound.md`, `KKB Placeholder Inbound Kannada.md` (role only). Analyser (A1/E1 fork-bleed + new placeholder-role class) updated centrally.

## 2026-07-16 — Parent consolidation: harden inbound create_profile-first gate
- **Feedback/bug:** The KKB **inbound** Step 4 NO-branch (new caller → `create_profile` then `apply_job`) carried weaker wording than the outbound gate fixed in the entry below — the same "skip `create_profile` → `apply_job` fails with no `profile_id`" class (C7 inverse) was latent inbound (flagged by the fix agent).
- **Change:** `KKB Placeholder Inbound.md` + `KKB Placeholder Inbound Kannada.md` — appended the forceful clause to the inbound apply NO-branch: **`create_profile` is the required FIRST step — not optional; `apply_job` without a `profile_id` will FAIL; never skip it or call `apply_job` first.** (Now consistent with the outbound gate and the Maya paths.)
- **Files:** `KKB/KKB Placeholder Inbound.md`, `KKB/KKB Placeholder Inbound Kannada.md`. Analyser C7 updated centrally.

## 2026-07-16 — new_seeker="yes" create_profile-first gate (outbound) + inbound +91 / country_code hardening
- **Feedback/bug:** Three live-call bugs. (1) **Outbound, `new_seeker="yes"` (new caller, no profile ever fetched):** at apply the agent said the bridge and called `apply_job` **directly, skipping `create_profile`** — no `profile_id` existed, so the apply FAILED (C5/C7). The Step 4 checkpoint's "NO → create_profile first" branch was not firing reliably for a new caller who had been told never to think about profiles. (2) **Inbound:** `get_profile` reportedly not always called with `+91` (C3). (3) **Inbound:** `${country_code}` was declared as if passed, but inbound calls carry **no input variables**, so it is unset.
- **Change (BUG 4 — outbound, `KKB Placeholder Hindi.md` + `KKB Placeholder Kannada.md`, agnostic English mirrored verbatim):**
  - **Step 4 (C5/C7):** rewrote the NO branch to be as salient as the YES branch — "**NO → NO profile was ever fetched → there is NO `profile_id` yet → you MUST call `create_profile` FIRST, then `apply_job`.**" States this is the path for EVERY `new_seeker="yes"` caller (and the get_profile-returned-nothing case), that `create_profile` is the required first step (not optional), that **calling `apply_job` without a `profile_id` will FAIL**, and that the "never think about profiles" instruction was conversation-only — at apply time the profile MUST be created first. Added a follow-on paragraph tying `apply_job`'s `profile_id` source to each path. **YES branch left intact** (get_profile ran → `apply_job` only, no duplicate `create_profile` — C7 not weakened).
  - **apply_job rules:** added "`apply_job` can NEVER run without a `profile_id` — it will FAIL otherwise"; on the new-caller path `create_profile` must run first. Payload-construction `profile_id` bullet now spells out both sources and forbids an empty `profile_id`.
  - **create_profile rules:** "Use create_profile when" now names EVERY `new_seeker="yes"` caller; added a **MANDATORY FIRST STEP** note that `create_profile` is the required first tool on the new-caller path and `apply_job` before it will fail. Age/gender (Step 3.5) gate preserved.
- **Change (BUG 1 + BUG 3 — inbound, `KKB Placeholder Inbound.md` + `KKB Placeholder Inbound Kannada.md`, agnostic English mirrored verbatim):**
  - **BUG 1 (country_code):** rewrote the `${country_code}` Input-Variable declaration to state it is **NOT a passed input on an inbound call** (no input variables inbound); always assume `+91`. Neutralized the create_profile "The user's country code: country_code" line ("No separate country code is sent … never add a `country_code` field from an unset variable") and removed `${country_code}` from the Hallucination-Guard call-metadata list. (Outbound `${country_code}` declarations left as-is — system-initiated, phone already literal `+91`.)
  - **BUG 3 (+91):** audited every `get_profile`/`create_profile` phone reference — all already `+91`-prefixed with the double-prefix guard intact. Hardened the first-action instruction to state the phone **MUST** be `+91`-prefixed and a **bare 10-digit number returns an empty result**; added "always with the `+91` prefix" to the `${contact_phone}` declaration.
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md` (BUG 4); `KKB/KKB Placeholder Inbound.md`, `KKB/KKB Placeholder Inbound Kannada.md` (BUG 1 + BUG 3).
- **Decision/flag:** BUG 4 scoped to outbound per instruction; the inbound Step 4 NO-branch still has the older (weaker) wording — same create_profile-first failure class is latent there and should be strengthened in a follow-up if it recurs inbound. Snapshot `versions/KKB/2026-07-16_162711__pre-bugfix-batch2` taken before edits. Self-checked all four files: H/K parity confirmed (new agnostic text byte-identical per twin), memory-injection block present in all four, C3 phone format clean, C5 success-line gating and C7 YES-branch guards unchanged, no digits introduced into spoken lines. Analyser update handled centrally by the parent.
- **Feedback/bug:** The inbound agent (`KKB Placeholder Inbound.md`, Hindi) was a version behind the just-finalized outbound KKB placeholder flow, and had no Kannada twin.
- **Change (Hindi inbound — carried the outbound "latest flow" into the get_profile-driven, hardcoded-inventory structure; did NOT reintroduce `${new_seeker}`/`${recommendations}`):**
  - **Ranking (C8):** Default Presentation Rule + Step 2 now treat the hardcoded Job Inventory as a POOL ranked by role → location → salary, presenting the 3 best-fit role-matched-first (not inventory order); the fallback draws the next best-fit batch of up to 3 from the rest of the inventory. Hallucination Guard reaffirmed (re-order only, never invent).
  - **Orient / pool-overview (C8):** Step 1 restructured into Case A (target role known → area question → ranked list) / Case B (role unknown → short pool overview naming only real inventory role types, no counts → "which interests you?" → rank), with the fork-safety guard (never the opener; changes nothing about the greeting or the silent fetch).
  - **Apply-time decision checkpoint (C7):** Step 4 now leads with the binary "Did `get_profile` return a profile in this call? YES → `apply_job` ONLY, `profile_id` = the fetch's top-level `id`, NO `create_profile`; NO → `create_profile` then `apply_job`." Added the create_profile **HARD GUARD** and bound apply_job `profile_id` to the fetch result.
  - **Bridge-once (B1):** apply_job rules now say the bridge line once, silent between/around tools, no extra apply-narration.
  - **Step 3.5 age/gender (HARD BLOCK):** new pre-apply step; skips any field already present on the fetched profile.
  - **Reading the get_profile response (C6):** new field-map (top-level `id` = profile_id; metadata.name/role/gender/age/etc.; present ⇒ known ⇒ never re-ask). The "known caller" branch now greets by first name and confirms role as its own turn (A7).
  - **+91 phone prefix (C3):** all `get_profile`/`create_profile` phone references now `+91`-prefixed, with the "Phone format (critical)" note.
  - **Examples (E1):** added the canonical-flow note; refreshed Example 1 (new caller) to ask name + age + gender before the single bridge; clarified Examples 2 & 5 skip age/gender validly (already on profile); `+91` in the get_profile/create_profile annotations.
- **Change (Kannada inbound — NEW FILE `KKB Placeholder Inbound Kannada.md`, structural parity with the refreshed Hindi):** mirrored the Hindi inbound section-for-section (112 headings identical, bar the expected "Devanagari" vs "Kannada transliteration" line). AGNOSTIC content (logic, rules, tool payloads, section skeleton, the memory-injection block) copied verbatim; SPECIFIC content (spoken lines, number-words, markers) translated to Kannada — reusing the existing Kannada translations from `KKB Placeholder Kannada.md` for all shared sections (Language/TTS/Speech-Recognition/Style/Prohibited/tool rules/success-failure/post-app/emotional/special-journey/graceful-exit/dignity) and translating the inbound-specific spoken lines.
- **Files:** `KKB/KKB Placeholder Inbound.md` (refreshed), `KKB/KKB Placeholder Inbound Kannada.md` (new).
- **Ported from:** KKB outbound placeholder (2026-07-15 latest flow). Self-checked both files against `bug-patterns.md` / `section-checklists.md` (C7, C6, C8, B1, A7, C3, memory block, TTS number-words, Devanagari/Kannada script separation) — no new bug class, so no analyser change (carrying already-working behaviour into a sibling variant + a new language twin).
- **Decision/flag:** the Kannada inbound's hardcoded inventory keeps the **real UP job data** (same `job_id`s, companies, salaries, Ghaziabad/Noida locations) rather than swapping to Bengaluru-region jobs — `job_id` is an `apply_job` payload key bound to those specific backend jobs, so localizing company/location would decouple the spoken details from the job actually applied to (a C3-class data risk). Only the `qualification` display strings were translated to Kannada, and salary/vacancy are spoken in Kannada number-words per the TTS rules. Sample-conversation place names therefore stay Ghaziabad/Noida (in Kannada script), not Bengaluru, since they must reference real inventory jobs.

## 2026-07-15 — Refresh sample conversations to the ported flow (E1)
- **Feedback/bug:** After the Maya port, the 6 sample conversations still modelled the older lead-in and (critically) applied WITHOUT the Step 3.5 age/gender step — an E1 risk (examples override prose; the model could learn to skip a HARD BLOCK).
- **Change (both languages):** rewrote **Example 1** to model the full new shape — profile-found greet + role-confirm as its own turn → separate orient/area turn → **ranked** list (role-matched first) → deep-dive → **age/gender asked (not on profile)** → ONE bridge → `apply_job` (no `create_profile`); added the apply-checkpoint note. Added a **canonical-flow note** to the Sample Conversational Patterns header clarifying the shape and that returning/profile-found examples correctly *skip* the age/gender ask because those fields are already known (a valid Step 3.5 skip, not an omission).
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md`.

## 2026-07-15 — Fix bare phone → +91 prefix in get_profile/create_profile (C3)
- **Feedback/bug:** Spotted during the Maya port — KKB passed the bare 10-digit `${contact_phone}` to `get_profile` (`phoneNumber: ${contact_phone}`) and built `create_profile` payloads with a bare `phone`. Same class as the Maya C3 bug: profiles are stored with a `+91` country-code prefix, so a bare number returns empty fetches and creates mismatched profiles.
- **Change (AGNOSTIC — both language files, verbatim):** `phoneNumber: +91${contact_phone}` in all `get_profile` references (Profile Handling, get_profile rules, Example 1); create_profile minimum payload `"phone": "+91<contact_phone>"`; additional-example phone `+91…`; Contact-Context-Variables note + a "**Phone format (critical)**" rule (no double-prefix if a country code is already present).
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md` (parity verified: 7 `+91` each, no bare phones). Analyser **C3** "Seen in" extended to KKB.

## 2026-07-15 — Port full Maya presentation + apply set to KKB placeholder (both languages)
- **Feedback/bug:** Parth: carry the Maya changes forward to KKB placeholder — the "we have a/b/c kinds of jobs, which interests you, then show the rest" overview, plus (chosen: full set) the ranking, apply-time checkpoint, bridge-once, and turn barriers.
- **Change (KKB Hindi source-of-truth, mirrored verbatim to Kannada; spoken lines adapted per language):**
  - **Default Presentation Rule → ranking:** treat `${recommendations}` as a pool; rank by **role → location → salary** and present the **3 best-fit**, role-matched first, instead of blind array order. Replaces "always first 3 / jobs 4–10 / lower-index". Applies to both new_seeker paths.
  - **Profile Handling "no" → "Using the fetched profile":** greet by first name, confirm role (turn ENDS on that question — WAIT), rank role-matched first, never re-ask known fields. New "## Reading the get_profile response" field-map (binds top-level `id` as `profile_id`).
  - **Step 1 → "Lead-in and orient" (Case A / Case B):** Case A (role known) → area question → ranked Step 2; Case B (role unknown) → short **pool overview** naming real role types → "which interests you?" → rank. Removes the old ask-before-show ("इस तरह का काम देख रहे हैं?" before listing). Includes the fork-safety guard (overview is never the opener, never replaces the profile-permission question).
  - **Step 2:** present the ranked best-fit 3 (role-matched first), fallback draws next best-fit from the rest of the pool (same ranking, batched up to 3).
  - **Step 4 → decision-first apply checkpoint:** "Did `get_profile` run in this call? → YES: `apply_job` ONLY (profile_id from the fetch result), no `create_profile`; NO: `create_profile` then `apply_job`." + create_profile **HARD GUARD** (no duplicate when a profile was fetched) + apply_job payload `profile_id` bound to the fetch result + **bridge-once** (silent between/around tools, no extra apply-narration).
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md` (parity verified: 0 stale refs, identical marker counts).
- **Ported from:** Maya (2026-07-13/15 ranking + overview + apply-checkpoint + bridge-once work). Not a new bug class — no analyser change (port of already-working behaviour).
- **Not done / flagged:** (1) the 6 sample conversations still model the older Case-A lead-in (they don't depict the Case B overview or the Step 3.5 age/gender step — largely consistent, optional refresh). (2) KKB `get_profile`/`create_profile` still pass the **bare** `${contact_phone}` (no `+91`) — this is the same C3 format bug Maya fixed (~14/80 empty fetches); left untouched as out-of-scope for this port, worth a separate fix.

## 2026-07-15 — No-Match line: drop the "galti ho gayi" self-blame
- **Feedback/bug:** The No-Match Fallback opened by admitting fault ("लगता है हमसे एक गलती हो गई —" / "ನಮ್ಮಿಂದ ಒಂದು ತಪ್ಪಾದಂತೆ ಕಾಣ್ತಿದೆ —"). Parth: remove the "galti ho gayi" wording — the bot shouldn't confess a mistake to the caller.
- **Change:** Removed the self-blame clause from both No-Match Fallback occurrences in each language; the line now opens directly with the status. Hindi: "आपके लिए relevant jobs अभी नहीं दिख रहीं। हम जल्द ही सही options ढूंढकर आपको बताएंगे।" Kannada: "ನಿಮಗೆ relevant ಜಾಬ್‌ಗಳು ಈಗ ಕಾಣ್ತಿಲ್ಲ. ನಾವು ಶೀಘ್ರದಲ್ಲೇ ಸರಿಯಾದ ಆಪ್ಷನ್‌ಗಳನ್ನು ಹುಡುಕಿ ತಿಳಿಸುತ್ತೇವೆ." (SPECIFIC spoken line — adapted per language, not verbatim.) KKB Inbound has no apology phrasing, so it was untouched.
- **Files:** `KKB/KKB Placeholder Hindi.md` (2 occurrences), `KKB/KKB Placeholder Kannada.md` (2 occurrences).

## 2026-07-13 — Reconcile repo to the live working copy: add Step 3.5 (Pre-Apply age/gender)
- **Feedback/bug:** While fixing the fork, a full compare of the repo files against the prompt Parth was actually running revealed the repo was a version behind: the running copy had a **`## Step 3.5 — Pre-Apply Data Collection (age and gender — mandatory before apply)`** block (age + gender questions, skip-if-in-profile, and a HARD BLOCK gating `apply_job` on age+gender being known) that neither repo language file had. Everything else matched (headings, Step 4 body, Example 1 all identical; grep confirmed zero age/gender content in the repo). Left unreconciled, the repo fork fix and the running copy's Step 3.5 would live in different files.
- **Change:** Added Step 3.5 to **KKB Hindi** verbatim from the running copy, and mirrored to **KKB Kannada** — rules/logic/HARD BLOCK copied verbatim (AGNOSTIC); the spoken lines adapted to Kannada idiom (age Q "ನಿಮ್ಮ ವಯಸ್ಸು ಎಷ್ಟು — ಸುಮಾರಾಗಿ ಹೇಳಿ?", confirm "ನೀವು [X] ವರ್ಷ ಅಂದ್ರಿ, ಸರಿನಾ?", gender "ನೀವು male ಆ, female ಆ?", decline "ಪರ್ವಾಗಿಲ್ಲ", seeker "ಹೌದು ಅಪ್ಲೈ ಮಾಡಿ"). Repo Hindi now == the running copy + the fork fix; both languages in sync (Step 1→2→3→3.5→4).
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md`.
- **Process note:** the fork fix earlier this session was applied after spot-checking only the fork lines against the pasted prompt, not a full compare — which is how the Step 3.5 gap went unnoticed at first. Lesson: when a user pastes a prompt, diff the whole thing against the repo copy before editing, so repo drift surfaces up front.

## 2026-07-13 — Fix the new_seeker fork: variable-interpolation order (G1) + branch contradiction (A4)
- **Feedback/bug:** The new_seeker fork wasn't working in KKB — the same failure fixed in Maya. Two mistakes: **(1) G1 (root cause):** the binding phrase read `Consider ${new_seeker} as new_seeker`, which interpolates at runtime to "Consider **no** as new_seeker" — the value lands where the label should be, so `new_seeker` never binds and the branch has nothing to switch on (falls through to a default path). Present in **two** places (Contact Variables line + Profile Handling step). **(2) A4:** the `new_seeker="no"` branch header says "caller already has a profile" but its body said "MANDATORY STEP IF USER PROFILE DOES NOT EXIST" — a header/body contradiction that muddies the returning-caller path. (Both were pre-flagged in the analyser from the Maya work: G1 was catalogued as "latent in KKB, not yet flipped"; A4 from Maya 2026-07-05.)
- **Change (both language files, AGNOSTIC → verbatim):**
  - Flipped both bindings to **`Consider new_seeker as ${new_seeker}`** (→ "Consider new_seeker as no", binds cleanly).
  - Rewrote the `"no"` branch's mandatory-step line to drop the "IF USER PROFILE DOES NOT EXIST" contradiction and state the path plainly: new_seeker "no" = caller already HAS a profile → the profile-permission question is the very next turn after the greeting, and `get_profile` must run before any job talk.
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md` (identical fix, parity preserved); `.claude/skills/prompt-analyser/reference/bug-patterns.md` (G1 "Seen in" updated — KKB no longer latent, now flipped).
- **Not affected:** `KKB Placeholder Inbound.md` — that variant removed `${new_seeker}` entirely (fork decided by the `get_profile` result), so it has no binding bug.
- **Re-test:** a `new_seeker="no"` call must ask "क्या मैं आपकी प्रोफाइल fetch कर सकती हूँ?" and call `get_profile`; a `"yes"` call must NOT mention/fetch a profile.

## 2026-07-13 — New agent: KKB Placeholder Inbound (Hindi)
- **Feedback/bug:** Need an inbound clone of the outbound KKB Hindi agent — same persona and safety, but the seeker calls *in* rather than being called.
- **Change:** Created a new standalone inbound conversation prompt by cloning `KKB Placeholder Hindi.md` and re-domaining three things: (1) **Introduction** — dropped the outbound "मैं गवर्नमेंट की तरफ से कॉल कर रही हूँ / आपके लिए कुछ जॉब्स हैं" opener; new callers now get a welcome + discovery question ("बताइए, आप किस तरह का काम ढूंढ रहे हैं?"). Returning-caller resume (contact memory) retained. (2) **Input variables removed** — no `${contact_name}`, `${new_seeker}`, or `${recommendations}`. The new-vs-returning fork is now decided by the `get_profile` result (called silently at call start with the caller-ID `${contact_phone}`, no permission ask): profile found → known caller; nothing → new-caller path (gather → `create_profile` before apply). `${contact_phone}`/`${country_code}` (caller ID) and `${contact_memory}` retained as the only inputs. (3) **Hardcoded Job Inventory** — replaced `${recommendations}` with a 17-job internal inventory injected in-prompt, plus a new **Inbound Discovery** step (ask role/location/salary), full-inventory scan with synonym + salary-floor + nearby-location matching, top-3 presentation, and an **Inbound No-Match Fallback**. Deep-dive `benefits` and post-apply `hr_contact` sharing wired to the inventory fields. All 6 sample conversations rewritten to inbound flow using real inventory jobs. All language/TTS/speech-recognition/dignity/tool sections preserved verbatim.
- **Files:** `KKB/KKB Placeholder Inbound.md` (new)
- **Feedback/bug:** The two language files had drifted: Kannada had a `## Pre-check (Before anything else)` step under Job Presentation Flow that Hindi lacked; Hindi had a second `# No-Match Fallback` section (after Step 4) that Kannada lacked. Decision: add both to both (additive, no deletions).
- **Change:** Added the `## Pre-check` block to KKB Hindi (verbatim agnostic logic). Added the second `# No-Match Fallback` to KKB Kannada (agnostic trigger/close logic copied; used the existing Kannada fallback message). Both files now contain both sections.
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md`

## 2026-06-29 — Add company name to job presentation
- **Feedback/bug:** When presenting job options, the agent did not name the company. This behavior existed in Maya but in neither KKB language.
- **Change:** Ported the company-name feature from Maya. Step 2 spoken format now reads `[role], [company], [location], सैलरी/ಸ್ಯಾಲರಿ [salary]` for 1/2/3-job cases; Step 3 deep-dive now names the company; added a Step 2 rule to speak `[company]` where present and skip silently if missing/"Not Available". Applied to Hindi (source) and mirrored to Kannada. Maya's neighboring `benefits`/`hr_contact` lines were intentionally NOT ported — KKB's `${recommendations}` has no such fields. `${recommendations}` already includes `company`, so no schema change was needed.
- **Files:** `KKB/KKB Placeholder Hindi.md`, `KKB/KKB Placeholder Kannada.md`
- **Ported from:** Maya

## 2026-06-29 — Initial system setup
- **Feedback/bug:** Maintenance system bootstrap; KKB had no memory prompt.
- **Change:** Created `KKB Memory.md` (language-agnostic seeker memory, English output), modeled on `DKB Memory.md` and re-domained to the seeker/job-search context. Backs the conversation prompt's "Introduction Priority Rule" via `last_action` / `last_options_presented` / `jobs_applied`.
- **Files:** `KKB/KKB Memory.md`

## 2026-09-03 — Job-count anchor: the all-told line gets a numeric guard the model can check
- **Feedback/bug:** On `22d80263` the bot presented 7 of 8 supplied jobs to a caller who repeatedly
  asked for the full list, then said "जो जॉब्स अभी हमारे पास हैं, वो सब मैंने बता दीं" with
  इलेक्ट्रिकल इंजीनियर never spoken. `cb9a4938` — same prompt, same fixture — presented 8 of 8.
  A mixed ratio, so per CLAUDE.md rung 0 this is an adherence gap, not unreachability.
- **Root cause:** the existing guard told the model to count what it had said aloud against
  `${recommendations}`. That count is not verifiable at the moment the closing line is chosen. The
  prompt already carried FOUR wordings of that same guard, so a fifth was forbidden (never add a
  third wording of a guard that has failed twice) — the mechanism had to change.
- **Change:** (1) new `### Job count anchor` in Step 2 — the first batch of every call now announces
  the total, "आपके इलाके में कुल [N] जॉब्स हैं — [तीन] अभी बताती हूँ।", said once per call;
  (2) ordinals now run continuously across batches and never restart; (3) both all-told closing lines
  gained a NUMERIC CHECK permitting them only when the highest ordinal spoken equals the announced
  total. The model compares two numbers already in its own output instead of re-counting an array.
- **Files:** `KKB/KKB Placeholder Hindi Signals.md`, `KKB/KKB Placeholder Kannada Signals.md`
  (mirrored: agnostic rule verbatim, spoken lines adapted — Kannada number-words, ಒಂದು…ಎಂಟು).
- **Analyser:** added pattern **D56** (completeness claim gated on an unverifiable count).
- **Status:** deployed to `kkb-hi-signals` (227049 bytes) and `kkb-kn-signals`. **VERIFY-PENDING** —
  live calls running; not to be called fixed without a call id showing 8 of 8 plus the anchor line.

## 2026-09-03 — Array-order walk after batch one; count anchor propagated to all job-presenting bots
- **Feedback/bug:** with the count anchor live, `54a0daa8` reached आठवाँ by naming सोलर एनर्जी
  कंसल्टेंट twice (तीसरा AND सातवाँ) and never spoke इलेक्ट्रिकल इंजीनियर; `22d80263` dropped the same
  entry outright. Two of four calls, always the entry the model had ranked LAST.
- **Root cause:** the prompt had the model re-rank `${recommendations}` on every batch, so "which job
  comes next" was a fresh judgement call each time; the tail of the ranking is where it failed.
- **Change:** best-fit ranking now applies to the FIRST batch only; later batches walk the list in
  array order, skipping entries already named. Added an explicit no-job-twice rule — reaching the
  announced total by repeating a job is a failure, not a completion.
- **Files:** all 12 job-presenting conversation prompts — `KKB Placeholder Hindi/Kannada Signals`,
  `KKB Placeholder Inbound Signals`, `KKB Placeholder Inbound Kannada Signals`, `KKB Placeholder
  Hindi/Kannada`, `KKB Placeholder Inbound`, `KKB Placeholder Inbound Kannada`, plus Maya's four
  (see `Maya/CHANGELOG.md`). Inbound variants reference the list `get_jobs`/the fetch returned rather
  than `${recommendations}`, which they do not receive.
- **Analyser:** D56.
- **Status:** VERIFIED on the two outbound Signals bots — Hindi `4da7af15`, `85e51aac` (8 of 8, all
  distinct, इलेक्ट्रिकल इंजीनियर named); Kannada `be837379`, `33187441` (8 of 8, ಒಟ್ಟು ಎಂಟು announced,
  array order). The other 8 prompts are **DEPLOYED, NOT VERIFIED** — live read-back confirms the text
  shipped to all 12, which proves nothing about behaviour.

## 2026-09-03 — The lookup leak was mandated by the prompt, not a model-adherence miss
- **Feedback/bug:** open item `fetch-leak-kn-signals` (since 2026-08-04) — the bot hints out loud
  that it looked the caller up. The item recorded the cause as model adherence and advised against
  prose changes.
- **Root cause:** that was wrong. Grepping the leaked phrases against the prompts (D50) found them
  **required**: the role-confirmation step instructed the bot to say "मैं देख रही हूँ कि आप अभी [role]
  का काम कर रहे हैं" (Hindi) / "ನಾನು ನೋಡ್ತಿದ್ದೀನಿ, ನೀವು ಈಗ [role] ಕೆಲಸ ಮಾಡ್ತಾ ಇದೀರಿ" (Kannada), the
  inbound twins "आपकी जानकारी में [role] दिख रहा है" / "ನಿಮ್ಮ ಮಾಹಿತಿಯಲ್ಲಿ [role] ಕಾಣ್ತಿದೆ", and sample
  conversations demonstrated all four — while a different section of the same file banned the phrase
  by name. 19 mandated occurrences across 12 prompts. Not Kannada-only: Hindi, Maya and both legacy
  pairs carried it.
- **Change:** every mandated line and sample now reflects the role back WITHOUT narrating a lookup —
  "आप अभी [role] का काम कर रहे हैं — क्या आप अभी भी [role] की जॉब देख रहे हैं?" and
  "ನೀವು ಈಗ [role] ಕೆಲಸ ಮಾಡ್ತಾ ಇದೀರಿ ಅಲ್ವಾ — ನಿಮಗೆ ಇನ್ನೂ [role] ಥರದ ಜಾಬ್ ಬೇಕಾ?". The ban stays; the
  lines that contradicted it are gone. Reflecting a known fact was always the intent — narrating the
  fetch never was.
- **Files:** all 8 KKB conversation prompts + Maya's 4 (see `Maya/CHANGELOG.md`).
- **Analyser:** D50 addendum — an adherence diagnosis is invalid until the bot's exact words have been
  grepped against every prompt file for that bot and found absent.
- **Status:** VERIFY-PENDING — deploying after the standing sanity sweep finishes.

## 2026-09-03 — Introduction is spoken once per call (ported from TRRAIN)
- **Feedback/bug:** open item `intro-spoken-twice-once-in-nine-calls` — on 1 of 9 live calls the bot
  greeted, fetched the profile, then said the whole introduction again.
- **Root cause:** the heading said "said only once" but no rule decided the ambiguous case, so an
  unclear reply left re-greeting available. A 1-in-9 rate is a gap, not flakiness.
- **Change:** ported TRRAIN's proven rule — the introduction is spoken once and never repeated, not
  even after a tool call, and **an unclear reply is treated as an acknowledgement so the call moves
  on**. That decision is the part that was missing.
- **Files:** all 12 job-presenting conversation prompts (8 KKB + 4 Maya).
- **Ported from:** TRRAIN Hindi ("Turn 2 is said ONCE per call and is NEVER repeated").
- **Status:** VERIFY-PENDING.

## 2026-09-03 — The already-applied branch cannot be satisfied honestly; gate it on evidence
- **Feedback/bug:** the three-outcome apply spec asked the bot to distinguish already-applied from a
  technical failure. Both halves are now failing in opposite directions: `d6e545d4` and `d401d6cf`
  (Kannada) called a REAL duplicate a technical issue, and `c5a10922` (Hindi) called a job the bot had
  never attempted "already applied" — with empty memory and no apply_job call for it.
- **Root cause:** the branch is keyed on a fact the agent cannot obtain. The error body is not given
  to the model (`[Error: apply_job request failed (HTTP 422).]`; the reason sits in a debug block for
  the transcript only), `contact_memory` is empty on these calls, and — newly established on
  `d6e545d4` — **`get_profile` does not return the caller's applications**; the only non-profile item
  it returned was an unrelated draft job posting the test number owns as a provider. Putting the
  ACTION_LIMIT mapping in the tool description (which was itself missing on 5 of 6 bots until today)
  cannot help, because the string it tests for never reaches the model.
- **Change:** row 1 now requires evidence the model can point at — either an `apply_job` result for
  that same `job_id` earlier in the SAME call, or a `jobs_applied` entry naming role and company.
  Absent both it must use row 2. This does not make the distinction work; it stops the bot inventing
  it, which is the half we control.
- **Files:** all 12 conversation prompts. Tool descriptions also brought to parity — the
  ACTION_LIMIT mapping existed only on `kkb-hi-signals` and is now on all six job-applying Signals
  bots (see the tool-schema note below).
- **Analyser:** D58 (a rule that cannot be satisfied honestly gets satisfied dishonestly).
- **Platform ask (nothing else unblocks this):** surface the tool error's `error`/`message` fields to
  the model, OR return distinct HTTP statuses per cause, OR add an applications list to
  `get_profile`. Any one makes the three-outcome spec achievable. Call ids: `d6e545d4`, `d401d6cf`,
  `c5a10922`, plus the ten from 2026-09-02.
- **Status:** evidence gate DEPLOYED to all 12, **VERIFY-PENDING**. The distinction itself is
  **BLOCKED** on the platform and must not be reported as fixed.

## 2026-09-03 — Tool schemas were never mirrored, only prompts
- **Feedback/bug:** two separate bugs today traced to the same thing — a fix that lived in the tool
  schema was applied to `kkb-hi-signals` and nowhere else, while the prompt text was mirrored to all
  twelve.
- **What was missing:** (1) the required `duplicate_check` parameter — present on 1 of 12 bots, so on
  the other 11 the prompt keyed its logic on a parameter the model was never given; (2) the
  `ACTION_LIMIT_REACHED` → already-applied mapping in the `apply_job` description — present on 1 of 6
  Signals bots.
- **Change:** `duplicate_check` added to all 12 (identical enum and description); the working
  `apply_job` description copied verbatim to the other five Signals bots (980 chars — note Raya caps
  tool descriptions at 1024 and answers a longer one with `PATCH 400`).
- **Standing gap to close:** `/sync-check` audits prompt text only. A bot's tool schemas — parameters,
  `required`, enums, descriptions — need the same per-language matrix, or this recurs.

## 2026-09-03 — profile_id was read positionally, so providers could never apply
- **Feedback/bug:** Santosh, KKB Kannada Signals: two applications failed. Both were
  `SOURCE_ITEM_NOT_FOUND` (`0d63dc50`) — NOT already-applied and NOT a stale job id; both job ids
  (`19e3da1f`, `bc2ac8de`) are live on Dharwad.
- **Root cause:** his `get_profile` returned exactly one item, of type `job_posting_1.0` — he is
  registered as a provider and has no seeker profile. The `apply_job` tool description said the
  profile id is "items[0].item_id from get_profile", and the prompts say `items[0]` 10–11 times, so
  the bot sent a JOB POSTING's id as `profile_id`. The source item of an apply is the profile, so the
  API was right. He had no profile and one was never created.
- **Why no test caught it:** the tester number's `get_profile` returns its `profile_1.0` first, so
  `items[0]` is correct there and every harness call passed. The rule was right by luck on the one
  account we test with.
- **Change:** `profile_id` must be the item whose `item_type` is `profile_1.0` AND `item_domain` is
  `seeker` — never `items[0]`. If no such item exists the caller is NEW: consent, then
  `create_profile`, then use the returned id. Applied to the `apply_job` and `update_profile`
  parameter descriptions on all six Signals bots, and as a rule in the six Signals prompts.
- **Files:** `KKB Placeholder Hindi/Kannada Signals.md`, `KKB Placeholder Inbound Signals.md`,
  `KKB Placeholder Inbound Kannada Signals.md`, plus Maya's two Signals prompts.
- **Analyser:** D59 (positional access into a tool result).
- **Status:** DEPLOYED, **VERIFY-PENDING** — the tester line cannot reproduce this (its profile is
  first). Confirming needs a provider-only number; Santosh's reproduces it directly. Any recurrence
  shows up as `SOURCE_ITEM_NOT_FOUND` in `apply_result_integrity`.

## 2026-09-04 — Khushboo, KKB Inbound Signals: consent dropped and location re-asked
- **Feedback/bug:** (1) consent missing; (2) bot fetched the profile but did not ask or confirm
  location. Call `bbdb6eaf`.
- **Root cause 1 (consent):** the mandated line is a disclosure plus a question. The caller asked to
  apply, the bot paraphrased only the question — "क्या मैं आपकी तरफ़ से अप्लाई कर दूँ?" — and dropped
  "आपकी personal details company के साथ share होंगी". The model keeps the half that advances the call.
  The prompt already forbade `apply_job` without the line, and that had failed before, so the guard
  moved into the `apply_job` tool description rather than gaining a third wording.
- **Root cause 2 (location):** NOT "already confirmed earlier". Her profile carried `Delhi, India`.
  The prompt printed the OPEN area question as the Case A script and put "ASK THIS ONLY IF YOU DO NOT
  ALREADY HAVE A LOCATION" underneath it, so the wrong line was the default and the guard was a
  caveat. Restructured: check first, then confirm / stay silent / ask, with the open ask as the LAST
  branch. Same fault was live on `5a3aef43`, `0358c875`, `452874bb`, `4ed09650`, `7b81a27a` — all
  three inbound bots, not just Hindi.
- **Files:** `KKB Placeholder Inbound Signals.md`, `KKB Placeholder Inbound Kannada Signals.md`,
  `KKB Placeholder Inbound.md`, `KKB Placeholder Inbound Kannada.md`, plus Maya's two inbound prompts;
  `apply_job` description on all six Signals bots.
- **Analyser:** D60 (disclosure dropped from a bundled line), D61 (suppression rule with no
  replacement).
- **Status:** **VERIFIED** — `334fc8f3` (location confirmed, disclosure before all three applies) and
  `a82cd401` (location confirmed, full consent line). Detector clean on both.

## 2026-09-09 — apply-failure table had no row for a NAMED non-duplicate error
- **Feedback/bug:** the apply-failure table routed every non-duplicate error into Row 2, "you cannot
  tell why it failed", whose line asserts a cause: "अप्लाई अभी आगे नहीं बढ़ा है, technical issue है".
  But the tool result DOES name the error — `__RAYA_TOOL_DEBUG__` carries a
  `response_body_excerpt` with `"error":"..."`, and 67 of 73 observed apply failures name it. So on
  `MINOR_ACTION_CHANNEL_BLOCKED` (an age/channel policy block, not a fault) the bot told 5 callers
  there was a technical issue — a claim the prompt had licensed and that was false. Calls
  `5a1c0c77` (kkb-hi-signals), `1715a207` (kkb-kn-signals), `05a4b394` (kkb-kn-in-signals),
  `2cb97508` (maya-hi-signals, `TARGET_ITEM_NOT_FOUND`), `b9629043` (`USER_NOT_FOUND`).
- **Change:** inserted a new row BEFORE the catch-all — a named error that is not
  `ACTION_LIMIT_REACHED` gets a line that asserts only that the apply did not complete:
  "इस जॉब के लिए अप्लाई अभी पूरा नहीं हो पाया। हमने आपकी रुचि नोट कर ली है। क्या मैं आपको दूसरी जॉब्स बताऊँ?"
  (Kannada: "ಈ ಜಾಬ್‌ಗೆ ಅಪ್ಲೈ ಇನ್ನೂ ಪೂರ್ತಿ ಆಗಿಲ್ಲ. ನಿಮ್ಮ ಆಸಕ್ತಿ ನಾವು ನೋಟ್ ಮಾಡ್ಕೊಂಡಿದೀವಿ. ಬೇರೆ ಜಾಬ್‌ಗಳನ್ನ ಹೇಳಲಾ?")
  Escalation-ladder rung 3 — the wrong option is removed rather than forbidden: Row 2 keeps
  "technical issue" only for the genuinely unreadable case (timeout, no response), where it is true.
  Purely additive; Row 1 and Row 2 are unchanged. Row order is Row 1, Row 2a, Row 2 so the specific
  case matches before the catch-all.
- **Files:** 9 Hindi + 4 Kannada conversation prompts across KKB, Maya and KKB-Slim.
- **Status:** VERIFY-PENDING. Rolling out to kkb-hi-signals and kkb-kn-signals first (the two bots
  where the false line was observed); the rest are DEPLOYED, NOT VERIFIED until called.

## 2026-09-09 — apply-failure catch-all tightened so a NAMED error has no catch-all (VERIFY-PENDING)
- **Feedback/bug:** the dominant apply-failure defect is the opposite of D80 — **45 of 60**
  `apply_job` calls that returned `ACTION_LIMIT_REACHED` spoke the Row 2 technical-issue line
  instead of the Row 1 already-applied line (measured 2026-09-03/04, `ESCALATION-litwiz.md` §1).
  Row 1 already named `ACTION_LIMIT_REACHED` as a trigger, so reachability was never the problem:
  Row 2 stayed available as a safe hedge and the model kept taking it. §1 concluded "there is no
  wording that resolves a distinction the model cannot observe" — but the model CAN observe it. The
  `apply_job` failure result carries `__RAYA_TOOL_DEBUG__` with
  `response_body_excerpt={"error":"..."}`, and 67 of 73 observed failures name the error.
  An earlier attempt to drive Row 1 off the error name was reverted because it leaked onto
  `USER_NOT_FOUND` (call `5f0d3671`); the new Row 2a now absorbs that case, so the fix is unblocked.
- **Change:** Row 2 is no longer "you cannot tell why it failed". Its condition is now "the result
  carries NO error name at all — a timeout, no response, or a body with nothing in `"error":"..."`",
  with an explicit instruction to check the result in hand before choosing it. The three rows are
  now disjoint and exhaustive: `ACTION_LIMIT_REACHED` matches ONLY Row 1, any other name matches
  ONLY Row 2a, and no name matches ONLY Row 2 — which stays the one row permitted to attribute a
  cause, because it is the only row where a technical fault is what you actually have. Rung 3: the
  wrong option is removed rather than forbidden. Spoken lines unchanged in all three rows.
- **Files:** 9 Hindi + 4 Kannada conversation prompts across KKB, Maya and KKB-Slim.
- **Status:** VERIFY-PENDING — not yet deployed; the Row 2a verification dial is still in flight and
  one change is being verified at a time.

## 2026-09-09 — returning-caller callback clause was missing from both Kannada prompts
- **Feedback/bug:** tracker items "Missing returning call user" were fixed on KKB Hindi, KKB Hindi
  Signals and Maya Hindi Signals and **never mirrored**. `KKB Placeholder Kannada Signals.md` and
  `KKB Placeholder Kannada.md` had ZERO occurrences of the callback clause,
  `last_conversation_summary` or `overall_conversation_summary`; the Hindi master has the clause 5x
  and "previous conversation" 20x. Kannada jumped straight from the get_profile-read paragraph to
  "Greet by first name", so a returning Kannada caller was greeted as if never called before.
  Maya Hindi had the same gap against its own Signals twin.
- **Change:** ported the whole block. English rules, field names and the callback-clause bullet list
  copied VERBATIM (agnostic); the quoted clause and its placeholder adapted to Kannada
  ("[ಮೊದಲ ಹೆಸರು] ಅವರೇ, ಹಿಂದಿನ ಸಲ ನಾವು [ಯಾವ ವಿಷಯದ ಬಗ್ಗೆ ಮಾತಾಡಿದ್ವಿ] ಬಗ್ಗೆ ಮಾತಾಡಿದ್ವಿ — …"), and the
  banned-wording bullet localised to the Kannada words it names. Maya Hindi took the Hindi block
  verbatim. No Hindi text leaked into either Kannada file (verified 0).
- **Files:** `KKB/KKB Placeholder Kannada Signals.md`, `KKB/KKB Placeholder Kannada.md`,
  `Maya/Maya Hindi.md`. Inbound variants deliberately untouched — their Hindi masters also lack the
  block, so that is a design question, not drift.
- **Status:** DEPLOYED (kkb-kn-signals, kkb-kn-out, maya-hi-out). **NOT VERIFIED** — needs a call
  from a number with prior memory.

## 2026-09-09 — Kannada apply-failure line blended two rows and re-asserted "technical issue"
- **Feedback/bug:** call `41a2c19d` returned `TARGET_ITEM_NOT_FOUND` three times and the bot said
  "ಈ ಜಾಬ್‌ಗೆ ಅಪ್ಲೈ ಇನ್ನೂ ಪೂರ್ತಿ ಆಗಿಲ್ಲ, technical issue ಇದೆ" every time — the new Row 2a opening welded
  to Row 2 cause claim. The two Kannada lines shared the prefix "ಈ ಜಾಬ್‌ಗೆ ಅಪ್ಲೈ ಇನ್ನೂ" and differed
  only in the verb phrase. Hindi passed the same test (`199caee7`) because its two lines are
  lexically distinct — a direct demonstration of the never-extrapolate rule.
- **Change:** Row 2a Kannada now opens on different words entirely — "ಈ ಅಪ್ಲಿಕೇಶನ್ ಸಧ್ಯಕ್ಕೆ ಆಗಿಲ್ಲ." —
  so there is no shared opening to blend, plus an inline note naming call `41a2c19d` so the wording
  is not "tidied" back into a shared prefix. Row 2 is UNCHANGED: its "technical issue" is there at
  the owner explicit request (see the note above the table) and was not removed.
- **Files:** the 4 KKB Kannada conversation prompts.
- **Status:** DEPLOYED (kkb-kn-signals, kkb-kn-out, kkb-kn-in-signals, kkb-kn-in). **NOT VERIFIED.**

## 2026-09-09 — the prohibition against speaking stage directions was supplying the string
- **Feedback/bug:** on `e4e81fe2` (kkb-kn-out, live) the bot spoke
  `*(Silent tool call: apply_job with profile_id: "5051" and job_id: "19e3da1f-...")*` aloud, leaking
  a profile id and a job UUID to the caller, then said "ಅಪ್ಲೈ ಆಗಿದೆ" — applied. **Zero tools ran on
  that call.** No `get_profile`, no `apply_job`, no application. Same class as `29c4f152` and the
  four occurrences on 2026-09-03 that the prompt already documents, so this guard has now failed
  five times. 6 more cached calls across kkb-kn-signals, maya-hi-out, kkb-hi-in and kkb-kn-out spoke
  a stage direction; two of them read the caller phone number `+917946350285` aloud inside a
  `create_profile` stage direction.
- **Root cause:** the guard quoted the forbidden output verbatim. Both the prohibition ("Writing
  `*(Silent tool call: apply_job)*` ... applies nobody") and the evidence citation for `29c4f152`
  wrote the exact string the bot then emitted. Rung 1 — the wrong output was in the prompt, in the
  rule meant to prevent it.
- **Change:** the literal form is gone from every prompt (verified 0 remaining). The prohibition and
  the citation now DESCRIBE it — "a stage direction naming the apply tool" — instead of printing it.
  No new prohibition wording was added: this guard had already failed five times, so volume was not
  the lever.
- **Files:** 12 KKB/Maya conversation prompts (TRRAIN and slim did not carry the string).
- **Status:** DEPLOYED to all 15 conversation targets, all verified in sync. **NOT VERIFIED** — needs
  a call that reaches an apply on a Kannada outbound bot.
- **Known larger change NOT made:** the samples still render 12-38 inline `*( )*` stage directions
  each. Converting them to a non-inline `INTERNAL:` form would remove the imitable shape entirely,
  but that is a 15-file reformat that cannot be tested in one night and needs sign-off.

## 2026-09-09 — slash spoken aloud: rule missing on 9 bots, and point-of-use missing on the rest
- **Feedback/bug:** tracker items "Slash is said out loud" were CLOSED, and the behaviour has
  regressed: **28 of 438 cached calls** emit a literal "/" inside a spoken line. Most common is the
  array role "Computer Operator / Data Entry" read verbatim (21 calls). Bots affected: dkb-kn-out,
  trrain-hi-out, kkb-hi-in-signals, maya-hi-out, maya-hi-in, maya-hi-in-signals.
- **Root cause, two halves.** (1) The "## Slash ( / ) symbol" section existed in the 12 KKB/Maya
  prompts but was ABSENT from all 6 DKB, both TRRAIN and slim — and dkb-kn-out and trrain-hi-out are
  among the offenders, so for them there was no rule at all. (2) On the bots that DO have the rule,
  it sits in its own section far from the template that speaks `[role]`. Same point-of-use failure
  as the location conversion, the `[company]` script fix and the never-invent guard.
- **Change:** ported the Slash section to the 9 prompts missing it (Kannada adapted: "ಅಥವಾ", not
  "या"), and added a one-line rule AT the job-presentation template in all 13 KKB/Maya/slim prompts —
  a `[role]` containing "/" is spoken with "या"/"ಅಥವಾ" in its place, naming "Computer Operator / Data
  Entry" as the worked case since it is the one that actually leaks.
- **Files:** 6 DKB + 2 TRRAIN + slim (new section); 12 KKB/Maya + slim (point-of-use line).
- **Status:** DEPLOYED to all 19 conversation targets, all verified in sync. **NOT VERIFIED** — needs
  a call presenting a slash-bearing role.

## 2026-09-09 — KKB and Maya spoke salary as digits (8% of salary phrases)
- **Feedback/bug:** 33 of 399 salary phrases across KKB and Maya carried digits — `f5a40741` said
  "12,000" and "16,000", `kkb-hi-in-signals` 17 of 120, `maya-hi-signals` 4 of 16. Found by
  `spoken_form.py`, not by the per-call grader, which had no salary check for KKB.
- **Root cause:** the rule exists — "Do not write digits in spoken Hindi output. Write them in
  words" — in the Numbers section, roughly 700 lines below the job-presentation template that
  speaks the value. Ninth instance of D82 tonight.
- **Change:** stated at the template itself, naming the two slots that actually leak: `[salary]`
  and `[vacancy]` arrive as digits and are spoken as words, with worked values per language. The
  distant Numbers section is left as it is.
- **Files:** 12 KKB/Maya conversation prompts + slim. **Status:** DEPLOYED to all 13 targets.
  **NOT VERIFIED.**
- **Also noted, not fixed:** Maya's identity line renders the college abbreviation twice —
  "माया, वीटीयू (VTU) की ओर से" reads the Latin in parentheses aloud (`0a3cba76`). Low severity, and
  Maya's caller-identity line is a product decision, so it is flagged rather than edited.

## 2026-09-09 — pincode: root cause and the three iterations it took (VERIFIED)
- **Reported:** Khushboo r5, "Pincode" not fixed. The bot read the written location with its digits.
- **Root cause, two things sitting three paragraphs apart.** (1) A paragraph titled "A PIN code is an
  identifier, not a number" that TAUGHT the pronunciation — "if one is ever spoken, say it digit by
  digit in words" — immediately followed by "Better: do not speak a PIN code at all". A permission
  next to a prohibition; the model took the permission. (2) The location block claimed "the sentence
  already contains the right place ... there is no resolution step" while the very next paragraph
  required a two-step conversion. Two contradictory instructions; `a9039634` obeyed the first and
  read "ಸರ್ಜಾಪುರ, 110045" out verbatim.
- **Three iterations, each on live evidence:**
  1. Deleted the pronunciation paragraph from all 5 prompts that carried it, and made step 1 read
     "**DELETE** every digit. Deleted, not rewritten — a PIN in Devanagari numerals is still a PIN".
     `1c6963bb` had rendered it as "११००४५".
  2. Moved the `${location}` token OUT of the spoken sentence onto its own line
     (`location_written is: ${location}`) so a conversion step exists between reading and speaking,
     and rewrote the contradicting paragraph. With the token inside the sentence the model read it
     verbatim.
  3. `29288fd3` then converted the place correctly and KEPT the pin code — step 2 ran, step 1 did
     not. Renamed the slot from "the spoken place" to **"place — without digits"**
     (`[जगह — अंकों के बिना]` / `[ಜಾಗ — ಅಂಕಿ ಇಲ್ಲದೆ]`), so the requirement is in the slot name.
- **VERIFIED on four calls, each variant independently:** on-list Hindi `b4e34994` and `13864c75`
  ("मुराद नगर"), off-list Hindi `2bb68def` ("सरजापुर"), off-list Kannada `aae2e523` ("ಸರ್ಜಾಪುರ").
  `location_said.py` over all traffic: 26 correct conversions, 3 RAW all pre-fix, 0 real-caller RAW
  since the first deploy.
- **Files:** `KKB Placeholder Hindi Signals.md`, `KKB Placeholder Kannada Signals.md` (the two-step
  block and the slot); the pronunciation paragraph removed from those two plus
  `KKB Placeholder Hindi.md`, `KKB Placeholder Kannada.md` and slim; the delete-not-rewrite clause
  added to Maya x4 and slim.
- **Analyser:** D82 (point-of-use), D83 (a concrete value beside a template becomes the output).

## 2026-09-09 — memory prompt no longer stores the jobs it presented (VERIFIED)
- **Feedback/bug:** the platform memory store carried previously-presented job lists into the next
  call and the bot offered them as current inventory. Given ONE job in `${recommendations}` the slim
  A/B bot offered four, the extra three being jobs from earlier calls — `45e2cb3b`, `293c92c2`,
  `11ce47ce`, `764cba1d`, **4 of 4, deterministic**. Every other channel was read and excluded on
  `764cba1d`: 1 job in args, `contact_memory` absent from `agent_args`, `get_profile` result clean
  (3,456 chars, no job names), no inventory table in the prompt, and only `get_profile` +
  `apply_job` called.
- **Root cause:** `KKB Memory.md` stored `last_options_presented` as job strings
  (`["2026-06-22: Electrician, Pune, 18K"]`). Nothing reads its contents — it is used only as a
  presence signal for the returning-caller callback clause, and its four siblings
  (`last_conversation_summary`, `jobs_applied`, `last_action`, `session_count`) serve that too. So
  the job text was pure exposure.
- **Change:** the field now stores a COUNT and a date — `["2026-06-22: 8 options shown"]` — with an
  explicit instruction not to store role, company, location or salary. `jobs_applied` is UNCHANGED
  because the duplicate check reads it. Same change in `Maya/Maya Memory.md`, whose example had
  named a role and a company ("Sales Executive, ABC Corp, Lucknow, 18K") — likely the source of the
  invented "एबीसी लॉजिस्टिक्स" on `a4f378b9`.
- **VERIFIED:** `7bf46d06` — 1 job supplied, exactly 1 job offered, immediately after `58eda292`
  presented a 12-job array. The pre-fix behaviour was 4/4.
- **Files:** `KKB/KKB Memory.md`, `Maya/Maya Memory.md`. Deployed to the 9 KKB conversation agents
  via `memory_instructions` (KKB has no separate memory agent — `raya/agents.json` marks
  `kkb-memory` `deploy: false` with an empty uuid) and to `maya-out-memory` / `maya-in-memory`.
- **I was wrong twice about this issue** and both are recorded in the overnight report: I said it was
  not fixable in a prompt, and that it could not be verified in one session. It was fixable in the
  memory prompt and verifiable with two calls.
- **See also** `raya/overnight/MORNING-2026-09-09.md` §11 — patching `memory_instructions` overwrote
  a live-only 7,489-char memory prompt on the four non-Signals KKB agents without a snapshot.

## 2026-09-09 — reconciliation flag for the unbacked apply claim (mitigation, not a fix)
- **Why:** the agent sometimes tells a caller their application went through when no `apply_job`
  ran at all — 1 of 11 REAL calls that claimed an apply (`4b6aca57`), 4 of 30 tester dials. Four
  prompt-side mechanisms and three candidate causes were tested against live calls and all
  falsified: memory disabled (`557fbeb0`), the narration form removed from the rule (`2126a5bc`),
  and all 151 sample demonstrations converted away (`f31e1587` — that one DID fix the stage-direction
  and phone-number leak, and the claim still remained). It needs the runtime; see
  `ESCALATION-litwiz.md` §1.
- **What this adds:** `unbacked_apply_claim` in the output prompt — "Yes" when a success line was
  spoken with no successful apply result in the transcript. It does not prevent the bug; it makes
  the affected caller findable so they can be rung back. An empty `jobs_applied` together with this
  flag set is exactly the case to surface.
- **Files:** `KKB/KKB Output.md`, `Maya/Maya Output.md`, and the live `output_instructions` field on
  all 13 KKB/Maya conversation agents (KKB/Maya output prompts have no agent of their own —
  `raya/agents.json` marks them `deploy: false` with empty uuids).
- **Every live-only prompt was snapshotted to `raya/live-snapshots/` BEFORE patching this time** —
  the correction to the mistake recorded in the overnight report §11.

## 2026-09-09 — the 12% already-applied defect has a root cause two layers away (DEPLOYED, UNVERIFIABLE tonight)
- **What the 12% actually is.** Row 1 (the already-applied line) has TWO routes: a duplicate
  pre-check that reads `jobs_applied` from `${contact_memory}`, and recognising
  `ACTION_LIMIT_REACHED` in the tool result. The pre-check is the reliable one. It is dead:
  **`jobs_applied` was non-empty on only 2 of 76 calls that carried it.** With an empty array the
  check can never fire, so every call falls through to the error-name route, which succeeds 12% of
  the time. The 2 calls where it IS populated are both inbound agents — and inbound is exactly where
  the already-applied line works (all 4 correct calls are inbound).
- **Why it was empty.** `KKB Memory.md` and `Maya Memory.md` DEFINE `jobs_applied` but never say
  what writes it, and the update rules say "update a field only if the conversation provides clear,
  direct evidence" — which reads as something the caller said. A successful `apply_job` result is a
  tool outcome, not a conversational statement, so it was never recorded.
- **Change:** the field now states that a SUCCESSFUL `apply_job` tool result IS the clear, direct
  evidence and must be APPENDED, carrying forward existing entries. Deployed to all 13 KKB/Maya
  conversation agents via `memory_instructions`, read-back confirmed on each.
- **UNVERIFIED, and it cannot be verified with the current harness.** The write rule only fires on a
  successful apply, and the tester profile `588a907f` has already applied to every job in the
  Ghaziabad inventory — `a656c451` tried two and got `ACTION_LIMIT_REACHED` on both. To verify:
  either clear that profile's applications, or use a fresh seeker profile, then run
  apply → next call → confirm the pre-check fires WITHOUT calling `apply_job`.
- **Prior attempts on this defect, all falsified against live calls** (`6caf1fbe`, `513a1d01`,
  `5bbb6ca1`): naming the error in Row 1, excluding it from the generic row, correcting the tool
  description's "you usually CANNOT read" premise, and collapsing to a single failure line. Those
  were all fixes to the FALLBACK route. This one repairs the primary route.

## 2026-09-09 — the apply-failure line no longer asserts something it cannot know (VERIFIED)
- **Why:** the routing between Row 1 (already applied) and the generic failure line is broken on
  BOTH of its routes — the duplicate pre-check ignores a `jobs_applied` entry naming the exact job
  (`7f2e3928`), and the error-name route fails after four separate mechanisms (`5bbb6ca1`). Since
  the wrong line gets picked ~88% of the time, the line itself had to stop being false.
- **Change:** "इस जॉब के लिए अप्लाई अभी पूरा नहीं हो पाया" → "इस जॉब के लिए आपकी दिलचस्पी हमने नोट कर ली है —
  इसकी अपडेट हमारी टीम आपको इसी नंबर पर देगी" (Kannada equivalent mirrored). It asserts nothing about
  whether an application exists, which is true whether the apply succeeded, failed, or failed
  because one already existed. Escalation-ladder rung 3, exactly as `CLAUDE.md` prescribes: rewrite
  the default so it asserts nothing that can be false.
- **VERIFIED:** `04c6f82a` — `ACTION_LIMIT_REACHED` returned, new line spoken, no claim either way.
- **Files:** 13 KKB/Maya/slim conversation prompts. An inline note names both call ids and says not
  to restore a wording that claims the application does or does not exist.
- **The routing bug itself remains** and is `ESCALATION-litwiz.md` §1 with three prioritised asks.
