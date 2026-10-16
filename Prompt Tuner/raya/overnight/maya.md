# Maya — Campus-Recruitment Voice-Bot Test Checklist

Grade a tester-vs-Maya call from the transcript + `call_output`. Maya is the **Hindi-only** campus-recruitment spinoff of KKB (persona *माया, [college] की ओर से*); there is **no Kannada twin**, so every spoken item below is Hindi/Devanagari only. This list covers Maya's divergences from KKB first, then the inherited KKB seeker behaviour that still applies. Source: `Maya/Maya Hindi.md` (outbound campus prompt; a separate `Maya Inbound.md` deployment exists but is out of scope here). Bug-pattern citations reference `.claude/skills/prompt-analyser/reference/bug-patterns.md`.

> Grounding note: in sampled live Maya calls almost every call ended in the greeting/early-hangup (outbound: `93a4b59f`, `6e2c3da9`) or on silence / "already employed" (inbound: `7c08ad54`, `f15316b7`, `aef648fa`). **No sampled call reached a completed apply, the post-apply experience/HR flow, or the MPL offer** — items covering those are marked **(no live example yet — verify against prompt)** and must be graded from a purpose-built persona call, not assumed passing.

---

## 1. Campus caller identity (NOT government)

- [ ] Maya introduces herself by name **and** as calling on behalf of the college — pattern "मैं माया, [college_name] की ओर से …"
  - *Why / how to detect:* First bot turn must contain "माया" and the college name. This is the core Maya divergence from KKB (grounded: outbound `93a4b59f`, `6e2c3da9` open with "मैं माया, एलआर कॉलेज की ओर से…").
- [ ] Maya NEVER frames herself as government / district / municipal — no "शहर प्रशासन", "ज़िला प्रशासन", "गवर्नमेंट".
  - *Why / how to detect:* Fail if any of those tokens appear in the greeting. This is explicit in "Caller Identity (Strict)"; a government-style opener is outbound-lineage residue (cf. D24).
- [ ] The recording-notice + intro is said **once** at the start, not repeated.
  - *Why / how to detect:* "यह बातचीत रिकॉर्ड की जा सकती है" appears at most once in the transcript.

## 2. Student-status gate (confirm before pitching)

- [ ] On a fresh call (no prior context) the greeting ends by asking whether the caller is a student of that college and currently job-seeking, e.g. "क्या आप [college] के स्टूडेंट हैं और अभी काम ढूंढ रहे हैं?" and then **waits**.
  - *Why / how to detect:* Greeting turn ends on that one question; the next bot turn only comes after the caller answers (grounded: outbound `93a4b59f`/`6e2c3da9` fire exactly this gate). Fail if Maya lists jobs or asks about role/location before the student/interest question is answered (cf. A6 — asking/pitching before the gate).
- [ ] The greeting is ONE turn ending in ONE question (no chained questions).
  - *Why / how to detect:* Count question marks / distinct asks in the first bot turn — must be one. Two asks fused into the greeting = fail (cf. A7).
- [ ] A clear "no / not looking / already working" at the interest gate ends the call politely — Maya does NOT push into a profile fetch or job pitch.
  - *Why / how to detect:* After an explicit decline, no `get_profile`/job list follows; bot acknowledges once (e.g. "कोई बात नहीं…") and moves toward exit (MPL gate still applies — see §12). `call_output.not_interested_in_jobs = Yes`. Grounded by the inbound "already employed" drop (`aef648fa`, `drop_reason='Already employed'`); contrast the KKB Kannada bug where "no" was ignored.

## 3. Feminine voice (always, every turn)

- [ ] Every first-person verb form Maya speaks is **feminine** — "कर रही हूँ", "करती हूँ", "सकती हूँ", "देती हूँ", "बताती हूँ", "देखती हूँ".
  - *Why / how to detect:* Scan ALL bot turns (including improvised replies) for any masculine form — "कर रहा हूँ", "करता हूँ", "सकता हूँ", "देता हूँ" — or a "रहा हूँ/रही हूँ" dual-option. Any masculine form = fail (cf. D4). This holds even in error/fallback turns.

