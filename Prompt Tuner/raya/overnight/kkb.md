# KKB Seeker — Voice-Agent Test Checklist (Signals + legacy backends)

Grade a KKB job-seeker call (काम की बात / ಕೆಲಸದ ಮಾತು) from its transcript, `tool_calls`, and `call_output`. Items are ordered along the call flow; each says what proves pass/fail. Backend arg-shapes differ between **Signals** (`get_profile(phone_number:"91…")`, no `+`, no `requirements_snapshot`) and legacy **up-getjob** (`get_profile(phoneNumber:"+91…")`) — confirm the persona used the matching shape before grading arg items.

## Opening & greeting

- [ ] The call opens with the fixed neutral greeting + one "are you looking for work?" question, and NOTHING personal.
  *Why / how to detect:* First bot turn must be the canonical line ("नमस्ते। शहर प्रशासन की काम की बात में आपका स्वागत है… क्या आप अभी काम ढूंढ रहे हैं?" / Kannada twin). Fail if turn 1 speaks the caller's name, a saved role, a "last time you were looking in [city]" resume line, or a stall/looking-up line ("आपकी जानकारी मिल रही है…"). (cf. D32, D29, B2)

- [ ] No personal detail is spoken before `get_profile` has actually returned this call.
  *Why / how to detect:* Read `tool_calls` — any name/role/"you applied last time" spoken while `get_profile` has 0 prior returns = fabrication from `${contact_memory}`. (cf. D32, C5b)

- [ ] A clear "no / not looking" at the interest gate ends the call politely with no further steps.
  *Why / how to detect:* On "नहीं" / "ಇಲ್ಲ", the bot should close (`drop_reason:"Said not looking"`) and must NOT go on to fetch the profile or pitch jobs. Fail if it pushes "आपकी बेसिक जानकारी देख लूँ?" after an explicit decline. (catalog: Kn outbound f4e85575 bug)

## get_profile — fires exactly once, silently, after the interest gate

- [ ] `get_profile` is emitted exactly ONCE, as the first action right after the caller answers the opening job question.
  *Why / how to detect:* Count `get_profile` in `tool_calls` — exactly 1. Zero = the fetch never fired (memory-substitution / greeting-bundling bug, D32/D29); ≥2 = it re-fetched at apply time, forbidden by the HARD SCOPE rule. (cf. D29, D32, D7, D25)

- [ ] `get_profile` is a real tool call, not substituted by reading `${contact_memory}`.
  *Why / how to detect:* If the bot greets by name / states a role but `tool_calls` shows no `get_profile`, memory stood in for the fetch — fail. The tool call must precede any personalization. (cf. D32, C5b)

- [ ] The fetch is silent: no permission-ask and no lookup narration anywhere in the call.
  *Why / how to detect:* No spoken "क्या मैं आपकी प्रोफाइल/जानकारी देख सकती हूँ?", "आपकी जानकारी देख रही हूँ/मिल गई", "प्रोफ़ाइल मिल गई" (or Kannada equivalents). The word "profile"/"प्रोफाइल"/"ಪ್ರೊಫೈಲ್" must never be spoken. (cf. B2, D8, D24)

- [ ] `get_profile`'s `hold_message` is the neutral hold only ("एक मिनट" / "ಒಂದು ನಿಮಿಷ"), never a reveal.
  *Why / how to detect:* Read `tool_calls[].function.arguments.hold_message` on `get_profile` — must be exactly the neutral one-moment phrase, never "आपकी जानकारी देख रही हूँ" / "ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ನೋಡುತ್ತಿದ್ದೇನೆ". A revealing hold_message is spoken by the platform = fail. (cf. D34)

- [ ] Phone is sent in the backend's required shape — Signals `phone_number:"91XXXXXXXXXX"` (12-digit, no `+`), single prefix.
  *Why / how to detect:* Inspect `get_profile` args. Signals must be `91`+10-digit digits-only; a bare 10-digit, a `+`, or a doubled `+9191…`/`919191…` is a fail (wrong-record / empty fetch). Legacy up-getjob uses `+91…`. (cf. D17, D39, C3)

