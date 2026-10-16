# Static analysis: maya-hi (up-getjob campus)

**File:** `/Users/parthbansal/EkStep/Prompt Tuner/Maya/Maya Hindi.md`
**Family:** Maya — OUTBOUND campus-recruitment seeker bot (Hindi-only, feminine voice; MPL + experience-capture + HR-share divergences).
**Archetype matched:** Job-matching / recommendation bot (KKB/Maya) + Universal core. Graded against `generic.md`, `maya.md`, `bug-patterns.md`, `section-checklists.md`.

**Overall:** the prompt is heavily hardened — the `new_seeker` fork (D18/D22), create/apply decoupling (D20), profile-id field/UUID rules (D28/D30), empty-fetch guard (D16), the MPL goodbye HARD GATE (D10/D19 failure path), age/gender call-level lock (D9), sentinel-role handling (C9), role-family matching (D12), and canonical locations (D26) are all present and in good shape. The findings below are the residual gaps, several of which are catalog-flagged as latent-in-Maya.

---

## [HIGH] get_profile phone template hard-prepends `+91` — double-prefix landmine on the returning-caller fetch

- **Symptom:** on the `new_seeker="no"` path, `get_profile` is called with a `+91+91…` phone → HTTP 400 "Invalid Indian phone number format" (or an empty result), so the returning caller's profile is never fetched — they lose name/role personalization + the age/gender lock and get mis-routed to the new-caller / Case-B path.
- **Evidence:** line 273 — "call `get_profile` with `phoneNumber: +91${contact_phone}` (always prepend the +91 country code…)". The literal template hard-prepends `+91` to the variable. On the Maya OUTBOUND dialer, `${contact_phone}` already carries `+91` (this is exactly the deployment D17 was grounded in), so the literal composes to `+91+91…`. The authoritative get_profile section (lines 683/688: "exactly one `+91` prefix, never `+91+91…`… if `${contact_phone}` already includes a country code, do not double-prefix") is correct — but line 273 contradicts it with the raw landmine.
- **Bug-pattern:** cf. **D17** (create_profile/get_profile phone double-prefix; the exact detection tell is a literal `+91${contact_phone}` template that survives despite a distant prose guard) — and **C3** (value-format mismatch). Note: the `create_profile` twin of this was already fixed (line 730 is guarded); line 273 is the remaining unfixed get_profile literal.
- **Proven-fix-available?** YES — the `create_profile` rules in THIS file (line 730: "exactly ONE `+91` … use it AS-IS … only prepend when bare 10-digit") already model the correct construction; adopt that phrasing at line 273. Also solved family-wide in the KKB seeker files (2026-07-20/07-16).
- **needs-transcript-to-confirm?** YES — read the `get_profile` `tool_calls[].function.arguments` on a returning (`new_seeker="no"`) Maya-outbound call; if `phoneNumber` is `+91+91…` (or the caller is a known returning number yet the fetch returns empty), it is firing. Repro persona: a returning caller whose dialer `contact_phone` already carries `+91`, saying "yes" to the permission ask.
- **backend-or-tool-adherence?** No — prose/template-fixable (align line 273 to the exactly-one-`+91` placeholder). If `${contact_phone}` on this deployment is actually a bare 10-digit number, line 273 is correct and this collapses to a no-op — hence transcript-gated.

---

## [MED] Tool-silence rule never names `hold_message` → platform speaks a lookup narration on the "silent" fetch