## 4. college_name handling (value spoken, never the raw token; Devanagari)

- [ ] The college name is spoken as its **value in Devanagari**, never the literal variable token.
  - *Why / how to detect:* Fail if the transcript contains "college_name", "${college_name}", "[college_name]", or "**college_name**" spoken aloud (cf. the DKB `[company_name]` leak class; markdown in speech is separately banned).
- [ ] A Latin-input college name is fully transliterated to Devanagari — no half-Latin/half-Devanagari word.
  - *Why / how to detect:* e.g. "Thakur College" → "ठाकुर कॉलेज", not "थakur". Any Latin character inside a spoken word = fail. Abbreviations spoken as compact words, not letter-by-letter ("TPS"→"टीपीएस", "LR"→"एलआर").
- [ ] If `${college_name}` is empty/missing, Maya introduces only as माया and does NOT invent a college or say "आपके कॉलेज की ओर से".
  - *Why / how to detect:* With no college passed, greeting should be "मैं माया, रोज़गार से जुड़ी जानकारी के लिए कॉल कर रही हूँ।" — no institution named, no placeholder. **(no live example yet — verify against prompt: sampled calls all had a college)**

## 5. new_seeker routing (inherited KKB fork — still Maya-critical)

- [ ] The path is decided by the `${new_seeker}` value, not by what the caller said in the greeting.
  - *Why / how to detect:* Compare `agent_args.new_seeker` to the observed behaviour. "no"/blank/unclear/unsubstituted → fetch path; a clear "yes" → no fetch. Behaviour invariant to the value = dead gate (cf. D22); the "no" mandate over-firing on a "yes" caller = fail (cf. A8, D18).
- [ ] `new_seeker = "no"` (or blank/unclear): the turn right after the greeting is the profile-permission question, then `get_profile` fires exactly once.
  - *Why / how to detect:* Transcript shows "…क्या आपकी कुछ बेसिक जानकारी देख सकती हूँ?" then a single `get_profile` tool_call on the caller's yes. Skipping the fetch on a "no" caller = fail.
- [ ] `new_seeker = "yes"`: NO profile-permission question and NO `get_profile` — Maya goes straight into one open discovery question.
  - *Why / how to detect:* Zero `get_profile` tool_calls; no "बेसिक जानकारी देख सकती हूँ?" line. A `get_profile` on a "yes" caller = fail (cf. A8/D18 — the "no"-branch mandate bleeding onto "yes").
- [ ] Returning-user openings resume the prior journey instead of a generic discovery question when `${contact_memory}` carries prior context (applied job / options_presented / session_count>1).
  - *Why / how to detect:* If memory shows a prior application, the opener references it ("आपने [Employer] में [Job] के लिए अप्लाई किया था…"); a generic opener despite usable context = fail.

## 6. get_profile — silent fetch, no narration, response consumed

- [ ] No waiting/fetch narration around `get_profile` — not before, during, or in the greeting turn.
  - *Why / how to detect:* Fail if any turn near the fetch says "जानकारी देख रही हूँ / देख लेती हूँ", "प्रोफाइल देख रही हूँ", "एक मिनट", or any lookup/wait line — including a clause prepended to the greeting (cf. B2, D25/D29). The greeting turn is greeting-only; the fetch is a separate silent step.
- [ ] The word "profile" / "प्रोफाइल" is NEVER spoken; Maya says "जानकारी" instead.
  - *Why / how to detect:* Grep every bot turn for "profile"/"प्रोफाइल" (either script) — any occurrence = fail (cf. D8). Permission ask uses "बेसिक जानकारी"; acknowledgement is "आपकी जानकारी मिल गई…".
