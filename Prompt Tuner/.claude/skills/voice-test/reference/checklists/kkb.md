# KKB Seeker: bot-specific test checklist

Grade a KKB job-seeker call (काम की बात / ಕೆಲಸದ ಮಾತು) on top of `generic.md`, which already covers the
audio check (§15), the returning-caller line (§16), the closing offer's shared rules (§17), safety (§18),
language and TTS (§8) and silence (§3); those are cited here, not restated. Ids are `kkb.<section>.<n>`.

**Variants** (resolve uuids and files in `raya/agents.json`; grade each one on its own calls):
Signals outbound (`kkb-hi-signals`, `kkb-kn-signals`) and inbound (`kkb-hi-in-signals`,
`kkb-kn-in-signals`) are the reference for this list. Differences are in §13: the legacy up-getjob
prompts (`kkb-hi-out`, `kkb-kn-out`, `kkb-hi-in`, `kkb-kn-in`) and the Slim A/B pair
(`kkb-hi-signals-slim`, `kkb-kn-signals-slim`). The source of truth is the prompt file; where this list
and the current prompt disagree, the prompt wins and this list is fixed.

## 1. Opening (outbound; inbound in §13)

- [ ] `kkb.1.1` Turn 2 (after the audio check) is the one introduction line: the city administration's "काम की बात" initiative, why we are calling, the recording disclosure, and the turn ENDS on "क्या आप अभी काम ढूंढ रहे हैं?" (Kannada mirror equivalent).
  *Why / how to detect:* Fail if the disclosure comes after the question, if the turn ends on a statement, or if it carries the caller's name, a saved role or a lookup line (cf. D29, D32, B2).
- [ ] `kkb.1.2` No "गवर्नमेंट" / "from the government" anywhere in the identity.
  *Why / how to detect:* Grep spoken turns for गवर्नमेंट / ಗವರ್ನಮೆಂಟ್ / government.
- [ ] `kkb.1.3` No tool call in the introduction turn; the introduction is never repeated.
  *Why / how to detect:* `get_profile` emitted in the same turn as the greeting, or the greeting re-spoken after the tool returns, is a fail (the caller hears the introduction twice and never answers it).
- [ ] `kkb.1.4` A clear "no / not looking" ends the call politely with no fetch and no pitch.
  *Why / how to detect:* `drop_reason` "Said not looking"; any `get_profile` or job talk after the decline is a fail (f4e85575).
- [ ] `kkb.1.5` Empty or missing `${recommendations}` gives the missing-job-data line and Goodbye, with no job presented.
  *Why / how to detect:* "अभी आपके लिए मुझे जॉब्स नहीं मिल रहीं — एक बार फिर से देखकर मैं आपको वापस कॉल करती हूँ।" then Goodbye; any spoken job is a fabrication.

## 2. Silent profile fetch

- [ ] `kkb.2.1` `get_profile` fires exactly ONCE, as the first action after the caller answers the introduction question, and never again (not at apply time).
  *Why / how to detect:* Count `get_profile` in `tool_calls`: 0 means memory stood in for the fetch (D32), 2+ breaks the hard scope rule (cf. D7, D25, D29).
- [ ] `kkb.2.2` `phone_number` is `${contact_phone}` as given: 12 digits starting 91, no `+`, never re-prefixed.
  *Why / how to detect:* A bare 10-digit, a `+`, or a 14-digit `9191…` value is a fail (wrong record or empty fetch; cf. D17, D39).
- [ ] `kkb.2.3` The fetch is never announced: no permission ask, no "आपकी जानकारी देख रही हूँ / मिल गई", no "प्रोफाइल" ever; `hold_message` is exactly the neutral "एक मिनट" / "ಒಂದು ನಿಮಿಷ".
  *Why / how to detect:* Spoken turns plus `tool_calls[].function.arguments.hold_message` (cf. B2, D8, D34).
