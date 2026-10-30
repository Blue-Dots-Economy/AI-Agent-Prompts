# Prompt Tuner — Voice Agent Prompt Maintenance

This repo holds the system prompts for three voice AI agents. The job of anyone
working here is to **iterate on these prompts from feedback/bugs while keeping the
language variants in sync**. Do not treat these as ordinary docs — a wording change
in one language that does not land in its twin is a regression.

## Multi-project — do not assume three bots and two languages

The Tuner is now a **shared rail across several BlueDot-team projects**, not a three-bot tool.
Assume **N projects, N bots, N languages** in everything you write here.

- **Blue Dots** — the employment rail: **KKB** (seeker job-matching), **DKB** (employer job
  capture), **Maya** (campus recruitment). Hindi (master) + Kannada; Maya Hindi-only.
- **Purple Dots** — a bot rail for **people with disabilities**, being taken multi-Indic.
  Accessibility (pacing, silence tolerance, repeat-on-request, never making a caller's
  disability the topic of the call) is a first-class grading concern for the whole fleet.
- **More to come.** A new project is first-class, never an exception: record it as
  `project: <kebab-case-name>` and register it like any other.

So never hard-code a bot list or a language pair — resolve bots through the path map below and
`raya/agents.json`, and resolve languages from the manifest, not from filenames.

**Two documents to read alongside this one:**

- **`docs/WORKFLOW.md`** — the **end-to-end map**: the full onboarding → registration → analysis →
  test-case generation → live testing → fix → deploy → re-verify → language expansion → standing
  regression path, a decision table ("I want to ___ → run /___"), three worked scenarios, and the
  known limits/gotchas. This is what you hand a third person instead of a verbal handover.
- **`docs/MULTI-PROJECT-ROADMAP.md`** — the **multi-project spec of record**: why the new skills
  exist, and the structural gaps G1–G8 (path map, `/register-bot`, N-language `/sync-check`,
  config-driven regression fleet, per-language personas, per-bot checklists, digest labels,
  accessibility checks) with their resolutions and build order.

## Surgical edits only — these prompts are fragile

These prompts run live voice agents; a stray change can break the whole agent. Every edit
must be **surgical**: change only what the task requires, and nothing more.

- Make the **smallest edit** that accomplishes the goal. Do not reformat, re-wrap, re-style,
  re-order, or "clean up" surrounding text while you're in there.
- **Preserve exactly:** spoken lines, variable names (`${...}`), tool names, JSON payloads
  and field names, fixed params (e.g. `sourceService: "ONESTAGENT"`, `app_instance`), and
  section structure — unless the change is explicitly about one of them.
- Prefer **additive** changes. Do not delete content the task didn't ask you to remove.
- Never localize a variable/tool/payload name; never paste one language's spoken text into
  the other file.
- When in doubt, do less and ask. After editing, the diff should contain **only** the intended
  change — if it shows incidental edits, revert them.
- One real exception: a fix the user explicitly approved that is broad by nature (e.g. the
  DKB full reconciliation). Even then, scope it to the approved items and preserve everything else.

## Agents

- **KKB** — government job-matching agent for workers/seekers (Hindi + Kannada). Persona: *काम की बात / ಕೆಲಸದ ಮಾತು*.
- **DKB** — "Dhandhe Ki Baat", job verification & capture agent for MSME business owners/employers (Hindi + Kannada). Persona: *धंधे की बात*.
- **Maya** — a KKB spinoff for higher-ed graduates in UP; campus-recruitment context. **Hindi only.** Persona: *माया, [college_name] की ओर से*.
- **TRRAIN** — an **outbound-only** follow-up campaign (Hindi + Kannada) calling seekers who have **already applied** to a job, to offer them one free support service and capture their interest. **Its only tool is `get_profile`** (added 2026-08-11, so it can greet the caller by their real name and reference the role they actually applied for); it **cannot** fetch jobs, apply, create or update anything — it cannot fetch, apply, or update anything. Short call (under two minutes), one offer per call. **The partner TRRAIN Trust IS now named aloud** — spoken as "ट्रेन ट्रस्ट" / "ಟ್ರೇನ್ ಟ್ರಸ್ಟ್", with a one-line introduction of who they are, and it is the ONLY partner that may be named. (This line used to say the partner is never named; that was superseded in the Hindi prompt and the manual was left behind — corrected 2026-09-04, when the Kannada mirror was also found still carrying the old "never name TRRAIN" rule and was brought up to the master.)

