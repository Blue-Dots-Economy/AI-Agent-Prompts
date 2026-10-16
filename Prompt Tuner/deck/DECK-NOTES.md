# Prompt Tuner deck — speaker notes & claim traceability

Companion to `deck/prompt-tuner-deck.html` (22 slides, self-contained, opens offline).
Built **2026-08-05** from the repo state on that date.

**Navigation:** ← → (also PageUp/Down, Space, Home/End) · **T** for the contents overlay ·
click the right/left half of the screen to advance/go back · `#s7` in the URL deep-links to slide 7.

---

## How to run this deck

| Audience | Route | Time |
|---|---|---|
| Exec / leadership | 1 → 2 → 4 → 6 → 10 → 16 → 19 | ~10 min |
| Whole team (default) | 1 → 19, skip appendices | ~30 min |
| Engineers adopting it | 5 → 9, 11, 12, 14, 18, 20 | ~25 min |
| Someone challenging a number | 22 first, then the slide they doubt | ~5 min |

**The one thing to protect:** the deck's credibility rests on the honesty legend and slide 22.
If you cut anything, do not cut those. If asked a number you cannot source live, say
"that's on slide 22, and if it isn't, we didn't claim it."

---

## Per-slide speaker notes

### 1 — Title
Open with the sentence that is genuinely new: **two AI agents talk to each other over a real phone
call, and the find→fix→verify loop runs with no human in it.** Everything else in the deck is
evidence for that. The four numbers in the footer are all repo-verifiable — don't round them up.

### 2 — Executive summary / the ask
The only slide a busy exec needs. Land the three asks explicitly and pause on the third: **the
weekly live tier is blocked on credentials, not engineering.** That is a decision someone in the
room can make today.
Introduce the legend here — Shipped / In progress / Planned — and say out loud that you will use it
on every capability. That framing buys trust for the rest of the deck.

### 3 — The problem
Read two or three of the bug rows aloud verbatim. They are funny and they land instantly with a
non-technical audience — "the bot said the word *slash* out loud", "told a caller she was looking
for *Any* work". Then pivot hard to the right-hand column: these were not sloppiness, they are
**structural** failure modes of LLM voice agents, which is why the thesis quote matters —
*a rule being present in the prompt does not mean it holds at runtime.*
If someone asks "were these caught in production?" — some were reported by the team, some were
found by our own harness, and slide 8 shows one of the latter.

### 4 — Cost of the status quo
The point of this slide is that manual verification sits **on the critical path to a campaign going
live**. Cost 4 is the one to dwell on: three inbound bots would have offered jobs that do not
exist, to real job-seekers. Cost 3 is the setup for slide 12 — don't spend the Maya story here.
Cost 5 (the 07-23 rollback) is the strongest argument for the taxonomy; foreshadow slide 11.

### 5 — The solution / architecture
Keep this fast — it is a map, not an argument. Trace the arrow path left to right once, then point
at the loop bar underneath and say **"and this is the part that used to need a human."**
The three cards at the bottom are the guardrails that stop this from becoming a machine that
confidently makes things worse. "No fix without a transcript" is the single most important rule in
the repo.

### 6 — HERO 1 · Topology
**Slow down. This is the slide people will remember.**
Walk it in this order: (1) the persona library — 16 human characters mined from real calls;
(2) the tester agent, whose *entire prompt is the persona*; (3) the real phone call between them —
not a simulation, real telephony, the bot runs its real prompt and hits its real backend;
(4) capture *both* legs including the tool payloads; (5) grade; (6) fix; (7) deploy; (8) re-test.
The line to say out loud: **"nobody dials anything."**
If asked why the tester must be a separate agent: the callee receives no per-call arguments, so the
persona has to be swapped by patching its prompt — which is also why scenarios run serially
(slide 9).

