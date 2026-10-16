# Overnight report — 2026-09-03, 06:10 IST

## Fixed and verified by call

| bug | bot(s) | proof |
|---|---|---|
| Location: bot spoke the profile's place, not the campaign's | KKB hi + kn Signals | 2a6ccc0b, 62dc3ee7 (दिल्ली) · 1119c329, af1c6e2a (ಹುಬ್ಬಳ್ಳಿ) |
| "Job posting expiring" told to NEW providers (sheet row 105) | DKB hi + kn Signals | 2c197514, b1b71d68, 9e2e0056 |
| DKB invented role / vacancies / salary / company name | DKB hi + kn Signals | 46812a71, 3f996a3d |
| Relevance filter hid jobs the caller asked to hear | KKB hi + kn Signals | d9bf1f43, 4b0ea64d |
| Location asked though the profile already had it | KKB hi inbound | a6ca5a12, 52ef63d2 |
| "No such job" + hang-up while jobs went unnamed | KKB hi + kn inbound | a6ca5a12, b45a7e22 |
| City slot named one city when jobs spanned two | KKB kn Signals | 8976c120 |
| TRRAIN on the Signals API (no migration needed) | TRRAIN hi + kn | c83fdf8d, 755b73ea |
| Maya: no false "we have <role> jobs" claim | Maya hi Signals | 962f4476, 4882a3c1 |

Earlier the same day: greeting waits (67058058, 7f3aa27d) · role changed without asking
(67058058, 4eed42c8) · consent/data-sharing line before apply (67058058) · read-back is one
question (0178c996, 503440a3) · apply-success not spoken after a failed apply (9cb7e453) ·
Muradnagar / गाज़ियाबाद spellings (0decf61a, 7f3aa27d).

## Closed after the first draft of this report

- **DKB no longer claims to be the government.** Rows 4/56 had already decided this; it was applied
  to KKB and Maya and DKB was missed. Now the city administration's employment initiative in all
  five spoken lines, both languages. Verified: `dc200be7` (hi), `def744e0` (kn).
- **"Already applied" now names the likely cause truthfully.** The model still never receives the
  tool error body, so it cannot KNOW — but the caller's question is answerable anyway: "इस जॉब में
  अभी अप्लाई आगे नहीं बढ़ा — हो सकता है आपकी एप्लीकेशन पहले से लगी हो" / "ನಿಮ್ಮ ಅಪ್ಲಿಕೇಶನ್ ಈಗಾಗಲೇ ಇರಬಹುದು".
  True whichever the reason, and it names the commonest one. Verified: `87427928`.

## Still owed to the platform (not prompt-fixable)

- **LitWiz: surface the tool error body to the conversation model.** 9 `ACTION_LIMIT_REACHED` calls
  across 3 bots, 2 languages and 3 prompt structures never once produced the explicit line. Until
  that lands, the bot hedges rather than states.
- **LitWiz: a read-only endpoint for a contact's stored memory.** Without it, memory-gated rules
  (never-ask-twice, the duplicate pre-check) cannot be verified from the harness at all.
- **A second tester DID.** One line means one call at a time; it is also why fixture state is shared
  and polluted.

## The pattern worth keeping

Three separate bugs tonight had one cause: **the model could not SEE a value the prompt described.**
Location, DKB's posting fields, and the withheld jobs. Four wordings of a resolution rule failed
before the fix turned out to be printing the value (or substituting the token) at the point of use.
Wording was never the problem in any of them.

## Harness facts established
- Inbound bots ARE testable: PATCH `{"out_did": <INTEGER>}`, then dial the tester.
- The platform DROPS empty-string args; a missing field arrives as an unsubstituted token.
- `contact_memory` sent via agent_args does not reach the model; stored memory cannot be read.
- One tester DID = one call at a time. Keep `caffeinate` running or the machine sleeps mid-sweep.


## After the report — Khushboo's 03 Sep reports (5015866 / 5016050)

**Reported:** on a failed apply the bot said "हो सकता है आपकी एप्लीकेशन पहले से लगी हो" for all three
jobs she tried, so a real duplicate was indistinguishable from a broken apply. That hedge was mine,
added a few hours earlier, and she was right that it is worse than naming the failure.

**Worth knowing:** all three applies actually returned `ACTION_LIMIT_REACHED` — they WERE duplicates
from her 02 Sep test calls (`29d76039`, `d55db597`, `1df89679`). The hedge was factually correct every
time and still unusable. Correctness is not the same as being useful to the person listening.

**Fixed — three distinct outcomes, decided by the bot's own `duplicate_check` assertion:**
| what the bot did | what it says |
|---|---|
| pre-check matched, tool not called | "इस जॉब के लिए आपकी एप्लीकेशन पहले से लगी हुई है।" |
| sent `not-applied-before`, tool errored | "इस नौकरी के लिए अप्लाई अभी आगे नहीं बढ़ा है, technical issue है। हमने आपकी रुचि नोट कर ली है।" |
| tool succeeded | "अप्लाई हो गया है।" |
Verified `22781eb6`. No new information needed — the bot already knows which case it is in.

**And a second bug that surfaced on the same call:** the service-provider acknowledgement turn said
"अप्लाई हो गया है" seconds after the failure line. Fixed twice tonight, regressed twice, because every
version asked the model to REMEMBER across turns. Now positional and checkable against the turn in
front of it: the success line may only appear in a turn that also contains a fresh `apply_job` result.
Verified 4/4 — `778cbb8f`, `57e3716b`, `c86fca56` (hi) and `af228ce3` (kn), all clean on the detector.

**Trade-off she should know about:** the bot will now say "technical issue" for a real duplicate its
memory has not recorded, because it never receives the tool error body. That is the direction she
chose, and it is why the LitWiz ask matters.
