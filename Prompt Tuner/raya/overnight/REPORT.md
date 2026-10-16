# Overnight run — main REPORT

**Status: as of ~03:00 IST 2026-07-30 — the run is still ongoing; this report may be updated.**

Scope: the autonomous Prompt Tuner overnight run (2026-07-29 → 2026-07-30). Everything below is grounded in the repo's real artifacts — Raya call uuids, commit shas, deploy snapshots, changelog entries, and the 8 static analyses. Nothing here is invented. Companion files: `open-items.md` (decisions left for Parth — not restated in full here), `PRIORITY_BUGS.md` (ACTIVE/LATENT grounding), `TEST_LOG.md` (raw call log), `analysis/*.md` (per-bot static audits), `ideas.md` (improvement ideas).

---

## A. Executive summary

- **Skills built this run.** `/voice-test` (agent-to-agent voice-test harness: a persona "tester" agent dials/receives a Raya bot, then the call is graded) and `/onboard` (customer-facing intake for a new bot). Both are backed by **197-item grading checklists** (generic + per-bot). Committed in `e7663c8`.
- **Bots exercised.** All **8** conversation bots got a static pre-flight audit (`analysis/*.md`). **4 got LIVE voice tests:** KKB Signals **Hindi** (5 scenarios) + **Kannada** (1), KKB **Kannada outbound** (1). **DKB** was grounded on a real **historical** transcript (`cf3fc048`), with a fresh DKB-Kannada live call still pending.
- **Bugs found → fixed → deployed.** 8 fixes shipped across **8 live agent deployments**, each rollback-snapshotted: KKB **Signals** apply-blocker resolved (missing `location` → `PROFILE_NOT_LIVE`) + live-item selection + a new **role-update offer** feature (2026-07-29); KKB **inbound** new-caller apply-404 (**D31**) + hold-narration (**D34**); **DKB** callback-invite close (**D5**) + hold-narration (**D34**); KKB **outbound** hold-narration (**D34**) — all 2026-07-30.
- **ACTIVE vs LATENT.** Most static findings are **LATENT** (a real transcript shows the bot works in practice); the confirmed **ACTIVE** breakages were: KKB-inbound new-caller apply-404, the `hold_message` reveals (KKB in/out, DKB), the DKB callback-invite close, and the Signals `PROFILE_NOT_LIVE`. The tonight fixes targeted exactly those.
- **Deferred to `open-items.md`.** Phone double-prefix on outbound/Maya (no real repro; dicey harness artifact), DKB phone-format + the DKB campaign's mis-mapped `agent_args` (a **data**, not prompt, issue), the memory-substitution (D32) class (confirmed latent, left as-is), inbound-fix verification (not harness-testable), and Maya's D31 batching.
- **Restart resilience — set then removed.** To survive the ~03:40 IST usage-limit cooldown, a durable **scheduled task + auto-memory anchor + repo state anchor** (plan / TEST_LOG / analysis / RESUME) were set up so the run could self-resume (commits `2bada7b`, `89a073b`); this scaffolding was **removed** once the run resumed and the repo state was canonical.
- **Harness reality.** Testing is **sequential** (one tester DID = one persona at a time), bridging is intermittently flaky, `POST /api/call` is rate-limited (~1/13 s), and **inbound bots cannot be harness-tested** (the tester can only receive, not dial an inbound bot).
- **Discipline held throughout.** No fix without a real transcript; every deploy carries a rollback snapshot + a `CHANGELOG.md` entry + an analyser (`bug-patterns.md`) update so the same failure class is pre-empted next audit.

---

## B. Issues identified

Row per issue, covering all 8 bots (PRIORITY_BUGS + `analysis/*.md` + TEST_LOG). Status tokens: **FIXED+deployed** (change shipped this run), **RESOLVED** (fixed + confirmed by a post-fix passing call), **verify-pending** (no change; confirm a config/schema), **deferred→open-items#N** (flagged, not actioned), **latent** (static risk only). "(+twin)" = the sibling-language file received the same fix.

