---
name: voice-test
description: Test a live Raya voice bot with real agent-to-agent phone calls (a persona "tester" agent plays the caller) and grade each call mechanically against written pass/fail rules, the universal checks and the bot's checklist, with call ids read from the run rather than guessed. Runs a test-case Google Sheet and fills in Actual Response / Verdict / call ids per row, and adds newly found bugs as rows. Use when someone says "test this bot", "test this fix", "verify the fix", "reproduce this bug", "call the bot", "run this sheet", "run these test cases, 3 calls each, and update the sheet", "run the Smoke rows", "test the inbound bot", "test the Kannada version", or before a demo. Works for outbound and inbound bots in every language.
---

# Voice Test

**What it produces.** Real calls to the bot under test, each graded from its full call record, with a
call id behind every verdict; the sheet rows filled in when a sheet was given; and a short report
(Fixed / Failed / New bugs / Next, root `CLAUDE.md` → "How to report back"). Two separate steps,
always: **run** a call, then **grade** it. A printed transcript is not a grade.

## Fast paths

| The user says | Do this |
|---|---|
| "run this sheet" / "run these test cases, N calls each, update the sheet" | → **Run a test sheet**. |
| "test this fix" / "verify the fix" | The issue's `R` row (write it first if missing: `/generate-test-cases` → "add a test case for this bug"), **N ≥ 3 calls on every affected variant**, then the blast-radius rows around the change. Report per fix with call ids (→ Report contract). |
| "reproduce this bug" | One call that recreates the reported inputs and behaviour, read against the original call's `agent_args` first (it may be an input problem, not a bot bug). Report what the call showed, not the possible causes. |
| "test the inbound bot" | → Run one call → **Inbound bots**. Inbound is testable. |
| "does the bot remember the caller?" / "test memory" / "the second call forgot the first" | → **Memory test**: two calls from the same number, graded per detail. |
| "test before the demo" | The Smoke rows of every variant being shown. |

**Before the first call of any session:** read the bot's open-issues list (the tracker sheet, or
`raya/intake/<bot-id>.md`) and say how many are open. **After the last:** update every issue you
touched (status, call id, date). Every report ends with what is still open from before.

**Written cases first.** Grade only against written cases: a lint-clean sheet row or a manifest case
(`raya/testcases/<bot-id>.json`). Without one there is no pass rule, no FAIL signal and no record of what
was never exercised. If what you are about to test has no row, write it first (`/generate-test-cases`).

## Setup

- `raya/.env` (`RAYA_BASE_URL`, `RAYA_API_TOKEN`), never committed.
- **The tester agent** ("Testing Agent- Blue Dots", uuid `f60e0899-aa3a-4be7-9b4f-0296bd28ef48`, in_did
  `911204404272`, so the 10-digit DID to dial is `1204404272`, as of 2026-10-14). It is
  non-interruptable, capped at 5 minutes, and its persona is swapped by PATCHing its instructions.
  **DIDs get rebound** (the old `7946350285` now belongs to a Purple Dots bot): confirm with
  `python3 scripts/raya_testcall.py whoami <tester_uuid>` before a session. `raya_testrun.py` refuses to
  dial a DID that is not the tester's `in_did`.
- `scripts/raya_testcall.py`: `whoami <uuid>` · `persona <tester_uuid> <file>` · `lang <tester_uuid>
  <code>` (language and voice pair from `raya/voices.json` for `RAYA_ACCOUNT`, default `ekstep`) ·
  `call` (raw POST, rarely needed).
- `scripts/raya_testrun.py <bot_uuid> <to_10digit> <args.json> <tester_uuid> [label]`: one call, retries
  the connect (4 tries, 90 s apart), polls to the end, prints the transcript. No grading.
- `scripts/raya_call.py <agent_uuid> [limit] [offset]`: past calls with full tool arguments (a tool turn
  has `content: null` and the payload in `tool_calls[].function.arguments`).