### 7 — HERO 2 · How a call is graded
Pre-empt the obvious objection: *"an AI grading an AI is marking its own homework."* The answer is
on this slide — every checklist item specifies **how to detect pass/fail from the transcript, the
tool payloads, or the call output**, and cites the bug pattern it guards. It is not a judgement call.
The dark box is the technical crux: **read the tool-call arguments, not just what was spoken.** A
grader that reads only the spoken text sees a clean call and misses the bug entirely. That one
insight is why this harness finds things humans listening to recordings do not.
Be precise if pressed: these are agent-graded against written criteria — not a passing unit-test suite.

### 8 — HERO 3 · A real bug, found and killed
Tell it as a story, in four beats:
1. A harness call ran an edge-case campaign argument nobody had thought to test.
2. The bot read a database placeholder aloud to an employer — *"Not Available, Not Available
   vacancies, salary Not Available"* — and took the wrong branch entirely.
3. Root cause was one word: the condition tested whether the field was *present*, and
   `"Not Available"` is a non-empty string.
4. Fixed, mirrored to Hindi, **and re-verified on both languages separately**, same day.
The kicker in the dark bar: **this bug was never reported by anyone.** That is the difference
between a testing system and a bug tracker.
Note honestly if asked: the transcript panels are condensed to the graded findings recorded in
TEST-LOG.md, not a verbatim dump.

### 9 — HERO 4 · What it catches, and what it cannot
Do not skip the right-hand column. Stating the limits is what makes the left-hand column
believable. The three that matter most:
- inbound bots cannot be dialled by the tester, so anything unverifiable is marked
  **VERIFY-PENDING** rather than "done";
- one tester means one persona at a time, so scenarios are serial;
- backend and runtime tool-adherence failures are **not prose-fixable** — we escalate rather than
  pile on more prompt text, because that has already backfired.
Close on the dark box: 5 entries carry VERIFY-PENDING and 1 is an outright rollback. The log's
willingness to say "not proven yet" is what makes 8/8 mean something.

### 10 — The three tiers
This is the **proposal slide** — the standard we want adopted. Give each tier its one-line reason
for existing. Tier 2 is the one teams skip and the one that catches "fixed X, silently broke Y";
the 07-23 rollback is the proof.
Then read the law at the bottom aloud, in full. "It works for Hindi, so Kannada is fine" is the
cheapest shortcut and the most expensive mistake — and slide 12 has the receipt.

### 11 — The taxonomy (67 patterns)
Frame it as the compounding asset: **every bug we fix is required to leave behind a way to catch it
earlier.** The changelogs are the feed; this catalogue is the distilled form.
Pick ONE of the three examples and go deep — D31 is the crowd-pleaser: the prompt said "do it in a
single turn", so the model batched both tool calls and built the second one's arguments before the
first had returned. **The wording was the bug.** The detection heuristic is to grep for that exact
phrasing near a create→apply pair.
If someone says "I heard 74" — say so first, before they do: an in-progress file in the repo cites
74; the verifiable count is 67; we use 67. Volunteering the correction is worth more than the number.

### 12 — Multi-language integrity
Two things to land. First, the rule that surprises everyone: **instructions are always in English,
in every language file** — only what the bot literally *speaks* is in Hindi or Kannada. That is why
twins can share byte-identical instructions.
Second, the receipt for slide 10's law: Maya-outbound **passed**. Extrapolating from it was the
obvious, cheap call. Testing Maya-inbound independently found `+91+91…` — profile lookup empty,
profile creation 400. Read the log's own sentence: *"extrapolating from Maya-out passing would have
shipped the bug."*
The divergences registry is marked In progress deliberately — the file exists as of today, but it
has not yet been exercised by a sync run.

### 13 — The standing daily net
Be precise about the number, because someone will check: **6 check classes × 16 bot scripts = 96
script-by-class cells, which expand to 269 individual assertions.** The "100+ test cases" phrasing
in the repo's CLAUDE.md is the aspirational framing; 269 is the instrumented count (6 classes x 18
scripts = 108 cells). Recomputed 2026-08-05 after the fleet was corrected from 16 to 18 bots.
Emphasise two things: it runs **in the cloud** so it survives the laptop being off (that was the
literal requirement), and the digest is **written for a stranger** — no jargon, a glossary, and a
"start here" section. Show the phone-doubling sentence as the example of tone.
Volunteer the caveat: the shared cron queue delays runs by up to ~3.5 h, so it is "each morning",
not a guaranteed clock time.

