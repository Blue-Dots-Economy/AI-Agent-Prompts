# Raya Voice-Agent Test-Scenario Catalog

Grounded reconnaissance of real historical Raya call transcripts (read-only) to seed an
agent-to-agent voice-testing harness. Each scenario below is a **persona + situation a
tester agent must reproduce**, backed by at least one real call I actually read (call-uuid
prefix cited). Priority order inside each family: common happy-paths first, then the
bug-exposing edge cases (highest regression-test value).

## Backend / arg-shape cheat-sheet (persona harness must feed the right shape)

Three distinct KKB backends surfaced — a tester harness must mimic the matching one:

- **KKB "Signals"** (`signals.bluedotseconomy.org`): `get_profile(phone_number:"91XXXXXX0249")`
  — 12-digit, **no `+`**. `apply_job(job_id=<jobUUID>, profile_id=<LIVE profile UUID>,
  acting_as_user_id=<user_id UUID>, hold_message)` — **no** `requirements_snapshot`.
  `create_profile(name, age, role, phone:"XXXXXX0249"(10-digit), gender, location,
  workExperience, hold_message)`. Profile object has a **draft `item_id`** (`2d1510d6…`) AND a
  separate **live `profile_id`** (`300a4a0b…`) + `user_id` (`8e99c637…`); using the wrong one
  is the central bug (see S10/S12).
- **KKB inbound/outbound "up-getjob" (ONEST/Beckn)** (`up-onest-lite-bap.dhiway.net`):
  `get_profile(phoneNumber:"+91XXXXXX2014")` — **`+` and country code**. `apply_job(job_id,
  profile_id, hold_message)`. `create_profile(agentId:"up-getjob", age:int, gender, name,
  phone:"+91…")`. Profiles are UUIDs or numeric ids (e.g. `5126`).
- **DKB** (`up-postjob`): outbound to employers. `agent_args` carry `job_id, company_name,
  contact_name, contact_phone:"+91…", _scheduler_country_code`, and (existing-jobs campaign)
  `city/location/salary/job_role/num_vacancies/qualification`. Tools: `get_talent_insights(role,
  location, hold_message)` and `create_job(app_instance:"up-postjob", eventType:"JOB",
  payload{title, companyName, orgName, jobProviderLocation, salaryMin, salaryMax, positions,
  workexperience}, phoneNumber, sourceService:"ONESTAGENT")`.

`new_seeker` ('Yes'/'No') appears in `agent_args` on scheduled outbound KKB/Maya calls.
Every KKB/Maya call opens with `[user] hello` (the callee/telephony connect token), then the
bot greets.

---

# KKB — Seeker agents (Hindi + Kannada; Signals, inbound, outbound)

## Scenario: Existing seeker applies to a listed job (happy path)
1. **Existing seeker, one-tap apply.**
2. KKB seeker — Signals (Hi + Kn) and up-getjob inbound. Hindi + Kannada.
3. Signals: `to=+91XXXXXX0249`, `get_profile` returns a profile with role="Data Entry
   Operator", live `profile_id 300a4a0b`, `user_id 8e99c637`. Inbound: caller number,
   `get_profile(phoneNumber:"+91…")` returns 1 personal profile.
4. Caller answers "जी / ಹೌದು", confirms they want the same kind of job, says "कहीं भी चलेगा /
   ಎಲ್ಲಾದ್ರೂ ಸರಿ" for location, then "पहले वाले के लिए अप्लाई कर दो / ಫಸ್ಟ್ ಇಂದ ಅಪ್ಲೈ ಮಾಡಿ".
