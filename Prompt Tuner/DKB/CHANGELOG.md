# DKB Changelog

Every prompt edit to DKB is logged here. Entry format:

```
## YYYY-MM-DD — <short title>
- **Feedback/bug:** what prompted the change
- **Change:** what was changed
- **Files:** which files were touched
- **Ported from:** <source agent> (only for cross-agent ports)
```

## 2026-10-26 - Rewritten: one bot for both directions, built on the job board's own data
- **Feedback/bug:** Parth (26 Oct): DKB Signals had no inbound capability like KKB, and the prompt described the Signals tools as changes from the old ONEST backend ("What Changed", "the old fixed params are GONE", a "Signals note" on every input) with leftovers that contradicted what the bot now does ("Experience answers are conversation-only", "Do NOT send these in any tool call", `update_job` only for role, count or place). It also told owners a posting "expires today" (postings do not expire) and quoted a fixed "सोलह हज़ार से ज़्यादा एक्टिव जॉब सीकर्स".
- **Change:** New prompt in both languages (Hindi master, Kannada mirror), about 27 KB each instead of 70 KB:
  - **One bot, both directions** (no branching on who dialled; nothing said that is only true one way).
  - **New tool `get_employer`** (GET participant by phone): a silent lookup after the audio check returns the employer's live and draft postings and the business name, so an incoming call needs no campaign arguments. Campaign job arguments are no longer used.
  - **Step 4, a numbered per-posting procedure:** live postings get the still-needed question, then close or the six questions; drafts get name, number and the update that makes them visible, then the six questions. Each of the six questions (salary, area, qualification, experience, hours, benefits) has its own spoken line, one per turn, and the candidate count follows. Step 5 (new vacancies) comes only when every posting is finished.
  - **New callers and wrong callers:** an unknown business is asked its name; a job seeker calling the employer line is told politely it is for business owners.
  - **Tools:** `update_job` carries the manager's name and phone on every call; `phoneNumber` is required; every `job_id` has a UUID pattern; `get_employer`'s number is always "91 + the last ten digits"; company names in Latin letters; a failed update is never mentioned to the owner.
  - **Kept:** the automated-message rule, audio check, identity rules, consent ends the turn, name and number before posting, the failure and limit lines, the candidate count, script and number rules, listening rules.
- **Files:** `DKB/DKB Hindi Signals.md`, `DKB/DKB Kannada Signals.md`, `raya/toolspecs/dkb_get_employer.json` (new), `dkb_create_job*`, `dkb_update_job*`, `dkb_close_job*`, `dkb_candidate_count.json`; test copies `dkb-hi-signals-ab`, `dkb-kn-signals-ab` registered in `raya/agents.json`.
- **Verified on the Hindi test copy:** existing employer, live post and draft both finished (`008e0604`); both already complete (`9f7e523e`); new employer, no arguments, posted with the count "संतानवे लोग" (`51ea27d8`); job seeker turned away (`36ad1b48`). Kannada test copy: new employer end to end (`ba4ec361`), seeker turned away (`8234cf78`), one existing posting finished with all six questions (`6a111872`); the two-posting Kannada case still dropped one posting on `8e5a70fe` and was tightened after it: VERIFY-PENDING.
- **Rolled out:** Hindi prompt and tools to the live `dkb-hi-signals` agent; the inbound number 911204404271 moved to it from "DKB Hindi- New" (old backend, unreachable). Live-agent checks after rollout (both languages, 2026-10-26): Hindi existing employer `0b8f7439` and `8965ac46`, Kannada new employer posted end to end `22c620e8`, Kannada existing employer `6247dbb0` (draft made visible, all six questions saved, count). **Known limit, not fixed:** with two or more postings the bot reliably finishes one; the second is confirmed (still needed or closed) but its missing details are not always asked. Two redesigns of the Step 4 loop (counts at the end; details for one posting only) were tried on the test copies and did worse (`d481ea5d`, `496e2d74`, `eb0ab71c`, `11cff4e9`, `83c9ee8a`, `31a7a847`), so the rolled-out version is the one that tested best. Real inbound routing (a call from an ordinary phone to 911204404271) is not verified: Raya does not connect a call from one of its own numbers to another (`ea49b3e9`, `04031e43`).

## 2026-10-23 - Tell the employer how many people nearby want this kind of work
- **Feedback/bug:** Tushar (call, 23 Oct): after a post, tell the MSME how many candidates match, never who. The prompts said no such tool existed on Signals.
- **Change:** New tool `get_candidate_count(job_id, role)`: signals-search over seeker profiles, anchored on the posting just created, narrowed by ONE role word set, within 20 km; only `message.meta.total` is used (names come back masked and are never spoken). After a successful `create_job` the bot says once: "आपके आसपास बीस किलोमीटर के अंदर [count in words] लोग [role] का काम ढूंढ रहे हैं।" (Kannada: "ನಿಮ್ಮ ಸುತ್ತಮುತ್ತ ಇಪ್ಪತ್ತು ಕಿಲೋಮೀಟರ್ ಒಳಗೆ [count in words] ಜನ [role] ಕೆಲಸ ಹುಡುಕ್ತಾ ಇದ್ದಾರೆ."). Zero or an error: nothing about candidates. The three passages saying no candidate-count tool exists were rewritten. Probes: gzb machine operator 175, electrician 387; Dharwad fitter 846-864; a combined role ("Electrician | Fitter") returns 0, so the role is one kind of work.
- **Not done (blocked on Sanketika, asked 23 Oct):** applicant count and accept/reject by voice need on-behalf-of access to action/fetch and action/update-status; inviting top matches needs a product decision and cannot be tested on the live board without touching real seekers.
- **Files:** `DKB Hindi Signals.md`, `DKB Kannada Signals.md`, `raya/toolspecs/dkb_candidate_count.json`
- **Status:** Hindi `a8c1423d`: "हो गया। आपके आसपास बीस किलोमीटर के अंदर आठ लोग हेल्पर का काम ढूंढ रहे हैं।" Kannada `4162b710`: "ಆಯ್ತು. ನಿಮ್ಮ ಸುತ್ತಮುತ್ತ ಇಪ್ಪತ್ತು ಕಿಲೋಮೀಟರ್ ಒಳಗೆ ಎಂಟುನೂರ ಅರವತ್ತೊಂಬತ್ತು ಜನ ಫಿಟ್ಟರ್ ...". Zero case `155cc047`: count 0, the bot said only "ಆಯ್ತು.". Fixed along the way: `8081ff14` said the count in digits ("20 ... 2 ಜನ"), so the slot is now named for the spoken form ([ಜನರ ಸಂಖ್ಯೆ ಪದಗಳಲ್ಲಿ] / [लोगों की गिनती शब्दों में]); `3c44d30d` posted with the manager name "मालिक" (the caller said "मैं मालिक बोल रहा हूँ") and skipped the phone question, so the prompt now says a role word in any language is not a name: DEPLOYED, NOT VERIFIED (on the re-test the caller gave his name unasked). Also added: say the business name once in the caller's script, never followed by its English spelling (`9b143638`, `bfee5f43`), DEPLOYED, NOT VERIFIED.

