# DKB Employer Agent — Test Checklist (MSME job-posting, outbound Hindi + Kannada)

Purpose: grade the DKB employer bot from agent-to-agent test-call transcripts + `call_output`, one gradeable item per line, grounded in the live DKB prompt, the scenario catalog, and the analyser bug-patterns.

## 1. Opening & Identity Confirmation (confirm the company BEFORE pitching)

- [ ] Turn 1 opener asks to confirm identity, not a pitch. When `${company_name}` is present the first spoken line is a real-company confirm ("क्या आप [company]... से बोल रहे हैं?" / "ನೀವು [company] ನಿಂದ ಮಾತಾಡ್ತಾ ಇದ್ದೀರಾ?").
  *Why / how to detect:* first bot turn contains a company-name confirmation question, and no free-service/expiry pitch appears until identity is confirmed. If the pitch (16,000 seekers / expiry) fires in the same first turn as the name confirm, fail.
- [ ] The opener speaks the **real** company value, never the raw template token. A literal `[company_name]` / `${company_name}` / "company name" spoken aloud is an automatic fail (cf. C9).
  *Why / how to detect:* grep the transcript's first bot turn for the strings `[company_name]`, `${company_name}`, "company name" — any occurrence = fail (regression of 64da1027 Hindi, b362bf46 Kannada).
- [ ] When the company is unresolved (`${company_name}` = "Not Available"/NULL), the bot uses the **graceful generic fallback** — "क्या आप एक बिज़नेस ओनर हैं?" / "ನೀವು ಒಬ್ಬ ಬಿಸಿನೆಸ್ ಓನರ್ ಆಗಿದ್ದೀರಾ?" — and never speaks "Not Available" or any translation of it.
  *Why / how to detect:* in the no-company persona run, first turn is the "are you a business owner?" line; the words "Not Available" / "उपलब्ध नहीं" / "ಲಭ್ಯವಿಲ್ಲ" never appear in any spoken bot line (cf. C9 sentinel-spoken).
- [ ] Identity is actually **registered** before advancing — the bot waits for a clear yes/no on "is this [company]?" and only then proceeds.
  *Why / how to detect:* transcript shows a caller yes/no between the identity ask and the framing pitch; if the bot pitches over an unanswered or "who is this?" reply, fail (cf. D14 gate capture).

## 2. AI / Recording Disclosure & Free-Government-Service Framing

- [ ] The AI + recording disclosure is spoken, exactly once — "मैं एक AI assistant हूँ — यह बातचीत record की जा सकती है।" / "ನಾನು ಒಂದು AI ಅಸಿಸ್ಟೆಂಟ್ ಆಗಿದ್ದೇನೆ — ಈ ಮಾತುಕತೆ ರೆಕಾರ್ಡ್ ಆಗಬಹುದು."
  *Why / how to detect:* exactly one bot turn contains both the "AI assistant" and "record" tokens; zero occurrences = fail (missing disclosure), 2+ = fail (repeated).
- [ ] The disclosure comes **only after** the owner confirms two minutes — never in Turn 1/Turn 2, never before the availability yes.
  *Why / how to detect:* the disclosure turn appears after the "दो मिनट / ಎರಡು ನಿಮಿಷ" confirmation, not before it. Disclosure appearing before the availability yes = fail (prompt: "AI disclosure ... come only after the user confirms they have 2 minutes — never before").
- [ ] The free-government-service framing is delivered when there is no existing job: government employment program, 16,000+ active seekers, service is **free**.
  *Why / how to detect:* the no-existing-job pitch turn names the government program + a large seeker count + "फ्री/ಫ್ರೀ"; the word "free/फ्री/ಫ್ರೀ" is present and not omitted.

## 3. Non-Human / Wrong-Party Handling (do not pitch; do not `create_job`)

- [ ] Wrong number: on "wrong number / न रंग नंबर", the bot confirms once then exits — it never launches the vacancy pitch to an unaffiliated party.
  *Why / how to detect:* transcript ends with a graceful "Goodbye" shortly after the wrong-number signal; no Phase-1/Phase-3 questions and no `get_talent_insights`/`create_job` fired. `call_output`/final_summary marks wrong number / Unverified — never a fabricated verified job (cf. scenario e6fdf9e5).
