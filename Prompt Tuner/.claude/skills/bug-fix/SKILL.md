---
name: bug-fix
description: Work through reported bugs from the Consolidated Feedback Tracker (Google Sheet, tab "All Issues") or a bot's open-issues list, end to end on the live Raya agents. Reads what is open, grounds each issue in its real call, separates prompt bugs from input, backend and platform causes, fixes only real prompt gaps (one fix per cause), carries the fix to sibling bots that have the same bug, deploys, tests, and writes the status back. Use when the user says "process the feedback sheet", "fix the reported bugs", "go through the tracker", "what is still open on <bot>", "fix the open issues", "run the bug-fix loop", or points at the tracker or a sheet row. Locates each failure to the part of the prompt that produced it, lists what else a fix touches before editing, and finds competing rules ("which part of the prompt caused this", "what else will this change affect").
---

# Bug-fix loop

**What it produces:** every open issue for the bot(s) worked to a verdict, prompt fixes deployed for the
real prompt gaps only, the sheet (or intake issue list) updated row by row, and one short report in the
root `CLAUDE.md` format (Fixed with call id · Failed / still open · New bugs · Next · still open from
before), written in plain words.

**Fast path:** read the open list → pull each issue's real call → **locate** the first wrong turn in the
prompt map → classify → group by cause → **impact** check → `/update-prompt` (or `/port-feature`) →
deploy → `/voice-test` each variant (re-locate the proving call) → flip the sheet status → report last.

Tools it ties together: `scripts/prompt_map.py` (which part of the prompt a turn came from, what else a
change affects, every rule about one thing), `scripts/gsheets.py` (sheet read/write), `scripts/raya_call.py` (transcripts with
tool arguments), `scripts/raya_deploy.py` (diff / pull / deploy), `/raya-reconcile`, `/update-prompt`,
`/port-feature`, `/voice-test`, `/sync-check`.

## Four habits that make the loop converge (feedback from teams using the tuner, Oct 2026)

People using the tuner saw it (a) forget issues it had reported earlier and focus only on the newest,
(b) write a long report of possible causes ("maybe the schema, maybe the data") instead of making the
one call that would decide, (c) fix issues one at a time when one change would have fixed several, and
(d) find new issues on every run, which made the first report look incomplete. Each has a fix:

1. **Keep one open-issues list per bot and re-read it every time.** The list of record is the tracker
   sheet when the bot has one, otherwise the issue table in `raya/intake/<bot-id>.md` (ids
   `<bot-key>-i<NN>`). At the **start** of any fixing or testing session, read it and say how many are
   open. At the **end**, update every issue you touched: status, the call id that proves it, the date.
   A report never ends without a "still open from before" line, even if the user only asked about the
   newest issue.
2. **Reproduce before you report.** When the cause is unclear, do not write up the candidate causes.
   Design and place the one call that tells them apart (the input that differs between "schema" and
   "data"), then report the cause it shows. A report whose findings are all "may be" is not finished.
3. **Get the whole list first, then group by cause before fixing.** Run the bot's full Smoke + Core set
   once (a baseline sweep) before the first fix, so the issue list is as complete as it can be up front.
   Then group the issues by root cause: several symptoms often share one rule, one example or one tool
   description. Make **one** fix per cause, and say which issues it is expected to close. Each of those
   issues still needs its own proving call (root `CLAUDE.md`: one call id per fix).
4. **Expect some new issues after each fix, and say why.** A change can break something nearby (Tier 2
   exists for this), and some defects only show on paths the earlier calls never reached. Say which new
   issues are regressions caused by the last change and which are first sightings of an old defect, so
   the person can tell progress from churn.
5. **When the same issue survives two fixes, read the whole prompt cold before the third.** A fresh
   subagent with no history (`/prompt-analyser` step 0) plus `scripts/prompt_structure.py`. A session that
   has been fixing for hours reads the prompt through its own theory of the bug; on Orange Dots that
   meant hours of added rules, while a fresh read found the step numbering was sending the bot to the
   wrong question (D125).