## Reading the fetched profile & selecting the right one (1:1 live profile)

- [ ] The bot selects the LIVE profile item by `lifecycle_status`, never blindly `items[0]`.
  *Why / how to detect:* When `get_profile` returns >1 item, the id later used as `profile_id` must belong to an item whose `lifecycle_status` is `"live"`. Fail if it picked a `draft` (esp. a draft at `items[0]`) while a live item existed. This is the central Signals bug. (cf. D37)

- [ ] A stale `draft` is ignored whenever a live item exists; the bot does not treat "a profile was found" as "ready".
  *Why / how to detect:* Readiness must key on the item's `lifecycle_status`, NOT on participant `user_consent` (which can be all-true while an item is still draft). Fail if it applied to a draft or created a duplicate despite a live item. (cf. D37, D35)

- [ ] Fields present in the selected item (name, role, age, gender, experience, location) are treated as KNOWN and not re-asked.
  *Why / how to detect:* If the profile carried age/gender/etc. yet the bot asks for them, fail. Known status must persist across every apply in the same call. (cf. A5, D9, C6)

- [ ] A returning caller with a `live` profile is applied directly — no `create_profile`, no re-asked consent/age.
  *Why / how to detect:* READY path fires `apply_job` only (one tool). A `create_profile` on a live profile is a duplicate = fail. (cf. D37, C7)

- [ ] Placeholder/sentinel role values ("Any", "Not Available", empty, garbled) are treated as UNKNOWN — never spoken, never role-confirmed.
  *Why / how to detect:* Fail if the bot says "आप Any का काम देख रहे हैं" or role-confirms a sentinel. On unknown role it must go to the Case-B pool overview instead. (cf. D36-adjacent, C9)

## Role confirmation & role-update offer

- [ ] Role-confirm is framed as the caller's CURRENT occupation, then asks if they still want that kind of job — as its own turn.
  *Why / how to detect:* Expect "मैं देख रही हूँ कि आप अभी [role] का काम कर रहे हैं — क्या आप अभी भी [role] की जॉब देख रहे हैं?" The turn must END on this question — fail if the area question or job list is bundled into the same turn. (cf. A7, A6)

- [ ] On a role mismatch (returning caller with a LIVE profile), the bot offers ONCE to update the stored role, then acts on the answer.
  *Why / how to detect:* Expect a single "अभी आपका role [old] है — क्या मैं इसे [new] कर दूँ?"; on "yes" an `update_profile` with the new `role`; on "no" no update. Either way the call continues with the new role. Fail if it argues/pushes the old role or updates without asking.

## Job presentation — only from recommendations, relevance-filtered

- [ ] Every job presented comes from `${recommendations}`; no job is invented or pulled from profile/memory/user text.
  *Why / how to detect:* Cross-check each spoken role+company against `jobs_recommended` in `call_output` and the input array. Any job not in the array = hallucination (hard fail). If recommendations are empty/invalid, the bot must trigger No-Match and close, never invent. (cf. Hallucination Guard, C-family)

- [ ] With a KNOWN role, only role-relevant jobs are shown — the batch is NEVER padded to three with unrelated roles.
  *Why / how to detect:* Fail if an unrelated role (e.g. EV-charging technician to a data-entry seeker) appears as option one or as filler. 1 relevant job → present only 1. (cf. D36)

- [ ] The role-matched job is presented FIRST (ranking role → location → salary), not the array's given order.
  *Why / how to detect:* Compare presentation order to the caller's known role/city. Leading with an out-of-city or off-role job when a same-city/same-role job exists = fail. (cf. C8, D13, D12)

- [ ] Role-name variants / the customer-facing family are matched as the same role (no false "no jobs").
  *Why / how to detect:* customer service = support = care; sales = tele-sales = marketing = field = promoter; crew = team-member = retail/store. Fail if the bot says a family term has "no jobs" while a family member sits in the pool. (cf. D12)