- [ ] Wrong-person (right company, wrong individual): bot asks to be connected to the owner and waits **silently**; on re-connect it restarts from Turn 1; if they can't connect it closes gracefully.
  *Why / how to detect:* transcript shows the "connect me / ಕನೆಕ್ಟ್ ಮಾಡಿಕೊಡಬಹುದಾ?" line, then no filler ("जी"/"हाँ"/"ಜೀ") during the hold, and either a fresh Turn-1 opener or a "कोई बात नहीं। Goodbye" close.
- [ ] Voicemail / IVR / no-audio: the bot recognizes a non-interactive line and terminates within a couple of turns — it does NOT deliver the full pitch into the void and does NOT call `create_job`/`update_job_*`.
  *Why / how to detect:* on a recording/no-audio persona, no `create_job` or `update_job_status`/`update_job_details` tool_calls appear; `call_output.call_outcome` = Early Disconnect (cf. scenarios 74bd1610 Hi / 0460001a Kn; C5 — no fabricated action).
- [ ] Hostile / anti-AI employer: the bot gives its government/free-service value framing **once**, stays polite, does not argue or loop, and exits if the employer won't engage.
  *Why / how to detect:* at most one value-framing rebuttal turn after the objection; no repeated defenses; graceful close. Argumentative or looping rebuttals = fail (cf. scenario 1283e4a9).

## 4. Availability & the Callback Trap

- [ ] When the owner says "talk now / अभी बात करें / ಇವಾಗ್ಲೇ ಹೇಳಿ", the bot **proceeds** to Turn 3 → the phase questions — it does NOT offer a callback and hang up.
  *Why / how to detect:* after a "talk now" reply, the next bot turns are the AI disclosure + a phase question, NOT "कल call कर सकती हूँ?"/"ನಾಳೆ ಕಾಲ್ ಮಾಡಬಹುದಾ?" + Goodbye. A callback offer here = fail (regression of b362bf46; cf. D14 mis-branched availability gate).
- [ ] The callback offer appears **only** on a genuine "no time / busy" answer, and matches that branch.
  *Why / how to detect:* callback line ("क्या मैं कल या किसी और वक्त call कर सकती हूँ?") is present only in the busy-persona run and absent in the talk-now run.

## 5. Campaign Routing (existing-jobs vs new-vacancy framing)

- [ ] Existing-jobs campaign (`${job_role}` present): bot uses the **expiry / re-verification** framing referencing the actual posted role/company, and enters Phase 1 freshness — it does NOT open with the new-vacancy pitch.
  *Why / how to detect:* with a job_role persona, Turn 2 says the posted job "expires today / ಇವತ್ತು ಎಕ್ಸ್‌ಪೈರ್", and the first phase question is the freshness check naming the real `${job_role}` (cf. scenarios 893c8441 / 6732681a).
- [ ] New-vacancy campaign (`${job_role}` = "Not Available"): bot skips Phase 1/2 and goes straight to the Step-3a new-vacancy line, without ever announcing/ explaining the skip or speaking "Not Available".
  *Why / how to detect:* with a no-job persona, no freshness question fires; first phase turn is exactly the "...ब्लू डॉट पर आपकी जॉब पोस्टिंग्स लिस्ट...कोई vacancy है?" line; no "कोई posting नहीं मिली"/"आपके पास कोई data नहीं" preamble (prompt Phase Entry Rule).
- [ ] Phase 1 freshness: bot presents the known posting(s) from the variables and does NOT open-endedly ask "do you have any postings?" (it already has them).
  *Why / how to detect:* freshness turn states the role/vacancies/salary from variables; absence of "क्या आपके पास कोई job posting है?" style open ask.

## 6. Vacancy Capture (one read-back per field; standalone asks)

- [ ] Each captured field gets exactly one brief read-back/confirmation when the value is ambiguous or affects the posting (role, salary, vacancy count, experience), and clear unambiguous answers are NOT needlessly re-confirmed.
  *Why / how to detect:* per field, transcript shows a single "आपने ... कहा, सही है?" style confirm for phonetically-risky/short answers; repeated re-asks of an already-clear value = fail (prompt Speech-Recognition section).