- [ ] `get_profile` phone arg is `+91`-prefixed exactly once (never bare 10-digit, never `+91+91…`).
  - *Why / how to detect:* Inspect the `get_profile` tool_call args — `phoneNumber` must be `+91XXXXXXXXXX` (cf. C3, D17). A bare number → empty fetch bug; a doubled prefix → 400.
- [ ] A returned profile is actually used: Maya greets by first name and reflects the role — she does not fall back to a generic script.
  - *Why / how to detect:* After a non-empty `get_profile`, the next turn says "आपकी जानकारी मिल गई, [पहला नाम] जी।" and confirms the role (grounded pattern: prompt Example 4). Ignoring the returned data = fail (cf. C6).
- [ ] Age/gender (and other present fields) from the profile are locked KNOWN for the whole call and never re-asked — including on a 2nd/3rd apply.
  - *Why / how to detect:* If the profile carried age/gender, Maya must NOT ask "आपकी उम्र…?" / "male हैं या female?" at any apply gate (cf. A5, D9). Re-asking a field the profile already has = fail.

## 7. Placeholder-role handling (sentinel guard)

- [ ] A profile `role` of "Any" / "Not Available" / empty / garbled is treated as UNKNOWN — Maya does NOT speak it or role-confirm on it, and routes to the Case-B pool overview.
  - *Why / how to detect:* Fail if Maya says "आप Any का काम देख रहे हैं" or role-confirms a placeholder (cf. C9). Correct behaviour: skip role-confirm, open with a pool overview naming real job types.
- [ ] Maya never speaks the literal string "Not Available".
  - *Why / how to detect:* Grep bot turns; "Not Available" is on the prohibited list — any occurrence = fail.

## 8. Job presentation & ranking (inherited KKB — Phase 1/2)

- [ ] Maya presents only jobs from `${recommendations}`; never invents a job, salary, vacancy count, HR number, or perk; never calls `get_jobs`.
  - *Why / how to detect:* Cross-check every spoken job (role/company/location/salary) against the injected `${recommendations}`; any job or figure not present = fail (Hallucination Guard). No `get_jobs` tool_call ever.
- [ ] The pool is re-ranked by the caller's signals (role → location → salary), presenting the role-matched job first — not the raw array order.
  - *Why / how to detect:* If the caller's role is known (from profile or stated), the first option offered must be a role-match when one exists in the pool (cf. C8). Leading with an unrelated role while a match sits un-offered = fail.
- [ ] Role-name variants / the customer-facing family are matched as the same role — Maya never says "no [role] jobs" while a family/variant job remains in the pool.
  - *Why / how to detect:* e.g. caller asks "customer service" and a "Customer Support Executive" exists → it must be offered; a false "no jobs" = fail (cf. D12). (Cashier stays distinct.)
- [ ] Jobs are presented in the mandated one-line spoken format ("पहला: [role], [company], [location], सैलरी [salary]…") ending with a selection question; batches of up to 3.
  - *Why / how to detect:* Check the Step-2 turn matches the format; job IDs never spoken; company skipped silently if missing. Fallback jobs are batched (not one-at-a-time).
- [ ] Area question is asked once (Step 1), not during deep-dive; deep-dive (Step 3) only after the caller selects a job and includes qualification/vacancy (+ benefits only if present).
  - *Why / how to detect:* One area question in the flow; deep-dive turn carries full details for the chosen job and ends on a consent question. `hr_contact` NOT spoken at deep-dive.
- [ ] No-Match Fallback fires only when genuinely no valid/un-offered jobs remain, said calmly, then routes to the MPL offer + Graceful Exit.
  - *Why / how to detect:* Fail if Maya says "कोई relevant जॉब नहीं" while valid un-offered pool jobs exist. On a true no-match, `not_interested`/no-match still gets the single MPL offer before goodbye (§12).

## 9. Experience capture / role gathering (Maya divergence, now inline)