## The prompt map: which part is wrong, what else it touches, how to resolve it

A prompt is treated as a structure, not a wall of text: its sections are the nodes, step references and
shared values are the links. The map is **built from the prompt file every time** by
`scripts/prompt_map.py`, never kept as a second copy: a structure maintained beside the prompt drifts
from it (an MSR 2025 study of 1,262 real prompt changes found most edits undocumented and some
introducing contradictions; our own stale step references, D125, are that drift). The method borrows four
well-tested ideas: prompts as programs made of components (Microsoft SAMMO, POML), a call as a walk through
a graph of steps (Pipecat Flows, Retell), impact analysis by following what writes and what reads each
value (program slicing), and ranking suspects by failing versus passing runs (spectrum-based fault
localisation). Use it at four moments:

**A. Which part produced the failure (root cause, step 2).**
`python3 scripts/prompt_map.py locate <prompt> --call <uuid or saved call.json>` lists every bot turn and
tool call with the section it came from. Find the **first** turn that went wrong: later turns are often
its consequences (error-analysis practice: code the first failure in each trace). What the first wrong
turn tells you:
- it matches a rule section, said at the right moment, with the wrong content → a problem **inside that
  step** (its instructions);
- it matches the right line at the wrong moment, or a step was skipped or repeated → a problem **between
  steps**: the transition, the guard on the step (D1-D3, read the guard), or a step reference that lands
  in the wrong place (`scripts/prompt_structure.py`, D125);
- it matches a line in an **example** → the example taught it (D50): fix the example, not the rule;
- **no prompt line is close** → the bot improvised: a branch the prompt never covers, or a rule it never
  reached. Look for the missing branch before adding words;
- a tool fired, or did not, against its section's contract → read that tool's section and its live schema.
A turn can also be placed alone: `locate <prompt> --say "<what the bot said>"`.

**B. Group by cause (habit 3).** Locate the first wrong turn of every failing call in the batch and group
the issues by the section (or the value) they land on: several symptoms at one section are one cause and
get one fix. With ten or more calls of the same bot, some passing and some failing,
`prompt_map.py spectrum <prompt> --calls <dir> --fail <uuid prefixes>` ranks the sections that go most
with the failures. It is a ranking, not a verdict: a section that runs on every call scores low even when
it is the culprit, so always confirm with `locate` on the failing calls. (Checked on 32 saved KKB Slim
Hindi calls: the 5 calls that repeated a line traced, with `locate`, to step 8, step 10 and Turn B;
`spectrum` ranked step 8 first and Turn B third, and missed step 10, whose line also runs in passing calls.)

**C. What else the fix touches (before editing, and the Tier 2 list).**
`python3 scripts/prompt_map.py impact <prompt> --section "<title words or line number>" [--sheet <rows.json>]`
lists the rules elsewhere that point at that part (they break if it is renamed, renumbered or moved), the
values it writes and which steps read them, the values it depends on and which steps write them (a wrong
value often starts upstream), the tools it uses, the same part in every other language, and, given a
pulled test sheet (`scripts/testcase_sheet.py pull`), the rows to re-run. That list **is** the
blast-radius plan for Tier 2; paste it into the report. If it says a value is both checked and written in
the same part, read the guard first (root `CLAUDE.md`, D3).

**D. Is there already a rule about this (before adding one).**
`python3 scripts/prompt_map.py rules-about <prompt> <tool | ${variable} | field | phrase>` prints every
line about it, grouped by section, and flags directions and prohibitions that sit in different places.
Models do not reliably resolve two rules that can both be followed (instruction-hierarchy studies,
2025), so a fix usually **scopes, merges or deletes** an existing rule rather than adding a new one
(ladder rungs 2-3).

**After the fix:** run `locate` on the proving call. The report quotes the turn and names the section it
now comes from: that is the evidence the fix landed where intended, next to the call id.

## Fix until the sheet passes (`/goal`)

