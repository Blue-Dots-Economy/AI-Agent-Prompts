# Static analysis: kkb-hi-signals (Signals)

**File:** `/Users/parthbansal/EkStep/Prompt Tuner/KKB/KKB Placeholder Hindi Signals.md`
**Archetype matched:** Job-matching / recommendation bot (KKB), **Signals** backend, get_profile-driven (always-fetch, no `new_seeker` fork), outbound-dialed (receives `${recommendations}` + contact input vars).

**Scope note.** The three items called out as fixed today are present and coherent: **D37 live-item selection** (lines 366-368, 776-788, 841, 861), **D40 location-before-create** prose gate (line 812; the durable lever is the *tool schema* `required`, not prose — see note under L-items), and the **role-update offer** (line 213). The `new_seeker`/G1 fork bugs are gone (design removed the branch variable, line 194). `requirements_snapshot` is correctly absent from `apply_job` (line 863). D31 create→apply batching is guarded (lines 374-375, 839, 875). D34 `hold_message` and D32 memory-as-fetch are both handled (lines 177, 198, 755). This audit is for what remains.

---

## [HIGH] create_profile/update_profile phone: bare-10-digit vs 12-digit contradiction → wrong-user write / duplicate profile

- **Symptom:** On a new-caller apply, `create_profile` is told to pass a **bare 10-digit** phone. With the tool template that "adds only the leading `+`" (`"+{{phone}}"`, stated at line 832), a 10-digit value composes to `+<10digits>` — a malformed/wrong E.164 number. Signals then resolves the *wrong* participant or **mints a NEW user** (`user_existed:false`), so nothing the bot gathered lands on the caller's real record; a later `update_profile` 403s `ITEM_NOT_OWNED_BY_USER`. Duplicate/orphan profiles, silent data loss.
- **Evidence:** Line 818 (create_profile `## Payload`): "`phone` — the caller's **10-digit** mobile number, digits only, **no country code and no `+`** (required)." Update_profile example line 931: `"phone": "<10 digits>"`. Both are directly contradicted by line 832 (create_profile Allowed-values): "`phone`: ALWAYS the caller's **12-digit** number = `91` + `${contact_phone}` … the tool adds only the leading `+`. **Do NOT pass the bare 10-digit number (it would resolve the wrong record)**." Three spots: 10-digit twice (818, 931), 12-digit once (832). The most prominent field-spec (the `## Payload` list) carries the wrong value.
- **Bug-pattern:** cf. **D39** (Signals write phone → new user / 403), **C3** (value-format mismatch; write and lookup must use identical format), **A4** (intra-prompt contradiction).
- **proven-fix-available?** Yes. The correct 12-digit convention is already in THIS file at line 832, and **D39 was fixed across the Signals bots (Kn + Hi) on 2026-07-29**. Fix is surgical: make line 818 and the update_profile example (line 931) read the same 12-digit `91`+number value as line 832.
- **needs-transcript-to-confirm?** No to fix the contradiction (static, self-refuting — line 832 explicitly says the 10-digit form is wrong). A transcript confirms which branch the model followed: read `create_profile`/`update_profile` `tool_calls[].arguments.phone` for a 10-digit value, `user_existed:false` on create, or a 403 on a follow-up update. Repro persona: brand-new caller (empty `get_profile`) who applies → `create_profile`, then Phase-2 → `update_profile`.
- **backend-or-tool-adherence?** No — prose contradiction, prose-fixable (align the two payload specs + the example to 12-digit).

---

## [MED] Phase-2 post-apply examples contradict the Phase-2 rules + the write schema

- **Symptom:** The examples model behaviour the Phase-2 prose explicitly forbids, and models mimic examples over prose (E1). (a) Examples 2 and 5 ask **"अभी आप कोई काम कर रहे हैं, या पढ़ाई कर रहे हैं?"** (working/studying) — line 982 bans exactly this ("There is NO profile field for 'currently working / studying' — do not ask it"). (b) Example 1 announces the vague count **"एक-दो छोटी बातें"** where the rule (lines 970/973) demands an *exact* number that already covers every Phase-2 question. (c) Example 2 models an `update_profile` with **`totalYearsOfExperience: 3`** — a field that is **not** in the create/update schema (the schema field is the enum `workExperience`, lines 828, 921-925), so it would be ignored/rejected. Net effect: wasted turns, an unstorable question asked, a count that doesn't match, and a dead payload field.
- **Evidence:** Ban at line 982; working/studying asked at line 1267 (Ex 2) and line 1379 (Ex 5); vague count at line 1225 (Ex 1); non-schema field at line 1283 (Ex 2 note: `update_profile … totalYearsOfExperience: 3`).
- **Bug-pattern:** cf. **E1** (few-shot examples contradict the rules), **C3/C4** (non-schema field / wrong type in payload), **D10-adjacent** (exact-count rule).
- **proven-fix-available?** In-file — the correct Phase-2 scope (Gender-if-missing + granular location only) and the exact-count bridge already exist in prose (lines 964-982); repair the three examples to match. No sibling port needed.
- **needs-transcript-to-confirm?** No (static example-vs-rule/schema contradiction). A post-apply enrichment transcript would show the working/studying question firing. Repro persona: any successful apply that proceeds into Phase-2 enrichment.
- **backend-or-tool-adherence?** No — example prose, prose-fixable.