### 14 — Skill catalogue
Do not read all fourteen. Say "this is the whole system in one view" and let people scan.
Then be explicit about the badges: **three of the fourteen were written today and have produced
nothing yet** — `raya/testcases/` is empty, no bot exists in a third language, no bot has been
registered through the new flow. Calling those "shipped" would be the exact kind of overstatement
this deck is trying to avoid.
Highlight `/translate-prompt`'s 12 declared languages as the reach story — but as *declared*, not
*delivered*.

### 15 — Results to date
All measured, 37 days. The campaign table is the centrepiece: 8 bots, 11 graded calls, 7 revertible
decisions, 16 sync fixes, 1 ship-blocker caught, **2 pre-existing bugs nobody had reported.**
Then immediately show the honest column: 5 VERIFY-PENDING, 1 rollback, 1 minor finding open today,
6 tracked open items with the highest being an unverified apply path. Presenting the caveats
yourself is what makes the greens credible.

### 16 — Impact, quantified
**Open by saying what this slide is not:** it is not a measured saving. The quantities in column 2
are measured; the rates in column 3 are assumptions we chose, printed on the slide.
State the assumptions out loud — 2.5 h → 0.75 h per bug-fix cycle, $25/h blended, and a fortnightly
(not daily) manual-regression baseline. Then the numbers: ~148 h ≈ $3,700 over 37 days; ~$36.5k/year
if the intensity holds, which is an **extrapolation from 37 days**.
The red row is deliberate and you should point at it: campaign go-live delay is the owner's stated
largest cost, and the repo has **no** campaign-volume or cost-per-call data — so we print no number.
Close on the right-hand card: the strongest argument is not the money, it is that a bilingual bot
can now be verified **per variant**, which manual testing was never going to do.

### 17 — Ecosystem use case
The argument: the prompts are specific, everything around them is not. The taxonomy has already
been applied to Purple Dots — a different domain, a different audience — and produced 11 root-caused
findings. **Different bot, different purpose, same failure classes.**
Then the DPG framing: most voice agents reaching the next hundred million Indians will be built by
small teams with no QA function; a shared quality-and-testing rail is exactly the horizontal
capability a composable public-good ecosystem should provide.
Flag clearly that the DPG paragraph is an *argument*, not a repo fact — and name the two real
portability limits (one voice platform, two persona languages).

### 18 — How to adopt
Walk the five steps quickly; the audience mostly needs to know the path exists. Land the three
cards at the bottom, especially the third: **if the transcript shows the inputs were wrong, we say
"the prompt is fine" and make no edit.** A tuner that fixes non-bugs to look busy destroys the only
thing that makes it useful.
Note that step 1 touches nothing — onboarding gathers and reproduces only.

### 19 — Roadmap
Ordered by what unblocks the most. Item 1 is the ask from slide 2 restated with the blocker named:
**keys in CI, not engineering work.** Items 2 and 3 are honestly In progress — written today,
unexercised. Item 4 (Purple Dots) is the first real test of multi-project support, and item 5
(accessibility test family) is the prerequisite for doing item 4 properly rather than nominally.
Item 6 is the open-items list; don't hide it.

### 20 — Appendix · technical map
Reference only. Two things worth saying if you land here: 18 conversation prompts exist but 16 are
in the regression fleet (2 DKB inbound prompts are written but have no live agent), and the repo is
**public**, which is why this deck contains no identifiers, phone numbers, or tokens.

### 21 — Appendix · glossary
Hand this to anyone joining cold. The dark box holds the three sentences that carry the whole
system; the card beside it holds the one that keeps it honest.

### 22 — Appendix · claim traceability
The trust slide. Say plainly: **if a number is not in this table, it is not a claim we are making.**
Point at the two corrections we volunteered (74→67, 127 vs 129) and at "what we deliberately did not
claim". Volunteering your own weak points is the cheapest credibility you will ever buy.

---

