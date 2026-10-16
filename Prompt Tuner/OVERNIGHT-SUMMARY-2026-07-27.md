# Overnight Run Summary — 2026-07-27

Scope: every open issue assigned to **Parth** on the Consolidated Feedback Tracker (11 issues), each **root-caused against its real Raya call transcript** before any edit. Prompt fixes are surgical, mirrored across languages, propagated to sibling bots where the bug exists, and regression-checked. Deploys are read-back-verified and in-sync on the live agents.

> **The single most important line:** the biggest P1s — **rows 15 / 42 / 65 (apply failing, 241 attempts)** — are **NOT prompt bugs**. They are `get_profile` not firing at call start (a **runtime** tool-adherence failure) plus **placeholder job inventory** (a backend/data issue). They need **LitWiz/console action**, not a prompt edit. Details below.

> **On "fixed":** per your bar, nothing is marked *confirmed-fixed*. There are **zero post-deploy calls** to verify against (last call 07-26 12:32; deploys 07-27 00:56–01:40), and I have no way to place a test call. Fixes are **deployed + grounded in the pre-deploy bug**; a watcher is running to confirm the moment morning/UAT traffic arrives.

---

## 1. Fixed & deployed (grounded; live-confirmation pending traffic)

### r68 — apply-loop "apply kar rahi hu" repeats (P1) — KKB **and** Maya
- **Root cause (call `4663a367`, 07-26):** on a *failed* apply, the bot re-spoke the apply bridge/hold ("…अप्लाई कर देती हूँ" / "एक बार apply कर देती हूँ") at the head of the failure message with **no new tool call**, and re-fired `apply_job` on the **same already-failed `job_id`** across repeat user requests.
- **Fix (two additive guards in Apply Failure Handling):** (1) the failure message must **begin directly with the base failure line** — never re-speak the bridge/hold on the failure turn; (2) a **job that already failed `apply_job` this call is DONE** — never re-fire it; go straight to the interest-noted / HR / alternate-job path.
- **Propagated:** the identical structural gap existed in **Maya** (out + inbound) → ported. DKB has no `apply_job` → N/A.
- **Live:** KKB Hi/Kn inbound + Maya Hi/inbound — deployed, in-sync.