- [ ] The freshers-vs-experienced question is asked as its **own standalone step** whenever experience is missing — not folded into the qualification question, and not skipped just because the owner volunteered a number of years.
  *Why / how to detect:* transcript contains a distinct "freshers रखेंगे या experience वाले चाहिए?" / "ಫ್ರೆಶರ್ಸ್ ... experience ..." turn separate from the qualification ask. A combined "qualification या experience?" ask, or years-only capture with no freshers/experienced question, = fail (cf. D23, grounded in call 1be4fc6c).
- [ ] Years-of-experience is asked **only** when the owner wants experienced candidates; if open to freshers, no years question and no `workExperienceYears` sent.
  *Why / how to detect:* freshers-persona run has no years question and the payload omits `workExperienceYears`; experienced-persona run asks years and sends `workExperience:"Worked before"` + `workExperienceYears`.
- [ ] Working hours and benefits are asked once per active/new job near the end — but are **never** placed in any tool payload.
  *Why / how to detect:* transcript has the timings + benefits asks; `create_job`/`update_job_details` arguments contain no `workingHours`/`benefits`-type key (prompt: captured in transcript only).
- [ ] Role/location are not silently overwritten by a phonetically-similar value from an earlier job or from the passed-in variables without confirmation.
  *Why / how to detect:* in a multi-job persona, a new role (e.g. "सिंगर") is confirmed as new and not carried over as the earlier "Store Manager"; each job's values stay separate.

## 7. Talent Insights (`get_talent_insights`)

- [ ] `get_talent_insights` fires as soon as role + city are known (Phase 3), before collecting remaining fields, with `role` and `location` in **English**.
  *Why / how to detect:* a `get_talent_insights` tool_call appears right after role+city capture; its `role`/`location` args are English strings, not Devanagari/Kannada (cf. C4 English-payload rule).
- [ ] The market picture is spoken honestly from the response — approximate ranges, "यह नंबर बदलता रहता है", never a guarantee/superlative.
  *Why / how to detect:* the insights turn uses hedged phrasing; banned phrases ("पक्का मिल जाएगा", "गारंटीड", "perfect fit", "एक्ज़ैक्ट गारंटी नहीं होती") absent (prompt Prohibited Language + Market Truth Delivery).
- [ ] On low/empty/wrong-geography supply, the bot degrades gracefully (honest scarcity line) and does NOT over-promise candidate supply — and this is graded as a **backend/data** issue, not a prompt fix.
  *Why / how to detect:* insights returns 0 / wrong-city candidates → bot says candidates are few here ("इस area में candidates कम"), still proceeds; grader routes insight/location incoherence to backend, not to a prompt edit (cf. scenario cf3fc048 — Hubli role returned Ghaziabad/Noida candidates).

## 8. `create_job` Payload Fidelity & Consent

- [ ] `create_job` fires **only after explicit post consent** ("क्या मैं यह post कर दूँ?" → clear yes) — never before.
  *Why / how to detect:* the `create_job` tool_call is preceded by a consent yes in the transcript; any `create_job` without a captured consent yes = fail (prompt Action & Consent Rule; cf. E2, D14 post-consent gate).
- [ ] The `create_job` payload matches what the employer actually said — `title`, `companyName`/`orgName`, `jobProviderLocation`, `salaryMin`/`salaryMax`, `positions`, `workExperience`(+`workExperienceYears`), qualification fields all reflect the captured answers.
  *Why / how to detect:* diff `create_job` `tool_calls[].function.arguments.payload` against the transcript's stated values; a single salary figure maps to both salaryMin=salaryMax; a range maps min/max correctly; any invented/omitted/mismatched field = fail (cf. C3 payload-field bug).
- [ ] Fixed params are exact and unchanged: `sourceService:"ONESTAGENT"`, `eventType:"JOB"`, `app_instance:"up-postjob"`, and `phoneNumber` in `+91…` form (single prefix, not doubled).
  *Why / how to detect:* inspect the payload for these literals; any drift, missing fixed param, or `+91+91…` phone = fail (cf. C4 fixed-param integrity, C3/D17 phone double-prefix).