When the user wants the loop to keep going on its own ("keep fixing until every case passes"), use
Claude Code's built-in **`/goal`**. After each turn a small model checks the condition against what
Claude has printed, and Claude keeps taking turns until it is met, judged impossible, or stalled. It
cannot read files or run commands itself, and it does not start subagents, so:

- Write the condition so it can be proven from printed output, and make each turn end by printing the
  results table (row id, verdict, call ids). Example:
  `/goal every Smoke and P0 row in the "<tab>" tab of <sheet link> shows PASS on 3 of 3 calls in the
  results table you print, and the sheet is updated; or stop after 25 turns`.
- Always include a stop ("or stop after N turns"), and run it in auto mode or with the needed tools
  allowed, or it waits on permission prompts.
- The loop still obeys everything here: a transcript before every fix, one fix per cause, a cold read
  after two failed fixes on one issue, never a third wording, escalation after the ladder, every variant
  tested, and "fixed" only with a call id. A goal that can only be met by breaking a rule is reported as
  blocked, not met.

## The two non-negotiable rules

- **No fix without a transcript.** Never edit a prompt off a sheet report, a hunch, or a static/analyser
  finding alone. Pull the actual call, read the offending turns, confirm the bug is real and understand
  its cause first. A plausible static gap that no transcript reproduces is an ungrounded change (r70,
  2026-07-27: a static "gap" 40 calls never reproduced). If no recent call reproduces it, do not fix:
  ask the reporter for the call uuid and time, or place a repro call with `/voice-test`.
- **"Fixed for UAT" is not "confirmed".** `Fixed for UAT` means deployed and ready for the user's
  acceptance test. Only a **post-deploy** call transcript on that variant makes it confirmed; with no such
  call, say DEPLOYED, NOT VERIFIED.

## The sequence (in order; the summary is always last)

0. **Read the open list** (habit 1) and, before the first fix, run the baseline sweep (habit 3).
1. **Find**: pull every row with status `Open` or `Accepted to Fix` for the bot(s) in scope. Temporal-check
   each against the bot's `CHANGELOG.md`: if a fix for it shipped after the report date, mark it
   `Fixed for UAT` with the changelog date and make no change.
2. **Root-cause with the real call** (step details below). For any "it does this sometimes" report, run
   **D1-D3** from root `CLAUDE.md` ("FIRST localize the cause") before choosing a fix: **count** how often
   the right branch was ever taken; **split** the calls by each injected variable's value and shape,
   tool-result shape, earlier branch, language and direction (a near-clean split is a condition bug, not
   adherence); and **read the guard** of any skipped step, because it may have been correctly skipped
   under a too-generous condition. On 2026-09-23 a remedy applied before this split cost two failed
   fixes, one a regression. Place the first wrong turn in the prompt with `prompt_map.py locate`
   (prompt map, A).
3. **Classify** (table below). Only *prompt gap* gets a prompt edit.
4. **Group by cause** (habit 3, prompt map B), check what the fix touches (`impact`, prompt map C) and
   what rules already exist (`rules-about`, prompt map D), then **fix** each cause once via `/update-prompt`: reconcile with live
   first, snapshot, surgical edit on the master, mirrors brought up, `CHANGELOG.md` entry, and a new or
   sharpened `bug-patterns.md` entry.
5. **Propagate**: check each sibling for the SAME gap and port it only where present (step details).
6. **Verify nothing broke** before deploying (step details).
7. **Deploy** each changed target with `scripts/raya_deploy.py deploy <target>`.
8. **Test** each changed variant (Tier 1 and Tier 2) with `/voice-test`; Tier 2 covers what `impact`
   listed. Re-run `locate` on the proving call. The daily standing check is Tier 3.
9. **Write the sheet status** for every row touched (status discipline below).
10. **Repeat** until every open row has a verdict.
11. **Report last**, in the root `CLAUDE.md` format. Never write the summary before the work is done;
    write it to a file only if the user asks for one.

## Prerequisites