Each agent has three prompt types: a **conversation prompt** (one file per language),
a **memory prompt** (one language-agnostic file, English output), and an
**output prompt** (one language-agnostic file that extracts call variables).

## File path map

Filenames are kept as-is (note KKB's "Placeholder" naming). Always resolve files through this map.

| Agent | Hindi | Kannada | Memory | Output |
|---|---|---|---|---|
| KKB | `KKB/KKB Placeholder Hindi.md` | `KKB/KKB Placeholder Kannada.md` | `KKB/KKB Memory.md` | `KKB/KKB Output.md` |
| DKB | `DKB/DKB Hindi.md` | `DKB/DKB Kannada.md` | `DKB/DKB Memory.md` | `DKB/DKB Output.md` |
| Maya | `Maya/Maya Hindi.md` | — (none) | `Maya/Maya Memory.md` | `Maya/Maya Output.md` |
| KKB-Slim | `KKB-Slim/KKB Slim Hindi Signals.md` | `KKB-Slim/KKB Slim Kannada Signals.md` | (shares KKB's, per-agent on Raya) | `KKB-Slim/KKB Slim Output.md` (Hindi agent only — diverged from KKB's on 2026-09-23) |
| TRRAIN | `TRRAIN/TRRAIN Hindi.md` | `TRRAIN/TRRAIN Kannada.md` | `TRRAIN/TRRAIN Memory.md` | `TRRAIN/TRRAIN Output.md` |

## Core principle: agnostic vs language-specific

Every conversation prompt is built from two kinds of content. **Every edit must be
classified before it is mirrored.**

- **Language-agnostic** — call-flow logic, phase/step structure, input-variable names,
  tool-call rules and JSON payloads, conditions/routing, prohibited-behavior rules,
  dignity safety checks, the section skeleton itself. → **Copied verbatim** across languages.
- **Language-specific** — spoken greeting scripts, example dialogues, TTS
  number-to-word spellings, script rules (Devanagari vs Kannada), tone markers,
  culturally-adapted prohibited phrases, sample conversations (incl. place/person
  names). → **Translated and adapted** to the target language's idiom, script, and
  conventions. Kannada uses "Kanglish", Kannada-script numerals spelled as words, and
  local place names (Bengaluru/Mysuru/Dharwad rather than Pune/Ghaziabad).

**Instructions are ALWAYS in English — only spoken content is in the target language.**
Every instruction, rule, heading, condition, and explanatory note in a prompt is written in
**English**, regardless of which language file it lives in. The ONLY parts written in
Hindi/Kannada are the actual words the agent **speaks**: quoted spoken lines, example
dialogues, and TTS number-word spellings. Never write rule or instruction prose in
Hindi/Kannada. When you add a spoken line, wrap it in an English instruction and quote the
line, e.g. *Offer line (say once): "एक और मौका…"*. This is exactly why a Hindi file and its
Kannada twin share the **same English instructions** and differ only in the quoted spoken
text. A section whose rules are written in Hindi/Kannada is a bug — rewrite the prose to
English and keep only the spoken lines translated.

The full section-by-section taxonomy with agnostic/specific tags lives in
`.claude/skills/update-prompt/reference/prompt-anatomy.md`.

Memory and Output prompts are **single language-agnostic files per agent** (their output
values are always English) — they have no cross-language twin and are edited once.

## Sync rule

A conversation-prompt change is never "done" after editing one language. The Hindi file
is the **source of truth**; changes are applied there first, then mirrored to Kannada
(verbatim for agnostic content, adapted for language-specific content). Before applying
any new change, the prompt pair must already be in sync — `/update-prompt` runs
`/sync-check` first to guarantee this.

**One master, N mirrors.** Two languages is the special case, not the model. A bot's languages
are one **master** (edited first) and **N mirrors** (each brought up independently): for KKB/DKB
that is Hindi → Kannada, for an N-language bot it is master → every mirror. `/sync-check` audits
the master against **each** mirror and reports a per-language matrix; the master language is
marked in the path map, and the language set is discovered from `raya/agents.json`, never
enumerated in a skill. A change that lands in some languages and not others is a regression.

**Deliberate divergences are registered, not remembered.** Some language differences are
intentional and must never be reconciled away (e.g. the 2026-08-04 KKB Kannada Signals persona
name **ಮಾಯಾ / Maya**, kept while the Hindi Signals twins keep the institution-only intro). These
live in **`raya/divergences.json`** — the machine-checkable divergence registry recording which
bot/targets and languages diverge, which sections/`contains` tokens legitimately differ, why, who
approved it, when, the changelog reference, and what must **still** match. `/sync-check` consults
it and downgrades covered differences to *EXPECTED (registered divergence)*; only **unregistered**
differences in agnostic content are flagged as drift. Whenever `/update-prompt` or
`/port-feature` deliberately applies a change to some languages and not others, it **must** add
the registry entry in the same change as the prompt edit and the changelog entry — no entry means
the next audit will "fix" the divergence away. A registry entry is scoped, not a licence to drift.

## Maya rule (flag-and-ask)

Maya inherits KKB's language-agnostic core but has its own divergences that must **never**
be overwritten by a KKB sync:

- `${college_name}` input variable and campus caller-identity ("माया, [college] की ओर से", not government)
- optional `hr_contact` and `benefits` recommendation fields
- the **Experience Capture** section
- HR-number sharing post-apply
- the explicit **feminine-voice** rule (Hindi feminine verb forms only)

(The MPL Competition offer was removed from all Maya prompts on 2026-10-12 at the programme's request; it is no longer a divergence to protect.)

When a KKB change touches shared core logic, **flag it and ask** the user whether to
also apply it to Maya Hindi before doing so. Maya is Hindi-only — there is no Kannada sync for it.

## Memory injection block (required when memory is enabled)

Once an agent has memory enabled (its memory prompt exists), **every** conversation prompt
for that agent — in every language — must contain this block **exactly**, verbatim:

```
### Contact context
Here is the caller context:
{${contact_memory}}
```

This is the injection point where the memory prompt's output (`contact_memory`) is fed back
into the conversation prompt. It is **language-agnostic** — the same three lines in English
in every language file; never translate or alter them. Placement: inside the intro rules
(KKB/Maya) or at the end of the Input Variables section (DKB) — wherever the agent already
has it; if absent, add it at the end of Input Variables. Creating/enabling a memory prompt
(`/update-memory`) must verify and, if needed, add this block to all of the agent's
conversation prompts.

Every bot in the path map has memory enabled, so every conversation prompt carries this block (the daily static check verifies it).

## Changelog rule

Every prompt edit appends an entry to the agent's `CHANGELOG.md`
(`<bot folder>/CHANGELOG.md`, e.g. `KKB/CHANGELOG.md`, `KKB-Slim/CHANGELOG.md`, `TRRAIN/CHANGELOG.md`). Entry format:

```
## YYYY-MM-DD — <short title>
- **Feedback/bug:** what prompted the change
- **Change:** what was changed
- **Files:** which files were touched
- **Ported from:** <source agent> (only for cross-agent ports)
```

## Bug-fix feedback loop (pre-empt the next occurrence)

Fixing a **bug** in a prompt is not done until the analyser is taught to catch it. Whenever a
bug is fixed (via `/update-prompt`, `/port-feature`, `/update-memory`, or `/update-output`),
you must also update **`/prompt-analyser`** so the same failure class is flagged pre-emptively
in future audits:

- Add or sharpen an entry in `.claude/skills/prompt-analyser/reference/bug-patterns.md` —
  symptom → root cause → **detection heuristic** → fix direction → source agent + date.
- If the bug implies a section that must always exist for that use case, update
  `.claude/skills/prompt-analyser/reference/section-checklists.md`.

The `CHANGELOG.md` entry records *what* changed; the analyser update ensures the scenario is
*detected before it ships again*. This applies to bug fixes only — not to pure feature
additions or ports of already-working behaviour.

## How to make a change

| Task | Skill |
|---|---|
| Apply a feedback item / bug fix to a conversation prompt (both languages) | `/update-prompt` |
| Create or edit an agent's memory prompt | `/update-memory` |
| Create or edit an agent's output prompt | `/update-output` |
| Audit whether the language variants have drifted | `/sync-check` |
| Take a bot into a NEW Indic language — re-author the spoken content the way that language is actually spoken, re-derive its TTS/script machinery, stand up + test the new agent ("add Telugu/Tamil/Marathi", "make it multi-language"). Rules and tool calls are never handed to a translator (`scripts/speech_split.py`), the size is projected first (`scripts/prompt_size.py`), and the prompt-level language checks gate the deploy (`scripts/language_checks.py`) | `/translate-prompt` |
| Carry a feature from one agent to another (e.g. KKB → DKB / Maya) | `/port-feature` |
| Audit a prompt for latent gaps / bug-prone patterns before running it | `/prompt-analyser` |
| Reconcile a repo prompt against the LIVE prompt on Raya (who's ahead) | `/raya-reconcile` |
| Run the feedback loop end-to-end: sheet → transcript → fix → deploy → sheet | `/bug-fix` |
| Test a live agent by having a persona "tester" agent CALL it, then grade the call against generic + bot-specific checklists (find bugs ourselves; verify a fix end-to-end) | `/voice-test` |
| Build ONE bot's own test suite — scenarios from its flow/tools/audience/reported issues + the learned bug patterns → test manifest, tester personas, bot checklist with explicit pass/fail detection ("what should we test on this bot") | `/generate-test-cases` |
| Onboard a new user/customer bringing a voice bot (or point at an existing repo bot) | `/onboard` |
| Register a new bot — or a new language/direction variant — so every skill and script resolves it: folder + prompt files + `CHANGELOG.md`, path-map rows, `raya/agents.json` target(s) with hand-copied uuids, regression fleet entry ("wire up Purple Dots", "add a Tamil variant") | `/register-bot` |
| Bring a COPY of the tuner (a team's own repo, e.g. Purple Dots or Orange Dots) up to date with this parent repo: newest skills, scripts and docs merged in, the copy's own bots never touched ("upgrade the prompt tuner", "/upgrade") | `/upgrade` |
| Find which part of a prompt produced a bot's line, what else a change to a part affects, every rule about one thing, and which parts go with failing calls (`/bug-fix` → "The prompt map") | `python3 scripts/prompt_map.py locate / impact / rules-about / spectrum` |
| Check a bot really remembers a caller between calls: memory wiring check, then two calls from the same number (outbound or real inbound), graded per detail (`/voice-test` → Memory test) | `python3 scripts/raya_memory_test.py check / run / grade / platform` |
| Check that every "go to Step N" / "see <section>" in a prompt lands where it says (run after any edit that adds, removes or renumbers a section) | `python3 scripts/prompt_structure.py <file>` |
| Shrink a long conversation prompt into a "slim" variant without losing behaviour, on its own A/B agent, proven by a coverage table + live calls before any traffic moves ("slim this prompt", "compress the prompt") | `/slim-prompt` |

**For a new or non-technical user, start with `docs/WHAT-YOU-CAN-ASK.md`**: what the tuner does, in
plain sentences they can type, no skill names needed.

**The end-to-end map is `docs/WORKFLOW.md`** — how these skills chain together from intake to the
standing daily regression, plus a decision table for every real situation, three worked scenarios,
and the platform gotchas. Point a newcomer there rather than explaining the pipeline in chat.

`/update-prompt` auto-runs `/sync-check` first, so a new change always lands on an
aligned base. `/prompt-analyser` is a read-only pre-flight review (flags, does not fix);
route its confirmed findings to `/update-prompt`. **Always route prompt edits through
`/update-prompt`** (or `/port-feature` for cross-agent) — it enforces the sync rule, the
English-instructions rule, the changelog entry, and the analyser update; don't hand-edit a
prompt file directly.

**The only other sanctioned write paths** are `/translate-prompt` (authors a **new** language
variant of an existing prompt) and `/register-bot` (files a customer's supplied prompt **verbatim**
as a new baseline), plus `/slim-prompt` (writes a shorter variant as a NEW file on its own A/B agent, or
trims a master that is past its size limit through `/update-prompt`). Those **create** prompt files;
only `/update-prompt` / `/port-feature` change content that already exists. All of them still owe the same obligations — the pre-edit snapshot
(`/prompt-version`), the `CHANGELOG.md` entry, and the sync obligations of the family they touch
(a new variant is registered as a mirror of its master and audited by `/sync-check` like any other).
Anything outside these skills is hand-editing a prompt file, which is never allowed.

## Testing is mandatory — a change is not DONE until tested

**Testing is not optional — a change is not DONE until tested.** A change is NOT done when the
files are edited/deployed — only when it has been TESTED and confirmed working, with overall
sanity intact. Never report a prompt/agent change as "done", "fixed", or "confirmed" until you
have actually tested it.

### The word "fixed" requires a call id. No exceptions.
**You may not write "fixed", "done", "resolved", "working", or "confirmed" about any behaviour
change unless you can name the live call that proves it** — a uuid, and the specific line or tool
argument in that transcript which demonstrates the new behaviour. Deploying is not fixing.
Read-back verification proves the prompt SHIPPED, never that the bot BEHAVES. Static checks,
diffs, `agent_args` audits and "verified present in the live instructions" are all necessary and
none of them is evidence of behaviour.

If you have not called it, the only permitted words are **DEPLOYED, NOT VERIFIED** or
**VERIFY-PENDING**, and they must appear in the same breath as the change — in the changelog entry,
in the commit message, and in what you tell the user. Writing "fixed" for four untested edits and
then discovering it later is worse than saying "untested" at the time, because the user has already
acted on the claim. **When several fixes ship together, each one needs its own call id.** One
passing call does not verify the other three; say which are proven and which are not, per fix.

### "Intermittent" is not a result. It is an unfinished fix.
**Never report a behaviour as "works sometimes", "flaky", "intermittent", or "runtime adherence" and
stop there.** That is a description of a defect, not an outcome. If the same prompt, on the same
error, with byte-identical tool results, produces the right line on one call and the wrong line on
the next, the fix is not good enough yet — and the reason is almost always that **the wrong output
is still available to the model.**

### FIRST localize the cause. The ladder below is a list of REMEDIES.

**Rungs 1-5 are cures for one disease — the model declining to follow a rule it was given. Applying
one before you know that is the disease is how you make a bug worse.** Do D1-D3 first, every time.
On 2026-09-23 the landmark turn was "fixed" twice without them: once by a theory about why the model
skipped, once by moving the constraint into the tool schema (rung 4). The second attempt shipped a
regression — the model filled the required parameter falsely and the skip arrived carrying a claim it
had not happened. Both were remedies for a disease the bug did not have.

**D1 — Count how many times the right branch has EVER been taken.** Pull every call where the
condition actually occurred and count. **`0/N` is not flakiness — it is unreachability**, and no
sentence will fix it: either the branch's trigger never arrives (a tool-error string the model is not
given), or a dangling label means the rule cannot bind to it, or a nearer competing line always wins.
On 2026-09-01 this count turned "the already-applied line is intermittent" into "the model has never
once received the error name" — 8/8, then 9/9 with the mapping in the tool description (D52, D51).
Any other ratio: continue to D2, and **do not call it adherence yet.**

**D2 — Segment by input. An aggregate ratio lies.** Split those calls by every candidate
discriminator — the value or SHAPE of each injected variable, the shape of each tool result, which
earlier branch was taken, language, direction — and compare the rate in each group. **A near-clean
split means this is NOT adherence: it is a condition evaluating correctly on an input you had not
identified.** Stop the ladder and go read that condition; the rungs below cannot help you. On
2026-09-23 the landmark turn scored **6/16** — textbook "mixed, therefore adherence" — and one split
by `${location}` gave **2/12** where it carried an area+pin against **5/6** where it did not. That is
a branch condition, and it had already survived three adherence remedies.

**D3 — If the step is governed by a guard, read the guard before concluding disobedience.** A step
that did not happen may have been correctly SKIPPED. For every skip / skip-unless / "only when"
clause, ask: **what is the WEAKEST value that satisfies this as written, and is that value routinely
present in the inputs?** Two smells that this is your bug: (a) the field the guard tests is also named
elsewhere as the destination the captured value is written to, so the storage slot doubles as the
evidence slot; (b) the condition is phrased by vibe — "hold", "have", "on record", "point at" —
rather than by type. Fix the test, not the volume of the rule: name the weaker fact and exclude it,
define the stronger fact by type, and make any write into the tested field one-way (analyser D95).

**Only when the behaviour is still mixed WITHIN a single input segment is it adherence.** Then:

The escalation ladder, in order. Do not stop before the end of it:

1. **Grep the bot's wrong output verbatim against the whole prompt** (analyser D50). A hit inside a
   sample conversation is the cause, and it is proof, not a theory. Fix the demonstration.
2. **Find the competing instruction and delete or scope it.** A prohibition sitting next to a
   requirement licenses the model to obey the prohibition. Two rules that can both be "followed"
   means the model picks — and it will not always pick yours.
3. **Remove the wrong option instead of forbidding it.** This is the one that actually works. A
   generic fallback line that makes a factual claim ("कोई तकनीकी दिक्कत है") will be chosen for
   cases it is false about, however loudly you forbid it. Either give every case its own mandatory
   line with NO general default, or rewrite the default so it asserts nothing that can be false.
   **Make the worst case truthful rather than trying to make the wrong case unreachable.**
4. **Move the decision out of prose.** Tool parameter descriptions, `required` fields, enums, and
   payload templates are read at the moment of use and are far stickier than rules paragraphs. A
   constraint expressible in the tool schema belongs in the tool schema. **Known failure mode — check
   before reaching for this:** a required parameter constrains what the model SAYS, not what it DID,
   so it only enforces when the model cannot produce a plausible value without doing the work.
   `profile_id` qualifies — it comes from a prior tool result. A landmark, a pin, a "yes I read the
   disclosure" never will: the model types a value and the skip is now laundered behind a claim that
   it did not happen, which is harder to detect than the plain miss (D91, D95).
5. **Only if 1-4 are genuinely exhausted** may you escalate to the platform — and then you must
   state exactly what you tried, what the evidence is, and what change you are asking for. "The
   model ignores it" is not an escalation; "the same tool result yields two different lines and here
   are both call ids" is.

**Never add a third wording of a guard that has already failed twice.** Two failures of the same
prohibition is the signal to change mechanism, not volume. Adding emphasis to a rule the model has
already ignored twice makes the prompt longer, more contradictory, and no more correct (analyser
D25, D47, D49, D50). **Inbound bots are testable** (corrected 2026-09-02): PATCH the inbound agent
with an integer `out_did`, then `POST /api/call` with the inbound agent as `agent_id` and the tester's
DID as `to_number`; the inbound bot looks up the caller's number, so inbound test data goes on the
tester's number. Only where a bot genuinely cannot be called (telephony down, no voice for the
language), do the best available verification (post-deploy transcript review + static sanity) and
explicitly mark the residual **VERIFY-PENDING**: never claim done/confirmed on an untested change. Revert on any regression (see `/prompt-version`).

### Test EVERY variant — never extrapolate (recipe-for-disaster rule)
**"It works for Hindi, so Kannada is fine" is a recipe for disaster.** A change verified on ONE
bot/language/direction is NOT verified on its twins. Every affected variant is tested
**independently** — Hindi AND Kannada, outbound AND inbound, KKB/DKB/Maya separately — even when the
edited logic is "identical agnostic content". Runtime adherence, ASR, and TTS differ per language;
a mirrored edit can land differently. Static/sync verification is necessary but never sufficient in
place of a live test of each variant.

### The three testing tiers (mandatory for every bug fix / change)
A fix is not done until it passes all three, in order:

1. **Tier 1 — Fix verification (did the bug get fixed?).** Reproduce the EXACT reported failure and
   confirm it no longer occurs, on each affected bot variant, in a real call transcript (not "looks
   fixed"). No transcript, no claim.
2. **Tier 2 — Blast-radius regression (did the fix break anything adjacent?).** A fix can break its
   neighbours. Enumerate what the change could have affected — the same section, the shared agnostic
   logic, the sibling language/bot that received the mirrored edit, the tool payload it touches — and
   run targeted tests around those areas on each variant. This is the step that catches "fixed X,
   silently broke Y".
3. **Tier 3 — Daily general regression (standing check).** A full regression suite (100+ test cases
   across all bots) runs automatically **once a day as a scheduled cloud task that survives the
   developer's machine being off**, catching drift/regressions since the last run. Critical findings
   are surfaced and (email-digest phase) mailed to the specified addresses. See
   `raya/regression/` for the suite + the scheduled worker.

Never skip a tier, and never collapse Tier 1/Tier 2 into a single happy-path call.

## How to report back (keep it short)

Parth's standing instruction (2026-09-02): **the reports are too long and too hard to follow.**
Simple language, bug-fix facts only. Structure every status reply as:

- **Fixed** — one line per bug: what was wrong → what changed. Name the call id that proves it.
- **Failed / still open** — one line each, with the call id where it failed.
- **New bugs found** — one line each.
- **Next** — one line.

Rules:
- No preamble, no recap of what I did to investigate, no narrating the method.
- A table only when it is genuinely a list of items with the same 2-3 fields.
- Don't explain the mechanism unless asked. Don't quote the prompt unless the wording IS the fix.
- One spoken line quoted per bug, maximum — and only when the exact words matter.
- Don't re-explain platform limits (memory unreadable, one tester DID, error body invisible) every
  time. State them once when they first block something; after that just say "blocked, see above".
- Keep "verified" vs "not verified" — that rule stands (see the call-id section above). Just say it
  in fewer words.

**Write for someone who is not a prompt engineer** (feedback from teams using the tuner, Oct 2026:
"whatever it says flies over my head"; the people who will run it are programme staff, not
specialists). This applies to every skill's report, to every user, every time:

- Use the words of the call, not of the tuner: "the bot told the caller their details were saved, but
  nothing was saved" — not "D115 false-success on create_job with empty tool_calls".
- Do not use these words to a user unless they used them first, and if one is unavoidable, explain it
  in five words: agnostic / specific, payload, enum, adherence, obligation, axis, tier, D-number,
  guard, fixture, sync family, divergence registry, read-back.
- Say what the person can do next, in one line, as a sentence they could type ("say 'run the Smoke
  cases on the Marathi bot'"), not as a slash command alone.
- Show the evidence they can open: the sheet row, the call id with its console link, the two or three
  prompt lines that changed (before → after). A little visibility of the prompt helps people trust and
  question a fix; the whole prompt does not.
- Never leave a report that only lists possibilities ("may be the schema, may be the data"). Make the
  call that decides, then report what it showed (`/bug-fix` → four habits).
- End with what is still open from before, so nothing reported earlier silently disappears.

## Feedback-loop operating sequence (from the sheet — don't ask to be re-told)

When processing reported bugs from the tracker, run this fixed order (full detail in `/bug-fix`):

**find → root-cause each against its real call transcript → classify → fix only genuine prompt gaps → propagate to sibling bots where the same bug is present → verify nothing broke → deploy → mark the sheet → repeat → summarize LAST.**

Two non-negotiables:
- **No fix without a transcript.** Never edit a prompt off a sheet report, a hunch, or a static/analyser finding alone — pull the actual call, confirm the bug, understand the root cause. If no recent call reproduces it, don't fix; ask for the reproducing call uuid.
- **On deploy, flip the sheet status to `Fixed for UAT`** (= deployed, ready for the user's acceptance test) — never leave a deployed fix marked `Open`. Backend/runtime causes → `Flagged - Backend Issue`; no-repro → keep `Open` + request the call. `Fixed for UAT` ≠ *confirmed* — don't claim confirmed until a POST-deploy transcript shows the corrected behavior.

Not every reported bug is a prompt bug — **push back before fixing; sometimes there is no bug.** Root-cause every report against BOTH the real transcript AND the call's **input args** before touching a prompt. Distinct non-prompt causes to name and PUSH BACK on rather than "fix":
- **User/data input error** — the args were sent wrong (job list in the wrong field, malformed/missing values, mis-mapped campaign `agent_args`). The prompt is fine; the inputs weren't. Say so; make no edit. *(2026-07-31: a "new profile, apply failed" on kkb-hi-signals was actually the jobs sent in `contact_memory` instead of `${recommendations}` — a user mistake, not a bot bug. Every working call carries jobs in `recommendations`.)*
- **Backend** (placeholder/bad job inventory, API 4xx/5xx, region-specific endpoint behavior) is NOT prose-fixable: escalate for a platform fix, don't experiment on the live flow.
- **Apparent runtime tool-adherence** (the model not following an instruction the prompt already states clearly, e.g. `get_profile` not firing) is not fixed by piling on more prose, which regresses (analyser D25). Diagnose first (D1-D3 in *Testing is mandatory*: it is often a condition evaluating on an input you had not identified), then walk the remedy ladder; escalate to the platform only when rungs 1-4 are exhausted, with the call ids.

Only genuine prompt gaps get a prompt edit. When the inputs were wrong, say "the prompt is fine, the inputs were wrong" out loud instead of editing. (A proactive safeguard the user explicitly asks for — e.g. an empty-`${recommendations}` fallback line — is a chosen feature, not a blind fix, and is fine to add.)

The tracker tab is **`All Issues`** (id `1cqT9EVk_vap16wJ3fQM7txLklf-kbMDHdYWsiHImbHU`). If the sheet key at `~/Downloads` is TCC-blocked, decode it from `kaam-ki-baat/.env.local` (`GOOGLE_SERVICE_ACCOUNT_JSON_BASE64`) into `secrets/gsheets-sa.json` (git-ignored).

## Push by default (this repo is PUBLIC)

**Every commit is pushed to GitHub straight away.** `git config core.hooksPath .githooks` (set once per
clone) installs two hooks: `post-commit` pushes the branch in the background (log:
`.git/autopush.log`; skip once with `NO_AUTOPUSH=1 git commit ...`), and `pre-push` runs
`scripts/push_guard.py`, which BLOCKS the push if the new lines carry a secret from `raya/.env` or
`secrets/`, a key-shaped string, a Raya tool snapshot, or a phone number that is not one of our test
lines and is not already public. Pushes go out as `parthekstep` (`gh auth token --user parthekstep`).

- When the guard blocks: mask the number at the source (`XXXXXX1234`) and amend; never `--no-verify`
  unless the finding was reviewed as a false positive.
- Never paste a real caller's or colleague's phone number into a changelog, report or fixture; cite the
  call uuid instead, and use the `9188888888xx` block for fixtures.
- History before 2026-10-08 was pushed after a scan: two third-party numbers were masked across the
  165 unpushed commits (so their commit ids changed; old ids in chat history no longer resolve).

## Deploying to live agents (Raya) + the feedback loop

The prompts run on **Raya Voice AI** (LitWiz Labs). Config + tooling live in `raya/` and `scripts/`:

- **Deploy** a prompt to its live agent: `scripts/raya_deploy.py` via the Raya **API PATCH**
  (`PATCH /api/agent/{id}` with `{"instructions": <file>}`), verified against the PATCH
  response. Proof that a deploy landed is the PATCH read-back, never a later GET: the GET reads most
  prompts now but can still return empty or flaky content.
  Each agent's uuid is in `raya/agents.json`; deploys are recorded in `raya/deploy-history.md`.
  Secrets (base URL + token) live in git-ignored `raya/.env`.
- **Reconcile BEFORE every edit** (mandatory — the live agent can be AHEAD; the team maintains the
  real job inventory / `job_id`s directly on the console). `scripts/raya_deploy.py diff <target>` shows
  who's ahead (GET now reads most conversation prompts; if flaky/empty, use `/raya-reconcile`'s browser
  sha-boolean). If Raya is ahead, adopt live into the repo with `scripts/raya_deploy.py pull <target>`
  (two agreeing GETs, snapshots first) and commit it BEFORE editing — never edit a repo file behind live,
  or you clobber live-only content (e.g. overwrite a real inventory with placeholders → `apply_failed`).
  `deploy` refuses any prompt still carrying placeholder `job_id`s / a `[PLACEHOLDER SAMPLE DATA]` flag.
- **Feedback loop** (`/bug-fix`): read the Consolidated Feedback Tracker (Google Sheet) via
  `scripts/gsheets.py` (service-account Sheets R/W), pick OPEN issues, temporal-check them
  against the changelog, ground each in the real Raya call transcript
  (`GET /api/call?agent_id=…` → `GET /api/call/{uuid}`), fix only genuine prompt gaps
  (via `/update-prompt`), deploy, and write the status back to the sheet. Cross-agent
  propagation of an agnostic fix is gated by an email approval.

Note: `raya/`, `scripts/gsheets.py`, and `scripts/raya_deploy.py` are the self-contained
deploy/feedback layer — nothing here changes prompt *content*; content edits still go through
`/update-prompt`.