- [ ] Job IDs, JSON, field names, or payloads are never spoken aloud.
  *Why / how to detect:* Scan spoken lines for a `{`, quoted field names, or a UUID. Any = hard fail. (cf. D20, "Never Speak Tool Payloads")

## Consent before apply (details shared with company)

- [ ] Before applying, the consent/data-share line is spoken.
  *Why / how to detect:* Expect "अप्लाई करने पर आपकी personal details company के साथ share होंगी — अप्लाई कर दूँ?" (in Step 3 deep-dive) and, on the new/draft path, the create-consent line "…आपकी प्रोफाइल बनानी होगी और आपकी जानकारी कंपनी के साथ शेयर करनी होगी — क्या इसके लिए आपकी सहमति है?" Fail if `apply_job`/`create_profile` fired with no consent turn. (cf. E2)

- [ ] On the NOT-READY (new/draft) path, the create-consent question is asked exactly once and BEFORE `create_profile`.
  *Why / how to detect:* Finding a `draft` does NOT imply prior consent — the consent ask must still precede `create_profile`. Fail if `create_profile` fired with no preceding consent ask, or if consent was re-asked on a later apply in the same call. (cf. D35, E2, B1)

- [ ] A consent decline cleanly stops the flow — no `create_profile`, no `apply_job`.
  *Why / how to detect:* On "नहीं", expect a graceful close and NO create/apply `tool_calls`; the decline surfaces in `final_summary`/`drop_reason`. Fail if any profile/apply tool fires after a refusal. (cf. E2)

## NOT-READY path — Phase-1 minimum-required before create_profile