---

## [MED] Canonical new-caller create-consent line speaks "प्रोफाइल" aloud (D8)

- **Symptom:** On the new/draft path the bot says **"अप्लाई करने के लिए आपकी प्रोफाइल बनानी होगी …"** — the caller hears the internal term "प्रोफाइल". The prompt's own CRITICAL Profile Wording Rules call this a hard failure, and the bans list forbids "प्रोफाइल बना रही हूँ".
- **Evidence:** Consent ask at line 356 contains "आपकी प्रोफाइल बनानी होगी". Contradicts line 723 ("the word 'profile'/'प्रोफाइल' must NEVER appear in any seeker-facing turn, in any form") and the bans at lines 743-745. Example 1 already uses the profile-free phrasing at line 1217: "अप्लाई करने के लिए आपकी जानकारी दर्ज करके कंपनी के साथ शेयर करनी होगी — क्या इसके लिए आपकी सहमति है?"
- **Bug-pattern:** cf. **D8** (internal term "profile" spoken to the caller).
- **proven-fix-available?** Yes — the profile-free version is already in this file at Example 1 (line 1217); use it verbatim at line 356.
- **needs-transcript-to-confirm?** No (static — the canonical spoken line literally contains the banned word). Repro persona: any new-caller/draft apply that reaches the create-consent gate.
- **backend-or-tool-adherence?** No — prose, prose-fixable.

---

## [MED] get_profile literal `91${contact_phone}` — double-prefix landmine (D17)

- **Symptom:** If the dialer passes `${contact_phone}` **already carrying the country code**, the literal template `phone_number: 91${contact_phone}` composes to `9191…` → `get_profile` queries a wrong number → **empty fetch** → a returning caller with a live profile is misread as NEW → duplicate `create_profile` + re-gathered fields (and possible PROFILE_NOT_LIVE downstream). D17's lesson is that a literal `91`-prepend template can win over a prose "don't double-prefix" guard placed elsewhere.
- **Evidence:** Literal template at line 198 and line 763 ("`phone_number: 91${contact_phone}`"). The anti-double-prefix guard is **prose-only**, adjacent at line 767 ("if it already includes the country code, do not double-prefix").
- **Bug-pattern:** cf. **D17** (literal `91`-prepend template beats prose guard), **C3**.
- **proven-fix-available?** Yes — D17 was fixed in the Signals family by making phone compose to exactly one prefix. Adopt the "exactly one `91` — use as-is if already prefixed, prepend only if bare 10-digit" construction at the template itself, not only in prose. (Note the guard here is better-placed than the classic D17 cases, so this is lower-confidence than H1.)
- **needs-transcript-to-confirm?** Yes — read `get_profile` `tool_calls[].arguments.phone_number` to see what `${contact_phone}` actually contains on this deployment: bare 10-digit → no bug; already-`91` → double-prefix. Repro persona: any returning caller whose dialer number carries the country code.
- **backend-or-tool-adherence?** Partly — depends on the platform's `${contact_phone}` format; the prompt/template-side fix (compose exactly one prefix) is prose/template-fixable.

---

## [LOW] Outbound-bot closings invite callbacks — possible modality leak (D5)

- **Symptom:** Several closings invite the caller to reach out — "जब भी … बात कीजिए / call कीजिए", "आप खुद संपर्क कर सकते हैं". On an outbound bot (the input-variable model — `${recommendations}` + contact vars — implies outbound-dialed) this is inbound-framed; the generic + KKB checklists test for it ("expect 'the center will contact you'-style closing").
- **Evidence:** Lines 1112, 1146, 1315, 1340, 1344.
- **Bug-pattern:** cf. **D5** (modality leak / outbound invites callbacks).
- **proven-fix-available?** N/A until modality is confirmed (may be established KKB closing, and an inbound fallback number may legitimately exist).
- **needs-transcript-to-confirm?** No — needs a product/modality confirmation, not a call. Prose-fixable if confirmed a leak.
- **backend-or-tool-adherence?** No — prose.

## [LOW] Example 6 is malformed — two agent closing turns for one do-not-call

- **Symptom:** Example 6 shows **two** consecutive `**Agent:**` closing turns responding to the same do-not-call request, each ending in "Goodbye" — a broken example the model could mimic (two closings).
- **Evidence:** Lines 1405 and 1409.
- **Bug-pattern:** cf. **E1** (example hygiene).
- **needs-transcript-to-confirm?** No (static). **backend-or-tool-adherence?** No — prose-fixable.

## [LOW] Duplicate "No-Match Fallback" sections

- **Symptom:** Two near-identical "No-Match Fallback" sections with slightly different trigger wording — redundant and a future-drift risk (edit one, forget the other).
- **Evidence:** Lines 123-136 and lines 384-394.
- **Bug-pattern:** none specific (hygiene / A3-adjacent overlap).
- **needs-transcript-to-confirm?** No (static). **backend-or-tool-adherence?** No — prose-fixable.

---

*Also worth a one-line note (not counted): the **D40 location-required** fix is only durable if `location` is in the `create_profile` tool's `parameters.required` (a schema PATCH) — the prose gate at line 812 alone is a known runtime tool-adherence risk (D25/D40, NOT prose-fixable). The task states this was done today; confirm the schema, not just the prose.*

---

**Counts:** HIGH = 1, MED = 3, LOW = 3.
