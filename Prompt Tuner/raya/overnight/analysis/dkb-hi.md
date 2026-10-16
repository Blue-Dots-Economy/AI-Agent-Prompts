# Static analysis: dkb-hi (up-postjob)

Read-only pre-flight audit of `DKB/DKB Hindi.md` (outbound MSME employer / job-posting bot, backend `up-postjob`). Archetype matched: **Employer / verification & capture bot (DKB)** + Universal core. Grounded against `bug-patterns.md`, `section-checklists.md`, `generic.md`, `dkb.md`.

Tools in this prompt: `update_job_status`, `update_job_details`, `get_talent_insights`, `create_job`. No `get_profile`/`create_profile`/`apply_job` (this is an employer bot, not a seeker bot). Memory is enabled (`{${contact_memory}}` block present, verbatim — E3 OK). Consent gate on `create_job` present and correctly hard-gated (E2 OK). Five-gate Yes/No capture section present (D14 OK). Freshers-vs-experienced is now its own standalone step (D23 already fixed 2026-07-22 — not a finding). Company-name placeholder guard present (64da1027/b362bf46 regression guarded — not a finding).

No HIGH findings survived verification. The strongest issues are latent payload/narration defects that need a live call to confirm impact.

---

## [MED] Silent tools have no empty-`hold_message` rule → the platform filler will narrate the lookup/update/creation

- **symptom:** On any of the four silent tool calls the caller hears a spoken filler like "अभी अपडेट कर रही हूँ / जानकारी देख रही हूँ" — directly breaking the prompt's core promise that the owner never knows a tool ran. Most damaging on `create_job`/`update_job_status`/`update_job_details`, which are meant to be 100% silent.
- **evidence:** The prompt's silence discipline is stated only as prose banning spoken narration — line 219 ("Tool calls are silent and internal … Never say things like 'मैं system update कर रही हूँ'"), per-tool "Never announce this call to the owner" (lines 424, 444, 470, 476, 528), and Tool Call General Instructions line 861 ("Never respond with a waiting message like 'कृपया प्रतीक्षा करें'"). **None of these names the `hold_message` parameter or sets it to `""`.**
- **bug-pattern:** cf. **D34** (platform `hold_message` narrates a step the prompt says is silent — the words come from the model populating a universal Raya tool param, not from a spoken turn, so a prose "no narration" ban does not stop it). Also generic checklist §10, DKB §9.
- **proven-fix-available?** Yes — **the KKB Kannada Signals clone (2026-07-29)** added an explicit rule naming `hold_message` and forcing it empty for silent tools. Port that: list `update_job_status`, `update_job_details`, `get_talent_insights` (silent), `create_job` and set `hold_message=""` (or a neutral "एक मिनट" that reveals nothing). D34 note explicitly flags "every get_profile-driven agent is exposed — the platform param is universal," and DKB is exposed for the same reason.
- **needs-transcript-to-confirm?** No to prove the gap (structural, and D34 is a confirmed live class); **yes** to prove it is firing on DKB — read `tool_calls[].arguments` for a non-empty `hold_message` on any DKB tool. Reproduce: any Phase 3 create flow (owner posts one job) — inspect `create_job`/`get_talent_insights` args.
- **backend-or-tool-adherence?** Prose-fixable at the tool-config level (set the param), i.e. a prompt/config edit — not a backend defect.

---

## [MED] No "payload values must be English/Latin" rule on `update_job_details` (and `update_job_status`) → Devanagari can leak into the payload

- **symptom:** In Phase 2, when the owner supplies a missing field for an active job (e.g. work location or role), the model may write the spoken Devanagari value into the `update_job_details` payload — `title:"इलेक्ट्रीशियन"`, `jobProviderLocation:"गाज़ियाबाद"` — instead of the English/Latin form the downstream store expects.
- **evidence:** The English-only payload rule is stated per-tool for `get_talent_insights` (line 438 "All tool call parameters must be in English") and `create_job` (line 585 "All text field values must be in English in the payload"), but the `update_job_details` section (lines 474–522) has **no** such rule, and there is no global payload-script rule in Language & Script Rules (620–641, which only governs *spoken* output = Devanagari). `update_job_details` carries free-text fields (`title`, `jobProviderLocation`, qualification fields) that Phase 2 collects by voice.
- **bug-pattern:** cf. **D3** (script separation: Devanagari leaking into API payloads) / **C4** (enum/field integrity). Universal checklist "payload = English/Latin" line.
- **proven-fix-available?** Yes — the same English-only clause already present on this prompt's own `create_job` (line 585) and `get_talent_insights` (line 438); mirror it onto `update_job_details`. (`update_job_status` only sends jobId/phone/status enum, so lower risk, but add for parity.)
- **needs-transcript-to-confirm?** Yes — persona: an existing active job missing location/qualification; owner answers in Hindi (e.g. "गाज़ियाबाद, industrial area"). Check the `update_job_details` `arguments` for Devanagari in `title`/`jobProviderLocation`.
- **backend-or-tool-adherence?** Partly tool-adherence (model may already Latinize), but the prompt gap is real and prose-fixable — add the rule.