- `raya/.env`: `RAYA_BASE_URL`, `RAYA_API_TOKEN` (git-ignored).
- Google service-account key. `scripts/gsheets.py` looks in `$GOOGLE_SA_KEY` → `secrets/gsheets-sa.json`
  → `$GOOGLE_APPLICATION_CREDENTIALS` → `~/Downloads/service-account.json`. The service account
  `kkb-sheets-writer@operation-rozgar.iam.gserviceaccount.com` has edit access.
  - If `~/Downloads` is blocked (macOS privacy prompt after an app restart), the same key is
    base64-encoded in `kaam-ki-baat/.env.local` as `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64`. Decode it into
    `secrets/gsheets-sa.json` (git-ignored) by piping base64 to the file; never print the key.
- Tracker: id `1cqT9EVk_vap16wJ3fQM7txLklf-kbMDHdYWsiHImbHU`, tab **`All Issues`** (the old "Doc 1
  Issues" tab is gone).
  ```bash
  python3 scripts/gsheets.py --sheet-id 1cqT9EVk_vap16wJ3fQM7txLklf-kbMDHdYWsiHImbHU get "'All Issues'!A1:L400"
  python3 scripts/gsheets.py --sheet-id <id> update "'All Issues'!B<row>" '[["Fixed for UAT"]]'   # one cell, after the fix is deployed
  ```

## Sheet columns (`All Issues`)

`A DATE · B STATUS · C Bot · D Title · E Type · F Issue description · G Owner · H Priority · I ETA · J Call IDs · K Additional comments · L "Fixed, Date / call id"`.
Status values in use: `Open · Accepted to Fix · Fixed for UAT · Flagged - Backend Issue · Rejected / Not an Issue · Closed`
(older rows also say `Rejected, not an issue`). Column K carries `DPG` on rows handed to the DPG team
(`docs/DPG-asks-2026-10-13.md`).
Column J "Call IDs" are the team's own ids and usually do **not** resolve in the Raya API: find the call
by **agent uuid + date** instead.

## Sheet "Bot" label → target id

Labels as they appear in column C (checked 2026-10-14). Files and uuids come from `raya/agents.json`
(`python3 scripts/raya_deploy.py targets`), never from this table. **The agent a reported call actually
ran on wins over the label**: always confirm with the call's agent uuid.

| Sheet "Bot" | target id(s) |
|---|---|
| KKB (Ghaziabad) | `kkb-hi-out` |
| KKB Kannada, KKB (Kannada, outbound) | `kkb-kn-out` |
| KKB placeholder Inbound | `kkb-hi-in` |
| KKB Kannada Inbound | `kkb-kn-in` |
| KKB Placeholder- Hindi Signals API | `kkb-hi-signals`; since late Sept 2026 the campaign calls run on the slim agent, `kkb-hi-signals-slim` (all Oct 2026 rows) |
| KKB Placeholder- Kannada Signals API | `kkb-kn-signals` (or `kkb-kn-signals-slim`, check the call's agent) |
| KKB Signals placeholder Inbound | `kkb-hi-in-signals` (Kannada: `kkb-kn-in-signals`) |
| KKB HE (Higher-Ed = Maya) | `maya-hi-out` |
| KKB HE Inbound | `maya-hi-in` |
| KKB Maya- Signals | `maya-hi-signals` (inbound calls: `maya-hi-in-signals`) |
| DKB (Ghaziabad) | `dkb-hi-out` |
| DKB Kannada | `dkb-kn-out` |
| DKB Hindi- Signals | `dkb-hi-signals` (Kannada: `dkb-kn-signals`) |
| TRRAIN Hindi | `trrain-hi-out` (Kannada: `trrain-kn-out`) |
| Platform, Unassigned / Ops, KKB (roadmap), All bots | no single prompt: platform, ops or roadmap items; classify, do not edit |

A label not in this table (a new bot or project): match it to a `raya_name` in `raya/agents.json`, add it
here, and if the bot is not registered, hand off to `/register-bot`.

## Classify (step 3): only one class gets a prompt edit

| Class | Signal | Action → sheet status |
|---|---|---|
| **prompt gap** | the transcript shows a real gap: missing guard, wrong wording, missing step, an example that teaches the wrong thing | fix via `/update-prompt`, propagate, deploy → `Fixed for UAT` |
| **wrong inputs** | the call's `agent_args` were sent wrong: jobs in the wrong field, missing or malformed values, mis-mapped campaign args | say "the prompt is fine, the inputs were wrong"; no edit → `Rejected / Not an Issue` + comment naming the bad input (2026-07-31: jobs sent in `contact_memory`, not `${recommendations}`) |
| **backend** | a tool returns 4xx/5xx on a well-formed payload; placeholder inventory (`job_id "1"/"2"` → "Job not found") | no edit → `Flagged - Backend Issue` + what is needed |
| **adherence** | D1-D3 done, and the behaviour is still mixed within one input group, on a rule the prompt states clearly | no new wording of the same rule. Walk the remedy ladder in root `CLAUDE.md` (rungs 1-4: grep the wrong line against the prompt's examples, scope the competing rule, remove the wrong option, move it into the tool schema). Escalate to the platform only at rung 5, with both call ids → `Flagged - Backend Issue` |
| **no-repro** | not reproduced in recent calls | no edit; keep `Open` + "not reproduced in N calls; need the call uuid" |
| **verbiage** | a pure wording or tone preference, not a bug | note it and reassign (Aryan) |
| **ops** | telephony, spam labelling, account (e.g. Truecaller verification) | not a prompt; leave for Ops |

**Never add more prose to a rule the model already ignores.** The 2026-07 attempt to force `get_profile`
by calling it "silent/invisible" made the model stop calling it (regression, reverted; analyser D25).
Two failed wordings means change the mechanism, not the volume (D47, D49, D50).

## Step details

**Step 2: ground in the transcript.** Find the call by agent + date:
```
GET {BASE}/api/call?agent_id=<uuid>&limit=20   -> {calls:[{uuid, caller_no, to_number, created_at, call_duration, outcome}]}
GET {BASE}/api/call/<call_uuid>                -> {call_transcript:[…], call_output:{drop_reason,…}, agent_args}
```
Headers `X-API-Key`, `User-Agent: Mozilla/5.0`. Paginate with `&offset=N` (`limit` up to about 100).
There is no server-side phone filter: match `caller_no` for inbound callers and `to_number` for outbound
callers, client-side.

Use `python3 scripts/raya_call.py <agent_uuid> [limit] [offset]`: it prints each call's `agent_args`,
`call_output`, and every tool call with its arguments and linked result. Do not hand-roll a reader that
prints only `content`. (It reads the default Raya account only; a bot with `"account"` set in
`raya/agents.json` needs that account's token.) If the API omits a field you need, say so; do not guess.
For a batch, fan out one grounding agent per issue plus an adversarial check, and every verdict must
quote the actual tool call or result.

**Read the transcript properly: tool arguments are where payload bugs live.** Each `call_transcript`
turn has `role`, `content`, `tool_calls`, `tool_call_id`.
- An assistant turn that makes a tool call has `content: null` and `tool_calls:
  [{id, type:"function", function:{name, arguments}}]`. `function.arguments` is the exact payload the
  model sent (e.g. `apply_job {"job_id":"…","profile_id":"5051"}`).
- A tool turn (`role:"tool"`) holds the result or error in `content`, linked by `tool_call_id`. Errors
  carry `response_body_excerpt` (e.g. `{"error":"Invalid or missing profile_id"}`).
- To diagnose a tool failure, compare what was sent with what came back, field by field.
- Judge the call by its transcript turns, not `call_duration`. A 0-second call never connected: re-dial,
  do not score it (`/voice-test` → "Harness traps").

**Known payload trap (caused many apply 404s, D28):** `create_profile` returns both a numeric top-level
`id` (e.g. `5051`) and a `profileId` UUID. `apply_job`'s `profile_id` must be the `profileId` UUID.
`get_profile`'s top-level `id` already is the UUID.

**Step 4: reconcile, snapshot, fix.** Run `python3 scripts/raya_deploy.py diff <target>`. If live is
ahead (console-only edits, a real job inventory), `pull <target>` (try `--dry-run` first) and commit
before editing; if the GET is empty or unstable, use `/raya-reconcile`. Then fix via `/update-prompt`,
which snapshots (`scripts/prompt-version.sh save <agent> pre-<slug> "<why>"`), edits the master,
brings up every mirror (agnostic text byte-identical, spoken lines re-authored), keeps registered
divergences (`raya/divergences.json`) and the Maya divergences, appends `CHANGELOG.md`, and adds or
sharpens the `bug-patterns.md` entry. Show the two or three prompt lines that changed (before → after)
in the report.

**Step 5: propagate.** Siblings are the bot's other language and direction targets (outbound / inbound),
its Signals and Slim variants, and bots that share the same section (KKB → Maya). Resolve them from
`raya/agents.json`; check each for the SAME gap before porting, never assume. Same bot family: carry the
fix through `/update-prompt`. Another bot: `/port-feature`, re-fitted to that bot's variables, tools and
spoken lines. A change that touches logic Maya inherits from KKB follows the Maya flag-and-ask rule: ask
before applying it to Maya. Broad propagation of an agnostic fix to bots the user has not scoped needs the
email approval (root `CLAUDE.md`).

**Step 6: verify nothing broke (before deploy).** Does a new rule contradict an existing line, including
the prompt's own examples (2026-07-27: a new canonical-spelling rule against the file's sample-dialogue
spellings)? Did an insertion split a section or break the greeting → fork → apply → failure flow? Run
`/sync-check` so the master and every mirror still match. Where a mirror's spoken lines changed, also run
`python3 scripts/language_checks.py <master> <mirror> --lang <iso>`, and
`python3 scripts/prompt_size.py check <file> --target <id>` on every changed file (a prompt past the
bot's size limit stops calling tools with no error, D116).

**Step 7: deploy.** `scripts/raya_deploy.py deploy <target>` is name-guarded, snapshots, refuses
placeholder `job_id`s and oversize prompts, verifies the saved prompt against the update response, and
records to `raya/deploy-history.md`. `--yes` only after the user has approved the push. Never deploy by
editing the agent in the Raya console. Afterwards confirm every changed target is `in sync`
(`raya_deploy.py status <target>`).

**Step 8: test.** A deploy proves the prompt shipped, never that the bot behaves (root `CLAUDE.md` →
"The three testing tiers"). With `/voice-test`, on **every changed variant separately** (each language,
outbound AND inbound; inbound bots are testable by giving the inbound agent an integer `out_did` and
calling the tester DID):
- **Tier 1:** the exact reported failure no longer happens; name the call id and the line that proves it.
- **Tier 2:** the neighbours of the change: same section, shared logic, the mirrors, the tool payload.
- **Tier 3:** the daily standing check (`raya/regression/`).
Test on test numbers only; real users' numbers and profiles are read-only.

**Step 9: sheet status discipline (always flip the status, not only a comment).**
- deployed prompt fix → **`Fixed for UAT`** + comment: cause, call uuid, what changed, deploy date,
  "awaiting post-deploy call" until a proving call exists; column L gets the date and proving call id.
- backend, or adherence escalated at rung 5 → **`Flagged - Backend Issue`** + what is needed from LitWiz
  or the console.
- wrong inputs → **`Rejected / Not an Issue`** + the input that was wrong.
- no-repro → keep **`Open`** + "not reproduced in N calls; need the call uuid".
- verbiage → note + reassign. ops → leave.
Never leave a deployed fix marked `Open`. Never overwrite a cell someone else has filled in; add to
column K instead.

## Safety

- Work only on OPEN rows; temporal-check against `CHANGELOG.md` first.
- Every prompt change is snapshotted and surgical; mirrors stay in step; deploys are name-guarded,
  verified and recorded.
- Rollback: `scripts/prompt-version.sh restore <agent> <pre-fix-label>`, then deploy again.
- Never paste a caller's phone number into the sheet, a changelog or a report: cite the call uuid.