## 2026-10-23 - Education, experience and benefits reach the post; post-call record follows tool results; no hold message on writes
- **Feedback/bug:** Since the 19 Oct schema fix, education reached 6, experience 3 and benefits 2 of 13 posts; test call `fddfcbfd` dropped all three although the owner gave them. Cause: three older lines survived the 19 Oct alignment and contradicted it ("Salary, qualification, experience, working hours, and benefits are NOT part of any tool call"; "conversational and not saved to any field on Signals"), and in Hindi four variable lines had their start replaced by a literal `\1` from a broken substitution, so `${salary}`, `${qualification}`, `${work_experience}`, `${work_experience_years}` were no longer described. Separately, Moksh (Raya, 20 Oct): `new_job_posted` should be decided from the create_job result, add a tool-results rule, add `posting_consent` to the output field list.
- **Change:**
  - Signals Hindi: restored the four variable lines. Signals Hindi and Kannada: the two contradicting lines now say every value the owner gave, including hours, benefits, salary, qualification and experience, is sent in the next `create_job` / `update_job` through its own parameter. Kannada: removed "[INTERNAL: no `update_job` call for these two]" (not in the master).
  - create_job description (both instances): "Salary/qualification/experience are NOT persisted" replaced by "sent in their own fields".
  - Output: Moksh's `new_job_posted` definition word for word, the "TOOL RESULTS ARE THE SOURCE OF TRUTH" block, `posting_consent` "Given" no longer requires the post to have succeeded; `posting_consent` added to `output_fields` and the `new_job_posted` field description updated, on all four DKB agents.
  - Raya's new per-tool switch `speak_hold_message` set to false on create_job, update_job and close_job (and on every write tool of every other bot).
- **Files:** `DKB/DKB Hindi Signals.md`, `DKB/DKB Kannada Signals.md`, `DKB/DKB Output.md`, `raya/toolspecs/dkb_create_job*.json`. Deployed to dkb-hi-signals, dkb-kn-signals (prompt, create_job tool) and dkb-hi-signals, dkb-kn-signals, dkb-hi-out, dkb-kn-out (output). Older DKB prompts left alone: their tools really have no hours or benefits fields.
- **Verified:** Kannada post `ed0cfc84`: create_job carried `minEducationalInstitute: School`, `candidateExperienceType: Fresher`, `benefitsOffered: ["Food Provided"]`, post live. Output: `fddfcbfd` and `ed0cfc84` new_job_posted Yes / posting_consent Given; `a3d86b5e` (employer said no) No / Declined. Hold: `fddfcbfd` create_job sent with no hold message. Hindi posts `bfee5f43` and `d76905df`: School / Fresher / Food Provided all sent, posts live (`a3d86b5e` is not evidence: the tester answered "no" to the post question, and the bot correctly did not post).

## 2026-10-19 - Aligned to the live job-board schema: posts now go live; close_job; owner name and phone; automated-message rule
- **Feedback/bug:** Vineela/Parth: profile and post updates failing since the Signals schema change. Checked against `bluedots-schemas` (`blue_dot/up-gzb/network.json`, updated 2026-10-15): `job_posting_1.0` REQUIRES `hiringManagerName` + `hiringManagerPhoneNumber` to go live, and now stores salary, education, experience, hours and benefits. DKB sent neither the phone field nor any of those, so all 30 posts on 2026-10-08 stayed hidden drafts. Aryan (2026-10-19): ask the hiring manager's name and phone; add the IVR/voicemail rule.
- **Change (Hindi + Kannada, prompts and tools):** `create_job` / `update_job` send `jobProviderName`, `hiringManagerName`, `hiringManagerPhoneNumber` (from a `hiringManagerPhone` parameter: the dialled number after "क्या कैंडिडेट इसी नंबर पर आपसे बात कर सकते हैं?", or the number the owner gives), `salaryMin`/`salaryMax`, `minEducationalInstitute`, `candidateExperienceType`, `workExperienceYears`, `workingHours`, `benefitsOffered`; `natureOfJob` limited to the schema's values. Every "no Signals slot / never persisted / DROPPED" passage rewritten. New `close_job` tool (POST `/api/v1/item/lifecycle`, action pause) for a filled posting; "removed" said only after it returns paused. The consent question now ends the turn (tool goes out only after the yes). Closing and bad-line lines no longer promise a callback; "समझ गया" -> "समझ गई". New top-priority automated-message rule (voicemail/IVR -> "Goodbye" only), also added to the legacy DKB Hindi/Kannada.
- **Files:** `DKB/DKB Hindi Signals.md`, `DKB/DKB Kannada Signals.md`, `DKB/DKB Hindi.md`, `DKB/DKB Kannada.md`, `raya/toolspecs/dkb_{create_job,update_job,close_job}{,_kn}.json`. Snapshot `pre-oct19-schema`.
- **Verified (live test calls on test numbers and our own test postings, all retired after):** post goes LIVE with every field, owner name and phone asked (Hindi `ee20caba`); filled posting paused by `close_job` and only then "हटा दी है" (Hindi `8c440eb8`); failed post gets the truthful failure line, r130 (Hindi `0407c2f6`); hold request gets "जी, ज़रूर।" r133 (`642038cc`, 13 Oct); Kannada bad-line close without a callback promise (`9890a31c`).
- **VERIFY-PENDING:** consent-ends-the-turn fix (posted early on `0407c2f6`, fix deployed after); Kannada new post and Kannada close_job; automated-message rule.
- **Verified later 2026-10-19:** Kannada post live after name, same-number and consent questions, each its own turn (`b724636c`); consent question ends the turn and nothing is posted without a yes (Hindi `5e3eb3a9`); voicemail answered with "Goodbye" only (`61edee70`). Test postings retired after the runs.