5. Bot greets → `get_profile` → confirms detected role → asks area → lists 3 jobs
   (name/company/city/salary) → confirms + consent line ("अप्लाई करने पर personal details
   शेयर होंगी") → `apply_job` → success → post-apply enrichment questions → end-confirm summary.
   Clean examples: **51c6f63e**, **ce59a84c**, **8c6e69a1** (Hi Signals, all `applied_to_job=Yes`);
   **bedffaf5** (inbound, sales rep, apply OK).
6. Pass: fires exactly one `get_profile`; presents jobs from inventory (no hallucinated jobs);
   asks consent before applying; `apply_job` returns `status:success`; confirms "अप्लाई हो गया"
   only after a success result; does not re-ask questions already answered.

## Scenario: New seeker — no profile, capture then apply
1. **New seeker, full profile capture.**
2. KKB seeker — Signals (Kn) + up-getjob inbound (Hi). Hindi + Kannada.
3. `get_profile` returns `[]` / `{user_id:None, items:[]}` / consent flags all False.
   `new_seeker='Yes'` common in agent_args.
4. Caller: "जी" → names a job type ("डेटा एंट्री / सेल्स") + location, picks a job, then bot
   collects **age → gender → (name)** one at a time with read-backs ("आपने चौबीस साल कहा, सही?").
5. Bot: greet → get_profile(empty) → ask job type + location → list jobs → collect
   name/age/gender → `create_profile` → `apply_job`. Inbound success: **1fde1677**
   (create_profile id 5126 → apply OK). Kannada Signals: **f87fbeca**, **2289c071** (create_profile
   fires; apply then errors — see S10).
6. Pass: does not claim a profile it never fetched; collects each field once with a read-back;
   calls `create_profile` before `apply_job`; phone sent in the backend's required shape
   (10-digit for Signals `create_profile`); no duplicate field questions.

## Scenario: Seeker asks many clarifying questions before/after applying
1. **Inquisitive seeker (process, timing, who calls back).**
2. KKB seeker — up-getjob inbound. Hindi.
3. Existing/new profile; caller stays on the line 5+ min.
4. Caller interrogates: "अप्लाई करने के लिए क्या करना होगा?", "कब तक होगा प्रोसेस?", "डायरेक्ट नंबर
   पे कॉल आएगा?", "इंटरव्यू के लिए कितना टाइम?". Example: **1fde1677** (347s, many follow-ups).
5. Bot answered each without inventing specifics; correctly refused to share the employer's
   direct number ("डायरेक्ट employer का नंबर नहीं दिया जाता"). 
6. Pass: answers only with known facts (shortlist→employer calls, timing varies); never
   fabricates a date/number; never promises a callback channel it can't guarantee; stays on
   task and still lands the apply.

## Scenario: Requested job type / location has no matching inventory
1. **Out-of-area / out-of-category request → bot offers nearest alternative.**
2. KKB seeker — inbound (Hi) + Signals (Kn). Hindi + Kannada.
3. Any profile state.
4. Caller asks for a place/category with no jobs: Modinagar (**5449910e**), part-time
   (**bf587299**), Hubballi-Dharwad (**6d63f47c** — "ಹುಬ್ಬಳಿ-ಧಾರವಾಡಿಂದ ಜಾಬ್ ಬೇಕು", none there).
5. Bot acknowledges no inventory there, proposes nearby/related (Ghaziabad/Noida; or Bengaluru
   for the Kn caller) and asks if that's acceptable before listing. 
6. Pass: never presents a job outside the requested filter as if it matched; states plainly
   that the exact ask isn't available; offers the nearest real option and gets buy-in.

## Scenario: Commute too far / no transport → declines
1. **Distance objection.**
2. KKB seeker — up-getjob inbound. Hindi.
3. Existing profile (BCA graduate).
4. Caller asks distance from "लोहिया नगर" to the job; on hearing ~10–12 km says "मेरे पास कोई
   बाइक नहीं है… थोड़ा कम डिस्टेंस चाहिए" and declines. Example: **cceba987**
   (`drop_reason='Commute distance too far; no personal transport'`).
5. Bot estimated distance, offered a second option, respected the constraint.
6. Pass: gives a plausible distance framing without over-precise fake numbers; offers a
   closer alternative; does not push-apply against an explicit distance refusal.

## Scenario: Declines a job mid-flow, then applies to a different one
1. **Changes mind / switches option.**
2. KKB seeker — Signals (Kn). Kannada.
3. Existing profile.
4. Caller: "ಡೇಟಾ ಎಂಟ್ರಿ ಆಪರೇಟರ್ ಜಾಬ್‌ಗೆ ಅಪ್ಲೈ ಮಾಡಲ್ಲ" (won't apply to data-entry) → bot offers
   remote CSE → "ಹಾ, ಮಾಡಿ". Example: **1db97590**.
5. Bot switched target job, collected the missing age/gender, attempted apply on the new job.
6. Pass: drops the rejected job cleanly; re-targets `apply_job` at the newly chosen job_id (not
   the declined one); doesn't restart the whole flow.

## Scenario: "Not looking" / not interested
1. **Declines the outbound call.**
2. KKB seeker — outbound (Hi + Kn). Both.
3. `new_seeker='No'`.
4. Caller: "नहीं" / "ಇಲ್ಲ" at the opening "क्या आप काम ढूंढ रहे हैं?".
5. **Correct**: Hi outbound **328a7fd0** → "कोई बात नहीं, सोचिए… Goodbye" (`drop_reason='Said not
   looking'`). **BUG to regress-test**: Kn outbound **f4e85575** — caller says "ಇಲ್ಲ" but bot
   ignores it and pushes "ನಿಮ್ಮ ಬೇಸಿಕ್ ಮಾಹಿತಿ ನೋಡಬಹುದಾ?" (should have closed).
6. Pass: a clear "no" at the interest gate ends the call politely; the bot must NOT proceed to
   fetch profile / pitch jobs after an explicit decline.

## Scenario: Silent / no-audio / one-word caller
1. **Low-signal caller (soft speech, monosyllables, immediate hangup).**
2. KKB seeker — inbound (Hi), Maya inbound. Hindi (+ Kn hangups).
3. Any.
4. Repeated `*No audio/User is speaking softly*` or a single "यह"/"क्या" then silence.
   Examples: **d1327a39**, **ecae68a8** (inbound), **7c08ad54**, **f15316b7** (Maya in), plus
   many `dur<15s` "Hung up mid-call" (**1d7ee410**, **6470ad95**).
5. Bot re-prompts gently ("कोई बात नहीं, सोचिए…"), escalates to a menu of job types, eventually
   ends.
6. Pass: bounded number of re-prompts (doesn't loop forever); offers concrete examples to
   unstick the caller; ends gracefully with the right `drop_reason`; never fabricates an answer
   on the caller's behalf.

## Scenario: ASR mishearing of a critical field (gender / age / number)
1. **Homophone / accent confusion loop.**
2. KKB seeker — inbound. Hindi (ASR-driven, reproduce with noisy/accented persona).
3. Any.
4. "female" heard as **"ईमेल"** repeatedly (**5449910e** — 6 back-and-forths before "मैं लड़की
   हूँ"); age "20"→"24" correction (**1fde1677**); "तीन नंबर" vs option (**34f1f587**).
5. Bot re-asks with read-backs, eventually resolves; sometimes wastes many turns.
6. Pass: uses confirm-read-backs ("आपने … कहा, सही?"); recovers the correct value; does not
   write a mis-heard value into `create_profile`/`apply_job`; caps the retry loop.

## Scenario: apply_job backend rejection — Signals (PROFILE_NOT_LIVE / requirements_snapshot / bad id)
1. **Signals apply failure cluster (HIGH regression value).**
2. KKB seeker — Signals. Kannada (mostly) + Hindi.
3. Profile has draft `item_id 2d1510d6` + live `profile_id 300a4a0b` + `user_id 8e99c637`.
4. Caller does a normal apply; the failure is bot-side arg shape.
5. Observed failures (all end with the neutral "apply complete ಆಗಿಲ್ಲ — technical ತೊಂದರೆ" line):
   - `profile_id` = **draft item_id** `2d1510d6` → **422 PROFILE_NOT_LIVE** (**eaa3f2d1**, **663869cd**).
   - `requirements_snapshot` sent as `[]` or `{}` → **400 FST_ERR_VALIDATION body/requirements_snapshot**
     (**d7657df1**, **1db97590**, **2289c071**, **ebb05fd1**, **a3db87a4**, **2f41c499**).
   - `acting_as_user_id` = phone `"91XXXXXX0249"` instead of user_id (**ebb05fd1**).
   - **Fixed path** (regression target = should look like this): `profile_id 300a4a0b`, no
     `requirements_snapshot` → success (**5804fd6b** Kn, and all Hi Signals **51c6f63e/ce59a84c/8c6e69a1**).
6. Pass: `apply_job` sends the **live** `profile_id` (not the draft item_id), the real `user_id`
   as `acting_as_user_id`, and **omits** `requirements_snapshot` entirely; returns
   `status:success`. Grader should assert `apply_job` args by shape, not just the spoken line.

## Scenario: apply_job backend rejection — up-getjob (404 invalid profile_id / job not found)
1. **Inbound apply failure cluster.**
2. KKB seeker — up-getjob inbound. Hindi.
3. Existing or freshly-created profile.
4. Normal apply.
5. Failures: `profile_id="up-getjob"` (the agentId literal, not a real id) → **404 Invalid or
   missing profile_id** (**5449910e**, twice); `job_id` without dashes
   `"eab4805a7d5f4bf2b1a91fd34521550d"` → **404 Job not found** (**8ddcaa5a**); fake UUID
   `profile_id="a8a0e6f0-…-123456789abc"` → 404 (**34f1f587**). Bot then reads out an HR phone
   number digit-by-digit as fallback (**5449910e**).
6. Pass: `profile_id` is the id returned by `get_profile`/`create_profile` (never the agentId,
   never a placeholder UUID); `job_id` is the exact id from the listing; on genuine backend
   failure the bot degrades gracefully without inventing an application success.

## Scenario: Malformed / placeholder tool arguments (literal template strings)
1. **Model emits un-substituted placeholders into tool args.**
2. KKB seeker — Signals (Kn) + inbound (Hi). Both.
3. Any.
4. Normal flow; the defect is purely in the emitted JSON.
5. Real occurrences: `apply_job(profile_id:"items[0].item_id", acting_as_user_id:"user_id")`
   → 400 "body/source_item/item_id Invalid UUID" (**b31fa5c9**); `profile_id:"a8a0e6f0-1a2b-4c3d-
   9e4f-123456789abc"` (**34f1f587**). Related data bug: `create_profile` sending
   `phone:"XXXXXX0249"` that the backend stored as **`9191XXXXXX0249`** (double country code) →
   spawned a duplicate user and a later `update_profile` **403 ITEM_NOT_OWNED_BY_USER**
   (**7935ce5a** Hi Signals).
6. Pass: every tool-arg is a resolved runtime value (real UUIDs/ids), never a template token
   like `items[0].item_id`/`user_id`; phone normalization does not double the country code;
   `update_profile` targets a profile the resolved user actually owns.

## Scenario: Post-apply profile enrichment
1. **Fill missing fields after applying (gender, occupation/study, area/mohalla).**
2. KKB seeker — Signals + inbound. Hindi + Kannada.
3. Live profile missing some fields.
4. After "अप्लाई हो गया", bot asks 1–3 short questions: "male हैं या female?", "काम कर रहे हैं या
   पढ़ाई?", "किस इलाके/मोहल्ले में रहते हैं?"; caller answers ("कोरमंगला", "तुमकुर रोड").
   Examples: **ce59a84c**, **51c6f63e**.
5. Bot `update_profile` per field with read-back, then a final "एक बार confirm कर लूँ — नाम…
   उम्र… काम… एरिया — सब सही?".
6. Pass: enrichment happens only AFTER apply; each field confirmed; `update_profile` succeeds
   (correct profile ownership — contrast the 403 in S12); final recap matches captured values;
   name script/spelling preserved (see note below).

## Scenario: (minor) Name script / TTS mismatch
1. **Devanagari vs Kannada name rendering in the wrong-language call.**
2. KKB seeker — Signals. Hindi call carrying a Kannada-script name.
3. Stored `name:"ಪಾರ್ಥ"` (Kannada script) surfaced inside a Hindi call.
4. Bot sometimes speaks "ಪಾರ್ಥ जी" verbatim (**ce59a84c**, **7935ce5a**) instead of "पार्थ जी".
5. Cosmetic TTS/readback glitch; not fatal.
6. Pass: caller's name is spoken in the call's own script; `update_profile` doesn't overwrite a
   good name with a mis-transliterated one.

---

# DKB — Employer / MSME agent (Hindi + Kannada, outbound)

## Scenario: Employer posts a NEW job (full happy path)
1. **New vacancy capture end-to-end (HIGH value — the DKB golden path).**
2. DKB employer — Kannada (clean full example); Hindi flow identical.
3. `agent_args`: `job_id, company_name:"ANUSHARAN VENTURES LLP", contact_phone:"+91XXXXXX2169",
   _scheduler_country_code:"91"`; campaign `DKB - New Blue Dots`.
4. Employer answers, confirms company, says "ಹಾ ಇದೆ ಹೇಳಿ" (has 2 min), then feeds one vacancy:
   role "ಅಕೌಂಟ್ಸ್", city "ಹುಬ್ಬಳ್ಳಿ", 1 vacancy, salary "ಹತ್ತು"(=10k), address "ಶಿರೂರ್ ಪಾರ್ಕ್
   ವಿದ್ಯಾನಗರ", qual "ಬಿಕಂ", freshers+experienced OK, hours 9–6:30, benefit ESI. Example:
   **cf3fc048** (225s, `new_job_posted:Yes, phases_reached:Phase 3`).
5. Bot: confirm identity → AI/recording disclosure + free-service pitch → ask for vacancy →
   read-back each field → `get_talent_insights(role, location)` → capture salary/positions/
   address/qual/experience/hours/benefits → "post ಮಾಡಲಾ?" → `create_job(app_instance:"up-postjob",
   sourceService:"ONESTAGENT", payload{…})` → `{success:true}` → "ಇನ್ನು ಹೊಸ posting ಇದೆಯಾ?" → close.
6. Pass: confirms company before pitching; one read-back per captured field; `create_job`
   payload matches what the employer actually said (salaryMin/Max, positions, title, location);
   posts only after explicit "post it" consent; closes by inviting future postings.

## Scenario: Wrong number / not that company
1. **Reached someone unaffiliated with the target business.**
2. DKB employer — Hindi.
3. `company_name` in agent_args, e.g. "MANJUSHA NARROW FABS (P) LTD.".
4. Callee: "न रंग नंबर" (wrong number). Example: **e6fdf9e5** (`final_summary`: wrong number).
5. Bot re-asks to confirm identity, then should exit.
6. Pass: does NOT launch the job pitch to a wrong-number party; confirms once, then ends;
   marks status Unverified — never fabricates a verified job.

## Scenario: Voicemail / answering machine picks up
1. **IVR/voicemail, not a human.**
2. DKB employer — Hindi + Kannada.
3. Any DKB agent_args.
4. First "utterance" is a recording: "please record your message… you may hang up" (Hi
   **74bd1610**; Kn **0460001a**).
5. Bot delivered its pitch into the void, got no-audio, ended.
6. Pass: recognizes non-interactive/no-audio and terminates within a couple of turns; does not
   attempt to `create_job`; `call_outcome=Early Disconnect`.

## Scenario: Identity confirmed but bot wrongly offers a callback and hangs up
1. **Premature call-back exit (BUG to regress-test).**
2. DKB employer — Kannada.
3. Standard agent_args.
4. Employer confirms identity and says "ಇವಾಗ್ಲೇ ಹೇಳಿ ಪರವಾಗಿಲ್ಲ" (talk now, it's fine), but the
   bot says "ನಾಳೆ ಕಾಲ್ ಮಾಡಬಹುದಾ?" then "Goodbye". Example: **b362bf46** (`final_summary` flags
   the bug explicitly).
5. Bot mis-routed to the "busy, call later" branch despite a clear "talk now".
6. Pass: when the employer agrees to talk now, the bot proceeds to the vacancy questions; it
   only offers a callback when the employer says they're busy.

## Scenario: Hostile / anti-AI-call employer
1. **Employer distrusts automated calls.**
2. DKB employer — Kannada.
3. Standard.
4. "ಇವ್ರ ಏನು AI ಕಾಲ್ಸ್… ಸುಮ್ಮ್ ಮಾಡ್ತಾರೆ, ಏನು ರಿಸಲ್ಟ್ ಬರಲ್ಲ" (these AI calls do nothing). Example:
   **1283e4a9**.
5. Bot gave its government/free-service framing; call disconnected early.
6. Pass: responds to the objection with the value framing once, stays polite, doesn't argue or
   loop; exits if the employer won't engage.

## Scenario: Unsubstituted `[company_name]` placeholder
1. **Template variable spoken literally (BUG).**
2. DKB employer — Hindi + Kannada.
3. agent_args where company resolution failed (or Maya-style default).
4. Bot opener literally says "क्या आप **[company_name]** से बोल रहे हैं?" (Hi **64da1027**) /
   "ನೀವು [company_name] ನಿಂದ?" (Kn **b362bf46**).
5. Placeholder leaked into speech.
6. Pass: opener always contains a real company name (or a graceful generic "किस कंपनी से बोल रहे
   हैं?" fallback — cf. **1283e4a9** "ಯಾವ ಕಂಪನಿ/ಇಂಡಸ್ಟ್ರಿ?"), never the raw `[company_name]` token.

## Scenario: get_talent_insights returns wrong-geography candidates
1. **Insights data mismatch (data/backend bug to flag, not prompt-fixable).**
2. DKB employer — Kannada (Hubli job).
3. Role="Accounts", location="Hubli".
4. `get_talent_insights` returned candidates in **Ghaziabad/Noida/Modinagar** (UP), 0 for Hubli
   — bot correctly said "ಈ area ನಲ್ಲಿ candidates supply ಕಡಿಮೆ". Example: **cf3fc048**.
5. Bot degraded gracefully but the insight geography was wrong.
6. Pass (harness note): grader should detect insight/location incoherence and route it to
   backend, not to prompt edits; bot should not over-promise candidate supply it doesn't have.

## Scenario: Existing-job re-verification / expiry pitch
1. **"Your posted job expires today" re-engagement.**
2. DKB employer — Hindi (+ Kn). Campaign `DKB - Existing Jobs`.
3. agent_args carry an existing `job_id` + `company_name` (+ city/location/salary for the posting).
4. Bot: confirm company → "आपने हमारे प्लेटफॉर्म पर एक जॉब पोस्ट की थी — वो आज एक्सपायर हो जाएगी…
   दो मिनट बात हो सकती है?". Examples: **893c8441**, **6732681a** (employer confirms then drops).
5. Bot pivots to re-verify/renew the existing job rather than capturing a brand-new one.
6. Pass: uses the expiry framing for existing-jobs campaigns (not the new-vacancy pitch);
   references the actual posted role/company; only re-posts/updates on consent.

---

# Maya — Campus recruitment (Hindi only)

## Scenario: Maya outbound campus intro (student gate)
1. **Campus outbound greeting + interest gate.**
2. Maya — Hindi, outbound. `new_seeker='Yes'`.
3. `to=+91…` scheduled numbers; college identity baked in.
4. Bot: "मैं **माया, एलआर कॉलेज की ओर से**… क्या आप एलआर कॉलेज के स्टूडेंट हैं और अभी काम ढूंढ रहे
   हैं?"; most callees hang up in <20s (`early_hangup`). Examples: **93a4b59f**, **6e2c3da9**.
5. Only the greeting fired before disconnect in the sampled calls.
6. Pass: identifies as Maya + the specific college (not "government"); confirms student status
   before pitching; feminine Hindi verb forms; graceful close on early hangup. (No completed
   apply/Experience-Capture/MPL flow was observed — see Coverage notes.)

## Scenario: Maya inbound seeker (काम-की-बात style)
1. **Inbound student caller.**
2. Maya — Hindi, inbound.
3. Caller phone; `get_profile(phoneNumber:"+91…")` → `[]` for new callers.
4. Opener "माया की रोज़गार सेवा में आपका स्वागत है… किस तरह का काम ढूंढ रहे हैं?"; most callers are
   silent/soft (**7c08ad54**, **f15316b7**) or already-employed ("मैं तो काम कर ही रहा हूँ",
   **aef648fa**, `drop_reason='Already employed'`).
5. Bot re-prompts with job-type menu (customer support / telesales / sales) + location (Ghaziabad/
   Noida), does `get_profile`.
6. Pass: bounded re-prompts on silence; recognizes "already employed" and closes or pivots
   appropriately; keeps feminine voice; menu options match Maya's real inventory geography (UP).

---

## Coverage notes

Agents actually read (all via `scripts/raya_call.py`, most-recent-first):

| Agent (uuid prefix) | Calls pulled | Substantive transcripts | Notes |
|---|---|---|---|
| KKB Hindi Signals `115b38a5` | 5 (all that exist) | 4 | apply mostly **succeeds** (fixed path) |
| KKB Kannada Signals `33037201` | 15 | ~12 | apply mostly **fails** — richest bug source (20 tool-error blocks) |
| KKB Hindi outbound `da612923` | 15 | ~4 | many `dur=0` scheduled shells + early hangups |
| KKB Kannada outbound `87ab9108` | 15 | 2 | mostly `dur=0`; 1 "said no but bot continued" bug |
| KKB Hindi inbound `b6222233` | 15 | ~9 | up-getjob/ONEST backend; clarifying-Q + 404 apply bugs |
| KKB Kannada inbound `4ac90bf1` | **0** | 0 | API returned no calls |
| DKB Hindi `57814ac8` | 20 | ~7 | all early-disconnect / wrong-number / voicemail; no completed post |
| DKB Kannada `d1a1614f` | 12 | ~4 | **1 full completed job-post** (cf3fc048) + callback bug |
| Maya Hindi outbound `47fdffe6` | 10 | 2 | mostly `dur=0` / early_hangup |
| Maya Hindi inbound `df99f501` | 10 | ~4 | silence + "already employed" |

Reader caveat: `scripts/raya_call.py` crashes when a call's `call_output` is a **list** (some
DKB calls). I used a self-contained patched copy in the scratchpad (`rc.py`) to read DKB fully;
worth hardening the repo reader with `co = co if isinstance(co, dict) else {}`.

### Scenarios suspected but NOT found with a real example (Synthetic — no real example found)
- **"Wrong person / not the seeker"** for KKB (someone else answers the seeker's phone). DKB has
  wrong-number (S: e6fdf9e5) but no KKB seeker analogue was seen.
- **Explicit consent refusal** ("नहीं, मेरी डिटेल्स शेयर मत करो") mid-apply — the consent line is
  spoken (ce59a84c) but no caller declined it in the sample.
- **Multi-profile / PROFILE_NOT_LIVE across multiple live profiles** — referenced in the repo
  changelog ("apply to the LIVE profile, not items[0]") and visible as the *mechanism* behind the
  Signals failures, but I did not read a call where a single user had 2+ live profiles to pick between.
- **Maya completed apply + Experience Capture + MPL competition offer** — Maya's distinctive
  post-apply sections; every sampled Maya call ended before reaching them, so no transcript
  evidence. Build these personas from the Maya prompt, not from a call.
- **Seeker withdrawing / asking to delete data**, and **caller speaking a third language** — none seen.