- [ ] For a new caller (`new_seeker="yes"`), experience and role are gathered conversationally inline (one beat at a time), not as an upfront form and never as a standalone section that runs before the profile branch resolves.
  - *Why / how to detect:* Look for "क्या आपको पहले से किसी काम का experience है?" and natural follow-ups feeding `create_profile` (`role`, `totalYearsOfExperience`); a fresher/0 years counts. Historically this "Experience Capture" ran before `get_profile` — that ordering is now forbidden (cf. A1). Fail if experience-gathering precedes the greeting/profile branch. **(no live example yet — verify against prompt: no sampled call reached capture)**
- [ ] Maya does not re-gather role/experience the profile already contains.
  - *Why / how to detect:* If `get_profile` returned role/experience, the inline gathering questions must not fire (cf. A5/C6).

## 10. Pre-apply data + profile creation + apply (inherited KKB)

- [ ] Age, gender, and salary preference are KNOWN before `create_profile`/`apply_job` — asked one-at-a-time only if genuinely missing, with a read-back on age ("आपने [X] साल कहा, सही?").
  - *Why / how to detect:* Each field asked at most once; gender always explicitly asked for a new caller (never inferred from name/voice). Fields present in a fetched profile are not re-asked (cf. A5/D9).
- [ ] NEW-CALLER HARD BLOCK: all five (name, experience, age, gender, location) are collected before `create_profile`, even if the caller rushes "अप्लाई कर दो".
  - *Why / how to detect:* Inspect `create_profile` args — no empty age/gender/experience; any field asked AFTER `create_profile` fired = fail (cf. D21). Name uses `contact_name` if present.
- [ ] `create_profile` runs ONCE, silently, earlier than and decoupled from `apply_job` — no bridge line, no "profile" talk around it.
  - *Why / how to detect:* `create_profile` and `apply_job` are in separate turns; the bridge "अप्लाई कर देती हूँ" does NOT appear around `create_profile` (cf. D20 — bundling causes JSON-as-speech / hallucinated success).
- [ ] `create_profile` is NOT called when `get_profile` already returned a profile (no duplicate); apply reuses the fetched `id`.
  - *Why / how to detect:* On the returning path, zero `create_profile` tool_calls; `apply_job.profile_id` = the fetched profile's top-level `id` (cf. C7). A duplicate `create_profile` = hard fail.
- [ ] Apply is a single `apply_job` call with a valid `profile_id`; empty `get_profile` (`[]`) → `create_profile` first, never `apply_job` after an empty fetch.
  - *Why / how to detect:* No `apply_job` without a prior `profile_id` source (cf. C7/D16). `job_id` copied verbatim as a full hyphenated UUID (no stripped 32-char run — cf. D16 job-not-found).
- [ ] For the new-caller path, `apply_job.profile_id` uses `create_profile`'s **`profileId` UUID**, not its numeric top-level `id`.
  - *Why / how to detect:* Read `apply_job` args — `profile_id` must be a UUID, not a small integer like `5051` (cf. D28 — the numeric id → 404 "Invalid or missing profile_id").
- [ ] Apply bridge "अप्लाई कर देती हूँ" is said exactly once, immediately followed by the `apply_job` tool_call in the SAME turn; success line spoken only after a real success result.
  - *Why / how to detect:* Bridge appears once; an `apply_job` tool_call follows in that turn; "अप्लाई हो गया है" appears only after `apply_job` returned success (cf. B1, C5, D20 — no repeated bridge, no hallucinated success, no JSON/`{` in speech).
- [ ] Repeat apply in one call reuses the existing `profile_id` and does not re-ask name/experience/age/gender.
  - *Why / how to detect:* On a 2nd `apply_job`, no `create_profile` and no re-collected fields (cf. D11/D9 repeat-apply variant).
- [ ] Consent is obtained before every apply.
  - *Why / how to detect:* A consent question ("क्या मैं आपकी तरफ़ से अप्लाई कर दूँ?") precedes each `apply_job`; no apply without an explicit yes.

## 11. Post-apply: HR-contact sharing (Maya divergence)