## 2026-10-13 - Tracker r130, r131, r133: false "done", false "removed", spoken stage direction
- **Feedback/bug:** tracker rows dated 12/10, grounded in 713 DKB Signals campaign calls (Oct 8).
- **Change (DKB Hindi Signals and DKB Kannada Signals):** `create_job` success line only when the result returned the item, with a truthful failure line and no further posting after `PROFILE_LIMIT_REACHED` (`121bebdf` said "हो गया" on two 409s); a filled or unwanted posting gets "ठीक है, मैंने नोट कर लिया कि यह पोस्टिंग अब नहीं चाहिए।" and the bot may never say it closed, removed or paused a posting (`06d0224d`, `4a597bc7`); hold requests get "जी, ज़रूर।" instead of an instruction to stay silent, which was spoken as "(Wait silently)" on 24 calls.
- **Not prompt (flagged):** r115 job_posting schema has no salary/qualification/experience fields; r116 no update/close API; r120 5-profile cap; r145 pitch drop-off (53% hang up on the 258-char pitch: proposed A/B of a shorter line, needs sign-off).
- **Files:** `DKB/DKB Hindi Signals.md`, `DKB/DKB Kannada Signals.md`. Snapshot `pre-oct13-tracker`.
- **Verified:** r131 on `8cf101ad`. r130 and r133: DEPLOYED, NOT VERIFIED (see session report).

## 2026-08-10 — Audio-check turn added ahead of Turn 1 (ported from the KKB pilot)
- **Feedback/bug:** Fleet-wide intro change: outbound bots were launching into their opening line while the person who just picked up was still saying "hello, who is this?" — so the opening was talked over. Requested that outbound bots first ask a short "can you hear me?" and only continue once the person confirms.
- **Change:** Added `## Turn 0 — Audio check` immediately before the existing `Turn 1 — Opening`, in all four DKB **outbound** prompts. It speaks only the audio check ("हैलो, मेरी आवाज़ आ रही है?" / "ಹಲೋ, ನನ್ನ ಧ್ವನಿ ಕೇಳಿಸ್ತಾ ಇದೆಯಾ?"), then waits; branches for confirm / cannot-hear (ONE slower repeat, then a polite close) / silence. `Turn 1` was renamed from "spoken immediately when call connects" to "spoken once the caller has confirmed they can hear you" — its business-owner question, the `${company_name}` / `${job_role}` branching, and every later turn are untouched. **Numbered Turn 0 deliberately** so the existing Turn 1 / Turn 2 / Turn 3 cross-references throughout the prompt stay valid — a renumber would have been a far larger and riskier diff. `say_hello` set to **false** on the four outbound agents.
- **Domain adaptation:** the shared block's "do NOT ask about work" line (seeker framing) was reworded for DKB to "do NOT ask who they are or about their business", since DKB's first real turn asks whether the caller is a business owner.
- **Files:** `DKB/DKB Hindi.md`, `DKB/DKB Kannada.md`, `DKB/DKB Hindi Signals.md`, `DKB/DKB Kannada Signals.md`.
- **Ported from:** KKB (pilot `KKB Placeholder Hindi Signals.md`, verified live on 4 calls before rollout).
- **Not ported (deliberate):** the returning-caller callback line and the Need Capture service-provider offer are **not** applied to DKB. Need Capture is meaningless here — it offers a job-seeker help finding work, and DKB's caller is the employer. The returning-caller line would need employer-specific wording ("we spoke about your job posting") and is left for a separate decision. The two DKB **inbound** prompts are also untouched: the caller dialled us, so an audio check is not warranted and disabling the greeting would risk dead air on pickup.
- **VERIFY-PENDING:** verified live on KKB Hindi Signals only. Per the never-extrapolate rule each DKB variant still needs its own live call — Hindi and Kannada, legacy and Signals.

## 2026-08-01 — DKB Signals: remove get_talent_insights + are-you-AI + fix Not-Available routing (CD1/CD4/CD5)

- **Feedback/bug:** (user, deep E2E pass) the DKB Signals bots still carried the ONEST/Dhiway `get_talent_insights` tool and its whole market-picture step, guarded as a "backend dependency" that could only ever return nothing on Signals — a step that could stall or invite fabrication. There is **no Signals talent-insights endpoint**, so keeping a stub was worse than removing it.
- **Change (CD1):** **removed `get_talent_insights`** from both DKB agents (tools now `create_job`+`update_job` only) and deleted the market-picture flow — Phase-3 now goes role+city → remaining fields → working-hours/benefits → consent → `create_job`, with no market lookup. Deleted the `## get_talent_insights` tool section, the `# Market Truth Delivery` section, the market-data branches of `# Error and Uncertainty Handling`, and the "after disappointing market data" silence line. Softened two persona lines that promised "market data / talent picture" to a grounded "help them post the job clearly." Guardrails added stating the tool is removed and the bot must never look up/speak a candidate count or salary benchmark. **(CD4):** added a short honest "are you a real person / machine / AI?" responder ("मैं एक AI assistant हूँ…" / Kannada twin).
- **Change (CD5):** live testing exposed a pre-existing bug — with `job_role="Not Available"` (new-vacancy campaign) the bot took the *existing-posting* branch and spoke "Not Available, Not Available vacancies…" aloud (C9 leak). Root cause: Turn-2 said "If job_role is **present**", but `"Not Available"` is a non-empty string. Rewrote the Turn-2 branch to key strictly on a REAL role value (Not Available/empty/NULL → new-vacancy pitch; a real title → existing-posting pitch), stated `company_name` presence ≠ a posting, and added a "never speak a Not Available value" guard to the Phase-1 freshness list. Both languages.
- **Files:** DKB/DKB Hindi Signals.md, DKB/DKB Kannada Signals.md (both languages mirrored); live agents fabda71d + 847a85e2 re-PATCHed (tools + instructions).
- **Test status:** ✅ **VOICE-VERIFIED both languages.** DKB Hindi (146dc70e, e2eec29a) + DKB Kannada (a02f61b3, 3177339f): market-picture step gone, `create_job` fires with a correct provider payload, are-you-AI answered honestly, and after CD5 the Not-Available new-vacancy routing is correct with no sentinel spoken. **Bonus:** the DKB-Kannada `create_job` D25 non-adherence (failed 4× on 2026-07-31) is now RESOLVED — dropping `get_talent_insights` left Phase 3 with only `create_job`, removing the tool-choice ambiguity (analyser C11 updated). Revert snapshots: raya/signals-expansion/e2e/snapshots/DKB *.pre-gti-removal.md + dkb-*.tools.pre-gti-removal.json.

## 2026-07-31 — DKB Hindi + Kannada Signals (new bots, migrated to Signals DPG — provider side)