### r69 / r71 — city mispronunciation (P1) — KKB + Maya
- **Fix:** added the **Canonical Location Spellings** section you provided (Ghaziabad, Indirapuram, Mohan Nagar, Rajendra Nagar, Sector 5), overriding phonetic transliteration.
- **Scope:** KKB Hindi + Kannada (out + inbound, Kannada-script localized) and Maya (Hindi + inbound). **DKB skipped** — no hardcoded locations (employer sites are dynamic).
- **Caveat:** the transcript confirms the bot now emits the **canonical text**; whether TTS *pronounces* it right needs a **listen** (audio isn't in the transcript).

### Backlog + regression reconciliation deployed tonight
- **Kannada `get_profile` revert** — restored the last-known-good after an earlier regression (see §4).
- **No-break reconciliation** — my canonical edits introduced 2 contradictions, caught by a regression pass and fixed: Kannada Ghaziabad set to `ಗಾಜಿಯಾಬಾದ್` (matches its 15 dialogue occurrences); Maya's MPL name `घाज़ियाबाद मार्केटर प्रीमियर लीग` **exempted** from the canonical rule so its branded spelling isn't normalized.

---

## 2. Not a prompt fix — root cause **is** the resolution

### r15 / r42 / r65 — apply failing (P1, 241 attempts) — **the headline**
- **Root cause A (runtime):** `get_profile` is **not firing** at call start even though the prompt mandates it in multiple HARD BLOCKs → empty/fabricated `profile_id` → `apply_job` returns HTTP 404 "Invalid or missing profile_id". The model is *ignoring* existing instructions — a **tool-adherence** problem prose can't reliably fix.
- **Root cause B (backend):** the agents run on **placeholder job inventory** (`job_id "1"/"2"`) → the dhiway BAP returns "Job not found".
- **Needed (outside prompt scope):** (1) **Raya/LitWiz platform tool-forcing** to guarantee `get_profile` fires first; (2) **real job inventory** loaded on the console. Sheet rows flagged **"Flagged - Backend Issue."**

### r61 / r73 — "apply fallback missing in Kannada" — **not reproduced**
- The apply-failure fallback **is present** in KKB Kannada and **fires correctly for both old-seeker (`ade09ec6`) and new-seeker (`2bc77d58`)**. The "works for new, not old" claim is unfounded. The underlying 404 is the same backend inventory issue.

### r70 — "profile JSON spoken aloud" — **not reproduced**
- Scanned **40 recent calls** (07-24 → 07-27) on KKB Ghaziabad out + inbound. **No** assistant turn speaks JSON / payload / field names / IDs — the profile/apply flow is natural Hindi throughout. **Need the specific call uuid + timestamp** that reproduces the leak before any edit (a static-analysis "gap" here would have been an ungrounded fix — your no-transcript-no-fix rule caught it).

### r44 — Truecaller Business verification — **ops/telephony**, not a prompt.

---

## 3. Held (documented, ready to apply)

### r39 — name-confirm at call start (P4)
- **Root cause (call `069c7370`):** name is asked only when blank, never confirmed for a known caller.
- **Held because:** the fix adds a confirmation turn to the *returning-caller opening*, which (a) currently violates that section's "one question per turn, end on the role-confirm" rule and (b) sits in the exact opening flow that's **unstable from the `get_profile` issue**. For a P4 nice-to-have, editing that fragile area unattended is the highest-risk-per-value move. **Ready to apply attended** once `get_profile` firing is sorted.

---

## 4. Why earlier attempts went wrong (the honest part)

### The `get_profile` / fetch-narration saga (the core unsolved issue)
The recurring "एक मिनट, आपकी जानकारी निकल रही है…" prepended **before** the greeting:
- **Attempts 1–2:** banned the specific phrases → the model **invented new synonyms** (whack-a-mole). Failed.
- **Attempt 3 (structural rewrite):** reframed the `get_profile` call as "silent / invisible / nothing to acknowledge" and locked turn-1 to "greeting and NOTHING else." The model over-generalized this to **"the tool call is skippable" and stopped firing `get_profile`** → empty `profile_id` → apply failures. **This was a regression — reverted.**
- **Lesson (now in bug-patterns D25):** never de-emphasize a *required* tool call, and don't solve a turn-1 narration problem by piling prohibition weight on turn 1. The durable fix is **platform-side** (a static first-message / tool-forcing), which is exactly why I did **not** attempt another prose fix for rows 15/42/65 tonight.

### Other guardrails learned this cycle
- **Console clobber:** editing a live agent in the Raya console once overwrote inbound-Kannada content → **deploy only via API PATCH**, reconcile-before-edit.
- **Tonight's no-break catch:** additive canonical edits can contradict a file's own existing spellings (Kannada virama; Maya MPL) — always regression-check after adding a normalization rule.

---

## 5. Pending / next actions (ranked)

1. **Platform escalation to LitWiz** — `get_profile` tool-forcing + real job inventory. **Resolves the P1 apply-failures (15/42/65) — the biggest lever.** (Outside prompt scope; needs you/LitWiz.)
2. **Confirm the deployed fixes** (r68, r69/71) on post-deploy calls — watcher running; or a Khushboo UAT pass.
3. **r39 name-confirm** — apply attended once (1) lands.
4. **r70** — obtain the reporter's reproducing call.
5. **Optional:** re-sync the Blue Dots public mirror with tonight's prompts.

---

## 6. Deploy record (all read-back-verified, in-sync)
`kkb-hi-in · kkb-kn-in · kkb-hi-out · kkb-kn-out · maya-hi-out · maya-hi-in` — location section + r68 guards + reconciliations. Full shas + timestamps in `raya/deploy-history.md`.

## 7. Bottom line
- **Prompt-side is essentially done:** every genuinely prompt-fixable issue is fixed, mirrored, propagated, regression-checked, and deployed.
- **"Confirmed fixed" is blocked only by the absence of post-deploy call traffic** (not by any remaining work) — the watcher closes that as calls arrive.
- **The highest-impact issue (apply-failures) is not a prompt bug** — it needs `get_profile` tool-forcing + real inventory from LitWiz/console. That's the one thing that will actually move conversion.