- [ ] All payload text values are English/Latin regardless of the spoken language (title, location, etc.).
  *Why / how to detect:* payload string fields contain no Devanagari/Kannada characters (cf. D3 script separation).
- [ ] After a successful `create_job`, the bot confirms with "हो गया।" / "ಹೋಯ್ತು." only on a real success result, then asks if there are more postings.
  *Why / how to detect:* the success line follows an actual `create_job` success result — never spoken when the tool never fired or errored (cf. C5 fabricated-success).

## 9. Tool-Call Silence & Terminal-Tool Sequencing

- [ ] No tool call is narrated — the bot never says "मैं update कर रही हूँ / record हो रहा है / system" or any fetch/lookup narration around a silent tool.
  *Why / how to detect:* scan spoken turns adjacent to each tool_call; any line describing the tool action or a waiting/"कृपया प्रतीक्षा करें" filler = fail (cf. B2; prompt "Tool calls are silent and internal").
- [ ] Phase 1 fires `update_job_status` per job (open/closed) as soon as the answer is clear — the terminal status call is never dropped before advancing.
  *Why / how to detect:* one `update_job_status` per discussed job with status matching the owner's answer (unsure → "open"); missing status calls before Phase 2/next job = fail (cf. C1 silent terminal tool dropped).
- [ ] Phase 2 `update_job_details` fires per turn with only the newly-provided fields — not batched across turns, never resending fields already present.
  *Why / how to detect:* each `update_job_details` payload contains only the just-answered field(s); already-present variables (e.g. `${city}` when passed) are not re-asked or resent.

## 10. Language, TTS & Script

- [ ] Numbers, money, and times are spoken as words, not digits/symbols — salary "बीस हज़ार रुपये", time "सुबह नौ बजे" (never AM/PM), phone digit-by-digit.
  *Why / how to detect:* scan spoken lines for raw digits, `₹`, AM/PM, DD/MM — any = fail (cf. D2).
- [ ] No "/" is voiced as "slash" in role/category labels; it is read as "या"/"ಅಥವಾ".
  *Why / how to detect:* transcript contains no "slash"/"स्लैश"/"ಸ್ಲ್ಯಾಶ್" in spoken role labels (cf. D6).
- [ ] Spoken output stays in-script (Devanagari for Hindi, Kannada script for Kannada) with simple Hinglish loanwords; no hard/Sanskritised administrative vocabulary.
  *Why / how to detect:* no Roman-Hindi in spoken lines; no tatsama jargon where a common loanword exists (cf. D1, D3).

## 11. Yes/No Gate Capture (register before advancing — all five gates)

- [ ] At each of the five gates — identity, availability (2 min), job freshness, new-vacancy, post-consent — the bot registers a clear yes/no (with a brief reflect-back) before branching or firing any tool.
  *Why / how to detect:* for each gate, transcript shows a captured owner answer before the next branch/tool; advancing on silence/unclear reply, or taking a branch the owner didn't choose, = fail (cf. D14).
- [ ] On an unclear/unheard/silent reply at a gate, the bot re-asks once ("माफ़ कीजिए... क्या यह हाँ है, या नहीं?") rather than guessing; a clear "I'm not sure" at freshness is handled as active/open.
  *Why / how to detect:* one gate re-ask line appears on ambiguous input; no silent branch-advance.

## 12. Closing (invite future postings)

- [ ] The bot ends only when the owner has nothing more, gives a one-line recap, and closes by **inviting future postings**, with the final word "Goodbye".
  *Why / how to detect:* final bot turn contains the future-posting invitation ("...कोई नई जॉब पोस्ट करनी हो, तो ज़रूर फोन करना" / equivalent Kannada) and ends on the literal token "Goodbye" (prompt Graceful Exit).
- [ ] Being an outbound bot, the close does not invite the employer to "call me back" as an inbound support line, and no promise of a specific callback time is made.
  *Why / how to detect:* closing turn frames future contact as the owner posting/updating jobs, not an inbound-support callback; no committed date/time (cf. D5 modality-leak class).