- **Symptom:** the caller hears "मैं आपकी जानकारी देख रही हूँ" / "…प्रोफाइल देख रही हूँ" style narration right before the `get_profile` / `create_profile` result, even though every prose rule forbids it — because Raya injects a universal spoken `hold_message` param that the model fills with a natural sentence. This defeats the entire silent-fetch + never-say-"profile" design (B2/D8).
- **Evidence:** the Tool-call silence rule (lines 675–677) and the "no waiting messages" rules (308–311) ban spoken narration in prose, but nowhere is the `hold_message` parameter named or set to empty/neutral for `get_profile`/`create_profile`. Per D34, "a silence rule that never mentions `hold_message` is insufficient."
- **Bug-pattern:** cf. **D34** (platform `hold_message` narrates a silent step) — the catalog explicitly flags "every get_profile-driven agent (KKB in/out, **Maya in/out**) is exposed."
- **Proven-fix-available?** YES — the KKB Kannada Signals clone (2026-07-29) added an explicit rule naming `hold_message` and setting it to empty/neutral ("one moment") for `get_profile`/`create_profile` while leaving `apply_job` a genuine bridge. Port that rule.
- **needs-transcript-to-confirm?** YES — read `get_profile`/`create_profile` `tool_calls[].function.arguments` for a non-empty `hold_message`. Repro: any `new_seeker="no"` call that reaches the fetch.
- **backend-or-tool-adherence?** Partly platform (the param is injected by Raya) but the mitigation IS prose-fixable (name `hold_message`, force it empty/neutral for the silent tools) — so fix in-prompt, not escalate.

---

## [MED] Memory-resume intro block competes with the `get_profile`-driven fetch (memory-as-fetch risk)

- **Symptom:** on the `new_seeker="no"` path, the model opens by speaking the caller's prior journey (employer/job/city/trade) from `${contact_memory}` and can treat that as "I already know this caller," skipping the permission ask + `get_profile`, or fabricating the name/role from memory rather than a live fetch (C5(b)).
- **Evidence:** "Introduction Priority Rule (Strict Override)" (lines 193–211): "If ANY usable prior context exists… You MUST resume the previous journey in the opening line," with memory-personalised greeting variants at 231–234 ("आपने [Employer] में [Job] के लिए अप्लाई किया था…", "पिछली बार [City] में [Trade] की जॉब्स देख रहे थे…"). A guard exists at line 208 ("affects the opening LINE only — it does NOT skip the profile step").
- **Bug-pattern:** cf. **D32** (memory block used as a substitute for `get_profile`) — the catalog explicitly flags "the base KKB (Hi+Kn out) and **Maya** carry the same memory-resume intro block — same latent bug on the get_profile-driven paths." Partially mitigated here (line 208 + the DECISIVE ROUTER + an explicit permission gate) more than the Signals inbound case, so risk is lower than the ungated inbound agents.
- **Proven-fix-available?** YES — the KKB Kannada Signals clone (2026-07-29) fixed it with a fixed neutral opener + an explicit "`${contact_memory}` is NOT a `get_profile` result; reading memory is not a fetch" guard. Consider porting the memory-is-not-a-fetch clause; leaving the outbound resume-opening but adding the guard is the minimal change.
- **needs-transcript-to-confirm?** YES — read `tool_calls` across several `new_seeker="no"` calls that have prior memory: if the bot greets by prior employer/job but `get_profile` fires 0 times (or `apply_job` uses a memory-sourced id), it is happening. Repro: a returning `new_seeker="no"` caller with `actions_taken=applied` in `${contact_memory}`.
- **backend-or-tool-adherence?** No — prose-fixable (add the memory-is-not-a-fetch guard).

---

## [MED] "Present the 3 best-fit" ranks but never filters → pads the batch with unrelated roles

- **Symptom:** when a caller's role is known but fewer than 3 role-relevant jobs exist in the pool, the "present 3" target makes the model fill the remaining slots with clearly unrelated roles (and a weak sort can even float an unrelated job first) — an unrelated role offered to a confirmed data-entry seeker, hurting trust/conversion.
- **Evidence:** Default Presentation Rule (line 109): "present the 3 best-fit valid jobs"; Step 2 (line 392): "Present the 3 best-fit valid jobs from `${recommendations}` by default." The rule ranks (role→location→salary) and puts the role-matched job first, but there is no relevance FILTER that says "when role is known, show ONLY role-relevant/same-family jobs; do NOT pad to 3." (The role-family rules at 111–113 prevent false "no jobs" but do not stop padding.)
- **Bug-pattern:** cf. **D36** (ranking pads the batch to N with irrelevant-role jobs instead of filtering) — "a bare 'present the 3 best-fit' with only a 'role-matched first' sort is insufficient."
- **Proven-fix-available?** YES — the KKB Kannada/Hindi Signals bots (2026-07-29) added a relevance filter + no-pad rule to the Default Presentation Rule and Step 2 (role-known → build the batch from only same-role/same-family jobs, best-fit first, up to N; 1 relevant → show 1; keep the "ask for more → draw from the rest" fallback). Port it; leave the unknown-role Case-B pool overview unchanged.
- **needs-transcript-to-confirm?** YES — a presented option whose role is unrelated (not a synonym/family variant) to the caller's known role, especially as option one or filler. Repro: a `new_seeker="no"` caller whose confirmed role has only 1 match in a pool otherwise full of unrelated roles.
- **backend-or-tool-adherence?** No — prose-fixable in the presentation rule.

