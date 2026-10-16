# Signals bots — deep E2E test + fix campaign (2026-08-01)

Goal (user): run detailed end-to-end tests on ALL Signals bots against the 70+ param voice-test
checklists, fix every real bug, and log all **critical decisions** so the user can revert any single
one they disagree with. Example the user flagged: DKB still used the Dhiway `get_talent_insights`
tool → remove it (no Signals alternative) + update the flow.

Bots in scope (8): kkb-hi-signals `115b38a5`, kkb-kn-signals `33037201`, kkb-hi-in-signals `3f521174`,
kkb-kn-in-signals `f38da775`, maya-hi-signals `904f333f`, maya-hi-in-signals `1c24feda`,
dkb-hi-signals `fabda71d`, dkb-kn-signals `847a85e2`.

Snapshots for revert: `raya/signals-expansion/e2e/snapshots/*.pre-*.md` (+ tool JSONs).

---

## CRITICAL DECISIONS (each independently revertible)

### CD1 — DKB: remove `get_talent_insights` + the market-picture step  ✅ DEPLOYED (test pending)
- **Why:** `get_talent_insights` is the ONEST/Dhiway tool; it is **not mapped on Signals** and there is
  no equivalent endpoint. The prompt kept the whole "market picture" conversation guarded as a "backend
  dependency" with a weak-signal fallback — a step that could only ever stall or risk fabrication.
- **Decision:** removed the tool from both DKB agents (tools now `create_job`+`update_job` only) and
  deleted the market-picture flow: Phase-3 now goes role+city → remaining fields → working-hours/benefits
  → consent → `create_job`. Also softened two persona lines that promised "market data / talent picture".
