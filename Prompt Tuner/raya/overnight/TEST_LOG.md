# TEST LOG — overnight run (append every call)

Columns: bot | scenario | call_uuid | result | key observations. "FIXED" = bug found + fixed this session.

## KKB Hindi Signals — `115b38a5`
| scenario | call | result | notes |
|---|---|---|---|
| new-seeker apply | fb1283cb | 🐛 FAIL → **FIXED** | create_profile omitted `location` → profile `draft` → apply_job 422 PROFILE_NOT_LIVE. Fix: `location` now REQUIRED param on create_profile (both Signals bots). Curl-grounded (no-loc→draft, +loc→live). Analyser D40. |
| existing-seeker happy path | b83e86de | ✅ PASS | picked LIVE profile (ignored draft), relevance filter (only Data Entry shown), consent line, apply success, Phase-2 asked area (gender present→skipped), end-confirm incl. gender. |
| not interested (declines at gate) | 4e624597 | ✅ PASS | 29s; closed politely, no push, no get_profile, no pitch. |
| wants a different job (fallback/re-target) | a0c24a1d | ✅ PASS (feature gap found) | applied to Remote CSE (correct job_id) on live profile. GAP: bot did NOT offer to update the stored role → **feature added** (role-update offer). |
| role-update offer verify | 15e3f9d9 | ✅ PASS | bot offered "your role is X — update to Y?", called update_profile(role), then apply success. MINOR: set role="Remote Work" (vague) instead of the real target role — quality nit, logged. |