## Quantified-claim traceability

Every number that appears anywhere in the deck. **Measured** = read directly from a repo artifact.
**Derived** = arithmetic on measured values. **Classified** = human judgement over repo content.
**Declared** = stated in a repo file as intent/support, not demonstrated. **Modeled** = depends on
an assumption we chose; the assumption is printed on the slide.

### Measured

| Claim | Value | Source file | Method |
|---|---|---|---|
| Logged prompt changes | **127** | `KKB/CHANGELOG.md` (62), `DKB/CHANGELOG.md` (10), `Maya/CHANGELOG.md` (55) | `grep -cE '^## [0-9]{4}-[0-9]{2}-[0-9]{2}'` |
| Changelog date span | **2026-06-29 → 2026-08-04** (37 days incl. deck date) | same three files | first/last dated entry |
| Cross-agent ports | **14** | same three files | entries with a `- **Ported from:**` field (KKB 9, DKB 0, Maya 5) |
| Entries citing a call id | **33** | same three files | narrow `call <8-hex>` pattern |
| VERIFY-PENDING entries | **5** | `KKB/CHANGELOG.md` (3), `Maya/CHANGELOG.md` (2) | literal string match |
| Explicit rollbacks | **1** | `KKB/CHANGELOG.md` 2026-07-23 | literal entry |
| Busiest single day | **25 entries** (2026-07-20) | three CHANGELOGs | entries grouped by date |
| Catalogued bug patterns | **67** | `.claude/skills/prompt-analyser/reference/bug-patterns.md` | `grep -c '^### '`; ids A1–A8, B1–B2, C1–C12, D1–D40, E1–E4, G1 — contiguous, no duplicates |
| Pattern families populated | **6** (7 headings, F is a pointer) | same | `^## ` headings |
| Patterns with dated provenance | **56 of 67** | same | 11 are standing rules / undated Purple Dots review |
| Required sections (analyser) | **30 distinct**; 11 universal core + 8/7/4 by archetype | `prompt-analyser/reference/section-checklists.md` | enumerated |
| Universal rule ticks | **24** in 6 groups | same | checkbox count |
| Analyser severities | **3** (high / medium / low) | `prompt-analyser/SKILL.md` | verbatim |
| Generic checklist | **13 sections, 47 items** | `voice-test/reference/checklists/generic.md` | `grep -c '^## '` / `grep -c '^- '` |
| KKB checklist | **14 sections, 51 items** | `…/checklists/kkb.md` | same |
| DKB checklist | **12 sections, 39 items** | `…/checklists/dkb.md` | same |
| Maya checklist | **16 sections, 60 items** | `…/checklists/maya.md` | same |
| Persona scripts | **16** (10 Hindi, 6 Kannada) + router + catalogue = 18 files | `raya/personas/` | listing |
| Bot scripts in regression fleet | **16** (8 KKB, 4 DKB, 4 Maya) | `raya/regression/latest-report.json` → `prompts_checked` | direct read |
| Static check classes | **6** | `raya/regression/static_regression.py` | leakage · phone-doubling · memory-block · enum-drift · required-sections · sync-parity |
| Individual assertions per run | **269** | same script | recomputed 2026-08-05 for the 18-bot fleet: leakage 148, sections 36, enum 24, phone 18, memory 18, fleet-coverage self-check 18, Hi/Kn parity 7 |
| Script × class cells | **96** (6 × 16) | derived from the two above | — |
| Suite runtime | **~6 s** | `raya/regression/README.md` | stated |
| Latest report | **18 prompts · 0 critical · 0 major · 1 minor** | `raya/regression/latest-report.json` | direct read |
| Language pairs compared | **6** | `static_regression.py` `sync_parity()` | instrumented (Maya has no Kannada) |
| Curated open items | **6** (1 high, 4 medium, 1 low) | `raya/regression/open-items.json` | direct read, updated 2026-08-04 |
| Digest email sections | **4** | `raya/regression/build_digest.py` | `section()` calls |
| Signals E2E result | **8/8 bots green** | `raya/signals-expansion/e2e/TEST-LOG.md` | "Result: 8/8 bots GREEN" |
| Graded live calls, Signals campaign | **11** | same | table rows |
| Critical decisions | **7** (CD1–CD7) | `e2e/DECISIONS-AND-FIXES.md` | enumerated |
| Mechanical sync fixes | **16** (M1–M12, M14–M17; M13 unused) | same | enumerated |
| Legacy bots restructured | **6**; **5 green + 1 VERIFY-PENDING** | `e2e/LEGACY-REGRESSION.md` | table |
| E2E revert snapshots | **28** | `e2e/snapshots/` | listing |
| Conversation prompts on disk | **18** (KKB 8, DKB 6, Maya 4) | `KKB/ DKB/ Maya/` | listing minus CHANGELOG/Memory/Output |
| Total prompt lines | **22,004** | same | `wc -l` summed over the 18 files |
| Largest single prompt | **1,591 lines** (`KKB Placeholder Inbound Kannada.md`) | same | `wc -l` |
| Deploy targets | **25** (18 conversation, 4 memory, 3 output) | `raya/agents.json` | JSON load |
| Version snapshots | **228** (KKB 141, DKB 11, Maya 76) | `versions/` | listing |
| Purple Dots findings | **11** (6 high, 4 medium, 1 verify) | `Purple Dots — Prompt Gap Analysis.md` | priority-summary table |
| Skills authored | **14**, all with a complete `SKILL.md` | `.claude/skills/` | listing at 2026-08-05 |
| Skills with a track record | **11** | same + changelogs/E2E logs | the 3 authored 2026-08-05 have produced no artifacts |
| `get_profile` miss rate (example) | **0 of 8 calls** | `KKB/CHANGELOG.md` 2026-07-27 | verbatim |
| `create_job` prior failures (example) | **4×** on 2026-07-31 | `e2e/TEST-LOG.md` | verbatim |