---

## [MED] `${phoneNumber}` not declared in Input Variables + inconsistent phone format across the three payload examples

- **symptom:** The phone value sent on writes is inconsistent: `update_job_status` may go out as a bare 10-digit number while `update_job_details`/`create_job` go out `+91`-prefixed. If the backend keys on the `+91…` E.164 form, the bare-number status update silently fails (a dropped terminal write, no error surfaced to the owner).
- **evidence:** Every tool payload sources phone from `${phoneNumber}` (lines 448, 480, 531), but `${phoneNumber}` is **not listed** in the Input Variables section (lines 144–168). The example payloads disagree: `update_job_status` shows `"phoneNumber": "XXXXXX0249"` (bare 10-digit, no +91 — line 463), while `update_job_details` (line 509) and `create_job` (line 565) show `"+91XXXXXX0249"`. DKB checklist §8 mandates `phoneNumber` in `+91…` single-prefix form.
- **bug-pattern:** cf. **C3** (value-format mismatch; create/read must use the same key format) / **C4** (fixed-param integrity). Note: `${phoneNumber}` is the *correct* DKB variable name (it was fixed from `${phone(number}` on 2026-06-29 per the C3 catalog entry), so this is a format/consistency defect, **not** an unbound-variable / double-prefix (D17) defect.
- **proven-fix-available?** Partly — the repo's standing "exactly one `+91` prefix" convention (D17 family) applies; make all three examples consistent with the `+91…` single-prefix the checklist requires, and declare `${phoneNumber}` in Input Variables so its format is pinned in one place.
- **needs-transcript-to-confirm?** Yes — persona: existing-jobs campaign, owner says one job is closed → inspect the `update_job_status` `arguments.phoneNumber` format and whether the write succeeded.
- **backend-or-tool-adherence?** The "does bare 10-digit fail?" half is **backend** (depends on what the endpoint accepts) — escalate/confirm there. The example inconsistency + missing declaration are prompt-fixable.

---

## [LOW] Voicemail / IVR / no-audio not recognized; silence handling is not bounded-then-exit

- **symptom:** On an outbound dialer, hitting an answering machine / IVR / dead air, the bot has no rule to recognize a non-interactive line and terminate within a couple of turns; on repeated silence it offers "one gentle bridge" but never states "then end gracefully," risking a stalled or looping call.
- **evidence:** Silence Handling (lines 865–872) has only "Longer pause: Use one gentle bridge only" with no bounded-reprompt-then-graceful-exit and no voicemail/answering-machine detection. Generic §3 and DKB §3 both require this explicitly.
- **bug-pattern:** No dedicated catalog code; maps to generic checklist §3 and DKB §3 (voicemail/no-audio → terminate, no `create_job`/`update_*`).
- **proven-fix-available?** Yes — the seeker/DKB families have silent-caller + voicemail handling patterns (checklist grounds it in DKB 74bd1610 Hi / 0460001a Kn); adopt the bounded-reprompt + non-interactive-line exit.
- **needs-transcript-to-confirm?** Yes — voicemail/no-audio persona (recorded greeting then beep, or total silence); confirm no `create_job`/`update_*` fires and the call ends as Early Disconnect. (No fabricated write is likely since `create_job` is consent-gated — that limits severity to a wasted call, hence LOW.)
- **backend-or-tool-adherence?** Prompt-fixable (add the handling section).

---

## [LOW] No handlers for off-topic redirect, "are you a real person/AI?" mid-call, or "do not call me again"

- **symptom:** If the owner goes off-topic, asks mid-call whether it is a bot, or says "don't call me again," there is no explicit rule to redirect briefly / self-identify honestly / acknowledge-and-close. The do-not-call case is the sharpest edge for an outbound bot (a pitch turn after a stop request is a compliance miss).
- **evidence:** The only AI self-identification is the one-time Turn-3 disclosure (line 83) and the pre-confirm "who are you" purpose line (lines 113–118); there is no mid-call are-you-AI handler, no off-topic-redirect rule, and no do-not-call handler. Guard sections present are Prohibited Language (803), Emotional (876), Dignity (902) — none covers these.
- **bug-pattern:** cf. **E4** (guard sections thin/absent); generic §2 (stay on task off-topic), §13 (are-you-AI / do-not-call / wrong-person).
- **proven-fix-available?** Yes — the seeker bots + DKB scenario catalog have anti-AI (1283e4a9) and do-not-call handling patterns to port.
- **needs-transcript-to-confirm?** Yes — personas: (a) owner asks "तुम इंसान हो या मशीन?" mid-flow; (b) owner says "दोबारा कॉल मत करना." Confirm the bot self-IDs / closes without pitching further.
- **backend-or-tool-adherence?** Prompt-fixable (add guard rules).