## KKB Kannada Signals — `33037201`
| scenario | call | result | notes |
|---|---|---|---|
| cooperative existing-seeker | b3ef7abe | ✅ PASS | Full parity w/ Hindi: live-selection, role-confirm "ಕೆಲಸ ಮಾಡ್ತಾ ಇದೀರಿ" (doing), apply success, Phase-2 area (gender skipped), end-confirm incl. gender, graceful KN close. MINOR: "ಅಪ್ಲೈ ಆಗಿದೆ" x2; role="Remote Work" reflected (from prior test's role-update). |

## KKB Kannada outbound (up-getjob) — `87ab9108`
| scenario | call | result | notes |
|---|---|---|---|
| end-to-end retest (phone fix + real up-getjob job_ids) | 082b21ea | ✅ phone+D34 · 🐛 apply glitch | **Phone-malform FIXED + VERIFIED** (`get_profile` sent clean `+917946350285`). D34 hold neutral ✅. Real up-getjob jobs shown ✅. **BUT new-caller apply BROKE:** bot called `get_profile` 2× (skipped `create_profile`+`apply_job`) and **falsely claimed applied**. Apply-router prose is already correct/strong → **runtime tool-adherence glitch** (friction-provoked: bot re-asked known fields → persona pushed back). Consistency re-check `bfai1a2ms`. Per D25 not prose-fixable → open-items + platform backstop if consistent. |
| D34 re-verify (post-fix) | (bz8fjqumk) | ✅ D34 hold VERIFIED | `get_profile` hold_message now neutral "ಒಂದು ನಿಮಿಷ" (was "ನಿಮ್ಮ ಮಾಹಿತಿ ಪರಿಶೀಲಿಸುತ್ತಿದ್ದೇನೆ"). RESIDUAL: bot still SPEAKS "ನಿಮ್ಮ ಮಾಹಿತಿ ಸಿಕ್ತು" as content (runtime narration, prose ban exists → open-items, not prose-fixable). Phone still "+9197946350285" (open-item #2). |
| cooperative + memory-substitution probe | fa530906 | 🐛 findings | (1) **D32 memory-substitution LATENT** — bot opened neutrally, did NOT resume the `contact_memory` "Fitter\|Hubballi" journey; get_profile fired. (2) **D34 ACTIVE** — get_profile/create_profile `hold_message="ನಿಮ್ಮ ಮಾಹಿತಿ ಪರಿಶೀಲಿಸುತ್ತಿದ್ದೇನೆ"` spoken; also "ನಿಮ್ಮ ಮಾಹಿತಿ ಸಿಕ್ತು" said on an EMPTY fetch (`[]`). → PORT neutral-hold fix to KKB outbound pair. (3) **Phone malform** — create_profile `phone:"+9197946350285"` → HTTP 400 "Invalid Indian phone number"; DICEY (may be harness-DID artifact since contact_phone bound to tester DID) → open-items + ready exactly-one-+91 fix. (4) Age read-back worked (ASR "28"→"8" caught + corrected). |

## DKB (Hi `57814ac8` + Kn `d1a1614f`) — up-postjob, outbound
| scenario | call | result | notes |
|---|---|---|---|
| static + historical (cf3fc048) | — | 🐛→✅ D5 FIXED+VERIFIED; D34 deployed | **D5** outbound close invited callback → reframed to "our team will reach out": **VERIFIED** on DKB Kn verify `90959fdc` (bot closed "ನಮ್ಮ ಟೀಮ್ ನಿಮ್ಮ ಜೊತೆ ಮತ್ತೆ ಮಾತಾಡುತ್ತೆ. Goodbye", not "phone ಮಾಡಿ"). **D34** empty-hold deployed both langs (…024108/…024109) — VERIFY-PENDING (the `90959fdc` call hit the 4-min cap before reaching create_job; get_talent_insights hold still narrated — arguably OK since its result is spoken). Phone-format (bare 10-digit Kn) → open-items. |
| employer new-vacancy (verify D5/D34) | 90959fdc | ⚠️ partial | D5 ✅. **NEW: unbounded read-back loop** — bot asked "vacancies ಎರಡು, ಸರಿನಾ?" ~8× on a 2-vs-22 ASR/persona confusion, never capping → wasted the call, hit max duration (generic checklist §4 re-prompt bound). Partly a persona artifact (tester garbled "2"→"22"); the bot's failure to cap the loop is a real weakness → open-items. |

## Maya outbound (up-getjob, campus, Hindi) — `47fdffe6`
| scenario | call | result | notes |
|---|---|---|---|
| student cooperative (D34 + feature check) | baf836fe | 🐛→✅ D34 fixed + ✅ features | **D34 ACTIVE** — create_profile hold "आपकी जानकारी तैयार कर देती हूँ" narrated → PORTED neutral-hold fix (DEPLOYED maya-hi-out `47fdffe6` + maya-hi-in `df99f501`). **All Maya features WORKING:** campus identity ("माया, एलआर कॉलेज की ओर से"), feminine voice, student gate, and **MPL Competition offer fired** (first live observation). create_profile phone clean single +91 (so the malform is kkb-kn-out-specific). Harness artifacts (not Maya bugs): apply 404 (Signals job_ids passed to an up-getjob bot), max-duration hit. |

## Harness / platform findings (apply to all bots)
- **Concurrency SUPPORTED** — 3 parallel calls to the tester DID overlapped in time, all bridged (c0455a9b/08c48abe/5d4dc390). BUT one tester = one persona at a time (callee gets `agent_args={}`), so parallel = SAME scenario only. Different scenarios in parallel need multiple tester DIDs (unavailable) → **testing is sequential** (Approach B).
- **Bridging is intermittently flaky** — some dials fail instantly (Failure/Unanswered, dur=0); retry + ~45s cooldown recovers. Rapid bursts degrade it.
- **`POST /api/call` rate-limited** ~1 per ~13s (429).
- **`GET /api/call` lags** post-call (Pending/dur=0 before finalize) — re-poll.
- **Bot looks up the DIALED number** (tester DID), not agent_args.contact_phone. Signals has **no delete route** → the tester-DID profile can't be reset to "new".
- **out_did:** omit it on trigger (passing it → Unanswered).

## Minor issues seen (low priority — candidate open-items)
- Role-update sets a vague role value ("Remote Work") instead of the actual target role → tighten to "use the real target role, not a loose descriptor".
- Post-apply "apply ho gaya / ಅಪ್ಲೈ ಆಗಿದೆ" restated across Phase-2 turns (mild repetition).
- Role-update offer bundled with the next question instead of ending the turn to wait (both minor; Signals bots).