- [ ] `kkb.2.4` The caller's profile is the item with `item_type: profile_1.0` and `item_domain: seeker`, and among those the LIVE one, never blindly `items[0]`.
  *Why / how to detect:* The `profile_id` later used must be that item's `item_id`. A `job_posting_1.0` id sent as `profile_id` (`0d63dc50`, `SOURCE_ITEM_NOT_FOUND`) or a draft chosen while a live item exists is a fail (cf. D37). Readiness comes from the item's `lifecycle_status`, never from participant consent flags.

## 3. Account and terms (Part 1, Signals)

- [ ] `kkb.3.1` Asked only when no seeker profile came back, or one of `user_terms`, `user_privacy` (the top-level `compliance` rows) or the item's `profile_consent_accepted` is false or absent; asked nothing when all three are true.
  *Why / how to detect:* Read the `get_profile` result; asking a fully consented caller, or skipping an unconsented one, is a fail.
- [ ] `kkb.3.2` Its own turn, after the caller answered the greeting, with all five elements, saying "अकाउंट" and never "प्रोफाइल", ending on its one question.
  *Why / how to detect:* Welded onto the greeting turn is the known failure (`722b4131`, `3c3f8740`, `7a059554`, `7b5f6945`); a summarised disclosure is a fail.
- [ ] `kkb.3.3` On agreement: `record_consent` fires once, silently, with the seeker item's `item_id` when an item came back (live or draft); nothing fires when no item came back (consent is written later by `create_profile`). No "आपका अकाउंट बन गया है".
  *Why / how to detect:* `tool_calls`; a `create_profile` used to fix an unconsented existing item mints a second live profile (fail). Assert on the backend afterwards: the item is `live` with all three consents true and there is exactly one seeker item (`ab98be47`).
- [ ] `kkb.3.4` On a refusal the call ends with the decline line and no `record_consent`, `create_profile` or `apply_job`; an unclear answer gets one shorter re-ask, then counts as a refusal; a `record_consent` error ends the call with the "अभी आपका अकाउंट पूरा नहीं हो पाया" line.
  *Why / how to detect:* `tool_calls` after the answer; asked once per call, never again for a second application.

## 4. Returning caller: name and role