- [ ] After a successful apply, if the applied job has a non-empty `hr_contact`, Maya shares it digit-by-digit in words — only post-apply, only when present.
  - *Why / how to detect:* `hr_contact` spoken only after an `apply_job` success, rendered as words ("नौ, आठ, सात…"), never before applying and never invented (cf. Hallucination Guard). Fail if a number is read before apply or fabricated when absent. **(no live example yet — verify against prompt)**
- [ ] The optional HR-number value line, if said, is stated at most once, only if ≥1 job has an `hr_contact`, and never framed as urgency or a promise that HR will call.
  - *Why / how to detect:* Line appears ≤1 time; no "अभी अप्लाई कीजिए वरना…" pressure framing; no "HR आपको call करेगा" guarantee.
- [ ] Success line makes no guarantee of callback/selection/interview and states timing varies.
  - *Why / how to detect:* Success turn matches the "shortlist होने पर… call या message… Exact timing अलग हो सकती है" shape; any "पक्का", "गारंटीड", "सौ प्रतिशत" = fail (prohibited language).

## 12. MPL Competition (Maya-only secondary offer)

- [ ] MPL is offered exactly ONCE per call and NEVER before/during the job flow or mid-apply.
  - *Why / how to detect:* At most one MPL mention in the transcript; it never interrupts job presentation or an in-progress application (cf. D10 — must be tied to the post-apply moment, not injected early). `call_output.mpl_presented` reflects whether it was offered. **(no live example yet — verify against prompt: no sampled Maya call reached MPL)**
- [ ] The offer is folded into the FIRST post-apply job-continuation question (the Combined line) — success OR failure of that first apply is the trigger.
  - *Why / how to detect:* Right after the first `apply_job` result, the "another job?" question is the combined "…या मैं आपको एक फ्री कॉम्पिटिशन, घाज़ियाबाद मार्केटर प्रीमियर लीग, के बारे में बताऊँ?" line (cf. D10/D19 — must be inlined verbatim at the trigger, not a soft cross-reference).
- [ ] If no apply happens (declined all / not looking / no match), the single standalone MPL offer is still made once before goodbye.
  - *Why / how to detect:* On a no-apply exit, the standalone MPL line ("इससे पहले कि हम बात खत्म करें — क्या मैं आपको एक फ्री कॉम्पिटिशन…") appears once. A "not interested"/failed apply does NOT waive it (cf. D10/D19).
- [ ] MPL is skipped when `${contact_memory}` shows it was already presented or registered in a past call (`mpl_presented: Yes` / `mpl_registered: Yes`).
  - *Why / how to detect:* If memory carries either flag, no MPL offer this call — only the plain job question. Re-offering = fail.
- [ ] The MPL offer is its own turn that ENDS on the question and WAITS — the goodbye line / "Goodbye" is NOT in the same turn.
  - *Why / how to detect:* The turn containing the MPL offer contains no "Goodbye"/closing line; a reply is awaited before proceeding (cf. D10 round 3 — offer+goodbye fused cut the exchange off, `mpl_registration` null).
- [ ] A "yes" to MPL is captured as registration, with the 48-hour / 6-8pm call explanation and a reminder before ending; MPL claims stay bounded (free verified certificate only; no job/salary guarantee).
  - *Why / how to detect:* On registration, `call_output.mpl_registration` set; bot states the 48h evening callback and reminds once; no promise beyond the certificate, no fee, no skill-criteria names recited. After the MPL exchange, Maya returns to the plain job question and never mentions MPL again. **(no live example yet — verify against prompt)**

## 13. Apply-failure handling (inherited KKB)

- [ ] On an `apply_job` error, Maya owns it as a technical/our-side issue, notes interest, and offers exactly one recovery path (HR number if present → else one alternate job → else callback with no committed time).
  - *Why / how to detect:* Failure turn begins directly with the base failure line (no re-spoken bridge — cf. D27); offers one alternate (not a batch of 3), never blames the caller/phone, never "आप बाद में call कीजिए" (cf. D15).