### Derived

| Claim | Value | Derivation |
|---|---|---|
| Items graded per call | **86–107** | generic 47 + bot-specific (DKB 39 = 86; KKB 51 = 98; Maya 60 = 107) |
| Bug-fix share of entries | **~60–65%** | ~80 of 127 |
| Port share of entries | **~1 in 9** | 14 of 127 |
| Sustained change rate | **~3.5/day** | 127 over 37 days |

### Classified (human judgement — stated as ±4 per bucket on the slide)

| Claim | Value | Basis |
|---|---|---|
| Bug fixes | **~80** | hand classification of all 129 logical entries |
| Feature additions | ~23 | same |
| Reconciliations | ~8 | same |

### Declared (stated as intent/support in a repo file; **not** demonstrated)

| Claim | Value | Source |
|---|---|---|
| Translation languages supported | **12** — Hindi, Kannada, Telugu, Malayalam, Tamil, Marathi, Bengali, Gujarati, Punjabi, Odia, Assamese, Urdu | `.claude/skills/translate-prompt/SKILL.md` frontmatter. **No bot exists in a third language.** |
| Test-case families | **6** (F/T/A/R/X/G) | `generate-test-cases/reference/test-case-taxonomy.md`. **No suite generated yet.** |

### Modeled — assumptions chosen by us and printed on slide 16

| Figure | Value | Grounded input (measured) | Assumption (ours) |
|---|---|---|---|
| Bug-fix hours saved | **140 h** | ~80 bug-fix cycles in 37 days | 2.5 h manual → 0.75 h assisted per cycle |
| Bug-fix $ saved | **$3,500** ($5,600 at $40/h) | 140 h | blended rate **$25/h**, sensitivity $40/h |
| Voice-test hours saved | **7.6 h** | 17 graded calls (11 Signals + 6 legacy) | 35 min manual → 8 min assisted per call |
| Voice-test $ saved | **$190** | 7.6 h | $25/h |
| Regression hours saved | **10 h/month** | 269 assertions × 18 scripts, daily, ~6 s | manual pass ≈ 5 h; baseline cadence **fortnightly**, not daily |
| Regression $ saved | **$250/month** | 10 h | $25/h |
| Cycle-time reduction | **70%** | — | 2.5 h → 0.75 h |
| Regression cadence gain | **15×** | daily cron is real | fortnightly manual baseline |
| Observed-window total | **~148 h ≈ $3,700** | sum of the three levers over 37 days | as above |
| Annual run-rate | **~1,460 h ≈ $36,500/yr** | — | **extrapolation from 37 days**, labelled as such on the slide |

