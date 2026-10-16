# Static analysis: dkb-kn (up-postjob)

**File:** `/Users/parthbansal/EkStep/Prompt Tuner/DKB/DKB Kannada.md`
**Family:** DKB (employer / verification & capture bot), **outbound**, Kannada.
**Archetype matched:** *Employer / verification & capture bot (DKB)* + Universal core. All DKB-critical sections are present: turn-based intro + phase-entry routing, per-record freshness/completeness tool discipline, consent-gated create, market/insight delivery separated from phrasing, and a Yes/No Gate Capture section. The recently-fixed items (**D23** freshers-vs-experienced now a standalone question; **D14** Yes/No Gate Capture; **C9** company-name sentinel/placeholder guards) are correctly in place and are **not** re-flagged. **D26** (canonical location spellings) is not applicable — the catalog explicitly exempts DKB (no hardcoded location inventory).

No HIGH-severity defect (nothing that hard-breaks the call, skips a mandatory step, or violates consent). Three MED latent risks and three LOW hygiene/sync items follow.

---

## [MED] create_job / update_job_details example payloads use a bare 10-digit phone (no +91) — drift from Hindi + checklist requires single +91

- **Symptom (on a call):** `create_job` / `update_job_details` may be sent `phoneNumber` in a format the backend does not accept (bare 10-digit when the store keys on `+91XXXXXXXXXX`), so the write silently fails while the bot still says "ಆಯ್ತು." (done) — a posted-job-that-wasn't. The reverse (already-`+91` value reformatted to bare to match the example) is equally possible.
- **Evidence:** all three Kannada example payloads show a bare number — `update_job_status` `"phoneNumber": "XXXXXX0249"` (line 448), `update_job_details` `"phoneNumber": "XXXXXX0249"` (line 497), `create_job` `"phoneNumber": "XXXXXX0249"` (line 553). The Hindi twin shows **`+91XXXXXX0249`** in `update_job_details` (line 509) and `create_job` (line 565). The prose in both only says the number is "the caller's phone number passed into the call, which is `${phoneNumber}`" (lines 435/466/517) — it never specifies +91-vs-bare, so the example is the only format signal, and Kannada's is bare.
- **Bug-pattern:** cf. **C3** (value-format mismatch — create/lookup must use the identical key format the store expects) and **C4** (fixed-param/format integrity). DKB checklist §8 explicitly requires `phoneNumber` "in `+91…` form (single prefix, not doubled)". This is **not** a D17 double-prefix — the templates use `${phoneNumber}` directly, so there is no hard `+91` prepend to double.
- **Proven-fix-available?** Partially — the seeker bots' phone rules (KKB/Maya, per D17/D39) already mandate an exactly-one-`+91` E.164 construction; the same "compose to exactly one `+91XXXXXXXXXX`" discipline can be ported and the Kannada examples aligned to Hindi's `+91` form.
- **needs-transcript-to-confirm?** **yes** — pull a real DKB Kannada `create_job` call and read `tool_calls[].function.arguments.payload.phoneNumber` to see the actual format sent and whether the write 200s. Persona: any owner who consents to post a new vacancy (e.g. "electrician, Dharwad, 2 posts, ಇಪ್ಪತ್ತು ಸಾವಿರ, post ಮಾಡಿ").
- **backend-or-tool-adherence?** Partly backend-dependent (need the API's required phone format), but the prompt-side inconsistency + Hindi drift is prose-fixable — align the Kannada examples and add an explicit exactly-one-`+91` rule.

## [MED] Silence rule bans waiting-messages but never names the platform `hold_message` param → silent tools can still be narrated aloud

- **Symptom (on a call):** before a "silent" `update_job_status` / `update_job_details` / `create_job`, the caller hears a filler the model wrote into Raya's universal `hold_message` param — e.g. "ಒಂದು ನಿಮಿಷ, update ಮಾಡ್ತಾ ಇದ್ದೇನೆ" / "ಜಾಬ್ post ಮಾಡ್ತಾ ಇದ್ದೇನೆ" — narrating the exact action the prompt forbids ("Never say … 'ಈಗ record ಆಗ್ತಾ ಇದೆ' …").
- **Evidence:** Tool Call General Instructions (line 845) bans spoken waiting messages ("ದಯವಿಟ್ಟು ತಡೆಯಿರಿ" / "ಒಂದು ನಿಮಿಷ ಇರಿ") and the Conversation-Flow CRITICAL (line 210) bans tool narration — but **neither names `hold_message` nor sets it to empty** for the silent tools. Per D34's detection, a silence rule that never mentions `hold_message` is insufficient because the words come from the model populating a platform param, not from a spoken turn (grepping the prompt finds nothing).
- **Bug-pattern:** cf. **D34** (platform `hold_message` narrates a step the prompt says is silent). Generic checklist §10 covers the same class.
- **Proven-fix-available?** **Yes** — the **KKB Kannada Signals clone** (D34, 2026-07-29) already added an explicit rule naming `hold_message` and setting it to empty `""` (or a neutral filler) for tools that must not announce their action. Note the DKB nuance: DKB *bans* the neutral phrase "ಒಂದು ನಿಮಿಷ ಇರಿ" as a spoken waiting line, so the safe `hold_message` value here is empty `""`, not "one moment".
- **needs-transcript-to-confirm?** **yes** — read `tool_calls[].function.arguments.hold_message` on a real DKB call; a non-empty value = confirmed. Persona: any owner who confirms a freshness answer or consents to a post (triggers `update_job_status` / `create_job`).
- **backend-or-tool-adherence?** No — prose-fixable (add the explicit empty-`hold_message` rule for `update_job_status`, `update_job_details`, `create_job`). The platform param is the mechanism; the prompt is where the fix lands.

## [MED] Outbound bot's closing line invites a callback ("ಖಂಡಿತ phone ಮಾಡಿ") — modality leak

- **Symptom (on a call):** DKB is outbound (the bot dials the employer); the Graceful-Exit line tells the owner to "definitely call/phone" if they have an update or a new job — but there is no inbound support line for them to call, so the close is inbound-framed and misleading.
- **Evidence:** Graceful Exit (line 878): "ಧನ್ಯವಾದ. ಯಾವುದಾದರೂ update ಇದ್ದರೆ, ಅಥವಾ ಯಾವುದಾದರೂ ಹೊಸ job post ಮಾಡಬೇಕಿದ್ದರೆ, **ಖಂಡಿತ phone ಮಾಡಿ**. Goodbye" ("…definitely phone. Goodbye"). Same leak exists in the Hindi twin ("…तो ज़रूर फोन करना। Goodbye", Hindi line 896), so this is a shared/agnostic issue, not Kannada-only drift.
- **Bug-pattern:** cf. **D5** (modality leak — outbound bot invites callbacks). DKB checklist §12 explicitly grades this: "the close does not invite the employer to 'call me back' as an inbound support line."
- **Proven-fix-available?** No direct sibling port (the Signals/seeker fixes don't cover this closing line); apply the D5 fix direction — reframe the close so future contact is the *bot/center reaching out* or the owner posting via the platform, not "call me back," and keep the final token "Goodbye".
- **needs-transcript-to-confirm?** **no** — the offending line is fixed prompt text spoken at every graceful close; it will appear verbatim. (A transcript would only reconfirm what the prompt already mandates.)
- **backend-or-tool-adherence?** No — pure prose fix; because it is shared with Hindi, route through `/update-prompt` and sync both languages.

---

## [LOW] Silence / no-audio handling has no bounded graceful exit; no explicit voicemail/IVR termination

- **Symptom (on a call):** on sustained silence or a voicemail/IVR pickup, the bot issues "one gentle follow-up only" and then has no defined next step — it can hang or keep waiting rather than closing with "Goodbye". Generic checklist §3 and DKB checklist §3 want a *bounded* number of re-prompts then a graceful end, and explicit non-interactive-line recognition.
- **Evidence:** Silence Handling (lines 849-856) defines short-pause (wait) and longer-pause ("ನನಗೆ ಕೇಳಿಸಲಿಲ್ಲ, ನೀವು ಮತ್ತೊಮ್ಮೆ ಹೇಳಬಹುದಾ?") but no "if still silent → close gracefully"; there is no voicemail/answering-machine rule anywhere.
- **Bug-pattern:** no exact catalog code (closest is the generic §3 silent-caller / voicemail scenarios). Firing a write into the void is largely mitigated here because every tool sits behind a Yes/No Gate Capture that needs a clear human answer.
- **Proven-fix-available?** Partially — the seeker bots and generic checklist encode "bounded re-prompts → graceful exit"; a small "after one follow-up with no response, close with Goodbye; recognize a recording and terminate" rule can be added.
- **needs-transcript-to-confirm?** **yes** — a silent/voicemail persona run (no audio / answering-machine greeting) to confirm the bot loops or hangs instead of ending.
- **backend-or-tool-adherence?** No — prose-fixable.

## [LOW] `${phoneNumber}` used in three tool payloads but not declared in Input Variables

- **Symptom (on a call):** grounding gap — the number the write depends on has no presence/format rule; contributes to the phone-format ambiguity above.
- **Evidence:** `${phoneNumber}` appears only inside the tool sections (`update_job_status` line 435, `update_job_details` line 466, `create_job` line 517) but is absent from the Input Variables list (lines 143-166), which declares `company_name`, `job_role`, `num_vacancies`, `job_id`, `city`, `salary`, `location`, `qualification`, `work_experience`, `work_experience_years` only.
- **Bug-pattern:** cf. **C2** (identifier referenced in the body but not declared) — analogous for a variable rather than a tool.
- **Proven-fix-available?** N/A (declaration is a doc fix); pairs naturally with the phone-format finding above.
- **needs-transcript-to-confirm?** **no** — it is a static declaration gap (same in the Hindi twin, so not a Kannada-only drift).
- **backend-or-tool-adherence?** No — prose fix (declare `${phoneNumber}` with its format expectation).

## [LOW] Graceful-Exit sync drift: Kannada omits Hindi's "confirm nothing else + reflect what was covered" pre-close step

- **Symptom (on a call):** the Kannada close can end more abruptly than the Hindi one, without confirming the owner has nothing else or a one-line recap.
- **Evidence:** Hindi Graceful Exit (lines 892-894) says "Before ending: confirm there is nothing else they want to ask; briefly reflect what was covered in one natural line." The Kannada Graceful Exit (lines 874-880) has only "End only when the owner clearly has nothing more." and the closing line — the confirm/reflect instruction is missing.
- **Bug-pattern:** cf. **F** (cross-language drift — an agnostic instruction present in one language only). Flag for `/sync-check`, not to be reimplemented here.
- **Proven-fix-available?** Yes — mirror the Hindi agnostic instruction into Kannada (English instruction verbatim; no new spoken line needed beyond the existing close).
- **needs-transcript-to-confirm?** **no** — static drift, visible in the files.
- **backend-or-tool-adherence?** No — prose/sync fix.

---

**Count by severity:** HIGH=0, MED=3, LOW=3.