- `scripts/testcase_sheet.py pull | lint | result | add-bug`: the sheet, through the service account.
- Personas `raya/personas/` (index: `scenario-catalog.md`); fixtures `raya/testcases/args/`; checklists
  `reference/checklists/` (`generic.md` for every bot, plus the bot's own).
- Graders over real traffic: `raya/regression/grade_call.py <call-uuid> …` (mechanical checks; SKIP is
  not PASS), `raya/regression/run_runtime_checks.sh [--since …] [--agent …]` (all transcript detectors),
  `raya/regression/spoken_form.py --call <uuid>`.

## Run one call

```bash
python3 scripts/raya_testcall.py persona <tester_uuid> raya/personas/<lang>-<behaviour>.md
python3 scripts/raya_testcall.py lang    <tester_uuid> <lang>          # match the bot's language
python3 scripts/raya_testrun.py <bot_uuid> <tester_10digit_DID> <args.json> <tester_uuid> "<row-id>-<target-id>" \
  | tee raya/testcases/runs/<run-id>/<row-id>-<target-id>-<n>.log
```

- `<args.json>` is the bot's `agent_args`: a fixture from `raya/testcases/args/` or copied from a known
  good call (`raya_call.py`). Check job ids with `scripts/validate_fixture_ids.py <args.json>` first.
- **Always label the call** with the row id and target id: it is what ties the call to the case.
- **The printed dump is lossy** (turns cut at 600 characters, tool results included; no `agent_args`).
  Grade from the full call JSON: `GET /api/call/{uuid}` or `raya_call.py <bot_uuid> 3`, saved
  unmodified as `raya/testcases/runs/<run-id>/<call_uuid>.json`.
- **Before starting ANY call, including a retry, wait until the bot has no `Pending` call** and no other
  wave is using the tester (→ Platform reality 6, 7).

### Inbound bots

**Inbound bots are testable** (corrected 2026-09-02). PATCH the inbound agent with `{"out_did": <number>}`
(an **integer**: a string returns 400 `expected number, received string`), then run exactly as above with
the inbound agent as `<bot_uuid>` and the tester DID as the number. Without an `out_did` the POST 500s.
Already set: `kkb-hi-in-signals` 911204404274, `kkb-kn-in-signals` 918037006352, `maya-hi-in-signals`
911204413383 (each its own `in_did`); check the others with `whoami`. **The inbound bot looks up the
caller's number**, so inbound test data goes on the tester's number. `raya_testrun.py` also supports the
reverse direction (the tester dials the bot's `in_did`: pass the tester's uuid as `<bot_uuid>` and the
bot's DID as the number; the tester then needs an `out_did`).

## Memory test

For a bot that should remember callers between calls (`memory_enabled` on the agent). One script does
it: `scripts/raya_memory_test.py`.

```bash
python3 scripts/raya_memory_test.py check <bot>                     # is memory wired up? fix any FAIL first
python3 scripts/raya_memory_test.py run <bot> --fact name=Aisha --fact area=Malpe \
    --reask name="your name" [--direction in] [--gap 180]          # call 1, wait, call 2, grade
python3 scripts/raya_memory_test.py grade <call1> <call2> --fact name=Aisha --reask name="your name"
python3 scripts/raya_memory_test.py platform                         # is Raya carrying memory at all?
```

- **`check`** looks for the three things memory needs: memory switched on, a memory writer prompt, and
  the injection block word for word in the conversation prompt. Any FAIL means the test cannot pass;
  fix it before calling.
- **`run`** writes two personas from the `--fact`s: call 1 gives every detail; call 2 says "I called a
  little while ago", never volunteers a detail, and ends by asking "do you remember what I told you
  last time?". Between the calls it waits `--gap` seconds for the memory to be written. It saves the
  tester's persona and language and puts them back afterwards, and refuses to start while the tester
  line is in use (`--force` to override).
- **The grade, per detail:** REMEMBERED (the bot used it before the caller repeated it), FORGOTTEN
  (asked for it again, matched by `--reask`), MIXED, NOT USED, or INVALID (the caller never gave it in
  call 1, so the test proves nothing). PASS only when every detail is REMEMBERED. The report quotes the
  bot's answer to "do you remember?", which is the plainest evidence for a non-specialist.
- **`--direction in`** is a real inbound call: the tester dials the bot's `in_did`, so the bot needs an
  inbound number (`check --direction in` says so). Keep both calls in the same direction.
- **When a bot forgets, run `platform` before touching the bot.** It calls the memory probe, an agent
  that reads its own stored memory aloud word for word (`reference/memory-probe/`, uuid in
  `raya/memory-probe.json`; another account makes its own with `probe-create --like <bot>`). If call 2
  of the probe also says "Nothing stored", Raya is not keeping memory on this account: that is a
  platform report with the probe's call ids, not a prompt fix. On 2026-10-28 it failed on the EkStep
  account (probe calls `bd332b65`, `63ce32c9`, `51359f4b`, `8d872d33`; with and without a call report
  prompt, so that is not the cause). On 29 Oct a `contact_memory` value sent with the call reached the
  bot unchanged (`ad458bb1`): with memory on, Raya used to replace it with the stored memory, so the
  memory switch was behaving as if it were off.
- **The stored memory cannot be read through the API** (no endpoint; the console's memories page is
  the only direct view). The probe and the "do you remember?" answer are the evidence.
- **Use the tester's number only, never a real caller's.**

## Run a test sheet

("run these test cases, N calls each, and update the sheet")

No sheet yet? `/generate-test-cases` builds one for the bot first. To keep going unattended until every
row passes, use `/goal` as described in `/bug-fix` → "Fix until the sheet passes".

1. **Read it through the service account, never a browser:**
   `python3 scripts/testcase_sheet.py pull --sheet-id <ID> --tab "<tab>" --out <scratch>.json`. A 403
   means it is not shared with `kkb-sheets-writer@operation-rozgar.iam.gserviceaccount.com`: ask the
   owner to add it as an editor (one line).
2. **Lint it** (`testcase_sheet.py lint <scratch>.json`). A row with lint errors (no quoted expected
   line, vague pass criteria) cannot be graded mechanically: list those rows for the user and record them
   `NOT TESTED` with the reason, rather than guessing.
3. **Plan before the first call**: rows × N × variants at about 10 to 14 calls per hour per tester.
   Say the number and the time. Order: Smoke rows first; if a Smoke row fails, stop and report (the rest
   would be noise). Order the rest by what each call writes (Fixtures 4).
4. **Run every row N times** (default **3** for any row whose behaviour branches; one call is not a
   result for a branching row). Each call is one `raya_testrun.py` run labelled with the row id.
5. **Write each result to its own row, found by its `#` id, never by row number:**
   `testcase_sheet.py result --sheet-id <ID> --tab "<tab>" --id DK-07 --verdict FAIL --actual "<what
   happened, quoting the bot's line>" --calls "3 calls: 2 pass, 1 fail (<id>, <id>, <id>)"`.
   Actual Response is plain: verdict, call count, call ids, and the one line that decided it ("FAIL
   (8c546b11). The bot ran the whole interview after an empty profile, then …").
   Verdicts the sheet accepts: PASS · FAIL · PARTIAL (some of the N calls passed: also an unresolved
   result, Report contract 4) · BLOCKED (the harness cannot reach it; say what would) · NOT TESTED.
   Grader states map as: `VOID` / `INPUT-INVALID` / `NOT_EXERCISED` → re-run, or NOT TESTED with the
   reason in notes; never PASS or FAIL. A call that never connected is not a result: re-dial.
6. **Never overwrite a person's verdict.** `result` replaces Actual Response and Verdict (it prints the
   previous values). If `pull` shows a row already carries a human tester's verdict, do not call
   `result` on it; tell the user and ask, and put your finding in your report instead.
7. **A bug the sheet did not have becomes a new row**: `testcase_sheet.py add-bug --sheet-id <ID>
   --tab "<tab>" --after-phase "<phase>" --scenario … --tester-says … --expected … --language …
   --direction … --priority P0|P1|P2 [--type …] [--actual … --verdict FAIL --notes "<call id>"]`. The
   row must itself pass lint (the script refuses otherwise), so it is re-run next time.
8. **Report** in the house format and link the sheet.

## Platform reality

Respect these or waste calls; check this list before calling anything a bot bug.

1. **Trigger:** `POST /api/call` with `agent_id` = the bot under test, `to_number` = the tester's
   **10-digit** DID (`country_code` 91 is added), `agent_args` = the bot's inputs. For an outbound bot,
   **omit `out_did`** (passing it gave `Unanswered`). Inbound: see above.
2. **Rate limit:** about 1 call creation per 13 s, then 429 with `retry_after`.
3. **Bridging fails often** (`Failure` / `Unanswered`, 0 s, no transcript). It is mostly contention on
   the tester line: bridge rate rises from about 27% when redialled within 30 s to about 62% after 10
   idle minutes. The runner waits 90 s between tries. A burst of rapid calls makes it worse.
4. **`GET /api/call/{uuid}` lags**: `Pending` / 0 s for a while. Keep polling.
5. **`call_output` lags further than the transcript.** Read it only once the field you need exists; a
   consumer that falls back to a pre-call input writes stale data (`6c12ef52`).
6. **Stopping your runner does not stop the call.** A new test would share the tester (its persona
   PATCHed mid-call) and both calls write the same record (`9c0aeb63` overlapping `9a6c87b4`).
7. **One tester holds one persona at a time.** Parallel calls do bridge, but only for the SAME scenario.
   Different scenarios in parallel need one tester agent each (own DID, own persona): K testers turn N
   calls into about N/K wall-clock. **Never overlap two test waves on one tester.** Default: sequential.
8. **The tester receives no `agent_args`.** Choose the scenario by PATCHing the persona.
9. **Judge whether a call happened by its transcript turns, never by `call_duration`**: a 300 s,
   56-turn call read `Completed`, 0 s (`b989416d`) and was nearly retried into an overlap.
10. **The leading `[user] hello`** in a transcript is a platform seed turn, not the caller.
11. **Payloads have arrived truncated at exactly 1023 characters** from the campaign layer (D42). Check
    the delivered args before blaming the bot.
12. **Target ids are instance-scoped**: a stale job id returns not-found and looks like a bot bug.
13. **macOS file names are case-insensitive**: `PHONE.log` and `phone.log` are one file. Never tell two
    files apart by case.

### Harness traps that look like bot bugs

Each was nearly reported as a bot bug by a team using the tuner (Purple Dots, Oct 2026).

| What you see | What it usually is | What to do |
|---|---|---|
| Call "failed" at 0 seconds, no transcript | the line never connected | re-dial; never score it |
| Inbound bot greets the wrong name and hangs up | the inbound bot looks up the **caller's own number**; the test profile was on another number | prepare inbound test data on the tester's number |
| Setup "succeeded" but the case exits for the wrong reason | the backend refused the setup (e.g. an under-18 profile) and the setup script hid it | setup scripts stop on any backend refusal; read the response |
| Empty call report / `call_output` nulls | it arrives after the call ends | poll until the field exists |
| Grader missed a native word | the bot used the English loanword (wheelchair vs its native word) | match through `variants()` (Script-aware matching) |
| A call reached the wrong bot, two agents talk past each other | the DID was rebound to another agent | `whoami`; the runner's preflight blocks this |
| Fluent call, caller told "saved", no tool calls at all | not a harness trap: the prompt is past this bot's size limit (D116) | `scripts/prompt_size.py check --target <id> <file>`; record the size evidence |

## Fixtures: what the bot will find

0. **A real user's number and profile are READ-ONLY. Always.** No calls, no apply, no update, no
   "diagnostic" that turns out to write. A probe of which jobs were still free on a QA tester's own
   number applied her profile to three jobs, because the API answers that only by attempting an apply.
   If a question can only be answered by a write, read it from past `call_output` or reproduce it on a
   test number. Setup scripts never run against a real person's number.
1. **Which record the bot looks up.** With no `contact_phone` in `agent_args`, the bot looks up the
   dialled number (outbound: the tester DID; inbound: the caller, i.e. the tester). **A `contact_phone`
   sent in `agent_args` DOES reach the model** (`e0e7bbc2`: the args carried `918888888888`, `get_profile`
   was called with it, the call was dialled to the tester). So any profile state can be built:
   1. **Pick the instance the bot reads**, from its OWN live `get_profile` `api_details.url` (e.g. the
      Hindi slim reads `gzb-signals`, the Kannada slim `dharwad-signals`). A fixture on another host is
      invisible and looks like a fetch failure.
   2. **Pick a number that cannot be a real person**: the `9188888888xx` block.
   3. **POST the state** to `/api/v1/admin/participant` with that `phone_number`: *new caller* = post
      nothing · *draft / unconsented* = omit `compliance` · *terms only* = `compliance` with `user_terms`
      + `user_privacy` (together, else `400 USER_LEVEL_INCOMPLETE`) · *live and complete* = all three
      true plus a top-level integer `age` · *a missing field* = post without it. Consent is
      write-once-true (`false` returns `400 CONSENT_DECLINED`), so build the state up front.
   4. **Point the call at it**: `contact_phone` (and a matching `contact_name`) in the args, dial the
      tester as usual, and check the transcript shows `get_profile` called with your number. If it shows
      the DID, stop: everything after is testing the wrong record.
   Never assert anything about the caller's own number from such a call (the telephony leg is still the
   tester). **Assert the outcome on the backend too**: re-read the record after the call ("one seeker
   item, now `live`, consent true" catches a duplicate profile the transcript cannot show).
2. **`contact_memory` sent in `agent_args` does NOT reach the model**; the platform substitutes its own
   stored memory (`c2ffe9fb`: fixture facts never voiced). Never express a memory precondition
   (returning caller, `jobs_applied`, a stored landmark) as an args fixture: that case is
   `fixture_blocked`, and a FAIL on it reports a fiction. The stored memory cannot be read either (no
   endpoint). What is left: build the state through a real first call and observe a second (inference,
   say so), and assert extractions on `call_output`. On a bot you have not checked, run the
   discriminator first: put facts in the fixture that memory cannot hold and see whether they are voiced.
3. **Which record the bot picks is not `items[0]`.** Determine it empirically (one throwaway call, read
   the `profile_id` from its tool arguments) and pin the precondition to that id; record it on the case.
4. **Order a wave by what each call writes**: no-record cases first (one-shot: Signals has no delete
   route), then draft, then live, then cases that overwrite fields, then action cases (each record and
   job pair can be actioned once; a repeat returns the limit error). Refuse to fire a no-record case when
   the pre-state already shows a live record.
5. **Snapshot the record before and after every call** (read it out of band, not through a call) and
   store the delta: drift produces both false FAILs and false PASSes (a field skipped because an earlier
   test wrote it looks like correct "don't re-ask"). A pre-state that does not match the case's declared
   precondition makes every verdict in it `VOID (fixture-contaminated)`, naming the field.
6. **Persona lock**: note the persona at fire time and re-read the tester's instructions at the end. A
   change mid-call makes the case `VOID`, reported, not silently retried.
7. **Unreachable preconditions are declared**, not dropped: `fixture_blocked: <reason>` plus the
   substitute route (a production detector, a human call, a platform ask), listed in the report.

## Grader contract (mandatory)

A grade produced without this contract is void.

1. **Assertion form.** Every checklist item and case is a record with a stable id:
   `{ id, scope: universal|bot|scenario, source: transcript|tool_args|tool_result|call_output|agent_args,
   matcher, pass_condition, FAIL_SIGNAL, scope_turns, compare, evidence_required }`. The FAIL_SIGNAL is the
   literal thing that proves failure (a token, a count, a missing key), not the inverse of the pass rule.
   An item that cannot be written this way is an **observation**: reported as commentary under the
   checklist's `## Observations (not graded)`, never PASS or FAIL. Mechanise what can be: "two questions
   in one turn" = counted question markers with the mandated tag forms allow-listed; "off-topic derail" =
   N consecutive bot turns with no token from the current step's line set; "verbatim repeat" = normalised
   equality count with legitimate re-prompts listed.
2. **Five verdict states**: `PASS` · `FAIL` · `NOT_EXERCISED` (the call never reached the state; a PASS
   whose evidence is "nothing found" IS this) · `VOID` (contaminated fixture, persona changed mid-call,
   deployed prompt differs from the graded one) · `INPUT-INVALID` (the inputs failed the pre-checks; the
   bot is not at fault). A universal invariant is PASS, FAIL or VOID, never NOT_EXERCISED.
3. **No locator, no verdict.** Every verdict carries `{call_uuid, turn_index, exact_substring}` or
   `{call_uuid, tool_call_index, tool_name, arg_path, arg_value}`.
4. **Normalise before matching** (Script-aware matching).
5. **Results are files.** Per run, `raya/testcases/runs/<run-id>/` holds each call's full JSON and the
   runner log; where a manifest exists, write `status.<target-id>` per case back into it (`result`,
   `last_run`, `call_uuid`, `evidence`). The deployed prompt must be the one graded: check with
   `python3 scripts/raya_deploy.py diff <target>` (or `/raya-reconcile`) before the wave; a run graded
   against a different prompt is `VOID`.

## Universal invariants: asserted on EVERY completed call

Section-scoped checking is how a missing closing offer survived on apply calls and a doubled question
on a gathering call. These run on every call, from the machine-readable record:

1. Turn 1 is the mandated opener alone (the audio check for outbound bots); the platform's leading
   `[user] hello` is ignored.
2. The recording / AI disclosure is present, **in its mandated position**.
3. No `${...}`, `{`, `}`, JSON fragment, field name, tool name, bracketed slot or UUID in any spoken turn.
4. No digits, `₹`, AM/PM, or a `/` spoken as "slash" in any spoken turn.
5. Spoken script matches the call's language; no Latin-script rule prose in speech (allow-listed
   loanwords excepted).
6. No banned machinery token **within its declared scope** (masked per Required boilerplate).
7. The read/lookup tool fires exactly once, before any personal detail is spoken.
8. Every phone-bearing arg has a single country prefix in the shape that backend needs; never doubled.
9. Every tool arg value is Latin script; no Indic script in any payload.
10. Every enum-typed arg holds a literal from the live enum set, byte-exact.
11. A create and its dependent action are never in the same turn; the dependent action's identifier is
    non-empty and correctly formatted.
12. Every identifier arg matches its format (e.g. 8-4-4-4-12 with all four hyphens) **and** exists in the
    delivered inventory (or the prompt's own inventory for bots that carry one). Resolve the bot family
    first (D46).
13. No spoken success claim without a matching successful tool result in the same or an earlier turn.
14. No profile value (`location`, `role`, `age`) written that the caller did not say aloud (script-aware;
    a third party's city is never the caller's).
15. Every mandated say-once line occurs exactly once (normalised equality).
16. The mandated closing offer is present on an engaged call and absent on do-not-call / never-engaged.
17. Every mandated pre-goodbye step happens before the closing turn; goodbye is last and once.
18. `call_output` end / drop reason matches the transcript's ending.
19. Every `call_output` field the output prompt declares is filled or explicitly `NA`; none is filled from
    an input the caller never spoke.
20. `agent_args` sanity: valid JSON, **not exactly 1023 characters**, no phantom args, no sentinel passed
    through as a real value.
21. The deployed prompt is the one being graded.
22. The record's before and after state is recorded (Fixtures 5).

**Per-scenario assertions** are the only ones allowed to be `NOT_EXERCISED`: the branch taken, the tool
error provisioned, the line under test, the reproduction. They carry the case's FAIL signal.

## Script-aware matching

The transcript is in-script, payloads and args are Latin, and prompts use both spellings of borrowed
words. Bare substring search fails both ways: it misses a Latin-spelled mandated line (a defect stays
hidden) and finds nothing when comparing Latin args to in-script speech (bogus CRITICALs, D46/D49).

1. **`norm(s)`**: NFC; strip nuqta variants (गाज़ियाबाद ≡ गाजियाबाद); collapse whitespace, ZWJ/ZWNJ;
   casefold Latin.
2. **`variants(term)`**: native-script form, Latin form, and the common Latin-in-native borrowing
   (`option ⇄ ऑप्शन`, `profile ⇄ प्रोफाइल`). A match on any variant is a match. The table today lives
   in `raya/regression/location_integrity.py` (`TRANSLIT` / `spoken_forms()`).
3. **Cross-script comparisons are typed** (`compare: cross_script`). Zero matches on both sides is
   `INCONCLUSIVE`, never FAIL: it is the signature of a broken matcher, not of a silent bot.
4. A cross-script FAIL prints both the normalised needle and the haystack window.

## Required boilerplate: scoped prohibitions

Prohibitions are scoped ("never say X *in these lines*"), and the required and the forbidden often share
a token (the mandatory disclosure contains `रिकॉर्ड`, banned in acknowledgement lines). Graded globally,
a scoped rule fails a correct bot.

1. Every prohibition carries `scope_turns`: `intro_turn`, `acknowledgement_lines`, `failure_turn`,
   `phase2_turns`, `whole_call`. **There is no default `whole_call`**; an unscoped prohibition does not run.
2. **Mask the required lines first** (disclosure, audio check, consent line, closing offer, read-back,
   from `raya/testcases/<bot-id>/required-lines.json` when it exists, else from the prompt), then
   evaluate prohibitions on the masked text only.

## Provenance: call ids are read, never inferred

Pairing a case to a call by position or recency is banned: under retries it attributes evidence to the
wrong case, undetectably, and then nobody can say which call changed the record.

1. **Take the uuid from the run itself.** The runner prints it on the `POST /api/call -> 200 {"uuid": …}`
   line and again on the `BOT <uuid>` line. Keep each run's output (`tee` as in Run one call) and record
   `{run_id, row/case id, persona file, args file, target, call_uuid, connect_attempt}` per call.
   (The runner does not write a run log itself yet.)
2. **Never** fetch `?agent_id=…&limit=N` and pair by position or time.
3. **The tester leg by identity**: the runner shows the tester's latest call (`limit=1`), which is wrong
   when calls overlap. Match by start time inside this call's window and duration; mark it uncertain when
   more than one matches.
4. **Keep the full call object** per case, unmodified, and grade from it.

## Input pre-checks: before behaviour is graded

Failing these makes the call `INPUT-INVALID`, not a bot FAIL: "the prompt is fine, the inputs were
wrong", computed instead of argued.

- The inventory / recommendations arg parses as JSON and is not exactly 1023 characters long.
- Every identifier in it resolves on this variant's instance.
- No phantom args; no sentinel (`"Any"`, `"NA"`, `"Not Available"`, an unsubstituted `${…}`) where a
  real value belongs. If one is there, the assertion becomes "the bot did not speak it".
- Assertions that depend on platform-injected, unreadable inputs (`contact_memory`) are marked
  `UNGRADEABLE: input not observable` in the checklist, so they stop looking like passing checks.

## Where each assertion is graded

| `graded_by` | When | How |
|---|---|---|
| `harness` | reachable by a tester call | this skill |
| `static` | provable from the prompt or tool schema | `static_regression.py`, the `/generate-test-cases` static audit; runs first, zero calls |
| `production_detector` | precondition unreachable on the harness | a `raya/regression/` script over real calls (`run_runtime_checks.sh` runs them all; `--since`, exit 1 on violation, prints call uuid + line) |
| `human_call` | untestable by a TTS tester (garbled speech) | a person dials; say who and when |

**A blocked assertion with no route is an open gap with its own id, reported, never omitted.** Runtime
detectors do not run in the daily job yet (`raya/regression/README.md`): run them by hand after a
behaviour change and cite them next to the harness rows (`graded_by`, last run, violations).

## Grade a call: the walk

1. Resolve the call uuid from the run output for this row. Fetch and save the full JSON.
2. Deployed prompt == graded prompt, persona unchanged → else `VOID`.
3. Input pre-checks → else `INPUT-INVALID`.
4. Record before/after state and the precondition match → else `VOID (fixture-contaminated)`.
5. Mask the required lines; run the 22 universal invariants (`grade_call.py <uuid>` covers many of
   them mechanically; its SKIP is not PASS).
6. Run the row's or case's own pass rule and FAIL signal.
7. Run the checklist items by id: `reference/checklists/generic.md` (every bot) and the bot's own
   (`reference/checklists/<bot-slug>.md`), each with its scope and compare type. Items cite the bug
   pattern they guard (`cf. D40`) so a FAIL routes to a known fix direction.
8. Write the result (sheet row and/or manifest status), then the report.

## Report contract

1. **One row per fix, never per deploy**: `fix · state · call_uuid · the exact line or arg · variant`,
   `state` ∈ CONFIRMED · FAILED · VOID · NOT_EXERCISED · FIXTURE-BLOCKED · DEPLOYED, NOT VERIFIED. With no
   call id the only words allowed are **DEPLOYED, NOT VERIFIED** or **VERIFY-PENDING**; "fixed", "working",
   "done", "confirmed", "resolved" are forbidden there. The same words go in the changelog and the commit.
   Several fixes shipped together need a call id each.
2. **Evidence is the line**, quoted with its turn, or `arg_path=value`. Never a paraphrase.
3. **Every variant gets its own row**: each language, inbound and outbound, each bot. A variant with no
   call of its own is VERIFY-PENDING, never inherited from its twin.
4. **Branching behaviour needs N ≥ 3** calls, same persona, same args, same precondition. `k/N`:
   all pass → CONFIRMED; none → FAILED; anything between is **not a result**: report
   `UNRESOLVED` and diagnose before any remedy, as root `CLAUDE.md` → "FIRST localize the cause"
   requires: count how often the right branch was ever taken (0/N is unreachability), split by input
   (a clean split is a condition, not adherence), read the guard. Only then the remedy ladder, and never
   a third wording of a rule that failed twice. "Intermittent" with no diagnosis recorded is a contract
   violation.
5. **`NOT_EXERCISED` is always printed** with its count. A run with untested assertions is reported as
   partial, with the ids listed, never green.
6. **Plain words** (root `CLAUDE.md` → "Write for someone who is not a prompt engineer"): the words of
   the call, the sheet row and call id they can open, the few prompt lines that changed. Reproduce
   before reporting: a report made only of "maybe" causes is not finished. End with what is still open
   from before and the next step as a sentence they could type.

## From a finding to a fix

- **No fix without a transcript.** A static or analyser finding opens an item; only a call closes it.
- Check the inputs and the backend before the prompt: wrong args, a 4xx with a well-formed id, a stale
  job id are not prompt bugs. Say "the prompt is fine, the inputs were wrong" when that is what the args
  show.
- Grep the bot's wrong words against the whole prompt (D50): a hit in a sample conversation is the cause;
  the fix is an example edit.
- Route a confirmed prompt gap to `/update-prompt` (or `/port-feature` for a fix proven on a sibling);
  the full loop from a tracker is `/bug-fix`. After the fix: snapshot, deploy, re-test here (N ≥ 3 per
  variant), revert on regression.
- The three testing tiers (root `CLAUDE.md`): the fix itself, the blast radius around it (same section,
  shared logic, the mirrored languages, the payload touched), and the daily standing check. Never skip
  one, never collapse the first two into one happy-path call.

## Personas

`raya/personas/<lang>-<behaviour>.md`, indexed in `raya/personas/scenario-catalog.md`. English
instruction header, spoken lines in the call's language, and the **forcing gate** the persona drives
(two cases share a call only if their personas want the same thing at every gate). Never write a persona
that must mumble: a TTS tester either speaks clearly or goes silent; route those rows to `static` +
`human_call`. New personas come from `/generate-test-cases`.
