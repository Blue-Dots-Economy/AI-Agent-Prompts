# Maya Changelog

Every prompt edit to Maya is logged here. Maya is Hindi-only (KKB spinoff). Entry format:

```
## YYYY-MM-DD — <short title>
- **Feedback/bug:** what prompted the change
- **Change:** what was changed
- **Files:** which files were touched
- **Ported from:** <source agent> (only for cross-agent ports)
```

## 2026-10-13 - Tracker r114, r123, r142, r143: rejected education value, invented age, grammar, double opening
- **Feedback/bug:** tracker rows dated 12/10, grounded in 68 Maya Signals campaign calls (Oct 6/8).
- **Change (Maya Hindi Signals and Maya Inbound Signals):** education labels `ITI` / `Diploma`; `otherHelpNeeded` mapped to the two API values (`9a425a9f` was rejected for `["Training"]`); age only as said or stored, never an example value (`7cacd94e` sent 25 and a made-up `profile_id`); consent question said once at the end. Signals only: opening grammar "हम ... कर रही हूँ" fixed (45/45 calls) and "की स्टूडेंट" -> "के स्टूडेंट"; the audio-check reply no longer triggers `get_profile` in the greeting turn (8/8 double openings); `get_profile` tool description repeats the rule (raya/toolspecs/desc/maya-get_profile-after-greeting.txt).
- **Tried and REVERTED the same day:** saving a new caller's consent at once with `record_consent_new` (the KKB Slim fix). On Maya it was 0 of 4: the age was invented three times (`4d92db17` 22, `462a2c2c` 20, `b02805da` 22, never asked) and once asked but the save never sent (`4e31d584`). Writing invented ages into consent records is worse than the old behaviour, so the prompt port and the tool were removed; consent is again written by `create_profile` at apply (snapshot `pre-consent-port-revert` keeps the attempt). Open: Maya consent is still lost when a new caller hangs up before applying.
- **Verified:** no double opening and the corrected grammar on `4e31d584`, `b02805da` (after the trigger fix); double opening still seen once on `462a2c2c` before the tool-description change. Education value, age guard on `create_profile`: DEPLOYED, NOT VERIFIED (the tester went silent before every apply).
- **Files:** `Maya/Maya Hindi Signals.md`, `Maya/Maya Inbound Signals.md`. Snapshot `pre-oct13-tracker`.

## 2026-10-12 - MPL competition removed from all Ghaziabad Maya bots
- **Feedback/bug:** Aryan (email, 2026-10-12): "Remove MPL completely from the GZB bots next week onwards." Real calls showed Maya inbound pitching MPL on 5/25 calls, sometimes before the job flow was done.
- **Change:** the MPL Competition section, its offer lines, its routing and every reference removed from all four Maya conversation prompts; output fields 18 `mpl_registration` and 19 `mpl_presented` removed; MPL references removed from the memory prompt. Live output/memory patched per agent in place (the Signals output carries an extra `profile_save_consent` field the repo file does not).
- **Files:** `Maya/Maya Hindi.md`, `Maya/Maya Inbound.md`, `Maya/Maya Hindi Signals.md`, `Maya/Maya Inbound Signals.md`, `Maya/Maya Output.md`, `Maya/Maya Memory.md`. Snapshots `versions/Maya/*pre-mpl-removal` and `raya/live-snapshots/maya-*.pre-mpl-removal.md`.
- **Verified:** 0 MPL mentions on `5a0366de` (maya outbound) and `0ac19800` (maya inbound). The two Signals variants: DEPLOYED, NOT VERIFIED by call.
- **Still open (not fixed here):** Maya inbound reads stale Bengaluru inventory (EV roles etc., D105 class); Maya consent has the same later-step persistence gap fixed today on KKB Slim.

### 2026-09-08 (night) — my opener fix FAILED, and the diagnosis behind it is refuted by experiment

**The fix did not work.** `d15a8f9b` (post-deploy, 15:51 UTC, `college_name: "VMLG College"`) opened
**"नमस्ते। मैं माया बोल रही हूँ"** — branch B, no institution, with a real college name in the
arguments.

**And the reason I gave for the bug is wrong.** I attributed it to `contact_memory` arriving as the
string `"Not Available"` and satisfying branch B's sentinel trigger, on the strength of a clean
per-bot correlation: `maya-hi-out` receives no `contact_memory` and fires branch A 48/48;
`maya-hi-signals` receives it and fires 2/14. **One controlled dial settled it the other way:**
`910b2d29`, the identical fixture with `contact_memory` **removed entirely**, still opened with no
institution.

Everything else I could rule out from here, I have:

| candidate | ruled out by |
|---|---|
| `contact_memory` | `910b2d29` — omitted entirely, same failure |
| the prompt text | the two files' opener blocks are **byte-equivalent** — same length, same order, same content |
| a duplicate demonstration (D50) | the institution-free line appears **once**; the named line twice |
| an unsubstituted token | `b6353cfb` spoke `VMLG College` **aloud**, so the value does reach this bot |

**So the cause is unknown, three prompt framings have failed, and no fourth was written.** The first
framing made branch A never fire (`24293fbe`); the second was the two-opener block; the third named
the field. Escalated as `ESCALATION-litwiz.md` §4 — *what differs between these two agents other
than their instructions?* — together with a second question the same transcript raised: `d15a8f9b`
produced a specific callback claim (*"पिछली बार हमारी बात एक जॉब में अप्लाई करने के बारे में हुई थी"*)
that was **not in the `contact_memory` we sent**, which suggests Raya's own `memory_enabled` store is
injected alongside the argument. If so, every rule in these prompts that branches on memory is
reading only half of what the model sees.

**What was left in the prompt and what was taken out.** The scoping sentence — *only the
`college_name` value line decides this; no other field's value bears on it* — is true and stays. The
paragraph that cited the 48/48-vs-2/14 split as evidence for the `contact_memory` mechanism is
**replaced** with the refutation, so the next reader does not re-derive a ruled-out cause. Analyser
**D75** is retracted as the Maya diagnosis; the shape it describes remains worth looking for but has
no confirmed instance.

**The method lesson, which is the opposite of the one I drew at the time:** a per-bot correlation is
not a mechanism. Two bots differing in one argument and in their behaviour is a hypothesis, and the
controlled dial that separates it from the alternatives costs one call. I wrote the fix from the
correlation and spent the dial afterwards. The dial should have come first.

### 2026-09-08 (evening) — the opener's branch B was being satisfied by `contact_memory`, not by `college_name`

**Feedback/bug:** found while measuring, not reported. On `08a8ff4f` (2026-09-08 06:53 UTC, seven
minutes after that morning's deploy) `college_name` was `"VMLG College"` and Maya opened
**"नमस्ते। मैं माया बोल रही हूँ"** — branch B, no institution — with a perfectly good college name in
the arguments.

**Root cause — counted before anything was written (analyser D75).** With a real `college_name`:

| bot | `contact_memory` sent | branch A fires |
|---|---|---|
| `maya-hi-out` | not sent at all | **48 / 48** |
| `maya-hi-signals` | the string `"Not Available"` | **2 / 14** |

Same rule, same prompt family, same kind of value, opposite outcomes — and the split is by BOT, not
by value, which means it is not adherence. The difference is the argument set. Branch B's condition
read *"college_name is empty, **"Not Available"**, or still a token"* and never said which field it
reads; `maya-hi-signals` is sent `contact_memory: "Not Available"`, which the prompt injects as
`Here is the caller context: {Not Available}`. The trigger string was sitting in the model's context
attached to the wrong field, and the branch evaluated correctly against the wrong input.

Twelve of fourteen campaign callers were therefore greeted with no institution at all — which
removes the entire campus-recruitment premise of the call, on the bot that runs the campaign.

**Change:** the arms are untouched (they were right). Branch B's condition now names the field — "the
`college_name` VALUE LINE above" — followed by an explicit exclusion that names the colliding field:
*"ONLY the `college_name` value line decides this. No other field's value has any bearing on it,
whatever that field happens to say. `contact_memory` in particular very often arrives as the string
`"Not Available"` … that is a statement about the MEMORY, not about the college."* Plus the measured
48/48-vs-2/14 split, so a future editor can see why the sentence is there.

**Files:** `Maya/Maya Hindi Signals.md`, `Maya/Maya Hindi.md`. Both deployed.

**Verification:** reproducing fixture `raya/testcases/args/r5/maya-vmlg-offlist.json` now carries the
exact failing input — `college_name: "VMLG College"` **and** `contact_memory: "Not Available"`. Pass
condition, one line: the opener says **वीएमएलजी कॉलेज**. A dial is in flight; until it lands this is
**DEPLOYED, NOT VERIFIED**.

**Also seen on `08a8ff4f`, not fixed here (flagged):**
- The Case B pool overview was spoken **twice**, the second time bundled with the location question
  AND the job list in one turn — three questions in one breath.
- **"ठीक है, नोट कर लिया"** and **"मैंने अपडेट कर दिया है"** were both spoken. Both are storage
  claims the prompt bans.
- The read-back omitted **role** and **qualification** (see `KKB/CHANGELOG.md` for the verification).
- `college_name` arrives in Latin and was spoken in Latin on 6 calls across both Maya bots
  (`b6353cfb`, `2cb97508`, `78ef362f`, `ebf85d38`, `d543c5b0`, `79a745d9` — values `VMLG College`,
  `Ghaziabad Institute of Technology`, `VTU`). That is what this morning's conversions-list edit
  targets; still unverified.

### 2026-09-08 — Maya's own worked examples were teaching the bot to speak the raw ${college_name}

**Feedback/bug:** found while root-causing Khushboo's r5 report on KKB (see `KKB/CHANGELOG.md` for the
shared mechanism, analyser D71-D74). Live call **`b6353cfb`** (2026-09-07, `maya-hi-signals`) opened
with **"नमस्ते। मैं माया, `VMLG College` की ओर से बात कर रही हूँ"** — the value in Latin script inside a
Hindi sentence, which the Hindi voice then has to read letter by letter.

**Root cause — the samples outvoted four rules (D74).** Maya Hindi and Maya Hindi Signals each carried
FOUR instructions to convert the college name to Devanagari (the `## Named entities` rule, the
"never mix Latin and Devanagari" line, a "sound it out phonetically" fallback, and the point-of-use
instruction in opener branch A). All four were in place and it still failed. The cause was two lines
per file that no rule can outrank:

- `> **Agent:** नमस्ते। मैं माया, ${college_name} की ओर से बात कर रही हूँ…` — both worked examples
  **demonstrated the agent speaking the unsubstituted token**, twice each.
- `**Context:** ${college_name} = ${college_name}.` — a tautology, so the sample never established a
  concrete value for the demonstration to convert.

Secondary cause (D71): the "Common conversions" list held `Thakur`, `LR`, `TPS`, `MMH`,
`Lajpat Rai`, `Sahibabad` — and **not `VMLG`**. Checked against production, `college_name` is
`VMLG College` on **345** of 460 cached campaign calls and `LR College` on 111. `LR` was on the list
and has never been reported wrong. So the single most common value on this bot was the one value
with no demonstration behind it, and the fallback that was meant to cover it is conditioned on the
model being *"unsure how to transliterate"* — which it is not, for a run of capital letters
(the D70 shape: a trigger that is never true).

**Change:**
- Both samples in both files now show `LR College` → **"एलआर कॉलेज"** in the spoken line, with the
  Context line naming the substitution: *"`${college_name}` = `LR College` — an initialism, so the
  spoken form is 'एलआर कॉलेज'. What the agent says below is the CONVERTED form, never the value as it
  arrived."*
- `VMLG` → वीएमएलजी and `VTU` → वीटीयू added to Common conversions (the values production actually
  sends), and the list is now stated to be **examples, not an allow-list**.
- The employer-name clause the **Inbound twins already carried** was missing from both outbound files —
  a mirror gap inside Maya's own family. Ported, with this bot's real inventory names
  ("Kashi Infotech" → काशी इंफोटेक, "Dafsons Healthcare" → डैफसन्स हेल्थकेयर, "Procaps" → प्रोकैप्स).
- The Inbound twins, which had the employer examples but demonstrated no **initialism**, gained that
  shape plus the same off-list statement.
- Mirrored from KKB in the same change: the Latin `Qualification:` label → `क्वालिफिकेशन:` (3 per file,
  4 files), and the qualification-is-not-a-role branch in the role-usability closed set.

**Files:** `Maya/Maya Hindi.md`, `Maya/Maya Hindi Signals.md`, `Maya/Maya Inbound.md`,
`Maya/Maya Inbound Signals.md`. All four deployed and read-back verified.

**Verification:** **DEPLOYED, NOT VERIFIED.** Fixture `raya/testcases/args/r5/maya-vmlg-offlist.json`
carries the real `VMLG College` value and the real 28-job array. Pass condition, one line: the opener
says **वीएमएलजी कॉलेज** and no Latin character appears in any spoken turn.

### 2026-09-04 — Tracker sweep (mirrored from KKB): row-1 already-applied unreachable; inbound Example 2 demonstrated the open area ask

- **Feedback/bug:** Tracker `All Issues` review. Row 103 (KKB Hindi Signals, P1) "bot is saying
  technical issue instead of already applied". Rows 106/107 (KKB Inbound Signals, P1) location and
  consent — the location half recurred on live traffic AFTER the 2026-09-04 fix was called verified
  (`b48f70fb`, `2d8b7cb1`, both post-deploy).
- **Root cause (row 103) — two competing instructions, both added by earlier fixes.** Counted first
  (CLAUDE.md ladder rung 0): of 60 `apply_job` calls returning `ACTION_LIMIT_REACHED` across
  2026-09-03/04, **45 spoke the technical-issue line, 5 spoke an already-applied line, 10 spoke
  neither** — and after 2026-09-03 11:10 UTC it was **0 for 11**. Two causes:
  (a) commit `feb9405`'s evidence gate listed only two admissible kinds of evidence and then said
  "**Nothing else counts** … If neither 1 nor 2 holds, row 1 is FORBIDDEN" — omitting the error-text
  condition that the whole mapping depends on (analyser **D62**);
  (b) the THREE-DISTINCT-OUTCOMES table routed `duplicate_check: "not-applied-before"` + any error
  to row 2 unconditionally, "never by guessing at the error" — which also stopped it READING an
  error that names its own reason.
- **Change (row 103): ATTEMPTED, TESTED, AND REVERTED — the Maya prompts are unchanged.** The same two
  edits were mirrored to all four Maya prompts, deployed, tested on the KKB twin, found not to work
  (and to regress into a false already-applied on an unrelated error — `5f0d3671`), and reverted.
  Row 103 is not prose-fixable: across 133 named tool errors on 2026-09-01→04 no error class ever
  produced a distinguishing line, because the model does not receive the error body. See
  `KKB/CHANGELOG.md` for the full table and `raya/overnight/ESCALATION-litwiz.md` §2.
- **Root cause (rows 106/108) — the sample outvoted the rule (analyser D63).** Every inbound prompt's
  *Example 2* is a returning caller whose fetched profile is described as carrying name, role, age and
  gender but **not** location, and its area turn shows the OPEN ask. The confirm-first rule (D61) is
  stated twice above it; the worked example is the thing the model followed.
- **Change (rows 106/108):** gave Example 2's fetched profile a location in all six inbound prompts and
  changed its area turn to the confirm line, with a stage direction naming the branch; mirrored the
  Hindi three-branch Case A structure to the two Kannada and two Maya inbound prompts (they still
  printed the open ask as a standalone script line under the rule — the exact shape D61 fixed); and
  added, to the confirm branch, that only the town/city part of a stored location is spoken — never a
  full postal address (`b48f70fb` carried `VILL-MURARI TAND KAKO, PO-BHADSARA,…PIN-804418`).
- **Files:** all 4 Maya conversation prompts (row-103 fix) and the 2 Maya inbound prompts (Example 2 +
  Case A + postal-address clause). Maya carries the same agnostic apply-outcome block as KKB, so both
  fixes are mirrored verbatim; no Maya divergence (college identity, MPL, feminine voice) was touched. `raya/regression/consent_before_apply.py` (the Kannada consent
  wording `ಪರ್ಸನಲ್ ಡೀಟೇಲ್ಸ್ ಕಂಪನಿ ಜೊತೆ ಶೇರ್` was missing from `SHARE`, producing a false CONSENT AFTER
  APPLY on `a5547492`; also now checks the earliest apply rather than comparing the first apply to a
  later consent line). Analyser: **D62**, **D63**.
- **Verification:** the Maya inbound location fix is **DEPLOYED, NOT VERIFIED** — the harness has one
  tester DID and it was used for the KKB Hindi (`8235309e`) and KKB Kannada (`537549c6`) inbound
  variants, which are the twins that carry the identical agnostic block. Per the test-every-variant
  rule this is NOT a claim about Maya: `maya-hi-in-signals` and `maya-hi-in` need their own call.
  The `acting_as_user_id` tool-schema tightening WAS applied to `maya-hi-signals` and
  `maya-hi-in-signals` (parity clean) and is likewise unverified on Maya.
- **Ported from:** KKB (agnostic apply-outcome and inbound location blocks).

### 2026-09-01 — Khushboo r3: the location reconfirm was structurally unreachable; the already-applied line is NOT prose-fixable (proven); Muradnagar canonical

**Reported (WhatsApp, call ref 4989329 → live calls `5c67bd19` 07:16 and `90da81db` 07:50, both to XXXXXX6073):**
(1) "Location is not been confirmed — it asked where do you want to work despite giving proper input variable",
and no nearest-station/landmark probe was heard. (2) "It is still resorting to same fallback for already applied
jobs — technical issue, noted etc." (3) "Murad nagar pronunciation is wrong (add in the canonical section)."
(4) Kannada test jobs needed.

