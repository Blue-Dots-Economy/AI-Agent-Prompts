# KKB-Slim — Changelog

A/B twin of `kkb-hi-signals` (`115b38a5`). Same tools, voice, language, DID, timings, memory and
output prompts; the ONLY difference is the conversation prompt — a ground-up rewrite at ~73k chars
against the master's ~224k. It exists to test whether prompt size is what the latency complaints
are about. Not a language variant, so `/sync-check` must not treat it as a mirror.

## 2026-10-19 - Automated-message rule; false "already applied"; invented gender; PIN read with bars; under-18 line
- **Feedback/bug:** Aryan (2026-10-19): end calls on IVR/voicemail per the shared instructions. Today's live tests and the first nightly run found: "already applied" said with no `apply_job` when the caller said "फिर से अप्लाई"; the read-back said "ಮಹಿಳೆ" for a man who never answered; the PIN read back as "दो | शून्य | …"; a city from the job rows confirmed as the caller's location; lines wrapped in quote marks; an under-18 close composed with "18" in digits (nightly call `6b7454a9`).
- **Change (Hindi + Kannada):** top-priority automated-message rule; "What the caller says is never evidence" in the duplicate check; empty read-back slots left out; the silent PIN split uses commas; "a city in job results is never the caller's location"; no quotation marks in replies; a fixed under-18 line with the number in words.
- **Files:** `KKB-Slim/KKB Slim Hindi Signals.md`, `KKB-Slim/KKB Slim Kannada Signals.md`.
- **Verified (live):** applications go through again end to end, Hindi `c1ce0293` and Kannada (kkb-kn-new run, apply success on our test posting); education saves accepted (`Diploma` Kannada, `ITI` Hindi), r113; consent saved with the spoken age (`c1ce0293`, Kannada run); bare yes after the job details gets the one-line answer, r137 (`1d748aef`); unanswerable job question gets "यह कंपनी से बात होने पर पता चलेगा।", r144 (`c1ce0293`); PIN read with commas (`ae53a6af`).
- **VERIFY-PENDING:** already-applied on a real duplicate (r118; the repeat test's tester script was overwritten mid-call), the automated-message rule, the gender and under-18 fixes. `hold_message` on writes cannot be emptied from the prompt (the platform fills it): raised with Raya.
- **Verified later 2026-10-19:** voicemail answered with "Goodbye" only (Hindi `6c65aa09`, Kannada `ba701225`); off-topic request redirected in two short sentences, r141 (`cc664798`). Raya's error wrapper ("tell the caller it may or may not have gone through") overrides the already-applied routing even when the body says ACTION_LIMIT_REACHED (`078532ed`): override added to every Signals prompt, platform fix asked of Raya.

## 2026-10-13 - Tracker r111-r146 (Gaurav's Oct 6/8 campaign review) and Aryan's test sheet (KI-02, KI-12)
- **Feedback/bug:** 36 new tracker rows dated 12/10 plus Aryan's KKB Inbound + Slim test results (2 PARTIAL). Every row was grounded in the downloaded Oct 6-12 calls (1,139 calls over 20s) before any edit; the calls ran on the pre-2026-10-12 prompt.
- **Change (Hindi master, Kannada mirrored; English instructions byte-identical except the registered region list):**
  - r113 education values: `ITI` and `Diploma` (the backend rejected `ITI / Other Vocational Trainings` 5/5 and `Polytechnic / Diploma` 3/3); `otherHelpNeeded` mapped to the two values the API accepts.
  - r118 already-applied: `ACTION_LIMIT_REACHED` now appears only in the already-applied row (was said 0/5); already-applied rows are dropped in 6a.
  - r119 wrong ids: no `apply_job` after a failed `create_profile`; a phone, user id or job id is never a `profile_id`.
  - r122 invented age: the age row and `record_consent_new` tool description now allow only an age the caller said or the stored one.
  - r124/N1 invented jobs: removed "Never call `get_jobs`" from law 1; company examples are word-level, not whole names.
  - r125/r127 example values copied: every example PIN replaced by `<pin>`; worked calls no longer contain a PIN read-back; a digitless `${location}` gets the open ask, never the incomplete-pin line; Sarjapur removed from the names table.
  - r126 slots: dead "[city]" and "[शहर]" quotes removed; ambiguous role pick asks by company.
  - r128: rows that survive cleaning but do not match go to No-Match, never "no jobs".
  - r111/r117: stale "city is masked" fact corrected; 6a drops out-of-region rows (Kannada: outside Karnataka / Hubballi-Dharwad, registered divergence `kkb-slim-6a-region-list`) and test/placeholder companies.
  - r132: 27 worked-call notes rewritten as "Note (not spoken): ..." outside the quote block.
  - r134: "didn't catch the greeting" gets a short re-intro instead of the full greeting (was replayed on 112/729 calls).
  - r135: a yes to the role check no longer counts as naming new work (recommendations used instead of text search).
  - r136: unrecorded promises removed (closing "हमारी टीम फिर संपर्क करेगी", apply-failure callbacks).
  - r137: bare yes to the deep-dive question no longer repeats the deep dive.
  - r138: "call me later" asks a time once; output field 12a `callback_requested`.
  - r140: `hold_message` "एक मिनट" only on the four lookup tools; empty on writes and apply.
  - r141: off-topic requests declined in one line; three-sentence cap, no markdown.
  - r144: no sentence about a missing salary; a salary question gets "यह कंपनी से बात होने पर पता चलेगा।"
  - KI-02: mid-call "can't hear" gets one slower repeat before the bad-line close. KI-12: the 6b gate also requires the pin turn.
- **Not changed (decision needed):** r146 (move PIN/landmark after the first jobs; conflicts with KI-12), U18 callers who say they are adults.
- **Files:** `KKB-Slim/KKB Slim Hindi Signals.md`, `KKB-Slim/KKB Slim Kannada Signals.md`, `KKB-Slim/KKB Slim Output.md`, `raya/toolspecs/record_consent_new.json`, `raya/divergences.json`, `scripts/location_writeback.py`. Snapshots `pre-oct13-tracker`.
- **Follow-ups found by today's retests (same day):** (1) the consent save went out with an invented age or not at all after the age answer (`d795ee9a`, `9dd4f1c9`, `80ad26b5` invented; `da19618e` asked but never saved): the age is now asked before the consent question, the save is the sole reply to the age answer, and worked call B demonstrates that order (it previously showed a new caller with no consent ask at all); (2) step 0 still said "no jobs" covers irrelevant rows, contradicting the r128 fix (`2bfa078e`); (3) a qualification request ("mechanical diploma") now counts the trade's jobs as relevant (`f063e40c`); (4) Kannada worked call B's caller answer "ಹುಬ್ಬಳ್ಳಿ, ಕೇಶ್ವಾಪುರ" was read back as the caller's location (`da19618e`): example place answers are now neutral; (5) output field 12a came back as a timestamp: renamed `call_later_request` with text values.
- **Verified (live test calls, test numbers):** consent saved with the spoken age, Hindi `29771cd5`, Kannada `162a489b`; r128 trade jobs offered `29771cd5`; no invented place or PIN `162a489b`, `29771cd5`; r134 no greeting replay `2bfa078e`, `29771cd5`; r138 time asked `4451e954`; r140 no hold on saves `29771cd5`; PIN asked (KI-12) `29771cd5`, `162a489b`.
- **DEPLOYED, NOT VERIFIED:** r113 education save, r118, r119, r135, r137, r141, r144, KI-02 mid-call, output field `call_later_request` (short calls produced no output record).
- **New, minor:** since the last Hindi deploys the bot wraps its lines in quote marks (`f063e40c`, `29771cd5`); not yet traced.
- **Location write-back switched on (r121, approved by Parth 2026-10-13):** `scripts/location_writeback.py` now writes ONE address
  string, `<landmark>, <area>, <City>, <State> <PIN>, India`, into the profile's single `location` field (agreed on the 13/10 call,
  since the DPG schema has one field). Backfilled 55 campaign profiles (0 failures); runs every 15 minutes for both KKB Slim
  bots via launchd (`org.ekstep.location-writeback`, `scripts/location_writeback_cron.sh`, log `raya/location-writeback.log`).
  Fixed on the way: calls are processed oldest first so a caller's latest answer wins (newest-first let an older call
  overwrite it; 5 callers re-run), and a refused profile lookup (U18) is skipped instead of crashing. Limit: it runs only
  while this Mac is on; a missed window is caught up only for calls still in the latest 100.
- **Analyser:** D111-D115.

## 2026-10-12 - Aryan's GZB review: consent lost for new callers, irrelevant recommendations, unconfirmed service yeses
- **Feedback/bug:** Aryan's email with `KKB_Oct06_Dropoff_Analysis.xlsx` (issues 2-4). Grounded in 85 real calls on `kkb-hi-signals-slim` before any edit.
  - Consent: 10 new callers said yes to the disclosure but consent was only written later by `create_profile`, so every drop before that step lost it; existing callers with no consent got `record_consent` 1/5 times. (25 more calls hit `get_profile` 400 `U18_NOT_ALLOWED`: backend, see below.)
  - Recommendations: 14/63 searches used the query `"helper"`, which was the prompt's own default for an undecided caller; results read out "ITI (Other)" (a qualification, not a role) and duplicate rows; the OPEN location ask spoke a literal "[city]"; worked call B carried a Sarjapur example that the bot reused when `${location}` was empty.
  - Services: 17/45 "Yes" were bare "हाँ"/"ठीक है" backchannels to a statement, never a real yes.
  - Callback promises the team cannot keep ("एक-दो दिन में", "हम आपको कॉल करेंगे") on no-jobs and bad-line exits.
