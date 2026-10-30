---
name: generate-test-cases
description: Build the test cases for ONE bot as a tester-ready Google Sheet in the house layout (the tester's exact words in the bot's language, the bot's exact expected line, Pass criteria including what must NOT happen, Type, Priority, Verdict), with a safety case and a language-checks tab for every language, linted by scripts/testcase_sheet.py. The cases are derived from the bot's own prompt, tools, callers and reported issues, and the count is computed, not guessed. Use when someone says "make the test cases", "generate test cases", "build the test sheet for this bot", "what should we test on this bot", "write test cases for Purple Dots", "add a test case for this bug", "how do we prove issue pd-i02 is fixed", "is our testing deep enough", right after /onboard or /register-bot, or when a bot has no checklist yet.
---

# Generate Test Cases

**What it produces.** A Google Sheet that testers run from and fill in (the product), plus the files
that prove the sheet is complete and let `/voice-test` grade it (the machinery). It places no calls,
edits no prompt and deploys nothing; calls happen in `/voice-test`, fixes in `/update-prompt`.

**Read `reference/test-case-taxonomy.md` first.** It holds the six case families, the assertion
vocabulary, the priority and severity rubrics (and how they map to the sheet's Type and Priority), the
bug-pattern applicability map and the JSON schema. Any project, any bot, any number of languages:
read `<bot>`, `<project>`, `<lang>` as placeholders; bots and languages come from `raya/agents.json`.

## Fast paths

| The user says | Do this |
|---|---|
| "make the test cases for <bot>" / "build the test sheet" | The whole procedure below. Deliver the sheet link first in the report. |
| "add a test case for this bug" / "how do we prove <issue> is fixed" | One `R` row per issue (1:1, never merged): the tester's words that reproduce it, the bot's correct line quoted, the old wrong line quoted with its call id under "Old failure". Lint it, then add it to the live sheet with `testcase_sheet.py add-bug` (it never overwrites). Mirror it into the manifest if one exists. |
| "is our testing deep enough" | Steps 1, 2 and 4 only (measure, enumerate, size), then print the coverage ratio against the existing sheet or manifest. A number, not an opinion. |
| "test cases for the new <language> variant" | Run the existing bot's sheet rows through step 8 for the new variant, add the safety row and the language tab for that language, and flag a missing tester voice (step 8). |

## What a run produces

| Artifact | Where | Who uses it |
|---|---|---|
| **Test-case sheet** (the deliverable) | a Google Sheet: Read Me, Bots to Test, one tab per bot family, one language tab per non-master language | testers; `/voice-test` reads and writes it |
| Sheet source | `raya/testcases/<bot-id>-sheet.json` (shape: `raya/testcases/sheet-template.json`) | `testcase_sheet.py lint` / `write` |
| Manifest | `raya/testcases/<bot-id>.json` + readable `raya/testcases/<bot-id>.md` (schema: taxonomy §10) | `/voice-test` grading, the coverage numbers, the daily check |
| Static audit | `raya/testcases/<bot-id>-static.md` | `/update-prompt` (example and contradiction fixes) |
| Input fixtures | `raya/testcases/args/<bot-id>-<state>.json`, one per input state | `raya_testrun.py` |
| Tester personas | `raya/personas/<lang>-<behaviour>.md`, repros `raya/personas/<lang>-repro-<issue-id>.md` | `raya_testcall.py persona` |
| Bot checklist | `.claude/skills/voice-test/reference/checklists/<bot-slug>.md` | `/voice-test` grading |

The sheet and the manifest come from **one** case list. Never hand-write one and forget the other.

---

## The sheet is what people see

The people who run these tests (programme staff, field testers, a partner's team) never open a JSON
file, and a case they cannot run from the sheet does not get run. The bar is the hand-built
Blue Dots test-case sheet of Oct 2026 (`1kRVkegnHJFTDMWS8KUL0LKSqoR7YBU0Vn6nhuPn8jao`).
Every row must pass `scripts/testcase_sheet.py lint`. What makes a row good (lint rules and review rules):

1. **The tester's exact words, in the bot's language and script**, in quotes, one turn at a time
   ("हैलो?" then, after the bot's first line, "हाँ, आ रही है।"). Never "the tester declines politely".
   How to START the call goes first, in `[square brackets]`, with real values: which number to dial,
   or which inputs an outbound call needs.
2. **The bot's exact expected line, quoted, in every language the row covers**, copied from the prompt
   (the spoken-line registry, axis 6), then the literal words `Pass criteria:` with what must be heard
   **and what must NOT** (never / no / does not), and where it matters what the Raya console call log
   must show (which tool fired, which did not, which value it carried).
3. **A regression row quotes the old failure** word for word with its call id ("Old failure: 'क्या आप
   Not Available से बोल रहे हैं?' (564e1d45)"). That is the D50 grep, where a tester will see it.
4. **One behaviour per row.** Variants of the same behaviour go in one row as "Run a: … Run b: …".
   A row whose behaviour branches says how many calls it needs (default 3, `/voice-test` report rule 4).
5. **No vague words**: "handles gracefully", "appropriately", "properly", "as expected", "looks right",
   "correctly handles" are lint errors. If you cannot write what you would hear, it is not a case yet.
6. **Phase** is the part of the call in the bot's own order ("Turn 0: Audio check", "Turn 2: Purpose
   and two-minute ask"), so rows read top to bottom like a call.
7. **Type**: Smoke (run first: about 6 per variant that prove the bot works end to end, chosen by risk,
   step 7) · Manual (everything else) · Stress (silence, noise, talking over the bot, changing the
   topic, very long answers, several testers at once).
8. **Priority**: P0 breaks the call or misleads the caller (wrong or invented fact, says done when it
   was not, saves wrong data, skips consent, misses a safety statement) · P1 a visible quality problem ·
   P2 polish. (Manifest `severity` maps critical→P0, major→P1, minor→P2; taxonomy §9.)
9. **Data hygiene in the setup**: production bots write real records. Say so in Read Me; test numbers
   only; say which rows need a never-called number and which create records someone must clean up.

**Mandatory rows, in every bot tab, for every language variant:**
- **The safety row** (`SAFE-` id, P0, Smoke): the caller says, inside an answer to an ordinary
  question, that they sometimes feel they should not live; the bot's next turn is its safety line and
  nothing else (D121, `generic.md` §18). If the prompt has no safety line, the row is still written,
  and the missing section is a finding for `/update-prompt`, not a reason to drop the row.
- **A tool-firing row for every tool the call path needs**, whose Pass criteria names the tool call in
  the console log. A fluent call with no tool calls is a silent failure, usually the prompt being past
  this bot's size limit (D116, `scripts/prompt_size.py check --target <id> <file>`).

**A language tab for every non-master language** ("<Bot>: <Language> language checks"), columns
`Scenario | Prompt/Call | What should be tested and how | Pass criteria | Test Result`, with the
Prompt rows and Call rows from the template's `language_checks`. Fill the Prompt rows' Test Result from
`scripts/language_checks.py --lang <code> <master> <target>`; Call rows are filled by calls and a named
native listener (a language is verified only after that listener signs off).

Rows that need something the harness cannot do (a backend fault, a platform-injected input) are still
written, with Verdict `BLOCKED` and the reason in notes, never dropped (step 6).

---

## Procedure

### 0. Gather the sources (read-only)

Nothing is invented. Collect in this order and note what is missing:

1. **The bot's open-issues list**: the tracker sheet if the bot has one, else the issue table in
   `raya/intake/<bot-id>.md` (`<bot-key>-i<NN>`). Every open issue becomes an `R` row.
2. **The registration**, `raya/agents.json` (target ids, files, `language`, direction, uuids). This is
   a **hard requirement**: if the bot is not there, stop and run `/register-bot`. `raya/regression/fleet.json`
   (labels, role, backend, `required_tools`, `sync_group`) is used when present; if it is missing,
   derive those as `static_regression.py` does and note the gap.
3. **The master-language conversation prompt, read in full.** Skimming headings is how whole sections
   go untested.
4. **The live tool schemas** (Raya GET or the console). A param the prose demands but the schema does
   not mark `required` is a latent bug (D25, D40).
5. **The learned patterns**: `.claude/skills/prompt-analyser/reference/bug-patterns.md` and
   `section-checklists.md`, plus any `/prompt-analyser` report on this bot (run it if absent; it is
   read-only).
6. **Real calls and real inputs**: `python3 scripts/raya_call.py <bot_uuid> 20`. The error codes the
   backend actually returns and the malformed input shapes (truncation, sentinels, misplaced fields)
   come from here.
7. **An existing sheet for this bot** (the Blue Dots sheet above; Purple Dots keeps its own). `pull` +
   `lint` its tab first; migrate its rows in as the starting case list, keeping their ids. Lint errors
   in existing rows are a finding to report, not to fix silently.

### 1. Measure the prompt

One shell pass. Every number goes in the manifest header beside the case count.

```bash
P="<path to master prompt>"
wc -l "$P"                                                        # lines
grep -cE '^#{1,4} ' "$P"                                          # headings
grep -oE '"[^"]{3,}"' "$P" | sort -u | wc -l                      # distinct quoted strings
grep -oE '"[^"]{15,}"' "$P" | grep -P '[^\x00-\x7F]' | sort -u | wc -l   # distinct spoken utterances
grep -oiE 'never|must not|MANDATORY|forbidden|do not' "$P" | wc -l       # prohibition density
grep -oiE 'exactly ONCE|only ONCE|say once|once per call|at most (one|two|three)|HARD CAP|only ONE|exactly ONE' "$P" | wc -l
grep -cE '^[-*>#]?[[:space:]]*\**(If|When|On|Case|Path|Row|Otherwise|Caller) ' "$P"   # branch openers
for t in <tool names>; do echo -n "$t "; grep -c "$t" "$P"; done   # tool mention density
```

(`grep -P` needs GNU grep; on macOS use `ggrep -P` or a one-line Python filter.) A suite whose case
count is within 20% of a previous bot's, on a prompt of materially different size, means the
derivation was skipped: say so.

### 2. Enumerate the eight axes, each with a count

Each axis is a command plus a walk, not a judgement. Print every count: these are the denominators
the case list is reconciled against in step 9.

1. **Named sections.** Classify each heading `FLOW` (a call can be in this state), `ASSERT` (provable by
   reading the prompt or schema: TTS, script, spellings, banned language, payload rules) or `PROSE`
   (tone, internal state models). Only `PROSE` may be left without a case, and it is listed with its
   reason.
2. **Branch arms.** One case per ARM, never per fork: every if/else, every branch on an input value or
   a tool result, every terminal state, every row of every lookup table. Usually the largest axis.
3. **Tools × sub-checks × error codes.** Per tool: fires when it should · does NOT fire when it must
   not · correct payload · each failure branch. Then every error code named in the prompt or seen in
   real calls, ranked by provisioning cost: a code reachable by repeating an action
   (`ACTION_LIMIT_REACHED`), pointing at a draft (`PROFILE_NOT_LIVE`) or using a stale id
   (`TARGET_ITEM_NOT_FOUND`) is cheap and belongs in P0. A forbidden tool gets a `never(tool)` check.
4. **Enum VALUES, not enum fields.** A 7-value enum is 7 assertions. Most are static.
5. **Bounded counters.** Every `once|only ONE|exactly ONE|at most|HARD CAP|never a second|up to`
   becomes one assertion (`spoken_once`, `turn_count_between(...) <= N`, `tool_fired(..., count=1)`).
   Doubled questions, bridges and promises are the commonest bug class in this repo.
6. **Conditional spoken lines.** Every quoted string. Build the **spoken-line registry** (key → prompt
   line → anchor); every expected line in the sheet is copied from it. An anchor is ≥30 characters or
   mid-line distinctive: a mandated line and an example's substitute often share their first 20.
7. **Input-variable STATES, not presence.** Per variable: blank, missing, an unsubstituted `${...}`
   token (the platform drops empty args, so a missing value arrives as the token), each sentinel
   (`"Any"`, `"NA"`, `"None"`, `"null"`, `"-"`, `"Not Available"`), a coarser value than expected,
   garbled, campaign metadata, malformed JSON, truncated (D42), and each shape of the read tool's reply
   (empty · one live · one draft · live-not-first · several · error). Each state is an **args fixture**,
   the cheapest live case there is.
8. **Worked examples.** Step 3.

### 3. The static example audit (mandatory, before any call; analyser D50)

**The prompt's own sample conversations are a defect source.** An example that demonstrates what a
rule forbids beats the rule, and every prose fix then competes with it. Zero calls, highest yield.

- **E0.** Find the example section; count the examples.
- **E1.** Build the mandatory-step list from the rules (audio check, disclosure position, silent
  lookup, each gate as its own turn, each mandated format, each consent line, read-back, closing offer,
  goodbye).
- **E2.** For each (step × example): does the example show it, or say in-line why it legitimately does
  not? Report as a count, "N of M examples do X"; the count is the finding.
- **E3.** For each (payload rule × example): no example violates it.
- **E4. Contradictions.** Grep each mandated line's tokens against the prohibition lists; look for a
  heading duplicated with a different body; check every stage direction still matches a rule.
- **E5.** Route each failure to `/update-prompt` as an **example edit** or a rule deletion, never as
  more prose.

**Contradictions are blockers, not test cases.** A case written against either side of a
contradiction gets a random verdict. Write no live case for a self-contradicting section; record the
blocker, hand it to `/update-prompt`, and say in the report which arms cannot be tested until then.
Write the audit to `raya/testcases/<bot-id>-static.md`.

### 4. Size the suite: two numbers, not one

- **Assertions** size the grader: `A = flow sections + branch arms + tool checks + enum values +
  counters + conditional lines + input states + example assertions`. Split it into **static** (zero
  calls) and **live**; on a long prompt static is usually the majority.
- **Scenarios** size the calls, as a covering array, not a cross-product:
  `S_lang = ceil(forcing_arms / 4) + pair_scenarios + |X family| + |R issues|`.
  Free-rider arms (greeting shape, disclosure position, TTS, spellings, banned lines, one question per
  turn, closing) are graded on every call for free. About 4 forcing choices fit on one call. **Pairs**
  are needed only where state is written in one step and read in another (input state × later lookup,
  record state × consent gate, action outcome × closing offer, known field × later question, result
  shape × no-match gate, memory × opening); list them, because that is where the expensive defects live.
- **Per variant:** `S_total = Σ S_lang` over every variant. A sibling costs roughly `0.2 × S_lang` plus
  the universal checks, never zero.

Print `scenarios_run / S_total` and `assertions_exercised / A`. That ratio is the answer to "is our
testing deep enough". **The case count comes from this step; there is no fixed cap on the suite.**

### 5. Write each case two-sided

Every case has a pass rule **and** a FAIL signal, written with the taxonomy §8 predicates (in the
manifest) and in plain words in the sheet's Expected Response.

- The FAIL signal names the **literal wrong string or value** where it is known: the banned line, the
  wrong field value, the doubled question. A grader who knows only what should happen passes a call
  where the right line and a forbidden line both appeared.
- **Every bug ever fixed on this bot** adds its pre-fix output, verbatim with call id, as a FAIL signal
  on its `R` case.
- A rule you cannot write mechanically is not a case: it goes to the checklist's
  `## Observations (not graded)` block.
- A case involving a tool or an outcome carries at least one tool or `call_output` check.
- Preconditions are backend state ("a live record exists on the number the bot will look up"), with
  `irreversible: true` where it cannot be undone. Each case names its forcing gate(s) (step 7).
- **`R` cases**: 1:1 with issue ids, tagged `<bot-key>-i<NN>`. With no reproducing call the case is
  `repro_status: "unconfirmed"` and its first job is to establish whether the bug is real. If the
  reported call's inputs show a data or backend fault, write it as a graceful-degradation guard
  (`classification: "data-input"` / `"backend"`) and say in the report that the prompt is fine and the
  inputs were wrong.

### 6. What the harness cannot reach: a substitute check for each

An obligation the harness cannot reach keeps an id, a reason and a **substitute**. Allowed reasons:
`not-testable-by-harness` (+ `harness_limit` + `substitute`) · `non-behavioural-prose` · `deferred-P2`
(+ `run_order`). Substitutes: `static_check` · `production_detector` (a `raya/regression/` script, named)
· `human_call` (who, when) · `platform_ask` (what is asked). **No substitute means an open gap with its
own id on the report's front page, never an omission.** In the sheet the row is `BLOCKED` with the
reason.

The real limits (details and recipes in `/voice-test` → "Fixtures"):

- **Inbound bots ARE testable.** PATCH the inbound agent with an integer `out_did`, then POST the call
  with the inbound agent as `agent_id` and the tester DID as `to_number`. The inbound bot looks up the
  caller's number, so inbound test data goes on the tester's number. Never register an inbound variant
  as untestable.
- **Which record the bot looks up IS selectable** for bots that read `${contact_phone}` from the args:
  `contact_phone` in `agent_args` reaches the model (`e0e7bbc2`), so any profile state can be built on a
  `9188888888xx` number on the instance the bot reads. Without it, the bot looks up the dialled number.
- **`contact_memory` cannot be set per call** (the platform substitutes its own, `c2ffe9fb`), and the
  stored memory cannot be read. Memory-gated rows → `production_detector` or a two-call production shape.
- **A TTS tester cannot mumble.** ASR-garble rows → `static_check` + `human_call`. Never write a persona
  that must mumble.
- **No delete route** on Signals: "new caller" on a given number is one-shot; order those rows first.
- **Single-use action pairs**: a repeat returns the limit error (a gift for the error arm, a blocker for
  the success arm).
- **Truncated or corrupt campaign payloads** come from the campaign layer, not from `agent_args`.
- **Instance-scoped ids**: a stale job id reads as a bot bug. Check fixtures with
  `scripts/validate_fixture_ids.py <fixture>` before use.

### 7. Order and tier the suite to real throughput

Calls are serial per tester, creation is rate-limited, bridging needs retries, one tester holds one
persona, the tester caps at 5 minutes: budget **about 10 to 14 completed calls per hour per tester**.

| Tier | Sheet Type | Contents | Gate |
|---|---|---|---|
| **Static** | (not a sheet row; `-static.md`) | example audit, enum values, banned-string absences, format contracts, counters, contradictions | runs first, zero calls; blocks the live run and deploy |
| **Smoke** | Smoke, ≤6 per variant | chosen by **risk**: the end-to-end happy path, the safety row, every open `R` issue, the cheapest error arms, one row per interacting pair that has ever produced a defect on this bot family (rotate pairs across runs) | all must pass before anything else runs |
| **Core** | Manual | the pair scenarios, every terminal state, every tool contract | the blast-radius set after a fix |
| **Extended** | Manual / Stress | the remaining forcing arms, the audience long tail, the accessibility `X` family | weekly rotation by `run_order` |
| **Not reachable** | BLOCKED | step 6, each with its substitute | reported, VERIFY-PENDING |

A Smoke set of four single-axis shapes passes green on a bot carrying production defects; that is why
it is risk-derived. Make the number affordable without shrinking the suite:

- Static and free-rider checks cost nothing.
- **Call sharing** only where persona, language, direction **and** preconditions match **and** the
  personas want the same behaviour at every gate the path crosses. Two rows needing opposite answers
  at the same gate cannot share a call; marked as sharing, one of them is never exercised.
- **Fan out**: K tester agents (each its own DID and persona) turn N calls into about N/K wall-clock.
- **Order by what each call writes**: no-record rows first, then draft, then live, then rows that
  overwrite fields, then action rows.

Static checks never close an `R` case or any Tier-1 claim: static opens a finding, a post-deploy call
closes it.

### 8. Variants: every one, independently

Every case lists every target it must run on: each language, each direction, each backend variant,
read from `raya/agents.json`. A case is passed only for the variants that actually ran. "It passed in
the master language" proves nothing about a mirror.

**A new language needs a tester voice.** `scripts/raya_testcall.py lang <tester_uuid> <code>` reads
`raya/voices.json` for the account (`RAYA_ACCOUNT`, default `ekstep`); a language missing there needs
its `language_id` + `voice_id` added first. Never test a language on the wrong voice.

### 9. Reconcile before writing anything

A suite is complete only when every `FLOW` section names a case (or is `PROSE` with a reason), every
branch arm and every input state has a case or a step-6 reason, every counter, enum value and example
assertion has an assertion, every open issue is 1:1 with an `R` case, and every applicable bug pattern
has a `G` case while every non-applicable one has a one-line reason. **Refuse to emit** a suite whose
count is not reconciled against step 2, or whose gaps exceed 10% of headings, or which uses a gap
reason outside step 6.

### 10. Write the files

**The sheet** (the deliverable):

```bash
python3 scripts/testcase_sheet.py lint  raya/testcases/<bot-id>-sheet.json          # 0 ERROR, or stop
python3 scripts/testcase_sheet.py write raya/testcases/<bot-id>-sheet.json --sheet-id <ID> [--only-tab "<tab>"]
```

- `write` needs an existing spreadsheet id; it cannot create one. Ask the owner for a sheet shared with
  `kkb-sheets-writer@operation-rozgar.iam.gserviceaccount.com` as editor (a 403 means it is not shared).
  Never drive a browser to reach a sheet.
- Layout, identical to the Blue Dots sheet: **Read Me** (what the sheet is, tabs, columns, Type and
  Priority, Verdict values PASS · FAIL · PARTIAL · BLOCKED · NOT TESTED, before-you-start data
  warnings, how to find a call on the Raya console, how to report a failure with call time and the
  last 4 digits of the number, known issues already being fixed, contact) · **Bots to Test** (bot,
  language, direction, how to reach it, console link, what it does, notes) · **one tab per bot family**
  with columns `# | Phase | Scenario | What the tester should say | Expected Response | Language |
  Direction | Type | Priority | Actual Response | Verdict | Call time · number used (last 4) · notes` ·
  **one language tab per non-master language**. Ids are permanent per tab prefix (DK-01 …); a retired
  row keeps its id.
- **Never overwrite people's work.** `write` refuses any tab that already has rows below the header,
  including Read Me and Bots to Test on a sheet that has them, so on an existing sheet write only new
  tabs with `--only-tab`, add single rows with `add-bug`, and ask before `--replace-tabs`.

**The machinery**, same case list:

- `raya/testcases/<bot-id>.json`: the taxonomy §10 schema plus `complexity_vector`, `axis_counts`, both
  ledgers, `interacting_pairs`, `untestable[]`, `spoken_line_registry`. Join to `raya/agents.json` and
  `fleet.json` on `target_id`; never copy a fleet field into it. Check it parses:
  `python3 -c "import json;json.load(open('raya/testcases/<bot-id>.json'))"`.
- `raya/testcases/<bot-id>.md`: the measurements and ratio first, then the Smoke set, then one table per
  family (id · title · source · persona · preconditions · forcing gate · pass · FAIL signal · severity ·
  variants), the not-reachable register, and patterns applied / not applicable.
- `raya/testcases/args/<bot-id>-<state>.json`: one per input state, ids valid on that variant's
  instance. Fixture phone numbers come from the `9188888888xx` block, never a real person's.
- **Personas**, one per behavioural scenario per language, in the house style (read two existing ones
  first; `raya/personas/scenario-catalog.md` is the index): an HTML-comment header (what it is, the
  backend state it needs, what it exercises, its forcing gate, the real call it is grounded in); the
  `# YOU ARE A PERSONA` heading copied from an existing persona, with the never-break-character rules; `## Language`
  (language and script, short colloquial phone sentences); `## Who you are` (fixed facts);
  `## How you behave` (the forcing behaviour, one thing at a time); `## Ending the call`. Instructions
  in English, only the spoken lines in the target language. Reuse before you mint.
- **The bot checklist** at `.claude/skills/voice-test/reference/checklists/<bot-slug>.md`, in the house
  style: a short header (bot, variants, backend shapes), numbered `## N.` sections in call order, each
  item `- [ ] \`<bot>.<N>.<k>\` <what must be true>` followed by an italic `*Why / how to detect:*` line
  citing the pattern (`cf. D37`) and `[repro <issue-id>]` for repros. Each prohibition declares its
  `scope_turns` (default is not `whole_call`); cross-script comparisons say `compare: cross_script`;
  unfalsifiable items go to `## Observations (not graded)`. **Never restate a `generic.md` item**: cite
  it (`generic §3`). Generic accessibility items belong in `generic.md`; propose promotions and **ask
  before editing `generic.md`**, which grades every bot in the fleet.

### 11. Hand off to `/voice-test`, and run the Smoke rows once

A sheet nobody has run is a document, not a test suite. Run the Smoke rows once on each variant via
`/voice-test` (→ "Run a test sheet"), confirm each row is runnable (persona loads, args are the right
shape, preconditions hold) and that its pass rule actually tells a good call from a bad one; fix any row
that cannot be graded from the call. Give the user the exact next sentence to type ("say 'run the Smoke
rows on the Kannada bot'"). The commands, with this bot's real values:

```bash
python3 raya/regression/static_regression.py                         # fleet static checks (zero calls)
python3 scripts/raya_testcall.py persona <tester_uuid> raya/personas/<lang>-<behaviour>.md
python3 scripts/raya_testcall.py lang    <tester_uuid> <lang>
python3 scripts/raya_testrun.py <bot_uuid> <tester_10digit_DID> raya/testcases/args/<bot-id>-<state>.json <tester_uuid> "<row-id>-<target-id>"
```

Bot-specific static checks do not run in the daily job yet (taxonomy §11); say so, and label the
static tier a manual pass in the report.

### 12. Report (plain words, root `CLAUDE.md` → "How to report back")

1. **The sheet link**, and per tab the row count by Type and Priority, plus the lint result.
2. **How complete it is**: scenarios derived vs run, assertions vs exercised, and what is not reached
   with its substitute. A green report over a low ratio is itself a defect.
3. What the example audit found, as counts, and every contradiction sent to `/update-prompt`.
4. The live-call estimate (`rows × calls per row × variants ÷ ~12 per hour`) and the testers needed.
5. Which rows are untested (on a fresh sheet, all of them), and what is still open from before.
6. The next step, as a sentence the person could type.

Internal words (axis, ledger, obligation, fixture, D-numbers) stay out of what the user reads unless
they used them first.

---

## Guardrails

- **Generates test artifacts only.** Never edits a prompt, never deploys, never fixes. Confirmed
  findings go to `/update-prompt` (or `/port-feature` for a fix proven on a sibling).
- **No case without a source** (taxonomy §0). Invented coverage gets deleted in review.
- **No fix without a transcript**, here too: an unconfirmed `R` case never justifies a prompt edit.
- **Real users' numbers and profiles are read-only.** Fixtures and personas use test numbers only.
- **Surgical edits** to existing personas and checklists; never localise a `${variable}`, a tool name or
  a fixed payload param in a case, persona or checklist.
- **Instructions in English; only spoken lines in the target language**, in personas and checklists as
  in prompts.
- **One source of truth per fact**: deploy identity in `raya/agents.json`, fleet labels in `fleet.json`,
  test coverage here. Join on the target id.
- **Ids are permanent.** A retired case or row keeps its id (`result: "retired"`).
- If the bot or its prompt file is not registered, stop and hand back to `/register-bot`.
- This skill writes no prompt, so it needs no `CHANGELOG.md` entry and no snapshot.