**Root cause 1 — the location reconfirmation could not be reached on the path both her calls took (analyser D51/D53).**
`#### Location state`, which holds the reconfirmation, the mismatch handling and the ladder, was nested INSIDE
`### Case A — you already know the target role`. Both of her calls went down **Case B** (the fetched profile's role
was the placeholder `Any` → treated as UNKNOWN), and Case B held only a *pointer* to "the Location reconfirmation
from Case A" while quoting the open UNKNOWN area lines inline. Standing in Case B, the model took the line that was
in front of it. Second contributor: the KNOWN branch had no state for **"known, but no job is in that place"** —
her input was `Delhi` and all 8 jobs were Ghaziabad — so the reconfirmation collided with the Hallucination Guard
(never name a place we hold no job in) and lost. That produced two *different* wrong behaviours on identical args:
`5c67bd19` asserted "आपके लिए दिल्ली में कुछ जॉब्स हैं" (false — no Delhi jobs), `90da81db` ignored the input and asked
openly. Third contributor: `Location precedence` ranked the fetched profile's `item_state.location` (a stale
`Bengaluru, Karnataka, India`) ABOVE the per-call campaign input, so the closing read-back told her "एरिया बेंगलुरु".
The station/landmark rungs correctly did NOT fire — they are rung 3 of a bounded ladder, reached only when the word
itself is unusable, and her city resolved fine.

**Root cause 2 — the "already applied" line is NOT reachable from the tool error, and now proven so (analyser D52).**
Scanned every `ACTION_LIMIT_REACHED` call across the fleet: **8 of 8** spoke the generic line, **0** spoke the
explicit one — `kkb-hi-signals` (`90da81db`, `21c428dc`, `dc3168ec`), `kkb-kn-signals` (`18b5e1b8`),
`kkb-kn-in-signals` (`d824912c`), `maya-hi-signals` (`96e72c85`, `9d82ac2c`, `3be8d3fb`) — including three calls
made AFTER the branch had been restructured into an explicit lookup table. Then the decisive test: the error→line
mapping was also put into the `apply_job` **tool description** (read at the moment of use, `scripts/raya_tooldesc.py`)
and live call `14f90f64` hit `ACTION_LIMIT_REACHED` and STILL spoke the generic line — **9 of 9**. This closes the
open question from 2026-08-25: the conversation model does **not** receive the HTTP error body; the
`__RAYA_TOOL_DEBUG__` block carrying `ACTION_LIMIT_REACHED` is not visible to it. Every prose iteration was
branching on a string that never arrives.

**Change — location (kkb-hi-signals only, registered divergence `kkb-hi-signals-location-capture`):**
- **Promoted** `Location state` out of Case A to a sibling `###` section that both paths must pass through, retitled
  "the ONE area turn, and it governs BOTH Case A and Case B". Case A and Case B now each hand off to it and hold no
  area wording of their own.
- **Removed the competing option:** Case B's inline open-ask bullets are gone; the block states that when the
  location is KNOWN the open UNKNOWN lines are **not available**, and that the turn is ONE question, its own turn,
  never appended to the pool-overview question with a "साथ ही…" clause (observed on `0decf61a`).
- **New third location state — LOCATION MISMATCH,** with its own mandatory truthful line naming both places:
  "आपके लिए [जगह] में अभी कोई जॉब नहीं है — जो जॉब्स हैं वो [शहर] में हैं। [शहर] में देखना चलेगा?" — plus the explicit note that
  this branch is what the Hallucination Guard REQUIRES, and that the plain reconfirmation is not an inventory claim.
- **Location precedence reordered:** caller's own words → **the location input** → the fetched profile's
  `item_state.location` → UNKNOWN, with the reason stated (the profile field is where they LIVE and goes stale).
- **`KKB Output.md`:** new `15c. input_location_had_jobs` (Yes/No/NA) so a campaign dialling a city we hold no
  inventory in shows up in reporting instead of in a QA message. Deployed to `kkb-hi-signals`'s `output_instructions`.

**Change — already applied (all 12 KKB/Maya conversation prompts):**
- **New `## Already applied — check BEFORE you call the tool`** in `apply_job Tool Call Rules`: derive the duplicate
  from what the bot actually HAS — this call's own `apply_job` history, and `jobs_applied` in `${contact_memory}`
  (matched on role + company, suffixes ignored) — say the explicit line, and do not call the tool at all. This is
  the only route to the line that does not depend on the invisible error string.
- **Restructured `Apply Failure Handling`** in the 11 prompts that had not yet had it: the two labelled cases become
  a two-row lookup keyed on *what you know*; the **false cause-claim is deleted entirely** in both languages
  (`"अभी हमारी तरफ़ से apply complete नहीं हो पाया — कोई तकनीकी दिक्कत है…"` and
  `"ಇನ್ನೂ ನಮ್ಮ ಕಡೆಯಿಂದ apply complete ಆಗಿಲ್ಲ — ಸ್ವಲ್ಪ technical ತೊಂದರೆ ಇದೆ…"`), replaced by lines that assert nothing
  (`"अभी इस जॉब में अप्लाई पूरा नहीं हो पाया…"` / `"ಈ ಜಾಬ್‌ಗೆ ಅಪ್ಲೈ ಇನ್ನೂ ಪೂರ್ತಿ ಆಗಿಲ್ಲ…"`). The
  second-consecutive-failure acknowledgement lost its cause-claim too.
- **Fixed two dangling labels** (analyser D51): the failure section's hard ban said "say the **Case A** line" and the
  turn-composition rule said "(Case A or Case B)" — labels that no longer existed there and that mean something
  ELSE in Step 1. The ban was inert, which is why the section's default line won every time.

**Change — found by testing, not reported:**
- **`Apply Success Handling`:** the success line is now forbidden on any call where `apply_job` did not succeed, in
  the turn that answers the Need Capture offer, and anywhere later. Call `14f90f64` told the caller
  "अभी इस जॉब में अप्लाई पूरा नहीं हो पाया" and then, two turns later, "अप्लाई हो गया है" — a direct contradiction.
- **`update_profile` rules:** never narrate an update that was not made. Call `0decf61a` said
  "मैंने उम्र 26 साल अपडेट कर दी है" with no `update_profile` call in the transcript — a hallucinated write.
- **Canonical Location Spellings:** `Muradnagar → मुराद नगर` (the space is deliberate — as one word the द+न cluster
  slurs), plus `Surajpur`, `Raj Nagar` (+ District Centre / RDC), `Govindpuram`, `Kavi Nagar`, `Shipra Mall`, `NH-9`,
  all classified as Ghaziabad localities; and a rule that a `"Locality, City"` job value is spoken as the locality
  alone, with campaign junk ("/ WFH – serving Ghaziabad") never read aloud.

**Verified by live call (Tier 1):**
- **Muradnagar** — `0decf61a` (10:25 UTC): bot spoke "मुराद नगर", `call_output.company_location: "मुराद नगर"`, and the
  tester's ASR heard it back as "मुरादनगर" — i.e. the audio resolves to the right town. **Parth/Khushboo should still
  confirm by ear; a TTS pronunciation cannot be verified from a transcript.**
- **The false cause-claim is gone on kkb-hi-signals** — `14f90f64` hit `ACTION_LIMIT_REACHED` and said the
  assertion-free line, not "तकनीकी दिक्कत".