- [ ] `kkb.4.1` The name comes from the fetched profile only (first name, in the call's script), never from memory; with no usable name, no name.
  *Why / how to detect:* A name spoken before `get_profile` returned, or one that differs from the profile's, is a fail (cf. C5, D32).
- [ ] `kkb.4.2` One turn: name, the optional callback clause (`generic.md` §16), and the role check framed as the caller's current work ("आप अभी [role] का काम कर रहे हैं — क्या आप अभी भी [role] की जॉब देख रहे हैं?"), ending on that question. No location question and no job list in it.
  *Why / how to detect:* Two questions in this turn is a fail (cf. A6, A7).
- [ ] `kkb.4.3` A sentinel role ("Any", "Not Available", empty, garbled) or a qualification stored as a role ("B.Tech", "12th Pass") is never spoken as the caller's work; the bot opens with the pool overview instead (Case B).
  *Why / how to detect:* "आप Any का काम देख रहे हैं" or "आप अभी B.Tech का काम कर रहे हैं" is a fail (cf. C9).
- [ ] `kkb.4.4` When a returning caller with a live profile names different work, the bot updates the role with `update_profile` WITHOUT asking permission, and does not say jobs in that role exist before it has looked.
  *Why / how to detect:* "क्या मैं इसे [new role] कर दूँ?" is a fail (removed after `42e6dd04`: the tool ran first, then the bot asked). A "जॉब्स हैं" reassurance before reading `${recommendations}` is a fail (`7f3aa27d`).
- [ ] `kkb.4.5` Fields present on the profile (name, role, age, gender, experience, location) are never asked again, on any later apply in the call either.
  *Why / how to detect:* A question for a field the profile carries is a fail (cf. A5, D9, C6).

## 5. Location step

- [ ] `kkb.5.1` The location work follows CONFIRM (Turn A, its own turn, one of the two closed-set sentences) → at most ONE finer-detail question (Turn B, first call only) → jobs; never more than three location-asking turns.
  *Why / how to detect:* Grade with `python3 raya/regression/location_chain.py --since <date> --agent <id>` (checks C1 to C6: confirm, landmark asked once and only when memory lacks it, never bundled, never after the job list).
- [ ] `kkb.5.2` The place confirmed is the caller's words this call, else `${location}`, else the profile or memory; a remembered place never outranks a non-empty `${location}`.
  *Why / how to detect:* Grounded in `2bf465d9`, `8976c120`, `4b453ebe`, `29964cf6` (sent Hubli, said Koramangala).
- [ ] `kkb.5.3` Turn B is skipped when the memory already carries a `nearest_landmark` (a caller is never asked for their bus stop twice). `UNGRADEABLE: input not observable` when the memory cannot be seen.
- [ ] `kkb.5.4` `${location}` (where to search) is never written to the profile's `location` (where they live).
  *Why / how to detect:* `create_profile` / `update_profile` args; also `raya/regression/location_integrity.py`.

## 6. Presenting jobs

- [ ] `kkb.6.1` Every job spoken is in `${recommendations}`, with role, company, city and salary verbatim from that entry; a masked field (`A***`) is left out, never replaced.
  *Why / how to detect:* Cross-check each spoken job with the args (`0a5ec09d` invented three jobs when all locations were masked). Any job not in the array is a hard fail.
- [ ] `kkb.6.2` With a known role, only role-relevant jobs are offered, role-matched first (role, then location, then salary) in the first batch; never padded with unrelated roles; role families match (customer service = support = care; sales = tele-sales = marketing = field = promoter).
  *Why / how to detect:* cf. C8, D12, D13, D36.
- [ ] `kkb.6.3` The bot never says how many jobs it has; ordinals continue across batches and never restart; no job is named twice; later batches follow array order.
  *Why / how to detect:* "बीस जॉब्स हैं" or a second "पहला" is a fail.

## 7. Before applying

- [ ] `kkb.7.1` Before `create_profile`, every Phase-1 field is known: name, age, location (a city), work experience, role (nature of job defaults to Full-time). Gender never blocks an apply.
  *Why / how to detect:* A Phase-1 question asked after `create_profile` fired, or a create with no city, is a fail (cf. D21, D40). With no city at all there is no create and the call goes to the closing offer.
- [ ] `kkb.7.2` Before EVERY `apply_job`, the data-sharing line names that job's company and role and is the only question in its turn: "आपकी personal details [company] के साथ [role] के काम के लिए शेयर होंगी। वे आपसे सीधे संपर्क कर सकते हैं। क्या मैं अप्लाई कर दूँ?"
  *Why / how to detect:* Look at the two bot turns before each `apply_job`; no share line, a second apply question in the same turn (`0d1cbd72`), or one line reused for two jobs is a fail. The caller asking to apply is not the disclosure (`42e6dd04`, `a52f384c`).
- [ ] `kkb.7.3` A refusal of the share line stops that apply: "कोई बात नहीं। क्या मैं आपको दूसरी जॉब्स बताऊँ?", no `apply_job`.
- [ ] `kkb.7.4` A job already applied to (this call, or in memory's `jobs_applied` by role and company) gets "इस जॉब के लिए आपकी एप्लीकेशन पहले से लगी हुई है — दोबारा अप्लाई करने की ज़रूरत नहीं।…" and NO tool call, unless the caller asks again (then one call, never a third).
  *Why / how to detect:* `apply_job` carries the required `duplicate_check`; a value of "not-applied-before" on a job the transcript shows was already applied is a laundered skip (cf. D91, D95).

## 8. Tool payloads

- [ ] `kkb.8.1` No `create_profile` when a live seeker item exists; on the new or draft path, `create_profile` first, then `apply_job` in a later turn using `items[0].item_id` (profile) and top-level `user_id` (acting user).
  *Why / how to detect:* Both in one batch gives an empty `profile_id` (cf. D20, D31); a create on a live profile is a duplicate (cf. C7, D37).
- [ ] `kkb.8.2` Enum values are byte-exact: `workExperience` ∈ Fresher / Worked before / Returning after a break; `gender` ∈ Male / Female / Other / Don't want to share; `natureOfJobsInterestedIn` ∈ Internship / Apprenticeship / Full-time / Flexible; Phase-2 enums as the prompt lists them.
  *Why / how to detect:* A raw phrase ("one year", "ladka") returns 400 `INVALID_ITEM_STATE` (cf. D38).
- [ ] `kkb.8.3` `phone` on `create_profile` / `update_profile` is the same 12-digit value used for `get_profile`; every value is Latin (names and places transliterated); `location` is "City, State, India" (Phase 2: "Area, City, State, India").
  *Why / how to detect:* cf. D3, D17, D39.
- [ ] `kkb.8.4` `apply_job.job_id` is the selected job's id copied verbatim, 8-4-4-4-12 with all four hyphens; `profile_id` and `acting_as_user_id` are UUIDs from the same response; no `requirements_snapshot` is sent.
  *Why / how to detect:* A stripped 32-character id returns 404 (cf. D30); `requirements_snapshot` returns 400 (cf. D33).
- [ ] `kkb.8.5` No line containing "अप्लाई" before the apply result; the only permitted bridge is a bare "ठीक है।". "अप्लाई हो गया है…" only in the same turn as a successful `apply_job` result, never later.
  *Why / how to detect:* "आपकी तरफ़ से अप्लाई कर देती हूँ" before the tool, narration ("आवेदन भेज रही हूँ"), or the success line with no success result in that turn is a fail (cf. C5, D20, D27, D78).

## 9. Apply failure

- [ ] `kkb.9.1` The failure line is looked up, not chosen: an already-existing application (duplicate check matched, or the error names `ACTION_LIMIT_REACHED` / "already exists") gets the already-applied line; every other error gets the single failure line ("अप्लाई अभी पूरा नहीं हो पाया…"), which names no cause.
  *Why / how to detect:* `raya/regression/apply_outcomes.py` and `apply_failure_wording.py`. A "technical issue" claim, a "maybe you already applied" hedge, or both rows spoken together (`b4e34994`, `41a2c19d`) is a fail.
- [ ] `kkb.9.2` The failure turn ends on the offer of another job ("ठीक है। एक और option है — [role], [company], [location]। इसमें अप्लाई करने की कोशिश करूँ?", one job, never the failed one) or, with none left, the "आपकी दिलचस्पी हमने note कर ली है…" line; no blame, no "आप बाद में call कीजिए", no third attempt.
  *Why / how to detect:* cf. D15, D27. The "आज यह अप्लाई पूरा नहीं हो पा…" line is allowed only after a SECOND failed apply.
- [ ] `kkb.9.3` After a failed apply the success line is never spoken, in any later turn.
  *Why / how to detect:* `a111ed52`, `0178c996`, `503440a3`, `4b0ea64d`, `22781eb6`; `apply_result_integrity.py` check X.

## 10. After a successful apply (Phase 2)

- [ ] `kkb.10.1` The bridge "आपकी जानकारी पूरी करने के लिए कुछ छोटी बातें पूछ लूँ।" says nothing about the application; then only the MISSING topics, one per turn, in order: gender, qualification (+ one follow-up), experience details (not for a Fresher), other help needed, granular area.
  *Why / how to detect:* Asking a field the profile has, or skipping a missing one (`67058058`), is a fail. "कुछ और पूछना है?" is not a Phase-2 question.
- [ ] `kkb.10.2` Each answer is saved at once with `update_profile` (the field plus `profile_id`, `name`, `age`, `phone`; no empty fields), corrections saved again; `hold_message` "एक सेकंड।"; "नोट कर लिया" said once and only after the tool returned.
  *Why / how to detect:* A spoken "नोट कर लिया / अपडेट कर दी" with no `update_profile` in that turn is a hallucinated write.
- [ ] `kkb.10.3` The closing read-back is labelled (नाम, उम्र, gender, काम, पढ़ाई, एरिया), with age in words and gender in the language (never "38", "Male"), no phone number, ending on "सब सही?" with nothing appended.
  *Why / how to detect:* A second question in that turn is a fail (`c260fb90`).

## 11. Closing service-provider offer (Need Capture)

Shared rules: `generic.md` §17 (once, skip list, no partner named).

- [ ] `kkb.11.1` The path matches the outcome: applied, or declined for a concrete reason → Path A ("जॉब मिलने के चांस और बढ़ाने के लिए हमारे पास कुछ सर्विस प्रोवाइडर हैं…"); confused or no clear reason → Path B ("मैं समझती हूँ, डिसाइड करना मुश्किल…").
  *Why / how to detect:* Path B to a caller who gave a concrete reason is a fail.
- [ ] `kkb.11.2` After a successful apply, the offer (Path A) follows the success line in the same turn, and Phase 2 still runs after the reply, whatever it was.
  *Why / how to detect:* Closing after "नहीं" to the offer without the Phase-2 questions and read-back is a fail (`8674462f`).
- [ ] `kkb.11.3` A yes is answered with the acknowledgement template ("बहुत बढ़िया, हमारी टीम आपसे एक-दो दिन में संपर्क करेगी।") plus exactly one next question, never a sentence about the application.
- [ ] `kkb.11.4` `service_provider_pitched` and `service_provider_interest` in `call_output` match the transcript.

## 12. Language and words (beyond `generic.md` §8)

- [ ] `kkb.12.1` Canonical place spellings (e.g. गाज़ियाबाद with nukta); PIN codes digit by digit, never as a number.
  *Why / how to detect:* cf. D26; `spoken_form.py`.
- [ ] `kkb.12.2` No prohibited promises: "गारंटीड जॉब", "पक्का मिलेगा", "selection हो जाएगा", "बेस्ट ऑपर्च्युनिटी".
- [ ] `kkb.12.3` "अकाउंट" only inside the Part 1 line; "प्रोफाइल" never.

## 13. Variant differences

- [ ] `kkb.13.1` **Legacy up-getjob** (`kkb-hi-out`, `kkb-kn-out`, `kkb-hi-in`, `kkb-kn-in`): `get_profile(phoneNumber: "+91…")`, single prefix; no Part 1 / `record_consent`; §2.4 and §8 Signals ids do not apply. Grade the rest against that prompt's own lines.
- [ ] `kkb.13.2` **Inbound** (`*-in`, `*-in-signals`): a welcome opener instead of the audio check and outbound introduction (`generic.md` §1.4); the bot looks up the CALLER's number, so test data sits on the tester's number. Tested by PATCHing an integer `out_did` (see `/voice-test` → Inbound bots).
- [ ] `kkb.13.3` **Slim** (`kkb-*-signals-slim`): the closing offer is `get_services` first, then one turn naming only the organisation the tool returned (e.g. "ट्रेन ट्रस्ट"); a service Yes needs the caller to name a time; new callers' consent is written at once with `record_consent_new`. Graded against the Slim prompt and `generic.md`; this file's §11 Path A/B lines do not apply.
- [ ] `kkb.13.4` **Every agnostic rule holds in every language**: the Kannada bots get their own calls for §2, §3, §7, §8 and §9.
  *Why / how to detect:* Historically the richer bug source (most `PROFILE_NOT_LIVE` and payload failures were Kannada). A rule that holds in Hindi and fails in Kannada is drift.

## Observations (not graded)

- **Need Capture placement after a failed apply is contradictory in the Signals prompt** (2026-10-14):
  "Need Capture → POSITIONAL RULE" says the offer waits until the job conversation is over and never
  shares the failure turn, while "Apply Failure Handling" says the failure turn ENDS on the Path A
  offer, and "Need Capture → Rules" names a "scoped exception" that the same section also calls deleted.
  Until `/update-prompt` resolves it, record where the offer fell on failure calls as an observation;
  grading either side would give a random verdict.