- **Feedback/bug:** migrate DKB (the employer/provider bot) onto Signals as the final Signals-expansion phase. DKB is provider-side (posts/verifies jobs), so it required a separate provider-API discovery (raya/signals-expansion/DKB-provider-discovery.md).
- **Change:** created `DKB/DKB Hindi Signals.md` + `DKB/DKB Kannada Signals.md`. create_job now POSTs to Signals `/api/v1/admin/participant` (domain=provider, item_type=job_posting_1.0): company name -> top-level `name`, location -> `item_state.jobProviderLocation`, item_state = title/role/natureOfJob/positions/jobProviderLocation/hiringManager*; consent via compliance array. update_job = same endpoint by item_id. **SALARY/QUALIFICATION/STIPEND/EXPERIENCE have NO Signals slot — collected in conversation but NOT persisted (flagged in-prompt).** get_talent_insights NOT-YET-MAPPED on Signals -> kept conversational with an honest low-signal fallback (backend dependency for Srivatsa). Repurposed agents fabda71d (Hi) + 847a85e2 (Kn) with hand-built Signals create_job/update_job tools + get_talent_insights.
- **Files:** DKB/DKB Hindi Signals.md, DKB/DKB Kannada Signals.md (new); agents fabda71d, 847a85e2 repurposed.
- **Test status:** create_job CURL-GROUNDED (200, job item f6c3d7bb created with a fresh employer phone). DKB Hindi VOICE-VERIFIED (call `09a7b6c8`): employer greeting, Phase-1 verify -> Phase-3 capture, full field-collection, honest market-signal, create_job fires with correct Signals payload, D5 close. (Voice test used the seeker-registered tester phone so the response echoed the seeker participant — a test artifact; the fresh-phone curl-ground confirms clean job_posting creation.) DKB Kannada voice test running.
- **Open (backend deps, flagged):** requirements-style schema completeness (a description field may exist), get_talent_insights endpoint unmapped, job open/closed status has no confirmed slot, ${job_id} for updates must be a Signals item_id. Confirm with Srivatsa.


---

## 2026-07-30 — DKB (Hi+Kn): D5 outbound callback-invite close + D34 hold_message narration [overnight run]
- **Feedback/bug:** overnight static analysis + historical call `cf3fc048` — (D5) the outbound Graceful-Exit close invited a callback ("अगर कोई अपडेट देना हो… तो ज़रूर फोन करना" / "…ಖಂಡಿತ phone ಮಾಡಿ") — a modality leak for an outbound bot with no inbound support line; (D34) silent tools (`update_job_status`/`update_job_details`/`create_job`) carried a natural `hold_message` that the platform narrates aloud, announcing the "silent" write.
- **Change:** (D5) reframed the close so future contact is the team reaching out, not "call me back" (kept "Goodbye"); (D34) added a rule setting `hold_message` to an EMPTY string `""` on EVERY tool call (DKB uses no spoken "one moment" filler). Both are agnostic/spoken changes applied to Hindi (source) + mirrored to Kannada.
- **Files:** `DKB/DKB Hindi.md` (DEPLOYED dkb-hi-out, snapshot `pre-deploy-dkb-hi-out-2026-07-30_024108`) + `DKB/DKB Kannada.md` (DEPLOYED dkb-kn-out, snapshot `…024109`). Verify: DKB Kn employer-persona call pending. NOTE: DKB Kn `create_job` example uses a bare 10-digit phone (Hindi uses +91) — flagged to open-items (needs backend format confirmation), NOT changed here.

## 2026-07-22 — DKB (Hi+Kn): "open to freshers?" question was being skipped — decouple from qualification + make it a distinct ask
- **Feedback/bug:** Sheet row 66. Grounded in live call 1be4fc6c: the freshers-vs-experienced question never fired. Root cause: the completion step asked a COMBINED question ("इस role के लिए कोई minimum qualification या experience चाहिए?"), the owner answered with experience ("two years"), the agent captured it and moved on — so the distinct "क्या आप freshers को रखने के लिए तैयार हैं, या सिर्फ़ experience वाले candidates चाहिए?" ask (which the prompt DID contain) was short-circuited. (The prompt having the question was not enough — it was structurally unreachable when the owner volunteered experience.)
- **Change:** (1) Decoupled the qualification question from experience — it now asks qualification only ("कोई minimum qualification चाहिए — जैसे पढ़ाई या कोई सर्टिफिकेट?"), no longer absorbing the experience answer. (2) Strengthened the experience rule: ask the freshers-vs-experienced question as its OWN distinct question whenever ${work_experience} is "Not Available"; do NOT fold it into the qualification question, and do NOT skip it just because the owner mentioned experience while answering something else. Hindi source-of-truth, mirrored to Kannada (English rule identical; only the quoted qualification line adapted). Deployed dkb-hi-out + dkb-kn-out (echo-verified).
- **Files:** DKB/DKB Hindi.md, DKB/DKB Kannada.md

## 2026-07-20 — DKB (H+K): Yes/No Gate Capture — register the owner's answer before advancing
- **Feedback/bug:** Sheet row 26 — employers said yes/no clearly but the bot didn't register it and advanced anyway (wrong branch / skipped consent), causing frustrated drop-offs (calls 2465759, 3663530, 3664822).
- **Change:** Added a "Yes/No Gate Capture (Mandatory — Register Before Advancing)" section listing the five yes/no gates (identity, availability, job-freshness, new-vacancy, post-consent) and requiring the bot to capture + briefly confirm a clear yes/no before branching or firing a tool, with a single re-ask when no clear response is captured (an explicit "unsure" is itself a captured answer). (Analyser D14.)
- **Files:** DKB Hindi.md, DKB Kannada.md