- [ ] All Phase-1 minimum-required fields are KNOWN before `create_profile`: Name, Age, Location, Work Experience, Role, Nature.
  *Why / how to detect:* On the new/draft path, confirm each was gathered (or reused from a draft's `item_state`) before `create_profile` fires. A field asked AFTER `create_profile` already ran = the gate didn't hold (fail). Gender is NOT a Phase-1 field — apply must never block on it. (cf. D21, D40)

- [ ] A rushed "हाँ अप्लाई कर दो" does not skip Phase-1 collection.
  *Why / how to detect:* Even after an eager apply-consent, missing fields (esp. Location) must still be collected one at a time before `create_profile`. (cf. D21)

- [ ] For a draft profile, fields the draft already carries are reused, not re-asked.
  *Why / how to detect:* If `item_state` had age/gender/name/location/experience yet the bot re-asked them, fail — a fully-populated draft should go straight to consent. (cf. D35)

- [ ] `create_profile` is called with `location` present (so the profile is minted LIVE, not draft).
  *Why / how to detect:* Read `create_profile` args — a missing/empty `location` mints a `draft`, which then fails `apply_job` with `422 PROFILE_NOT_LIVE`. Pair a missing location with a `draft` create-response + PROFILE_NOT_LIVE to confirm. (cf. D40)

## create_profile payload integrity (Signals)

- [ ] Enum fields carry only allowed values, mapped from the spoken answer (never a raw phrase).
  *Why / how to detect:* Read `create_profile`/`update_profile` args: `workExperience` ∈ {Fresher, Worked before, Returning after a break}; `gender` ∈ {Male, Female, Other, Don't want to share}; `natureOfJobsInterestedIn` ∈ {Internship, Apprenticeship, Full-time, Flexible}. A raw phrase ("one year", "ladka", "koi bhi") → 400 INVALID_ITEM_STATE = fail. (cf. D38)

- [ ] `create_profile.phone` is a single E.164 value — Signals 12-digit `91`+number, no `+`, never doubled.
  *Why / how to detect:* Inspect args; `+9191…` / `919191…` / a bare 10-digit resolves the wrong (or a new) user → duplicate profile / later 403 ITEM_NOT_OWNED_BY_USER. Must equal the phone used for `get_profile`. (cf. D39, D17, C3)

- [ ] All payload values are English/Latin script (name, location transliterated); no Devanagari/Kannada in the payload.
  *Why / how to detect:* Read args — a `name:"पार्थ"`/`"ಪಾರ್ಥ"` or `location:"कोरमंगला"` = fail (transliterate to "Parth"/"Koramangala"). (cf. D39, D3)

## apply_job — correct ids, exact job_id, decoupled from create

- [ ] `apply_job` uses the LIVE `profile_id` + the real `acting_as_user_id` (top-level `user_id`), both UUIDs.
  *Why / how to detect:* Read `apply_job` args. `profile_id` must be the live item's `item_id` UUID (returning) or `create_profile`'s `items[0].item_id`/`profileId` UUID (new) — never a draft id, never the numeric top-level `id`, never the phone, never a template token like `items[0].item_id`. `acting_as_user_id` must be the `user_id` UUID, not the phone. (cf. D37, D28, C7, catalog S12)

- [ ] `job_id` is the exact hyphenated UUID from the selected job, copied verbatim.
  *Why / how to detect:* Read `apply_job.job_id` — a 32-char hex run with hyphens stripped → 404 "Job not found" = fail. Must be 8-4-4-4-12 and match a `job_id` in `${recommendations}`. (cf. D30)

- [ ] `apply_job` sends NO `requirements_snapshot`.
  *Why / how to detect:* The Signals apply payload must omit `requirements_snapshot` entirely; sending `[]`/`{}` → 400 FST_ERR_VALIDATION / "expected record, received undefined" = fail. (cf. D33, catalog S10)

- [ ] On the new-caller path, `create_profile` and `apply_job` are NOT emitted in the same turn/batch.
  *Why / how to detect:* They must cross a tool-result boundary — `create_profile` returns first, then `apply_job` reads its id. A same-batch emit yields `apply_job` with an empty `profile_id` = fail. (cf. D31, D20)

- [ ] `apply_job` actually fires; success is claimed only after a real success result.
  *Why / how to detect:* The success line ("अप्लाई हो गया है") requires an `apply_job` result of success in the same turn. A success line with no `apply_job` call, or after only `create_profile`, is a hallucinated apply (hard fail). Cross-check `applied_to_job:"Yes"` / `applications_count` / `jobs_applied[]` against actual successful `apply_job` calls. (cf. C5, D20)

- [ ] No apply narration stands in for the tool call, and no repeated bridge.
  *Why / how to detect:* The bridge ("अप्लाई कर देती हूँ") is said once, immediately before the tool; "आपका आवेदन भेज रही हूँ / process कर रही हूँ" narration = fail. A bridge spoken 2+ times with no new `apply_job` = fail. (cf. B1, C5c, D20, D27)

## Apply-failure handling

- [ ] On `apply_job` error, the bot owns the failure and offers exactly one recovery path — never dead-ends or blames the seeker.
  *Why / how to detect:* Expect the base failure line once, then ONE alternate job (not a batch of three, never the same failed job) or a no-time-committed callback. Fail on "sorry" over-apology, "आप बाद में call कीजिए", blaming phone/network, or a third retry loop. (cf. D15)

- [ ] The failure turn does not re-speak the apply bridge, and an already-failed `job_id` is never re-fired.
  *Why / how to detect:* Failure message begins directly with the base failure line (no bridge/hold re-spoken); the same failed `job_id` must not appear in a second `apply_job` call this call. (cf. D27)

## Phase-2 post-apply enrichment

- [ ] Enrichment runs ONLY after a successful `apply_job`, and asks ONLY genuinely-missing fields.
  *Why / how to detect:* Sequence check — enrichment questions appear after an `apply_job` success. Only Gender (if `item_state.gender` empty) and granular location are in scope; asking a field the profile already has = fail. (cf. A5, C6, D9)

- [ ] The bot announces the EXACT count of Phase-2 questions up front and never adds "one more".
  *Why / how to detect:* Expect "…के लिए [N] छोटी बातें पूछ लूँ" where N covers every Phase-2 question (usually one; two only if gender missing). A follow-on unannounced question = fail. (cf. D10-adjacent)

- [ ] Gender is asked only if absent, never inferred from name/voice; questions are one-at-a-time.
  *Why / how to detect:* If profile had gender, no gender question should appear. Two questions stacked in one turn = fail. (cf. A7, A5)

- [ ] Each captured Phase-2 field is persisted via `update_profile` (one field per call), reusing the live/created profile id.
  *Why / how to detect:* Read `update_profile` `tool_calls` — one per gathered field, carrying required `profile_id`+`name`+`age`+`phone` plus only the new field (enum-valid, Latin script, no empty fields). No `update_profile` after enrichment answers = fail. (cf. D38, D39, C-family)

- [ ] The bot does not ask for anything the Signals profile cannot store.
  *Why / how to detect:* Fail if it asks "working or studying?", highest qualification, college, exact years, last role, email — none has a profile field. (grounded in Phase-2 section)

- [ ] A final labelled read-back confirms all known fields INCLUDING gender, and phone is not read aloud.
  *Why / how to detect:* Expect one labelled line "…नाम [नाम], उम्र [age], [gender], काम [role], एरिया [एरिया] — सब सही?" Fail if unlabelled comma-list, gender omitted, or the phone number spoken. Corrections must trigger another `update_profile`. (cf. Phase-2 confirm rule)

## Language, TTS & voice hygiene

- [ ] Spoken output is Devanagari (Hindi) / Kannada script only; payloads stay Latin.
  *Why / how to detect:* No Roman-Hindi in speech; no native script in tool args. (cf. D3)

- [ ] Numbers, money, phone, dates spelled as words; no "/" voiced as "slash".
  *Why / how to detect:* Scan spoken lines for digits, `₹`, AM/PM, or a literal "/". Role/category labels must use "या"/"ಅಥವಾ". (cf. D2, D6)

- [ ] Canonical location spellings are used consistently (e.g. गाज़ियाबाद, never गाजियाबाद).
  *Why / how to detect:* Compare each spoken place name to the Canonical Location Spellings list. (cf. D26)

- [ ] No hard/Sanskritised or prohibited promotional vocabulary.
  *Why / how to detect:* Fail on "गारंटीड जॉब", "बेस्ट ऑपर्च्युनिटी", "पक्का मिलेगा", "Not Available" spoken aloud, or over-formal tatsama words. (cf. D1, Prohibited Language)

## Silence / low-signal & clarification

- [ ] On silence/soft/one-word input, the bot uses a bounded number of gentle re-prompts, then exits gracefully.
  *Why / how to detect:* Expect "कोई बात नहीं, सोचिए…" and a job-type menu; fail if it loops forever or fabricates an answer on the caller's behalf. `drop_reason` should reflect the reason. (catalog: silent-caller scenario)

- [ ] ASR-ambiguous critical fields (gender/age/number/option) are confirmed with a read-back before being written.
  *Why / how to detect:* Expect "आपने [X] कहा, सही?" before a value reaches `create_profile`/`apply_job` or a job is locked in. A mis-heard value written without confirmation = fail. (catalog: ASR-mishearing scenario; State Safety Check)

## Cross-language parity (Kannada twin)

- [ ] The Kannada Signals bot enforces the same agnostic logic as Hindi (live-item selection, decoupled create→apply, no requirements_snapshot, enum mapping, single-E.164 phone, Phase-1 gate incl. location).
  *Why / how to detect:* Run the same Signals apply on `KKB Kannada Signals` — historically the richer bug source (most PROFILE_NOT_LIVE / requirements_snapshot failures were Kannada). Any agnostic guard that holds in Hindi but fails in Kannada = drift (fail). (cf. bug-patterns F; D20 cross-language check)