| # | bot | sev | ACTIVE/LATENT | symptom | D-pattern | status |
|---|-----|-----|---------------|---------|-----------|--------|
| 1 | kkb-hi-in (+kn twin) | HIGH | ACTIVE | New inbound caller: `apply_job` sent a fabricated/empty `profile_id` with no `create_profile` → 404 (new callers can't apply) | D31/D16/D28 | **FIXED+deployed** (verify-pending: inbound) — repro `5449910e`,`34f1f587` |
| 2 | kkb-hi-in (+kn twin) | MED | ACTIVE | `hold_message` narrates the "silent" `get_profile`/`create_profile` aloud | D34 | **FIXED+deployed** (verify-pending: inbound) — repro `8ddcaa5a`,`1fde1677` |
| 3 | kkb-hi-in | HIGH | LATENT | Memory-resume opener may speak name/role/journey before/instead of `get_profile` | D32 | deferred→open-items#6 (probe `8ddcaa5a`: fetch still fired) |
| 4 | kkb-hi-in | LOW | LATENT | Canonical-location list pins only 5 places vs a much larger Job Inventory | D26 | latent |
| 5 | kkb-hi-in | LOW | LATENT | `+91` hard-prepend template (landmine); inbound `contact_phone` is bare-10-digit so it doesn't fire | D17/C3 | deferred→open-items#3 |
| 6 | kkb-hi-out (+kn twin) | MED | LATENT | `hold_message` narrates the silent fetch/create | D34 | **FIXED+deployed** (kkb-kn-out re-test pending) |
| 7 | kkb-hi-out | HIGH | LATENT/no-repro | `+91` hard-prepend on `get_profile`/`create_profile` → `+91+91…` if dialer sends prefixed phone | D17/C3 | deferred→open-items#3 |
| 8 | kkb-hi-out | MED | LATENT | Memory-resume "Strict Override" + Example 2 model skipping `get_profile` → apply w/o `profile_id` | D32/E1 | deferred→open-items#6 |
| 9 | kkb-hi-out | MED | LATENT | Outbound bot invites callbacks in closings ("call कीजिए") | D5 | latent |
| 10 | kkb-hi-out | LOW | LATENT | Apply-failure turn lacks the "don't re-speak the bridge" guard (D27 parity) | D27 | latent |
| 11 | kkb-kn-out | MED | ACTIVE | `hold_message` spoken; "info received" said even on an EMPTY fetch `[]` | D34 | **FIXED+deployed** (re-test pending) — repro `fa530906` |
| 12 | kkb-kn-out | HIGH | DICEY | `create_profile phone:"+9197946350285"` → HTTP 400; may be a harness-DID artifact | D17/D39 | deferred→open-items#2 — evidence `fa530906` |
| 13 | kkb-kn-out | HIGH | LATENT | Memory-resume opener may substitute for `get_profile` | D32 | deferred→open-items#6 (probe `fa530906`: fetch fired, no resume) |
| 14 | kkb-kn-out | MED | LATENT | `+91` double-prefix landmine | D17/C3 | deferred→open-items#3 |
| 15 | kkb-kn-out | MED | LATENT | Ranking pads to 3 with unrelated roles (no relevance filter) | D36 | latent |
| 16 | kkb-kn-out | MED | LATENT | Apply-failure D27 guard(a) missing; same-job re-fire guard scoped to alt path only | D27 | latent |
| 17 | kkb-hi-signals (+kn twin) | HIGH | ACTIVE→RESOLVED | New-seeker `create_profile` without `location` → profile `draft` → `apply_job` 422 `PROFILE_NOT_LIVE` | D40 | **RESOLVED** (tool-schema `location` required, 2026-07-29) — repro `fb1283cb`; verify schema stuck |
| 18 | kkb-hi-signals | HIGH | LATENT | `create/update_profile` phone spec: 10-digit vs 12-digit self-contradiction → wrong-user write | D39/C3/A4 | latent (prose hygiene) |
| 19 | kkb-hi-signals | MED | LATENT | Phase-2 examples contradict rules (working/studying asked, vague count, non-schema `totalYearsOfExperience`) | E1/C3 | latent |
| 20 | kkb-hi-signals | MED | LATENT | New-caller create-consent line speaks "प्रोफाइल" aloud | D8 | latent |
| 21 | kkb-hi-signals | MED | LATENT | `get_profile` `91`-prepend double-prefix landmine | D17 | latent |
| 22 | kkb-hi-signals | LOW | LATENT | Example 6 malformed (two closings) + duplicate No-Match sections | E1 | latent |
| 23 | kkb-kn-signals | MED | ACTIVE→RESOLVED | `apply_job` on a `draft` `items[0]` while a live item existed → 422 `PROFILE_NOT_LIVE` | D37/D40 | **RESOLVED** (live-item selection, 2026-07-29) — `eaa3f2d1` failed pre-fix; `5804fd6b`/`b3ef7abe` pass |
| 24 | kkb-kn-signals | MED | LATENT | `create_profile` phone 10-vs-12-digit contradiction (twin of #18) | D39/C3/A4 | latent (prose hygiene) |
| 25 | kkb-kn-signals | MED | LATENT | Outbound bot invites callbacks in closings | D5 | latent |
| 26 | kkb-kn-signals | LOW | verify | D40 `location`-required is only durable at the tool-schema level; not verifiable in the prompt | D40 | verify-pending (agent config) |
| 27 | kkb-hi-signals (+kn twin) | MED | ACTIVE (feature gap) | Returning caller wants a different role — bot switched job/applied but never offered to update the stored role; multi-profile not treated 1:1 | feature | **FIXED+deployed** (role-update offer + 1:1 principle, 2026-07-29) — found `a0c24a1d`, verified `15e3f9d9` |
| 28 | maya-hi | HIGH | LATENT/no-repro | `get_profile` `+91` hard-prepend (line 273) → double-prefix on returning caller | D17/C3 | deferred→open-items#3 |
| 29 | maya-hi | MED | LATENT | `hold_message` narrates the silent fetch | D34 | latent |
| 30 | maya-hi | MED | LATENT | Memory-resume intro competes with `get_profile` (memory-as-fetch) | D32 | deferred→open-items#6 |
| 31 | maya-hi | MED | LATENT | "Present 3 best-fit" ranks but never filters → pads unrelated roles | D36 | latent |
| 32 | maya-hi | LOW | LATENT | Rare create→apply fallback (+ out/in batching language) lacks a tool-result boundary | D31 | deferred→open-items#9 (Maya out is harness-testable) |
| 33 | dkb-hi (+kn twin) | MED | ACTIVE | Silent tools (`create_job`/`update_job_*`) `hold_message` narrated aloud | D34 | **FIXED+deployed** (verify-pending: DKB Kn call) — repro `cf3fc048` |
| 34 | dkb-hi (+kn twin) | MED | ACTIVE | Outbound close invites a callback ("ज़रूर फोन करना" / "ಖಂಡಿತ phone ಮಾಡಿ") | D5 | **FIXED+deployed** (verify-pending: DKB Kn call) — repro `cf3fc048` |
| 35 | dkb-hi | MED | LATENT | `update_job_details` lacks the English/Latin-payload rule → Devanagari can leak into the payload | D3/C4 | latent |
| 36 | dkb-hi | MED | LATENT | `${phoneNumber}` undeclared + inconsistent phone format across the 3 payloads | C3/C2 | deferred→open-items#4 |
| 37 | dkb-hi | LOW | LATENT | Female persona has no feminine-verb rule; line 99 uses masculine "समझ गया" | D4 | latent |
| 38 | dkb-hi | LOW | LATENT | No voicemail/IVR bounded exit; no off-topic / are-you-AI / do-not-call handlers | E4 | latent |
| 39 | dkb-kn | MED | ACTIVE-non-breaking | `create_job` `phoneNumber:"Not Available"` (var unbound) + bare-10-digit example vs Hindi's `+91` | C3/C2 | deferred→open-items#4 |
| 40 | dkb-kn | LOW | LATENT | Graceful-Exit sync drift: Kannada omits Hindi's confirm/reflect pre-close step | F | latent |
| 41 | dkb (campaign) | — | ACTIVE (data) | Scheduled `agent_args` field-misaligned (`city:"200"`, salary=an address, `job_role:"Not Available"`) | data | deferred→open-items#5 (data team; no prompt fix possible) |

**Coverage of the 8 bots:** kkb-hi-in (#1–5), kkb-hi-out (#6–10), kkb-kn-out (#11–16), kkb-hi-signals (#17–22, #27), kkb-kn-signals (#23–27), maya-hi (#28–32), dkb-hi (#33–38), dkb-kn (#33–34, #39–41). kkb-kn-in is the sync twin of kkb-hi-in (fixes mirrored, rows 1–2).

---

## C. Voice tests run

Row per call (from `TEST_LOG.md`). All live calls are agent-to-agent via the tester persona; `cf3fc048` is a real historical DKB transcript used for grounding (no fresh live DKB call this run).

| bot | scenario | call_uuid | result | notes |
|-----|----------|-----------|--------|-------|
| kkb-hi-signals `115b38a5` | new-seeker apply | `fb1283cb` | FAIL → FIXED | `create_profile` omitted `location` → `draft` → `apply_job` 422 `PROFILE_NOT_LIVE`. Fix: `location` made a REQUIRED param on both Signals bots (curl-grounded). Analyser D40. |
| kkb-hi-signals `115b38a5` | existing-seeker happy path | `b83e86de` | PASS | Picked the LIVE profile (ignored draft), relevance filter (only Data Entry shown), consent line, apply success, Phase-2 asked area (gender present→skipped), end-confirm incl. gender. |
| kkb-hi-signals `115b38a5` | not interested (declines at gate) | `4e624597` | PASS | 29 s; polite close, no push, no `get_profile`, no pitch. |
| kkb-hi-signals `115b38a5` | wants a different job | `a0c24a1d` | PASS (feature gap) | Applied to Remote CSE (correct `job_id`) on the live profile. GAP: never offered to update the stored role → **role-update feature added**. |
| kkb-hi-signals `115b38a5` | role-update offer verify | `15e3f9d9` | PASS | Bot offered "your role is X — update to Y?", called `update_profile(role)`, then apply success. Minor: set a vague role ("Remote Work"). |
| kkb-kn-signals `33037201` | cooperative existing-seeker | `b3ef7abe` | PASS | Full parity with Hindi: live-selection, role-confirm, apply success, Phase-2 area (gender skipped), end-confirm, graceful KN close. Minor: "ಅಪ್ಲೈ ಆಗಿದೆ" x2. |
| kkb-kn-out `87ab9108` | cooperative + memory-substitution probe | `fa530906` | findings | (1) **D34 ACTIVE** — hold narrated + "info received" on an EMPTY fetch → PORT neutral-hold fix (done). (2) **D32 LATENT** — didn't resume `contact_memory` journey; `get_profile` fired. (3) phone `+9197946350285` → 400 (dicey: harness-DID artifact). (4) age read-back worked. |
| DKB `57814ac8`/`d1a1614f` | static + historical | `cf3fc048` | FIXED (deployed, verify pending) | **D5** callback-invite close + **D34** narrated silent tools, both confirmed in the historical call; both fixed + deployed Hi+Kn. DKB-Kn live verify pending. |

**Harness constraints (apply to all bots):**
- **Sequential only.** One tester DID = one persona at a time (the callee gets `agent_args={}`), so parallel calls can only run the SAME scenario. Concurrency itself IS supported (3 overlapping bridged calls: `c0455a9b`/`08c48abe`/`5d4dc390`) — but different scenarios in parallel need multiple tester DIDs (unavailable).
- **Bridging is intermittently flaky** — some dials fail instantly (dur=0); retry + ~45 s cooldown recovers. `POST /api/call` is rate-limited (~1 per ~13 s → 429); `GET /api/call` lags post-call.
- **Inbound bots are NOT harness-testable** — the tester can only RECEIVE calls, so it cannot dial an inbound bot's `in_did`.
- **The bot looks up the DIALED number** (tester DID), not `agent_args.contact_phone`; Signals has **no delete route**, so the tester-DID profile can't be reset to "new".

---

## D. Fixes deployed

Row per fix. Snapshots are the git-ignored rollback copies; shas + snapshots pulled from `deploy-history.md` / the changelogs. Agent uuids from `raya/agents.json`.

| fix | bots + agent uuids | change | deployed (rollback snapshot) | verified? |
|-----|--------------------|--------|------------------------------|-----------|
| **Signals `location`-required (D40)** — new-seeker apply-blocker | kkb-hi-signals `115b38a5`, kkb-kn-signals `33037201` | Added `location` to `create_profile.parameters.required` (tool-schema PATCH, not prose) → profile mints `live` | 2026-07-29 (Raya tool PATCH) | **RESOLVED** — post-fix applies succeed (`b83e86de`, `b3ef7abe`) |
| **Signals live-item selection (D37)** | kkb-kn-signals `33037201` (+ Hi twin) | Select profile by `lifecycle_status:"live"`, never `items[0]`; never apply to a draft while a live item exists | 2026-07-29 (snap `…kkb-kn-signals-2026-07-29_163727`) | **RESOLVED** — `b3ef7abe` picks live profile, applies |
| **Signals role-update offer + 1:1 profile** | kkb-hi-signals `115b38a5`, kkb-kn-signals `33037201` | On role-mismatch, offer once to update the stored role → `update_profile(role)`; treat profile:user as 1:1 (use only the live item) | 2026-07-29 | **VERIFIED** — feature-gap found `a0c24a1d`, confirmed `15e3f9d9` |
| **KKB inbound D31** — new-caller apply-404 | kkb-hi-in `b6222233`, kkb-kn-in `4ac90bf1` | `create_profile` FIRST → WAIT for its result → then `apply_job` with the returned `profile_id`; forbid same-turn create+apply / empty `profile_id` | 2026-07-30 (Hi snap `…kkb-hi-in-2026-07-30_003534` sha `9b92a60e`; Kn snap `…kkb-kn-in-2026-07-30_004810` sha `9c47ef45`, reconciled to live inventory first) | **verify-pending: inbound** (historical repro `5449910e`, `34f1f587`) |
| **KKB inbound D34** — neutral hold | kkb-hi-in `b6222233`, kkb-kn-in `4ac90bf1` | `hold_message` = neutral "एक मिनट" / "ಒಂದು ನಿಮಿಷ" for `get_profile`/`create_profile`/`update_profile`; only `apply_job` keeps a spoken bridge | 2026-07-30 (Hi snap `…kkb-hi-in-2026-07-30_003943` sha `1b20779a`; Kn same reconcile pass `…004810`) | **verify-pending: inbound** |
| **DKB D5** — callback-invite close | dkb-hi-out `57814ac8`, dkb-kn-out `d1a1614f` | Close reframed so future contact is the team reaching out, not "call me back" (kept "Goodbye") | 2026-07-30 (Hi snap `…dkb-hi-out-2026-07-30_024108` sha `6edaca1f`; Kn snap `…dkb-kn-out-2026-07-30_024109` sha `835f4705`) | **verify-pending: DKB Kn call** (repro `cf3fc048`) |
| **DKB D34** — empty `hold_message` | dkb-hi-out `57814ac8`, dkb-kn-out `d1a1614f` | `hold_message=""` on EVERY tool call (DKB uses no "one moment" filler) | 2026-07-30 (same snaps as DKB D5, `…024108` / `…024109`) | **verify-pending: DKB Kn call** |
| **KKB outbound D34** — neutral hold | kkb-hi-out `da612923`, kkb-kn-out `87ab9108` | Neutral hold for `get_profile`/`create_profile`/`update_profile` (ported from the Signals/inbound D34 fix) | 2026-07-30 (Hi snap `…kkb-hi-out-2026-07-30_024527` sha `3d8606c8`; Kn snap `…kkb-kn-out-2026-07-30_024528` sha `0c195839`) | **verify-pending: kkb-kn-out re-test** (found via `fa530906`) |

Note on the Kannada inbound reconcile: before applying D31/D34 to `kkb-kn-in`, the run **pulled the live prompt** (which carried the real Burger King / CIEL HR inventory the repo lacked), committed the reconciliation (`3e46fa6`), then re-applied the edits on top — so the live inventory was preserved (post-deploy diff = 0 hunks).

---

## E. What needed recurring rounds — the 2026-07-29 Signals saga

The KKB Signals bots (Kn first, then the new Hindi twin) took **many test→fix→retest cycles** across 2026-07-29 before the apply flow was stable. The iteration, in order (all grounded in Parth's real test calls + curl to the Signals Dev API):

1. **`ebb05fd1`** — memory-substitution killed the fetch: the "Introduction Priority Rule (Strict Override)" made the bot resume from `${contact_memory}` and **never fire `get_profile`**; the only tool call was `apply_job` with a memory-sourced id. Also `apply_job` 400'd on `requirements_snapshot` (Raya prunes a literal `{}`). → replaced the memory-resume opener with a fixed neutral greeting + "memory is NOT a fetch" guard; switched the tool payload to a whole-value placeholder. (Analyser **D32/D33**.)
2. **`2289c071`** — fetch narrated aloud; ranking padded with an EV-charging job for a data-entry seeker; a draft profile re-asked known fields and skipped consent. → neutral `hold_message`, relevance filter (no padding), draft-field reuse, consent HARD BLOCK. (**D34/D35/D36**.)
3. **`eaa3f2d1`** — apply 422 `PROFILE_NOT_LIVE`: the caller had multiple profiles and the bot applied to `items[0]` (a stale **draft**) while a **live** item existed. → select by `lifecycle_status`, never by position. (**D37**.)
4. **Schema round** (`7935ce5a`, `ce59a84c`, `51c6f63e`) — the persistence saga: `update_profile` sent a **double-`91`** phone (`+91` + a stored 12-digit) → resolved a *different* user (`user_existed:false`) → 403 `ITEM_NOT_OWNED_BY_USER` → **nothing persisted all call**; gender re-asked though on-profile; "noting it down" said twice; Devanagari/Kannada in payloads; Phase-2 dribbled ("दो बातें… एक और बात") with a wrong count; a "working/studying" question that had no API slot. → phone fixed to a single 12-digit convention, **English-only payloads**, gender-skip-if-present, one-field-per-`update_profile`, decide-missing-fields-once + exact-count, dropped working/studying. (**D38/D39**.)
5. **`fb1283cb`** (overnight harness) — a NEW seeker still hit `PROFILE_NOT_LIVE` because `create_profile` ran **without `location`** → profile `draft`. Curl-confirmed: no-location → draft, +location → live. → `location` made a **required tool-schema param** (a runtime tool-adherence fix, not more prose — cf. D25). (**D40.**)
6. **`a0c24a1d` → `15e3f9d9`** — the last round found a *feature* gap (no role-update offer on a role-mismatch) → added the offer + the 1:1 profile:user principle → verified working.

The through-line: several of these were **runtime tool-adherence** misses (fetch skipped, `location` dropped, double-`91`) that pure prose kept failing to fix — the durable levers were the **tool schema** (`location` required, whole-value placeholders) and structural rewrites, not more instruction weight.

---

## F. Coverage + caveats

**Got a LIVE voice test this run:**
- **KKB Signals Hindi** (`115b38a5`) — 5 scenarios (`fb1283cb`, `b83e86de`, `4e624597`, `a0c24a1d`, `15e3f9d9`).
- **KKB Signals Kannada** (`33037201`) — 1 scenario (`b3ef7abe`).
- **KKB Kannada outbound** (`87ab9108`) — 1 scenario (`fa530906`).

**Grounded on a real HISTORICAL transcript (no fresh live call this run):**
- **DKB** (`cf3fc048`, 2026-07-04) — D5 + D34 confirmed; fixes deployed Hi+Kn, DKB-**Kannada** live verify still pending.
- **KKB inbound Hindi** (`b6222233`) — 15 historical calls including the D31 repros (`5449910e`, `34f1f587`), the D34 repros (`8ddcaa5a`, `1fde1677`), and positive controls.

**Static-only (no completed tool-call transcript exists — all recent calls dur=0 / short):**
- **kkb-hi-out** (`da612923`), **maya-hi-out** (`47fdffe6`), **dkb-hi** (`57814ac8`). Their findings are LATENT-by-construction and need a fresh live probe to move ACTIVE.

**NOT covered this run:**
- **Maya live** (outbound `47fdffe6` and inbound `df99f501`) — no live call; Maya's D17/D32/D36/D31 findings remain static/latent. Maya outbound IS harness-testable (queued, open-items#9).
- **KKB Hindi outbound live** (`da612923`) — no completed live call; the D34 fix is deployed but unverified live.
- **All inbound bots** (KKB in Hi/Kn, DKB in, Maya in) — structurally **not harness-testable** (tester can only receive). The inbound D31/D34 fixes are deployed + rollback-snapshotted but **verify-pending** — they need a real inbound call (open-items#1).

**Tester limits:** single tester DID (sequential scenarios only); the persona is single-line (limited multi-turn realism); Signals has no profile-reset/delete route so new-seeker Signals paths can't be re-tested on the tester DID.

**Bottom line:** the ACTIVE, user-facing breakages found this run are fixed + deployed (all rollback-snapshotted). The remaining volume is LATENT static risk on bots with no reproducing transcript — captured in `PRIORITY_BUGS.md` and, where a decision/probe/backend answer is needed, in `open-items.md`. See `ideas.md` for how to close the harness gaps that block the outstanding verifications.

---

## G. Post-restart continuation (2026-07-30, morning — after manual session restart)

The user restarted the session manually and asked to (1) re-verify the fixes to a **high bar** ("retest until you can confirm everything is working perfectly"), (2) chase the KKB-outbound apply glitch, and (3) do the bonus tasks. What happened:

### G.1 — KKB outbound: `new_seeker` removed → fetch-driven flow VALIDATED live
- **Root cause of the earlier "apply glitch":** it was a **test-data artifact**, not a bot bug — the harness passed `new_seeker="No"` while the tester DID has **no** profile (an impossible production state), so the branch-on-flag router misfired. Per the user's direction ("remove the new_seeker variable, like we did for the Signals bots"), the outbound bots were restructured to be **fetch-driven**: always call `get_profile` first and branch on the RESULT (profile → returning; empty → new caller), exactly like the Signals + inbound bots. `${new_seeker}` and all 13 references were removed; the apply-router two-step (create→WAIT→apply, never empty `profile_id`) was left unchanged. Hi + Kn, surgical, symmetric. Deployed (commit `ebbb3e2`), rollback-snapshotted (`pre-deploy-kkb-{hi,kn}-out-2026-07-30_0401*`).
- **Validated on TWO live bridged calls** (`7e5e1173`, `ab930586`, kkb-kn-out): `get_profile` **always fires first** → empty `[]` → **new-caller path** → `create_profile` **before** `apply_job` (never batched, never empty `profile_id`) → **no false success** → age/gender gate respected → D34 neutral hold. `create_profile` returned a clean `SUCCESS` with a valid `profileId`. **The `new_seeker` removal works and broke nothing.**

### G.2 — kkb-kn-out apply 404 → flagged as a BACKEND issue (not a prompt/config bug)
- On the validated call, everything the bot did was correct, but `apply_job` returned **HTTP 404 "Invalid or missing profile_id"** on the Karnataka BAP endpoint (`onest-lite-bap.dhiway.net`) **even with the valid `profileId`** that `create_profile` had just minted (both job attempts). Grounded in `7e5e1173` + `ab930586`.
- **This is a backend matter**, likely a cross-ecosystem mismatch (create writes to `jobs-onest-interface` with `agentId: up-getjob`; the Kannada bot applies on the Karnataka BAP). **Flagged**: sheet row 84 = `Flagged - Backend Issue`; open-items #10. Needs the backend/LitWiz team to confirm whether real Karnataka outbound applies succeed in production.

### G.3 — Endpoint mis-diagnosis, caught and reverted (a lesson, now in the analyser)
- I initially read kkb-kn-out's Karnataka endpoints (`jobs.onest.seeker` / `onest-lite-bap`) as *drift* vs the Hindi (UP) twin and PATCH-aligned them to the UP hosts. The user corrected: **"karnataka doesn't use those endpoints."** I **reverted immediately** from the pre-change tools snapshot — live config restored to the Karnataka endpoints, instructions byte-intact, **net change = none**.
- **Durable learning captured** in analyser `bug-patterns.md` **C10** (rewritten): endpoint differences between language twins can be **region-specific by design** (KN=Karnataka, HI=UP) — never "align to twin" without the owner's confirmation; a tool 4xx with a *well-formed id* is a **backend** flag, not a prose or config fix (reinforces D25). Deploy-history annotated with the revert.

### G.4 — Phone handling: intermittent, not a hard bug
- Across the two live calls the same `+91`-prefixed input produced a **clean** `+917946350285` once and a **mangled** `+9197946350285` once — model-adherence flakiness (D39 class), not a deterministic prompt fault. The current prompt rule already forbids the mangled shape; a stronger deterministic "take the last 10 digits, prepend exactly one `+91`" rule is **ready** but was **not** shipped tonight (kept the change surface minimal after the endpoint mis-step; low incidence; see open-items #2/#3). Production input format (`91`-prefixed 12-digit, no `+`) should be the basis for any future hardening.

### G.5 — Bonus: 5 combined `${call_direction}` bots (built v0; NOT deployed — needs a direction-aware v1)
Goal: one prompt per bot that serves BOTH inbound and outbound, branching on the Raya auto-variable `${call_direction}`. Built via a 10-agent workflow (5 builders + 5 adversarial surgical-diff reviewers). All 5 v0 prompts written to `raya/combined/*.md`.

| Combined bot | Lines (out→combined) | Review | State |
|---|---|---|---|
| kkb-hi-combined | 1366→1615 (+249) | PASS (additive, math-verified) | v0, inbound-incomplete |
| kkb-kn-combined | 1364→1690 | **FIX_NEEDED** | v0 + inherited kkb-kn-in inventory-prose bug (open-items #11) |
| maya-hi-combined | 1140→1436 | PASS | v0, inbound-incomplete |
| dkb-hi-combined | 911→964 | PASS | v0, dangling "Inbound Routing Rule" refs |
| dkb-kn-combined | 893→953 | PASS | v0, dangling "Inbound Routing Rule" refs |

**What v0 IS:** a strictly-additive transform of each **outbound** base — `${call_direction}` var + a gated greeting (outbound vs inbound scripts, each verbatim from its own source) + (seeker bots) the folded-in hardcoded Job Inventory gated to inbound + a gated close where it diverges. Independently verified for kkb-hi: **0 deletions/changes vs the outbound base** (purely `>` appends), gates present, memory block verbatim. So v0 **preserves the outbound direction byte-for-byte** — `call_direction=outbound` behaves exactly like today's standalone outbound bot.

**What v0 is NOT (why it must not be deployed as-is):** the additive constraint left the **shared flow** still written in outbound terms, so the **inbound** direction would misfire:
- Seeker bots: "Job Presentation Pre-check", "Hallucination Guard", and "No-Match Fallback" trigger on empty `${recommendations}` — which is unset on inbound — so they could fire No-Match/close before the hardcoded inventory is consulted. Profile-handling still runs the outbound **permission-to-fetch** ask, which the inbound design bans (inbound fetches silently). Maya additionally still carries the `${new_seeker}` branch (unsubstituted on inbound).
- DKB bots: the folded inbound greeting references an "Inbound Routing Rule" section that doesn't exist in the combined file (the shared outbound "Phase Entry Rule" is kept). Builder notes it "degrades gracefully" to Phase-3 new-job capture, but the dangling refs should be resolved.

**v1 to make them deployable (spec):** make the shared job-source sections (`No-Match`, `Hallucination Guard`, presentation pre-check, get/create/apply "the selected job") reference *the source `${call_direction}` selects* rather than `${recommendations}`; gate the profile-handling permission-ask on `${call_direction}`; (Maya) gate/remove the `${new_seeker}` branch; (DKB) resolve the Inbound-Routing-Rule refs; (kkb-kn) fix the inventory-prose contradiction (open-items #11) first. This is an edit to **shared logic**, not a greeting swap — bigger and higher-risk than v0, and the inbound branch is **not harness-testable** (needs a real inbound DID). The outbound branch of any v1 IS harness-testable.

**Further bonus (Signals port):** not started — depends on a settled v1 pattern.

**Recommendation:** do NOT stand up 5 experimental agents on v0 (their inbound is knowingly broken and can't be harness-verified, and the Raya console has no delete). Complete v1 (direction-aware shared flow) first, review, then create + outbound-smoke-test. v0 scaffolds + this spec are the head start.

### G.6 — Combined bots: v1 built + 5 agents created, but a PLATFORM BLOCKER found (call_direction not injected)
After the v0 finding (G.5), I ran a direction-aware **v1** pass (workflow: 5 builders + 5 adversarial reviewers) that made the shared flow honor `${call_direction}` — job source resolves to the hardcoded inventory on inbound (not empty `${recommendations}`), and the `get_profile` permission-ask is gated (outbound asks, inbound fetches silently). Verdicts: **dkb-kn + maya-hi PASS; kkb-hi/dkb-hi/kkb-kn FIX_NEEDED** (residual inbound spoken-nuance). I then fixed kkb-kn's two real structural gaps (ungated inbound fetch + the stale Kannada inventory prose → rewritten to Karnataka; 0 UP leftovers) and **created all 5 as experimental Raya agents** (`deploy=false`, NOT migrated):

| Combined bot | agent uuid | source cloned |
|---|---|---|
| kkb-hi-combined | `3f521174` | kkb-hi-out |
| kkb-kn-combined | `f38da775` | kkb-kn-out |
| maya-hi-combined | `904f333f` | maya-hi-out |
| dkb-hi-combined | `fabda71d` | dkb-hi-out |
| dkb-kn-combined | `847a85e2` | dkb-kn-out |

**THE BLOCKER (open-items #12).** The outbound smoke test on kkb-hi-combined (`b2e9e1e9`) exposed a platform issue that invalidates the approach as-tested: I triggered it OUTBOUND with real `${recommendations}` (Burger King/Pantaloons), but the bot opened with a **welcome** greeting and presented **hardcoded-inventory** jobs (CY Future Noida, Weavings Greater Noida) — i.e. it ran the **inbound** branch. The call's `agent_args` = `[contact_memory, contact_name, contact_phone, country_code, recommendations]` — **`call_direction` is absent (None)**, and it's ALSO absent from real standalone `kkb-hi-out` calls. So `${call_direction}` is **not injected on `POST /api/call`-triggered calls**; with it empty the branch is ambiguous and the model defaults to inbound (inventory + welcome).

**Conclusion:** the combined `${call_direction}` bots are BUILT (v1) and CREATED, but **cannot be validated or trusted until LitWiz/Raya confirm when/how `call_direction` is actually set** (likely only on real DID telephony, or in the prompt template rather than `agent_args`, or needs per-agent enabling). The 5 experimental agents exist for the user to test on REAL inbound/outbound DID calls where the flag may be populated. **Recommendation: keep the separate inbound/outbound bots (today's production design) — they don't depend on a runtime direction flag — until `call_direction` injection is confirmed.** Further bonus (Signals port) is not started (gated on a validated pattern).