## 2026-07-16 — DKB Inbound: drop `${country_code}` input assumption; always `+91`
- **Feedback/bug:** An inbound call has **no input variables**, so `${country_code}` is never passed — but the DKB inbound Input Variables section declared it as a caller-ID input "used for tool calls where required." This is a false-input assumption (C3-adjacent): if the model tried to build a phone value from a non-existent `${country_code}`, the `phoneNumber` lookup would be malformed/empty.
- **Change:**
  - Rewrote the `${country_code}` declaration to state it is **NOT a passed input** on an inbound call, must never be referenced in any tool payload, and that the country code is **always assumed `+91`** — the `phoneNumber` field is built from the caller's number with a literal `+91` prefix (pointing to `${contact_phone}`).
  - Strengthened the `${contact_phone}` declaration to require the `+91` prefix always (never the bare 10-digit number) and added the **don't-double-prefix guard** ("if `${contact_phone}` already includes a country code, do not double-prefix; the value must carry exactly one `+91`"), mirroring the KKB inbound precedent (`KKB Placeholder Inbound.md`).
  - **Audited all four tool payloads** (`create_job`, `update_job_status`, `update_job_details`, `get_talent_insights`): none references `${country_code}`; every `phoneNumber` already uses `${contact_phone}` "(in +91 form)" and the example payloads use literal `+91XXXXXX0249`. No payload change was needed — only the input-variable declaration was wrong.
  - **Untouched (verified byte-identical):** all fixed params (`sourceService: "ONESTAGENT"`, `eventType: "UPDATE_JOB"`/`"JOB"`, `app_instance: "up-postjob"`), enum values, field names, the `### 2026-09-07 — The legacy DKB pair was still SCRIPTING the government identity

- **Feedback/bug:** found by the overnight sweep's own detector, not by a report.
  `dkb_employer_integrity` flagged **G CLAIMED TO BE GOVERNMENT** on live call `4b2d7dca`
  (`dkb-hi-out`, 2026-09-04T18:41): the bot opened with *"जी, मैं **गवर्नमेंट एम्प्लॉयमेंट प्रोग्राम** की
  तरफ से कॉल कर रही हूँ"* and then said *"हम **गवर्नमेंट के साथ मिलकर** ब्लू डॉट पर आपकी जॉब पोस्टिंग्स
  लिस्ट करने में हेल्प कर रहे हैं"*.
- **Root cause:** tracker rows 4/56 ("remove 'government ki taraf se'") were applied to KKB, Maya and
  the DKB **Signals** pair on 2026-09-03. The **legacy** pair was missed, and it did not carry the
  never-government rule at all — so there was nothing to violate. Five scripted spoken lines in
  `DKB Hindi.md` and five in `DKB Kannada.md`, plus one in each Inbound file, named the government
  outright. This is not model drift: the prompt told it to say that.
- **Change:** replaced the identity in all four legacy prompts with the wording the Signals twins
  already use — शहर प्रशासन की एम्प्लॉयमेंट पहल / ನಗರ ಆಡಳಿತದ ಎಂಪ್ಲಾಯ್ಮೆಂಟ್ ಉಪಕ್ರಮ — 12 spoken lines in
  total, and added the never-claim-to-be-the-government rule to each. No other content touched.
- **Guard widened:** `raya/regression/fix_presence.py`'s `dkb-not-government` row was scoped to
  `DKB_SIGNALS`, which is precisely why it reported CLEAN while the legacy pair was broken. **A row
  that checks only the bots you happened to fix is not a guard.** It now covers all six DKB
  conversation prompts, and was self-tested by dropping the rule from `DKB Kannada.md` (caught) and
  restoring it (clean).
- **Files:** `DKB/DKB Hindi.md`, `DKB/DKB Kannada.md`, `DKB/DKB Inbound Hindi.md`,
  `DKB/DKB Inbound Kannada.md`, `raya/regression/fix_presence.py`.
- **Deployed:** `dkb-hi-out`, `dkb-kn-out`. The two inbound DKB targets have no prod uuid in
  `raya/agents.json`, so they are repo-only and cannot be deployed or tested from here.
- **Verification:** **DEPLOYED, NOT VERIFIED.** The prompt text is fixed and read back, but no call
  has yet been placed on the corrected legacy prompt. `4b2d7dca` is the call that proves the bug; the
  call that proves the fix does not exist yet.
- **Also corrected downstream:** these four files had already been pushed to the PUBLIC
  `Blue-Dots-Economy/AI-Agent-Prompts` repo earlier today, so an adopter forking it would have
  inherited a prompt that impersonates a government programme. Re-pushed.

### Contact context` memory block, and every spoken line.
  - Change is language-agnostic (payload/logic); applied to Hindi (source of truth) and mirrored **verbatim** to Kannada. The two edited declaration lines are byte-identical across H/K.
- **Files:** `DKB/DKB Inbound Hindi.md`, `DKB/DKB Inbound Kannada.md`

## 2026-07-15 — New agent: DKB Inbound (employer-inbound, Hindi + Kannada)
- **Feedback/bug:** Need an inbound variant of DKB — an MSME owner **calls in** to post or verify a job (rather than DKB calling out about an expiring posting). Built new, not an edit to the outbound files.
- **Change:**
  - **Intro reframed to inbound:** replaced the outbound turn-based screening ("are you the owner / your posting expires today / do you have 2 minutes / connect me to the owner") with an inbound welcome + AI-and-recording disclosure (said once, Turn 1) + a single discovery question ("क्या आप नई जॉब पोस्ट करना चाहते हैं, या किसी मौजूदा जॉब के बारे में बात करनी है?"). Kept a "who are you" handler and a non-employer/wrong-number close.
  - **Input variables:** removed all outbound job inputs (`${company_name}`, `${job_role}`, `${num_vacancies}`, `${job_id}`, `${city}`, `${salary}`, `${location}`, `${qualification}`, `${work_experience}`, `${work_experience_years}`). Kept caller-ID inputs `${contact_phone}` / `${country_code}` and the verbatim `### Contact context / {${contact_memory}}` memory-injection block.
  - **Phase Entry Rule → Inbound Routing Rule:** returning-vs-new fork is decided by the silently-read `${contact_memory}` (returning-owner opening + recalled roles) plus the owner's discovery answer — DKB has **no read/lookup tool**, so no tool fetch is used and none was invented. New-job capture (Phase 3) is the primary, fully tool-backed flow. Phase 1/2 (freshness/completeness) are kept but hard-gated on a `${job_id}` being available on the call (there is no `${job_id}` input inbound and `${contact_memory}.roles_posted` has no id); if none is available the agent must not fabricate one or call update_job_status/update_job_details — it re-captures via Phase 3.
  - **Preserved byte-identical:** all four tools and payloads (`get_talent_insights`, `update_job_status`, `update_job_details`, `create_job`), fixed params (`sourceService: "ONESTAGENT"`, `eventType: "UPDATE_JOB"`/`"JOB"`, `app_instance: "up-postjob"`), enum values, field names, Market Truth Delivery, Language/Script, TTS, Speech-Recognition, Prohibited, Consent, Error/Uncertainty, Silence, Emotional, Graceful Exit, Dignity. `phoneNumber` value is the inbound caller-ID `${contact_phone}` in `+91` form (consistent with the KKB inbound precedent and the C3 phone-format fix).
  - **Hindi is source of truth; Kannada mirrored** — agnostic logic/payloads verbatim, spoken lines reused from `DKB Kannada.md` for shared sections and adapted for the inbound intro/routing; region example values kept per convention (Hindi Ghaziabad/UP, Kannada Dharwad/Karnataka). Section headings verified identical across the two files.
- **Files:** `DKB/DKB Inbound Hindi.md` (new), `DKB/DKB Inbound Kannada.md` (new)