---

## [LOW] Female persona has no explicit feminine-verb rule, and one line uses a masculine form

- **symptom:** A caller occasionally hears a masculine verb form from the female persona; the "same" Step-3a line also appears in two different grammatical forms across the prompt.
- **evidence:** Persona is an explicitly **female** voice guide (line 3), but there is **no** "feminine verb forms only" rule (unlike Maya's D4 divergence). Concrete leak: line 99 `"समझ गया। Goodbye"` is masculine ("समझ गया" — should be "समझ गई"). Drift: Turn 3 says "…हेल्प कर रही हूँ" (line 90) while the Phase Entry Rule (line 188) and Step 3a (line 344) say "…हेल्प कर रहे हैं" — the same line in two forms (and line 90 mixes "हम … कर रही हूँ").
- **bug-pattern:** cf. **D4** (voice-gender inconsistency).
- **proven-fix-available?** Yes — **Maya** carries the explicit feminine-voice rule (Hindi feminine verb forms only); port that rule and fix line 99 to "समझ गई".
- **needs-transcript-to-confirm?** No — the masculine form at line 99 and the drift are visible in the prompt text; a call is not required to see them.
- **backend-or-tool-adherence?** Prompt-fixable.

---

## [LOW] `get_talent_insights` "do not announce" (Step 3b) contradicts the mandated bridge line (Market Truth Delivery)

- **symptom:** Two instructions pull opposite ways on whether to speak before `get_talent_insights`, so the bot's behavior there is unstable (silent one call, spoken bridge another).
- **evidence:** Phase 3 Step 3b step 2 says `[INTERNAL: immediately call get_talent_insights … do not announce]` (line 367) and the tool section repeats "Never announce this call to the owner" (line 424), while Market Truth Delivery says "Before calling get_talent_insights, **say exactly:** 'ठीक है, मैं अभी [location] में [role] के लिए eligible candidates देखती हूँ।'" (lines 592–593). The Step-3b sample (lines 385–388) omits the bridge, matching the "do not announce" side.
- **bug-pattern:** cf. **A4** (intra-prompt contradiction); the bridge mildly resembles **B2** (narrating a lookup) but for an employer bot a "let me check the numbers now" lead-in is a legitimate value-delivery bridge, so impact is low — the issue is the literal contradiction to reconcile.
- **proven-fix-available?** Internal to this prompt — reconcile the two sections (either sanction the bridge and scope "do not announce" to naming the tool/API, or drop the bridge).
- **needs-transcript-to-confirm?** No — the contradiction is textual.
- **backend-or-tool-adherence?** Prompt-fixable.

---

## [LOW] Phase-3 sample has an orphaned line interleaving the market-delivery branches with the sample dialogue

- **symptom:** The market-picture branches and the walkthrough dialogue are spliced together, so it is unclear what the bot should say; the model may reproduce the stray fragment.
- **evidence:** Lines 390–396: the "supply_density is Low" branch ends, then line 395 `कितनी vacancies हैं?"` appears with a closing quote but no opening quote, immediately followed by `User: "दो।"` — the sample dialogue resumes mid-branch-list.
- **bug-pattern:** No catalog code; example/formatting hygiene (relates to E1 — examples must model the flow cleanly).
- **proven-fix-available?** Internal cleanup (separate the three market-delivery branches from the continuing sample dialogue).
- **needs-transcript-to-confirm?** No — visible in the prompt.
- **backend-or-tool-adherence?** Prompt-fixable.

---

## [LOW] `${contact_memory}` block present but its use is unguided; `[company_name]` bracket sits inside the spoken line

- **symptom:** (a) Memory is injected with no rule on how DKB uses it or a guard that it is background-only — low fabrication risk here because Turn 1 is a fixed company-confirm, but unguided. (b) The company-name spoken line embeds the bracket token, the exact shape that regressed before.
- **evidence:** (a) `{${contact_memory}}` block at lines 170–173 with no accompanying usage/guard rule. (b) Turn 1 line 59 `"हैलो! क्या आप [company_name] से बोल रहे हैं?"` uses the `[company_name]` placeholder inside the quoted line.
- **bug-pattern:** (a) cf. **E3** (block present — satisfied) / **D32**-adjacent (memory-as-substitute, but DKB has no fetch so risk is low). (b) cf. **C9**/**D18** placeholder leak — but the CRITICAL guard at line 63 ("Always substitute the real value; never say 'company name'") **is present**, so this is residual risk only.
- **proven-fix-available?** The guard already exists (line 63); optionally add a one-line "contact_memory is background context only" note (mirrors the seeker bots' memory-is-not-authoritative guard).
- **needs-transcript-to-confirm?** No for the structural observation; a call could confirm the guard holds. Persona: any resolved-company call — confirm the literal "[company_name]" is never spoken.
- **backend-or-tool-adherence?** Prompt-fixable; largely already handled.

---

### Count by severity: H=0 M=3 L=6