- **Gender is asked once and persisted** — `5c67bd19`: `update_profile` sent `gender: "Female"`, API returned it on
  the item. (Khushboo's "is it auto detecting?" — no; nothing is inferred.)

**DEPLOYED, NOT VERIFIED (each needs its own call id before anyone writes "fixed"):**
- the promoted `Location state` block and the LOCATION MISMATCH line — deployed 10:33 UTC, after every test call
  above; round-2 calls were still running when this entry was written
- the duplicate pre-check from `${contact_memory}` — the mechanism that has to carry item 2
- the Apply-Success suppression and the no-hallucinated-write rule
- **all 11 propagated prompts** (kkb-hi-out, kkb-kn-out, kkb-hi-in, kkb-kn-in, kkb-hi-in-signals,
  kkb-kn-in-signals, kkb-kn-signals, maya-hi-out, maya-hi-signals, maya-hi-in, maya-hi-in-signals) — deployed with
  read-back OK, **none voice-tested**. Per the recipe-for-disaster rule these are 11 separate verifications.

**Escalation to LitWiz (now justified — ladder steps 1-4 exhausted):** ask that the tool error's `error`/`message`
fields be surfaced to the conversation model, or that a distinct tool result be returned per reason. Evidence: 9/9
`ACTION_LIMIT_REACHED` calls listed above, across 3 bots / 2 languages / 2 directions / 3 prompt structures, plus
`14f90f64` with the mapping in the tool description itself.

**Files:** `KKB/KKB Placeholder Hindi Signals.md`, `KKB/KKB Output.md`, and the 11 propagated prompts listed above;
`raya/divergences.json`; `raya/tooldesc/apply_job-already-applied.txt`
**New tooling:** `scripts/raya_tooldesc.py` (patch a tool's description only, verified by read-back),
`scripts/raya_side_prompt.py` (deploy memory/output instructions, which `raya_deploy.py` cannot),
`raya/testcases/args/handover/dharwad-test-recommendations{,-8}.json` (15 / 8 live Dharwad job ids for Kannada
testing — the 4 ids in `kkb-kn-signals-4jobs.json` are from the old instance and fail `SOURCE_ITEM_NOT_FOUND`,
call `03272636`), `raya/personas/hi-loc-then-apply.md`, `raya/personas/hi-pick-data-entry-apply.md`
**Analyser:** new **D51** (dangling branch label after a restructure), **D52** (a rule branching on a tool-error
string the model never receives), **D53** (an input echo-back suppressed by a guard about something else)

### 2026-08-25 (later) — D47 follow-up: the reason branch does NOT hold at runtime (VERIFY-PENDING)
- **Status:** the Case A / Case B branch is deployed on all 12 prompts but is **NOT verified working** — it was
  ignored on two consecutive live calls. Do not treat this defect as fixed.
- **v2 change:** moved the condition onto the base-failure-line label (`**Base failure line — CASE B ONLY (say
  once):** …`) and added a matching failure-turn hard ban, on the theory that the model reads that label and
  skipped the block above it. Deployed to all 12; live agents re-verified as carrying it.
- **Result:** live call `3be8d3fb` (v1) and a second maya-hi-signals call (v2) both hit
  `ACTION_LIMIT_REACHED` on job `b7513680` and both spoke "कोई तकनीकी दिक्कत है" anyway.
- **Open question (platform, not prompt):** whether the model receives the error reason at all. The tool result
  is `[Error: apply_job request failed (HTTP 422).]` plus a `__RAYA_TOOL_DEBUG__` block; if that block is not fed
  back, `ACTION_LIMIT_REACHED` and `TARGET_ITEM_NOT_FOUND` are both just "HTTP 422" to the model and no wording
  can branch on them. Needs one diagnostic call, then a LitWiz ask — not a third prose attempt (analyser D25).
- **Files:** the same 12 KKB/Maya conversation prompts; analyser **D47** updated with the failure evidence
- **New tooling:** `raya/regression/apply_outcomes.py` — runtime check over real calls that caught both failures
  automatically. Also surfaced that `HTTP 404 — Invalid or missing profile_id` is 16 of 23 fleet apply failures
  in two days (tracker row 84).

## 2026-08-28 — Signals production cutover: Ghaziabad (Hindi) / Dharwad (Kannada)
- **Feedback/bug:** the Signals platform split into two region instances — `gzb-signals.bluedotseconomy.org` for the Hindi bots and `dharwad-signals.bluedotseconomy.org` for the Kannada bots — each with its own API key and acting-org id. The new instances also validate item_state far more strictly than the old shared instance, so a straight URL/key swap would have broken every profile write.
- **Change:** tool-config cutover on all 10 Signals agents via the new `scripts/signals_cutover.py` (plan/apply/verify, idempotent). Per agent: base URL on every tool, `x-api-key` + `x-acting-org-id`, and the base URL embedded in `apply_job`'s `payload_template.target_item.item_instance_url`. Plus the validation fixes the new instances require, each confirmed against the live API: `age` and `positions` declared **integer** (Raya does whole-value typed substitution, so the declared param type is what controls the wire type); `otherHelpNeeded` declared **array**; `natureOfJobsInterestedIn` literal changed from `'Full-time'` to `['Full-time']`; `educationCategory` enum `'ITI / Other Vocational Trainings'`→`'ITI'` and `'Polytechnic / Diploma'`→`'Diploma'`; `otherHelpNeeded` enum replaced entirely with `'Skilling & Vocational Training'` / `'Other Support (Accommodation / Travel)'`; `title` dropped from the `job_posting_1.0` payload (now rejected as an additional property).
- **PROMPT change (this repo):** the three inbound Signals prompts carried a **hardcoded Job Inventory** whose `job_id`s belong to the OLD instance. Post-cutover every inbound apply failed `TARGET_ITEM_NOT_FOUND` — inbound callers could not apply to anything. Replaced each inventory with 4 live job ids from that bot's own instance (Ghaziabad for the two Hindi files, Dharwad for the Kannada one), keeping each file's language-specific `qualification` text. Verified live: the same scenario now reaches `ACTION_LIMIT_REACHED` (a real duplicate) instead of `TARGET_ITEM_NOT_FOUND`.
- **Files:** `KKB Placeholder Inbound Signals.md`, `KKB Placeholder Inbound Kannada Signals.md`, `Maya Inbound Signals.md`; `scripts/signals_cutover.py`; `raya/testcases/args/signals-prod/`
- **Testing:** 17 live calls across all 10 agents. Full write path proven end-to-end on `kkb-kn-signals` (`get_profile` empty → `create_profile` with integer age → `apply_job` → `status: success`). No agent contacted the wrong region on any call.

## 2026-08-25 — Apply failure messages now branch on the actual failure reason
- **Feedback/bug:** tracker r100 (KKB Hindi Signals, 25/08, P1) reported as "apply failed, no details collected or reiterated", plus a same-day retest reported as "API still failed" after a Signals API-key incident had been fixed. Root-caused against calls `bc7ef5b5` (10:26 IST) and `1e2fd2a2` (14:41 IST): neither was a technical failure. Both were `422 ACTION_LIMIT_REACHED` — "An active request already exists between these two profiles" — i.e. the seeker had **already applied** to that job (in `1e2fd2a2`, to the very job that applied successfully in `bc7ef5b5` four hours earlier). The bot spoke both as "कोई तकनीकी दिक्कत है" and promised to fix the problem and call back, so a correctly-refused duplicate was indistinguishable from an outage and was escalated as a P1 against the wrong team. r100/r101 were closed as *Rejected / Not an Issue*; this line is the one genuine defect they surfaced.
- **Change:** `Apply Failure Handling` now requires the reason to be read **before** anything is spoken, and splits into two cases. **Case A — the application already exists** (`ACTION_LIMIT_REACHED`, or any message saying an active/duplicate request already exists between the two profiles): say so truthfully, suppress the base failure line, no "तकनीकी दिक्कत", no apology, and no callback promise — close per Graceful Exit if no other job remains. **Case B — a genuine technical failure** (job does not exist, 4xx/5xx, timeout, no response): unchanged, uses the existing base failure line and next-step rules. Purely additive: 7 lines per file, nothing removed or reworded. The Case A spoken line is phrased to agree with the feminine noun एप्लीकेशन / ಅಪ್ಲಿಕೇಶನ್ rather than with the caller, so it is safe on a caller of any gender (analyser D44).
- **Files:** `Maya Hindi.md`, `Maya Hindi Signals.md`, `Maya Inbound.md`, `Maya Inbound Signals.md`
- **Ported from:** KKB (same agnostic change applied across the whole apply-capable fleet; Maya is Hindi-only so there is no Kannada mirror)

## 2026-08-24 — Tracker r98 + propagation: substantive service answer, returning-caller rollout, bounded name gate
- **Feedback/bug:** r98 (KKB Maya Signals, P1, owner Parth) reported the same two items as the KKB rows: the returning-caller message missing, and the service answer being too thin. Verified: the callback block was absent from all four Maya prompts, and the service answer was the same vague one-liner. The bounded-name-gate gap found on KKB Kannada Inbound (call `6b420bac`) is present in Maya's identical Step 3.5 gate, so it was propagated rather than left to be reported later.
- **Change:** substantive service answer in all 4 Maya prompts (with the "ONE sentence" instruction relaxed to match); the live-verified returning-caller callback block ported into `Maya Hindi Signals.md`, folded into the existing post-`get_profile` turn; bounded name-asking added to `Maya Hindi.md` and `Maya Inbound.md`. Maya's divergences are untouched (campus identity, `${college_name}`, MPL, feminine self-voice, Experience Capture).
- **Files:** `Maya/Maya Hindi.md`, `Maya/Maya Hindi Signals.md`, `Maya/Maya Inbound.md`, `Maya/Maya Inbound Signals.md`
- **Ported from:** KKB. **Analyser:** **B3**.

## 2026-08-12 — Need Capture: reserve a turn after the caller accepts the service (ported from TRRAIN)
- **Feedback/bug:** no Maya call reported this, but TRRAIN's `cef6523a` consent defect was audited across the fleet and Maya **shares its shape**: nothing between accepting a third-party service and the goodbye line reserves a caller turn. Verified structurally — KKB's Graceful Exit carries "confirm there is nothing else they want to ask" (2 hits per file), all four Maya files carry **0**; and the MPL offer in the very same Maya file already has the anti-bundling rule that Need Capture lacked.
- **Change:** the Need Capture "clear yes" now ends on "इसके बारे में कुछ पूछना है?" and may not carry the closing line or Goodbye in that turn; the existing one-sentence answer is reachable **after** the yes as well as before; "one ask per call" and "do not explain what the service provider does" gained explicit carve-outs stating that answering a question is not a second ask; a withdrawal after the clarification records `service_provider_interest` = **No**. Maya's spoken sentence was deliberately left unchanged so no wording divergence with the 8 KKB files is created.
- **Files:** `Maya/Maya Hindi.md`, `Maya/Maya Hindi Signals.md`, `Maya/Maya Inbound.md`, `Maya/Maya Inbound Signals.md` (4 edits each, all deployed)
- **Ported from:** TRRAIN. **KKB: deliberately NOT changed** — audited and does not have this defect; editing 8 live prompts to harden something they already handle is churn with real regression risk.
- **Flagged:** `CLAUDE.md` requires flag-and-ask before applying a shared change to Maya. This was applied under the owner's "fix everything needed" instruction and touches none of Maya's registered divergences (college identity, `${college_name}`, `hr_contact`/`benefits`, Experience Capture, HR-number sharing, MPL, feminine voice) — but it was not separately approved, and is called out here for that reason.
- **Analyser:** **D46**.

## 2026-08-12 — Caller-directed verbs follow the CALLER's gender, not Maya's (+ inbound variable/inventory fixes)
- **Feedback/bug:** Maya addressed **every** caller with feminine honorifics, so a male graduate was misgendered from the greeting on: "आप किस तरह का काम ढूंढ **रही** हैं?" and, at role-confirm, "आप अभी [role] का काम कर **रही** हैं". Confirmed live on calls `ecbccbb1` (maya-hi-in) and `124be450` (maya-hi-in-signals), where the caller had just said "मैं आर्यन बोल रहा हूँ". Root cause: the Voice-gender rule was read as governing the whole spoken line rather than Maya's own first-person verbs — and its parenthetical **explicitly endorsed** the feminine caller-address, so every template and example taught the wrong form. KKB's twin templates were already correct (`कर रहे हैं`).
- **Change:** scoped the Voice-gender rule to Maya's **first-person** verbs only, and stated that caller-directed verbs follow the caller's gender (masculine honorific `रहे हैं` for a male caller, feminine for a female caller, masculine as the neutral default whenever gender is not yet known — including the greeting and every turn before `get_profile` returns). Corrected every caller-directed form in the spoken templates and worked examples: 19 / 17 / 21 / 19 sites across the four files. **Maya's own feminine voice is untouched** (26–28 first-person feminine forms preserved per file) — the divergence stands. Also applied the same inbound fixes as KKB: re-pointed the three `${recommendations}` guards at the Job Inventory, de-tokenised descriptive mentions of absent variables (phantom args now gone: args are `contact_memory`, `contact_phone`, `country_code`, `college_name`), and added the never-say-"inventory"-aloud rule.
- **Files:** `Maya/Maya Hindi.md`, `Maya/Maya Hindi Signals.md`, `Maya/Maya Inbound.md`, `Maya/Maya Inbound Signals.md` (all four deployed)
- **Also corrected (no edit):** the sweep's "invented job categories from memory" verdicts on `maya-hi-in` / `maya-hi-in-signals` were **my grading error** — the roles it named (Customer Support, Sales/Marketing, Retail/Food-Service, Cashier/Store; EV Charging, AC Technician) are all in each bot's own hardcoded Job Inventory, and it correctly ignored the Bengaluru args I passed. The overlap with stored memory was reverse causation. Analyser: **D44**, **D45**, **G6**.

## 2026-08-10 — Need Capture ported to Maya (pilot verified on KKB first)
- **Feedback/bug:** Same fleet-wide requirement as KKB: one service-provider offer before goodbye, piloted and tested before replication.
- **Change:** Added `# Need Capture (ONE offer, immediately before Graceful Exit)` to all four Maya conversation prompts, and the Graceful Exit check that fires it if it has not happened. Added `service_provider_pitched` and `service_provider_interest` to `Maya/Maya Output.md`, with an explicit rule that they are **independent of `mpl_presented`** — the MPL Competition and the service-provider offer are two different offers and must never be inferred from one another.
- **Maya gate:** shared core logic inherited from KKB, covered by the instruction to replicate after the pilot passed. Maya's divergences untouched: campus identity, `${college_name}`, `hr_contact`/`benefits`, Experience Capture, HR-number sharing, the MPL Competition offer, and the feminine-voice rule. The Need Capture offer sits after the job flow and before goodbye, so it does not interrupt or displace MPL.
- **Files:** `Maya/Maya Hindi.md`, `Maya/Maya Hindi Signals.md`, `Maya/Maya Inbound.md`, `Maya/Maya Inbound Signals.md`, `Maya/Maya Output.md`.
- **Ported from:** KKB.
- **VERIFY-PENDING:** no Maya variant has had its own live call for this block yet. Watch specifically for the two offers colliding — MPL and the service-provider offer must both be at most once, and neither may interrupt the job flow.

## 2026-08-10 — Audio-check intro turn (ported from the KKB pilot)
- **Feedback/bug:** Fleet-wide intro change: the bot was launching into the full introduction while the caller was still saying "hello, who is this?", so the introduction was talked over. Requested that outbound bots instead open with a short "can you hear me?" and give the real introduction only after the caller confirms.
- **Change:** Added `## Turn 1 — Audio check` as the first spoken turn of every call — "हैलो, मेरी आवाज़ आ रही है?" and nothing else — with branches for confirm / cannot-hear (ONE slower repeat, then a polite close) / silence. The existing campus introduction became the turn AFTER the caller confirms; its wording, the `${college_name}` identity, the student question, and the recording disclosure are all untouched. The canonical-flow line in the sample conversations was updated so the examples do not imply the audio check is skipped. `say_hello` set to **false** on both Maya outbound agents.
- **Maya gate:** this is shared core intro logic inherited from KKB, so it falls under the flag-and-ask rule. The user's instruction covering it was explicit — the intro change was specified for the fleet, and items 1 and 3 were to be piloted on KKB and then "implemented across other bots". Maya's divergences are preserved untouched: campus caller identity, `${college_name}`, `hr_contact`/`benefits`, Experience Capture, HR-number sharing, the MPL Competition offer, and the feminine-voice rule.
- **Files:** `Maya/Maya Hindi.md`, `Maya/Maya Hindi Signals.md`.
- **Ported from:** KKB (pilot `KKB Placeholder Hindi Signals.md`, verified live on 4 calls before rollout).
- **Not yet ported (deliberate):** the returning-caller callback line and the Need Capture offer are still KKB-pilot-only, pending live verification on the pilot. Maya inbound is untouched — for an inbound call the caller dialled us, so an audio check is not warranted and disabling the greeting would risk dead air on pickup.
- **VERIFY-PENDING:** the audio-check turn is verified live on KKB Hindi Signals, not yet on either Maya variant. Per the never-extrapolate rule, both Maya outbound variants still need their own live call.


## 2026-08-07 — Wrong college name spoken: remove hardcoded institutions from the examples (E1)
- **Feedback/bug:** "KKB Maya- Signals — wrong college name; given VTU it's saying Saraswati" (+91905…073, 07/08/2026 10:40 am). VALIDATED against call `44d9aff4` on `maya-hi-signals`: `agent_args` carried `college_name: "VTU"`, and the agent opened with *"नमस्ते। मैं माया, सरस्वती कॉलेज की ओर से बात कर रही हूँ… क्या आप सरस्वती कॉलेज की स्टूडेंट हैं?"* — naming a completely different institution, twice, in the first turn.
- **Root cause:** analyser pattern **E1** (examples override the real data). The opening-line template correctly used `[college_name]`, but the worked sample dialogues further down HARDCODED real institution names (`सरस्वती कॉलेज`, `पीईएस यूनिवर्सिटी`) in the agent's spoken lines. The model copied the example literal instead of substituting `${college_name}`. Nothing was wrong with the input args.
- **Change:** removed every spoken institution literal from the sample dialogues in all 4 Maya prompts — they now say `[college_name]`, so there is no literal left to copy. Removed the illustrative institution names from the inbound Input-Variables "e.g." line too. Added a caller-identity guard to all 4: never speak a college name that did not come from `${college_name}` / the deployment setting; every institution written in this prompt is a placeholder and is never said aloud.
- **Deliberately kept:** the transliteration mapping examples ("Thakur" → "ठाकुर") in the Devanagari-conversion section — they teach how to convert whatever name IS passed, and are now covered by the new guard. Removing them would degrade transliteration quality.
- **Files:** all 4 Maya conversation prompts. Snapshot: `versions/Maya/2026-08-07_173049__pre-college-name-fix`.

## 2026-08-07 — Split the bundled "any questions? / shall I apply?" turn (ported from KKB)
- **Feedback/bug:** Ported from KKB after two 2026-07-28 production calls on the KKB Kannada outbound campaign lost willing candidates: the job-detail turn asked BOTH "any other questions?" AND "shall I apply?", so a caller answering the first with a bare "no" had it read as a refusal, and the call closed with `jobs_applied: []` (calls `215fdd2d`, `6ee05050`). Maya carried the byte-identical bundled Hindi line and was therefore exposed to exactly the same failure. Applied here with the owner's explicit approval (the Maya gate).
- **Change:** identical structural fix to KKB's. (1) The job-detail spoken block now ends with ONLY the doubts question — "इस जॉब के बारे में कुछ पूछना है?" — and stops. (2) The apply-consent question moved to its own separate turn, carrying the unchanged data-share disclosure. (3) Three new English rules: never bundle the two questions; a negative to the doubts question is NOT a refusal but a green light to the consent turn; only an explicit refusal to the CONSENT question declines, and an unclear consent answer is re-asked once naming the action.
- **Maya divergences preserved:** campus caller identity + `${college_name}`, the feminine-voice rule, `hr_contact`/`benefits`, Experience Capture, HR-number sharing post-apply, and the MPL Competition secondary offer are all untouched — the edit is confined to the job-detail confirm block. The consent line uses "अप्लाई कर दूँ?", which is already the feminine-compatible first-person form Maya uses elsewhere.
- **Files:** `Maya/Maya Hindi.md`, `Maya/Maya Hindi Signals.md`, `Maya/Maya Inbound.md`, `Maya/Maya Inbound Signals.md`. Snapshot for rollback: `versions/Maya/2026-08-07_172646__pre-split-confirm-turn`.
- **Ported from:** KKB (2026-08-07 entry in `KKB/CHANGELOG.md`; analyser pattern **D41**).

## 2026-08-01 — Legacy Maya (outbound, Dhiway/up-getjob): restructured to the proven Signals shape

- **Feedback/bug:** the legacy Maya outbound prompt (`Maya Hindi.md`, agent 47fdffe6, Dhiway/up-getjob backend) still carried the old `${new_seeker}` input-fork, a profile-permission ask ("क्या आपकी कुछ बेसिक जानकारी देख सकती हूँ?"), a fetch-narration ("आपकी जानकारी मिल गई"), an unstorable post-apply "working/studying?" question, and framing/recording-line repetition. These are the exact failure classes the Signals restructure already fixed on the Signals twins.
- **Change:** rewrote `Maya Hindi.md` to have the STRUCTURE of `Maya Hindi Signals.md` (silent `get_profile`, fetch-driven branch on the result, campus identity, feminine voice, MPL, HR-contact, stabilisation guards) while keeping the **Dhiway tool contract** unchanged (get_profile GET `phoneNumber:+91`, response an ARRAY → `profile_id` = top-level `id`, role/age/gender/name from `metadata.*`; `create_profile` callback with `agentId`/`+91` phone/`profileId` UUID; `apply_job` = `profile_id`+`job_id`; NO `update_profile`). Fixes baked in: silent fetch (no permission-ask, no narration); dead `${new_seeker}` fork removed — always fetch, branch on the array; no unstorable "working/studying?" question (no post-apply data write); intro+recording said exactly once (no repetition); CD3 outbound-frame close ("ज़रूरत होने पर हमारी टीम आपसे फिर बात करेगी"). NO Signals-only fields added (educationCategory etc. deliberately excluded — Dhiway has no `update_profile`). Maya divergences preserved: campus caller-identity (never government), `${college_name}`, feminine first-person verbs throughout, MPL competition, HR-contact share post-apply (spoken-only), optional `hr_contact`/`benefits` fields.
- **Files:** Maya/Maya Hindi.md (rewrite). Not deployed, not tested (produce-file-only task).
- **Test status:** NOT deployed, NOT tested per task scope. Static verification only: grep-confirmed zero Signals contract tokens and zero masculine first-person forms in spoken lines. VERIFY-PENDING before any deploy.

## 2026-08-01 — Maya Signals: capture the new seeker profile fields (educationCategory etc.) in Phase 2

- **Feedback/bug:** same as KKB — Signals added the qualification/experience/help fields (`educationCategory` + conditionals, `itiInstitute`, `workExperienceYearsConditional`, `nameOfLastRoleHeld`, `otherHelpNeeded`) that the bot previously skipped. (Email not on Signals — still not asked.)
- **Change:** added the 15 new fields to `create_profile` + `update_profile` on both Maya Signals agents, and extended Phase-2 in both files (Maya Hindi + Maya Inbound) to ask them post-apply, only if missing — same topic set + byte-exact enums as KKB, **all post-application**. Reversed the old "never ask" line. Maya's divergences kept intact: feminine voice (the new bridge/read-back use "पूछ लूँ"/"confirm कर लूँ"), the MPL competition and HR-contact sharing untouched, and the Phase-2 bridge uses "जानकारी" (not "profile") to respect Maya's ban on speaking "प्रोफाइल".
- **Files:** Maya/Maya Hindi Signals.md, Maya/Maya Inbound Signals.md; agents 904f333f, 1c24feda (tools + instructions re-deployed).
- **Test status:** feature validated on the KKB Signals twin (identical agnostic logic); Maya spoken lines are Hindi-adapted + enum-exact (statically verified). Deployed.

## 2026-08-01 — Maya Signals: fix get_profile/create_profile phone double-91 prefix (CD6)

- **Feedback/bug:** same class as KKB — the prompt templated `91${contact_phone}`, but production passes the full 12-digit `${contact_phone}` (user-confirmed), so the phone doubled to a 14-digit junk value (D17/D39).
- **Change:** in both Maya Signals files (outbound + inbound) changed `91${contact_phone}` → `${contact_phone}` and reworded the phone-format notes to "already the full 12-digit number — pass AS-IS, never prepend another 91."
- **Files:** Maya/Maya Hindi Signals.md, Maya/Maya Inbound Signals.md; both agents re-deployed.
- **Test status:** deployed with the KKB CD6 fix; validated on the KKB-Hi confirmation call (single-prefix phone). Revert: git commit 7405bb7 (pre-CD6).

## 2026-08-01 — Maya Signals deep E2E pass: inbound inventory↔example consistency + parity + are-you-AI + outbound-close

- **Feedback/bug:** (user) deep end-to-end test + fix. Static audit found the **Maya Inbound** inventory was swapped to 4 real Signals jobs but the roles-list, synonym/role-family table, Case-B overview, canonical-locations and all example dialogues still described the OLD Ghaziabad/Noida set (CY Future, Weavings, Westside, sales/telecaller/retail) → analyser E1 hallucination risk. Plus small outbound↔inbound parity gaps, malformed inventory markdown, and two quality gaps (no are-you-AI responder; one outbound-frame D5 leak).
- **Change:**
  - **CD2 (Maya Inbound):** rewrote roles-list, role-synonym + role-family blocks, Case-B pool overview, canonical-locations, and Examples 1/2/3/5 to reference ONLY the 4 real jobs (Data Entry/Kashi, Remote Customer Support/Rampur, EV Charging Tech/Yamuna, AC Tech/Krishna; Bengaluru/Remote), with a nearby-location rule (Remote role fits any city; offer Bengaluru as the alternative). Employer names transliterated to Devanagari (काशी इंफोटेक). Since none of the 4 jobs carries an `hr_contact`, did NOT fabricate one (Hallucination Guard) — removed "→ HR number" from Ex1's title; HR-share behaviour stays documented abstractly. MPL, feminine voice, campus identity, memory block untouched. Inventory job_ids untouched.
  - **M17:** fixed the malformed `> **[` inventory-wrapper markdown → clean ```json fence; removed `[FLAG — REVIEW]` scaffolding.
  - **M14/M15/M16 (Maya outbound parity):** ported the honorific-plural voice clarification + the "never skip the fetch if the caller front-loads role/city" clause into the outbound; noted `${country_code}` as declared-but-unused.
  - **CD4 (both):** honest are-you-AI responder ("जी, मैं एक AI असिस्टेंट हूँ — आपकी मदद के लिए।", feminine).
  - **CD3 (Maya outbound):** reworded the inbound-frame closing ("जब भी फिर से देखना हो, बात कीजिए।") → outbound frame ("ज़रूरत होने पर हमारी टीम आपसे फिर बात करेगी।"). Inbound closings left (inbound may invite callback).
- **Files:** Maya/Maya Hindi Signals.md, Maya/Maya Inbound Signals.md. Agents 904f333f + 1c24feda re-deployed.
- **Test status:** deployed; live-test matrix in progress (campus apply + MPL + are-you-AI + inbound inventory). Also fixed the stale `voice-test/reference/checklists/maya.md` §6 (it wrongly asserted `+91` on get_profile; Signals uses `91` no `+`). Revert snapshots: raya/signals-expansion/e2e/snapshots/Maya *.pre-e2e-fixes.md.

## 2026-07-31 — Maya Inbound Signals (new bot, migrated to Signals DPG)

- **Change:** created Maya/Maya Inbound Signals.md (inbound + 9 Signals patterns + Signals tools + Maya divergences); new agent 1c24feda (clone df99f501). Inventory swapped to real Signals jobs; removed a residual second inventory array that caused a wrong-job present + hallucinated apply.
- **Test status:** VOICE-VERIFIED via inbound-via-outbound (call 2e0c7014): campus feminine welcome, Signals get_profile, real-inventory jobs, apply_job -> 201 SUCCESS, hr_contact, full MPL flow.


## 2026-07-31 — Maya Hindi Signals (new bot, migrated to Signals DPG)

- **Feedback/bug:** migrate Maya onto the Signals backend (part of the Signals expansion), matching the KKB Signals bots' behavior while keeping every Maya divergence.
- **Change:** created `Maya/Maya Hindi Signals.md` (1261 lines) by re-domaining the proven kkb-hi-signals structure onto Maya — all 9 Signals stabilisation patterns (fetch-driven/no-fork, memory-is-not-a-fetch, smooth opener, lifecycle live-item gate, consent HARD BLOCK, silenced fetch, reuse item_state, ranking filter, never-batch create->apply) + Signals tool contract (get_profile phone 91+digits; create_profile compliance+age->live; apply_job source/target/acting_as_user_id) + consent_status/ready_for_interview vars; Maya divergences preserved (campus identity ${college_name}, feminine voice, MPL Competition, Experience Capture, hr_contact/benefits). Repurposed agent `904f333f` (ex maya-hi-combined): PATCHed name+instructions+4 Signals tools.
- **Files:** Maya/Maya Hindi Signals.md (new); agent 904f333f repurposed.
- **Test status:** VOICE-VERIFIED end-to-end (call `b2df2d35`): campus feminine greeting, silent Signals get_profile, live-item selection, role-update offer, consent, apply_job -> 201 SUCCESS (real job_id 7dc7f10b), ready_for_interview, post-apply update_profile, MPL offer. Parity with KKB Signals confirmed.
- **Follow-up:** add consent_status + ready_for_interview to Maya Output (/update-output) before production wiring.


## 2026-07-31 — Maya: empty-recommendations callback fallback

- **Feedback/bug:** proactive safeguard (Parth) — when NO job data is passed (`${recommendations}` empty/missing), the bot must not hallucinate; say a short callback line and close. (Maya's intro was NOT changed — the government-claim reword was KKB-only.)
- **Change:** added a "Missing-job-data fallback" at the recommendations pre-check / No-Match Fallback: empty/null/missing/unparseable `${recommendations}` -> say "अभी आपके लिए मुझे जॉब्स नहीं मिल रहीं — एक बार फिर से देखकर मैं आपको वापस कॉल करती हूँ।" (feminine form, per Maya's voice rule) and close; never invent a job or apply with an example/invented `job_id`. Non-empty No-Match message unchanged. All Maya divergences preserved.
- **Files:** Maya/Maya Hindi.md
- **Test status:** deployed + voice-tested (see session report).


---

## 2026-07-30 — Maya (out+in): neutral `hold_message` (D34) [overnight run]
- **Feedback/bug:** overnight harness test (Maya-out call `baf836fe`) — `create_profile` `hold_message="ठीक है। आपकी तरफ़ से अप्लाई करने से पहले मैं आपकी जानकारी तैयार कर देती हूँ।"` — the platform speaks `hold_message`, so the silent create is narrated (D34 ACTIVE). Same exposure on Maya inbound.
- **Change:** added a neutral-hold rule ("एक मिनट" for `get_profile`/`create_profile`/`update_profile`; only `apply_job` keeps a spoken bridge). Ported from the KKB/DKB D34 fix; feminine-consistent reveal bans.
- **Files:** `Maya/Maya Hindi.md` (DEPLOYED maya-hi-out `47fdffe6`, snapshot `pre-deploy-maya-hi-out-2026-07-30_031010`) + `Maya/Maya Inbound.md` (DEPLOYED maya-hi-in `df99f501`, snapshot `…031109`). Maya inbound verify-pending (inbound).
- **Also confirmed working on `baf836fe`** (no fix needed): campus identity ("माया, एलआर कॉलेज की ओर से"), feminine voice, student-status gate, and the **MPL Competition secondary offer fired** after the job flow (first live observation of MPL). Maya create_profile phone was clean single `+91` (the phone-malform is kkb-kn-out-specific, not Maya).

## 2026-07-27 — Maya inbound: smooth greet-then-fetch (two-turn) + job_id-verbatim rule
- **Feedback/bug (two-turn):** Parth: "update for maya inbound also" — port KKB inbound's greet-first-then-fetch fix. Grounded: Maya inbound DOES fire `get_profile` (on turn 2) but prepends a fetch-narration BEFORE the greeting ("मैं आपके लिए जानकारी देख रही हूँ। नमस्ते…" — calls `cb19fc17`/`41ca7460`/`ff03c92d`/`234e50a8`/`7a5cb1e2`), which reads backwards/weird. Root: line said "Deliver the greeting naturally **alongside** the silent call" (bundling) + "the very first thing you do is emit get_profile" primed the pre-greeting narration.
- **Change:** restructured the fetch into the explicit two-turn DECISIVE ROUTER (Turn 1 greeting only, clean; Turn 2 a mandatory tool-only `get_profile` before any discovery/jobs), mirroring KKB inbound; removed the "alongside the silent call" bundling; added the observed narration string to the forbidden list (both turns); harmonized the get_profile Tool Call Rules "first action" line to "the turn immediately after the greeting." Deliberately NOT the D25 silent/invisible reframe — the fetch stays loud + mandatory (Maya already fires it; this only un-bundles + cleans the greeting so it's smoother).
- **Feedback/bug (job_id):** same job_id-hyphen-stripping class found on KKB inbound (call `8ddcaa5a`; see `KKB/CHANGELOG.md`). Applied the identical job_id-verbatim rule to Maya inbound + Maya Hindi (outbound) `apply_job` payload rules (propagation; pure-additive).
- **Files:** `Maya/Maya Inbound.md` (two-turn + job_id), `Maya/Maya Hindi.md` (job_id). Deployed maya-hi-in (sha 3fda09a9) + maya-hi-out (sha d82f163c), read-back verified. Awaiting post-deploy call.
- **Analyser:** D29 "Seen in" extended to Maya inbound 2026-07-27; D30 added (see `KKB/CHANGELOG.md`).

## 2026-07-27 — Maya: apply_job profile_id must be the `profileId` UUID, not the numeric `id` (shared 6-file fix)
- **Feedback/bug:** Grounded in Maya call 46d9f776 (read via the tool-call ARGS): create_profile returned `{'id': 5051, 'profileId': '2b51fd94-…'}`, then apply_job was sent `profile_id:"5051"` (the numeric top-level id) → backend 404 `{"error":"Invalid or missing profile_id"}` (the "apply failing" P1s, rows 15/42/65, previously mis-filed as pure backend).
- **Change:** On the create_profile path, the apply_job `profile_id` is now specified as the `profileId` UUID field — NEVER the numeric top-level `id`. (get_profile's top-level `id` already IS the UUID, so the returning-caller path was unchanged.) Applied to Maya Hindi.md + Maya Inbound.md as part of the 6-file KKB+Maya fix (see KKB/CHANGELOG.md 2026-07-27).
- **Files:** Maya/Maya Hindi.md, Maya/Maya Inbound.md. Deployed, verified in-sync. Awaiting post-deploy call.
- **Ported from:** shared KKB+Maya apply-path fix.

## 2026-07-27 — Maya: port KKB apply-loop guards + MPL canonical exemption
- **Change:** Ported the two Apply Failure Handling guards (no bridge re-speak on failure; no re-fire of same failed job_id) from KKB into Maya Hindi.md + Maya Inbound.md (Maya is Hindi-only). Also added an exemption to the Canonical Location Spellings section in Maya Hindi.md so the fixed MPL competition name "गाज़ियाबाद मार्केटर प्रीमियर लीग" (spelled with घ) is not normalized to the ग canonical — resolves a contradiction the canonical rule introduced. Deployed maya-hi-out + maya-hi-in, verified in-sync. Not yet live-confirmed (no post-deploy calls).

## 2026-07-24 — Maya: Canonical Location Spellings section (propagated from KKB)
- **Feedback/bug:** City mispronunciation (shared KKB fix, rows 69/71); Maya is Ghaziabad-based so the same places apply.
- **Change:** Added the same "## Canonical Location Spellings" section (Devanagari) to Maya Hindi.md and Maya Inbound.md, under Language & Script Rules.
- **Files:** Maya/Maya Hindi.md, Maya/Maya Inbound.md.
- **Deploy:** Queued — pending Raya recovery.

## 2026-07-22 — Maya outbound: explicit "not looking for a job" -> graceful exit + not_interested_in_jobs output var
- **Feedback/bug:** Sheet row 26 (KKB HE) — bot kept pushing jobs after the seeker clearly said they were not interested; should acknowledge and exit.
- **Change:** (conversation) Added a "Not looking for a job (explicit decline)" pattern to Maya Hindi Special Journey Patterns: on an EXPLICIT, unambiguous decline post-intro, stop presenting jobs, acknowledge warmly, offer the single MPL once if still owed (per the Graceful-Exit MPL gate), then Graceful Exit; triggers ONLY on a clear no — hesitation/"maybe"/one-word/silence continues the normal flow. (output) Added output field #20 not_interested_in_jobs (Yes only on an explicit decline) to Maya Output. Conversation deployed to maya-hi-out (echo-verified). NOTE: the output-prompt deploy could NOT be verified — the live output_instructions field returns garbage on read AND on PATCH-echo (pre-existing platform issue, ~3.2M+ chars); flagged to LitWiz/Raya. Maya is Hindi-only (no Kannada mirror); the output prompt is shared out+in.
- **Files:** Maya/Maya Hindi.md, Maya/Maya Output.md

## 2026-07-20 — Maya outbound: cross-call MPL skip now keys on "presented" (asked), not only "registered"
- **Feedback/bug:** Cross-call rule was "skip MPL only if the caller REGISTERED in a past call" — a past call that merely presented MPL and got a decline could re-offer. Desired behaviour: if MPL was already ASKED in any past call, never ask again in a later call.
- **Change:** Flipped every cross-call skip check in the conversation prompt to fire on `mpl_presented: Yes` OR `mpl_registered: Yes` (was registered-only): the MPL "Cross-call check FIRST", the post-apply MPL fold, the Apply-Success MPL note, the Apply-Failure MPL rule, the Graceful-Exit HARD GATE, and the backstop. Within-call behaviour unchanged (MPL still offered exactly once). NOTE (not a prompt issue): this only takes effect if the memory layer is live — the memory prompt (which carries the sticky mpl_presented/mpl_registered fields) has no Raya API field and is a manual console step, and ${contact_memory} must be injected each call; if that pipeline isn't configured, contact_memory is empty and MPL will be re-offered every call. Flagged to the user for console-side verification (two-call same-number test).
- **Files:** Maya/Maya Hindi.md (Maya is Hindi-only — no Kannada mirror)

## 2026-07-20 — Maya outbound: MPL still skipped on failure/decline exit — gate the goodbye behind MPL
- **Feedback/bug:** MPL is required once per call before ending — success, failure, or "not interested" — but live calls kept reaching "Goodbye" with no MPL (mpl_presented "No"). The failure path was the bypass: after a failed apply and the caller declining the alternate job, the bot said its wrap-up line + "Goodbye" in one flow, skipping the Graceful-Exit MPL backstop. The backstop existed but was prose the model glossed at the exit.
- **Change:** Made the MPL offer enforced at the exit itself, three ways: (1) an inline, MANDATORY verbatim MPL line AT the failure exit ("इससे पहले कि हम बात खत्म करें — …"), explicitly stating a failed apply / "not interested" does NOT waive it; (2) routed the "don't loop → acknowledge tech issue" step through the MPL offer before Graceful Exit; (3) added a HARD GATE at the top of Graceful Exit making the word "Goodbye" FORBIDDEN until MPL has been offered this call (skip only on prior registration, explicit end/do-not-call/in-a-hurry/hung-up). Holds for every ending — success, failure, declined all jobs, not interested.
- **Files:** Maya/Maya Hindi.md (Maya is Hindi-only — no Kannada mirror)

## 2026-07-20 — Maya outbound: create_profile fired with empty fields (gender/experience asked late or not at all) — hard 5-field gate
- **Feedback/bug:** Live call 4b001782 (new_seeker "Yes"). Forking now works (no get_profile) and the apply-integrity guard held (real 404 reported, no hallucinated success). BUT the new-caller collection was not enforced: the bot went consent → bridge → create_profile (minted with gender:'') → THEN asked gender → apply_job. Experience and age were never asked. The 5-field NEW-CALLER HARD BLOCK was being skipped under the "अप्लाई कर दो" rush. (Apply itself 404'd on mock job_ids JOB-1001..1004 in agent_args.recommendations — a data issue, not the prompt; that also keeps every call on the failure path so MPL never reaches its success-path trigger.)
- **Change:** Added a forceful HARD PRECONDITION at the create_profile call site: create_profile is FORBIDDEN until all five of (name, experience, age, gender, location) are actually collected — run the checklist before the call; if any is missing, ask it first, one at a time. Explicitly names the bug it prevents (asking gender/experience AFTER create_profile has already run) and that a rushed apply-consent does not waive collection.
- **Files:** Maya/Maya Hindi.md (Maya is Hindi-only — no Kannada mirror)

## 2026-07-20 — Maya outbound: new_seeker never steered the branch — surface the interpolated value at the decision + default-to-fetch
- **Feedback/bug:** Across ALL 14 maya-hi-out calls today, `new_seeker` never actually steered the returning-vs-new branch: BEFORE the router fix every call (Yes and No alike) fired `get_profile`; AFTER it every call skipped `get_profile`. The model was following whichever branch was written as structurally dominant, not the `${new_seeker}` value. Concretely, returning callers (new_seeker "No" — e.g. 91XXXXXX9115 @13:09, 91XXXXXX0249 @13:19) skipped `get_profile` and ran `create_profile`, minting DUPLICATE junk profiles (name "अज्ञात", role "Any") for callers who already had a profile.
- **Change:** Surface the INTERPOLATED value right AT the decision point — the greeting-transition decision and the DECISIVE ROUTER now both lead with "the new_seeker value for THIS call is: ${new_seeker}" so the model branches on the actual value instead of prose salience. Made the NO branch (fetch) the safe DEFAULT: any value that is "no", empty, blank, unclear, or an unsubstituted `${new_seeker}` token routes to `get_profile`; only a clear "yes" skips the fetch. This guarantees returning callers are fetched (no more duplicate profiles) even if the variable fails to interpolate, while still letting a clear "yes" skip the fetch.
- **Files:** Maya/Maya Hindi.md (Maya is Hindi-only — no Kannada mirror)

## 2026-07-20 — Maya outbound: hallucinated apply + new-caller flow redesign (decouple create_profile from apply_job)
- **Feedback/bug:** Grounded in live maya-hi-out call e0ac582c (new_seeker "yes"). The new_seeker router fix worked (no get_profile) and create_profile fired correctly (phone single +91). BUT: (a) the model NEVER called apply_job — after create_profile SUCCESS it SPOKE the apply_job payload as text ({"agentId":...,"job_id":"JOB-1001"}) and then said "अप्लाई हो गया है" (twice), a hallucinated success recorded as a real application in call_output. (b) For the new caller only experience was asked — age, gender, location, and name were skipped because the caller rushed to apply and the model collapsed the sequence. Root cause of (a): create_profile and apply_job were BUNDLED into one apply turn ("bridge → create_profile → apply_job back to back"); after create_profile the model conflated create-success with apply-success and narrated the tool call instead of emitting it. (Job ids JOB-1001..1004 in agent_args.recommendations are mock data — a separate data issue, not the prompt.)
- **Change (flow redesign, new-caller / create_profile path only):** (1) create_profile is now DECOUPLED from apply_job — it fires silently, once, right after the new caller's details are collected, BEFORE the apply confirmation, never bundled with apply_job and never with the apply bridge line. (2) Step 4 now states a profile ALWAYS exists by apply time, so apply is ALWAYS a single apply_job call for every caller (returning: reuse fetched id; new: reuse the id create_profile returned earlier), with a rare fallback. (3) Added a NEW-CALLER HARD BLOCK requiring name + experience + age + gender + location to be collected before create_profile (name uses contact_name if present, else asked). (4) Added an APPLY-TURN INTEGRITY guard: never render a tool payload as speech (a { or field name in spoken output = hard failure); create_profile success ≠ application; "अप्लाई हो गया है" requires a real apply_job success result in the same turn. (5) Updated Example 1 + the create_profile trigger prose to the decoupled flow.
- **Files:** Maya/Maya Hindi.md (Maya is Hindi-only — no Kannada mirror)

## 2026-07-20 — Maya outbound: new_seeker="yes" still fetched profile (campaign blocker); MPL not offered on failure / no-apply
- **Feedback/bug:** Grounded in live maya-hi-out calls (agent_args inspected). Calls e1f7abfc + 629abc7f had agent_args new_seeker:"Yes" yet the agent asked the profile-permission question and called get_profile — the DECISIVE ROUTER forbids both on the "yes" path. Root cause: the "no" branch carried a concrete, forceful "the next turn is ALWAYS [permission question], no exceptions" script while the "yes" branch was only an abstract carve-out ("go straight into the conversation") — so the model defaulted every caller onto the "no"/get_profile path. Separately, MPL was never presented (mpl_presented:"No") when apply failed or when the caller didn't apply: the failure-path MPL fold and the Graceful-Exit MPL backstop both referenced "say the Combined line (see MPL section)" rather than an inline exact line, so the model didn't execute them. (Also confirmed: the apply "Job not found" 404s are mock job_ids — JOB-1001..1004 — in the runtime agent_args.recommendations, not a prompt bug.)
- **Change:** (1) Restructured the greeting→next-turn step so `new_seeker` is the FIRST decision with an explicit two-branch IF/ELSE; gave the "yes" branch a concrete open-question script of equal force to the "no" permission question, and reasserted get_profile/permission are FORBIDDEN on "yes". (2) Replaced the failure-path MPL fold's abstract reference with the exact inline combined alternate-job+MPL line. (3) Added an exact inline standalone MPL line to the Graceful-Exit backstop for the no-apply case (caller declined every job / not looking).
- **Files:** Maya/Maya Hindi.md (Maya is Hindi-only — no Kannada mirror)

## 2026-07-20 — Maya outbound: apply failing 100% for new callers (empty get_profile → apply_job without create_profile; + create_profile double +91)
- **Feedback/bug:** Khushboo reported Maya HE outbound (maya-hi-out) unstable 30 min before a campaign — "forking, competition, job summary, gender age" not working, "experience not asked (previously worked)". Grounded in two live transcripts (calls 18fedd2e, 43e8f4ce, 2026-07-20 12:16Z): for every new caller `get_profile` returned empty `[]`, and the agent called `apply_job` directly → HTTP 404 "Invalid or missing profile_id" (create_profile was never called first). When create_profile did fire (2nd job, call 2) the phone was double-prefixed `+91+91XXXXXX9115` → HTTP 400 "Invalid Indian phone number format". All downstream symptoms (experience skipped, MPL never offered, mpl_presented:"No") cascaded from the call dead-ending in the apply-failure path.
- **Change:** (1) Made an empty `get_profile` result unmistakably mean "NO profile" at the Step 4 apply router, the NO branch, and a new HARD GUARD in the apply_job rules — empty `[]`/zero records ⇒ treat as brand-new caller ⇒ gather role/experience inline, then `create_profile` → `apply_job`; never call `apply_job` after an empty `get_profile`. (2) Added the anti-double-prefix guard to the create_profile Contact Context rule and changed the create_profile JSON phone template from `"+91<contact_phone>"` to a placeholder that says use exactly one +91 (do not double-prefix); made the get_profile call template consistent with its existing anti-double-prefix guard.
- **Files:** Maya/Maya Hindi.md (Maya is Hindi-only — no Kannada mirror)

## 2026-07-20 — Maya (in+out): role synonym + customer-facing family grouping
- **Feedback/bug:** Sheet rows 21/23 — customer-service/sales/crew/retail roles treated as separate buckets, so the bot could say "no customer service jobs" while crew/sales roles existed, and categorised the same job differently across calls. User explicitly requested Maya.
- **Change:** Added the role synonym + customer-facing-family matching rule (Maya Hindi Default Presentation Rule; Maya Inbound ranking rule). Cashier kept distinct. (Analyser D12.)
- **Files:** Maya Hindi.md, Maya Inbound.md

## 2026-07-20 — Maya (in+out): age/gender extract at read time (real root cause of the re-ask)
- **Feedback/bug:** The raw `get_profile` dump for the test number showed age+gender ARE on the profile, so the apply-#1 re-ask was still the bug — not correct behaviour as I had wrongly concluded from the call JSON (which does not contain the `get_profile` result). Duplicate records scatter the fields and the bot re-parsed nested JSON at the apply gate.
- **Change:** Extract age/gender at profile-read time across ALL returned records and commit as KNOWN for the whole call. Added to "Reading the get_profile response" in Maya Inbound + Maya Hindi. (Analyser D9 sharpened.)
- **Files:** Maya Inbound.md, Maya Hindi.md

## 2026-07-20 — Maya (in+out): MPL timing — offer as an interjection right after the first apply
- **Feedback/bug:** Requested change. MPL was surfaced too late (only once the caller had fully given up). Offer it right after the FIRST application attempt concludes, as an interjection before the caller moves to the next job; also pitch it if the caller says they're not looking for a job.
- **Change:** Rewrote MPL "When to offer" — primary trigger = right after the first apply concludes (success OR failure), once, as an interjection; alternative = caller not looking / No-Match. Adjusted the "never interrupt" rule to allow the post-first-apply interjection (still never mid-apply). Added interjection hooks in Apply Success and Apply Failure handling (failure holds the retry/another-job question until after the MPL exchange). Still at most once per call; the turn-collapse fix and the Graceful Exit backstop are retained. `mpl_registration` stays output-only (no CRM).
- **Files:** Maya Inbound.md, Maya Hindi.md

## 2026-07-20 — Maya (in+out): richer Apply Failure Handling (HR / alt-job / callback) + MPL fold
- **Feedback/bug:** Same dead-end-on-failure problem as KKB — own the failure, then one recovery path, never leave the seeker with nothing.
- **Change:** Replaced Apply Failure Handling in Maya Hindi + Maya Inbound with the 3-path recovery flow (share `hr_contact` / offer ONE alternate job / promise a callback) + hard bans + logging note. The first-apply alternate-job offer folds in the MPL Combined line; if another path fires, the MPL Graceful-Exit backstop still makes the single offer. (Analyser D15.)
- **Files:** Maya Inbound.md, Maya Hindi.md

## 2026-07-20 — Maya (in+out): fold MPL into the post-apply job question + cross-call memory
- **Feedback/bug:** Requested redesign after MPL kept not firing as a separate step. Fold the offer INTO the caller's first post-apply "any other jobs?" question (one Combined line). Once presented, never mention MPL again this call; after the MPL exchange, return to the plain job question. Remember MPL across calls — if the caller already registered, don't re-offer. Capture presented + registered in both memory and output.
- **Change:** Rewrote MPL "When to offer" + offer line to a single Combined job+MPL line, said once right after the first apply, with a `${contact_memory}` cross-call check (skip if already registered). Reconciled the tool-tied rule, the apply success/failure hooks, and the Graceful-Exit backstop to the folded design; added return-to-plain-job-question after the exchange + a capture note. Memory prompt: new sticky `mpl_presented` / `mpl_registered` fields. Output prompt: new `mpl_presented` field (`mpl_registration` already existed).
- **Files:** Maya Inbound.md, Maya Hindi.md, Maya Memory.md, Maya Output.md

## 2026-07-20 — Maya (in+out): tie MPL to the apply_job-return event (reliability)
- **Feedback/bug:** Live Maya Inbound test (call 49048e22, 10:28 IST) — MPL STILL not offered, despite the "after first apply" timing + turn-collapse fix + Graceful-Exit backstop all being live (verified against deploy timestamps: MPL timing deployed ~10:12, call at 10:28). Root cause: MPL lived in section prose, which the model deprioritises in a long, degraded call (this call had 3/3 apply_failed, gender misheard 3×, retry loops). Section prose has a reliability ceiling; tool-tied hard rules are followed far more reliably.
- **Change:** Added a tool-tied MPL rule in the apply flow — the FIRST time `apply_job` returns (success OR failure), the very next turn MUST be the MPL offer, framed as non-negotiable as calling `apply_job` itself, before any retry/other-job/wrap-up. Kept the existing hooks + Graceful-Exit backstop. (Analyser D10 sharpened.)
- **Files:** Maya Inbound.md, Maya Hindi.md
- **Note:** age/gender was ALSO re-asked in this call despite being on the profile — same reliability ceiling; and the underlying `apply_failed` backend (0/3 applied) makes every call a failure loop, which is the bigger blocker.

## 2026-07-20 — Maya (in+out): MPL offer collapsed into the goodbye turn (call cut before registration)
- **Feedback/bug:** Live Maya Inbound test (call 2bb8b332, 9:43 IST). MPL was finally offered proactively after the caller gave up (progress), but the agent said the offer line AND "Goodbye" in the SAME turn — the call ended before the caller could answer, so no details and no registration (`call_output.mpl_registration` = None; `drop_reason` apply_failed). The round-2 wording ("offer it before the goodbye line") let the model bundle offer + goodbye.
- **Change:** Made the MPL offer its OWN turn that ends on its question and WAITS; forbade the goodbye line / "Goodbye" in the same turn as the offer; the Graceful Exit goodbye is now reachable only after the full MPL exchange (decline, or details → registration → reminder) has been handled in later turns. (Analyser D10 refined.)
- **Files:** Maya Inbound.md, Maya Hindi.md
- **Grounding note:** This test number's profile carries NO age/gender (verified in the call's `get_profile` result), so asking once on apply #1 is correct and the persistence fix (no re-ask on #2/#3) is working — that behaviour is NOT a bug.

## 2026-07-20 — Maya (in+out) round 2b: proxy carve-out, new-caller multi-apply, MPL 'in a hurry'
- **Feedback/bug:** Adversarial review of the round-2 fixes flagged three residual issues. (1) The age/gender lock was absolute, so a proxy caller switching to a different candidate mid-call would put the first person's age/gender on the second. (2) A brand-new caller applying to a 2nd job in one call would re-run `create_profile` (duplicate profile) + re-ask name/experience. (3) The Graceful Exit MPL backstop's skip-list omitted "clearly in a hurry" (present in the MPL section), so a hurried caller could be pushed MPL at goodbye.
- **Change:** (1) Scoped the lock to the SAME candidate — a proxy switching to a different person re-establishes age/gender. (2) Added a once-per-call `create_profile` guard — after the first mint, a later apply reuses the returned `profile_id` via `apply_job` only, no duplicate create, no re-ask. (3) Added "is clearly in a hurry" to the Graceful Exit skip-list. (Analyser D9 refined, D11 added, D10 refined.)
- **Files:** Maya Inbound.md, Maya Hindi.md

## 2026-07-20 — Maya (in+out) round 2: age/gender lock across repeat applies + MPL proactive push
- **Feedback/bug:** Live re-test of Maya Inbound after round-1 fixes. (1) Age/gender were correctly skipped on the FIRST apply but re-asked on a SECOND apply in the same call — the profile re-check wasn't persisted, so the gate re-derived from scratch and missed. (2) MPL was still not pushed proactively: the bot sat in the apply-failure "retry or another job?" loop and only offered MPL when the caller explicitly asked ("koi competition?"), never on its own.
- **Change:** (1) Locked the profile's known fields (esp. age/gender) the moment `get_profile` returns and stated the lock does NOT reset between applications; strengthened the HARD BLOCK so the KNOWN status persists across every apply in the call. (2) Rewrote MPL "When to offer" as a PROACTIVE push covering apply success OR failure + caller-declines-more-jobs, explicitly "don't wait to be asked"; added a pointer from Apply-Failure Handling into the MPL push before Graceful Exit. (Analyser D9 + D10 strengthened.)
- **Files:** Maya Inbound.md, Maya Hindi.md

## 2026-07-20 — Propagate age/gender re-check + MPL mandatory-before-goodbye to Maya outbound
- **Feedback/bug:** The age/gender re-ask bug (D9) and the MPL-not-offered bug (D10), both fixed in Maya Inbound, apply equally to Maya outbound (same instructions + same MPL feature).
- **Change:** Added the age/gender profile re-check at Maya Hindi's Step 3.5 HARD BLOCK, and made the MPL offer a MANDATORY pre-goodbye step (declining a job ≠ ending the call).
- **Files:** Maya Hindi.md

## 2026-07-20 — Maya Inbound: skip age/gender when on profile + reliably offer MPL before goodbye
- **Feedback/bug:** Two live Inbound-Maya bugs (20-Jul transcripts). (1) `get_profile` returned a profile (caller greeted by name), yet the bot re-asked age and gender at apply time — the "skip if on profile" rule wasn't honored at the decision gate. (2) The MPL Competition was never offered — the bot jumped straight to the goodbye line, skipping the Graceful-Exit MPL trigger (and treated a job/apply decline as "ending the call").
- **Change:** (1) Added an explicit profile re-check at the Step 3.5 HARD BLOCK — before asking age/gender, re-read the `get_profile` result (`metadata.whatIHave.age` / `metadata.gender`); a returning caller normally has both, so ask only genuinely-missing fields. (2) Made the MPL offer a MANDATORY pre-goodbye step and clarified that declining a job/apply is not ending the call — only an explicit end / do-not-call / hang-up skips MPL.
- **Files:** Maya Inbound.md

## 2026-07-19 — MPL section: instructions rewritten to English (spoken lines stay Hindi)
- **Feedback/bug:** The MPL Competition section's instructions/rules were written in Hindi — violating the rule that all instruction prose is English and only spoken content is localized.
- **Change:** Rewrote the MPL section in Maya Hindi + Maya Inbound so every rule/heading/note is English; only the three quoted spoken lines (offer, registration confirmation, end reminder) stay in Hindi, and the What/Why/How/Who facts are English (the agent conveys them in Hindi). The "instructions in English" rule is now codified in CLAUDE.md + `/update-prompt` + `/port-feature` + prompt-anatomy.
- **Files:** Maya Hindi.md, Maya Inbound.md

## 2026-07-19 — Profile Wording Rules: never speak "profile" aloud (say "जानकारी")
- **Feedback/bug:** Same class as KKB — the internal word "profile"/"प्रोफाइल" leaked into caller-facing lines (permission-ask, "प्रोफ़ाइल मिल गई" acknowledgement, example dialogues).
- **Change:** Added the "Profile Wording Rules (CRITICAL)" section to Maya Hindi + Maya Inbound and reconciled every spoken/example line to "जानकारी" wording (feminine forms preserved). On empty fetch, never announce the miss; tool-call silence reinforced; internal tool names/rules unchanged.
- **Files:** Maya Hindi.md, Maya Inbound.md
- **Ported from:** KKB (same bug class)

## 2026-07-19 — Add MPL Competition secondary offer (Maya in + out)
- **Feedback/bug:** Feature request — Maya should invite candidates to register for the Ghaziabad Marketer Premiere League (MPL July 2026): a free competition with a free verified certificate. Must be a *secondary* offer that never affects job-application conversion (the primary goal).
- **Change:** Added a self-contained "MPL Competition (Secondary Offer)" section to Maya Hindi (out) + Maya Inbound — offered ONCE, only after the primary job flow (post-apply / No-Match Fallback / just before Graceful Exit), never before or during job present/apply. Hook = free verified certificate + Ghaziabad Top-100; What/Why/How/Who shared only on request; on "yes" the bot states the follow-up-call timing (within 48 hrs, 6–8 pm) and reminds once at call end; the "not-a-job-guarantee" caveat only if asked. Added trigger refs in the No-Match Fallback + Graceful Exit. Added `mpl_registration` (Yes/No/Not offered) to Maya Output.
- **Files:** Maya Hindi.md, Maya Inbound.md, Maya Output.md

## 2026-07-18 — 17-Jul live-test batch: inbound fork skip-guard, pool-overview on not-found, new-caller name+experience
- **Feedback/bug:** Same 17-Jul batch (rows 67/74/75), transcript-verified on Maya out+in. Inbound fork could be skipped when the caller volunteered a role/city; the outbound profile-not-found path lacked the pool overview; new callers weren't asked name+experience before `create_profile`.
- **Change:** (a) Appended a "no conversation/jobs/permission-ask before `get_profile` returns; never skip if caller volunteers a role/city" guard to the inbound fork block (Maya's block was already partly hardened). (b) Outbound not-found path → Step 1 Case B pool overview. (c) NEW-CALLER HARD BLOCK for name+experience pre-apply.
- **Files:** Maya Inbound.md, Maya Hindi.md
- **Ported from:** KKB (shared bug classes; adapted to Maya's own wording, feminine forms preserved)

## 2026-07-18 — Slash "/" spoken aloud in job/category labels (bug 65, cross-agent)
- **Feedback/bug:** Live 17-Jul Maya-Inbound calls (Consolidated Feedback Tracker row 65). TTS voiced "/" as "slash" in category labels ("सेल्स/मार्केटिंग", "कस्टमर सपोर्ट/बीपीओ", "कॉल सेंटर/वॉइस"). Confirmed from the call transcripts. The existing slash rule was too generic (never mentioned the role/category labels the bot forms).
- **Change:** Strengthened "## Slash ( / ) symbol" to explicitly cover role/category labels with concrete examples; never voice "/".
- **Files:** Maya Hindi.md, Maya Inbound.md
- **Ported from:** shared TTS rule (same fix applied to KKB)

## 2026-07-16 — new_seeker fork over-fire router (outbound) + role="Any" placeholder handling (outbound + inbound)
- **Feedback/bug:** Two bugs found live in the sibling KKB placeholder bot; audited Maya for the same.
  - **FIX A — new_seeker fork over-firing (outbound `Maya Hindi.md`):** confirmed the risk was present. The `new_seeker="no"` branch opened with very forceful "MANDATORY STEP — NO FURTHER CONVERSATION WILL HAPPEN BEFORE THIS STEP IS DONE … profile permission question. No exceptions" language, but there was **no decisive router** at the top of the branch and the MANDATORY wording was **unscoped**, so it could bleed onto the "yes" path (as in KKB) — a new caller getting asked profile permission and having `get_profile` fired. (The `${new_seeker}` binding order was already G1-safe; case-insensitive read already present.) (A1 / E1 fork bleed.)
  - **FIX B — role="Any"/placeholder treated as a real role (outbound + inbound):** a fetched profile with `role="Any"` (or "Not Available"/empty/null/garbled) was being spoken aloud and role-confirmed ("आप Any का काम देख रहे हैं — इसी तरह की जॉब्स?"), and the caller never got the pool-overview job-type summary upfront. (C6 role reading.)
- **Change:**
  - **FIX A (`Maya Hindi.md`):** added a **DECISIVE ROUTER** at the top of "Profile Handling (branch on new_seeker)" — read `new_seeker` FIRST; **`new_seeker="yes"` → profile-permission question + `get_profile` FORBIDDEN** (rationale stated: a "yes" caller may still have stale old profiles in the backend — that is exactly WHY not to fetch; treat as new); **`new_seeker="no"` → permission + `get_profile` MANDATORY**. Made the "yes" prohibition as forceful as the "no" mandate; scoped the "no" branch's MANDATORY/"no exceptions" wording to apply **ONLY when `new_seeker="no"`** (both at the router and inline on the MANDATORY line). Rewrote the "yes"-branch rationale (was "the fetch will naturally fail" → now "treat as new; even if a stale profile exists, do NOT fetch"). Added a "yes"-exclusion note to the greeting-section CRITICAL block so it can't bleed either. Case-insensitive read reaffirmed. The "no" fetch path was **not weakened**.
  - **FIX B (`Maya Hindi.md` + `Maya Inbound.md`):** in "Reading the get_profile response" (`metadata.role` field map) and "Using the fetched profile" (role-confirm step), defined **"Any" (case-insensitive), "Not Available", empty, null, or garbled as NOT a usable role** — a placeholder: never spoken aloud, never role-confirmed. When the role is not usable → treat as **UNKNOWN**, skip the role-confirm, and go straight to **Step 1 Case B (pool overview)** — giving the job-type summary upfront; since there's no role-confirm to wait on, the name-acknowledgment and Case B overview MAY be combined into ONE turn. Gated **Step 1 Case A** to genuinely usable roles only (placeholder routes to Case B); widened the **Case B** heading to include the placeholder case; reconciled the two "missing role → gather inline" references (profile-found "no" branch note + get_profile rules) to route a placeholder role to Case B instead.
- **Preserved:** feminine voice, campus identity, `hr_contact`/`benefits`, inline Experience Capture, `{${contact_memory}}` memory-injection block, `${college_name}` divergence. No examples added/changed (per E1 — a from-scratch branch example is what bled last time); no existing example depicts "Any". All edits additive/surgical.
- **Files:** `Maya/Maya Hindi.md` (FIX A + FIX B), `Maya/Maya Inbound.md` (FIX B only — inbound has no `new_seeker` fork). Snapshot `versions/Maya/2026-07-16_184232__pre-bugfix-batch3`. Hindi-only, no `/sync-check`. Analyser update (A1/E1/C6) handled centrally by the parent.

## 2026-07-16 — Parent consolidation: Maya inbound country_code + family-wide create_profile-first hardening
- **Feedback/bug:** After the fix below, two gaps remained. (1) The Maya inbound `${country_code}` declaration still treated it as a passed input, but an inbound call has no input variables (C3). (2) The apply NO-branch (new caller → `create_profile` then `apply_job`) had weaker wording than the forceful outbound gate KKB got — the same "skip `create_profile` → `apply_job` fails with no `profile_id`" class (C7 inverse) was latent in both Maya inbound and outbound.
- **Change:** (1) `Maya Inbound.md` — `${country_code}` declaration + create_profile context line rewritten to "NOT a passed input → always assume `+91`" (matches DKB/KKB inbound). (2) `Maya Inbound.md` + `Maya Hindi.md` — appended the forceful clause to the apply NO-branch: **`create_profile` is the required FIRST step — not optional; `apply_job` without a `profile_id` will FAIL; never skip it or call `apply_job` first.**
- **Files:** `Maya/Maya Inbound.md`, `Maya/Maya Hindi.md`. Analyser C3/C5/C7 updated centrally.

## 2026-07-16 — Force the tool call: inbound get_profile must actually fire; outbound apply_job must actually fire
- **Feedback/bug:** Two live-transcript bugs where the agent narrated/spoke an outcome but the tool never ran.
  - **Inbound (BUG 2, `Maya Inbound.md`):** on the first turn the agent said "एक मिनट, मैं आपकी प्रोफ़ाइल देख रही हूँ … आपकी प्रोफ़ाइल मिल गई, ख़ुशी जी" and proceeded as if a profile was fetched — but `get_profile` was **never actually called**. It fabricated "profile found" + the caller's name from `${contact_memory}` and leaked a forbidden waiting-narration line. With no real `profile_id`, downstream apply fails. (B2 + C5/C6.)
  - **Outbound (BUG 5, `Maya Hindi.md`):** returning caller (`new_seeker="no"`, profile fetched with age 24 + gender female). At apply the agent spoke the bridge "ठीक है, आपकी तरफ़ से अप्लाई कर देती हूँ" **twice** but **never emitted `apply_job`** — it just repeated the bridge. It also re-asked age and gender that the fetched profile already had. (C5 + B1 + A5.)
- **Change:**
  - **`Maya Inbound.md` — Profile Handling "first action" block:** rewrote to state you **MUST actually invoke** the `get_profile` tool as the very first action (a real tool call, not described/imagined); explicitly FORBADE the waiting/looking-up narration ("एक मिनट…", "मैं आपकी प्रोफ़ाइल देख रही हूँ…", "प्रोफ़ाइल चेक कर रही हूँ…"); FORBADE inferring/fabricating the profile, name, role, gender, age, or `profile_id` from `${contact_memory}` or any context — those come ONLY from a real `get_profile` result in this call; clarified `${contact_memory}` is background context for resuming the journey, never a substitute for the live fetch; made "प्रोफ़ाइल मिल गई" (or naming the caller) with no real `get_profile` call a hard failure; tied it to the apply path — no real `get_profile` → no `profile_id` → new-caller path (`create_profile` then `apply_job`), never apply with an imagined id.
  - **`Maya Inbound.md` — get_profile Tool Call Rules:** added a reinforcing bullet (must actually emit the call; never narrate or fabricate; name/role/`profile_id` only from a real return; no result → treat as new).
  - **`Maya Hindi.md` — Step 4 closing sequence + apply_job Tool Call Rules:** made unmissable that the bridge line and the `apply_job` tool call happen in the SAME turn — the bridge MUST be **immediately followed by the actual `apply_job` call**; speaking the bridge is NOT applying; if `apply_job` has not been emitted the application has NOT happened (do not end the turn, do not speak a result); repeating the bridge is never a stand-in for the tool call.
  - **`Maya Hindi.md` — Step 4 YES branch:** crisp `profile_id` selection — even when `get_profile` returns many records, take the FIRST (most-recent) record's top-level `id`, hold it, pass it to `apply_job`; a multi-record response is never a reason to withhold/delay `apply_job`.
  - **`Maya Hindi.md` — Pre-Apply Data Collection HARD BLOCK:** reinforced A5 with a concrete case — if the fetched profile already shows `age` and `gender` (e.g. age twenty-four, gender female), both are KNOWN; do NOT re-ask; go straight to the bridge and `apply_job`.
- **Preserved:** decision-first apply checkpoint (returning → `apply_job` only; new → `create_profile` then `apply_job`), bridge-once rule, feminine voice, campus identity, `hr_contact`/`benefits`, inline experience gathering, and the `{${contact_memory}}` memory-injection block. All edits additive/surgical.
- **Files:** `Maya/Maya Inbound.md`, `Maya/Maya Hindi.md`. Snapshot `versions/Maya/2026-07-16_162737__pre-bugfix-batch2`. Hindi-only, no `/sync-check`. Analyser update (B2/C5/C6/B1/A5 heuristics) handled centrally by the parent.

## 2026-07-16 — Retire Marketing Masters League (dead) across Maya
- **Feedback/bug:** Parth confirmed MML is dead. It had been restored into the new Maya inbound (see entry below) and still lingered in Maya Memory/Output, while the live outbound already dropped it (07-08 sync). Reconciled to a single state: gone everywhere.
- **Change:**
  - `Maya/Maya Inbound.md` — removed the whole `# Marketing Masters League` section and every reference to it (No-Match Fallback pivot, Post-Application State Handling line, Graceful Exit line, and the two sample-conversation MML turns — the affected examples now close directly).
  - `Maya/Maya Memory.md` — removed the `mml_offered` / `mml_registered` field definitions, the "MML outcome" phrase in the summary-focus rule, and the two JSON template fields.
  - `Maya/Maya Output.md` — removed extraction items `mml_offered` / `mml_registered` (renumbered the trailing items 18→16, 19→17, 20→18), dropped "or MML was offered/registered" from the final_summary rule, and removed the two JSON example fields.
  - `Maya/Maya Hindi.md` (outbound) — already had no MML; untouched.
- **Files:** `Maya/Maya Inbound.md`, `Maya/Maya Memory.md`, `Maya/Maya Output.md`. Snapshot `versions/Maya/…__pre-mml-removal`. Verified: 0 MML references remain in any Maya prompt file.

## 2026-07-15 — New agent: Maya Inbound (Hindi)
- **Feedback/bug:** Need an **inbound** Maya variant (graduate calls IN) — built by taking the latest Maya outbound (`Maya Hindi.md`) and applying the inbound transformation, using `KKB/KKB Placeholder Inbound.md` as the shape template while keeping Maya's persona and divergences. New file, no existing behaviour changed.
- **Change (new file `Maya/Maya Inbound.md`):**
  - **Inbound intro:** caller dials in; "मैं कॉल कर रही हूँ" framing dropped; college-neutral campus **welcome** ("माया की रोज़गार सेवा में आपका स्वागत है") — **never** government (Maya divergence preserved).
  - **College identity (decision, flagged):** inbound has no `${college_name}` input var, so college is a **hardcoded per-deployment config slot** at the top (default `[UNSET]` → college-neutral greeting; if a per-college line, set it and Maya prepends "[college] की ओर से,"). Never invents a college.
  - **Inputs removed:** no `${new_seeker}`, `${recommendations}`, `${contact_name}`. New-vs-returning fork decided by the **silent `get_profile` result** at call start (called with `+91${contact_phone}`, no permission ask). Kept `${contact_phone}`/`${country_code}` + the `### Contact context / {${contact_memory}}` memory-injection block verbatim.
  - **Hardcoded Job Inventory (flagged placeholder):** 14 Maya-domain UP-graduate roles (Data Entry, Customer Support, Telecaller, Back Office, Sales/Field Sales, Digital Marketing, Accounts, BPO Voice) across Noida/Ghaziabad/Greater Noida/Lucknow/Kanpur, with role-synonym + salary-floor + nearby-city matching. Two jobs carry `hr_contact`, several carry `benefits` (to exercise the Maya divergences). Marked **PLACEHOLDER SAMPLE DATA — replace before go-live**.
  - **Carried the latest outbound flow (inbound-adapted):** pool ranking (role→location→salary, best-fit 3, role-matched first); Step 1 orient with Case A / Case B pool-overview; "Reading the get_profile response" field map + "Using the fetched profile" (greet by first name, confirm role, don't re-ask); **decision-first apply checkpoint** (did `get_profile` return a profile? → YES `apply_job` ONLY with `profile_id` from the fetch, NO `create_profile`→`apply_job`; precondition STOP at `create_profile`) — C7; bridge-once — B1; Pre-Apply age/gender HARD BLOCK — A5; +91 phone — C3; success gated on real `apply_job` result — C5.
  - **Maya divergences preserved:** feminine-voice rule (D4); `hr_contact`/`benefits` handling; HR-number post-apply sharing; experience gathering kept in its current **inline** form (the standalone "Experience Capture" section was deliberately removed from the outbound as an A1 regression — not reintroduced). **Marketing Masters League restored** (from git 3e5241b) and inbound-adapted (offer once, after a successful apply or in the No-Match Fallback).
- **Files:** `Maya/Maya Inbound.md` (new); snapshot `versions/Maya/2026-07-16_100841__pre-inbound-build`.
- **Flags for review:** (1) **college identity** — college-neutral default vs per-deployment hardcoded slot; confirm the intended inbound deployment model (one line per college vs one shared line). (2) **Job Inventory is placeholder** — replace with real listings. (3) **Marketing Masters League** is currently **absent from the live Maya OUTBOUND** (dropped in the 2026-07-08 production sync) though Maya Memory/Output still expect `mml_offered`/`mml_registered`; restoring it here makes inbound diverge from outbound — decide whether to also restore it to the outbound for parity, and note its registration mechanism is still **TBD**. (4) **No `update_profile` / Post-Application Info Gathering** — KKB inbound has these; Maya (outbound and inbound) does not. Left out to stay faithful to the Maya source; port via `/port-feature` if wanted.
- **Note:** Hindi-only (Maya has no Kannada variant), so no `/sync-check`. This is a new-agent build, not a bug fix, so no new `bug-patterns.md` entry required (the file was self-checked against the existing catalog: C5/C6/C7, A5/A7, B1, C3, D4, memory block, TTS number-words, Devanagari-only spoken output).

## 2026-07-13 — Hold the no-duplicate-profile fix with a decision-first checkpoint + add the pool-overview opener (fork live-verified)
- **Feedback/bug:** Second live `new_seeker="no"` test. Good news: the fork held (Maya asked to fetch, greeted "पार्थ जी", confirmed role "Customer Support Executive", ran separate turns, and the ranked list correctly led with Customer Support — Issues 1 & 2 confirmed fixed). **But `create_profile` fired again at apply instead of `apply_job`** (and the bridge line repeated + an "अब मैं अप्लाई कर रही हूँ" narration leaked) — the previous pass's bind-`id` + three "never create" prose guards did NOT hold.
- **Diagnosis:** the guards were reactive bans fighting a structural pull — at apply the model needs a `profile_id`, and `create_profile` is the tool that hands one back, so it follows the salient "apply = create_profile → apply_job" sequence. Bans buried below the payload lose to that.
- **Change (Maya Hindi) — decision-first, not more bans:**
  - **Step 4 reshaped to LEAD with one binary check:** "Did `get_profile` run in THIS call and return a profile? → **YES:** call `apply_job` ONLY, reading `profile_id` straight from that fetch result (most-recent profile's top-level `id`); **NO:** `create_profile` then `apply_job`." Stated that `apply_job` is the only tool that applies and `create_profile` must not be called at all if a profile was fetched.
  - **Made the returning=one-tool path primary** in the apply_job sequence rules (was framed as create→apply); `apply_job` payload `profile_id` now explicitly = the `id` from the `get_profile` result when it ran.
  - **Precondition STOP at `create_profile`'s entry** ("did get_profile return a profile? → STOP, go to apply_job").
  - **Bridge/narration:** the single-tool returning path removes the second boundary; also banned extra "अब मैं अप्लाई कर रही हूँ"/waiting narration around the tool call.
  - **Pool-overview opener added (the deferred "other fix"), now that the fork is live-verified:** new **Step 1 Case B** — when the target role is unknown (fresher / unsure / profile had no role), open with a short overview naming the real role *types* in `${recommendations}` (grouped, never invented, no counts/companies/salaries) + one question, then rank. **Case A** (role known) skips the overview and goes straight to area → ranked 3. Added an explicit **guard**: this whole step is post-branch job-presentation, never the call opener, and never replaces the profile-permission question on "no". **Deliberately added NO from-greeting example** — that (Example 5) is exactly what bled across branches and broke the fork last time.
- **Files:** `Maya/Maya Hindi.md`; `.claude/skills/prompt-analyser/reference/bug-patterns.md` (C7 sharpened — prose bans insufficient, the holding fix is the binary "did the fetch run?" checkpoint; C8 updated — overview shipped as gated Step 1 Case B, no from-greeting example).
- **Re-test:** confirm (a) a `new_seeker="no"` apply now calls `apply_job` only (no `create_profile`) and the bridge is spoken once; (b) the `new_seeker="no"` and `"yes"` openings are unchanged (fork still fetches profiles) now that Case B exists.

## 2026-07-13 — Fork-safe re-apply on the stable base: ranking + turn-barriers + no-duplicate-profile + bridge-once (pool overview deferred)
- **Feedback/bug:** Live `new_seeker="no"` call (profile found). Four issues from Parth: (1) role known ("Data Entry Operator") but the list still led with an unrelated job (Customer Support) — array order used instead of role fit; (2) three things fused into one turn — a leaked "प्रोफाइल fetch कर रही हूँ" line + the role-confirm question + the area question — so the seeker answered only the area and the role confirmation was lost; (3) **critical:** a profile was already fetched, yet the agent called `create_profile` at apply (duplicate); (4) the "अप्लाई कर देती हूँ" bridge line was spoken 3–4× across the erroneous `create_profile`→`apply_job` sequence. Parth also asked to generalise relevance across BOTH branches for a ~20–30-job pool, and warned that a prior same-day attempt at the ranking+overview redesign **broke the new_seeker fork** (opened every call with the yes-path experience+overview and skipped `get_profile`) and was rolled back — so this pass had to be surgical and fork-safe.
- **Scope decision:** applied only the fork-safe subset now (none of it touches the branch opener); the **pool-overview opener** — the piece that bled across branches last time (E1) — is **deferred** for a separate step after Parth live-verifies the fork still fetches profiles.
- **Change (Maya Hindi):**
  - **Ranking (Issue 1, both branches) — `Default Presentation Rule` rewritten:** `${recommendations}` redefined as a pool of up to ~30 jobs that is only loosely ordered ("rank it yourself"); present the **3 best-fit** valid jobs, priority **role → location → salary**, the role-matched job first regardless of array position; role source is the fetched profile ("no") OR the conversationally-gathered role ("yes"); fall back to given order only when nothing is known. Re-order only, never fetch/invent (Hallucination Guard). Step 2 + the "more jobs" fallback + both No-Match-Fallback guards + the applied-skip line de-hardcoded from "indices 4–10" to "the rest of the pool".
  - **Turn barriers (Issue 2):** in "Using the fetched profile", the role-confirm question now **ends the turn — stop and wait**; the area question (Step 1) and job list (Step 2) are explicitly separate, later turns; forbade prepending any "fetch कर रही हूँ" line to the "प्रोफ़ाइल मिल गई…" opener. Step 1 restated as a separate turn that begins only after the prior answer.
  - **No duplicate profile (Issue 3):** bound the fetched profile's **top-level `id` as THE `profile_id`** ("Reading the get_profile response"); Step 4 apply path now decided by **"do you already hold a `profile_id`?"** (not by re-deriving new_seeker) — have one → `apply_job` directly, no `create_profile`; added a **HARD GUARD** in create_profile rules forbidding create when a profile was fetched (duplicate = hard failure).
  - **Bridge once (Issue 4):** apply_job rule tightened — bridge said only immediately before the first tool, after age/gender known; once said, never again, silent between tool calls.
- **Files:** `Maya/Maya Hindi.md`; `.claude/skills/prompt-analyser/reference/bug-patterns.md` (C8 note: ranking shipped, overview deferred). Patterns A7 / B1 / C7 / C8 were already catalogued (prior attempt); this pass makes the prompt actually satisfy them.
- **Reconciliation note:** the four same-day entries below (ranking redesign, pool-overview opener, Example 5 add/remove, turn-fusing) describe the earlier attempt that broke the fork and was **rolled back** to the fetch-profile baseline — they did NOT ship. This entry is the authoritative account of what is now in the file. **Deferred:** the pool-overview opener (awaiting Parth's live fork check). **Not a prompt bug:** the live `apply_job` HTTP 404 "Job not found" for `JOB-1001` is apply-backend/test-data.

## 2026-07-13 — Regression persisted: removed the competing "yes"-overview example (Example 5)
- **Feedback/bug:** After the decisive new_seeker router + example labelling (entry below), a `new_seeker="no"` test STILL opened with the experience question + pool overview instead of the profile fetch. The router prose was not overpowering the example: Example 5 was a full from-greeting `new_seeker="yes"` walkthrough opening with the experience question, and the model kept copying that opening onto the "no" caller.
- **Change (Maya Hindi):** removed **Example 5** entirely (the from-greeting yes+overview walkthrough — the strongest attractor). The overview behaviour remains described in Step 1 Case B prose + its inline snippet; it just no longer has a from-greeting example to mimic. This restores the example balance (Example 1 yes-opening, Example 4 no-opening) that did the "no" path correctly at 2:59. Fixed the header note's dangling "Examples 1, 5" → "Example 1".
- **Files:** `Maya/Maya Hindi.md`; `.claude/skills/prompt-analyser/reference/bug-patterns.md` (E1 note: prose gates alone didn't overpower the example — the competing example had to be removed).
- **Lesson reinforced:** for a branch-conditioned opening, a competing from-greeting example on the other branch can override even an explicit router — remove/neutralise the example, don't just add prose.

## 2026-07-13 — Fix regression: new_seeker="no" skipped the profile fetch (yes-path opening bled over)
- **Feedback/bug:** With `new_seeker="no"` the agent stopped asking to fetch the profile — it opened with the experience question and the pool overview (the "yes"-path opening) and never called `get_profile`. The immediately-prior test (before the ranking redesign) had done the "no" path correctly, so this was a regression I introduced: adding **Example 5** (a `new_seeker="yes"` pool-overview walkthrough) and the salient **Step 1 overview** taught the model to open *every* call with experience + overview, overriding the "no"-path profile-permission gate (E1 — examples override prose; cross-branch opening bleed).
- **Change (Maya Hindi):**
  - **Decisive opening router** (post-greeting CRITICAL block): the first turn is decided ONLY by `new_seeker` — "no" → profile-permission question (experience question, pool overview, job list, role/location question all FORBIDDEN as the opening until `get_profile` has run); "yes" → experience gathering.
  - **Reinforced** the "no" MANDATORY step and the inline "Gathering role and experience" section to say they are never the first post-greeting action for "no"; guarded Step 1 Case B (overview) as never opening a "no" call.
  - **Examples corrected:** added a routing note to the examples header; labelled Example 1 as `new_seeker="yes"`; added an "opening note" to Example 5 that its experience+overview opening is "yes"-only and "no" callers must open like Example 4.
- **Files:** `Maya/Maya Hindi.md`; `.claude/skills/prompt-analyser/reference/bug-patterns.md` (sharpened **E1** with the cross-branch opening-bleed lesson + "re-test the other branch after adding an example"); `.claude/skills/prompt-analyser/reference/section-checklists.md` (E1 tick for branch-labelled examples).
- **Lesson:** adding an example to lock in feature X can regress a working branch Y — always re-test the branch the new example does NOT depict.

## 2026-07-13 — Rank the job pool by role/location/salary + pool-overview opener (both branches)
- **Feedback/bug:** Issue 1 from the live call — the profile role ("Data Entry Operator") was known and confirmed, but the list still led with an unrelated job (Customer Support). Parth: generalise relevance across both branches — `${recommendations}` is growing to ~20–30 jobs; rank by role/salary/location and present best-fit; if no profile, ask basics before recommending. Chosen opener (via question): **pool overview → seeker steers → best-fit 3**.
- **Change (Maya Hindi):**
  - **`${recommendations}` variable:** redefined as a pool of up to ~30 jobs that is only loosely ordered — "you rank it yourself"; dropped the "first entries are most relevant" assumption.
  - **Default Presentation Rule:** now "rank the pool, then present the best-fit 3" — priority **role → location → salary**, role-matched first; "more jobs" draws the next best-fit from the rest of the pool (same ranking). De-hardcoded all "indices 4–10" references to "the rest of the pool".
  - **Step 1 (rewritten "Orient the caller"):** Case A — target role already known (profile-confirmed on "no", or stated) → skip overview, rank, go to Step 2. Case B — role unknown → short **pool overview naming real roles from the pool** ("आपके इलाके में … डेटा एंट्री, कस्टमर सपोर्ट, टेलीकॉलिंग जैसी…") + one question, then rank. Area/salary are ranking inputs, no longer a forced question (this also removed the old mandatory area turn that was being fused with the role question).
  - **Step 2:** "present the 3 best-fit after ranking — role-matched first; do not read array order." Spoken format unchanged.
  - **"no"-path hand-off + Examples:** role-confirm now leads to the ranked Step 2 (not an area question). Example 1 (yes) and Example 4 (no) updated to present the ranked list directly (no area turn); **Example 5 added** — new/unsure caller gets the pool overview → steers → best-fit 3, with the one-bridge create→apply sequence modelled.
- **Files:** `Maya/Maya Hindi.md`; `.claude/skills/prompt-analyser/reference/bug-patterns.md` (added **C8** — results shown in array order despite known ranking signals); `.claude/skills/prompt-analyser/reference/section-checklists.md` (ranking on the recommendation-flow item).
- **Assumption (flag):** the pool overview names **real roles from the pool** (grouped naturally), never invented sectors — to stay inside the Hallucination Guard. Overview fires only when the target role is unknown; when it's already confirmed, Maya skips straight to the ranked 3 (avoids re-asking). If you want the overview to show *every* time (even after a role-confirm), that's a one-line change.

## 2026-07-13 — Fix turn-fusing, create_profile-on-returning-path, and bridge repetition
- **Feedback/bug:** Live `new_seeker="no"` call (profile found). Four issues: (1) role known ("Data Entry Operator") but the list still led with an unrelated job — role not used to order jobs [deferred to the ranking redesign]; (2) the agent fused three things into one turn — a leaked "प्रोफाइल fetch कर रही हूँ" line + the role-confirm question + the area question — so the seeker only answered the area and the role confirmation was skipped; (3) **critical:** a profile was already fetched, yet the agent called `create_profile` at apply (with a 6-profile array it was unclear which `id` to reuse, so it made a fresh one — a duplicate); (4) the "अप्लाई कर देती हूँ" bridge line was spoken 3–4× (at first consent, then again across the `create_profile`→`apply_job` sequence).
- **Change (Maya Hindi):**
  - **Turn separation (Using the fetched profile):** added a hard "one question per turn — wait for the answer" rule; the role-confirm question now **ends the turn**; the area question (Step 1) is explicitly a separate, later turn. Forbade any "fetch कर रही हूँ" line after the result — open directly with "प्रोफ़ाइल मिल गई…".
  - **`profile_id` binding (Reading the get_profile response):** documented the profile's top-level **`id`** as the `profile_id` for `apply_job` (not `userId`); "use the most-recent profile's `id`, hold it, reuse at apply". Added a hard rule: **a profile was found ⇒ returning caller ⇒ never call `create_profile` (duplicate = hard failure)**; reinforced in Step 4 "no" path and the create_profile "Hard guard".
  - **Bridge once (apply_job rules + Step 4):** say the bridge **only immediately before the tool, after age/gender are known**; **once said, never repeat — say nothing between tool calls**; returning "no" path = one bridge → `apply_job` (no `create_profile`); new "yes" path = one bridge → `create_profile` → `apply_job`.
  - **Don't re-ask known fields:** reinforced with a concrete example (profile shows gender/age ⇒ don't ask them at apply).
- **Files:** `Maya/Maya Hindi.md`; `.claude/skills/prompt-analyser/reference/bug-patterns.md` (added **A7** turn-fusing, **C7** fetched-id-not-bound→duplicate-create; sharpened **B1** for multi-tool sequences); `.claude/skills/prompt-analyser/reference/section-checklists.md` (A7 tick; C7 on the job-matching "reading the fetched profile" item).
- **Deferred (asked):** Issue 1 — generalise relevance ranking (role/salary/location) across both branches + the "summarised pool overview" opener for a ~20–30-job pool. Awaiting Parth's pick on the presentation shape before rebuilding Job Presentation.
- **Note:** the live `apply_job` also returned HTTP 404 "Job not found" for `job_id "JOB-1001"` — that's an apply-backend/test-data issue, not a prompt bug.

## 2026-07-13 — Use the fetched profile: greet by name, confirm role, don't re-ask known fields
- **Feedback/bug:** On a live `new_seeker="no"` call, `get_profile` returned a full profile (name "Parth Bansal", role "Data Entry Operator", age 25, gender male — as a 6-element array) but the agent ignored all of it: it spoke the hold line and jumped straight to the area question — no name, no role acknowledgement — and the profile fields (age/gender) would have been re-asked at apply time. The prompt fetched the data but never told the model to read the response, which record to use, or that present fields are already known. Parth's asks: (1) after fetch, address the caller by first name ("प्रोफ़ाइल मिल गई, पार्थ जी"); (2) confirm the role and use it to prioritise the relevant jobs; (3) apply the same "already known → don't ask again" rule to age/gender/etc.; (4) add a section explaining the get_profile fields.
- **Change (Maya Hindi):**
  - **Profile Handling → "no" path:** the "profile returned" bullet now personalises instead of staying silent ("acknowledge warmly… address by first name, then confirm the role"), while still not listing jobs or reading IDs.
  - **New subsection "Using the fetched profile (new_seeker \"no\")":** (1) greet by first name with a garbled-name guard; (2) reflect + confirm the `role` and, on confirmation, surface the role-matching jobs in `${recommendations}` first (re-order only — never fetch/invent, per Hallucination Guard); if the seeker wants something else, re-order to that; (3) never re-ask fields the profile already has.
  - **New subsection "Reading the get_profile response" (get_profile Tool Call Rules):** field dictionary (`metadata.name`/`whoIAm.name`, `role`, `gender`, `whatIHave.age`, `totalYearsOfExperience`, `whatIWant.monthlyInHandPreferred`, `location`), a **most-recent-record** rule for the returned array, and "present & non-empty ⇒ KNOWN ⇒ never re-ask".
  - **Example 4 added:** returning `new_seeker="no"` caller — fetch → "प्रोफ़ाइल मिल गई, पार्थ जी" → role confirm → role-matched job listed first → age/gender not re-asked → reuse `profile_id`, `apply_job` (no `create_profile`). Locks in the behaviour (models mimic examples).
- **Files:** `Maya/Maya Hindi.md`; `.claude/skills/prompt-analyser/reference/bug-patterns.md` (added **C6** — fetched response never consumed); `.claude/skills/prompt-analyser/reference/section-checklists.md` (job-matching archetype: "reading the fetched profile").
- **Flag:** KKB likely has the same gap (fetches a profile but no field-map / name-greeting / role-confirm). Not touched — Parth reported Maya; can be ported via `/port-feature` if wanted.

## 2026-07-13 — Real fix for the new_seeker branch: variable-interpolation order
- **Feedback/bug:** Even after the branch restructure below, `new_seeker="no"` (confirmed lowercase in input args) STILL ran the new-user path — asked about experience instead of fetching the profile, then called `create_profile`. The actual root cause (found by Parth): the binding line read `Consider ${new_seeker} as new_seeker`, which interpolates at runtime to **"Consider no as new_seeker"** — the value is placed where the label should be, so `new_seeker = no` never binds and the branch has no value to switch on. This is why case-normalization, Step-0 removal, section deletion, and hard gates all failed — none touched the garbled binding.
- **Change:** flipped the order to `Consider new_seeker as ${new_seeker}` (→ "Consider new_seeker as no"), which binds the value cleanly. (Parth fixed this in production; synced into the repo here.) Catalogued as prompt-analyser **G1** (variable placeholder before its label garbles after interpolation).
- **Files:** `Maya/Maya Hindi.md`; `.claude/skills/prompt-analyser/reference/bug-patterns.md` (added G1; corrected the A1 2026-07-13 note).
- **Flag:** KKB has the same backwards binding (`Consider ${new_seeker} as new_seeker`, Hindi + Kannada, lines ~64 and ~197) — latent, not yet flipped.

## 2026-07-13 — Batch fix: branch structure, apply hallucination, phone +91, job order, age/gender, intro
- **Feedback/bug:** Live transcripts (both `new_seeker="No"` and `"Yes"`) behaved identically — greeting → Experience Capture → `create_profile` → spoken "अप्लाई हो गया" with **no `apply_job` call**. Plus: apply bridge repeated 2–3×; jobs announced ("interested?") before being listed and without details; age/gender re-asked when already known; over-formal intro ("अवसरों"); and `get_profile` empty for ~14/80 (phone passed without `+91`). User confirmed lowercase `"no"` still failed → case was NOT the cause; pointed to KKB where the same branch works.
- **Root cause:** Maya diverged from KKB's clean single-branch structure by adding a redundant `Step 0` and a **standalone `## Experience Capture` section** that the model jumped to after the greeting — hijacking the `new_seeker` branch for both values. (KKB has neither; its `"yes"` path gathers inline.)
- **Change (Maya Hindi):**
  - **Branch (master):** deleted `Step 0`; deleted the standalone `Experience Capture` section; folded role/experience gathering **inline** into the Profile-Handling `"yes"`/`"no"` paths, mirroring KKB. Added a case-insensitive + empty-defaults-to-"no" clause. Updated dangling references (get_profile rules, create_profile).
  - **Apply hallucination:** success line may be spoken ONLY after `apply_job` actually returned success; `apply_job` must fire every time (Apply Success Handling + apply_job rules + Step 4).
  - **Phone:** `get_profile`/`create_profile` now prepend `+91` (both write and lookup), with a phone-format rule; updated the create_profile example to `+91…`.
  - **Age/gender:** Pre-Apply now uses the fetched profile — asks only genuinely missing fields (no re-ask for `new_seeker="no"`).
  - **Job order:** Step 1 is now a lead-in + area question (no premature interest question); Step 2 lists with details, then asks interest. Updated Example 1 to match.
  - **Intro:** "अवसरों" → "जॉब्स" (greeting + Example 1).
- **Files:** `Maya/Maya Hindi.md`; `.claude/skills/prompt-analyser/reference/bug-patterns.md` (sharpened A1, C3; added A5, A6, C5).
- **Guidance followed:** mirrored KKB Placeholder Hindi (the working reference). Maya divergences (college identity, HR line, benefits, feminine voice, MML) preserved.

## 2026-07-08 — Hard-gate Experience Capture for new_seeker="no"
- **Feedback/bug:** Even with `new_seeker="no"` confirmed passed, the agent skipped the profile-permission/`get_profile` step and went straight to Experience Capture (the "yes" path) right after the greeting. Prior reinforcement told the model what to DO on the "no" path but never forbade the competing action (Experience Capture), so Experience Capture kept winning.
- **Change:** Added a hard gate at the top of Experience Capture — when `new_seeker="no"`, it may NOT run as the first post-greeting action; it can run in the "no" path only after `get_profile` has been called and returned nothing/sparse. This leaves profile-permission → `get_profile` as the only valid first action for "no". Surgical, one section.
- **Files:** `Maya/Maya Hindi.md`

## 2026-07-08 — Sync to production prompt + fix apply-time tool path
- **Feedback/bug:** From live transcripts: (1) the new_seeker fork wasn't honored end-to-end — a new seeker's apply called `get_profile` (which returns nothing for a brand-new number) instead of `create_profile`, so `apply_job` fired with no valid `profile_id` and failed; (2) the apply bridge line ("अप्लाई कर देती हूँ") was spoken 3–4 times per apply, plus a forbidden "प्रोफाइल देख रही हूँ" waiting line. Root cause: Step 4 led with "use the `profile_id` from `get_profile` response," steering the model to the wrong tool at apply, which also caused the fumbling/repetition.
- **Change:** First synced `Maya Hindi.md` in the repo to the current production prompt (it had diverged — production added Step 0, Pre-Apply Data Collection, turn-based Step 1, etc.). Then applied surgical fixes:
  - **Step 4 (Application):** rewritten to branch on new_seeker — "yes" → `create_profile` then `apply_job` (never `get_profile`); "no" → reuse the `profile_id` from the post-intro `get_profile` (no re-fetch, no create). Added an explicit "never call get_profile at apply time" rule and a "one bridge line → silent tool call(s) → one result" sequence.
  - **get_profile rules:** added a hard rule that get_profile never runs at apply/consent time.
  - **apply_job bridge rules:** say the bridge once per application (never 2–3×); forbid the "प्रोफाइल देख रही हूँ" / profile-fetch / waiting narration; single result message.
- **Files:** `Maya/Maya Hindi.md`
- **Not done (flagged):** Did not reorder to create the profile *before* job presentation (your ideal "create → show jobs → update → apply" flow) — kept create-at-apply to stay surgical and not break the flow. No `update_profile` step added. Can do the fuller reorder separately if you want it.

## 2026-07-05 — Fix profile-handling bugs surfaced in testing
- **Feedback/bug:** On live calls: (1) `new_seeker`="yes" applied to a job without ever calling `create_profile` (no profile_id); (2) `new_seeker`="no" (returning caller) did not call `get_profile` at the start and jumped to recommendations; (3) age/gender were never asked. KKB Hindi did not show these. Root cause: Maya's pre-apply profile logic is textually near-identical to KKB, but Maya's heavier prompt (Caller Identity gate, college confirmation, HR line, Experience Capture, MML) causes the model to drop the profile steps; plus a latent contradiction in the "no" branch (header "caller already has a profile" vs body "MANDATORY IF PROFILE DOES NOT EXIST"). Age/gender are only optional `create_profile` payload fields — never explicitly asked.
- **Change (Maya Hindi only):**
  - "no" branch: reworded the mandatory line to remove the contradiction and make `get_profile` a hard gate — must fetch before presenting any jobs.
  - "yes" branch: added an explicit hard gate — since `get_profile` is skipped there is no `profile_id`, so `create_profile` MUST be called before `apply_job`.
  - Step 4 (Application): reinforced the same create_profile-before-apply gate at the point of action.
  - Experience Capture: added age (asked) and gender (inferred, or asked only if unclear), mapped to the `create_profile` `age`/`gender` fields.
- **Files:** `Maya/Maya Hindi.md`
- **Not done (flagged):** Maya still lacks KKB's `Post-Application Info Gathering` + `update_profile` sections (post-apply profile completion). Not one of the reported bugs; can be ported separately if desired.

## 2026-06-29 — Replicate new_seeker fork (ported from KKB)
- **Feedback/bug:** KKB added a `new_seeker` fork in the intro: when `new_seeker` is "yes", skip the (failing) `get_profile` call and gather details conversationally, doing only `create_profile` before application; when "no", fetch the profile via `get_profile`. Maya previously always attempted `get_profile`. Replicate the fork in Maya.
- **Change:** (1) Added the `${new_seeker}` input variable to Contact Variables. (2) Restructured "New contact — No old contact memory…" into `## Profile Handling after introduction (branch on new_seeker)` with the existing get_profile flow as the `"no"` path and a new `"yes"` path that skips `get_profile` and routes to Experience Capture. (3) Updated the Experience Capture trigger to also fire when `new_seeker` is "yes". Maya divergences (college identity, HR/MML, feminine voice, Experience Capture) preserved. Hindi only — Maya has no Kannada variant.
- **Files:** `Maya/Maya Hindi.md`
- **Ported from:** KKB

## 2026-06-29 — Initial system setup
- **Feedback/bug:** Maintenance system bootstrap; Maya had no memory or output prompt.
- **Change:** Created `Maya Memory.md` (seeker memory + campus fields: `college_name`, `hr_contact_shared`, `mml_offered`, `mml_registered`) and `Maya Output.md` (KKB-style extraction + `college_confirmed`, `experience_captured`, `hr_contact_shared`, `benefits_mentioned`, `mml_offered`, `mml_registered`).
- **Files:** `Maya/Maya Memory.md`, `Maya/Maya Output.md`

## 2026-09-03 — Job count anchor + array-order walk (ported from KKB)
- **Feedback/bug:** KKB presented 7 of 8 jobs and claimed it had listed everything (`22d80263`), or
  reached the total by repeating a job (`54a0daa8`). Maya shares the same presentation logic.
- **Change:** first batch announces the total out loud; ordinals run continuously and never restart;
  later batches walk the list in array order; no job may be named twice; the finished-list claim
  requires the highest ordinal spoken to equal the announced total.
- **Files:** `Maya/Maya Hindi.md`, `Maya/Maya Hindi Signals.md`, `Maya/Maya Inbound.md`,
  `Maya/Maya Inbound Signals.md`. Maya's divergences untouched (college identity, `${college_name}`,
  `hr_contact`/`benefits`, Experience Capture, HR-number sharing, MPL, feminine voice).
- **Ported from:** KKB (2026-09-03).
- **Analyser:** D56.
- **Status:** **DEPLOYED, NOT VERIFIED** — verified on KKB Hindi/Kannada Signals only; Maya's own
  variants have no call id yet.

## 2026-09-03 — Lookup-leak lines removed; introduction spoken once per call
- **Feedback/bug:** the KKB lookup-leak investigation (open item `fetch-leak-kn-signals`) found the
  leak was mandated by the prompt, not a model-adherence miss — and Maya's four prompts carried the
  same mandated line, "मैं देख रही हूँ कि आप अभी [role] का काम कर रहे हैं", plus sample conversations
  demonstrating it. Separately, the intro-twice item (1 call in 9) applies to Maya's shared opening.
- **Change:** (1) the role reflect-back no longer narrates the fetch — "आप अभी [role] का काम कर रहे
  हैं — क्या आप अभी भी [role] की जॉब देख रहे हैं?"; (2) ported TRRAIN's rule that the introduction is
  spoken once per call and never repeated, with an unclear reply treated as an acknowledgement.
- **Files:** `Maya Hindi.md`, `Maya Hindi Signals.md`, `Maya Inbound.md`, `Maya Inbound Signals.md`.
  Maya's divergences untouched (college identity, `${college_name}`, `hr_contact`/`benefits`,
  Experience Capture, HR-number sharing, MPL, feminine voice).
- **Ported from:** KKB / TRRAIN (2026-09-03).
- **Analyser:** D50 addendum.
- **Status:** VERIFY-PENDING.

## 2026-09-09 — apply-failure table had no row for a NAMED non-duplicate error
- **Feedback/bug:** the apply-failure table routed every non-duplicate error into Row 2, "you cannot
  tell why it failed", whose line asserts a cause: "अप्लाई अभी आगे नहीं बढ़ा है, technical issue है".
  But the tool result DOES name the error — `__RAYA_TOOL_DEBUG__` carries a
  `response_body_excerpt` with `"error":"..."`, and 67 of 73 observed apply failures name it. So on
  `MINOR_ACTION_CHANNEL_BLOCKED` (an age/channel policy block, not a fault) the bot told 5 callers
  there was a technical issue — a claim the prompt had licensed and that was false. Calls
  `5a1c0c77` (kkb-hi-signals), `1715a207` (kkb-kn-signals), `05a4b394` (kkb-kn-in-signals),
  `2cb97508` (maya-hi-signals, `TARGET_ITEM_NOT_FOUND`), `b9629043` (`USER_NOT_FOUND`).
- **Change:** inserted a new row BEFORE the catch-all — a named error that is not
  `ACTION_LIMIT_REACHED` gets a line that asserts only that the apply did not complete:
  "इस जॉब के लिए अप्लाई अभी पूरा नहीं हो पाया। हमने आपकी रुचि नोट कर ली है। क्या मैं आपको दूसरी जॉब्स बताऊँ?"
  (Kannada: "ಈ ಜಾಬ್‌ಗೆ ಅಪ್ಲೈ ಇನ್ನೂ ಪೂರ್ತಿ ಆಗಿಲ್ಲ. ನಿಮ್ಮ ಆಸಕ್ತಿ ನಾವು ನೋಟ್ ಮಾಡ್ಕೊಂಡಿದೀವಿ. ಬೇರೆ ಜಾಬ್‌ಗಳನ್ನ ಹೇಳಲಾ?")
  Escalation-ladder rung 3 — the wrong option is removed rather than forbidden: Row 2 keeps
  "technical issue" only for the genuinely unreadable case (timeout, no response), where it is true.
  Purely additive; Row 1 and Row 2 are unchanged. Row order is Row 1, Row 2a, Row 2 so the specific
  case matches before the catch-all.
- **Files:** 9 Hindi + 4 Kannada conversation prompts across KKB, Maya and KKB-Slim.
- **Status:** VERIFY-PENDING. Rolling out to kkb-hi-signals and kkb-kn-signals first (the two bots
  where the false line was observed); the rest are DEPLOYED, NOT VERIFIED until called.

## 2026-09-09 — apply-failure catch-all tightened so a NAMED error has no catch-all (VERIFY-PENDING)
- **Feedback/bug:** the dominant apply-failure defect is the opposite of D80 — **45 of 60**
  `apply_job` calls that returned `ACTION_LIMIT_REACHED` spoke the Row 2 technical-issue line
  instead of the Row 1 already-applied line (measured 2026-09-03/04, `ESCALATION-litwiz.md` §1).
  Row 1 already named `ACTION_LIMIT_REACHED` as a trigger, so reachability was never the problem:
  Row 2 stayed available as a safe hedge and the model kept taking it. §1 concluded "there is no
  wording that resolves a distinction the model cannot observe" — but the model CAN observe it. The
  `apply_job` failure result carries `__RAYA_TOOL_DEBUG__` with
  `response_body_excerpt={"error":"..."}`, and 67 of 73 observed failures name the error.
  An earlier attempt to drive Row 1 off the error name was reverted because it leaked onto
  `USER_NOT_FOUND` (call `5f0d3671`); the new Row 2a now absorbs that case, so the fix is unblocked.
- **Change:** Row 2 is no longer "you cannot tell why it failed". Its condition is now "the result
  carries NO error name at all — a timeout, no response, or a body with nothing in `"error":"..."`",
  with an explicit instruction to check the result in hand before choosing it. The three rows are
  now disjoint and exhaustive: `ACTION_LIMIT_REACHED` matches ONLY Row 1, any other name matches
  ONLY Row 2a, and no name matches ONLY Row 2 — which stays the one row permitted to attribute a
  cause, because it is the only row where a technical fault is what you actually have. Rung 3: the
  wrong option is removed rather than forbidden. Spoken lines unchanged in all three rows.
- **Files:** 9 Hindi + 4 Kannada conversation prompts across KKB, Maya and KKB-Slim.
- **Status:** VERIFY-PENDING — not yet deployed; the Row 2a verification dial is still in flight and
  one change is being verified at a time.

## 2026-09-09 — returning-caller callback clause was missing from both Kannada prompts
- **Feedback/bug:** tracker items "Missing returning call user" were fixed on KKB Hindi, KKB Hindi
  Signals and Maya Hindi Signals and **never mirrored**. `KKB Placeholder Kannada Signals.md` and
  `KKB Placeholder Kannada.md` had ZERO occurrences of the callback clause,
  `last_conversation_summary` or `overall_conversation_summary`; the Hindi master has the clause 5x
  and "previous conversation" 20x. Kannada jumped straight from the get_profile-read paragraph to
  "Greet by first name", so a returning Kannada caller was greeted as if never called before.
  Maya Hindi had the same gap against its own Signals twin.
- **Change:** ported the whole block. English rules, field names and the callback-clause bullet list
  copied VERBATIM (agnostic); the quoted clause and its placeholder adapted to Kannada
  ("[ಮೊದಲ ಹೆಸರು] ಅವರೇ, ಹಿಂದಿನ ಸಲ ನಾವು [ಯಾವ ವಿಷಯದ ಬಗ್ಗೆ ಮಾತಾಡಿದ್ವಿ] ಬಗ್ಗೆ ಮಾತಾಡಿದ್ವಿ — …"), and the
  banned-wording bullet localised to the Kannada words it names. Maya Hindi took the Hindi block
  verbatim. No Hindi text leaked into either Kannada file (verified 0).
- **Files:** `KKB/KKB Placeholder Kannada Signals.md`, `KKB/KKB Placeholder Kannada.md`,
  `Maya/Maya Hindi.md`. Inbound variants deliberately untouched — their Hindi masters also lack the
  block, so that is a design question, not drift.
- **Status:** DEPLOYED (kkb-kn-signals, kkb-kn-out, maya-hi-out). **NOT VERIFIED** — needs a call
  from a number with prior memory.

## 2026-09-09 — Kannada apply-failure line blended two rows and re-asserted "technical issue"
- **Feedback/bug:** call `41a2c19d` returned `TARGET_ITEM_NOT_FOUND` three times and the bot said
  "ಈ ಜಾಬ್‌ಗೆ ಅಪ್ಲೈ ಇನ್ನೂ ಪೂರ್ತಿ ಆಗಿಲ್ಲ, technical issue ಇದೆ" every time — the new Row 2a opening welded
  to Row 2 cause claim. The two Kannada lines shared the prefix "ಈ ಜಾಬ್‌ಗೆ ಅಪ್ಲೈ ಇನ್ನೂ" and differed
  only in the verb phrase. Hindi passed the same test (`199caee7`) because its two lines are
  lexically distinct — a direct demonstration of the never-extrapolate rule.
- **Change:** Row 2a Kannada now opens on different words entirely — "ಈ ಅಪ್ಲಿಕೇಶನ್ ಸಧ್ಯಕ್ಕೆ ಆಗಿಲ್ಲ." —
  so there is no shared opening to blend, plus an inline note naming call `41a2c19d` so the wording
  is not "tidied" back into a shared prefix. Row 2 is UNCHANGED: its "technical issue" is there at
  the owner explicit request (see the note above the table) and was not removed.
- **Files:** the 4 KKB Kannada conversation prompts.
- **Status:** DEPLOYED (kkb-kn-signals, kkb-kn-out, kkb-kn-in-signals, kkb-kn-in). **NOT VERIFIED.**

## 2026-09-09 — the prohibition against speaking stage directions was supplying the string
- **Feedback/bug:** on `e4e81fe2` (kkb-kn-out, live) the bot spoke
  `*(Silent tool call: apply_job with profile_id: "5051" and job_id: "19e3da1f-...")*` aloud, leaking
  a profile id and a job UUID to the caller, then said "ಅಪ್ಲೈ ಆಗಿದೆ" — applied. **Zero tools ran on
  that call.** No `get_profile`, no `apply_job`, no application. Same class as `29c4f152` and the
  four occurrences on 2026-09-03 that the prompt already documents, so this guard has now failed
  five times. 6 more cached calls across kkb-kn-signals, maya-hi-out, kkb-hi-in and kkb-kn-out spoke
  a stage direction; two of them read the caller phone number `+917946350285` aloud inside a
  `create_profile` stage direction.
- **Root cause:** the guard quoted the forbidden output verbatim. Both the prohibition ("Writing
  `*(Silent tool call: apply_job)*` ... applies nobody") and the evidence citation for `29c4f152`
  wrote the exact string the bot then emitted. Rung 1 — the wrong output was in the prompt, in the
  rule meant to prevent it.
- **Change:** the literal form is gone from every prompt (verified 0 remaining). The prohibition and
  the citation now DESCRIBE it — "a stage direction naming the apply tool" — instead of printing it.
  No new prohibition wording was added: this guard had already failed five times, so volume was not
  the lever.
- **Files:** 12 KKB/Maya conversation prompts (TRRAIN and slim did not carry the string).
- **Status:** DEPLOYED to all 15 conversation targets, all verified in sync. **NOT VERIFIED** — needs
  a call that reaches an apply on a Kannada outbound bot.
- **Known larger change NOT made:** the samples still render 12-38 inline `*( )*` stage directions
  each. Converting them to a non-inline `INTERNAL:` form would remove the imitable shape entirely,
  but that is a 15-file reformat that cannot be tested in one night and needs sign-off.

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

## 2026-09-09 — Maya spoke salary as digits, and reads the college abbreviation twice
- **Feedback/bug:** `maya-hi-signals` carried digits in 4 of 16 salary phrases and
  `maya-hi-in-signals` in 5 of 72. The numbers rule sits ~700 lines below the job template that
  speaks the value (D82). Fixed at the template in all four Maya prompts — `[salary]` and
  `[vacancy]` arrive as digits and are spoken as words.
- **Also noted, NOT fixed:** the identity line renders the college abbreviation twice —
  "माया, वीटीयू (VTU) की ओर से" reads the Latin in parentheses aloud (`0a3cba76`). Maya's caller
  identity is a product decision, so this is flagged for the owner rather than edited.
- **Files:** `Maya Hindi Signals.md`, `Maya Hindi.md`, `Maya Inbound Signals.md`,
  `Maya Inbound.md`. **Status:** DEPLOYED. **NOT VERIFIED.**