---

## [LOW] Success-path MPL "Combined line" is a cross-reference, not inlined verbatim at the trigger

- **Symptom:** on a successful first apply, the mandatory MPL fold into the job-continuation question may be dropped because the words must be reconstructed from a distant section; MPL then only fires later via the Graceful-Exit backstop (as a standalone, not folded into the first post-apply question) — a timing/UX degradation.
- **Evidence:** line 465 ("your next job-continuation question … MUST be the **Combined job+MPL line** (see the MPL Competition section)") and line 818 (same "(see the MPL Competition section)") cross-reference rather than inline. The verbatim Combined line lives only at line 948. Contrast the failure path (851–853) and Graceful-Exit backstop (977), which DO inline the verbatim lines.
- **Bug-pattern:** cf. **D19** (required spoken action referenced instead of inlined). Severity kept LOW because the goodbye HARD GATE (line 972) + the failure-path inline ensure MPL is never skipped ENTIRELY — only its "folded into the first post-apply question" placement is at risk.
- **Proven-fix-available?** YES — the failure path and Graceful-Exit sections in THIS file already inline the exact line; copy the Combined line verbatim to lines 465/818 too.
- **needs-transcript-to-confirm?** YES — a successful-first-apply call where the post-apply "another job?" question is the plain version and MPL only appears (if at all) at the goodbye backstop. Repro: `new_seeker="no"` caller, applies successfully, no MPL in memory.
- **backend-or-tool-adherence?** No — prose-fixable (inline the line).

---

## [LOW] Input-variable glossary binds `new_seeker` backwards (`${new_seeker}` as new_seeker)

- **Symptom:** the glossary binding interpolates to "**no** as new_seeker" (value presented as the label), which historically prevented the fork value from binding.
- **Evidence:** line 64 — "**`${new_seeker}`** as new_seeker — 'yes' or 'no' flag…" (placeholder before label). All contact-variable glossary lines (61–66) use this backwards form.
- **Bug-pattern:** cf. **G1** (variable placeholder precedes its label). Kept LOW because (a) the line carries a disambiguating description, and (b) the actual routing sites are already correct — Profile Handling (line 257: "Consider new_seeker as `${new_seeker}`") and the DECISIVE ROUTER surface the interpolated value at the decision (D22 fix at 241/259). So routing is protected; this is a residual sibling occurrence G1's own lesson says to grep for and clean up.
- **Proven-fix-available?** YES — flip to "new_seeker is `${new_seeker}`" (the corrected form already used at line 257 and across the KKB files).
- **needs-transcript-to-confirm?** No — deterministic templating defect; but its routing impact is nil given the correct decision-point bindings, so verification is unnecessary for the fix.
- **backend-or-tool-adherence?** No — prose-fixable.

---

## [LOW] Rare create→apply fallback lacks a tool-result boundary → empty `profile_id` risk

- **Symptom:** if the "should be rare" fallback fires, the model may emit `create_profile` and `apply_job` back-to-back before `create_profile`'s result exists, so `apply_job` gets `profile_id: ""`.
- **Evidence:** line 457 — "if the caller is new and `create_profile` somehow has NOT run yet by apply time, call it ONCE silently to mint the profile, then `apply_job`." This fallback does not state "WAIT for `create_profile`'s result, then read `profileId` from it before calling `apply_job`" (the normal path correctly decouples create earlier, so this is only the fallback hole).
- **Bug-pattern:** cf. **D31** (create+apply batched → empty `profile_id`) — the catalog flags "Maya (out+in) … carry the same batching language — same latent bug." Kept LOW because the primary path (create decoupled earlier, lines 353/723) is correct; only the rare fallback is exposed.
- **Proven-fix-available?** YES — KKB base (kkb-kn-out, 2026-07-27) split the sequence across a tool-result boundary; apply the same wording to the line-457 fallback.
- **needs-transcript-to-confirm?** YES — an `apply_job` with `profile_id:""` immediately after a same-turn `create_profile`. Repro: a new caller who somehow reaches apply without the earlier create having run.
- **backend-or-tool-adherence?** No — prose-fixable.