## 2026-06-29 — Full reconciliation: DKB Hindi brought up to Kannada
- **Feedback/bug:** A sync-check found DKB Kannada was a newer, stricter version than DKB Hindi (behavioral drift, not cosmetic). Kannada is the source of truth here. Bring Hindi up to parity (agnostic logic only; all Hindi spoken lines preserved).
- **Change (behavioral / bug fixes ported Kannada → Hindi):**
  - **Bug:** fixed the malformed `${phone(number}` → `${phoneNumber}` in all three tool payloads (update_job_status, update_job_details, create_job).
  - **Bug:** removed the redundant Phase 1 trailing block that used `status=active`/`status=closed` (the real values are `"open"`/`"closed"`) and had a typo ("thel"). Removed the duplicate Phase Entry "NO — no jobs present" bullet.
  - Added the global "Tool calls are silent and internal" CRITICAL note and per-phase `INTERNAL NOTE` headers (Phases 1–3).
  - Reframed Phase 1 owner-responses with `[INTERNAL: …]` discipline + CRITICAL ("call update_job_status for every job before proceeding").
  - Phase 2: added the `${city}` already-known rule (never re-ask the city of an existing job), per-answer internal `update_job_details` discipline, and fixed the payload field name `work_experience_years` → `workExperienceYears` in prose.
  - Phase 3 Step 3b: replaced the bullet rules with Kannada's mandatory numbered internal tool-call sequence + CRITICAL ("never call create_job before consent; never skip get_talent_insights").
  - Tool Usage Rules: tightened the "When to call" entries for get_talent_insights / update_job_status / update_job_details / create_job ("never announce", consent guards); "queries" → "parameters".