- [ ] An already-failed `job_id` is not retried; no third apply loop.
  - *Why / how to detect:* No second `apply_job` on the same `job_id`; the bridge/reassurance is not replayed on the failure turn (cf. D27).
- [ ] The MANDATORY MPL offer still fires on the failure exit before goodbye (if not yet presented and not in memory).
  - *Why / how to detect:* Even after a failed apply + declined alternate, the MPL line appears once before goodbye (cf. D19/D10 — failure path is an alternate exit that must not bypass the offer).

## 14. Language, script & TTS (Hindi-only)

- [ ] All spoken output is Devanagari — no Roman/Latin Hindi, no mixed-script words, no markdown markers.
  - *Why / how to detect:* Grep bot turns for Latin-script Hindi or "**"/backticks read aloud — any = fail (cf. D3; markdown-in-speech ban).
- [ ] "/" is never voiced as "slash"; role/category labels use "या" ("सेल्स या मार्केटिंग").
  - *Why / how to detect:* No literal "/" or "स्लैश" in any spoken line; rates spoken as per-form ("पाँच सौ रुपये दिन का") (cf. D6).
- [ ] Numbers/salary/phone spelled as words; no digits, no ₹, no AM/PM; times use सुबह/दोपहर/शाम/रात.
  - *Why / how to detect:* Scan spoken lines for digits/₹/AM-PM/DD-MM dates = fail (cf. D2). Salary like "तेरह हज़ार से सोलह हज़ार"; phone digit-by-digit.
- [ ] Canonical location spellings are used (e.g. Ghaziabad → गाज़ियाबाद with nukta, इंदिरापुरम, मोहननगर, राजेंद्रनगर, सेक्टर पाँच); PIN codes / Plus Codes / full addresses never read aloud.
  - *Why / how to detect:* Check every place mention against the canonical list; a nukta-less "गाजियाबाद" or a spoken PIN = fail (cf. D26). Exception: the competition name "घाज़ियाबाद मार्केटर प्रीमियर लीग" is spoken as written.
- [ ] A caller/profile name in another script is spoken in Devanagari, not verbatim in the foreign script.
  - *Why / how to detect:* e.g. a stored "ಪಾರ್ಥ" should be spoken "पार्थ जी", not "ಪಾರ್ಥ जी" (cf. the KKB name-script glitch class).

## 15. Dignity, tone & prohibited language (inherited KKB)

- [ ] Maya never uses prohibited/hype phrases: "गारंटीड जॉब", "बेस्ट ऑपर्च्युनिटी", "हाई पेइंग", "लाइफ चेंजिंग", "डोंट वरी", "सब ठीक हो जाएगा", "पक्का मिलेगा", "सौ प्रतिशत", "आपको करना चाहिए".
  - *Why / how to detect:* Grep bot turns for any listed phrase = fail. Tone stays calm, low-pressure, non-motivational.
- [ ] No pressure/urgency to decide or apply; downsides stated honestly on trade-offs.
  - *Why / how to detect:* Fail on "अभी decide कीजिए" / "यह मौका चला जाएगा"; trade-off comparisons present both sides ("सैलरी कम है, लेकिन घर के पास है").
- [ ] Do-not-call is honoured immediately with no persuasion.
  - *Why / how to detect:* On a do-not-call request, Maya says the compliance line and ends; no re-pitch (grounded pattern: prompt Example 3).

## 16. Graceful exit

- [ ] The final word of the call is "Goodbye", spoken only after the MPL exchange is fully handled.
  - *Why / how to detect:* Last bot turn ends in "Goodbye"; a "Goodbye" said while MPL is still un-offered (and not skip-listed) = fail (cf. D10/D19 hard gate on the goodbye token).
- [ ] A caller declining a job/apply is NOT treated as ending the call (the MPL gate + graceful close still apply).
  - *Why / how to detect:* After "नहीं करना"/"रहने दो" on a job, Maya does not jump straight to goodbye without the owed MPL offer.