- **Change (Hindi master, Kannada mirrored):**
  - Step 3.5: yes from a caller with a seeker item = `record_consent` alone; with no item = name + age, then the new `record_consent_new` tool (writes consent at once); under 18 = no call. Step 9 never calls `create_profile` after `record_consent_new`; step 10 uses `update_profile` on that item.
  - Undecided caller: no default query; ask the trade/qualification instead. 6a cleaning drops qualification-as-role rows and keeps one row per role + company.
  - OPEN ask is a neutral question with no slot. Worked call B now starts with `${location}` empty.
  - Section S: only a reply to the offer counts; bare agreement gets ONE time question, a named time = Yes + `service_callback_slot`, filler = Maybe, unclear closes with "ठीक है, कोई बात नहीं।" No callback promises anywhere (no-jobs line and bad-line close rewritten).
  - Output: field 17 `service_interest` redefined on the caller's own words; new 17a `service_callback_slot`.
- **Files:** `KKB-Slim/KKB Slim Hindi Signals.md`, `KKB-Slim/KKB Slim Kannada Signals.md`, `KKB-Slim/KKB Slim Output.md`, `raya/toolspecs/record_consent_new.json` (applied to both slim agents). Snapshots in `versions/KKB-Slim/` (`pre-oct12-consent-recs`) and `raya/live-snapshots/*.output_instructions.pre-2026-10-12.md`.
- **Verified (live calls, test numbers only):** new-caller consent written before profile, Hindi `6560f39e` (backend shows terms/privacy true) and Kannada `d9154118`; existing caller `record_consent` alone, Hindi `3e3f7d69`, Kannada `930a8667`; undecided caller asked the trade and searched "electrician" (`6560f39e`) / "fitter" (`d9154118`), no "helper"; bad-line close without a callback promise, Hindi `6296a5be`, Kannada `c85dc5b7`; returning-caller regression clean `444480ed`.
- **VERIFY-PENDING:** service-confirmation question (tester went silent before the offer on `bfb02c5e`/`8877a6fb`; see the final batch); no-jobs line on a real empty search.
- **Not prompt bugs (flagged, not fixed):** every `apply_job` 422 since ~Oct 6 (backend rejects the consent field it also requires); `U18_NOT_ALLOWED` on about half the ITI/Poly contacts; job inventory quality (duplicates, "na"/"Any" roles, Karnataka rows on gzb, masked locations, scores 0.45-0.6).
- **Analyser:** D106 (consent written at a later step), D107 (default search value), D108 (offer ending on a statement), D109 (example input value reused when the input is empty).
- **PIN loop (found by today's retest, same day):** test call `fad874e4` asked for the pin 20+ times while the caller kept saying "201002" (call hit max duration). Cause: the pin check said "every time, split `${location}`", and `${location}` never changes, so every answer was judged "no pin". Real calls had the milder form (valid chunked pins rejected 2-4 times; 24/32 pin turns used the incomplete-pin line with a digitless `${location}`). Fix: `${location}` decides only the first pin sentence; after that only the caller's answer is split (chunks joined); hard cap of two re-asks. Snapshot `pre-pin-loop-fix`. Analyser D110. **Verified:** Hindi `c6f1efa1` (chunked "20:10, 02" joined, read back once, moved on), Kannada `a0eada1b` ("580021" read back once, moved on).

## 2026-10-05 — Kannada slim ported to the live job/services APIs; now answers the Kannada INBOUND number
- **Feedback/bug:** same request (Operation Rozgar inbound readiness). The Kannada slim still read a
  campaign-injected `${recommendations}` list and had no job/services tools, so it could not serve
  inbound calls; its phone tool params still said "91 + 10 digits" (doubles on outbound).
- **Change:** `KKB Slim Kannada Signals.md` re-mirrored to the Hindi master throughout (one bot both
  directions, no direction branching; jobs via `get_recommended_jobs`/`get_jobs`; section S + step 13
  services offer; jobs-interest gate; worked call D; phone target-format rule; today's step-3.5
  new-caller consent fix). Spoken lines in Kannada, examples re-set in Hubballi/Dharwad, persona
  ಮಾಯಾ kept (registered divergence). Tools added on Dharwad (`raya/toolspecs/get_recommended_jobs.json`,
  `raya/toolspecs/kn/get_jobs.json`, `raya/toolspecs/get_services.json`); phone param of
  create_profile/update_profile/record_consent set to the target-format description; output
  prompt now `KKB Slim Output.md` (previous live one saved in `raya/live-snapshots/`).
  in_did `918037006352` moved from `kkb-kn-in-signals` to `kkb-kn-signals-slim` (state saved in
  `raya/live-snapshots/inbound_move_2026-10-05.json`).
- **Verification:**
  - `1a565768` (bot dialled the tester, cold): get_jobs "CNC Operator" → Orione Hydraulics, Basava
    Industries, Pavan Drives (Dharwad) → apply_job SUCCESS → profile completed → get_services empty →
    no service invented → close. CONFIRMED.
  - `887d1acf` (tester dialled +91 80 3700 6352, real inbound): routed to the Kannada slim, returning
    caller recognised, PIN read back, live jobs; apply 422 because the same profile had applied to the
    same job on `1a565768` — failure line made no claim. CONFIRMED (routing + flow).
  - New-caller path on Kannada: NOT_EXERCISED.
- **Known:** Dharwad has 0 service providers (gzb has 8) — the services offer always ends "not
  available"; worked call B still shows a new caller with no step-3.5 ask (both languages; copied from
  the master); the master's leftover "Need Capture" references and law 1 "never call get_jobs" were
  copied for parity — fix in both via /update-prompt.
- **Files:** `KKB-Slim/KKB Slim Kannada Signals.md`, `raya/toolspecs/kn/get_jobs.json`,
  `raya/live-snapshots/*`, `raya/testcases/args/kn-slim-cold.json`.

## 2026-10-05 — Slim Hindi now answers the production Hindi INBOUND number; new-caller consent fix (Hindi)
- **Feedback/bug:** Aryan (Operation Rozgar thread, 2026-10-02) asked for the Hindi and Kannada inbound bots
  to be ready for team testing from 2026-10-05. Investigation: the inbound Signals bots
  (`kkb-hi-in-signals`, `kkb-kn-in-signals`) never call the job API — they read a hardcoded 4-job list,
  and the prose around it still described the pre-cutover Bengaluru inventory, so live calls offered an
  invented "AC Technician, Krishna Enterprises, Bengaluru" job (`98a684b9`, `0edced72`; analyser D105).
  Parth chose to move the inbound numbers to the Slim bots, which fetch live jobs.
- **Change 1 (config):** in_did `911204404274` moved from `kkb-hi-in-signals` to `kkb-hi-signals-slim`.
  Prior state saved in `raya/live-snapshots/inbound_move_2026-10-05.json` (slim had `917946350283`, which
  is not provisioned for inbound; the old inbound agent keeps its out_did and is a fallback).
- **Change 2 (prompt):** step 3.5 — a brand-new caller (no seeker item; the backend still returns the
  `compliance` rows, all false) now gets the consent ask and, on yes, calls NO tool; `create_profile`
  records consent at step 10. `record_consent` only when a seeker item exists; an error from it is never
  read as a "no". Root cause (D1–D3): since the 2026-09-23 terms change, 7 of 10 new-caller calls sent
  `record_consent` with an invented all-zero `profile_id` (400); on `475f5cbb` the bot then said goodbye
  to a caller who had just agreed. The exclusion existed only in the Tools section, far from the
  step-3.5 "Agree" bullet that mandated the call.