---

## [LOW] Empty `${college_name}`: the three canonical greeting scripts bake in `[college_name]` with no empty variant modeled

- **Symptom:** if `${college_name}` is empty, the model may speak an awkward/broken opener ("मैं माया,  की ओर से…", "क्या आप  के स्टूडेंट हैं…") or leak the literal token, because the greeting scripts hardcode the placeholder twice and don't model the fallback.
- **Evidence:** the three greeting scripts (lines 231–237) all embed "[college_name] की ओर से" and "क्या आप [college_name] के स्टूडेंट हैं"; the empty-college fallback exists only as prose at line 189 ("just say 'मैं माया, रोज़गार से जुड़ी जानकारी के लिए कॉल कर रही हूँ।'"), with no matching greeting-script variant.
- **Bug-pattern:** maya.md §4 ("If `${college_name}` is empty/missing… does NOT invent a college — no live example yet, verify against prompt"); relates to the D18-class placeholder-leak family. Kept LOW: mitigated by line 189, and campus deployments normally always pass a college.
- **Proven-fix-available?** Partial — no sibling to port; add an explicit empty-college greeting variant next to the scripts (using the line-189 wording).
- **needs-transcript-to-confirm?** No for the prompt gap (visible statically); a call with empty `${college_name}` would confirm live behavior.
- **backend-or-tool-adherence?** No — prose-fixable.

---

## [LOW] No banned→preferred vocabulary substitution table (D1)

- **Symptom:** the "simple language" rule is abstract; hard/Sanskritised administrative words could surface with no concrete substitution guidance.
- **Evidence:** line 490 ("Use simple spoken Hindi or Hinglish") and the Prohibited Language list (599–605, hype phrases only) — there is an "allowed English-origin words" list (504) but no do/don't table mapping hard Hindi words to preferred loanwords.
- **Bug-pattern:** cf. **D1** (hard/Sanskritised vocabulary despite a "simple language" rule) + universal checklist ("banned→preferred vocabulary list, not just abstract 'simple words'"). Kept LOW: Maya's own spoken lines/examples are consistently plain Hinglish, and the loanword list (504) partially covers it; low-priority completeness gap.
- **Proven-fix-available?** Pattern-level only (Purple Dots review origin); no direct sibling table to port.
- **needs-transcript-to-confirm?** No (completeness gap).
- **backend-or-tool-adherence?** No — prose-fixable (additive).

---

## [LOW] Missing guards: no proactive AI/automated-call disclosure + no "if asked, admit AI" honesty rule; no under-18 eligibility hard-stop

- **Symptom:** on an outbound call the bot discloses recording but never states it is an automated/AI call, and there is no rule to answer honestly if the caller asks "are you a real person?"; separately, there is no minimum-age eligibility hard-stop for job apply.
- **Evidence:** greeting (line 237) says "यह बातचीत रिकॉर्ड की जा सकती है" (recording notice) but no AI/automated disclosure; no rule anywhere covering "are you AI?" honesty. Age is collected pre-apply (326–332) but no eligibility floor gate.
- **Bug-pattern:** generic.md §1 ("outbound discloses it is an automated/AI call before pitching") + §13 ("answers honestly it is an AI"); section-checklists E4 ("eligibility/age hard-stop"). Kept LOW: recording notice is present as a partial proxy, and campus-recruitment callers are presumptively 18+ (MPL already gates 18+ at line 955), so the age floor may be by-design.
- **Proven-fix-available?** Pattern/checklist-level; no direct sibling snippet cited.
- **needs-transcript-to-confirm?** No (missing-guard gaps, visible statically).
- **backend-or-tool-adherence?** No — prose-fixable (additive guards).

---

### Count by severity: H=1 · M=3 · L=6