- **Alternative if user disagrees:** keep a tool-free generic reassurance line ("candidates keep joining
  the platform") instead of full removal. **Revert:** restore `snapshots/DKB *.pre-gti-removal.md` +
  re-add the tool from `snapshots/dkb-*.tools.pre-gti-removal.json`.
- **Files:** DKB Hindi Signals.md, DKB Kannada Signals.md. Both languages mirrored.

### CD2 — Inbound bots: make examples/synonyms/overviews consistent with the real 4-job inventory  ⏳
- **Why (ship-blocker, all 3 graders agreed):** the hardcoded inventory is 4 real Signals jobs
  (Data Entry/Kashi Infotech, Remote Customer Support/Rampur Technologies, EV Charging Tech/Yamuna Solar,
  AC Technician/Krishna Enterprises), but the "What's available" line, synonym table, Case-B overview,
  canonical-locations and ALL example dialogues still describe the OLD Ghaziabad/Noida retail-food set
  (McDonald's, Burger King, CY Future, Weavings, Cashier, Sales…). Per analyser E1 the model mimics
  concrete examples over inventory → it will present jobs that don't exist = hallucination.
- **Decision:** keep the inventory JSON exactly as-is (the 4 job_ids are real + apply-verified — do NOT
  touch ids), and rewrite the surrounding prose + examples to reference ONLY those 4 jobs.
- **Alternative:** swap the placeholder inventory for a real region-appropriate production list (data
  dependency the user said they'll fill later). **Revert:** restore `*.pre-e2e-fixes.md`.
- **Files:** KKB Placeholder Inbound Signals.md, KKB Placeholder Inbound Kannada Signals.md, Maya Inbound Signals.md.

### CD3 — Outbound bots: fix inbound-framed closings (D5 modality leak)  ⏳
- **Why:** outbound closings invited the seeker/owner to "contact us / call us back" — an inbound frame
  on an outbound call (analyser D5).
- **Decision:** reword closings on OUTBOUND bots only (KKB Hi/Kn out, Maya out; DKB already outbound-framed —
  verify) to "the initiative/centre/our team will call you again". Inbound bots may legitimately invite
  callback — left as-is.
- **Revert:** restore the affected file's `.pre-e2e-fixes.md`.

### CD4 — All bots: add a minimal honest "are you a real person / AI?" responder  ⏳
- **Why:** no bot currently answers the "are you a real bot/person?" question (generic §13); they only
  disclose recording.
- **Decision:** add one short agnostic rule + one in-language spoken line ("मैं एक AI असिस्टेंट हूँ…"/
  Kannada twin) that answers honestly and returns to the task. Does NOT change the user's deliberate
  intro design (recording-disclosure-at-end stays).
- **Revert:** restore the file's `.pre-e2e-fixes.md`.

### CD5 — DKB: fix `job_role="Not Available"` misrouting to the existing-posting branch + sentinel leak  ✅ DEPLOYED + VERIFIED
- **Why (found via the DKB-Kn CD1 test, call a02f61b3):** with `job_role="Not Available"` (a new-vacancy
  campaign), the bot took the **existing-posting** branch at Turn 2 and **spoke "Not Available, Not
  Available vacancies, ಸಂಬಳ Not Available" aloud** in the Phase-1 freshness line (C9 sentinel leak +
  wrong pitch). Root cause: the Turn-2 condition said "If job_role is **present**" — but `"Not Available"`
  is a non-empty string, so the model read it as present. It also conflated `company_name` being set with
  a posting existing.
- **Decision:** rewrote the Turn-2 branch to depend strictly on whether `job_role` holds a REAL role
  value (explicitly: `"Not Available"`/empty/NULL → new-vacancy pitch; a real title → existing-posting
  pitch), stated `company_name` presence ≠ a posting, and added a hard "never speak a Not Available
  value" guard to the Phase-1 freshness list. Pre-existing bug (NOT a CD1 regression), fixed because the
  user asked for all bugs found in testing to be fixed.
- **Verified:** DKB-Kn retest (3177339f) — new-vacancy pitch used, zero sentinel spoken, straight to
  Phase 3, create_job fired. DKB-Hi retest in progress.
- **Revert:** the Turn-2 block + the Phase-1 guard line in both DKB files (this session's edits).

### CD6 — Seeker bots: `get_profile`/`create_profile` phone doubled the 91 prefix  ✅ APPLIED (user confirmed 12-digit contract 2026-08-01)
- **RESOLUTION:** user confirmed production passes the **12-digit** `${contact_phone}` (91 + 10-digit) — matching what the test showed. So `91${contact_phone}` was doubling it. Applied the fix across all 6 seeker files: changed the literal `91${contact_phone}` → `${contact_phone}` (26 occurrences) and reworded every phone-format note to "`${contact_phone}` is already the full 12-digit number — pass it AS-IS; never prepend another `91`." Deployed to all 6 seeker agents. ✅ **VERIFIED** (KKB-Hi confirm call ad8571ff: get_profile now sends `917946350285` — single 12-digit, no doubling; apply→success; the correct phone now resolves the correct user record). Revert: git (pre-CD6 commit `7405bb7`).

- **Found via KKB-Hi outbound test (07699d53):** `get_profile` sent `phone_number: "91917946350285"` — a
  doubled 91 (14 digits). Root cause: all 6 seeker prompts template the phone as **`91${contact_phone}`**,
  and they document `${contact_phone}` as a **10-digit** mobile ("91 + the 10-digit mobile"). But the test
  harness binds `${contact_phone}` to the 12-digit dialed number, and your stated contract is "the phone is
  ALWAYS the 12-digit number (91 + 10-digit)". If `${contact_phone}` is 12-digit in production, `91${contact_phone}`
  doubles it → keys the profile to a junk 14-digit number (D17/D39). The apply still SUCCEEDED (backend is
  lenient), and one other call sent it correctly — so it's runtime-inconsistent. The bots FUNCTION; this is a
  data-hygiene / correct-record-resolution issue.
- **Why flagged, not auto-fixed:** the fix depends on the production `${contact_phone}` format, which the
  prompt (10-digit) and your note (12-digit) disagree on. Rewiring phone→identity on all 6 seeker bots on the
  wrong guess would silently mis-resolve real users' records — a consequential, hard-to-detect change. Needs
  a one-fact confirmation.
- **The exact fix (once you confirm the format):**
  - If `${contact_phone}` is **12-digit** (your note): change the literal `91${contact_phone}` → `${contact_phone}`
    in all 6 seeker files (get_profile + create_profile + example stage-directions), and update the phone-format
    notes to "`${contact_phone}` is the full 12-digit number — use as-is, never prepend another 91."
  - If `${contact_phone}` is **10-digit** (prompt's current assumption): the prompt is already correct and the
    doubling I saw is only a test-harness artifact — no change needed (just make the line-782 "don't double-prefix"
    guard louder).
- **Files (if applied):** all 6 seeker Signals prompts. Occurrences located: KKB out Hi/Kn (lines 206/778/1205),
  KKB in Hi/Kn (291/852/910/1014/…), Maya out (247/680/1115), Maya in (318/750/…).

### CD7 (minor, follow-up) — outbound "प्रोफಾಇಲ್" vs inbound "जानकारी" consistency (D8)
- The KKB **inbound** consent line was changed (M6) to say "जानकारी दर्ज करके" (avoid the internal word
  "profile"), but the KKB **outbound** create-consent + success lines still say "प्रोफाइल" (the phrasing the
  KKB checklist currently sanctions). Minor D8 inconsistency — align outbound to inbound in a cleanup pass, or
  keep as the sanctioned create-consent wording. Not applied (checklist-sanctioned; low risk).

---

## MECHANICAL SYNC / CORRECTNESS FIXES (no judgment call — applied, logged in CHANGELOG)

KKB OUTBOUND pair:
- M1 Kn Pre-check: add the empty-`${recommendations}` fallback block (parity with Hindi).
- M2 Kn "Core belief" prose → English, byte-identical to Hindi (English-instructions rule).
- M3 Kn `update_profile` payload: add the enum-reminder sentence Hindi has.
- M4 Example-2 (both): stop persisting a non-schema `totalYearsOfExperience`; use `workExperience` enum,
  align to Phase-2 scope. (Correctness: a non-schema field 400s on Signals.)
- M5 No-Match top scaffolding: normalise the two twins to identical English.

KKB INBOUND pair:
- M6 Consent line: align Kn to Hi — say "जानकारी/ಮಾಹಿತಿ", drop the Kn "profile"-word carve-out (D8).
- M7 Hi Step-3 deep-dive: add the data-share consent clause Kn already has.
- M8 Kn `update_profile` hold_message: use "ಒಂದು ಕ್ಷಣ" consistently (fix Kn:836 contradiction, D34).
- M9 Kn extra NOT-READY HARD BLOCK + extra update_profile example: reconcile parity with Hi (add to Hi).
- M10 Kn "Core belief" prose → English.
- M11 relevance-filter illustrative example: same wording in both.
- M12 Kn intro section: defer all fetch mention to Profile Handling (match Hi; D29).

MAYA pair:
- M14 voice-gender clarification note: port inbound's honorific-plural clarification into outbound.
- M15 profile-handling router clause: port inbound's "never skip fetch if caller front-loads role/city".
- M16 `${country_code}`: note as intentionally-unused (dead input) or drop the declaration.
- M17 Maya inbound: fix the malformed `> **[` inventory-wrapper markdown + remove `[FLAG — REVIEW]` markers.

## CHECKLIST FIX (the checklist was stale, not the prompt)
- CL1 `voice-test/reference/checklists/maya.md` §6: expects `+91` on get_profile; Signals uses
  `91XXXXXXXXXX` (no `+`). Update the checklist to the Signals shape.

## NON-FIXES (checklist/generic rule vs the user's deliberate design — left as-is, noted)
- Recording-disclosure-at-END-after-one-question: the user's explicit intro spec. NOT a bug.
- Inbound greeting not confirming campus/student status: defensible for a college-neutral inbound line.

## DATA / BACKEND DEPENDENCIES (hand off — not prose-fixable)
- Real production inventory job_ids for all inbound bots + Maya recommendations (user will replace).
- DKB Kannada `create_job` runtime-adherence (D25) — needs a Raya platform backstop (prior finding).
- Output prompts: add `consent_status` (+ inbound `ready_for_interview`) via `/update-output`.