- **Verification (real inbound calls on +91 120 440 4274, tester dialling in):**
  - routing + live jobs + apply: `b17a3bf2` — get_jobs "data entry operator" → 3 Ghaziabad jobs →
    apply_job success (Bottmac India) → get_services → TRRAIN Trust offered → close. CONFIRMED.
  - new-caller consent: `ce679ec3` — consent agreed, NO record_consent, call continued to get_jobs,
    PIN, landmark, jobs read out. CONFIRMED (1/1; N≥3 still owed). create_profile + apply on the
    new-caller path NOT_EXERCISED (the tester's audio dropped at turn 29).
  - bug reproduction before the fix: `475f5cbb`.
- **Open (found today, not fixed):** stage directions spoken aloud on 3/52 calls (e.g. "*(Fetching
  services for the closing offer)*" on `b17a3bf2`) — copied from the worked examples' `*( )*` notes;
  PIN/landmark skipped for a returning caller (`b17a3bf2`); Turn A spoke "आपकी जॉब की लोकेशन है" with no
  place for a new inbound caller (`ce679ec3`); bad-line close promises a call-back on inbound calls.
- **Files:** `KKB-Slim/KKB Slim Hindi Signals.md`, `raya/live-snapshots/inbound_move_2026-10-05.json`,
  `raya/personas/hi-inbound-*.md`, `.claude/skills/prompt-analyser/reference/bug-patterns.md` (D105).

## 2026-09-23 — PINs must be six digits; the bot no longer invents one (Hindi + Kannada)

- **Feedback/bug:** Khushboo's UAT call `04365ced` carried `${location}` = `Delhi, 11024` (five digits)
  and the bot read it back as a pin. Owner's rule: every captured pin is six digits, or the caller is
  asked to check and repeat it.
- **What investigating it found — a worse, older bug.** Across 41 live calls the "ask for the pin"
  branch had fired **0 times**. Whenever `${location}` carried no pin the bot read one back anyway, and
  it was always **110045** — the pin in the prompt's worked examples, which pair it with Muradnagar
  (D102). Reproduced on a never-registered number with no memory (`ff13bfaa`), ruling out stored data.
  **Correction:** this morning's inbound pass `2027e477` was one of these — its `${location}` was empty,
  so the 110045 it read back was fabricated. It was scored as a pass; it was not.
- **Attempts:** a rule, then a split-then-count procedure — both 0/3 on five-digit input (models misjudge
  a number's length). Then fixing the demonstrations: worked call B now shows the ASK path, Turn B opens
  with a side-by-side input → decision table, and every example pin is re-paired with its own place so
  none can be transplanted (110045 removed from both prompts). The caller-given rule's "then accept
  whatever comes" ending is replaced with a terminal reject.
- **Verified (current build):**
  - **No pin in the data → asks, invents nothing** — `5f73c94d` (Muradnagar, clean number).
  - **Caller gives five digits → not accepted, asked again, six stored** — `986c0196`, `54c48491`.
  - **Valid pin → confirmed as before** — `e2952625`, `baa48e78`.
- **Still unreliable — five-digit pin IN THE DATA:** 1 of 2 (`ee2f7c0d` asked; `d4294874` read back
  "एक, एक, शून्य, दो, चार", though the caller corrected it and `201206` was stored). This is the model's
  counting limit, and prose has been tried three ways. A reliable fix needs the decision out of the
  prompt — see the owner decision in the report.
- **Output prompt:** the split-and-count check for `pin_code` added; it had recorded a confirmed
  "11024" as "110024", inventing a digit (`2ad96965`). Not yet re-verified on a five-digit case.
- **Seen, not caused here, not fixed:** on `c45a7ff3` the bot skipped the pin and landmark turns after
  an audio hiccup made it repeat Turn A; on `5f73c94d` it said "सैलरी उपलब्ध नहीं" — the absent-field
  announcement fixed this morning, recurring.
- **Files:** both slim conversation prompts, `KKB-Slim/KKB Slim Output.md`, analyser D101 + D102,
  personas `hi-pin-*`, fixtures `tc-pin-*`.

## 2026-09-23 — the caller's location now reaches the backend and is geocoded (post-call writer)

- **Ask:** geocode the location the caller gives, silently update the backend, don't affect the call;
  test with 5–6 bus-stop scenarios; and "will it re-geocode every time a user updates their location?"
- **No geocoding service needed.** The Signals backend already geocodes the profile's `location` string
  into `item_locations` on every write. Nine direct scenarios on a probe profile: agrees with
  OpenStreetMap within **0.15–0.76 km** wherever OSM has a reference (Modinagar Bus Stand, Vaishali
  Metro, Sahibabad Railway Station); handles a typo ("Bas Stand"), Devanagari, and an unknown shop (falls
  back to the locality, invents no point). **Every update re-geocodes.** For the record, Google's
  Geocoding API would have been 10,000 free/month then $5 per 1,000, billing account required.
- **The actual gap:** the location a caller gave reached the backend on **0 of 10** calls. The only write
  instruction sat in step 12 (successful apply only), and skipped when an area was "already captured".
- **Three in-call designs failed — do not retry them:**
  - *`update_profile` with `location`* — sent `role` instead of `location` (`482ea2e2`).
  - *A dedicated `save_location` riding the job fetch* (v2–v4) — the bot skipped the location questions:
    **4/4 asked before the tool existed, ~2/7 with it** (`28f4cf52`, `ea133066`, `9c0aeb63`). Its trigger
    ("after the questions are finished … or skipped") was satisfiable by `${location}` merely being in
    context — D95 written into a tool. Three wordings, same collapse.
  - *`save_location` riding the services step* (v5) — questions protected **6/6**, but the save fired on
    **2 of 8** calls: lost when the call ended early, forgotten when it did not (`793df52c` reached
    `get_services` and still skipped it).
- **What shipped:**
  - **`scripts/location_writeback.py`** — after the call, reads the call record and writes
    `"<landmark>, <area>, <City>, <State>, India"`. Nothing runs in the call. Safety: the phone is the
    one the bot used for `get_profile`, normalised in code; it never writes unless that phone resolves to
    an EXISTING user with a live profile (the endpoint finds-or-creates by phone); it waits until the
    post-call summary exists; and it drops a landmark that names the caller's old area after a move.
  - **Output prompt:** new `home_area` field (the caller's FINAL area); `nearest_landmark` now takes the
    final answer too, stated in the field's first line rather than an appended paragraph.
  - **Conversation prompt:** the confirm-role branch now routes to the location turn, as the
    change-of-role branch always did; `save_location` removed entirely (tool and prompt).
- **Verified — the writer on six real calls, each a different place, all 0.00 km from target:** Muradnagar
  Bus Stand `a09ad28a` (12.6 km from the city centre), Modinagar Bus Stand `c3eb8d17` (21.4 km), Vaishali
  Metro `793df52c` (11.5 km), Sahibabad Railway Station `f8108db8` (8.9 km), Shipra Mall `33873466`
  (9.2 km), no landmark known `9d87be89` (Raj Nagar Extension, 4.4 km). Three of those are calls where the
  in-call save had failed.
- **Mid-call move** (`6c12ef52`): caller confirmed Muradnagar, then said they had moved to Modinagar. The
  first write used the stale pre-call area (the summary was read too early) — fixed by the readiness
  check; re-run lands on **Modinagar**, 0.43 km from the bus stand they named.
  - **The bot ignored the move** (`a8281e55`): its step-12 read-back still said "एरिया मुराद नगर", the
    caller agreed, and the old place was recorded. Fixed with a "latest word on where they live wins"
    rule and a recency-defined read-back slot (analyser D100). **Verified on `ff922409`:** the bot said
    *"मैं समझ गई कि आप अब मोदीनगर में रहते हैं"*, `home_area` = Modinagar, and the writer landed on
    Modinagar, 21.3 km from the city centre. **The read-back path itself is VERIFY-PENDING** — that
    call's apply did not succeed, so step 12 never ran.
  - **`nearest_landmark` still keeps the pre-move stop (0 of 3 move calls)** after two prose edits. Not
    reworded a third time; the writer's code guard drops a landmark naming the old area, so the result
    is locality-level — Modinagar, 0.43 km from the named bus stand — rather than exact.
- **Location questions without any in-call save:** all three asked on `6c12ef52`.
- **NOT deployed as a running service.** The writer is proven but runs on demand. Where it runs after
  every call — the existing `kkb-dashboard` webhook (recommended; production, other repo) or a scheduled
  job here — is the owner's decision.
- **Files:** `KKB-Slim/KKB Slim Hindi Signals.md`, `KKB-Slim/KKB Slim Output.md`,
  `scripts/location_writeback.py`, `raya/toolspecs/save_location.json` (retired), personas
  `hi-geo-g1..g7`, fixtures `tc-geo-g1..g7`.

## 2026-09-23 — NEW BUG FOUND, NOT FIXED: KKB Slim Kannada invents jobs when the array is missing

**Severity: high. Reproduced 2/2. Recommend keeping kkb-kn-signals-slim out of UAT until fixed.**

- **What happens.** With no `${recommendations}` in `agent_args`, the bot invents jobs and reads them
  out as real. On `24e5dabd` it offered *ಎಬಿಸಿ ಸೊಲ್ಯೂಷನ್ಸ್* and *ಗ್ಲೋಬಲ್ ಟೆಕ್*; on `7fa799eb`,
  *ಗ್ಲೋಬಲ್ ಸೊಲ್ಯೂಷನ್ಸ್* and *ಟೆಕ್ ಸೊಲ್ಯೂಷನ್ಸ್* — **different names each call**, so it is generating
  them, not reading a stale list. It also invented salaries, qualifications and position counts, then
  answered follow-up questions about the invented job.
- **It goes as far as applying.** On `7fa799eb` it invented a job UUID
  (`7316715d-5900-479e-b873-195034636384`) and called `apply_job` with it; on `24e5dabd` it passed the
  **profile id as the job id**. Both returned `422` from dharwad-signals. **The backend's rejection is
  the only thing that stopped a real write.** The bot then told the caller their interest was noted and
  the team would call back — so the caller ends the call believing they applied to a job that does not
  exist.
- **Also on the same call:** a `*( )*` stage direction spoken aloud, which the prompt forbids outright.
- **Root cause (D98) — not missing guards.** The Kannada slim prompt carries **seven** "never invent a
  job" prohibitions, the same as its Hindi twin, which does not do this. Three things combine: the
  greeting promises jobs before anything knows whether any exist; there is no job tool on this agent,
  so a missing array is *silence* rather than an empty tool result the model must react to; and the
  escape line is guarded against misuse (*"more than zero and you may NOT say this line"*) but is
  **never made obligatory when the count is zero**. A promise, no observable absence, and no mandatory
  way to say "there are none".
- **Why Hindi is not exposed.** It fetches through `get_jobs` / `get_recommended_jobs`, so nothing
  arrives as an empty tool RESULT. Verified correct on `d70126e8` and `4dfcc12f`, which both said
  no-jobs and moved to services.
- **Fleet exposure — untested, assume present.** Every bot on the injected-array design shares the
  same two conditions. The non-slim Signals prompts carry only **2** never-invent guards against
  slim's 7, so they are less protected. Each needs one call with an empty array.
- **NOT FIXED.** This is a Kannada-slim prompt bug, outside the Hindi scope set by the owner, and the
  fix direction (make the zero path mandatory and terminal, or tie naming a job to quoting its
  `job_id`) is a behaviour change that needs its own approval and its own verification calls.

## 2026-09-23 — the services offer gets a turn of its own, even when what preceded it was a statement (Hindi + Kannada)

- **Feedback/bug:** on `d4dd4668` the bot delivered the no-match line and the services lead-in in one
  breath — *"अभी आपके लिए मुझे जॉब्स नहीं मिल रहीं — एक बार फिर से देखकर मैं आपको वापस कॉल करती हूँ।
  जॉब्स के अलावा हमारे पास कुछ और मदद भी है…"* Telling someone there is no work for them and pitching
  something else in the same breath reads as hurrying past the bad news.
- **This was the first bug run through the new diagnosis phase** (root `CLAUDE.md` → D1-D3, added the
  same day). It paid for itself twice over:
  - **D1 (count)** — my first count measured the wrong turn and reported 0/11 bundled, because I
    checked the *offer* turn, which is clean on every call. Re-counting the turn that actually carries
    the no-match line gave **1/3**.
  - **D2 (segment)** — the two clean calls (`d70126e8`, `4dfcc12f`) are the same scenario as the
    bundled one and both split it into two turns, so there was no input that discriminated. That
    ruled out a condition-on-input bug and pointed at the guard.
  - **D3 (read the guard)** — found the actual cause, and a second defect nobody had reported.
- **Root cause.** The rule read *"Never in the same turn as another **question**."* **The no-match line
  is a statement, not a question**, so the prohibition as written never covered it. The bot was not
  breaking the rule; the rule had a gap.
- **Second defect, found by D3, not reported by anyone.** The same clause still said the offer could be
  *"folded into the success turn per step 11"* — which step 11 had been changed to forbid outright the
  previous night. A cross-reference goes stale the moment the section it points at changes. Deleted.
- **Change (agnostic, identical English in both languages):**
  - The positional rule now reads: the offer gets a turn of its OWN, and **nothing else may share it —
    not another question, and not a statement either**, with the no-match case named explicitly.
  - The stale "folded into the success turn" clause is deleted.
  - A pointer added at the **point of composition** — beside the no-match line in the No-Match
    Fallback — saying that line ends its turn and the services move belongs to the next one. Same
    placement that fixed the `'Any'` leak; the rule states the constraint, the pointer catches it
    where the sentence is actually built.
- **Files:** `KKB-Slim/KKB Slim Hindi Signals.md`, `KKB-Slim/KKB Slim Kannada Signals.md`,
  `.claude/skills/prompt-analyser/reference/bug-patterns.md` (D97).
- **Sync:** both languages carried the identical rule and the identical stale clause; fixed verbatim in
  both. No divergence entry — the change lands in every language of the family.
- **Status: Hindi VERIFIED. Kannada verification in flight.**
  - **Hindi — `e8b6de81-ffbc-4bf7-a5d9-cbfe139705d5`** (123s), the direct repro: same fixture and same
    persona as `d4dd4668`, caller wants teaching work, none exists. The no-match line now ends its
    turn, the caller answers ("अच्छा, ठीक है"), and the services lead-in opens the NEXT turn — with
    *"कोई बात नहीं।"* in front of it, acknowledging the bad news before moving on, which is precisely
    what the rule exists for. Three clean turns: no-match → wait → lead-in → wait → `get_services`
    and the named offer.
  - **Kannada — first attempt did NOT test the fix; re-run in flight.** `aaa2e470` (211s) never
    reached the no-match branch: the fixture carried a `${recommendations}` array, so the bot showed
    jobs, applied, and arrived at the services offer by a different route. The turn separation held on
    that route, but it is not the path that was changed. Re-running on `kn-slim-nojobs.json` (the same
    fixture with the array removed), which forces the empty-array no-match line.
- **Known gap the Kannada attempt exposed — not caused by this change, not fixed here.** The Kannada
  slim agent has **no `get_services` tool** (`get_profile`, `create_profile`, `apply_job`,
  `update_profile`, `record_consent` only); it is still wholly on the pre-2026-09-23 services design.
  On `aaa2e470` it therefore used the retired generic pitch — *"ಜಾಬ್ ಸಿಗುವ ಚಾನ್ಸ್ ಇನ್ನೂ ಹೆಚ್ಚಿಸೋಕೆ ನಮ್ಮ
  ಹತ್ರ ಕೆಲವು ಸರ್ವಿಸ್ ಪ್ರೊವೈಡರ್‌ಗಳಿದ್ದಾರೆ… ನೀವು ಇಂಟರೆಸ್ಟೆಡ್ ಇದ್ದೀರಾ?"* — and named no organisation,
  which is exactly the wording step 13 calls retired because it asks people to consent to something
  undescribed. **The shared step-13 text now instructs the Kannada bot to do something it has no tool
  to do.** The services redesign was scoped to Hindi by the owner, so this is a consequence of that
  scope, not a regression; it needs either the tool ported to Kannada or the shared section split.

## 2026-09-23 — the landmark turn's skip test accepted an AREA as a landmark (Hindi + Kannada)

- **Feedback/bug:** Khushboo's UAT report, "nearby landmark is not being asked or confirmed at the
  end". Measured at **6 of 16** live calls that reached the location block with no landmark already on
  record. Two earlier attempts had failed to move it (see the previous entry).
- **Root cause — the bot was obeying the rule and answering its test wrongly.** Turn C's skip test
  read *"the skip needs a positive reason — a landmark you can actually point at in the context"*,
  while the same section, twenty lines down, said the captured landmark *"is persisted in step 12 as
  `location` = '<landmark or locality>, <City>, <State>, India'"*. Together those say the landmark
  lives in `location` — so an injected `${location}` of `Muradnagar, 110045`, which Turn A had just
  read aloud, counted as a landmark it could point at. FOUND ONE → SKIP, and the **FOUND NONE → YOU
  MUST ASK** branch was unreachable on exactly the calls that needed it. The split is clean:

  | `${location}` | landmark asked |
  |---|---|
  | area **+** pin | 2 / 12 |
  | absent, or an area with no pin | 5 / 6 |

- **Change (Turn C, agnostic — identical English in both languages):**
  - `${location}` is named as **not** a landmark source: a town, locality, city, district, state or
    PIN read out of it is not a landmark, however specific it looks, and having just said that value
    aloud in Turn A is not the same as holding their landmark.
  - A landmark is defined by **type** — a named point a person can stand at (bus stop, railway or
    metro station, market, school, hospital, temple or mosque, mall, factory gate). An administrative
    place name is an AREA, not a point.
  - The step-12 write is made **one-way**: `location` is where a landmark goes, never where one is
    read from.
  - The genuine skip is untouched — a caller who really did give us their bus stop before is still
    never asked again.
- **Files:** `KKB-Slim/KKB Slim Hindi Signals.md`, `KKB-Slim/KKB Slim Kannada Signals.md`,
  `.claude/skills/prompt-analyser/reference/bug-patterns.md` (D95 rewritten — its earlier text named
  the wrong cause).
- **Sync:** the Kannada twin carried this section **word for word**, so it had the identical bug. The
  fix is agnostic and was mirrored verbatim; only the worked example is localized (`Muradnagar,
  110045` → `Keshwapur, 580023`). Section parity re-checked. No divergence entry needed — this change
  lands in every language of the family.
- **Status: VERIFIED on both languages.**
  - **Hindi — verified twice, both on the area+pin repro condition (`${location}` = `Muradnagar,
    110045`), the exact input that produced 2/12 before.**
    - **`462e2425-6e80-459c-bcb5-4ba726b991f6`** (179s): all three turns in order — Turn A confirmed
      मुराद नगर, Turn B read the pin back as six digit-words, Turn C asked *"आखिरी सवाल, फिर सीधे
      जॉब्स पर आती हूँ — आपके घर के सबसे नज़दीक कौन सा बस स्टॉप, रेलवे या मेट्रो स्टेशन है?"* and the
      caller answered "मुरादनगर बस स्टैंड पास है।" Jobs fetched only after that.
    - **`344182e7-b9a3-45d0-b3cf-618abeb16791`** (186s) is the stronger one: it **merged the role line
      into Turn A** ("ठीक है, डेटा एंट्री ऑपरेटर की जॉब्स देखती हूँ। हमारे पास आपकी जॉब की लोकेशन मुराद
      नगर है — क्या यह सही है?"), which is precisely the compression that cost BOTH turns on
      `d70126e8` and `2b529ea1` — and it still asked the pin and the landmark.
  - **The pin misses share this root cause.** Of the three, the two clear ones (`d70126e8`,
    `2b529ea1`) were both *role change + populated `${location}`*; the two role-change calls whose
    `${location}` was empty (`612eda02`, `8ae650f2`) asked both turns normally, because they had to.
    So a populated `${location}` explains the landmark misses and the pin misses alike.
  - **Tier 2 — the role-change path, verified on `d4dd4668-da68-4667-b9ff-e99c20afec45`** (120s).
    This is a byte-for-byte repro of `d70126e8`, the call that lost BOTH turns: same fixture, same
    `${location}`, the caller says *"मुझे पढ़ाने का काम चाहिए, टीचर की जॉब"*, `update_profile` fires,
    and the bot merges the role line into Turn A exactly as before — *"ठीक है, टीचर की जॉब्स देखती
    हूँ। हमारे पास आपकी जॉब की लोकेशन मुराद नगर है — क्या यह सही है?"* On `d70126e8` the pin and the
    landmark were both skipped from here. Now both fire: the pin is read back as six digit-words and
    the landmark is asked before `get_jobs`. The rest of the call is also correct — no teaching jobs
    exist, so the no-match line ran and no unrelated job was offered, then `get_services` named
    ट्रेन ट्रस्ट.
  - **Minor, noted not fixed:** on `d4dd4668` the no-match line and the services lead-in shared one
    turn (*"अभी आपके लिए मुझे जॉब्स नहीं मिल रहीं — … जॉब्स के अलावा हमारे पास कुछ और मदद भी है…"*).
    Step 13 asks for the offer in its own turn. The offer itself was made correctly with
    `get_services` behind it, so this is a packaging deviation, not a miss.

  **Repro condition now passing 4 of 4** (`462e2425`, `344182e7`, `88c8ecdd`, `d4dd4668`), against
  2 of 12 before.
  - **Kannada — verified on `88c8ecdd-ff35-4b7e-b593-a02afea5f177`** (207s), tested independently per
    the test-every-variant rule. `${location}` was `Keshwapur, Hubballi, 580023` — the same area+pin
    condition — and all three turns ran: Turn A confirmed ಕೇಶ್ವಾಪುರ, ಹುಬ್ಬಳ್ಳಿ (the full area, not
    just the first word), Turn B read the pin as six Kannada digit-words *"ಐದು, ಎಂಟು, ಸೊನ್ನೆ, ಸೊನ್ನೆ,
    ಎರಡು, ಮೂರು"* = 580023 with both zeros spoken, and Turn C asked *"ಕೊನೆ ಪ್ರಶ್ನೆ, ಆಮೇಲೆ ನೇರವಾಗಿ
    ಜಾಬ್‌ಗಳಿಗೆ ಬರ್ತೀನಿ — ನಿಮ್ಮ ಮನೆಗೆ ಹತ್ರದಲ್ಲಿ ಯಾವ ಬಸ್ ಸ್ಟಾಪ್, ರೈಲ್ವೆ ಅಥವಾ ಮೆಟ್ರೋ ಸ್ಟೇಷನ್ ಇದೆ?"*
  - Telephony note: the first two Hindi attempts died at 8s with no tester leg created at all
    (`bd7f84ea`, `216ae2c5`) while the bot answered and spoke normally. DIDs were unchanged
    throughout; the third attempt went through untouched. Carrier-side, not the prompt.

## 2026-09-23 — the services offer now survives a failed apply (VERIFIED); the location-turn fix was attempted and REVERTED

- **Feedback/bug:** two defects found by counting live calls rather than by reading the prompt.
  (1) **Khushboo's UAT report** — "pincode is missing, only city name is asked or confirmed" and
  "nearby landmark is not being asked or confirmed at the end". Across the 13 live calls that reached
  the location block, the pin was read back on 10 and the landmark asked on 6; exactly one of the
  seven landmark misses had a landmark genuinely on record (`28704be3`), so the real score is
  **6/13**. (2) **The closing services offer never fired after a FAILED apply** — `c883aa34` and
  `670cbb12` both went from the failure line straight to Goodbye with `services_pitched: No`, while
  every successful-apply call made the offer.

### Shipped and VERIFIED — the services offer after a failed apply

Two competing instructions were routing the failure path past step 13, both nearer the decision than
step 13 itself:

- the failure branch read "**On FAILURE the turn ends on the offer of another job and NOTHING follows
  it** — no service-provider pitch", scoped to *the turn* by intent and read as scoped to *the path*.
  It now says "no service-provider pitch **in this turn**" and states where the offer is still owed;
- the second-failure route "Then Graceful Exit" became "Then **step 13**, then Graceful Exit";
- **step 14's pre-close checklist gained a second item** — "has the services offer been made?" — beside
  the Need Capture check that already works reliably. A checklist naming one owed item implies the
  list is complete, which is why step 13's own prose was being skipped.

**VERIFIED on `6ae79885`** (171s): `apply_job` returned 422, the bot spoke the honest interest-noted
line, offered two further jobs, the caller declined — and it then called `get_services` and made the
offer before closing. On the two previous runs of that exact scenario it went straight to Goodbye.

### Attempted and REVERTED — required tool parameters for the location turns

`get_recommended_jobs` and `get_jobs` were given `caller_pin_code` and `caller_landmark` as required
parameters (absent from `payload_template`, so never sent to the backend), on the ladder's principle
that a constraint expressible in the tool schema belongs there. **It failed on the first live call and
failed worse than the bug.** On `6ae79885` the model called `get_recommended_jobs` with
`caller_pin_code: "110045"` — lifted from the injected `${location}` string — and
`caller_landmark: "not-known"`, **then asked the location and pin questions afterwards**. The tool ran
before the turns it was meant to gate, the landmark was still never asked, and the skip now carried a
parameter asserting it had been asked. That is the D91 failure mode: a required parameter constrains
what the model says, not what it did. Both parameters were removed, the tools restored, and the
prompt paragraph describing them deleted, the same night.

- **Files:** `KKB-Slim/KKB Slim Hindi Signals.md`, `raya/toolspecs/get_recommended_jobs.json` and
  `get_jobs.json` (changed then restored), `.claude/skills/prompt-analyser/reference/bug-patterns.md`
  (D95 records the attempt and why not to repeat it; D96 records the checklist pattern).
- **Scope:** KKB Slim **Hindi only**, as instructed. The Kannada slim twin still runs the older
  `${recommendations}` design with its older toolset, is internally consistent, and was not touched.

### `call_direction` — the variable is found and working; read it from the call record, not the output prompt

`${call_direction}` is the variable you were thinking of, and it is alive and correct: the CALL
CONTEXT block carries `inbound` on genuine inbound legs (`72692e1a`, `28704be3`, `2027e477`) and
`outbound` on every dialled call.

Capturing it as an output metric did **not** work and was backed out. Added as field 26 of the output
prompt, it produced **`"outbound"` on `2027e477`, a call that was genuinely inbound** — the extractor
does not appear to see the CALL CONTEXT system block, so it fell back to the value in the prompt's own
JSON example. That is the D50 pattern (a demonstration becomes the output), and a metric that can be
silently wrong is worse than no metric. Field removed; the output prompt is byte-identical to what it
was before (18,274 chars, PATCH read-back verified).

**Direction is exactly derivable from the call record instead, with no model involved:**

| | `in_did` | `out_did` | `caller_no` | `to_number` |
|---|---|---|---|---|
| **inbound** | set | null | set | null |
| **outbound** | null | set | null | set |

Confirmed on `2027e477` (inbound) against `4817a3fd` and `511171cf` (outbound). Any reporting layer
should read it from there.

**One real consequence for the repo:** the slim agent's live `output_instructions` had already drifted
ahead of the shared `KKB/KKB Output.md` (18,274 vs 15,068) because tonight's new metrics —
`jobs_interest`, `jobs_fetched`, `services_pitched`, `service_offered`, `service_need_matched` and the
rest — were added on the agent and never filed. Overwriting the shared file would have pushed
slim-only fields onto the other KKB bots, so the live version was adopted into
**`KKB-Slim/KKB Slim Output.md`** and the path map in `CLAUDE.md` now points there for this agent.

**Reading note for anyone scripting against the API:** the call record field is **`call_output`**.
`output_variables` reads as empty on every call and is not a fallback — a throwaway script of mine
used it tonight and reported "no metrics" on calls that had all 31. Every script and skill in the
repo already uses `call_output` correctly, so nothing here needed changing.

### STILL OPEN

**The landmark turn is skipped on 10 of 16 calls** (pin on 3 of 16), counting only calls that
reached the location block with no landmark already on record. Prose has been sharpened twice and
the tool-schema route is now closed. The reason skipping is free is that **nothing downstream consumes
the answers** — the next step runs regardless. The next attempt should give them a real consumer
rather than add a third guard.

## 2026-09-23 (overnight) — ONE bot for both directions; jobs + services come from APIs, not an injected array

- **Request:** one bot for inbound and outbound; recommend jobs AND services; move off the
  campaign-injected `${recommendations}` onto the recommendations API for both directions; integrate
  a services API; make the conversation less rigid; measure it all as output variables. Location work
  and the DKB provider-initiated change explicitly out of scope.

### The direction variable is a dead end, and the resolution

`${call_direction}` is what the owner remembered. A combined prompt using it was built and **retired
in July 2026** because the platform never injects it on API-triggered calls
(`raya/combined/ABANDONED.md`, open-items #12). **Re-verified today:** no direction hint in the call
context on either an inbound or an outbound agent. So the flow is now **direction-agnostic** — same
audio check, same introduction, same silent fetch, same everything — and the prompt forbids inferring
direction from who spoke first, from `${location}`, or from anything else. **Direction for metrics is
derived from the call record** (`in_did`/`caller_no` = inbound, `to_number`/`out_did` = outbound), and
the output prompt says so, so nobody adds a hallucinated field later. The introduction was rewritten
to be true in both directions: it no longer says "आपको कॉल कर रही हूँ", because on an incoming call we
did not dial.

### Three new tools (specs in `raya/toolspecs/`)

- `get_recommended_jobs(profile_id)` — **signals-search ANCHOR** on the caller's own profile. This is
  the recommendations API. Scores 0.70-0.72 on a real role vs 0.58-0.69 for text search.
- `get_jobs(query)` — signals-search textSearch, for when the caller names what they want.
- `get_services()` — `fetch_local` on `item_domain: service_provider` / `profile_1.0`. **This is the
  services API**: not a parameter change on the jobs call, a different domain. Six live rows, five
  real (TRRAIN Trust, Aastha Skill Development Centre, Yuva Kaushal Vikas Kendra, Model Career Centre
  Ghaziabad, HHH Foundation) + one test record.
- signals-search is deployed on gzb and **accepts the existing Signals `x-api-key`** — no separate
  search key needed. `scripts/raya_tooladd.py` gained `path_override` so a tool can target another
  service on the same instance while still cloning auth headers (no key in the repo).

### Prompt + metrics

No job array in the inputs; the pre-call count is gone (nothing is pre-loaded, so the "no jobs" line
may only be said AFTER a tool returns nothing usable); step 6 split into 6a-fetch / 6b-present with a
junk filter and a relevance check; Case B no longer names a trade before a tool has returned one; a
**jobs-interest gate** at the introduction sends a "no" straight to services; a new **section S**
fetches, matches need→service, and offers ONE by name with its cost. Ten metrics added:
`jobs_interest`, `jobs_fetched`, `jobs_offered_count`, `job_roles_offered`, `job_no_match`,
`asked_job_location`, `services_pitched`, `service_interest`, `service_offered`,
`service_need_matched`.

### VERIFIED on live calls

| path | call | evidence |
|---|---|---|
| **INBOUND, full end-to-end** | **`28704be3`** (228s, genuine inbound leg) | identical flow; terms → `create_profile` → `get_jobs` → **apply succeeded** → `get_services` → **named TRRAIN Trust**. Metrics: `jobs_fetched: Search`, `applied_to_job: Yes`, `services_pitched: Yes`, `service_offered: "TRRAIN Trust"`, `service_need_matched: Placement` |
| Outbound, personalised recs + apply | `edd3d6f6`, `e0333123` | `get_recommended_jobs`; role + company, **no city**, junk dropped; **apply succeeded** |
| Outbound, new caller, no profile | `6dc1a058` | Case B asked openly; `get_jobs("data entry operator")`; **apply succeeded**; `consent_status: Given` |
| Outbound, profile role = `Any` | `2b529ea1` | correctly used `get_jobs`, **not** the anchor |
| Outbound, not looking for work → services | `9b43850e` | no job tool at all; `get_services`; named **Aastha Skill Development Centre** with its real cost; refused to invent a contact number |

### Defects found and fixed during the run

1. **Services offer failed twice in the apply-success turn** — first a generic pitch with no tool call
   and nobody named (`edd3d6f6`, `service_offered: NA`), then, after tightening, no offer at all
   (`e0333123`, `services_pitched: No`). Two failures of the same *placement*, so the offer was moved
   out of that crowded turn into step 13 with `get_services` as the step's first action. **Verified
   working on `28704be3`.**
2. **The placeholder role was spoken aloud** — `2b529ea1` said "कमल जी, आप अभी 'Any' का काम देख रहे
   हैं". The rule existed but sat away from where the sentence is composed; the check now happens at
   the point of speaking. **Verified on `511171cf`** — three roles read out ("डेटा एंट्री",
   "कंप्यूटर ऑपरेटर या डेटा एंट्री", "डेटा एंट्री ऑपरेटर"), no placeholder token spoken.
3. **Absent fields were announced** — "सैलरी की जानकारी उपलब्ध नहीं है". With 90% of rows carrying no
   salary this would be most of what callers hear; omission now explicitly means silence. **Verified
   on `511171cf` and `45490ef6`** — the third job (Inthing Creations) carries no salary and the bot
   read role + company only, in silence about the rest.
4. **The service name was read in Latin script** ("TRRAIN Trust" pronounced as English). **Verified
   fixed on `511171cf`** — spoken as "ट्रेन ट्रस्ट"; the English string survives only in the
   `service_offered` output variable, which is correct.

### Closed on the final sweep

- **The closing services offer on an OUTBOUND call — VERIFIED on `45490ef6`** (186s) and again on
  `511171cf` (200s): step 13 calls `get_services` and names ट्रेन ट्रस्ट, `service_offered:
  "TRRAIN Trust"`. The earlier outbound miss (`c883aa34`) was not the offer failing — that fixture
  had already applied to the job, so `apply_job` returned 422 and the call ended on the failure
  branch.
- **Asks-where-the-job-is — VERIFIED on `511171cf`.** The caller asked twice ("यह जॉब कहाँ पर है?",
  then "कौन से एरिया में है?"). Both times the bot said it does not hold the exact location and
  that the employer will make contact. **It invented no city** — which is the whole point, because
  99.9% of live rows carry a masked `jobProviderLocation` (`G***`, `R***`).

### NOT verified

- **No-match (caller wants teaching work)** — still unbridged after 4 attempts.

### On the ~24s "no audio" drops

Six of eighteen calls ended at 24–25s. The bot leg is healthy on every one of them (it greets, then
logs `*No audio/User is speaking softly*` twice and hangs up politely); the **tester** leg shows the
bot's audio arriving and **zero assistant turns** — the tester agent hears and does not speak. I
first blamed the harness, then the persona files. Both were wrong: `hi-asks-where-job-is` failed at
21:33 and the **same file, unchanged**, produced the clean 200s `511171cf` at 21:35. It is an
intermittent tester-side fault, and the only reliable handling is to re-dial.

### Test-harness changes

`scripts/raya_testrun.py`: line-buffered output; a preflight that refuses to dial a DID not bound to
the tester; and — after that guard blocked the first inbound attempt — a reverse-direction mode for
when the tester is the CALLER. The Testing Agent was given `out_did: 911204404272` (it had none, so
Raya 500'd on any call it tried to originate); this is our own test agent and reverse tests are
impossible without it.

**DID note:** `in_did` cannot simply be assigned — a number only used as a caller-ID elsewhere
(`917946350283`) is not provisioned for inbound, so the call completed in 3s and the bot never
received a leg. The inbound proof therefore borrowed **911204404274** from KKB Hindi Inbound Signals
for ~4 minutes; prior state was saved to `inbound_swap_state.json` and **restored immediately after**
(verified: KKB Hindi Inbound Signals has its number back).

**Files:** `KKB-Slim/KKB Slim Hindi Signals.md`, `raya/toolspecs/get_recommended_jobs.json`,
`raya/toolspecs/get_jobs.json`, `raya/toolspecs/get_services.json`, `scripts/raya_tooladd.py`,
`scripts/raya_testrun.py`, `raya/personas/hi-no-jobs-wants-training.md`,
`raya/personas/hi-wants-teacher-job.md`, `raya/personas/hi-asks-where-job-is.md`,
`raya/overnight/ESCALATION-data-team.md`

## 2026-09-10 — verification ledger for the day's slim work (16 live calls)

Per-scenario, per-variant, with the call that proves it. Tester leg ids; both bots dialled the tester
DID `917946350285`, backend state asserted on the API after each consent call.

| # | scenario | bot | call | result |
|---|---|---|---|---|
| 1 | flags all true → NO consent line, normal opening | Hindi | `00b805ce` | PASS |
| 2 | flags false → gate → agree → `record_consent` → normal flow; ONE profile, live+consented | Hindi | `f796df13` | PASS |
| 3 | consent DECLINED → exact decline line, **no tools**, call ends (65s) | Hindi | `f7207437` | PASS |
| 4 | new caller (empty fetch) → pool overview → jobs → create-consent → apply | Hindi | `b91340a8` | PASS (was the `fd01b717` bug) |
| 5 | multi-place `${location}` → every place word spoken | Hindi | `9c9f7e34`, `b7001381` | PASS |
| 6 | pin turn confirms the held pin, digit-by-digit | Hindi | `9c9f7e34`, `b7001381` | PASS |
| 7 | landmark turn last, and genuinely last | Hindi | `9c9f7e34` | PASS |
| 8 | pin refused ("पता नहीं") → accepted in a clause, no loop | Hindi | `a0dd528e` | PASS |
| 9 | Kannada happy path: Maya intro, dharwad fetch, 3 location turns, ranked jobs, salary in words | Kannada | `d7012890`, `63a2d145` | PASS |
| 10 | Kannada flags false → gate in Kannada → live+consented, ONE item | Kannada | `5e3d8c69` | PASS |
| 11 | Kannada consent DECLINED → decline line, no tools, 39s | Kannada | `8ce1d71e` | PASS |
| 12 | Kannada new caller (empty fetch on dharwad) → pool overview, no close | Kannada | `daa1a8bb` | PASS |
| 13 | pin read as SIX digit-words (both zeros) | Kannada | `36e314df`, `d3562f78` | PASS (was `5e3d8c69`) |
| 14 | `${location}` keeps both place words in Kannada | Kannada | `49f64839` | PASS (was `6ff40ebb`) |
| 15 | role-change line makes no fake storage claim | Kannada | `63a2d145`, `54f365d2` | 2/3 — regressed on `49f64839` |
| 15a | …re-mechanised as "tool is mandatory" | Kannada | `bec28724` | FAIL — killed the false claim but narrated the tool AND spoke the `*( )*` stage direction |
| 15b | …re-mechanised again as a CLOSED spoken template | Kannada | `c75ec7a9`, S17 | **DEPLOYED, NOT VERIFIED** — 0 violations on both, but the role-change branch never triggered: an earlier test's `update_profile` persisted "Data Entry Operator" onto the tester DID, so the persona now agrees with the stored role. Needs a tester DID whose stored role differs from the persona's. |
| 16 | static suite (all 22 fleet prompts) | both | — | 0 critical, 0 major, 1 pre-existing minor |

**Bugs found and fixed today, each with the call that showed it:**
1. the pin was never asked at all — added as location Turn B (UAT report, `280e9d0b`)
2. the pin turn was unreachable behind the landmark line's "आखिरी सवाल" promise — reordered (`d47db4c0`)
3. an "anywhere is fine" answer cancelled the pin as well as the landmark — scoped (`b42779bf`)
4. `create_profile` on an unconsented EXISTING caller minted a second live profile — switched to
   `record_consent`, which turns the draft live in place (`e0e7bbc2`)
5. **a genuinely new caller was told "no jobs" and the call was closed** — the no-jobs line is now
   scoped to the job array and cannot be reached from an empty fetch (`fd01b717`)
6. the Kannada role-change turn claimed "ನೋಟ್ ಮಾಡ್ಕೊಂಡೆ" with no tool call (`d7012890`, `49f64839`)
7. the Kannada pin was read back with five digit-words for a six-digit pin (`5e3d8c69`)
8. `${location}` was collapsed to its locality because the canonical-spellings rule printed that very
   pair as an example to shorten (`6ff40ebb`)

**Found, NOT fixed (out of scope, reported):** the production **Kannada** prompt
(`KKB/KKB Placeholder Kannada Signals.md`, line ~754) has "ಪ್ರೊಫೈಲ್" inside its create-consent line —
the one word the caller must never hear, and a law-3 breach in a MANDATED line. The slim Kannada twin
was authored without it. The fat Hindi twin had the same bug and it was fixed there on 2026-09-09.

**Still blocked (data team, `raya/overnight/ESCALATION-data-team.md` §5):** no successful `apply_job`
on either instance — fixture job ids are dead and a self-minted `job_posting_1.0` will not go live
(`PROFILE_NOT_LIVE` on the target). So the post-apply questions, the profile write-backs and the
closing read-back have never executed in a test, on any bot.

## 2026-09-10 — Kannada slim twin created (`kkb-kn-signals-slim`)
- **Ask:** "create a slim version of KKB Kannada as well. test everything thoroughly."
- **Prompt:** `KKB-Slim/KKB Slim Kannada Signals.md`, 121KB, authored from the Hindi slim master.
  Every English instruction is byte-identical; only spoken content was re-authored in Kannada, taking
  the proven wording from the live `KKB/KKB Placeholder Kannada Signals.md` where an equivalent line
  existed and authoring the new ones (the consent flag gate, the pin turn) natively. Built with an
  explicit fragment map and a **zero-Devanagari assertion**, so a missed line fails the build rather
  than shipping half-translated. Kannada machinery re-derived, not translated: Kanglish word list,
  Kannada-script numerals as words, Kannada number/ordinal normalisation, Karnataka canonical place
  spellings (ಹುಬ್ಬಳ್ಳಿ / ಧಾರವಾಡ / ಬೆಂಗಳೂರು / ಕೇಶ್ವಾಪುರ …) plus the Ghaziabad-payload list, prohibited
  phrases, style markers and the pin digit-words (`580023` → "ಐದು, ಎಂಟು, ಸೊನ್ನೆ, ಸೊನ್ನೆ, ಎರಡು, ಮೂರು").
- **Persona:** the bot names itself **ಮಾಯಾ**, matching its production Kannada twin — the registered
  divergence `kkb-kn-signals-maya-name`, extended to this target. A slim A/B twin that used a
  different persona name would not be comparable to the bot it is measured against.
- **Deliberate divergence registered:** `kkb-slim-location-pin-capture` — both slim twins declare
  `${location}` and carry the three-turn location step, which the production Kannada bot does not.
- **Agent:** created on Raya via the new `scripts/raya_clone_agent.py` (settings cloned from the Hindi
  slim — timings, nudges, interruption thresholds, out_did; language machinery cloned from
  `kkb-kn-signals` — language_id, voice_id, tools, memory/output prompts). It therefore reads
  **dharwad-signals** with `languageSpoken: ["Kannada"]`, verified. `record_consent` added as its 5th
  tool; `pin_code` added to its output prompt.
- **Registered:** `raya/agents.json` (`kkb-kn-signals-slim`), the path map in `CLAUDE.md` (KKB-Slim
  row, Hindi master + Kannada mirror), `raya/regression/fleet.json` (22 bots; KKB-Slim mapped to
  blue-dots in `build_fleet_manifest.py`, which was silently dropping it into "unassigned").
- **VERIFIED on live call `d7012890`** (first dial, Kannada tester persona): Maya intro → silent
  `get_profile` on dharwad → Kannada role check → location "ಕೇಶವಾಪುರ, ಹುಬ್ಬಳ್ಳಿ" (**both** place
  words, pin dropped) → pin confirmed digit-by-digit in Kannada → landmark last → ranked job list
  with ordinals and salary in Kannada words → deep dive → data-sharing line → `apply_job`. Static
  suite: 22 prompts, 0 critical, 0 major.
- **Bug found and fixed on that call:** the role-change turn said "ಸರಿ, ಡೇಟಾ ಎಂಟ್ರಿ ಕೆಲಸದ ಬಗ್ಗೆ ನಾನು
  ನೋಟ್ ಮಾಡ್ಕೊಂಡೆ" (*I've noted it*) and called no tool — a law-4 fake-storage claim. Added the
  point-of-use guard to BOTH twins: say only the quoted line, and the `update_profile` call is the
  record. **VERIFY-PENDING** on the re-dial.
- **Known gap:** `apply_job` 422s `TARGET_ITEM_NOT_FOUND` on the Kannada bot because the fixture job
  ids are gzb-instance ids and this bot reads dharwad. Needs real dharwad inventory ids.
- **Files:** `KKB-Slim/KKB Slim Kannada Signals.md`, `KKB-Slim/KKB Slim Hindi Signals.md`,
  `raya/agents.json`, `CLAUDE.md`, `raya/divergences.json`, `raya/regression/fleet.json`,
  `scripts/raya_clone_agent.py`, `scripts/build_fleet_manifest.py`,
  `raya/personas/kn-loc-pin-plain.md`, `raya/personas/kn-consent-plain.md`,
  `raya/testcases/args/kn-slim-loc-pin.json`, `raya/testcases/args/kn-consent-flags-false.json`

## 2026-09-10 — the pin code is confirmed and captured (location Turn B) + consent rewired to `record_consent`
- **Feedback/bug (UAT, Khushboo):** "Location — pincode is missing, only city name is asked or
  confirmed." Grounded on her call `280e9d0b`: `${location}` was `Muradnagar, Delhi 110098`, the bot
  said "मुराद नगर, दिल्ली" and the pin was never mentioned. The tracker's own location rows (22/35)
  say the intent is to "pass what we have, confirm it, capture simple markers (landmark / PIN /
  locality)" — so a silently dropped pin is the bug, not the design.
- **Change:** the location step is now three turns — **A** confirm the place, **B** the pin code,
  **C** one finer detail (landmark), then the jobs. Turn B confirms a pin we already hold (read
  digit-by-digit in words) or asks for one once when we do not; "don't know" is accepted in a clause
  and never blocks the jobs; it is skipped only when the pin is already settled this call or memory
  carries one. The blanket "a PIN is NEVER spoken" ban is now **scoped** rather than contradicted:
  never inside a place name, spoken digit-by-digit in this one turn. New output variable `pin_code`
  on both twins.
- **Order matters and is now recorded:** the pin turn originally sat AFTER the landmark turn and
  never fired, twice — the landmark line promises "आखिरी सवाल" (last question), and the model kept
  that promise. Reordered so the promise stays true. **VERIFIED on live call `9c9f7e34`**: all three
  turns, in order, pin spoken as "एक, एक, शून्य, शून्य, चार, पाँच".
- **Also fixed:** an "anywhere is fine" answer used to cancel the pin turn as well as the landmark
  turn. It is a statement about where they will WORK; the pin is where they LIVE. It now cancels only
  the landmark (lost the pin on `b42779bf` before this).
- **Consent path rewired to `record_consent` (better than the 2026-09-09 design):** on agreement the
  bot now records consent against the caller's existing seeker item whether `live` or `draft`.
  Grounded on the API: the consent array against a **draft** records the consent AND turns that item
  **live**, so the caller becomes applyable with no second profile. `create_profile` is now reserved
  for a genuinely empty fetch — on `e0e7bbc2` it had minted a SECOND live profile and left the draft
  behind, the duplicate this prompt forbids elsewhere. Create-response reading corrected from
  `items[0]` to "the item whose `lifecycle_status` is live".
- **VERIFIED end-to-end on live call `f796df13`** (fixture `918888888885`, a draft with
  `user_consent {terms:false, privacy:false}`): the gate fired straight after the intro, the caller
  agreed, tools were `get_profile` → **`record_consent`** → `apply_job` with **no** `create_profile`,
  the flow then ran normally (role → location → pin → landmark → jobs → deep dive → interview →
  data-share), and the record ended `live` / consent `true` with exactly ONE seeker item.
- **How the false-flag state was fixturable at all** (owner's suggestion, and it corrected a
  documented platform limit): `contact_phone` in `agent_args` DOES reach the model — `${contact_phone}`
  rendered the fixture value and `get_profile` fired against it while the call was dialled to the
  tester DID. `/voice-test` §6c said otherwise; corrected there as 6c-0. Consent facts learned:
  terms and privacy must be sent **together** (`USER_LEVEL_INCOMPLETE`), consent is **write-once-true**
  (`CONSENT_DECLINED` on any `false`), and every false-flag state is therefore necessarily a `draft` —
  "live profile + false flag" cannot be constructed, which is why the draft arm is the one that matters.
- **Files:** `KKB-Slim/KKB Slim Hindi Signals.md`, `raya/toolspecs/record_consent.json`,
  `.claude/skills/voice-test/SKILL.md`, `.claude/skills/prompt-analyser/reference/bug-patterns.md`
  (D89/D90/D91), `docs/signals-migration-guide.md`, `raya/personas/hi-loc-pin-plain.md`,
  `raya/personas/hi-loc-pin-unknown.md`, `raya/personas/hi-consent-decline.md`

## 2026-09-09 — location drops place words; landmark turn re-scoped off "first call"
- **Feedback/bug (reported):** (1) only the first word of `${location}` is spoken — `Muradnagar, KHB
  colony, 110045` came out as just "मुराद नगर"; (2) the nearby landmark is never asked, nor confirmed
  at the end.
- **(1) CONFIRMED on live call `591e5c28`:** given `Muradnagar, Delhi 110098`, the bot spoke "मुराद
  नगर" and dropped दिल्ली. **Root cause: the conversion examples, not the rule.** Two of the three
  table rows collapsed a two-token value to one word (`Muradnagar, 110045` → मुराद नगर), and the
  instruction read "Locality and city only" — so "keep the first place, drop the rest" was the
  pattern actually demonstrated. **Change:** the rule is now a count — every place word is spoken, in
  order, digits are the ONLY thing removed, count them before speaking and you have dropped one if
  you are about to say fewer. Table gained a `places in → out` column and the two reported shapes
  (`Muradnagar, Delhi 110098` → मुराद नगर, दिल्ली; `Muradnagar, KHB colony, 110045` → मुराद नगर, के एच
  बी कॉलोनी), plus a pointer to Abbreviations for an initialism inside a place name.
  **VERIFIED on 4 live calls** (`2712ae8e`, `b34ee8b8`, `ec4ec0a0`, `bcae62ca`): "मुराद नगर, के एच बी
  कॉलोनी" / "मुराद नगर और के एच बी कॉलोनी" — both places, no digits, KHB as letters.
- **(2) NOT a general break — Turn B is reachable and fires.** **VERIFIED on `ec4ec0a0`** (memory
  disabled for one call, so nothing could be injected): "आखिरी सवाल… कौन सा बस स्टॉप, रेलवे या मेट्रो
  स्टेशन है?" With memory ON it was skipped on 11/11 tester-DID calls — which is what the
  never-ask-twice rule looks like when the platform's stored memory already holds a
  `nearest_landmark` for that DID. Per `/voice-test` §6c, `${contact_memory}` sent in `agent_args`
  does not reach the model, so a "no landmark on record" state **cannot be fixtured** on the tester
  DID; whether a specific reported call was a legitimate skip needs that call's uuid.
- **Changes made anyway, as clarifications (each UNVERIFIED — the state they govern is unfixturable):**
  Turn B is no longer labelled "FIRST call only" — with a profile in front of it that reads as "not
  this call", and almost every caller has a profile; the gate is now purely *do we already hold a
  landmark*. Skipping now needs a positive reason (a landmark you can point at); found none and no
  कहीं-भी answer → the ask is REQUIRED before step 6. A bare "चलेगा" answering Turn A is scoped as
  agreement (LOCKED → Turn B), not as the anywhere-answer that cancels Turn B — it appeared in both
  rows of that table. The step-12 read-back's `[एरिया]` slot is now explicitly the Turn B
  stop/station/landmark when that is what was captured.
- **Not reproduced: the read-back at the end.** Step 12 runs only after a SUCCESSFUL apply, and no
  recent slim call has had one — every `apply_job` 422s on `TARGET_ITEM_NOT_FOUND` because the job
  ids in `raya/testcases/args/sweep/kkb-hi-signals.json` are stale. Needs real inventory ids (or the
  reporter's call uuid) before the read-back can be tested at all.
- **Test-harness finding (not a prompt bug):** a fixture with `contact_memory` empty/absent makes the
  bot wrap ~75% of its spoken turns in literal double quotes. Same prompt, same DID: sweep fixture
  0/13 quoted (`014ed170`), no-memory fixture 14/19 (`ddfd1a8d`). Confounded my first read of this as
  an edit regression — always vary one thing.
- **Owner decision (2026-09-09):** a landmark we already hold is NOT re-asked — the never-ask-twice
  rule stands as written. Read-back therefore scoped to what the caller said in THIS call: an
  already-on-record landmark is neither re-asked nor recited back, because a stored value can be
  stale or another person's and reciting it is a fabricated caller fact. (The tester DID's stored
  memory carries a landmark the caller never gave — see `/voice-test` §6c.)
- **Files:** `KKB-Slim/KKB Slim Hindi Signals.md`, `raya/testcases/args/loc-multiplace.json`,
  `raya/overnight/ESCALATION-data-team.md`

## 2026-09-09 — consent flags drive a re-ask for EXISTING callers (step 3.5) + `record_consent` tool (PARTLY VERIFY-PENDING)
- **Feedback/bug:** terms-of-use / privacy-policy acceptance was only ever captured on the
  new-caller path. `get_profile` returns `user_consent { terms_accepted, privacy_accepted, has_age }`
  and a per-item `profile_consent_accepted`, and the prompt explicitly told the model to IGNORE them
  ("never treat `user_consent: true` as live") — correct for readiness, but it meant a returning
  caller whose flags are `false` (a profile created outside the bot — portal, import, another
  partner) was never asked, and the call proceeded on a consent nobody had given.
- **Change:** new **step 3.5**, read the moment `get_profile` returns and before a word is said. All
  three flags true → nothing is asked and the call is byte-identical to before. Any one false →
  ONE combined plain-Hindi ask as its own turn, in the slot step 4 would have taken (name first,
  then the ask), before any job/location/apply talk. Agree + a `live` profile → silent
  `record_consent`; agree + `draft` only → nothing (step 10's `create_profile` records it). Decline
  → no jobs, no tool, graceful close. Consent given at 3.5 counts for the whole call, so step 9 is
  never asked after it, and step 4 opens on the role check because the name was already said.
  Missing/null/absent counts as NOT given; `has_age` is not a consent and is ignored. Worked call C
  added. Apply consent is unchanged — it has no stored flag (it rides in `apply_job`'s payload as
  `consent.acknowledged`) and is already asked every apply via the data-sharing line.
- **New tool `record_consent`** (5th tool, `raya/toolspecs/record_consent.json`, added with the new
  `scripts/raya_tooladd.py`): same Signals participant endpoint as `update_profile` (POST + an
  `item_id` = merge) plus the `compliance` array `create_profile` uses. Deliberately NOT folded into
  `update_profile`: that template is fixed, so compliance inside it would assert a consent on every
  gender/location write, asked or not.
- **Grounded against the live API (2026-09-09):** an update POST carrying `compliance` returns
  **200** and the `item_state` merge keeps every other field. Consent is **write-once-true** — a
  `compliance` value of `false` is rejected with **400 `CONSENT_DECLINED` "consent cannot be
  declined — omit a key to skip it"**.
- **Verification:**
  - **Flags-all-true path — VERIFIED on live call `00b805ce`** (tester DID, `user_consent` all true,
    `profile_consent_accepted: true`): no consent line spoken, no `record_consent` call, step 4
    opened normally ("विकास जी, आप अभी मशीन ऑपरेटर का काम कर रहे हैं…"), then location → jobs →
    deep dive → interview readiness → data-sharing line → `apply_job`. The apply 422'd on
    `TARGET_ITEM_NOT_FOUND` — a stale `job_id` in `raya/testcases/args/sweep/kkb-hi-signals.json`,
    not this change.
  - **Flags-false path (step 3.5's ask, and `record_consent` itself) — VERIFY-PENDING, NOT
    reproducible from our side.** The API refuses to un-set a consent flag, and a compliance-less
    item is necessarily `draft`, so "live profile + false flag" cannot be constructed by us. Needs a
    data-team-provisioned fixture: a dialable number whose participant has a **live** seeker profile
    with `terms_accepted` / `privacy_accepted` false.
  - **Also blocking on the tester DID:** `create_profile` now returns **409
    `PROFILE_LIMIT_REACHED`** (5/5 seeker profiles), so the whole new-caller path is untestable
    there until a profile is deleted or a second DID is provisioned. Seen live on `bc9e24a6`.
  - `bc9e24a6` (the first dial of this change) also shows the pre-existing intermittent
    missed-fetch: the model spoke the "एक मिनट।" hold without calling `get_profile`, then treated a
    5-profile caller as new and sent a **job_id as `profile_id`**. Pre-existing — the same miss is
    on `4c428090` before this change, and the re-dial `00b805ce` fetched correctly.
- **Files:** `KKB-Slim/KKB Slim Hindi Signals.md`, `raya/toolspecs/record_consent.json`,
  `scripts/raya_tooladd.py`, `.claude/skills/prompt-analyser/reference/bug-patterns.md`,
  `docs/signals-migration-guide.md`

## 2026-09-09 — never-invent guard moved to the point of use (VERIFY-PENDING)
- **Feedback/bug:** with a 1-job `${recommendations}` array the slim bot invented a job board —
  `45e2cb3b` offered 4 jobs on 1 supplied; `a4f378b9` offered "हेल्पर, एबीसी लॉजिस्टिक्स" with an
  invented salary, "2 पोज़िशन" and "क्वालिफिकेशन: 12th पास". 2 of 3 dials. The fat prompt is clean on
  5/5 comparable small-array calls, so this is a regression introduced by the rewrite.
- **Root cause:** guard placement, not wording. Fat states "never invent a job" 17 times, spread so
  the rule sits beside nearly every job-speaking site. The rewrite compressed it to 3 statements,
  all top-of-file or in a flow summary, none at the batch-list or deep-dive template. Two other
  mechanisms were tested and ruled out: memory carry-over (refuted — fabrication persisted with
  `memory_enabled: false`) and illustration/array name overlap (refuted — fat has the same overlap
  and is clean).
- **Change:** added two guards, each inside the block it governs. At the batch-list template — every
  `[role]`/`[company]` is copied from the array, the step-4 generic trades are illustrations of the
  local market and never offerable, and "count the array first, then pick the template whose count
  matches; there is no template for more jobs than you were given". At the deep-dive template — a
  job not in the array has no deep dive, so its salary/`[vacancy]`/`[qualification]` cannot be
  supplied. Count-based so it is answerable from the turn being composed. +991 chars (72,069 ->
  73,060); no other line touched.
- **Files:** `KKB-Slim/KKB Slim Hindi Signals.md`
- **Status:** DEPLOYED to `140d13ca` (sha 48a6108c), **NOT VERIFIED**. Three post-deploy dials on
  the 1-job fixture are in flight; the pre-fix rate was 2/3 fabricating, so three clean calls is
  the minimum bar. Slim must NOT be promoted until this passes.

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