- **Deliberately NOT changed (per fragility constraint):** Hindi spoken lines; region-appropriate example values (Ghaziabad/UP vs Kannada's Dharwad/Karnataka); language-specific rules ("plain spoken Hindi", Devanagari script rules); Hindi's slightly richer graceful-exit guidance. Residual differences are cosmetic (backticks, line-wrapping) or correct language differences — behavior is now in parity.
- **Files:** `DKB/DKB Hindi.md`

## 2026-06-29 — Add memory injection block
- **Feedback/bug:** Memory is enabled for DKB (memory prompt exists), but the conversation prompts were missing the required `### Contact context` injection block.
- **Change:** Added the exact language-agnostic block (`### Contact context` / `Here is the caller context:` / `{${contact_memory}}`) at the end of the Input Variables section in both language files. KKB and Maya already had it.
- **Files:** `DKB/DKB Hindi.md`, `DKB/DKB Kannada.md`

## 2026-06-29 — Initial system setup
- **Feedback/bug:** Maintenance system bootstrap.
- **Change:** No prompt changes. DKB already has the complete set (Hindi, Kannada, Memory, Output) and serves as the reference implementation for the new skills' anatomy docs.
- **Files:** none

## 2026-09-08 (night) — VERIFIED: three fixes proven on one call, with a clean before/after

**`b187ffeb`** (2026-09-08 16:04 UTC, `dkb-hi-signals`, fixture `dkb-latin-business-name.json` with
`company_name: "VANS TRADING COMPANY"`, `num_vacancies: "3"`, `salary: "14000"`):

> हैलो! क्या आप **वैन्स ट्रेडिंग कंपनी** से बोल रहे हैं?
> … आपकी एक posting है — हेल्पर, **तीन** vacancies, सैलरी **चौदह हज़ार**। क्या यह अभी भी चालू है?

Against the pre-fix baseline on the **same bot and the same template**:

| | call | spoke |
|---|---|---|
| before | `8f2f0a98` (09-04) | "क्या आप **Shree Balaji Traders** से बोल रहे हैं?" |
| before | `0da5e1f9` | "क्या आप **VANS TRADING COMPANY** से बोल रहे हैं?" |
| before | `0eb3fc72`, `12dc1466`, … | "सैलरी **१२,०००**", "सैलरी **2000**" |
| **after** | **`b187ffeb`** | **"वैन्स ट्रेडिंग कंपनी"**, **"तीन vacancies, सैलरी चौदह हज़ार"** |

**Three things proven at once:**
1. the business name converted to Devanagari — the `"literal"`/`"VERBATIM"` disambiguation works;
2. `[num_vacancies]` and `[salary]` spoken in words — the point-of-use conversion works;
3. no `[company_name]`, `[job_role]` or `[salary]` marker spoken — `bracket_leak` **clean** on the call.

**One residual, found by the detector on the same call and fixed.** The bot said **"10वीं पास"** from
`qualification: "10th pass"` — Devanagari and transliterated, but the digit kept. `[qualification]`
was not in the conversion line; it is now, with `10th pass` → "दसवीं पास" worked through and the
Kannada twin in Kannada. 4 DKB prompts, deployed. **NOT VERIFIED** — needs one more dial.

**Note on the check that caught it:** `spoken_form` flagged exactly one thing on a call I had already
read and judged clean by eye. That is the argument for the detector existing.

## 2026-09-08 (evening) — the business name was going out in Latin, and the template's own `[company_name]` marker was being read aloud

- **Feedback/bug:** found while checking whether the KKB payload-conversion fix needed porting to
  DKB. It did, and worse. Two separate failures on the opener:
  - **The business name spoken in Latin.** `0da5e1f9`: **"हैलो! क्या आप VANS TRADING COMPANY से बोल
    रहे हैं?"** · `199a3b20`: **"YOGITA CLOTH EMPORIUM"**. Across the cached calls, `Shree Balaji
    Traders` alone appears 24 times in Latin inside Hindi speech, and 55-57 turns per Signals bot
    speak some raw value from their own arguments.
  - **The marker itself spoken.** `1131d79c`, `9cde78df`, `cb4f29f8`, `f391ab35`, `f2c4cd80` and
    `7992e013` asked owners **"क्या आप [company_name] से बोल रहे हैं?"** — the slot, not the value.
    `1131d79c` also recited **"आपकी एक posting है — [job_role], [num_vacancies] vacancies, सैलरी
    [salary]"**, and `f391ab35` read out **"[Proceeding to Phase 2]"** and an **"[INTERNAL:
    update_job_status called with status \"open\" for the job]"** note.
- **Root cause 1 — the opener says to speak the *literal* value.** *"where [company_name] is replaced
  with the actual literal value of `${company_name}`"*, and the Signals pair adds *"`[company_name]`
  is `${company_name}` **VERBATIM** — never another business's name."* Both lines were written to stop
  the bot naming a DIFFERENT business (`e2ce642a`, `68de2002`). Neither meant "read Latin letters
  aloud" — but that is what they say, and it is what the bot did.
  **Change:** the line now draws the distinction it never drew — *the same business, spoken in
  Devanagari; "literal" and "VERBATIM" mean you may not substitute a different business's name, they
  do not mean you read Latin letters aloud* — with `VANS TRADING COMPANY` → "वैन्स ट्रेडिंग कंपनी",
  `YOGITA CLOTH EMPORIUM` → "योगिता क्लॉथ एम्पोरियम", `Shree Balaji Traders` → "श्री बालाजी ट्रेडर्स"
  worked through, and the Kannada twins in Kannada script.
- **Root cause 2 — no prompt in the fleet had a rule about square-bracket markers** (analyser
  **D77**). They cover `*( )*` stage directions and tool payloads, both written after those specific
  failures; the brackets their own templates are built from were never mentioned. **Change:** one
  language-agnostic rule, byte-identical, added to all 20 conversation prompts and the slim rewrite —
  a bracketed marker is a slot to FILL and never words to say; if you cannot fill it, say the
  sentence without that part or a different sentence; the same goes for `*( )*` and any `INTERNAL`
  line.
- **Files:** the 4 outbound DKB prompts for the script fix; all 6 DKB prompts (and every other
  conversation prompt) for the bracket rule. Deployed; **live read-back confirms the bracket rule on
  19 of 19 conversation bots.**
- **Detector:** `raya/regression/bracket_leak.py`, 9/9 self-test, wired into
  `run_runtime_checks.sh`. It has **no allow-list and no info tier** — unlike the Latin-script checks,
  nothing bracketed has any legitimate reason to reach a caller. `fix_presence` rows
  `brackets-are-slots-not-speech` (21 bots) and `dkb-business-name-in-script` (4).
- **Verification:** **DEPLOYED, NOT VERIFIED** for both. DKB is outbound-only from a campaign, so a
  harness dial needs a `company_name` fixture — `raya/testcases/args/r5/dkb-no-company-name.json`
  covers the absent case; the Latin-script case needs a fixture carrying a real Latin business name.
- **Tooling bug fixed in passing:** `deploy_check.sh` labelled two transient deploy failures as
  "REFUSED (guard)" because it grepped for the word "placeholder", which matches the **filename**
  `KKB Placeholder Kannada Signals.md`. The pattern is now anchored to the deploy script's own
  refusal wording. `kkb-kn-signals` had genuinely not received the rule; it has now.

## 2026-09-08 — DKB was greeting business owners as "Not Available" (7 live calls)

- **Feedback/bug:** found while measuring the KKB written-value bug class (analyser **D73**). On
  **`564e1d45`** (2026-09-05), `343f8924`, `7427b12e` and `7db95662` the Hindi outbound bot opened with
  **"हैलो! क्या आप Not Available से बोल रहे हैं?"** — "are you calling from Not Available?" The Kannada
  twin did the same on **`be4ab8c3`** (2026-09-07), `061fb2cd` and `431a070a`:
  **"ನೀವು Not Available ನಿಂದ ಮಾತಾಡ್ತಾ ಇದ್ದೀರಾ?"**
- **Root cause — the opposite of what it looks like.** Across **137** cached DKB calls that carried a
  `company_name` argument the value was **always real; not once was it the string "Not Available"**.
  On the seven failing calls **no `company_name` was sent at all** — the args held only
  `contact_memory`. The emptiness test read *"If `${company_name}` is exactly 'Not Available' or is
  NULL"*: two arms, neither of which matches a **dropped** argument, which the platform delivers as the
  raw `${company_name}` token. With no arm matching, the model fell through to the present-value branch
  — *"where `[company_name]` is replaced with the **actual literal value**"*, and in the Signals pair
  *"`[company_name]` is `${company_name}` **VERBATIM**"* — and synthesised the placeholder wording it
  had just read three lines earlier in that same section. The prompt supplied both the missing branch
  and the words to fill it with. The `CRITICAL: Never say ... "not available" aloud` line directly
  below had been there the whole time and did not help: a prohibition next to a substitution
  instruction loses.
- **Change:** the test is now *"is exactly 'Not Available', is NULL, **or is ABSENT**"*, followed by the
  **AN UNSUBSTITUTED TOKEN COUNTS AS ABSENT** clause — which is the identical clause already declared
  two paragraphs above for `${contact_name}` in the legacy pair, so this is its missing twin rather
  than a new guard. With the absent case matched, the pass-through branch is unreachable when there is
  no value (ladder rung 3), instead of being forbidden and obeyed anyway.
- **Files:** `DKB/DKB Hindi.md`, `DKB/DKB Kannada.md`, `DKB/DKB Hindi Signals.md`,
  `DKB/DKB Kannada Signals.md` (inbound has no `${company_name}` input, so it is not affected). All
  four deployed and read-back verified.
- **Analyser:** pattern **D73**; `raya/regression/spoken_form.py` treats a placeholder spoken to a
  caller as always-blocking, in any language; `fix_presence.py` row `dkb-absent-company-name`.
- **Verification:** **DEPLOYED, NOT VERIFIED.** Fixture
  `raya/testcases/args/r5/dkb-no-company-name.json` reproduces the failing input exactly (only
  `contact_memory`, no `company_name`). Pass condition: the bot opens with
  **"हैलो, क्या आप एक बिज़नेस ओनर हैं?"** and the words "Not Available" appear nowhere in the transcript.
- **Also found, NOT fixed (flagged):** on `09a7b6c8` and `0c4fd526` (both 2026-07-31, Signals) the
  campaign genuinely sent `job_role`, `num_vacancies`, `salary`, `qualification`, `location` and
  `work_experience` all as the string `"Not Available"`, and the bot read the posting recap out as
  **"आपकी एक posting है — Not Available, Not Available vacancies, सैलरी Not Available।"** The recap
  template has a placeholder test for `job_role` only, not for the other slots. Old calls and a data
  problem at source, but the recap should refuse to speak a placeholder in any slot — left for a
  scoped edit rather than folded into tonight's change.
- **Also found, NOT fixed (flagged):** `DKB Kannada Signals.md` condenses the Hindi Signals prompt's
  six-heading "Signals Backend — What Changed" section into one, so the pair fails heading-count parity
  59/54. The **content** is present in the Kannada file (`jobProviderLocation` ×11, `job_posting_1.0`
  ×12, `sourceService`, `get_talent_insights`, `hiringManagerName`), so this is a structural difference
  and not a live gap — but it is unregistered, and it belongs in `raya/divergences.json` or the
  headings should be aligned.

## 2026-09-03 — Signals tool contract documented identically in both languages
- **Feedback/bug:** the static suite reports a section-count gap between DKB Hindi Signals and DKB
  Kannada Signals every run. Token-by-token comparison of the "Signals backend — what changed" block
  showed the Kannada file documenting three things the Hindi file never stated: the literal endpoint
  path, and that the old ONEST fixed params are gone.
- **Change:** additively documented both in Hindi — `POST /api/v1/admin/participant` on the
  `create_job` bullet, and a bullet recording that `sourceService`, `eventType`, `app_instance` and
  `orgName` are GONE and must never be sent (the API 400s on unknown properties). No spoken line, no
  flow logic and no payload template touched; `sourceService`/`eventType`/`app_instance` are now 1:1
  across the pair.
- **Files:** `DKB/DKB Hindi Signals.md`
- **Remaining (NOT a bug, flagged for a decision):** the two files still organise that block
  differently — Hindi uses six headed sections, Kannada one numbered block. Content parity holds on
  every checked token, so this is formatting, not missing rules. Aligning it means restructuring a
  live prompt's layout for a cosmetic reason, and self-approving a divergence-registry entry is not
  mine to do — so it is left as-is and reported.
- **Status:** deployed. Documentation-only; nothing spoken changed, so there is nothing to verify by
  call beyond DKB Hindi Signals' standing sanity run.

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

## 2026-09-09 — DKB Kannada read a Latin business name aloud, and read the recap back in digits
- **Feedback/bug:** live sweep call `3e9590d2` (dkb-kn-signals) carried
  `company_name: "Sharma Traders"` and the bot asked **"ನೀವು Sharma Traders ನಿಂದ ಮಾತಾಡ್ತಾ ಇದ್ದೀರಾ?"** —
  the right business, read out in Latin letters on a Kannada call. The Hindi twin passes the same
  test (`b187ffeb` → "वैन्स ट्रेडिंग कंपनी"). Separately, the same call spoke the working hours and the
  vacancy count correctly in words while collecting them ("ಒಂಬತ್ತು ಗಂಟೆಯಿಂದ ಸಂಜೆ ಆರು", "ಇಬ್ಬರು") and
  then read the pre-consent recap back as "12,000 ರೂಪಾಯಿ", "10ನೇ ತರಗತಿ", "9 ರಿಂದ ಸಂಜೆ 6".
- **Root cause, both halves is placement.** (1) The Hindi prompt carries an explicit clarification
  that "VERBATIM" is about WHICH business, not about which script — Kannada never got it, so the
  VERBATIM emphasis read as "do not change the letters". This is sync drift: the Kannada file has
  the guard that fixed the *substitution* bug (`9cf80aa5`, `829e5eb7`) but not the script
  clarification that came later. (2) The numbers-in-words rule is stated at the field templates, and
  the recap is a sentence the bot COMPOSES rather than a template it reads, so nothing carried the
  rule there.
- **Change:** mirrored the Hindi script clarification into `DKB Kannada Signals.md` and
  `DKB Kannada.md`, worded so the identity guard is untouched — "you may not substitute a DIFFERENT
  business's name, but that does not mean reading Latin letters aloud", with Kannada worked examples.
  Added a recap rule at the consent step of all 6 DKB prompts. `DKB Inbound Kannada.md` gets the
  recap rule but NOT the company-name one: inbound receives no `${company_name}` at all.
- **Files:** `DKB Kannada Signals.md`, `DKB Kannada.md` (company name); all 6 DKB prompts (recap).
- **Status:** DEPLOYED to dkb-hi-signals, dkb-kn-signals, dkb-hi-out, dkb-kn-out. DKB inbound has no
  Raya agent, so nothing to deploy there. **NOT VERIFIED.**

## 2026-09-09 — DKB announced a posting built from the number rule's own example values
- **Feedback/bug:** live sweep call `714ebfc0` (dkb-hi-out). Every job field arrived as
  "Not Available" — `job_role`, `salary`, `num_vacancies`, `qualification`, `job_id`, `location` —
  and `contact_memory` was the "No Old Memory" sentinel. The bot still opened with
  **"आपकी एक posting है — Helper, दो vacancies, सैलरी बारह हज़ार रुपये। क्या यह अभी भी चालू है?"** and then
  ran the whole existing-posting flow against a job that does not exist.
- **Root cause:** "दो" and "बारह हज़ार" are the two worked examples in the number rule printed on the
  line IMMEDIATELY BELOW that template (`2` is "दो", `12000` is "बारह हज़ार"). With no real values to
  substitute, the model took the nearest thing that looked like values — the illustrations. Same
  class as the KKB generic-trades leak: an example sitting at the point of use gets read as data.
- **Change:** a precondition ABOVE the template — check `${job_role}` first; if it is
  "Not Available", NULL, absent or an unsubstituted token there is NO posting to confirm, skip the
  step and go to Phase 3 — plus an explicit line that the values below are illustrations of the
  number rule, never the posting. Also added the missing script rule for `[job_role]` /
  `[company_name]` (Latin in, Devanagari/Kannada out), which no DKB prompt had stated: the same call
  said "Helper" in Latin letters. The English loanwords already in these lines ("posting",
  "vacancies") are deliberately left alone.
- **Files:** 4 DKB outbound prompts. The 2 inbound prompts have no single-job sample and receive no
  job arguments, so neither change applies to them.
- **Status:** DEPLOYED to all 4 live DKB targets. **NOT VERIFIED.**

## 2026-09-09 — three more from the live sweep: digits in the posting line, and an invented business
- **`290d8e5c`** — `salary: '14000'`, `num_vacancies: '3'`, and the bot said "हेल्पर, **3** vacancies,
  सैलरी **14,000** रुपये". The conversion rule was printed on the very NEXT line, with worked examples.
  The slots were named `[num_vacancies]` and `[salary]` — i.e. named for the raw argument — so the raw
  argument is what went in. **Renamed the slots for the spoken form** (`[वैकेंसी शब्दों में]`,
  `[सैलरी शब्दों में]`; Kannada `[ವೇಕೆನ್ಸಿ ಪದಗಳಲ್ಲಿ]`, `[ಸಂಬಳ ಪದಗಳಲ್ಲಿ]`), the same mechanism that fixed the
  location slot. The `[job_role]` script rule added earlier tonight DID hold on this call — it said
  "हेल्पर", not "Helper".
- **`bd60c6b0`** — no `company_name` was sent at all and the bot greeted the owner as
  "वैन्स ट्रेडिंग कंपनी". That is the worked example that had been printed directly under the greeting
  template (added earlier tonight as part of the script-conversion fix). With no real value to
  substitute, the model took the nearest business-shaped string on the page. The no-name branch was
  present and correct; it just lost to an adjacent example. **Kept the rule at the point of use and
  moved the examples out**; there is now no substitutable business name anywhere in any DKB prompt.
- **Same bug was already documented and recurring** — the prompt cited `2ea06509` doing exactly this,
  and the citation itself printed the leaking name. Removed (D81: a guard that prints the forbidden
  output supplies it).
- **Also cleaned:** the Kannada prompts carried a HINDI evidence citation containing the old template
  verbatim — both a language leak and a printed substitutable template. Rewritten as a description.
- **Files:** 6 DKB prompts. **Status:** DEPLOYED to all 4 live DKB targets. **NOT VERIFIED.**
- **Verified on the same sweep:** DKB Hindi business-name conversion works — `290d8e5c` said
  "वैन्स ट्रेडिंग कंपनी" for `VANS TRADING COMPANY`.