### Deliberately NOT quantified

| Item | Why |
|---|---|
| Campaign go-live delay cost | The owner's stated largest cost, but the repo contains **no** campaign-volume, caller-count, or cost-per-call data. Any figure would be invented. Shown on slide 16 as an explicit non-claim. |
| Customer / adoption numbers | None exist in the repo. |
| Bugs prevented in production | Not measurable — we can count bugs *found*, not bugs that never happened. |
| Per-language quality scores | The checklists produce pass/fail per item, not a calibrated score. |

---

## Corrections put on the record in the deck

1. **"74 patterns" → 67.** `generate-test-cases/reference/test-case-taxonomy.md` refers to "the 74
   learned bug patterns". The verifiable count in `bug-patterns.md` is **67**
   (`grep -c '^### '`). The deck uses 67 and states the discrepancy on slides 11 and 22.
2. **127 vs 129 changelog entries.** 127 is the grep-verifiable count. Two KKB entries are missing
   their `## <date>` header, so the true logical count is 129. The deck quotes the lower number.
3. **"100+ test cases" (CLAUDE.md) → 269 assertions / 108 cells.** The repo's Tier-3 description says
   "100+ test cases". The instrumented static suite runs 6 check classes over 18 scripts = 108 cells,
   expanding to 269 individual assertions. The deck uses the instrumented figures.
   (Was 222/96 at 16 scripts; recomputed 2026-08-05 when the fleet was corrected to 18 — see #5.)
4. **Family C is filed partly under the G heading** in `bug-patterns.md` (C11, C12 sit below the
   `## G.` heading), so the deck does not claim a clean 7-way family partition.

## Marked PLANNED or IN PROGRESS rather than shipped

| Capability | Badge | Why |
|---|---|---|
| Weekly live-call regression tier | **Planned** | `.github/workflows/regression.yml`: "the weekly LIVE voice regression is NOT implemented yet". No live-call script; Raya/Signals keys absent from CI secrets. Tracked as `weekly-live-not-wired`. |
| `/generate-test-cases` | **In progress** | Complete `SKILL.md` authored 2026-08-05, but `raya/testcases/` does not exist — it has never generated a suite. |
| `/translate-prompt` | **In progress** | Complete `SKILL.md` authored 2026-08-05 declaring 12 languages, but no bot exists in a third language. |
| `/register-bot` | **In progress** | Complete `SKILL.md` authored 2026-08-05; no bot has been registered through it. |
| `raya/divergences.json` registry | **In progress** | File created 2026-08-05; not yet exercised by a `/sync-check` run. |
| Purple Dots rollout | **Planned** | A gap analysis exists (11 findings), but the bot is not registered, not deployed by us, and not in the regression fleet. |
| Accessibility test family (X) | **Planned** | Named as a roadmap gap in the test-case taxonomy. |
| Tier-3 as a substitute for tiers 1–2 | **explicitly denied** | The deck repeats the repo's rule that the standing suite is never a substitute for fix-verification and blast-radius testing. |

---

## Security / disclosure check performed on the deck

The repo is **public**. Before finalising, `deck/prompt-tuner-deck.html` was scanned and is clean of:
agent UUIDs (full or partial), DIDs / phone numbers, API keys or tokens, the tracker sheet id, the
Raya console host, service-account addresses, and email addresses. The only identifiers present are
**truncated 8-hex call-id references** (e.g. `a02f61b3`) that appear in the changelogs and are
ephemeral call records, not credentials.

The deck is also fully **offline-capable**: zero external `src`/`href`/`@import`/`fetch`/`<link>`
references. Fonts degrade gracefully to system stacks (Space Grotesk / Newsreader / JetBrains Mono
are used only if locally installed).

## Rendering verification performed

- All **22 slides fit 1280×720 with zero vertical or horizontal overflow** (measured via
  `scrollHeight − clientHeight` per slide).
- No inner-container clipping (the case where a `flex:1` child silently overlaps the content below).
  One intentional exception: the loop-bar label on slide 5 is positioned outside its bar by design.
- Stage is centred at any viewport size and preserves 16:9 (verified 1.778 aspect).
- Bold text on dark surfaces is explicitly forced to white — without that rule it inherits the dark
  ink colour and becomes invisible on the title slide, `.dark` cards, and `.lead-in` bars.

---

## Addendum — 2026-08-05 corrections and new claims

Added after the first build, when the underlying repo changed. All verified on disk.

| Claim | Value | Source | Note |
|---|---|---|---|
| Fleet size | **18** conversation prompts / deploy targets | `raya/agents.json` (`kind: conversation`), `raya/regression/fleet.json` | **was reported as 16.** `static_regression.py` hard-coded a 16-file list and silently omitted `DKB/DKB Inbound Hindi.md` (`dkb-hi-in`) and `DKB/DKB Inbound Kannada.md` (`dkb-kn-in`) — both `deploy:true`, i.e. **two live bots the daily check had never examined**, while the digest said "16 bots checked". Both now covered; both clean. |
| Assertions per run | **269** | instrumented `static_regression.py` | see breakdown above |
| Coverage self-check | **shipped** | `coverage_gap()` in `raya/regression/static_regression.py` | reads the deploy manifest and emits a **CRITICAL** finding if any live target is unchecked. Verified by negative test: hiding a bot raised the critical. This is the durable fix for the row above — the suite now audits its own coverage. |
| Generic checklist | **54 items, 14 sections** | `.claude/skills/voice-test/reference/checklists/generic.md` | `## 14. Accessibility & access needs` added: 7 fleet-wide items + 2 framing rules (never make the disability the subject of the call; never require disclosure to get help). Fleet-wide because the same items help elderly callers, bad lines, shared phones and non-fluent speakers. |
| Bug-pattern catalogue | **67** | `grep -c '^### '` on `bug-patterns.md` | not 74 (the figure in an earlier draft of `test-case-taxonomy.md`). Ids A1–A8, B1–B2, C1–C12, D1–D40, E1–E4, G1. The count grows with every bug fix by design, so prefer citing the file. |
| Skills | **14 authored, 11 with a production track record** | `.claude/skills/` | `/translate-prompt`, `/generate-test-cases`, `/register-bot` have complete `SKILL.md` files but have produced no artifact yet — **In progress**, not shipped. |
| Fleet manifest generator | **shipped** | `scripts/build_fleet_manifest.py` → `raya/regression/fleet.json` | derives the fleet from `agents.json` + the suite's own derivation, cross-checks both directions, CI-safe `--check` mode. Replaces the hand-maintained list that caused the coverage gap. |
| Multi-project tooling fixes | **shipped** | `scripts/prompt-version.sh`, `scripts/raya_call.py` | `prompt-version.sh` now discovers bot folders instead of hard-coding `kkb\|dkb\|maya` (it previously died on any newly registered bot, silently blocking the "snapshot before edit" law). `raya_call.py` now prints the **full** `agent_args`/`call_output` instead of 3 KKB-era keys — required by the repo's own "root-cause against the input args before editing" rule. |
| Review of the new skills | **39 findings, all closed** | 3 adversarial reviewers + an independent re-check | 5 critical, 12 major, 22 minor. The two worst: the coverage gap above, and a divergence registry that no skill wrote to (`/sync-check` and `CLAUDE.md` both asserted `/update-prompt` must record deliberate divergences, but neither `/update-prompt` nor `/port-feature` mentioned the file — so an owner's deliberate decision would have been "corrected" by the next audit). |

**Still PLANNED, not shipped:** the weekly live-call tier (blocked on CI credentials, not engineering), the Purple Dots rollout itself, and any artifact from the three new skills.
