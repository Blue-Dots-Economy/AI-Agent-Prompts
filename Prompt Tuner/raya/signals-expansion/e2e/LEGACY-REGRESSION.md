# Legacy (non-Signals) bot regression — 2026-08-01

Diagnostic to decide whether to restructure the old up-getjob/ONEST bots to the proven Signals-bot
shape (keeping the Dhiway schema). Grading: **fork** (new_seeker yes vs no), **fields asked**,
**apply not failing**, **no repetition**, + generic checklist.

The 6 legacy bots:
| bot | uuid | file | backend |
|---|---|---|---|
| KKB Hindi outbound | da612923 | Maya... KKB Placeholder | up-getjob |
| KKB Kannada outbound | 87ab9108 | KKB Placeholder- Kannada | up-getjob |
| KKB Hindi inbound | b6222233 | KKB Inbound Placeholder | up-getjob |
| KKB Kannada inbound | 4ac90bf1 | KKB Inbound Placeholder- Kannada | up-getjob |
| Maya Hindi outbound | 47fdffe6 | Maya/Maya Hindi.md | up-getjob |
| Maya Hindi inbound | df99f501 | Maya/Maya Inbound.md | up-getjob |

## Findings

### KKB Hindi outbound (da612923)
- **[MAJOR] Dead new_seeker fork.** `new_seeker="no"` (0b2e82c1) and `new_seeker="yes"` (e0df338a) BOTH fetch the profile (get_profile fires + a permission-ask). `new_seeker="yes"` should skip the fetch and go to discovery — it doesn't. The fork the Signals bots removed (fetch-driven) is broken here.
- **[MINOR-MAJOR] Repetition.** The recording disclosure ("यह बातचीत रिकॉर्ड की जा सकती है") + the full "शहर प्रशासन… क्या आप काम ढूंढ रहे हैं?" framing repeat in turn 2 (e0df338a, 0b2e82c1).
- **[NOTE/old-design] Permission-ask before fetch.** Asks "क्या आपकी बेसिक जानकारी देख सकती हूँ?" before get_profile — the Signals bots do a SILENT fetch (D24/B2 class the Signals rebuild fixed).
- Apply path: re-testing with an accepts-any persona (data-entry persona didn't match the machine-operator recs — test-data mismatch, not a bug).

- **[MAJOR] `update_profile` is BROKEN.** Apply-path re-test (0bbd8f79): apply_job → SUCCESS (Dhiway ONDC on_confirm), but Phase-2 `update_profile` → **`Exception: API details not found`** (the tool has no API config) — post-apply enrichment cannot persist AT ALL.
- **[MAJOR] Non-schema field + unstorable question.** The bot sent `update_profile({totalYearsOfExperience: 2})` (the same non-schema field class fixed in Signals) and asked "अभी आप कोई काम कर रहे हैं, या पढ़ाई कर रहे हैं?" (working/studying — no storage; the exact question removed from the Signals bots).
- **[MINOR] Repetition/jumble** at the update_profile failure (the next question + "नोट कर लिया" collide).

## DECISION (2026-08-01): RESTRUCTURE — do not patch
The legacy KKB-Hi bot alone has ~6 structural defects (dead fork, silent-fetch missing, broken update_profile, non-schema field, unstorable question, repetition) — all classes the Signals rebuild already solved. Per the user ("don't waste time re-testing, just do the rewrites"), the 6 legacy bots will be **rewritten to the proven Signals-bot STRUCTURE while keeping the Dhiway/up-getjob SCHEMA + tools** (get_profile `phoneNumber:+91…`, apply_job Dhiway `on_confirm`, the up-getjob profile/recommendations shapes). This is a structure transplant (the inverse of the Signals migration). Each rewritten bot is tested per the 3-tier standard — every variant independently.

Bugs to fix by the restructure: silent fetch (no permission-ask), fetch-driven (no dead new_seeker fork), no unstorable questions (working/studying, exact-years as a bad field), a working update_profile (or drop it if Dhiway has no endpoint), no framing/disclosure repetition, the 9 stabilisation patterns.

## Restructure progress
### KKB Hindi outbound (da612923) — ✅ RESTRUCTURED + VOICE-VERIFIED (7c1389ae)
Signals structure on the Dhiway contract. Tier-1 fixes confirmed live: **silent fetch** (no permission-ask, no "जानकारी मिल गई"), **no update_profile** (no 500), **no unstorable "working/studying?" question**, clean post-apply close. Tier-2: **apply_job → Dhiway on_confirm success**, relevance-filtered presentation intact. Correction: KKB-Hi never had a `new_seeker` fork (always-fetch is intended) — the earlier "dead fork" note was a misread; the real bugs (permission-ask / broken update_profile / unstorable question / repetition) are the ones fixed. Minor to apply to all 6: the CD3 outbound-frame close ("हमारी टीम आपसे फिर संपर्क करेगी" vs a callback-invite). Revert snapshot: snapshots/legacy-kkb-hi-out.instructions.pre-restructure.md.

### All 6 restructured + voice-tested (2026-08-01)
| bot | uuid | verdict |
|---|---|---|
| KKB Hindi outbound | da612923 | ✅ silent fetch, apply→Dhiway success, no update_profile/unstorable Q (7c1389ae) |
| KKB Kannada outbound | 87ab9108 | ✅ structure (silent fetch, single-+91 phone, create_profile SUCCESS); apply 404 = stale test job_id, not a bot bug (f28e565c) |
| KKB Hindi inbound | b6222233 | ✅ inbound welcome, silent fetch, apply→Dhiway success (2b505a45) |
| KKB Kannada inbound | 4ac90bf1 | (test running) |
| Maya Hindi outbound | 47fdffe6 | ✅ campus/feminine/MPL, silent fetch, apply→Dhiway success (75d8ffe1) |
| Maya Hindi inbound | df99f501 | ✅ campus/feminine/MPL, silent fetch, apply→Dhiway success (59feb365) |

**Phone-doubling fix (CD6-analog for Dhiway).** Maya-inbound caught a real per-variant bug: `phoneNumber:"+91+91…"` (the Dhiway `${contact_phone}` already carries `+91`, but the literal template `+91${contact_phone}` made the model double it) → get_profile empty + create_profile 400. Fixed the literal template → `${contact_phone}` (as-is) in ALL 6 Dhiway rewrites; re-verified Maya-in applies cleanly. **This is the "test every variant" rule paying off — extrapolating from Maya-out passing would have shipped the bug.**
- out_dids: set 911204404274 on the 3 legacy inbound bots (for inbound-via-outbound testing; harmless on inbound-only). KKB-Kn-out's production out_did (918037006352) restored after testing.

### KKB Kannada inbound (4ac90bf1) — ◑ structure verified, apply VERIFY-PENDING (14b128f3)
Inbound welcome ✅, silent-ish fetch, real Karnataka inventory presented, consent + HR-fallback ✅. Two findings: (1) **D29** — greeting + get_profile bundled in turn 1 (two-turn router didn't hold; the Hindi twin did it right — runtime variance). (2) **D28** — apply_job used `profile_id:"19"` (numeric) → 404 "Invalid or missing profile_id"; the fetched profile had a numeric top-level id (side-effect of the create_profile run in the KKB-Kn-out test contaminating this phone), so "returning → top-level id" yielded a non-UUID. The Hindi twin (byte-identical structure) applies cleanly with a UUID. **Needs a clean-profile re-test to confirm apply; the structure fixes (silent fetch/no-update_profile/phone) are verified.**
