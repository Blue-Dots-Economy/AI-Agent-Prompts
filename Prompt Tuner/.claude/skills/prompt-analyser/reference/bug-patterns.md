# Bug-Pattern Catalog

The distilled, reusable form of every failure class we've hit across KKB, DKB, Maya (and the
Purple Dots review). Each entry: **Symptom** (observable) → **Root cause** → **Detection
heuristic** (what to look for in a prompt) → **Fix direction** → **Seen in**. Apply every
heuristic during a sweep. When a new class appears, add it here (see SKILL.md → "Growing the
skill").

The recurring meta-lesson across almost all of these: **a rule being present in the prompt
does not mean it holds at runtime.** A competing action, an example, or skip logic can quietly
override it. Always check *why the rule would fail*, not just whether it exists.

## Index (read this first)

Every entry below, grouped by the kind of failure. Sections A-G further down are the original
families; from about D42 on, entries were numbered in the order they were found and sit wherever
they were added, so use this index, not the section headings, to sweep by family. Jump to an entry
with `grep -n "^#\+ D95\b" bug-patterns.md`. D89, D90 and D91 are each used for two different
entries (marked "2nd" here): cite them with their short name, e.g. "D91 (required parameter)".
New entries take the next free number (D124 onward) and get a row here.

**Flow, branches and guards (steps skipped, wrong branch, a guard that tests the wrong thing)** (50)

- A1: Mandatory step skipped because the competing action isn't forbidden
- A2: Skip-forward pressure with no backpressure
- A3: Overlapping/adjacent phases conflated
- A4: Latent contradiction inside one branch
- A5: Re-collecting data already available
- A6: Confirmation/interest asked before the content it refers to
- A7: Multiple questions/steps chained into one turn (no wait-for-answer)
- A8: Forceful one-branch mandate bleeds onto the other fork value (no decisive router)
- D5: Modality leak (outbound bot invites callbacks)
- D7: Inbound get_profile fork not hard-gated (fetch skipped / deferred / replaced with a permission-ask)
- D9: Skip-if-known field re-asked at the apply gate despite being on the fetched profile
- D10: Mandatory end-of-call step skipped because the closing script is jumped to directly
- D14: Yes/No gate advanced without capturing the owner's clear response (DKB)
- D15: Apply failure dead-ends the seeker (no recovery, or burden shifted to them)
- D18: Branch router overridden by a lopsided concrete-vs-abstract next step (new_seeker="yes" still fetches profile)
- D19: Required spoken action referenced instead of inlined ("say the X line - see Y section") -> not executed
- D21: New-caller pre-apply fields skipped when the caller rushes to apply
- D22: Variable-gated branch ignored - model follows structural dominance, not the ${var} value
- D23: Always-ask question folded into a combined multi-field prompt -> never fires
- D24: Outbound-lineage residue in an inbound prompt contradicts the silent-fetch router (permission-ask / outbound ...
- D35: `draft` profile handled inconsistently: known fields re-asked AND/OR consent skipped
- A9: A new conditional branch is silently defeated by a surviving "ALWAYS the same X" rule elsewhere
- A10: A new behaviour that DUPLICATES an existing one, a turn apart, is silently dropped
- D43: No-Match Fallback fires while unshown jobs remain (call ends early with stock in hand)
- D48: A preference is promised back to the caller with no field to store it in
- D49: "None of these suit me" collapses into No-Match while most of the list is still unspoken
- D51: A rule points at a branch label that no longer exists in the section it names (and often means something else ...
- D55: The model fills a gap the prompt left open (four bugs, one cause)
- D56: A completeness claim gated on a count the model cannot verify at the moment it speaks
- D58: A rule that cannot be satisfied honestly gets satisfied dishonestly
- D62: An evidence whitelist added to stop a branch being GUESSED also blocks the one case where it is KNOWN
- D64: A "CLOSED SET" of allowed sentences that enumerates only some branches deletes the others
- D70: A rule triggered "after X is captured" never fires when X is only-if-missing
- D75: A branch test that never names WHICH field it reads, satisfied by a different field that happens to carry the ...
- D76: A rule that requires the model to maintain a RUNNING COUNT across turns. It will lose it
- D78: A guard stops the line it names, and a DIFFERENT line carries the same claim
- D79: a guard stated only at the top of the prompt loses at the point of use
- D80: a decision table's catch-all row asserts a cause the specific case contradicts
- D82: the point-of-use rule (the pattern behind nine of ten bugs found on 2026-09-08/09)
- D88: a step gated on "first call" is dead for every caller who has a profile
- D89: a spoken line that promises finality kills every turn after it
- D94: a shortening rule for one object gets applied to a different object whose value matches the example
- D95: a skip test that accepts a WEAKER fact than the one it is guarding
- D96: a pre-close checklist that names ONE owed item silently excuses every other owed item
- D97: a prohibition scoped to one KIND of thing silently permits every other kind
- D98: an unfilled promise with no MANDATORY escape gets filled with invention
- D101: a validation rule whose remedy assumes the input is well-formed, or ends in "accept whatever comes"
- D105: a hardcoded list was replaced, but the prose around it still describes the old list
- D110: a guard that tests an injected variable is re-run after the caller answers, so the question loops
- D114: a routing keyword appears inside the WRONG row's exception text

**Repetition and loops** (4)

- B1: One-time utterance/consent fired repeatedly
- B2: Forbidden waiting/narration line leaks
- B3: Unbounded re-ask on a hard-gated field dead-ends the call (and the caller's own question is never answered)
- D27: Apply-failure turn re-speaks the apply bridge / re-fires apply_job on the same already-failed job

**Tool calls, payloads and results (missed or wrong calls, payload values, backend replies, failure lines)** (40)

- C1: Silent terminal tool calls dropped (no anchor, no gate)
- C2: Tool referenced but not declared
- C3: Payload field/data bug
- C4: Fixed-param / enum integrity
- C5: Spoken line stands in for a tool call that never fires (fabricated result / hallucinated success / ...
- C6: Fetched response never consumed (no field map, no "use what's present" rule)
- C7: Fetched identifier not bound -> downstream re-creates it (duplicate write)
- C8: Result set presented in given order; known ranking signals not applied
- C9: Placeholder / sentinel field value spoken or acted on as if real
- C10: Tool 4xx with a well-formed id = backend/endpoint issue, NOT prose (and endpoint differences across twins may ...
- D11: Repeat apply by a NEW caller in one call re-mints the profile (duplicate) + re-gathers details
- D12: Role-name variant / job-family not matched -> false "no jobs" + inconsistent categorisation
- D13: Out-of-city jobs surfaced in the first batch to a caller who stated their own city
- D16: Empty get_profile misread as profile-exists -> apply_job without create_profile
- D17: create_profile / get_profile phone double-prefix (+91+91…)
- D20: Bundled create_profile+apply_job -> tool call narrated as text + hallucinated apply success
- D25: Anti-narration / "say only X" edit near a mandatory tool call suppresses the tool itself
- D28: apply_job sent create_profile's numeric top-level `id` instead of the `profileId` UUID -> 404 "Invalid or ...
- D29: Greeting bundled with a silent fetch in ONE turn -> the model narrates the fetch OR skips it (un-bundle into ...
- D30: apply_job stripped the job_id UUID hyphens -> 404 "Job not found"
- D31: New-caller `create_profile`->`apply_job` batched in one turn -> `apply_job` sent an EMPTY `profile_id`
- D33: Raya prunes a literal empty-object `{}` from `payload_template` -> a required object field arrives `undefined`
- D36: Ranking pads the batch to N with irrelevant-role jobs instead of filtering to relevant
- D37: Multi-profile fetch: bot applied to `items[0]` (a stale draft) while a live profile sat later in the array -> ...
- D38: Signals dropdown field sent an off-enum value -> 400 INVALID_ITEM_STATE
- D39: Signals write fails / duplicates the profile: double-prefixed phone, or non-Latin payload values
- D40: `create_profile` omits `location` -> new profile is created `draft` (not live) -> `apply_job` PROFILE_NOT_LIVE ...
- C11: DKB create_job not emitted on the post-consent turn (D25 runtime tool-adherence; language-variant-specific)
- C12: Tool unmapped on a migrated backend kept as a "backend dependency" stub -> dead step / fabrication risk
- D47: Every tool failure is spoken as "a technical problem on our side", including the ones that aren't
- D52: A rule branches on a tool-error string the conversation model may never receive
- D59: "items[0]" works until the caller's first item isn't the one you meant
- D65: A licensed spoken line that is indistinguishable from the action becomes a substitute for the action
- D91: `create_profile` on a caller who already has a record mints a duplicate instead of fixing it
- D93: an empty tool result gets answered with the nearest "we have nothing" line
- D91 (2nd): a REQUIRED tool parameter can be asserted falsely; it constrains what the model SAYS, not what it DID
- D99: a tool description that states an OPERATION instead of a TARGET FORMAT, on an input whose shape varies
- D107: a default search value for undecided callers gives every undecided caller the same wrong jobs
- D111: an enum list in the prompt disagrees with the tool schema, and the prompt wins
- D115: "after the tool completes, say done" with no failure branch

**Inputs, variables and templates (`${...}`, `[slot]`, memory, campaign args)** (17)

- D32: Memory block used as a substitute for `get_profile` -> premature name/role + fetch never fires
- E3: Memory-injection block missing (repo standing rule)
- G1: Variable placeholder precedes its label in a binding phrase (garbles after interpolation)
- G2: A literal `${...}` written as an EXAMPLE becomes a phantom declared agent argument
- G3: A `[bracketed]` placeholder in a spoken line makes the MODEL do the substitution (spoken aloud, wrong value, or ...
- G4: `memory_enabled` silently overrides the `${contact_memory}` passed in `agent_args`
- D42: A truncated `${recommendations}` payload makes the bot go silent, invent a role, or drop the call
- G6: A guard rolled across bot families references a variable that family does not have
- D53: An input variable the prompt promises to speak back is silently suppressed by a guard about something else
- D54: A rule gated on stored memory, on a platform where memory is neither settable nor readable
- D66: An ALIAS for an input variable makes every test of that variable silently false
- D67: A spoken template with the slot INSIDE it makes the raw variable token the default utterance
- D68: An input the campaign SENDS that the prompt never names is an input the bot cannot use
- D73: An emptiness test that enumerates the placeholder STRING and NULL, but not the ABSENT argument
- D77: The `[slot]` markers a spoken template is BUILT FROM get read out as words
- D89 (2nd): an upstream field RENAME silently inverts a flag-driven gate
- D100: a slot defined by the TURN that filled it goes stale when the caller updates the value later

**Examples in the prompt (sample calls and example values that teach the wrong thing)** (12)

- E1: Few-shot examples contradict the rules (incl. cross-branch opening bleed)
- D50: The prompt's own worked examples demonstrate the violation the rules forbid
- D57: The samples depict a tool call as narration, so the model narrates it instead of calling it
- D63: A sample conversation whose CONTEXT omits the field a branch keys on demonstrates the wrong branch
- D74: A sample conversation whose Context line defines a variable in terms of itself, and whose speech line then ...
- D81: a prohibition that prints the forbidden output supplies it
- D81b: an EVIDENCE NOTE that quotes the bad output is the same trap as the prohibition
- D83: a concrete value printed beside a template becomes the output
- D87: a reduction rule demonstrated only on single-token inputs teaches "keep the first one"
- D102: a branch that is never demonstrated is never taken, and the demonstrated branch's VALUES get reused as fabrications
- D109: a worked example's input value is supplied as the real value when the call's input is empty
- D112: example VALUES in the prompt are copied into calls where the real value is absent

**What the caller hears (vocabulary, numbers in words, script, gender, internal words spoken)** (18)

- D1: Hard/Sanskritised vocabulary despite a "simple language" rule
- D2: TTS number/date/time/money not spelled as words
- D3: Script separation: conversation vs payload
- D4: Voice-gender inconsistency
- D6: Symbol/punctuation voiced literally (e.g. "/" read as "slash")
- D8: Internal technical term ("profile") spoken to the caller
- D26: Place/city names spoken inconsistently or mispronounced (no canonical-spelling pin)
- D34: Platform `hold_message` (spoken filler on a tool call) narrates a step the prompt says is SILENT
- D44: Caller-directed verbs hardcoded to the BOT's gender (a feminine-voiced bot misgenders every male caller)
- D45: An internal structure name spoken aloud to the caller ("this inventory", "the database")
- D61: A suppression rule with no replacement line falls back to the thing it suppressed
- D69: An identifier with no rule of its own falls to the "numbers in words" default and is spoken as a quantity
- D71: A script/spelling rule backed by a CLOSED LIST converts what is on the list and passes the rest through verbatim
- D72: An English field LABEL inside a spoken template is read out to the caller
- D84: "say it in words" gets satisfied by re-rendering the digits in the target script
- D92: a digit-by-digit spoken number loses a repeated digit unless the count is asserted
- D104: "reassure them, in your own words" turns a forbidden threat into an unkeepable promise
- D113: a stage direction or "stay silent" instruction is spoken aloud

**Consent, disclosure and safety** (10)

- D41: doubts question and apply-consent bundled in ONE turn -> a "no" (= no doubts) is read as a refusal to apply -> ...
- D46: Consent captured and the line dropped in the same breath: the caller cannot learn what they just agreed to
- E2: Consent handling: multiple gates, single-ask, hard-stop on decline
- E4: Guard sections thin or absent
- D60: A mandated line that bundles a disclosure with a question loses the disclosure
- D86: a flag the prompt tells the model to IGNORE is a consent nobody checks
- D103: a mandated disclosure that lives in ONE turn is lost on every exit reachable before that turn
- D106: consent heard at one step but only written at a later one is lost whenever the call ends in between
- D108: an offer that ends on a statement, plus a "clear yes" list containing a backchannel, records acknowledgements ...
- D121: a safety statement inside an ordinary answer is acknowledged only for the surface need

**Size and languages (translation, mirrors; run the scripts)** (7)

- D116: the prompt is past the size this bot can handle, so it stops calling tools without any error
- D117: a mirror's English rules still tell the bot to speak the master's language
- D118: a same-script mirror keeps master-language text that no script check can see
- D119: a defect in the master is copied into every language
- D120: a line with no equivalent in the target language becomes two identical lines
- D122: a proper noun changes in translation
- D123: the translation is correct but too formal for the caller

**Diagnosis and test method (not prompt defects; read before concluding)** (5)

- G5: A diagnostic prompt that lets the model JUDGE its input produces false negatives
- D50 addendum (2026-09-03): "it's model adherence, don't add prose" is a triage claim that must be GREPPED before ...
- D85: identical output across a CHANGED prompt means the source is not the prompt
- D90: "the caller's identity is fixed by the dialled number" is worth re-testing before you call a state unfixturable
- D90 (2nd): a redirected log that looks empty is buffering, not a dead process

Cross-language parity between a master and its mirrors: section F (pointer to `/sync-check`).

---

## A. Flow & sequencing

### A1 — Mandatory step skipped because the competing action isn't forbidden
- **Symptom:** a step the prompt calls "mandatory" is intermittently skipped; the agent jumps to a later phase.
- **Root cause:** the prompt says what to DO but never forbids the rival action that fires instead. Positive reinforcement alone loses to a strong competing default.
- **Detection:** for each "must / mandatory / always" step, ask "what else could the model do at this moment, and is that explicitly forbidden here?" If there's no **negative gate** ("X may NOT run / begin until Y has happened"), flag it. **Strongest signal:** a branch whose paths point to a *separate top-level section* (its own `##` heading) rather than to an inline action — the model treats that prominent section as the default next thing. Compare to a sibling agent whose equivalent branch works and check whether it keeps the action inline.
- **Fix direction:** add a hard negative gate at the top of the competing action. **But a negative gate can still lose if the competing action is a prominent standalone section** — the reliable fix is to **delete that section and fold its action inline into the branch paths, so there is nothing to jump to** (mirror the sibling agent where the branch already works).
- **Seen in:** Maya 2026-07-08 (Experience Capture ran before `get_profile` until it was forbidden as the first post-greeting action); Maya 2026-07-13 (the `new_seeker="no"` branch kept bypassing `get_profile` through Step-0 removal, standalone-section deletion, AND hard gates — **none of these was the real fix**; the actual root cause was a variable-interpolation ordering bug, see **G1**. Removing the competing section is still good hygiene, but it was not what fixed this — a reminder not to declare victory on a plausible structural change without confirming it on a live call).

### A2 — Skip-forward pressure with no backpressure
- **Symptom:** phases/steps that require active work get treated as optional; agent races to the end.
- **Root cause:** aggressive SKIP-AHEAD / ORDER-FLEX / "move silently to the next phase" / "never retroactively verify" logic, with no counterbalancing "you must still do X before proceeding."
- **Detection:** count the skip-enabling rules vs the must-do gates. Heavy skip logic + few hard gates on the mandatory/terminal steps = flag. Especially dangerous on silent tool phases (see C1).
- **Fix direction:** pair every skip rule with an explicit exception list of steps that are never skippable.
- **Seen in:** Purple Dots review (Solution Enablers + Phase 4-5-6 tool calls skipped under `[SKIP-AHEAD]`/`[ORDER-FLEX]`).

### A3 — Overlapping/adjacent phases conflated
- **Symptom:** the agent believes a later step is "already done" because an earlier step captured something similar.
- **Root cause:** two sections capture conceptually overlapping content (e.g. Phase 2 "challenges/barriers" vs Phase 3 "missing enablers"), and NO-REPEAT/SKIP logic then marks the later one satisfied.
- **Detection:** look for two sections that both capture "what the user lacks / needs / barriers." Check whether the prompt draws a sharp line between them and whether the later one has its own must-run gate.
- **Fix direction:** state the distinction explicitly and give the later step an independent gate.
- **Seen in:** Purple Dots review.

### A4 — Latent contradiction inside one branch
- **Symptom:** behaviour flip-flops on the same input.
- **Root cause:** a section's header says one thing and its body says the opposite (e.g. header "caller already has a profile" vs body "MANDATORY IF PROFILE DOES NOT EXIST").
- **Detection:** read each branch header against its body; flag any header/body or intra-section contradiction. Also flag the same rule stated with different thresholds in different places.
- **Fix direction:** reconcile to one statement.
- **Seen in:** Maya 2026-07-05 (contradictory `new_seeker="no"` branch).

### A5 — Re-collecting data already available
- **Symptom:** the agent asks for a field (age, gender, location…) it already has from the fetched profile / prior context, making the call feel like a form.
- **Root cause:** the data-collection step is unconditional ("always ask age and gender") and never checks the fetched profile / known context first.
- **Detection:** for each "always ask / must collect" field, check whether the prompt first says "skip if already present in the profile/context." An unconditional MANDATORY/HARD-BLOCK ask, with a profile fetch upstream, = flag.
- **Fix direction:** gate each ask on "not already known — asked in this call OR present in the fetched profile"; ask only the genuinely missing fields.
- **Seen in:** Maya 2026-07-13 (age/gender re-asked for returning `new_seeker="no"` seekers whose profile already had them).

### A6 — Confirmation/interest asked before the content it refers to
- **Symptom:** the agent asks "are you interested in these?" *before* actually presenting the options, then presents them, then asks again — a confusing double-ask; the first ask has nothing concrete behind it.
- **Root cause:** an ordering rule mandates a confirmation turn *before* the listing turn (ask-before-show), often with "do NOT list yet" guards.
- **Detection:** look for a confirm/interest question that is required before the content (jobs/options/details) is shown. Flag any "confirm interest → then list" ordering, and any "do NOT list yet" gate that pushes the ask ahead of the content.
- **Fix direction:** present the content (with the details the user needs to judge), then ask for interest/selection. A brief lead-in is fine; a standalone interest question before the content is not.
- **Seen in:** Maya 2026-07-13 (Turn 1A asked "इस तरह का काम देख रहे हैं?" before Step 2 listed the jobs).

### A7 — Multiple questions/steps chained into one turn (no wait-for-answer)
- **Symptom:** the agent asks two or more distinct questions (or acknowledgement + question + a next-step question) in a single turn, "just keeps talking," and the caller can only answer the last one — so earlier answers (e.g. the role confirmation) are lost.
- **Root cause:** adjacent steps are described as flowing one into the next ("do X, then continue to Step 1") with no explicit "end the turn / wait for the answer" between them, so the model fuses them into one utterance. A voice channel needs a hard one-question-per-turn bound at each hand-off.
- **Detection:** wherever two askable things are adjacent (acknowledge→confirm→next-step, role-confirm→area, age→gender), check there is an explicit "STOP / wait for the answer / this is a separate turn" between them. "then continue to Step N" with no wait = flag. Also check examples don't model a fused turn. A non-question acknowledgement may ride with one question; two questions together may not.
- **Fix direction:** end each turn on exactly one question; add "wait for the answer; the next question is a separate turn"; keep transitions explicit at every step hand-off.
- **Seen in:** Maya 2026-07-13 (name-ack + role-confirm question + area question all fired in one turn — "…इसी तरह की जॉब्स देख रहे हैं? …किस इलाके…?" — so the seeker answered only the area and the role confirmation was skipped).

### A8 — Forceful one-branch mandate bleeds onto the other fork value (no decisive router)
- **Symptom:** a control-variable fork (e.g. `new_seeker` yes/no) routes to the WRONG branch — a branch written with forceful, unconditional-sounding "MANDATORY / NO EXCEPTIONS / the very next thing you say" language fires even when the variable holds the OTHER value. E.g. `new_seeker="yes"` (new caller) but the bot still asks the profile-permission question and calls `get_profile` (the "no"-branch mandate over-fired).
- **Root cause:** the forceful/mandatory wording on one branch is not scoped to its branch value, and there is no decisive up-front router that reads the variable FIRST and dispatches. The salient MANDATORY block dominates the weaker other branch. (Distinct from **G1**, where the value never binds — here it binds fine but the prose over-fires; distinct from **E1**, where an *example* bleeds — here it's the *prose*.)
- **Detection:** for any control-variable fork, check (a) a **DECISIVE ROUTER** at the top reads the variable FIRST and dispatches, naming each path's forbidden actions; (b) each branch's forceful/mandatory language is explicitly **scoped to its value** ("applies ONLY when X = …"); (c) the two branches are **equally forceful** — the "do NOT do Y" branch forbids Y as strongly as the other branch mandates it. Asymmetric forcefulness (one branch "MANDATORY/NO EXCEPTIONS", the other a mild "do not…") or a missing router = flag.
- **Fix direction:** add a decisive router (check the var first; state each path's forbidden actions + the rationale); scope the mandatory wording to its branch value; make the prohibition on the other branch as forceful as the mandate. Do NOT weaken the branch that was working.
- **Seen in:** KKB 2026-07-16 (`new_seeker="yes"` still asked "क्या मैं आपकी प्रोफाइल fetch कर सकती हूँ?" and called `get_profile` — the "no"-branch MANDATORY bled onto "yes"; fixed with a decisive router + scoping the mandate to "no" + a forceful "yes → fetch FORBIDDEN"); Maya 2026-07-16 (same latent risk — unscoped MANDATORY, no router — found and fixed the same way). **Meta:** the `new_seeker` fork has now failed in THREE distinct ways — binding (G1), example bleed (E1), prose over-fire (A8) — so when a control-variable fork misroutes, audit all three.

---

## B. Repetition & loops

### B1 — One-time utterance/consent fired repeatedly
- **Symptom:** a bridge line, a consent ask, or a confirmation is spoken/asked several times in one call.
- **Root cause:** a one-time action is attached to a per-entity loop ("do X once for each provider/job") **or to a multi-tool sequence** (bridge → `create_profile` → `apply_job`), so it re-fires at each entity/tool boundary. **A bare "say once" rule in prose is not enough** — the model still re-emits the line at the next tool call unless it is *also* told "once said, never again; say nothing between tools," and told to say it *only immediately before the tool, after all prerequisites are met* (not at an earlier consent moment while fields are still being collected).
- **Detection:** find every "for each …" / multi-entity action and every **multi-step tool sequence**, and check whether a spoken line sits at a boundary inside it. Confirm each consent/bridge line has (a) an explicit "say **once**", (b) a "once said, never repeat — stay silent between tool calls" bound, and (c) a gate that it is said only right before the tool. Multiple backend entities/tools + one human-facing line = high-risk. **Signal for the apply bridge specifically:** the bridge line spoken 2+ times, OR spoken before / instead of `apply_job` firing, is the tell — a flat "never repeat the bridge" prohibition is not enough without the causal mechanism. Grep the bridge rule for whether it ties saying-the-bridge to firing the tool: saying it ⇒ `apply_job` MUST be emitted the SAME turn; a second bridge attempt means call `apply_job` instead; repeating the line is never a stand-in for the tool call. Absence of that causal clause = flag.
- **Fix direction:** say the line once, immediately before the tool, after prerequisites; then loop/chain the tool calls **silently**; never re-emit between tools. Reduce the number of tools in the path where possible (e.g. no `create_profile` on the returning path) so there are fewer boundaries to trip on.
- **Seen in:** Maya 2026-07-08 (apply bridge spoken 3–4× per apply) and **again 2026-07-13** (bridge said at first consent *and* 2–3× more across the `create_profile`→`apply_job` sequence, despite a "say once" rule — needed the "never again / silent between tools / only-just-before-tool" bounds); Purple Dots review (share-consent asked per provider); KKB Hi+Kn outbound, 2026-07-22 (causal clause ported from Maya — the bridge is NOT the application; said ⇒ `apply_job` this turn; a second bridge ⇒ call `apply_job` instead).

### B2 — Forbidden waiting/narration line leaks
- **Symptom:** agent narrates a background tool call ("प्रोफाइल देख रही हूँ…") though tool calls are meant to be silent. **Turn-1 shape (highest-value):** a fixed opening line (the greeting) gets a fetch/lookup/wait narration clause **prepended, OR inserted mid/after it,** at turn 1 — e.g. "अभी आपकी जानकारी मिल रही है" before / around "नमस्ते".
- **Root cause:** the tool-call instruction leads with a data source that steers the model to narrate, and there's no explicit ban on waiting/fetch narration. Voice models narrate a background tool call to fill perceived **dead air** / to **acknowledge the action**. Crucially, **a control that BANS SPECIFIC PHRASES does not hold — the model invents an un-listed synonym each time (confirmed across THREE recurrences of this bug); a phrase list is inherently whack-a-mole.**
- **Detection:** for each background tool, check for an explicit "do not announce / no waiting line" rule. Flag any spoken line that describes fetching/looking up. **Source cue (check this FIRST):** an inbound greeting turn that contains ANY text before the greeting line, or an instruction telling the agent to speak "alongside"/"while" a silent fetch — that phrasing is what invites the narration, and it is the thing to fix, not just the resulting line. **Whack-a-mole cue (check the SHAPE of the control, not just its presence):** grep the turn-1 greeting rules for a phrase-list ban ("NEVER say X / Y"); if the anti-narration control is a **phrase list** rather than **(a) a turn-1 whitelist** ("the first spoken output is EXACTLY the greeting, nothing before/between/after"), **(b) a reframe of the tool as a silent, non-conversational system event,** and **(c) an all-position causal stop**, flag it as whack-a-mole-prone (a variant will slip it). **Also flag any sanctioned "I found your info"-type acknowledgement** (e.g. "आपकी जानकारी मिल गई") that is **not explicitly scoped away from the opening turn** — it can be cited as license to narrate the fetch at turn 1. Secondary: the ban must cover phrasing VARIANTS — perfective AND continuous verb forms ("जानकारी देख लेती हूँ" / "देख रही हूँ" / "चेक कर लेती हूँ") AND the internal noun "profile" in BOTH scripts — Latin "profile" AND native "प्रोफाइल"/"ಪ್ರೊಫೈಲ್" (a ban listing only "प्रोफाइल" leaves "profile" open, and vice-versa — cf. D8) — and a "get_profile is 100% SILENT" rule must back it up.
- **Fix direction:** **prefer fixing the SOURCE instruction that invites the narration, and prefer STRUCTURE over enumerating more banned phrases.** Replace a phrase-ban with: **(1) a turn-1 whitelist** — the entire first spoken output is EXACTLY one greeting variant, no token before/between/after; **(2) a system-event reframe** — the tool is a silent background system action, NOT a conversational turn (do not defend it with an unverified "no dead air" claim — just forbid narrating it); **(3) an all-position causal/category stop** covering BEFORE/BETWEEN/AFTER positions and bare fillers, not a phrase list; **(4) a positive exemplar** of a correct turn 1; **(5) subordinate any "FIRST action" tool-timing language** (in the router / tool rules) to "silent background step, never spoken" so it doesn't prime narration; **(6) scope any sanctioned acknowledgement to a LATER turn** so it can't license turn-1 narration. As a backstop keep "silent and internal" per-tool + one result message + the "profile" noun ban in every script (cf. D8). **Where the platform supports it, recommend a static/first-message field (a deterministic opening line) as the durable fix — an instruction-only control is probabilistic.** **CAUTION (D25/D29):** item (2)'s "silent system-event reframe" can over-suppress and stop the tool from firing. The safest structural fix when the SAME turn is being asked to greet AND fetch is to **un-bundle into two turns (D29)** — greeting turn, then a mandatory tool-only fetch turn — rather than making a single greeting-turn both clean and silently-fetching.
- **Seen in:** Maya 2026-07-08; DKB 2026-06-29 ("Tool calls are silent and internal"); KKB inbound Hi+Kn, 2026-07-22 (after "hello" the bot prepended "ठीक है, मैं आपकी जानकारी देख लेती हूँ" before the greeting; root cause was a get_profile rule saying "deliver the greeting **alongside it**" — first fixed at SOURCE by making the first spoken turn greeting-only with a silent fetch. An earlier phrase-ban of the narration line was a misdiagnosis and was REVERTED). **KKB inbound (Hindi+Kannada), 2026-07-22 — 3rd recurrence:** despite the source fix + two phrase-bans (a live-vs-repo reconcile confirmed the phrase-ban was live and still failed), turn 1 said "अभी आपकी जानकारी मिल रही है। नमस्ते…". The model kept inventing a new synonym past each banned phrase. Fixed **structurally** (validated by a 3-lens adversarial red-team before deploy): turn-1 whitelist + system-event reframe + all-position causal stop + positive exemplar + subordinating the router/get_profile "FIRST action" framing to "silent background step" + scoping the "आपकी जानकारी मिल गई" acknowledgement to a later turn. Recommended durable fix: a platform static/first-message field (pending LitWiz). **Lesson: for a fixed opening line, the reliable anti-narration control is a whitelist + system-event reframe + all-position stop + a positive exemplar — never a phrase list, and ideally a platform-level deterministic first message.**

---

### B3 — Unbounded re-ask on a hard-gated field dead-ends the call (and the caller's own question is never answered)
- **Symptom:** an engaged caller who has already agreed to the action is asked for one required field over and over — three, four, five times — and hangs up. `call_output` shows the caller engaged and jobs shown, with no record created and no application. The transcript is a loop: the bot's request, the caller saying something else, the bot's request again, often re-worded only trivially ("please tell me your name" → "could you tell me your name?").
- **Root cause:** two gaps compounding. (1) A field is a HARD BLOCK before a write (correctly — the write needs it), but nothing bounds how many times it may be asked, so the model keeps satisfying "you must obtain this" forever. (2) When the caller replies with a QUESTION instead of the field, the prompt has no rule to answer it first, so the model deflects and re-asks in the same turn, which the caller experiences as not being listened to. The caller is usually asking something entirely reasonable — how much the job pays — and gets it brushed aside twice before leaving.
- **Detection:** in transcripts, count consecutive bot turns requesting the same field; two is design, three or more is this bug. Cross-check `call_output` for engaged-but-nothing-written. In the prompt, for every HARD BLOCK on a field, look for (a) any cap on attempts, (b) any instruction about what to do when the field cannot be obtained, and (c) any rule to answer a caller question raised mid-gathering. Absence of all three is the signature. A statistical tell across an agent: many engaged calls and near-zero writes.
- **Fix direction:** bound it. Ask at most twice; if the caller asked a question, answer it in one short sentence FIRST and then re-ask once, worded differently; if the second ask fails, STOP, say plainly that the action cannot be completed without it and that they can call back, and close gracefully. Do not try to fix this by adding more insistent wording to the same request — that is the bug, not the cure. Note the gate itself is usually correct and must stay: the fix is an exit from the gate, not removal of it.
- **Seen in:** KKB Kannada legacy inbound, 2026-08-24, call `6b420bac` (296 s) — the name was requested five times while the caller repeatedly asked about pay; no `create_profile`, no `apply_job`, caller hung up. Across ~60 calls on that agent in the same period, `create_profile` fired **zero** times. Reported on the tracker as "missed asking details for new seekers", which is the opposite of what the transcript shows: the bot did ask, and could not stop. Fixed across the six prompts carrying the same name gate (KKB ×4, Maya ×2).

## C. Tool calls & payloads

- **Gate POSITION matters as much as gate bounds (2026-08-28).** A hard gate placed in front of the step that DELIVERS the value costs the whole call when the field cannot be obtained; the same gate placed after it costs only the write. Before making any field a precondition, ask what the caller loses if it is never obtained. In the KKB Signals Hindi location work this decided the design: location capture sits before the job list (the recommendations depend on it) but is capped at three turns and **every** terminal state — captured, open, or failed — still routes to the job list. A failed location capture is explicitly barred from triggering No-Match, a callback line, or a close. Contrast the name gate, where the write genuinely cannot proceed without the value, so the bound is on the ASKING and the graceful close is the honest outcome.

### C1 — Silent terminal tool calls dropped (no anchor, no gate)
- **Symptom:** end-of-call APIs (update/match/connect) intermittently never fire; the call ends early.
- **Root cause:** the phases are entirely silent background calls with no conversational cue and no "you may not close the call until X has run" gate. Heavy prompts amplify this (the model sheds steps).
- **Detection:** find every background-only phase. Check for (a) a must-run gate before the next action, and (b) a "never end/close the call before <final tool> (or the decline path) has run" gate. Check cascading gates — if phase N is gated on phase N-1's tool, a miss upstream silently kills all downstream calls.
- **Fix direction:** add `CRITICAL: you MUST call <tool> before proceeding` per phase + a hard "do not close before <terminal tool>" gate; mark calls mandatory-but-silent.
- **Seen in:** DKB 2026-06-29 ("call update_job_status for every job before proceeding"); Purple Dots review (Phase 4-5-6).

### C2 — Tool referenced but not declared
- **Symptom:** a step that depends on a lookup sheet/tool is skipped or hallucinated.
- **Root cause:** the step names a tool/"sheet" that is never declared in the tools/source-of-truth section, so the model can't ground it.
- **Detection:** list every tool/sheet *named in the body* and diff against the tools *declared* in the tool section. Any referenced-but-undeclared tool = flag.
- **Fix direction:** declare the tool, or remove the dependency.
- **Seen in:** Purple Dots review (`solution_enablers tool sheet` referenced, never declared alongside `Disabilitytypes`/`AssistiveAids`).

### C3 — Payload field/data bug
- **Symptom:** tool call returns wrong/empty results or targets the wrong record.
- **Root cause:** swapped or mislabeled fields (e.g. `searchlng ← lat`, `searchlat ← lng`), malformed variable names (`${phone(number}`), a wrong field name in prose vs payload (`work_experience_years` vs `workExperienceYears`), a **value-format mismatch** (e.g. a phone passed as a bare 10-digit string when the store expects a `+91`/country-code-prefixed value → empty lookup), or a **hardcoded ID overriding dynamic results**.
- **Detection:** for each payload, trace every value to its source. Check coordinate order (GeoJSON = `[lng, lat]`), check field names match the schema exactly, scan for stray/unbalanced brackets in `${...}`, confirm identifier **formats** match what the target store expects (phone with/without `+91`) **and that a write (create) and its later read (fetch/lookup) use the same format**, and flag any hardcoded id that contradicts a dynamic search in the same flow. **Also flag any assumption that `${country_code}` (or a similar country/prefix variable) is a passed input — INBOUND calls carry NO input variables, so it is unset at runtime; the phone must be built as the caller number with a literal `+91` prefix (exactly one prefix, never doubled), never sourced from a `${country_code}` variable.**
- **Fix direction:** correct the mapping/format; make create and lookup use the identical key format; reconcile hardcoded vs dynamic; hardcode `+91` (never rely on a passed `${country_code}`, especially on inbound).
- **Seen in:** DKB 2026-06-29 (`${phone(number}` → `${phoneNumber}`, `workExperienceYears`); Maya 2026-07-13 (`get_profile`/`create_profile` passed the bare number → ~14/80 empty fetches; fixed to `+91`-prefixed on both); KKB 2026-07-15 (same bare-number bug in both KKB placeholder language files — carried the fix over from Maya); KKB/Maya/DKB **inbound** 2026-07-16 (`${country_code}` declared as a passed input on inbound calls that have none → unset at runtime; fixed to "not a passed input → always assume `+91`", with the double-prefix guard); Purple Dots review (lat/lng swap; hardcoded provider `item_id`).

### C4 — Fixed-param / enum integrity
- **Symptom:** downstream system rejects the payload or mis-routes.
- **Root cause:** a fixed param drifted (`sourceService`, `eventType`, `app_instance`, `network`, `item_type`), or an enum field was populated in the wrong language / with a value outside the allowed set.
- **Detection:** verify every "always use this exact value" param is present and unchanged. For every enum field, confirm the prompt constrains it to the exact allowed strings **in English/Latin** and forbids the conversational-language version.
- **Fix direction:** restate the fixed value and the strict enum list at the payload.
- **Seen in:** DKB (fixed params `ONESTAGENT`, `app_instance`); Purple Dots (`disability_type`/`looking_for`/`documents_available` enum + English-only rule).

### C5 — Spoken line stands in for a tool call that never fires (fabricated result / hallucinated success / intent-without-action)
- **Symptom:** the agent SPEAKS a tool's outcome or intent as if done, but the tool was never actually emitted. Three shapes: (a) **hallucinated success** — "अप्लाई हो गया" but `apply_job` never ran (or errored); (b) **fabricated fetch** — a silent `get_profile` "first action" is narrated as done ("प्रोफ़ाइल मिल गई, [name]") with the name/role pulled from injected `${contact_memory}`, the tool never called; (c) **intent-without-action** — the apply bridge ("अप्लाई कर देती हूँ") is spoken (often repeated) but `apply_job` is never emitted; the model loops on the line.
- **Root cause:** the spoken line is treated AS the action. Nothing binds "profile found" / "I'll apply" / "applied" to an actually-emitted tool call, so the model fabricates the result from memory/context or repeats the intent line instead of firing the tool. Injected `${contact_memory}` makes fabrication especially tempting (the name is right there).
- **Detection:** for every tool whose result or intent has a spoken line (`get_profile` "profile found / name", the apply bridge, the success line), confirm the prompt states: the SPOKEN LINE IS NOT THE ACTION — the real tool call MUST be emitted (for a bridge, in the SAME turn); the result/name/id/`profile_id` comes ONLY from a real tool result, **never fabricated from `${contact_memory}` or context**; repeating the line is never a substitute; no waiting-narration around the call. Missing any = flag.
- **Fix direction:** bind the spoken line to a really-emitted tool call; ban inferring the result (name/role/id) from memory/context; require a bridge to be immediately followed by the tool call in the same turn and forbid re-speaking it as a stand-in; gate the success line on a real success result; ban waiting-narration.
- **Seen in:** Maya 2026-07-13 (`apply_job` never fired but "अप्लाई हो गया" spoken after `create_profile`); **Maya inbound 2026-07-16** (silent `get_profile` faked — "प्रोफ़ाइल मिल गई, [name]" spoken from `${contact_memory}`, tool never called → no `profile_id` → apply failed); **Maya outbound 2026-07-16** (bridge spoken twice, `apply_job` never emitted). Fixed by binding each spoken line to a really-emitted call, banning memory-fabrication + waiting-narration, and requiring the bridge→`apply_job` call in the same turn.

### C6 — Fetched response never consumed (no field map, no "use what's present" rule)
- **Symptom:** a lookup succeeds and returns rich data, but the agent proceeds generically — never addresses the caller by the returned name, never reflects the returned role/context, and re-asks fields the response already contains. The fetch was effectively pointless.
- **Root cause:** the prompt calls the tool but never (a) describes the **response shape / field meanings**, (b) says **which record to read** when the response is an array / multi-record, or (c) states that **any present field is authoritative and must be used, not re-asked**. With no read-back contract, the model treats the call as fire-and-forget and falls back to a generic script.
- **Detection:** for every data-returning tool (`get_profile`, `get_talent_insights`…), check the prompt has a "reading the response" section: a **field dictionary**, an **array / most-recent-record selection rule**, and an explicit **"present ⇒ known ⇒ ask only for genuinely missing"**. Also check at least one **example actually uses** the fetched data (greets by name, confirms role). Missing any = flag. (A5 — re-asking known fields — is one visible symptom of this broader gap.)
- **Fix direction:** add a response-field map + a most-recent-record rule + "present ⇒ known ⇒ never re-ask"; personalise from it (address by first name, reflect/confirm role); have an example model it.
- **Seen in:** Maya 2026-07-13 (`get_profile` returned a 6-profile array with name/role/age/gender; the agent ignored all of it, spoke the hold line, and jumped straight to the area question — no name, no role check — and would have re-asked age/gender. Fixed by adding a "Reading the get_profile response" field map + a "Using the fetched profile" name/role-confirm flow + Example 4).

### C7 — Fetched identifier not bound → downstream re-creates it (duplicate write)
- **Symptom:** a read/fetch already returned the record, but at action time the agent calls the **create/write** tool instead of reusing the fetched record — creating a duplicate — often because the response held several records and it was unclear which id to reuse. **The INVERSE also fails:** a NEW caller (no profile ever fetched) reaches apply and calls `apply_job` DIRECTLY, skipping the required `create_profile` — so no `profile_id` exists and the apply FAILS.
- **Root cause:** the prompt says "reuse the id from the fetch" but never (a) names the exact field (top-level `id` vs `userId`), (b) says **which record** when the response is an array, or (c) states "a record exists ⇒ reuse it ⇒ the create path is forbidden here." With no bound key, the model regenerates one via create (which conveniently returns a fresh id).
- **Detection:** for any flow that fetches a record then acts on it, check the prompt (1) names the exact id field, (2) picks one record deterministically (most-recent) when several return, and (3) **hard-forbids** the create/write path when the fetch succeeded (not merely "prefer reuse"). Missing any = flag. Cross-refs C6 (response not consumed). **Also check the fix is structural, not just prose** (see Fix direction) — a prompt with three "do not create" sentences can still fail this if the apply step doesn't lead with the binary checkpoint.
- **Fix direction:** bind "the most-recent record's `id` is THE `profile_id`; read it straight from the fetch result at action time"; make the create path visibly the **exception** (lead the action step with the reuse=one-tool path); add a **precondition STOP at the create tool's entry**. **Prose "do not create" guards alone are NOT enough** — the model still calls create because it needs an id and create is the tool that hands one back. The lever that holds is an action-time checkpoint keyed on the binary, in-context signal **"did the fetch run in this call?"**: if yes → the action tool (apply) is the ONLY call and its id comes from the fetch result; the create tool is forbidden. Reframe the action step to *decide with that one question first*, not to react with bans. **Both directions must be equally forceful:** the NO branch (no profile → `create_profile` FIRST, then `apply_job`) needs the same salience as the YES branch — state that `apply_job` without a `profile_id` FAILS and `create_profile` is the required first step (not optional), and that any "never mention/think about profiles" instruction given to a new caller applies to the conversation only, NOT to apply time.
- **Seen in:** Maya 2026-07-13 (`get_profile` returned a 6-profile array on the returning `new_seeker="no"` path; at apply the agent called `create_profile` and used its fresh id — a duplicate). **First fix (bind `id` + 3 hard "never create" guards) did NOT hold — it recurred the same day**: the agent still called `create_profile` at apply. The holding fix reshaped Step 4 to *lead* with "Did `get_profile` run in this call? → YES: `apply_job` ONLY, `profile_id` read straight from the fetch result; NO: create then apply", made the returning=one-tool path primary, and added a precondition STOP at `create_profile`'s entry — i.e. the decision-first checkpoint, not more bans. **KKB outbound 2026-07-16** — the INVERSE: `new_seeker="yes"` (new caller) reached apply and called `apply_job` directly with no `create_profile` → no `profile_id` → apply FAILED. Fixed by strengthening the NO-branch create-first gate to match the YES branch's force, then hardening the same gate **family-wide** across KKB inbound + Maya inbound + Maya outbound new-caller paths (preemptive — same class was latent in all of them).

### C8 — Result set presented in given order; known ranking signals not applied
- **Symptom:** the agent reads a list (jobs, options) in the order the array returned it, leading with an item that does not fit the caller, even though a better-matching item is present and the matching signal (profile role, stated preference) is known.
- **Root cause:** the prompt says the array is "sorted by relevance" (so the agent trusts array order) and/or never tells the agent to re-rank by the caller's known signals; the backend order isn't actually personalised to this caller.
- **Detection:** find where results are presented. Does the prompt (a) assume array order = relevance, and (b) omit an explicit "rank by <caller signals> before presenting"? If a known signal (profile role, stated preference) exists but isn't wired into ordering, flag it — especially when the pool is large.
- **Fix direction:** treat the array as a pool; rank it by the caller's known signals (role → location → salary) before presenting; put the matched items first; do not rely on the given order. When the target isn't known yet, orient first (short overview + one question), then rank.
- **Seen in:** Maya 2026-07-13 (profile role "Data Entry Operator" was known and confirmed, but the list still led with "Customer Support"; fixed by treating `${recommendations}` as a ~30-job pool ranked by role/location/salary and presenting the role-matched job first. Verified on a live `new_seeker="no"` call — Customer Support profile → list correctly led with Customer Support). The **pool-overview opener** for the role-unknown case was added second, only after the fork was live-verified, as **Step 1 Case B** (gated on role-unknown; names only real roles from the pool; explicit guard that it is never the call opener and never replaces the profile-permission question; **no from-greeting example added** — the prior attempt broke the fork precisely via a from-greeting `new_seeker="yes"` overview example, E1). Lesson: a redesign that touches presentation *and* risks a fork should ship in two verifiable steps — the fork-safe ranking first, the opener second, each live-tested on the branch it does not depict.

### C9 — Placeholder / sentinel field value spoken or acted on as if real
- **Symptom:** a fetched field carries a placeholder/sentinel value ("Any", "Not Available", "N/A", a generic "उपयोगकर्ता"/"अज्ञात" name) and the bot speaks it or acts on it as if real — e.g. profile `role="Any"` → "मैं देख रही हूँ कि आप अभी **Any** का काम देख रहे हैं — इसी तरह की जॉब्स?" (a role-confirm on a non-role), which also suppressed the pool-overview the unknown-role path should have given.
- **Root cause:** the "present & non-empty ⇒ KNOWN" rule (**C6**) treats ANY non-empty string as usable, but some fields carry domain sentinels that mean "unset." The empty-check (empty/null/missing) doesn't enumerate those sentinels, so "Any" reads as a real role.
- **Detection:** for each fetched field with a "present ⇒ use/confirm it" rule, check the prompt enumerates the field's **sentinel/placeholder values** ("Any", "Not Available", "N/A", generic names) and treats them as **ABSENT/unknown**, not present. A role/name/etc. that can be spoken or confirmed without a sentinel guard = flag. (Job `role="Not Available"` is already sentinel-guarded in the Variable Presence Rules — the gap is the fetched **profile** fields.)
- **Fix direction:** define the sentinel set per field; treat sentinel = absent/unknown; never speak the sentinel aloud; route on "unknown" (e.g. role unknown → pool overview / Case B, not a role-confirm).
- **Seen in:** KKB + Maya 2026-07-16 (profile `role="Any"` spoken and role-confirmed; fixed to treat "Any"/"Not Available"/empty/null/garbled as NOT a usable role → UNKNOWN → skip role-confirm → Step 1 Case B pool overview, surfacing the job-type summary upfront).

### C10 — Tool 4xx with a well-formed id = backend/endpoint issue, NOT prose (and endpoint differences across twins may be BY DESIGN)
- **Symptom:** a tool consistently fails on one bot with a client error even though the prompt did everything right — e.g. `apply_job` returns **HTTP 404 "Invalid or missing profile_id"** on every call, even after a clean `create_profile` returned a **valid UUID** `profileId` that the bot correctly passed. Prose is correct; adding more prose does nothing.
- **Root cause:** the failure is in the **backend / live tool config**, not the prompt. Either the endpoint is down/deprecated, or there is a cross-host mismatch (e.g. profile created on one interface host but applied against a different regional BAP host whose DB doesn't hold that id).
- **Detection:** when grounding a tool failure in a transcript, read the `__RAYA_TOOL_DEBUG__` block: a `4xx`/`404` with a concrete `url=` **and a well-formed id** (a real UUID from a successful create) is an **endpoint/backend** problem, not a payload/prose problem.
- **⚠️ Do NOT assume endpoint differences between language twins are "drift."** Language variants may use **region-specific backends by design** — e.g. **KKB Kannada = Karnataka endpoints** (`jobs.onest.seeker.dhiway.net`, `onest-lite-bap.dhiway.net`) while **KKB Hindi = UP endpoints** (`job-up.seeker.dhiway.net`, `up-onest-lite-bap.dhiway.net`). A host that differs from the twin is **not evidence of a bug**. Never PATCH a bot's `api_details` to "match its twin" without the **owner confirming** the endpoint is actually wrong — doing so can point a regional bot at the wrong region's data.
- **Fix direction:** **flag for the backend/platform owner** (`Flagged - Backend Issue`); do NOT prose-fix and do NOT blind-align endpoints. Reinforces **D25** (backend/runtime failures are not prose-fixable).
- **Seen in:** KKB 2026-07-30 (`kkb-kn-out` `apply_job` → 404 "Invalid or missing profile_id" on the Karnataka BAP endpoint despite a valid `profileId` from a successful create; grounded in calls `7e5e1173`/`ab930586`. Initially mis-read as endpoint "drift" vs the Hindi twin and PATCH-aligned to the UP hosts — **reverted on owner correction: "Karnataka doesn't use those endpoints."** Correct handling: leave the Karnataka endpoints as-is and flag the apply 404 as a backend issue.)

---

## D. Language, script & voice

### D1 — Hard/Sanskritised vocabulary despite a "simple language" rule
- **Symptom:** agent says tatsama/administrative words (सेवा प्रदाता, प्रशिक्षण, पुनर्वास, मूल्यांकन…) over a low-literacy voice channel.
- **Root cause:** only an abstract instruction ("use simple words / no technical terms") with **no concrete banned→preferred lexicon**. Abstract rules underperform explicit lists.
- **Detection:** if the prompt says "simple language" but has no do/don't substitution table for domain vocabulary, flag it. Bonus: scan the prompt's own spoken lines/examples for hard words it fails to gloss.
- **Fix direction:** add a substitution table + the rule "prefer the common English/Hinglish loanword over the pure-Hindi equivalent"; use the gloss pattern ("विकलांगता यानि डिसेबिलिटी").
- **Seen in:** Purple Dots review; general to all agents (each relies on explicit banned-phrase lists).

### D2 — TTS number/date/time/money not spelled as words
- **Symptom:** TTS mangles digits, `₹`, AM/PM, DD/MM/YYYY, phone numbers.
- **Detection:** confirm a TTS-normalization section exists AND that examples obey it (numbers as words, money in words, सुबह/दोपहर/शाम/रात not AM/PM, phone digit-by-digit). Flag any digit/`₹`/AM-PM/short-date in a spoken line or example.
- **Fix direction:** enforce word-spelling; fix offending examples.
- **Seen in:** all agents (standing TTS rules).

### D3 — Script separation: conversation vs payload
- **Symptom:** Devanagari leaks into API payloads, or Roman/Latin Hindi leaks into spoken output.
- **Detection:** confirm the prompt states (a) all TTS output = Devanagari (no Roman/mixed Hindi), and (b) all payload values = English/Latin, with transliteration rules for names/addresses. Flag missing/weak either side.
- **Fix direction:** restate the strict boundary + transliteration examples.
- **Seen in:** all agents (payload script-separation rule).

### D4 — Voice-gender inconsistency
- **Symptom:** a female-persona agent uses masculine verb forms (or offers both).
- **Root cause:** no explicit feminine-only rule, and/or a line offering "…रहा हूँ/रही हूँ".
- **Detection:** if persona is female, confirm an explicit "feminine verb forms only" rule and scan for any masculine form or "रहा हूँ/रही हूँ" dual-option.
- **Fix direction:** add the feminine-voice rule; remove masculine options.
- **Seen in:** Maya (explicit feminine-voice divergence); Purple Dots review (§7 "समझ रहा हूँ/रही हूँ" on a female persona).

### D5 — Modality leak (outbound bot invites callbacks)
- **Symptom:** an outbound (bot-calls-user) agent ends with "you can call me / call back when you need."
- **Root cause:** modality is declared once at the top but there's no closing script and no ban on inbound-framed language; the model falls back to trained call-center endings.
- **Detection:** if modality = outbound, confirm (a) a fixed Graceful-Exit/closing script and (b) an explicit ban on "call me/us back"-type phrasing. Bare "close the call" with no script = flag.
- **Fix direction:** add a closing script matching the true modality (e.g. "the center will contact you") + prohibition on callback phrasing.
- **Seen in:** Purple Dots review.

### D6 — Symbol/punctuation voiced literally (e.g. "/" read as "slash")
- **Symptom:** the bot speaks a punctuation symbol out loud — most often "/" pronounced "slash"/"स्लैश"/"ಸ್ಲ್ಯಾಶ್" when reading a role/category label ("सेल्स/मार्केटिंग", "कस्टमर सपोर्ट/बीपीओ") or a rate.
- **Root cause:** the prompt writes labels/values containing "/" and the TTS-normalization section either lacks a slash rule or has only a generic one that never mentions the role/category labels the bot actually forms, so the model emits the literal "/".
- **Detection:** grep the prompt for "/" inside spoken lines, pool-overview groupings, and inventory role labels ("X / Y", "A/B"). If any exist, confirm a TTS rule that (a) bans voicing "/" and (b) shows the role/category-label conversion to "या"/"ಅಥವಾ" (or the per-form for rates). A bare "speak / as या" one-liner that does not cover labels = flag.
- **Fix direction:** add/strengthen a "## Slash ( / ) symbol" rule with concrete label examples; never voice the symbol. Applies to every spoken-output prompt (inbound + outbound, both languages) — cross-agent.
- **Seen in:** KKB/Maya inbound live calls, 2026-07-17 (Consolidated Feedback rows 65/73).

### D7 — Inbound get_profile fork not hard-gated (fetch skipped / deferred / replaced with a permission-ask)
- **Symptom:** on an INBOUND (get_profile-driven) agent, the new-vs-returning fork misfires — the bot skips `get_profile` and jumps to discovery/jobs when the caller volunteers a role/city, defers the fetch behind a discovery turn, or invents a "can I fetch your profile?" permission-ask before finally calling it. The branch-on-result is usually correct; the fetch itself is the failure.
- **Root cause:** the inbound fork is written as soft prose ("As your first action, silently call get_profile") with no hard gate — unlike the outbound `new_seeker` DECISIVE ROUTER. Nothing forbids conversation/jobs before the fetch returns, and nothing forbids skipping when the caller front-loads a role/city.
- **Detection:** on any inbound/get_profile-driven prompt, confirm the fetch instruction is a HARD gate: (a) "NO conversation/jobs/permission-ask before it returns" and (b) "never skip if the caller volunteered a role or city." A bare "silently call get_profile first" with neither clause = flag.
- **Fix direction:** wrap the fetch in a DECISIVE ROUTER mirroring the proven outbound router — first action, real tool call, no conversation before it returns, never skip. Language-agnostic (verbatim across H/K).
- **Seen in:** KKB Placeholder Inbound + Maya Inbound live calls, 2026-07-14/17 (Consolidated Feedback rows 71/78; related: outbound profile-not-found path must still route to the Case-B pool overview, and the new-caller path must gate name+experience before create_profile — rows 74/80, 67/72). **KKB inbound Hi+Kn, 2026-07-27 — recurred even WITH a DECISIVE ROUTER present:** the fetch still fired 0/8 because the router bundled the fetch into the greeting turn (see **D29**) — the hard-gate wording was correct but its turn-placement suppressed the tool. Fixed by un-bundling into two turns.

### D8 — Internal technical term ("profile") spoken to the caller
- **Symptom:** the agent says an internal system word out loud — "profile"/"प्रोफाइल"/"ಪ್ರೊಫೈಲ್" — in the permission-ask, the found/not-found acknowledgement, or an example dialogue (e.g. "क्या मैं आपकी प्रोफाइल fetch कर सकती हूँ?", "प्रोफ़ाइल मिल गई"). Callers don't understand the term and it erodes trust.
- **Root cause:** the prompt's OWN spoken lines/examples use the internal term, and there is no rule mapping it to a caller-friendly word.
- **Detection:** grep the prompt's spoken lines + `> **Agent:**` examples for internal system nouns ("profile", tool names, "payload", "database", "fetch", "id"). Any such word in a line the caller hears = flag. Then confirm a "never speak <term> aloud; say <friendly word> instead" rule exists.
- **Fix direction:** add a wording-rules section that bans the term aloud and gives the friendly replacement ("जानकारी" / "ಮಾಹಿತಿ" for profile), reconcile every spoken/example line, and on an empty fetch never announce the miss. Keep internal tool names + rule text unchanged.
- **Seen in:** KKB + Maya get_profile prompts, 2026-07-19 (Profile Wording Rules).

### D9 — Skip-if-known field re-asked at the apply gate despite being on the fetched profile
- **Symptom:** the bot re-asks a field (age, gender, name, experience) at apply time even though the `get_profile` result earlier in the call already carries it — the "don't re-ask what the profile has" rule is stated but not honored at the decision gate. **Repeat-apply variant:** the skip holds on the FIRST apply but the bot re-asks on a SECOND/third apply in the SAME call (the profile result is now buried in context and the gate re-derives from scratch).
- **Root cause:** the skip rule lives in a general section, but the apply-time HARD BLOCK / Step 3.5 lists the field as a thing-to-ask with a spoken line, so the model defaults to asking; nothing forces a profile re-check right at the gate. And the skip is a per-gate re-check, not a persisted call-level fact — so each apply re-derives it and a later one misses.
- **Detection:** at every pre-apply "must be KNOWN" gate, confirm there is an explicit instruction to RE-CHECK the fetched profile's exact fields (e.g. `metadata.whatIHave.age` / `metadata.gender`) and skip the ask when present. A gate that only says "ask X" without "first re-check the profile for X" = flag. Also confirm the skip is a **call-level lock**, not a per-gate re-derivation: the profile's known fields must be stamped KNOWN for the whole call so a SECOND or third apply in the same call does not re-ask them. A skip with no persistence statement fails on repeat applies = flag.
- **Fix direction:** at the decision gate, add an explicit profile re-check naming the exact fields; note a returning caller (profile found) normally has them; ask only genuinely-missing fields. Additionally, **lock** the known fields the moment `get_profile` returns and state the lock does NOT reset between applications, so repeat applies in one call reuse them. Scope the lock to the SAME candidate — if a proxy caller explicitly switches to a different person mid-call, re-establish that person's fields (per-person lock, not blindly per-call). Crucially, the lock is unreliable unless the fields are EXTRACTED at profile-read time: instruct the prompt to read age/gender from the profile the moment `get_profile` returns, checking ALL returned records (the same caller often has several duplicate records with the fields scattered — the most-recent may hold placeholders while age/gender sit on an older record). Re-parsing a nested field (`metadata.whatIHave.age`) from a multi-record JSON array at the apply gate is flaky — extraction must happen at read time, not the gate.
- **Seen in:** Maya Inbound, 2026-07-20 (age/gender re-asked for a named returning caller). Strengthened 2026-07-20 (round 2): the re-check held on apply #1 but the bot re-asked age+gender on a SECOND apply in the same call; fixed with a call-level lock that persists across every apply, propagated to all 6 seeker files (KKB out/in H+K, Maya out+in). Round 3 (2026-07-20): the profile genuinely HAD age+gender (verified from the raw get_profile dump) but the bot still asked on apply #1, inconsistently — root cause was reading age/gender from a duplicate record that lacked them and re-parsing at the gate; fixed by extracting age/gender at read time across ALL returned records and committing them as known for the whole call. Grounding lesson: the Raya call payload does NOT contain the get_profile result — never conclude a field is absent from the call JSON; check the profile store directly.

### D10 — Mandatory end-of-call step skipped because the closing script is jumped to directly
- **Acceptance-turn variant → see D46.** D10 covers a mandatory interactive step being SKIPPED. The mirror failure is a step that HAPPENED and was then closed off in the same breath — the caller accepts and the line drops before they can ask what they agreed to. When auditing any branch that captures an ANSWER, also run the D46 checks: no bare `Then close.`, no bundled confirmation+valediction+hangup example, and the sanctioned answer reachable AFTER the yes.
- **Symptom:** a required end-of-call step (e.g. the MPL Competition offer, a survey, a callback promise) never happens — the bot goes straight to the goodbye line, skipping the trigger that sits just before it. **Intermediate-loop variant:** the bot sits in a mid-flow loop (e.g. "retry the apply, or see another job?") that has NO trigger for the step, so it never reaches the pre-goodbye trigger and only performs the step if the caller explicitly asks for it.
- **Root cause:** the trigger is soft prose ("before ending, if not yet done, offer X") placed next to a self-contained goodbye script the model jumps to; and a job/apply decline is mis-read as "the caller ended the call." The trigger also lives ONLY at the goodbye line, so any juncture that doesn't flow straight to goodbye (apply failure, decline-to-continue) has no hook.
- **Detection:** for any mandatory pre-goodbye step, confirm it's framed as a MANDATORY step that must run BEFORE the goodbye line (not a soft "if"), and that "declining a job/apply" is explicitly distinguished from "ending the call / do-not-call". Confirm the trigger fires at EVERY end-of-flow juncture — after a successful apply, after an apply FAILURE once the caller declines to retry / see another job, and on No-Match — not only at the literal goodbye line. Also confirm the step is a PROACTIVE push (the bot offers on its own), never a wait-for-the-caller-to-ask. When the offer has MULTIPLE trigger sites, confirm their SUPPRESSION lists match — a mandatory backstop ("you MUST offer it now") that omits an exception the main section has (e.g. "clearly in a hurry") will override that exception. If the step is INTERACTIVE (an offer/question needing a reply), confirm it is framed as its OWN turn that ENDS and WAITS — and that the closing line / "Goodbye" token is explicitly forbidden in the same turn; otherwise the model bundles the offer AND the goodbye into one breath and cuts the exchange off before it can happen (offer → wait → details → confirm never runs).
- **Fix direction:** make the step mandatory-before-goodbye; only an explicit end / do-not-call / hang-up suppresses it; a decline does not. Add the trigger at the apply-failure / decline-to-continue juncture too (not just goodbye), and phrase it as a proactive push — the bot must not wait to be asked.
- **Seen in:** Maya Inbound, 2026-07-20 (MPL never offered before goodbye). Strengthened 2026-07-20 (round 2): the mandatory-before-goodbye still missed because the bot stayed in the apply-failure retry loop (no trigger there) and only offered MPL when the caller explicitly asked; fixed by (a) making "when to offer" a proactive push covering apply success OR failure, and (b) a pointer from Apply-Failure Handling into the MPL push (Maya out+in). Further strengthened 2026-07-20 (round 3): once the push fired, the model said the offer line AND "Goodbye" in the SAME turn (Maya Inbound call 2bb8b332) — cutting the call before the caller could reply or register (`mpl_registration` null); fixed by making the offer its own waiting turn and forbidding the goodbye token in the offer turn. Round 4 (2026-07-20): even with the offer as its own turn + a proactive "after first apply" trigger + a pre-goodbye backstop, MPL STILL didn't fire in a long degraded call (3/3 apply_failed, gender misheard 3×) — soft section-prose triggers are deprioritised when the call goes sideways. Lesson: for a MANDATORY secondary step, tie it to a concrete high-attention event (a tool-call return — here the first `apply_job`) and frame it as non-negotiable as that tool call; section prose alone has a reliability ceiling. Detection: for any must-happen secondary step, prefer a rule anchored to a tool-call event over a rule anchored only to a conversational phase.

### D11 — Repeat apply by a NEW caller in one call re-mints the profile (duplicate) + re-gathers details
- **Symptom:** a brand-new caller (no profile at call start) applies to job A — `create_profile` mints a profile, name/experience/age/gender gathered — then applies to job B in the SAME call; the bot calls `create_profile` AGAIN (duplicate profile) and/or re-asks name/experience/age/gender it already has.
- **Root cause:** the apply fork keys off the START-of-call `get_profile` ("returned nothing → create_profile then apply_job"), which is still true on the 2nd apply; nothing states that once `create_profile` has minted a profile THIS call, that profile now exists and later applies reuse it.
- **Detection:** at the apply fork's new-caller / NO branch, confirm there is an explicit "once `create_profile` has run this call, the profile now EXISTS — a later apply reuses its `profile_id` via `apply_job` only, never `create_profile` again" clause. A fork that only branches on the start-of-call `get_profile` result, with no once-per-call `create_profile` guard = flag.
- **Fix direction:** add a once-per-call `create_profile` guard: after the first mint, treat the returned `profile_id` (and the gathered name/experience/age/gender) as KNOWN for the rest of the call; a 2nd/3rd apply calls `apply_job` only. Parallels D9's persistence clause on the returning-caller path.
- **Seen in:** all 6 seeker files, 2026-07-20 (found by adversarial verify of the D9/age-gender fix; the new-caller twin of the same repeat-apply weakness).

### D12 — Role-name variant / job-family not matched → false "no jobs" + inconsistent categorisation
- **Symptom:** the seeker names a role variant (customer service) and the bot ranks the matching pool job (Customer Support Executive) as unrelated, or tells the caller a role isn't available, while a same-role/family job sits un-offered in the pool; the same job is categorised differently across calls (customer service one call, sales another).
- **Root cause:** no role-synonym/job-family mapping — ranking relies on an undefined "closely related"; overlapping customer-facing categories (customer-service/support, sales/marketing/tele/field/promoter, crew/team-member/retail/store) are treated as separate matchable buckets.
- **Detection:** in any seeker matching/ranking or synonym section, verify (a) role-name variants map to the same role, and (b) customer-service/sales/crew/retail/promoter are declared ONE matchable customer-facing family (cashier excluded). Grep the outbound Default Presentation Rule for "family"/"synonym" — absence = flag.
- **Fix direction:** add a role synonym + job-family matching rule before ranking / before any "no jobs" statement; propose family members together; keep cashier distinct.
- **Seen in:** KKB inbound had per-role synonyms but no cross-family grouping; KKB outbound + Maya had neither. Fixed 2026-07-20 across all 6 seeker files.

### D13 — Out-of-city jobs surfaced in the first batch to a caller who stated their own city
- **Symptom:** a caller who named their city (e.g. Ghaziabad) is shown Noida/Meerut jobs in the FIRST batch, unprompted → immediate drop.
- **Root cause:** ranking places location BELOW role with no first-batch city anchor, so a role-matched out-of-city job outranks a same-city job.
- **Detection:** a Default Presentation Rule whose priority list has role above location and NO "stated city anchors the first batch" clause = flag.
- **Fix direction:** add a city-anchor rule — the stated city anchors the first batch; surface other/nearby cities only after local options, on request, or when local yields too few. Preference, NOT a hard filter (never exclude other cities outright).
- **Seen in:** KKB seeker (out + in), 2026-07-20.

### D14 — Yes/No gate advanced without capturing the owner's clear response (DKB)
- **Symptom:** the employer says yes or no clearly but the bot doesn't register it and advances anyway — takes the wrong branch or skips consent; the owner drops off frustrated.
- **Root cause:** no rule mandating capture + brief confirm of a clear yes/no at each decision gate before branching / firing a tool.
- **Detection:** for each identity / availability / freshness / new-vacancy / post-consent gate, verify a rule requires a clear yes/no be registered before the branch or tool call, and a single re-ask on an unclear/silent reply (an explicit "unsure" is itself a captured answer, handled per that gate's rule).
- **Fix direction:** add a "Yes/No Gate Capture" section listing the gates and requiring register-before-advance + one re-ask on no-clear-response.
- **Seen in:** DKB (calls 2465759, 3663530, 3664822), 2026-07-20.

### D15 — Apply failure dead-ends the seeker (no recovery, or burden shifted to them)
- **Symptom:** on an `apply_job` error the bot only says "couldn't apply, try again / see another" and often ends the call — or says "call us back later" / blames the seeker's phone or network. A seeker who chose to apply leaves with nothing.
- **Root cause:** Apply Failure Handling is a single line with no recovery path and no ownership of the (our-side, technical) failure.
- **Detection:** the Apply Failure Handling section must (a) own the failure as technical/our-side and note the interest, (b) offer exactly ONE recovery path — share `hr_contact` if the job has it, else offer ONE alternate job (not a batch of three, never the same failed job), else promise a callback with NO committed time, (c) hard-ban over-apology, blaming the seeker, "call later", and looping to a third apply, and (d) log the failure system-side without narrating it. A bare "apply failed, retry?" line = flag.
- **Fix direction:** replace with the multi-path recovery block (HR-contact / one alternate job / callback + hard bans + logging note). On seeker bots that have MPL (Maya), fold the one MPL offer into the alternate-job path on the first apply.
- **Seen in:** all seeker bots (KKB out/in H+K, Maya out+in), 2026-07-20. Ties to the recurring backend `apply_failed`.

### D16 — Empty get_profile misread as profile-exists → apply_job without create_profile
- **Symptom:** `apply_job` fails HTTP 404 "Invalid or missing profile_id"; for a NEW caller the agent applies directly after an empty `get_profile` (which returned `[]`), never calling `create_profile` first — so no `profile_id` exists and the apply fails 100% for new callers.
- **Root cause:** the apply-time YES/NO router keys on "did `get_profile` RUN" instead of "did it RETURN ≥1 record". An empty array `[]` (zero records) is read as "profile exists → returning caller → apply_job only", so `create_profile` is skipped and `apply_job` is called with no `profile_id`. (Distinct from C7's inverse, which keyed off `new_seeker`; here the fork is `get_profile`-result-driven and the empty-array case is the specific hole.)
- **Detection:** in a seeker prompt (KKB/Maya, out+in), grep the apply / Step-4 decision and the `create_profile` precondition for whether the empty-array case is explicit. FLAG if the router says only "get_profile ran and returned nothing" WITHOUT explicitly enumerating "empty array `[]` / empty object / zero records = NOT a profile = NO". Also FLAG any `apply_job` section lacking a "no `profile_id` ⇒ `create_profile` first; never `apply_job` after an empty `get_profile`" hard guard.
- **Fix direction:** state at the router, the NO branch, AND the `apply_job` rules that empty `[]` / zero records = no profile = `create_profile` first; treat the caller as brand-new (gather role/experience inline, then `create_profile` → `apply_job`); never call `apply_job` after an empty `get_profile`.
- **Seen in:** Maya outbound, 2026-07-20 (every new-caller call had empty `get_profile` → `apply_job` direct → HTTP 404 "Invalid or missing profile_id"; grounded in live transcripts 18fedd2e / 43e8f4ce).

### D17 — create_profile / get_profile phone double-prefix (+91+91…)
- **Symptom:** `create_profile` (or `get_profile`) fails HTTP 400 "Invalid Indian phone number format: +91+91XXXXXXXXXX"; or `get_profile` returns empty for a caller who DOES have a profile because it queried a malformed `+91+91` number.
- **Root cause:** the payload/template blindly prepends `+91` (JSON template `"phone": "+91<contact_phone>"` or call template `phoneNumber: +91${contact_phone}`) while `${contact_phone}` on the outbound/dialer deployment ALREADY carries `+91` → double prefix. (Related to C3's format-mismatch class, but the specific failure here is a LITERAL template that hard-prepends +91 even when a prose "do not double-prefix" guard exists elsewhere.)
- **Detection:** grep every seeker prompt (KKB Hi/Kn out+in, Maya Hindi out, Maya Inbound) for `+91<contact_phone>` and `+91${contact_phone}`. FLAG any literal template that prepends `+91` to the variable — even when a prose "do not double-prefix" guard exists elsewhere, the literal template is a landmine that can win. Require an exactly-one-+91 construction (use as-is if already prefixed; prepend only if bare 10-digit).
- **Fix direction:** change templates to a "contact_phone with exactly one +91 prefix — do not double-prefix" placeholder and add the anti-double-prefix guard to BOTH `get_profile` and `create_profile` phone rules.
- **Seen in:** Maya outbound, 2026-07-20 (`create_profile` sent `+91+91XXXXXX9115` → HTTP 400; latent in KKB Hi/Kn + both inbounds via the same JSON template).

### D18 — Branch router overridden by a lopsided concrete-vs-abstract next step (new_seeker="yes" still fetches profile)
- **Symptom:** a new_seeker / direction router is ignored — e.g. `new_seeker="yes"` callers still get the profile-permission question + `get_profile`, which that path forbids.
- **Root cause:** one branch has a concrete, forceful "ALWAYS say/do X, no exceptions" script and the sibling branch is only an abstract carve-out ("go straight into the conversation" / "handle naturally"); the concrete script wins and the model collapses all callers onto it. A router can bind the value correctly (not G1) and even be decisive in name (not A8's missing router) yet still lose because the two branches are unequal in concreteness, not just forcefulness.
- **Detection:** in any branching router (new_seeker yes/no, inbound/outbound, returning/new), check that EACH branch's next action is written as a concrete equal-force instruction (ideally an exact spoken line). FLAG when one branch has an exact "always" script and the sibling branch is only prose like "go into the conversation" / "handle naturally" — that asymmetry makes the router lose. Also FLAG when the decisive branch check is placed AFTER the concrete script rather than before it.
- **Fix direction:** make the branch variable the FIRST decision (explicit IF/ELSE); give every branch a concrete, equal-force next action (an exact spoken line where possible); restate the prohibition on the losing branch at the decision point.
- **Seen in:** Maya outbound, 2026-07-20 (calls e1f7abfc / 629abc7f — `new_seeker="Yes"` yet the agent asked profile permission and called `get_profile`; the "no" branch's concrete "next turn is ALWAYS the permission question, no exceptions" script overrode the "yes" branch's abstract "go straight into the conversation" carve-out). Recurrence of the `new_seeker` fork-over-fire class (G1 / E1 / A8) with a NEW failure mechanism — lopsided concrete-vs-abstract branches; when a control-variable fork misroutes, audit this alongside G1/E1/A8.

### D19 — Required spoken action referenced instead of inlined ("say the X line — see Y section") → not executed
- **Symptom:** a mandatory offer/line that is conditionally required (e.g. the MPL fold on the apply-failure path, the Graceful-Exit MPL backstop) is silently skipped; the output shows it was never said (e.g. `mpl_presented:"No"`).
- **Root cause:** the instruction says "say the Combined line (see the MPL section)" / "offer it plainly" — it points to another section instead of giving the exact words at the point of use, so under load the model drops it. A cross-reference is not an action; the model won't reliably reconstruct the line from a distant section at the moment it must fire.
- **Detection:** grep required conditional spoken actions for cross-references like "(see the … section)" / "offer … plainly" WITHOUT an adjacent verbatim line. FLAG any mandatory line that must be constructed from another section at the moment it is needed. **For a mandatory END-OF-CALL action (a required one-time offer/step that must happen before goodbye — MPL, a survey, a callback promise), a section-level "backstop" is NOT sufficient on its own:** confirm the action is BOTH (a) inlined VERBATIM at EACH exit point that can reach goodbye — including the failure / decline exit, not just the success path — and (b) enforced as a HARD GATE on the goodbye token itself ("saying Goodbye / the closing line is FORBIDDEN until X has been offered this call", with the explicit skip-list). A backstop that lives only in the Graceful-Exit section, or an inline line present on the success exit but missing on the failure/decline exit, = flag — an alternate exit (the failure path) will bypass it and reach goodbye with the offer never made. **Detection tell:** live calls reach "Goodbye" / the closing line with the required offer's output field still false (e.g. `mpl_presented:"No"`), ESPECIALLY via an alternate exit (the failure/decline path) that flows to goodbye without passing through the graceful-exit section where the backstop lives.
- **Fix direction:** inline the EXACT spoken line at each point where it must fire (failure path, no-apply / graceful-exit backstop, success path), even if it duplicates the canonical line elsewhere; keep the canonical definition as the single source but copy the words to the trigger point. **For an end-of-call action, additionally gate the goodbye token itself** — make "Goodbye"/the closing line FORBIDDEN until the action has been offered this call (skip only on the explicit exceptions: prior registration, explicit end / do-not-call / in-a-hurry / hung-up) — so no exit, including the failure/decline path, can reach goodbye without it.
- **Seen in:** Maya outbound MPL, 2026-07-20 (the failure-path MPL fold and the Graceful-Exit MPL backstop both said "say the Combined line (see the MPL section)" rather than an inline exact line → MPL never presented, `mpl_presented:"No"`; fixed by inlining the exact combined alternate-job+MPL line on the failure path and an exact standalone MPL line at the Graceful-Exit no-apply backstop). **Recurred 2026-07-20** — MPL STILL skipped: after a failed apply the caller declined the alternate job and the bot said its wrap-up line + "Goodbye" in one flow, bypassing the Graceful-Exit backstop entirely (the failure path is an alternate exit that never enters the graceful-exit section). Fixed by (1) an inline MANDATORY verbatim MPL line AT the failure exit (stating a failed apply / "not interested" does NOT waive it), (2) routing the "don't loop → acknowledge tech issue" step through the MPL offer before Graceful Exit, and (3) a HARD GATE at the top of Graceful Exit making "Goodbye" FORBIDDEN until MPL has been offered this call. Lesson: for a mandatory end-of-call action, one section-level backstop is not enough — inline it at every exit AND gate the goodbye token. Relates to the "mandatory step collapsed / tie the step to a tool-call event for reliability" class (D10) — same reliability ceiling of section prose, addressed by putting the exact words at the trigger point.

### D20 — Bundled create_profile+apply_job → tool call narrated as text + hallucinated apply success
- **Symptom:** `apply_job` is never actually called; the model writes the `apply_job`/`create_profile` JSON payload as spoken text (e.g. `{"agentId":...,"job_id":"JOB-1001"}`) and/or says "अप्लाई हो गया है" after only `create_profile` returned (often repeated); `call_output` records a fake application that never happened.
- **Root cause:** the new-caller apply turn bundles `create_profile` THEN `apply_job` back-to-back ("bridge → create_profile → apply_job"); after `create_profile` returns success the model conflates create-success with apply-success and renders the NEXT tool call as prose instead of emitting it.
- **Detection:** in any seeker prompt (KKB/Maya out+in) check whether the new-caller apply path calls `create_profile` and `apply_job` in the SAME turn. FLAG bundling. Also FLAG any apply section lacking explicit guards that (i) a tool payload / `{` / field name must NEVER appear in spoken text, (ii) `create_profile` success is NOT an application, (iii) the success line ("अप्लाई हो गया है") requires a real `apply_job` success RESULT in that same turn. Also FLAG a spoken "submitting / sending your application" NARRATION (present-continuous — "आपकी अर्जी भेज रही हूँ", "ನಿಮ್ಮ ಅರ್ಜಿ ಸಲ್ಲಿಸುತ್ತಿದ್ದೇನೆ") as a hallucination signal in its own right — the model narrating the apply as if it is happening in place of emitting the tool; the only apply action is the `apply_job` tool call. **Cross-language sync check:** verify the APPLY-TURN INTEGRITY block is present in BOTH language variants of EVERY seeker bot (outbound AND inbound) — since a weaker-language model surfaces the gap first (KKB Kannada showed it while Hindi was not immune), a block present in one language/direction but missing in its twin = flag.
- **Fix direction:** DECOUPLE — fire `create_profile` earlier (right after collecting the new caller's details), so the apply turn is ALWAYS a single `apply_job` call for every caller (returning: reuse the fetched id; new: reuse the id `create_profile` returned earlier); add the three integrity guards above; keep `create_profile` silent (no bridge line).
- **Seen in:** Maya outbound, 2026-07-20 (live call e0ac582c — after `create_profile` success the model spoke the `apply_job` payload as text and said "अप्लाई हो गया है" twice, `apply_job` never emitted, recorded as a real application). Relates to the hallucinated-success / speak-JSON classes already catalogued (C5). KKB inbound Hi+Kn, 2026-07-22 (guard ported from Maya). KKB outbound Hi+Kn, 2026-07-22 (narrated 'submitting your application' + said applied with no apply_job tool call; guard ported from Maya).

### D21 — New-caller pre-apply fields skipped when the caller rushes to apply
- **Symptom:** for a NEW caller (create_profile path), only SOME of name / experience / age / gender / location get collected before applying; `create_profile` is minted with empty gender / no age; the caller said "अप्लाई कर दो" and the model skipped straight to apply.
- **Root cause:** the pre-apply data gate is not enforced as a HARD BLOCK on the new-caller path; a fast apply-consent bypasses the collection sequence.
- **Detection:** check the `create_profile` path for a HARD BLOCK enumerating ALL fields `create_profile` needs (name, experience, age, gender, location) that must be gathered before `create_profile` / apply, explicitly stating a rushed apply-consent does NOT waive it. FLAG if age / gender / name / location collection is optional or only "when natural". Crucially, confirm the gate lives as a HARD PRECONDITION **AT the `create_profile` call site** — a pre-call checklist of all required fields run immediately before the tool fires — NOT only in a separate Pre-Apply / data-collection section: a gate stated only in a distant section is skipped under the apply-rush, so a section-only gate = flag. Specific tell to grep for: `create_profile` minted with an empty `gender` / age / experience, with that field asked **AFTER** the tool already ran (fields collected post-mint = the gate didn't hold at the call site).
- **Fix direction:** add a NEW-CALLER HARD BLOCK requiring all `create_profile` fields to be collected (one at a time) before minting the profile, even if the caller rushes; name uses `contact_name` if present, else asked. Place the enforcement as a HARD PRECONDITION AT the `create_profile` call site (a pre-call checklist: verify name + experience + age + gender + location are all actually collected, and if any is missing ask it first before the call), not only as a rule in a separate Pre-Apply section — the call-site checklist is what holds under the apply-rush; name it as forbidding the specific failure (asking gender/experience after `create_profile` already ran).
- **Seen in:** Maya outbound, 2026-07-20 (live call e0ac582c — for the new caller only experience was asked; age, gender, location, name skipped when the caller rushed to apply). KKB Hi+Kn outbound, 2026-07-22 (experience gate ported from Maya).

### D22 — Variable-gated branch ignored — model follows structural dominance, not the ${var} value
- **Symptom:** a branch that should depend on an input variable (`new_seeker` yes/no, direction, language) behaves identically regardless of the variable's actual value — flipping which branch is written as dominant flips ALL calls, proving the variable never steered the decision.
- **Root cause:** the `${var}` token appears only in buried prose, not AT the decision; the model picks the structurally-dominant / first branch by salience instead of reading the interpolated value. (Also possible: the variable isn't interpolated at all by the platform.)
- **Detection:** for every variable-gated branch, check that the INTERPOLATED value is surfaced AT the decision point (e.g. "the X value for this call is: ${X}") — not just referenced abstractly ("consider X"). FLAG branches where the value isn't surfaced at the decision, or where both branches read as plausible defaults with no value anchor. Cross-check live calls: if behavior is invariant to the variable's value, the gate is dead.
- **Fix direction:** surface the interpolated `${var}` value immediately at the decision; make the SAFE branch the explicit default for empty/blank/unsubstituted values; state "branch strictly on the value shown, never by habit". If a Yes vs No test still shows identical behavior, escalate to a platform fix (register the variable, or split into separate agents).
- **Seen in:** Maya outbound, 2026-07-20 (across ALL 14 maya-hi-out calls `new_seeker` never steered the branch — before the fix every call fetched `get_profile`, after it every call skipped it, regardless of Yes/No; fixed by surfacing "the new_seeker value for THIS call is: ${new_seeker}" at both the greeting-transition decision and the DECISIVE ROUTER, and defaulting empty/blank/unsubstituted values to the fetch branch). KKB Hi+Kn outbound, 2026-07-22 (same new_seeker router; the value-surface + default-to-fetch fix ported from Maya) — now a confirmed cross-agent recurrence. Relates to the lopsided-branch class **D18** — this is the same router failing even with balanced branches, because the value wasn't read.

### D23 — Always-ask question folded into a combined multi-field prompt → never fires
- **Symptom:** a required / "always ask" question never appears in live calls even though the prompt contains it (e.g. DKB's "open to freshers, or only experienced candidates?" ask was skipped). The prompt having the question is not enough — it was structurally unreachable.
- **Root cause:** the mandatory question is FOLDED into a COMBINED question that also covers another field (e.g. "any minimum qualification or experience?"). When the user answers the other part — or volunteers the folded field in passing (the owner said "two years") — the agent treats that field as captured and moves on, short-circuiting the distinct ask.
- **Detection:** for every "always ask" / mandatory question, confirm it is a STANDALONE question, not bundled into a combined "X or Y?" prompt that pairs it with another field. FLAG combined asks like "any minimum qualification **or** experience?" that couple a mandatory distinct question with a second field. Cross-check live transcripts: if the field's dedicated question never appears while its value nonetheless gets captured from another answer, the ask is being short-circuited.
- **Fix direction:** decouple the combined question so each field is asked separately; state the mandatory question must be asked as its OWN distinct step (asked whenever its variable is "Not Available"), and not skipped just because the user mentioned it while answering something else.
- **Seen in:** DKB Hi+Kn, 2026-07-22 (freshers-vs-experienced ask folded into the qualification question — combined "कोई minimum qualification या experience चाहिए?"; owner answered with experience, so the distinct freshers ask never fired; grounded in live call 1be4fc6c. Fixed by asking qualification alone and making the freshers-vs-experienced question its own step whenever `${work_experience}` is "Not Available").

### D24 — Outbound-lineage residue in an inbound prompt contradicts the silent-fetch router (permission-ask / outbound greeting)
- **Symptom:** an INBOUND agent asks permission to fetch ("क्या आपकी बेसिक जानकारी देख सकती हूँ?") or fails to fetch silently first, despite a `get_profile`-driven "no permission" DECISIVE ROUTER — an old-caller can't get fetched / a new caller is asked to fetch.
- **Root cause:** the inbound prompt was derived/copied from the OUTBOUND prompt and still carries outbound-lineage residue — a "Permission ask (before get_profile)" spoken line, an "if the user declines the permission ask" clause, and/or an outbound "I'm calling you from the government" greeting ("मैं गवर्नमेंट की तरफ़ से कॉल कर रही हूँ") — which directly contradicts the inbound silent-fetch router; the model may follow the residual spoken line instead of the router.
- **Detection:** in every INBOUND prompt, grep for permission-ask spoken lines, "declines the permission ask", and outbound-style greetings ("गवर्नमेंट की तरफ़ से कॉल कर रही"); flag any that contradict the `get_profile`-driven DECISIVE ROUTER. Cross-check: an inbound Profile-Wording-Rules "Spoken lines to use" list should NOT contain a permission ask.
- **Fix direction:** remove/neutralize the outbound residue in inbound prompts — replace the permission-ask entry with an explicit "no permission ask on inbound; `get_profile` is silent" ban, drop the declines-permission clause; ensure the inbound greeting is inbound-style ("…में आपका स्वागत है").
- **Seen in:** KKB inbound Hi+Kn, 2026-07-22 (residual outbound permission ask + declines-permission clause in the Profile Wording Rules, contradicting the silent-fetch router; neutralized in both files. Maya inbound has the same latent residue — flagged, not yet fixed).

### D25 — Anti-narration / "say only X" edit near a mandatory tool call suppresses the tool itself
- **Symptom:** a mandatory tool call (e.g. `get_profile` as the required first action) silently STOPS firing on live calls after an anti-narration / "say only X" edit placed near it; downstream tools that depend on its result (`apply_job`) then fail.
- **Root cause:** an edit that de-emphasises a REQUIRED tool call — calling it "silent / invisible / produces no speech / nothing to acknowledge / not a conversational turn" — especially combined with a "turn N is EXACTLY X and NOTHING else" whitelist, gets over-generalised by the model into "the tool call is optional / skippable," so it omits the call. Suppressing the *narration* of a tool accidentally suppressed the *tool*. (Counterpart to **B2**: the structural anti-narration fix for a fixed opening line can regress tool firing. **Resolution — see D29:** don't try to make one turn both greet-clean and silently-fetch; un-bundle into two turns — greeting turn, then a mandatory tool-only fetch turn — so the tool keeps its own loud mandate.)
- **Detection:** after ANY anti-narration or "first spoken output is exactly X / nothing else" edit that sits near a mandatory tool call, treat tool-firing as a regression risk: (a) grep for language that frames a required tool as invisible / silent / nothing-to-do; (b) confirm the tool-call MANDATE ("you MUST call X; do not proceed until it returns") remains present and is NOT undercut by the same paragraph; (c) VERIFY on a live call that the tool still fires — do not assume. Keep the "must-call" mandate textually separate from the "don't-narrate-it" rule.
- **Fix direction:** keep the tool-call mandate strong, positive, and separate ("`get_profile` is REQUIRED and fires first; the call is silent but never skipped"). Do not solve turn-1 narration by loading turn 1 with prohibition weight; prefer a platform static-first-message / pre-call automation where available (cf. B2). When in doubt, roll back to a snapshot known to fire the tool.
- **Seen in:** KKB inbound (Hindi+Kannada), 2026-07-23 — the fetch-narration "structural fix" of 2026-07-22 (B2) was rolled back because it suppressed `get_profile` firing (the model stopped calling the tool → no profile fetched → `apply_job` failed).

### D26 — Place/city names spoken inconsistently or mispronounced (no canonical-spelling pin)
- **Symptom:** place/city names are spoken inconsistently or mispronounced by TTS (e.g. Ghaziabad rendered गाजियाबाद vs गाज़ियाबाद), the spoken form varying by the caller's own speech, the fetched profile, or how the location was formatted in the inventory. The same place comes out different across calls (or even within one call).
- **Root cause:** the prompt relies on general/dynamic transliteration + phonetic-matching for location names, so nothing pins one canonical spoken spelling per place — each mention gets re-transliterated from whatever surface form triggered it, and TTS reads the nukta-less / phonetically-approximated variant.
- **Detection:** for an agent with a known, finite set of inventory locations, check for a "Canonical Location Spellings" (or equivalent) section that pins each place's EXACT spoken spelling and explicitly OVERRIDES the general transliteration + phonetic-matching rules. FLAG its absence, or any place name that appears in the call flow / inventory / example dialogues but is NOT in the canonical list. Cross-check both language files carry the section (script-adapted) — a canonical list in Hindi but not Kannada = flag.
- **Fix direction:** add a "## Canonical Location Spellings" section under Language & Script Rules listing every inventory place with its exact canonical script form (nukta and all), stating it OVERRIDES all general transliteration / phonetic-matching rules; forbid dynamic/phonetic re-transliteration of these names regardless of how the caller or the data spelled them. Mirror across languages, script-adapted (Devanagari in Hindi files, Kannada script in Kannada files).
- **Seen in:** KKB + Maya, 2026-07-24 (Consolidated Feedback rows 69/71 — Ghaziabad + Indirapuram/Mohan Nagar/Rajendra Nagar/Sector 5 mispronounced; added the section to all 6 KKB/Maya seeker conversation prompts, Devanagari + Kannada-script; DKB skipped — no hardcoded location references).

### D27 — Apply-failure turn re-speaks the apply bridge / re-fires apply_job on the same already-failed job
- **Symptom:** on a FAILED `apply_job` turn, the bot re-speaks the apply bridge/hold reassurance it already said before the tool call ("अप्लाई कर देती हूँ") at the head of the failure message with no new tool call; and/or, when the caller re-requests the SAME job, it re-fires `apply_job` on that already-failed `job_id` instead of moving on.
- **Root cause:** the Apply Failure Handling section says the base failure line "say once" but does not explicitly forbid re-speaking the pre-tool bridge/hold on the failure turn; and the "no same-job retry" rule was scoped to the alternate-job path, not to a repeat request for the ORIGINAL failed job — so a fresh caller request re-enters the apply and re-fires the tool on a job that already failed.
- **Detection:** in the Apply Failure Handling section, confirm BOTH (a) an explicit "begin the failure message DIRECTLY with the base failure line; do not re-speak the bridge/hold on the failure turn" rule, AND (b) a call-wide "an already-failed `job_id` is DONE this call; never re-fire `apply_job` for that same `job_id`" rule (route straight to interest-noted / HR / alternate-job). Flag the absence of either. Cross-agent: confirm both guards exist in EVERY agent that has `apply_job` (KKB out/in H+K, Maya out+in), with the English scaffolding identical across languages.
- **Fix direction:** add both guards — (1) the failure message opens directly with the base failure line, never the bridge/hold; (2) an already-failed `job_id` is DONE for the call, never re-fire it, route to the interest-noted / HR / alternate-job path. Propagate to all `apply_job` agents; keep the English scaffolding identical across language variants (translate only the quoted bridge examples). Relates to B1 (one-time bridge line re-spoken) and D15 (apply-failure recovery).
- **Seen in:** KKB inbound (Hi+Kn) + Maya (Hi + Inbound), 2026-07-27 (Sheet row 68, P1; live call 4663a367, 2026-07-26 — on a failed apply the bot re-spoke the apply bridge/hold at the head of the failure message with no new tool call, and re-fired `apply_job` on the same already-failed `job_id` across repeat requests).

### D28 — apply_job sent create_profile's numeric top-level `id` instead of the `profileId` UUID → 404 "Invalid or missing profile_id"
- **Symptom:** `apply_job` (or any downstream tool) fails with `{"error":"Invalid or missing profile_id"}` / a 4xx despite `create_profile` having just SUCCEEDED — the profile was minted, but the apply is rejected. Reads as a backend/apply-endpoint fault, so it gets mis-filed as pure backend.
- **Root cause:** `create_profile` returns BOTH a numeric top-level `id` (e.g. `5051`) AND a `profileId` UUID (e.g. `2b51fd94-…`). The prompt told the model to use "the id `create_profile` returned," so it passed the numeric `id` as `profile_id`, which the backend rejects — it wants the UUID. (Note the asymmetry: `get_profile`'s top-level `id` IS the UUID, so the returning-caller path was correct; only the `create_profile` / new-caller path carries this trap.)
- **Detection:** read the tool-call ARGUMENTS in the transcript — the assistant turn's `tool_calls[].function.arguments`, NOT just `content` / the tool results — and check that `apply_job`'s `profile_id` is a UUID, not a small integer. A `profile_id` that is a short numeric string right after a `create_profile` = flag. In the prompt, check the `apply_job` payload rule (and the new-caller apply clause) names `profileId` explicitly (the UUID) for the create_profile path — a rule that says "use the id create_profile returned" without disambiguating `id` vs `profileId` = flag. Cross-agent: confirm the fix is present in EVERY apply-capable agent (KKB out/in H+K, Maya out+in).
- **Fix direction:** on the create_profile path, mandate the `profileId` UUID field as `apply_job`'s `profile_id` — NEVER the numeric top-level `id`; leave the get_profile / returning-caller path (top-level `id` already the UUID) unchanged. Propagate across all apply-capable agents; keep the English scaffolding identical across language variants. Relates to C7 / D16 (same "Invalid or missing profile_id" surface, different root cause — here a real profile exists but the WRONG field was read).
- **Seen in:** KKB + Maya, 2026-07-27 (grounded in Maya call 46d9f776 — `create_profile` returned `{'id': 5051, 'profileId': '2b51fd94-…'}`, `apply_job` was sent `profile_id:"5051"` → 404 "Invalid or missing profile_id"; a large share of the "apply failing" P1s, rows 15/42/65).

### D29 — Greeting bundled with a silent fetch in ONE turn → the model narrates the fetch OR skips it (un-bundle into two turns)
- **Symptom:** on an inbound (get_profile-driven) agent, turn 1 fails in one of two ways that keep *alternating* as you edit: (a) the model **narrates** the fetch — "एक मिनट, आपकी जानकारी निकल रही है" / "अभी आपकी जानकारी मिल रही है" prepended to the greeting (**B2**); or (b) the model **never emits `get_profile` at all** — speaks the greeting (often with a narration) and jumps straight to discovery/jobs, so at apply time it fabricates a `profile_id` → 404 (**D7** / C-family). Grounded: KKB inbound fired `get_profile` in **0 of 8** calls while every call spoke a fetch-narration.
- **Root cause:** the prompt tells the model to do BOTH in one turn — "say ONLY the greeting" AND "fire `get_profile` SILENTLY in that same turn." A voice turn is effectively either a spoken turn or a tool-call turn; asked to bundle, the model keeps the speech and drops the tool (narrating the fetch as its way of "doing" it). This is why the two symptoms alternate: emphasise the greeting → it narrates/skips the tool; reframe the tool as silent/invisible to stop the narration → it treats the tool as a non-action and skips it (that IS the **D25** regression). Narration (B2) and not-firing (D25/D7) are the SAME bug — the bundling — seen from two sides; no single-turn wording resolves both.
- **Detection:** in any inbound fetch rule, grep for language putting a spoken greeting and a `get_profile` tool call in the SAME turn — "fire it silently in that same turn," "deliver the greeting alongside the silent call," "your first spoken turn is the greeting AND the fetch." That co-location = flag, no matter how forceful the "you MUST call it" mandate is. Confirm on live transcripts by reading `tool_calls` (not `content`): turn 1 has spoken text and no `get_profile` tool_call across several calls ⇒ the bundling is suppressing the tool.
- **Fix direction:** **un-bundle into two turns.** Turn 1 = greeting only (clean, spoken, no tool, no narration). Turn 2 = the fetch as your FIRST action — a REAL, MANDATORY, tool-only `get_profile` call (no accompanying speech), before you answer the caller or ask/present anything ("NO conversation before it returns"). This stops the narration (the greeting turn is clean) WITHOUT making the fetch feel optional (it is a loud mandatory tool call that simply owns its own turn) — resolving the B2↔D25 tension a single-turn fix cannot. Keep the "must-call" mandate LOUD and the tool-timing as "your first action on the next turn," never "silent/invisible/nothing." This is what a WORKING reference already does (Maya inbound fires `get_profile` on turn 2). Language-agnostic (English rule verbatim H/K; only the quoted forbidden-narration strings adapt). A platform static/first-message field still helps, but the two-turn structure fires reliably instruction-only.
- **Seen in:** KKB Placeholder Inbound Hindi+Kannada, 2026-07-27 (0/8 calls fired `get_profile`; every call narrated a fetch it never performed — e.g. call 34f1f587 spoke "एक मिनट में आपकी जानकारी मिल जाएगी" then went straight to `apply_job` with a fabricated UUID → 404). Root cause line: "Fire `get_profile` SILENTLY in that same turn [as the greeting]." Fixed by the two-turn un-bundle, ported from the working Maya inbound mechanism (greet turn 1, fetch turn 2), made *smoother* than Maya by also banning the fetch-narration on both turns. Rows 15/42/65. **Maya inbound, 2026-07-27:** the same two-turn structure applied to Maya — which already fired `get_profile` on turn 2 — to remove its pre-greeting fetch-narration ("मैं आपके लिए जानकारी देख रही हूँ" before "नमस्ते"); un-bundled ("Deliver the greeting alongside the silent call" → two turns) + banned the narration, keeping the fetch mandatory (so firing is preserved, delivery is smoother).

### D30 — apply_job stripped the job_id UUID hyphens → 404 "Job not found"
- **Symptom:** `apply_job` fails HTTP 404 `{"error":"Job not found"}` even though the selected job clearly exists in the Job Inventory / `${recommendations}`. Reads as a bad-inventory / backend fault, so it gets mis-filed as backend.
- **Root cause:** the model emitted the `job_id` UUID with its hyphens **removed** — e.g. sent `eab4805a7d5f4bf2b1a91fd34521550d` (a bare 32-hex run) when the inventory holds `eab4805a-7d5f-4bf2-b1a9-1fd34521550d` (8-4-4-4-12). The backend keys on the exact hyphenated UUID, so the stripped form matches nothing → "Job not found". The prompt said "use the `job_id` from the selected job" but never required copying it verbatim, hyphens intact. (Sibling to **D28**: same "apply 404 that looks like backend," different mangled field — D28 = wrong field for `profile_id`, D30 = mangled `job_id`.)
- **Detection:** read the `apply_job` `tool_calls[].function.arguments` (NOT `content`) and check `job_id` is a full hyphenated UUID (8-4-4-4-12). A `job_id` that is a 32-char hex run with no hyphens (or otherwise altered) = flag. In the prompt, check the `apply_job` payload rule mandates copying the `job_id` verbatim with all hyphens — a bare "use the job_id from the selected job" without a verbatim/hyphen rule = flag. Cross-agent: confirm the rule is present in EVERY apply-capable agent (KKB in/out H+K, Maya in+out).
- **Fix direction:** in the `apply_job` payload rules, mandate passing the `job_id` EXACTLY as it appears — a full hyphenated UUID, every character including all four hyphens, never stripped/added/reformatted; name the "Job not found" 404 as the consequence. Additive, language-agnostic (identical English across variants). Propagate to all apply-capable agents.
- **Seen in:** KKB inbound Hindi, 2026-07-27 (call `8ddcaa5a` — `apply_job job_id:"eab4805a7d5f4bf2b1a91fd34521550d"` → 404 "Job not found"; `profile_id` was a correct UUID, so the mangled `job_id` was the sole failure). Fixed + propagated to all 6 apply-capable KKB/Maya files.

### D31 — New-caller `create_profile`→`apply_job` batched in one turn → `apply_job` sent an EMPTY `profile_id`
- **Symptom:** on the new-caller path, `apply_job` fails because its `profile_id` is an **empty string** (`""`), even though `create_profile` ran and succeeded immediately before it. Reads like the model "forgot" the id, but the id was never available yet.
- **Root cause:** the apply-sequence prose instructed the model to run `create_profile` + `apply_job` as "ONE clean sequence in a single turn" / "back to back" / "for the whole sequence." The model obeyed by emitting BOTH tool calls in the **same turn/batch**, so `apply_job`'s arguments were built **before `create_profile`'s result existed** — and `create_profile`'s returned id is the ONLY source of the new caller's `profile_id`. With no id available at emit time, the model fills `profile_id: ""`. (Distinct from the hallucinated-apply family where `apply_job` never fires — here it fires, but with an empty id; both stem from mishandling the `create`→`apply` hand-off.)
- **Detection:** read `apply_job`'s `tool_calls[].function.arguments` — a `profile_id` that is `""`/absent right after a `create_profile` in the same turn = flag. In the prompt, grep the apply-sequence for "single turn" / "back to back" / "whole sequence" applied to a `create_profile`→`apply_job` pair: any wording that tells the model to batch a create with an apply is the bug (the apply's id can't exist until create responds).
- **Fix direction:** make the new-caller apply **two steps that cross a tool-result boundary**: `create_profile` FIRST → WAIT for its result → then, as the NEXT action, read the `profile_id` from that result and call `apply_job` with it. Explicitly forbid emitting `create_profile` + `apply_job` in the same turn/batch, and forbid `apply_job` with an empty `profile_id`. Leave the returning-caller path (single `apply_job` after `get_profile`) unchanged. Language-agnostic (verbatim H↔K). Platform response-variable capture (auto-carry `create_profile`'s id into `apply_job`) or tool-forcing is the durable backstop.
- **Seen in:** KKB base (kkb-kn-out), 2026-07-27 (call `40c8e3db`, `new_seeker=Yes` — `[create_profile, apply_job]` with `apply_job profile_id:""`; returning path `61d713a6` fine). Fixed by splitting the sequence (Hi lines 387/889 + Kn). **Also ACTIVE on KKB inbound, 2026-07-30** (calls `5449910e`, `34f1f587` — new inbound caller: `apply_job` with a fabricated/empty `profile_id` and NO `create_profile` → 404; the inbound prompts still said "single turn / back to back / whole sequence"). Fixed **kkb-hi-in (DEPLOYED)**; **kkb-kn-in pending live-inventory reconcile** (pull real inventory first). **Flag:** ANY get_profile-driven agent whose apply-sequence says "single turn / back to back / whole sequence" for the new-caller create→apply pair — Maya (out+in) still carries it (verify + fix).

### D32 — Memory block used as a substitute for `get_profile` → premature name/role + fetch never fires
- **Symptom:** on a get_profile-driven agent, the bot opens by greeting the caller **by name** and naming their saved role/journey ("ನಿಮ್ಮ ಮಾಹಿತಿ ಸಿಕ್ತು, [name]…", "you applied to X last time") — often after a stall line ("ಒಂದು ನಿಮಿಷ") — yet `get_profile` **never fires** (transcript `tool_calls` show no `get_profile` all call). Consent is skipped and any later `apply_job` uses an id/name sourced from memory, not a live fetch. Looks like the fetch "worked" because the name is right — it didn't.
- **Root cause:** the prompt injects `${contact_memory}` AND carries a memory-resume rule ("if any prior context exists you MUST resume the previous journey" + memory-personalised greeting variants) that competes with the get_profile-driven flow. The model takes the cheaper path: it reads name/role/ids out of the memory block and treats that AS the fetch, so it greets personally, skips the tool, and skips every gate the fetch result was supposed to drive (readiness/consent). Memory becomes a substitute for the fetch.
- **Detection:** read `tool_calls` (not `content`) across several calls — the bot speaks the caller's name/role in the opening but `get_profile` appears **0 times** ⇒ flag. In the prompt, grep the intro for memory-resume language — "resume the previous journey," "if any prior context exists," memory-personalised greeting variants (name/role/"you applied last time" in the opening line) — co-existing with a "fetch first, branch on the result" rule. Any opening that can speak name/role/journey BEFORE a `get_profile` result exists = flag. Also flag a "silent fetch" mandate that never says "reading memory is NOT a fetch."
- **Fix direction:** make the opening a fixed neutral greeting + one qualifying question — **no name / no saved role / no resume line / no stall** in the opening turn. Add a hard guard: `${contact_memory}` is background context only, NOT a `get_profile` result — name/role/readiness may be spoken ONLY after the fetch tool actually returns THIS call; until then treat the caller as not-yet-fetched. Reinforce at the fetch mandate that "reading `${contact_memory}` is NOT a fetch and does not satisfy this step." Keep the memory-injection block itself verbatim. (Sibling to **D29**: D29 = greeting+fetch bundled in one turn suppresses the tool; D32 = memory content stands in for the tool so it never fires. Both end in `get_profile` 0-fires + fabricated downstream ids.)
- **Seen in:** KKB Kannada Signals clone, 2026-07-29 (call `ebb05fd1` — opened "ಒಂದು ನಿಮಿಷ … ನಿಮ್ಮ ಮಾಹಿತಿ ಸಿಕ್ತು, ಪಾರ್ಥ ಅವರೇ" + role, then `apply_job` was the ONLY tool call; name/role/`profile_id` came from `${contact_memory}`). Root cause: legacy "Introduction Priority Rule (Strict Override) → you MUST resume the previous journey" + memory-personalised greeting variants. Fixed by the fixed neutral opener + memory-is-not-a-fetch guard. **Flag:** the base KKB (Hi+Kn out) and Maya carry the same memory-resume intro block — same latent bug on the get_profile-driven paths.

### D33 — Raya prunes a literal empty-object `{}` from `payload_template` → a required object field arrives `undefined`
- **Symptom:** a tool whose API requires a specific field to be an **empty object** `{}` fails HTTP 400 with a validation error like `body/<field> Invalid input: expected record, received undefined` — even though the tool's `payload_template` clearly contains `"<field>": {}`. Reads as a backend/API fault; it is actually the field never being sent.
- **Root cause:** Raya's `payload_template` renderer **drops empty-object literals** (`{}`) at send time (it keeps non-empty objects, arrays, booleans, strings). So `"<field>": {}` is pruned and the request omits the field → the API sees `undefined`. The one value the API wants is the one value the renderer won't transmit.
- **Detection:** when an apply/action tool 400s with "expected record/object, received undefined/null" for a field, GET the tool config and check whether that field's `payload_template` value is a literal `{}` (or any empty container). If so, Raya is pruning it — do NOT keep piling prose on the prompt (the model can't fix a dropped payload field). Confirm the API's real constraint by curling it directly (`{}` vs omitted vs non-empty).
- **Fix direction:** make the field a **whole-value placeholder** — `"<field>": "{{field}}"` — plus a required tool param whose description forces exactly `{}` (a *bare* whole-value placeholder is often substituted typed, unlike an embedded one that stringifies). If the platform stringifies it too (`"{}"` → still 400), escalate a 1-line **backend default** (treat missing/`{}` as `{}`) to the API owner — this is a platform-rendering limitation, not a prompt bug. Never try to satisfy it with a non-empty object if the API rejects additional properties (422).
- **Seen in:** KKB Kannada Signals clone `apply_job`, 2026-07-29 (`requirements_snapshot: {}` in the template → live 400 "expected record, received undefined"; direct curl proved `{}` → 201, omitted/`null` → 400, any key → 422 "must NOT have additional properties"). Switched to `"{{requirements_snapshot}}"` + forced-`{}` param; backend default queued as the fallback.

### D34 — Platform `hold_message` (spoken filler on a tool call) narrates a step the prompt says is SILENT
- **Symptom:** a "silent" `get_profile` (or `create_profile`) is announced aloud anyway — the caller hears "ಸ್ವಲ್ಪ ಕಾಯಿರಿ, ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ನೋಡುತ್ತಿದ್ದೇನೆ" / "…ರಚಿಸುತ್ತಿದ್ದೇನೆ" right before the tool result — even though every silent-fetch rule forbids narration and the prompt has no such line.
- **Root cause:** Raya injects a universal `hold_message` parameter into EVERY tool call (a spoken filler to cover API latency); the model writes a natural sentence into it and Raya speaks it. It is NOT in the tool's `parameters` schema and NOT in the prompt, so grepping the prompt for the phrase finds nothing — the words come from the model populating the platform param. A prompt that only bans "narration" without naming `hold_message` doesn't stop it, because the model doesn't consider filling a tool parameter to be "narration".
- **Detection:** read the tool call's `tool_calls[].function.arguments` (not `content`) — a non-empty `hold_message` on `get_profile`/`create_profile` = flag (it will be spoken). In the prompt, check the tool-silence section explicitly sets `hold_message` to empty `""` for the silent tools by NAME; a silence rule that never mentions `hold_message` is insufficient.
- **Fix direction:** add an explicit rule that names `hold_message` and sets it to a NEUTRAL hold that reveals nothing (e.g. "ಒಂದು ನಿಮಿಷ" / "one moment") for tools that must not announce their action (`get_profile`, `create_profile`) — list the exact reveal phrases to never put in it (anything naming a profile/lookup/creation); allow a genuinely spoken bridge only where intended (`apply_job`). A neutral "one moment" covers API latency without announcing a lookup; empty is also acceptable but users often prefer the neutral filler to dead air — match the owner's preference. If the prompt already bans the neutral phrase elsewhere (e.g. "don't stall in the opening"), scope those bans to the spoken opening so they don't forbid the hold_message value. (This is the platform-param sibling of **D29**: same "silent step gets narrated", but the words come from `hold_message`, not a spoken turn.)
- **Seen in:** KKB Kannada Signals clone, 2026-07-29 (call `2289c071` — `get_profile({..., "hold_message":"ಸ್ವಲ್ಪ ಕಾಯಿರಿ, ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ನೋಡುತ್ತಿದ್ದೇನೆ."})` spoken verbatim; same on `create_profile`). Fixed by an explicit empty-`hold_message` rule for the silent tools. **Flag:** every get_profile-driven agent is exposed — the platform param is universal. **Also fixed 2026-07-30 (overnight):** KKB inbound (Hi `b6222233`/Kn `4ac90bf1`) + KKB outbound (Hi `da612923`/Kn `87ab9108`, ACTIVE in kkb-kn-out call `fa530906` — hold "ನಿಮ್ಮ ಮಾಹಿತಿ ಪರಿಶೀಲಿಸುತ್ತಿದ್ದೇನೆ" spoken + "ಸಿಕ್ತು" on an empty fetch) → neutral hold "एक मिनट"/"ಒಂದು ನಿಮಿಷ"; DKB (Hi `57814ac8`/Kn `d1a1614f`, ACTIVE `cf3fc048`) → EMPTY "" (DKB bans a spoken "one moment"). **Maya out `47fdffe6` + Maya inbound `df99f501` also FIXED 2026-07-30** (Maya-out D34 ACTIVE confirmed via `baf836fe` — create_profile hold "आपकी जानकारी तैयार कर देती हूँ" narrated). D34 now CLOSED across all get_profile-driven bots (KKB Signals + KKB in/out + DKB + Maya in/out).

### D35 — `draft` profile handled inconsistently: known fields re-asked AND/OR consent skipped
- **Symptom:** on a caller whose fetched profile is `lifecycle_status: "draft"`, the bot both (a) re-asks fields the draft already contains (e.g. asks age + gender when `item_state` already has age=25, gender=Male), and (b) fires `create_profile` WITHOUT asking the consent question. The two errors pull in opposite directions (treats the draft as "new" for data collection, as "already-consented" for consent).
- **Root cause:** a `draft` profile is an in-between state (has data, but not live because consent is missing). If the prompt frames the NOT-READY path as "the live profile is built from what you gather this call," the model reads it as "new caller → collect everything" and re-asks known fields; simultaneously, because a profile *was found*, the model assumes consent already happened and skips the gate. The draft's real meaning — complete data but no consent — is not stated crisply.
- **Detection:** on a `draft`-profile call, read the transcript: age/gender questions asked despite `get_profile` `item_state` carrying them = flag (a); `create_profile` fired with no preceding consent ask = flag (b). In the prompt, check the NOT-READY/create path (1) explicitly says to REUSE every `item_state` field the draft already has (ask only genuinely-missing), and (2) makes the consent ask a HARD BLOCK that fires even when a draft was found ("a found draft is NOT consented"). Framing like "the profile is built from what you gather this call" without the reuse clause = flag.
- **Fix direction:** state the draft meaning explicitly — reuse every present `item_state` field verbatim (never re-ask age/gender/name/location/experience the draft carries; a draft with age+gender filled needs NEITHER re-asked → go straight to consent); AND make consent a HARD BLOCK on `create_profile` that applies to draft AND new callers, with the reason ("draft = not live *because* consent is missing; finding one ≠ consent given"). Keeps Srivatsa's rule that every create records consent.
- **Seen in:** KKB Kannada Signals clone, 2026-07-29 (call `2289c071` — draft profile had age=25 + gender=Male + name + location + experience; bot re-asked age & gender and skipped consent, then created a still-draft profile). Fixed by the reuse clause + consent HARD BLOCK. **Flag:** any Signals (consent-gated) agent with a draft lifecycle.

### D36 — Ranking pads the batch to N with irrelevant-role jobs instead of filtering to relevant
- **Symptom:** the caller states/confirms a role, but the presented batch leads with or includes clearly unrelated roles — e.g. an EV-charging-technician job offered first (or as filler) to a confirmed data-entry seeker — because the rule insists on showing three.
- **Root cause:** the presentation rule *ranks* but never *filters*: "present the 3 best-fit jobs" makes 3 a target, so when fewer than 3 relevant jobs exist the model fills the remaining slots with unrelated roles, and a mediocre sort can even float an unrelated job first. Ranking-only ≠ relevance-gating.
- **Detection:** in a transcript, a presented option whose role is unrelated to the caller's known role (not a synonym/same-family variant) = flag, especially if it's option one or a filler to reach three. In the prompt, check the presentation rule has a relevance FILTER (when role is known, show only role-relevant jobs; do NOT pad to N) — a bare "present the 3 best-fit" with only a "role-matched first" sort is insufficient.
- **Fix direction:** add a relevance filter gated on role-known: build the batch from ONLY same-role + same-family jobs, best-fit first, up to N; never pad with unrelated roles (1 relevant → show 1). Keep the "ask for more/other → draw from the rest" fallback so nothing is permanently hidden; if zero match, name what IS available or No-Match rather than pad. Leave the unknown-role path (pool overview) unchanged.
- **Seen in:** KKB Kannada Signals clone, 2026-07-29 (call `2289c071` — confirmed data-entry seeker shown EV-charging technician as option one + remote customer-support as filler). Fixed with the relevance filter + no-pad rule in the Default Presentation Rule and Step 2.

### D37 — Multi-profile fetch: bot applied to `items[0]` (a stale draft) while a live profile sat later in the array → PROFILE_NOT_LIVE
- **Symptom:** on a Signals agent, `apply_job` fails `422 PROFILE_NOT_LIVE: source_item is not live` even though the caller clearly HAS a usable profile — and the bot went straight to apply (no `create_profile`), so it "thought" the profile was ready.
- **Root cause:** the Signals participant can own **multiple** profile items (up to 5), and `get_profile` returns them all in `items[]` in no guaranteed order. A stale `draft` can sit at `items[0]` while the `live` one is at `items[1]`. A prompt that reads **`items[0]`** (or says "items is newest-first, use the first") picks the draft and applies to it → PROFILE_NOT_LIVE. Compounding: `create_profile` (no `item_id`) mints a NEW live profile each call instead of flipping the existing draft, so users accumulate draft + live items and the draft persists at the front. Also a trap: participant-level `user_consent` can be all-`true` while a specific item is still `draft` — so keying readiness on `user_consent` (instead of the item's `lifecycle_status`) also mis-reads a draft as ready.
- **Detection:** read the `get_profile` result — if `items` has >1 entry, check whether the `apply_job` `profile_id` matches an item whose `lifecycle_status` is `"draft"` while another item is `"live"` = flag. In the prompt, grep the response-reading + readiness rules for `items[0]` / "use the first item" / "newest first" as the way the profile is chosen, and for any readiness decision keyed on `user_consent` rather than the item's `lifecycle_status` = flag.
- **Fix direction:** select the profile **by lifecycle, not by position** — scan ALL `items`; if ANY is `lifecycle_status: "live"`, use that live item's `item_id` as `profile_id` and apply directly (ignore any stale draft); only if NO item is live (all draft / empty) → `create_profile` (with consent) then apply. State explicitly "never apply to a `draft` while a live item exists" and "`user_consent: true` ≠ the item is live". Point every downstream rule (readiness gate, HARD GUARD, apply preconditions, age/gender field-reuse) at the *selected* item, not `items[0]`. (`items[0]` remains correct for the `create_profile` RESPONSE, which returns a single new item.)
- **Seen in:** KKB Kannada Signals clone, 2026-07-29 (call `eaa3f2d1` — `get_profile` returned `[{2d1510d6 draft},{300a4a0b live}]`; bot applied to the draft `items[0]` → PROFILE_NOT_LIVE). Fixed by the live-item selection rule across the reading section + gate + guard + preconditions. **Flag:** every Signals agent — any returning caller with >1 profile hits this.

### D38 — Signals dropdown field sent an off-enum value → 400 INVALID_ITEM_STATE
- **Symptom:** `create_profile` / `update_profile` fails `400 {"error":"INVALID_ITEM_STATE","message":"...must be equal to one of the allowed values..."}`, usually because the bot passed the caller's raw spoken phrase into a dropdown field.
- **Root cause:** several Signals `item_state` fields are strict enums (per the Job Seeker schema): `workExperience` ∈ {Fresher, Worked before, Returning after a break}; `gender` ∈ {Male, Female, Other, Don't want to share}; `natureOfJobsInterestedIn` ∈ {Internship, Apprenticeship, Full-time, Flexible}. The API validates them and rejects anything else (verified: `workExperience:"one year"`, `gender:"ladka"`, `nature:"koi bhi"` → 400). If the prompt/tool don't force the model to MAP the spoken answer to an allowed value, it sends the raw phrase and the write fails.
- **Detection:** read the `create_profile`/`update_profile` `tool_calls[].arguments` — an enum field carrying a free phrase (not one of the allowed values) = flag. In the prompt, check there is an explicit "allowed values (map to EXACTLY one)" list for `workExperience`/`gender`/`natureOfJobsInterestedIn`, and that the tool param descriptions name the allowed values. Absence = latent 400.
- **Fix direction:** add an enum-mapping block to the create/update rules (spoken answer → exact allowed value) and put the allowed set in the tool param `description`s. Never let a raw spoken phrase reach an enum field. Free-text fields (`nameOfJobRolesInterestedIn`, `location`, `name`) are exempt.
- **Seen in:** KKB Signals bots (Kn + Hi), 2026-07-29 (schema `Jobs Signal Schemas Apr 2026.xlsx`; API 400 on off-enum values). Fixed by the enum-mapping block + enum-bearing tool descriptions. **Flag:** every Signals agent writing profiles.

### D39 — Signals write fails / duplicates the profile: double-prefixed phone, or non-Latin payload values
- **Symptom:** `create_profile`/`update_profile` silently mints a NEW profile (`user_existed:false`) or 403s `ITEM_NOT_OWNED_BY_USER`, so nothing the bot gathered actually persists. Sometimes the saved `name`/`location` come out in Devanagari/Kannada.
- **Root cause:** (a) **phone double-prefix** — the model passed the profile's stored 12-digit phone (`91XXXXXXXXXX`) into a template that prepended `+91` → `+9191…`, which is a different E.164 number → the API resolves/creates a different user and the write lands on the wrong (or a new) record. (b) **non-Latin payload values** — the bot passed the spoken-script name/location (e.g. `"ಪಾರ್ಥ"`, `"कोरमंगला"`) into `item_state`; downstream expects English/Latin. (Note also: `phone_number` must be E.164 with a leading `+` — no `+` → 400.)
- **Detection:** read the `create_profile`/`update_profile` `tool_calls[].arguments` — a `phone` that is 12 digits going into a `"+91{{phone}}"` template (→ `+9191…`), or 10 digits going into a `"+{{phone}}"` template (→ missing 91); any `name`/`location`/`role` in Devanagari/Kannada script. A follow-up `update_profile` that returns `user_existed:false` or 403 `ITEM_NOT_OWNED_BY_USER` = the phone resolved the wrong user. Confirm the tool's phone template vs the phone format the prompt tells the model to pass — they must compose to exactly one `+91XXXXXXXXXX`.
- **Fix direction:** pick ONE phone convention and make the template + prompt compose to a single E.164 value — e.g. phone param = the 12-digit `91`+number, template `"+{{phone}}"` (and `item_state.phone` `"{{phone}}"`). Tell the model to reuse the SAME phone it used for `get_profile` (and that the profile's stored phone is already that 12-digit form). Add a rule that ALL payload values are English/Latin (transliterate spoken names/places), never the spoken script. Verify with curl: E.164 `+91…` → 200; no `+` → 400.
- **Seen in:** KKB Signals bots (Kn + Hi), 2026-07-29 (call `7935ce5a`: `update_profile phone:"91XXXXXX0249"` → `+91919108790249` → new user + 403; `name:"ಪಾರ್ಥ"`, `location:"कोुरमंगला"`). Fixed: templates → `"+{{phone}}"`/`"{{phone}}"`, phone param = 12-digit, English-only payload rule. **Flag:** every Signals write path.

### D41 — doubts question and apply-consent bundled in ONE turn → a "no" (= no doubts) is read as a refusal to apply → willing candidate dropped
- **Symptom:** an engaged caller who explicitly wanted work, picked a specific job, and asked about it is then dropped WITHOUT an application. `call_output` shows `jobs_applied: []` / `applied_to_job: "No"` on a call where `call_engaged: "Yes"` and `jobs_shown: "Yes"`. In the transcript the last caller turn before the close is a bare negative ("no questions", "nothing else").
- **Root cause:** the prompt's job-detail spoken block ended with TWO distinct questions in a single turn — "any other questions?" AND "shall I apply?" (e.g. `ಇನ್ನೇನಾದರೂ ಪ್ರಶ್ನೆ ಇದ್ಯಾ? … ಅಪ್ಲೈ ಮಾಡ್ಲಾ?` / `कोई और सवाल है? … अप्लाई कर दूँ?`). A caller answering the FIRST ("no, no questions") produces a lone "no" that the model may bind to the SECOND, reading it as a decline. **Prose ambiguity, not tool-adherence:** the prompt genuinely instructed a two-question turn, so the model had no unambiguous reading. Behaviour is PROBABILISTIC — the same line resolved correctly on a harness call and incorrectly on two production calls, so a single passing test does not clear it.
- **Detection:** grep every spoken block for a turn containing two question marks with distinct intents — especially a doubts/"any questions" question in the same turn as a commit/consent question ("shall I apply", "should I book", "confirm?"). Then in transcripts: find a bare negative caller turn immediately followed by the bot closing or offering an alternative, with the commit tool never appearing in `tool_calls`. Cross-check `call_output.jobs_applied == []` against `call_engaged == "Yes"`.
- **Fix direction:** **split the turn** — the doubts question ends its own turn and STOPS; the consent/commit question is a separate turn asked only after the caller answers. Then state explicitly that a negative to the doubts question is NOT a refusal (it is a green light to the consent turn), that only an explicit refusal to the CONSENT question declines, and that an unclear answer to the consent question is re-asked once naming the action. Do not try to fix this by adding disambiguation prose to a still-bundled turn — remove the ambiguity structurally. Also covered fleet-wide by generic checklist §14 (one question per turn).
- **Seen in:** KKB Kannada outbound legacy (`KKB Placeholder- Kannada`), 2026-07-28 production campaign — calls `215fdd2d` (candidate said "I need a job right now", picked Machine Operator, said "no questions" → dropped) and `6ee05050` (picked Customer Service → dropped). The identical bundled line was present in all 8 KKB seeker prompts and 4 Maya prompts. Fixed in KKB 2026-08-07. **Flag:** every commit/consent turn in every bot.

---

### D40 — `create_profile` omits `location` → new profile is created `draft` (not live) → `apply_job` PROFILE_NOT_LIVE (new-seeker path)
- **Symptom:** on a Signals agent, a NEW caller (no live profile) completes the flow, but `apply_job` fails `422 PROFILE_NOT_LIVE` immediately after a `create_profile` — and the just-created profile came back `lifecycle_status: "draft"`. Distinct from D37 (which is a multi-profile *selection* bug on an EXISTING caller); here the profile is freshly created and is draft because it is incomplete.
- **Root cause:** Signals only promotes a created profile to `live` when `location` is present in `item_state` (curl-verified: create without `location` → `draft`; with `location` → `live`; `gender` is irrelevant to liveness). `location` was NOT in the `create_profile` tool's `parameters.required` (only `age`/`name`/`phone`), so — even though the prompt's Phase-1 gate lists Location as a minimum-required field — the model skipped asking it and called `create_profile` without it, minting a draft that `apply_job` cannot use. Classic runtime tool-adherence miss (the prose already said to gather location) — see D25: not prose-fixable, needs a schema lever.
- **Detection:** read `create_profile` `tool_calls[].arguments` — a create on the new-seeker path with a missing/empty `location` = flag; pair it with the create response `lifecycle_status: "draft"` and a following `apply_job` `422 PROFILE_NOT_LIVE`. In the agent config, check the `create_profile` tool's `parameters.required` **includes `location`** — if location is only an optional property, the bug is latent.
- **Fix direction:** make `location` a **required** parameter of the `create_profile` tool schema (PATCH the agent's `tools`), so the model physically cannot create a profile without gathering it → the profile is created `live` and is applyable. Do NOT add more prose to force it (the Phase-1 gate already exists; piling on prose regresses per D25). Optionally add the "why" to the `location` param `description`. Keep the existing Phase-1 prose gate.
- **Seen in:** KKB Signals bots (Kn + Hi), 2026-07-29 (agent-to-agent harness call `fb1283cb`: `create_profile` without `location` → draft `3ef4bbd2` → `apply_job` 422 PROFILE_NOT_LIVE). Curl-grounded (no-location → draft; +location → live). Fixed by adding `location` to `create_profile.required` on both agents. **Flag:** every Signals create path.

---

### D44 — Caller-directed verbs hardcoded to the BOT's gender (a feminine-voiced bot misgenders every male caller)
- **Symptom:** a bot with a deliberately gendered persona addresses callers in that same gender regardless of who is on the line. On Maya (female voice) every male caller was asked "आप किस तरह का काम ढूंढ **रही** हैं?" from the greeting onward, and the role-confirm turn told a man "आप अभी [role] का काम कर **रही** हैं".
- **Root cause:** the persona's gender rule ("always feminine — no exceptions") was applied to the *whole spoken line* rather than to the bot's **own first-person verbs**. The spoken templates then baked the feminine caller-address in, and — worse — the rule's own parenthetical explicitly blessed it ("Addressing the caller with the honorific plural — 'आप … कर रही हैं' — is fine"). So every example, greeting and confirm line taught the wrong form, and the model was following the prompt correctly.
- **Detection:** in any gendered language, split every spoken line into *self-reference* and *caller-reference* and check them separately. Concretely: the bot's own verbs end in the first person (`रही हूँ` / `रहा हूँ`); caller-directed verbs take the honorific plural (`रहे हैं` / `रही हैं`). Grep for the honorific-plural feminine form (`रही हैं`) — on a feminine-persona bot, **every** hit is a caller-address and every one is a latent misgendering. Then check whether the gender rule's wording itself endorses it. Gender-neutral languages (Kannada 2nd-person plural) are unaffected — do not "fix" them.
- **Fix direction:** state the scope explicitly — the persona's gender governs **first-person verbs only**; caller-directed verbs follow the **caller's** gender (from the fetched profile, or evident from the caller's own speech), defaulting to the masculine honorific (`रहे हैं`), which is the neutral form when gender is unknown — and that includes the greeting and every turn before the profile returns. Then correct every spoken template and worked example, not just the rule. **Beware self-clobbering:** if you mass-replace the feminine form after rewriting the rule, the rule's own correct female-caller example gets replaced too — rewrite the rule *after* the sweep, or assert its final text.
- **Seen in:** Maya, all four prompts (Hindi out/in, Signals out/in), 2026-08-12 — 19/17/21/19 caller-directed feminine forms per file, including the greeting itself, so it fired on turn one of every call to a male graduate. KKB's twin templates were already correct (`कर रहे हैं`), which is the fastest way to spot it: **diff the sibling agent's spoken line against yours.**

### D45 — An internal structure name spoken aloud to the caller ("this inventory", "the database")
- **Symptom:** the caller hears the machinery. On a live call the bot said "ಈ **inventory**ನಲ್ಲಿ ಬೆಂಗಳೂರಿನ ಕೆಲಸಗಳು ಇಲ್ಲ" ("there are no Bengaluru jobs in this inventory") — twice in one call — instead of simply "there are no jobs in Bengaluru right now".
- **Root cause:** the prompt names its own hardcoded job list **"Job Inventory"** and refers to it in dozens of instructions, but never says that the phrase is internal. Every other machinery word in these prompts is explicitly forbidden ("never say प्रोफ़ाइल / memory / terms / API"); this one was not, so the model reused the prompt's own vocabulary in speech. The failure is invisible to a static read of the section — it only shows up in a transcript.
- **Detection:** list every internal noun the prompt uses for its own data structures (`Job Inventory`, `recommendations`, `array`, `list`, `payload`, `profile`, `database`, `system`) and confirm each has an explicit never-say-aloud rule. Then grade transcripts for those words directly — including transliterated and code-switched forms, which is how they actually surface (`inventory` sitting inside a Kannada sentence). A bot that is otherwise perfectly factual will still fail here.
- **Fix direction:** add one rule beside the section that owns the structure: the name is internal, never spoken; state the fact in human terms instead, with a correct/incorrect spoken pair in that language ("ಈಗ [city] ನಲ್ಲಿ ಜಾಬ್ ಇಲ್ಲ", never "ಈ inventory ನಲ್ಲಿ..."). Roll it to every language variant with its own adapted example.
- **Seen in:** KKB Kannada legacy inbound 2026-08-12 (call `077ea55c`). Fixed across all six inbound prompts (KKB ×4, Maya ×2), which are the ones carrying a hardcoded Job Inventory.

### D46 — Consent captured and the line dropped in the same breath: the caller cannot learn what they just agreed to
- **Symptom:** the caller accepts an offer (a service, a callback, a referral) and the bot confirms + says
  goodbye in ONE utterance. The caller's follow-up ("what is this?", "who will call?") lands on a dead
  line. Consent is recorded as Yes but was never informed.
- **Root cause:** the accept branch ends in a bare "Then close."; the exit section's opening rule says
  "close as soon as the answer has been captured"; and the worked accept examples bundle confirmation +
  valediction + the hangup token into one spoken line, so the model completes the familiar string.
  The prompt's sanctioned "what is this?" answer usually EXISTS but is gated on "if they have not
  answered yet" — shut in exactly this state — while one-offer / never-pitch-twice / brevity rules and a
  per-response dignity check independently suppress any post-acceptance sentence.
- **Detection:** for any turn that captures CONSENT to something the caller has not had described to
  them, confirm (1) the confirmation turn is its own turn that ENDS and WAITS, with the closing line and
  the hangup token explicitly forbidden in it; (2) a sanctioned one-sentence answer exists and is
  reachable AFTER the yes, not only before it; (3) the one-offer / never-repeat / brevity / dignity-check
  rules explicitly state that answering a question is not a second offer; (4) at least one worked example
  shows the post-acceptance question exchange, and NO example shows the bundled accept+goodbye; (5) the
  silence handler has an exception so silence on that turn closes warmly instead of firing the bad-line
  exit; (6) the captured value records the FINAL answer, so a withdrawal after the clarification is not
  stored as Yes. A prompt where "what is this?" is answerable only BEFORE agreeing = flag.
- **Fix direction:** split the accept utterance into confirm-and-invite (no hangup token) + close;
  ungate the sanctioned answer; cap it at ONE clarification to hold the call length; disarm each
  suppressor by name; rewrite every bundled example as two turns; add the silence exception and the
  last-answer-wins capture rule.
- **Seen in:** TRRAIN Hindi outbound, call cef6523a, 2026-08-12 (caller accepted, then reached a dead
  line asking what the service was). Same shape found latent in all 4 Maya files (Need Capture has no
  reserved post-accept turn and no anti-bundling rule, while the MPL offer in the same file has one);
  KKB's 8 files were audited and do NOT have it (accept is an acknowledgement only + Graceful Exit
  already confirms "nothing else to ask").

## E. Examples, consent & standing rules

### E1 — Few-shot examples contradict the rules (incl. cross-branch opening bleed)
- **Symptom:** the agent does the thing the prose forbids / skips a mandatory step. Special case: a control variable (e.g. `new_seeker`) is supposed to pick between two different openings, but the agent uses the wrong branch's opening — because an example modelled it.
- **Root cause:** an example models the shortcut/opening. Models mimic concrete examples over abstract prose, even with a "don't mimic examples" disclaimer. When two branches have different openings, an example for one branch bleeds into the other unless the branch variable is the decisive router AND every example is labelled with its branch value. **Adding a new example (or a salient new section) to lock in feature X can silently regress a working branch Y.**
- **Detection:** walk each example against the mandatory flow. Any example that skips a "mandatory" step, contradicts a canonical spoken line, uses a different greeting, or contains garbled text = flag. When a control variable selects between openings/paths, confirm EVERY example states its variable value in context and that no example's opening could be copied onto the other branch. Count how many examples model each opening — a lopsided majority pulls the model that way regardless of the branch value.
- **Fix direction:** repair examples to model the mandatory path and match canonical lines. For branch-conditioned openings, make the branch variable the **decisive router** (explicitly forbid each branch's opening on the other side) AND label every example with its branch value. **After adding any example, re-test the OTHER branch — the branch it does not depict is the one at risk.**
- **Seen in:** KKB/Maya (feature/behaviour patterns learned from examples); Purple Dots review (Example 1 skips Solution Enablers; Ex 2 greeting garbled + skips `get_profile`); Maya 2026-07-13 (adding Example 5 — a `new_seeker="yes"` pool-overview walkthrough — plus a salient Step 1 overview made the model open EVERY call, including `new_seeker="no"`, with the experience question + overview and skip the mandatory profile fetch; a "no" call that worked one test earlier regressed the moment the competing "yes" example landed. Fixed with a decisive new_seeker router forbidding the yes-opening on the "no" path + labelling every example's new_seeker value + **removing the competing from-greeting "yes"-overview example** (prose gates alone did not overpower it — the example itself had to go; the overview behaviour stayed in prose)).
- **Inventory-swap variant (hardcoded inventory + stale examples):** when a bot carries a **hardcoded job inventory JSON** and that inventory is swapped/repointed, but the surrounding "What's available" line, the role synonym / job-family table, the Case-B pool overview, the canonical-location list, and the example dialogues still reference the **OLD** inventory's companies/roles/locations → the model presents the example jobs (which are NOT in the current inventory) = hallucination + apply on a non-inventory item. **Detection:** cross-check EVERY company/role/location named anywhere in the prose + examples against the CURRENT inventory JSON; any named job entity absent from the JSON = flag. A section header that claims "all jobs shown are drawn from the inventory above" while the examples show other jobs is a hard flag. **Fix:** rewrite the "What's available"/synonym/overview/canonical-locations + every example to reference ONLY the current inventory jobs (do not touch the real `job_id`s). **Seen in:** KKB Hi/Kn inbound + Maya inbound Signals 2026-08-01 — inventory swapped to 4 real Signals jobs (Data Entry/Kashi, Remote CSE/Rampur, EV Tech/Yamuna, AC Tech/Krishna, Bengaluru/Remote) but the examples/synonyms/overview still walked the old Ghaziabad/Noida retail-food set (McDonald's, Burger King, CY Future, Weavings, Cashier, Sales).


- **2026-08-07 (Maya, call `44d9aff4`) — spoken-identity literals in sample dialogues.** A prompt whose opening TEMPLATE correctly used `[college_name]` still spoke the wrong college, because worked example dialogues lower down hardcoded real institution names in the agent's spoken lines. Passed `college_name: "VTU"`, the agent said "सरस्वती कॉलेज" twice. **Detection:** for every `${variable}` that is spoken aloud as an identity (college, employer, city, scheme, persona name), grep the prompt for any REAL value of that variable appearing inside an example — if a sample dialogue contains a concrete institution/company/place where the live call would substitute a variable, it is a copy source. **Fix:** write the placeholder (`[college_name]`) in example dialogues too, never a realistic value, and add a rule that no example value is ever spoken. Keep concrete values only in non-spoken pedagogy (e.g. transliteration mappings) and cover them with that rule.

### E2 — Consent handling: multiple gates, single-ask, hard-stop on decline
- **Symptom:** consent re-asked (see B1), or a decline doesn't cleanly stop the flow, or two different consents (recording/data vs sharing) get conflated.
- **Detection:** enumerate every distinct consent gate. For each: is it asked exactly once, and is there a clear "on decline, gently stop and make no tool calls" hard-stop? Are distinct consents kept distinct?
- **Fix direction:** one ask per gate, explicit decline hard-stop, distinct wording per gate.
- **Seen in:** Purple Dots review.

### E3 — Memory-injection block missing (repo standing rule)
- **Symptom:** a memory-enabled agent doesn't receive per-caller context.
- **Root cause:** the conversation prompt lacks the exact `### Contact context / Here is the caller context: / {${contact_memory}}` block required by repo `CLAUDE.md` for any agent with memory enabled.
- **Detection:** if the agent has (or should have) a memory prompt, confirm the block is present **verbatim** in every language file. Distinguish a live-profile fetch (`get_profile`) from cross-call memory — if only the former exists, flag as **Verify** (confirm whether cross-call memory is intended).
- **Fix direction:** route to `/update-memory` to add the block.
- **Seen in:** repo `CLAUDE.md` rule; DKB 2026-06-29 (block was missing, added).

### E4 — Guard sections thin or absent
- **Symptom:** unsafe/off-scope handling, missing age/eligibility hard-stop, options that aren't physically realistic for the disability/context.
- **Detection:** confirm presence of: forbidden-topics list, dignity/safety check, eligibility/age hard-stop, relevance + functional-sanity rule (options realistic for the stated condition), and a scope-boundary list (what the bot must never promise/do).
- **Fix direction:** add the missing guard.
- **Seen in:** standard across agents; sanity-check formalized in Purple Dots review.

---

## F. Cross-language (pointer)
Drift between an agent's Hindi and Kannada files (AGNOSTIC logic landing in one language only)
is its own audit — **don't reimplement it here.** This skill reviews one file. For parity, run
`/sync-check`. Flag only: "this change looks language-agnostic and should be sync-checked
against the twin."

---

## G. Templating & variable interpolation

### G1 — Variable placeholder precedes its label in a binding phrase (garbles after interpolation)
- **Symptom:** a branch/decision that depends on a control variable behaves as if the value were missing or wrong, even though the variable is passed correctly. Structural fixes, hard gates, and case-normalization all fail to help — because the value never actually binds.
- **Root cause:** the prompt binds the variable with the **placeholder first**, e.g. `Consider ${new_seeker} as new_seeker.` At runtime `${new_seeker}` is interpolated to its value, so the model literally reads **"Consider no as new_seeker"** — the value is presented *as if it were the label*, so "new_seeker = no" is never established. The model is left with no clean value and falls through to a default / natural-conversation path.
- **Detection:** scan for any binding/assignment phrase where a `${VAR}` placeholder appears **before** its human-readable label — `Consider/treat/use/read ${X} as X`, `${X} as x`, etc. Mentally interpolate it: does it still read as "x = <value>"? If it reads backwards ("<value> as x"), flag it — **critical** for any variable that drives a branch (new_seeker, flags, modes), lower for glossary lines that have a description to disambiguate.
- **Corollary — bind the value AT the decision, not in a block far away.** A branch that says "read the block above" makes the model go and find an unlabelled blob, then judge it. Printing the value inline where the choice is made, bound to its name (`contact_memory is: ${contact_memory}`, `applied_job_role is: ${applied_job_role}`), removes both steps. Two independent wins in one day: TRRAIN's job-title branch fixed first try, and the KKB returning-caller branch reworked this way after four other fixes failed. When someone proposes such a binding, check the ORDER before adopting it — the natural phrasing "let ${X} be X" is value-first and reintroduces exactly this bug.
- **Fix direction:** put the **label first, placeholder last** — `Consider new_seeker as ${new_seeker}` → interpolates to "Consider new_seeker as no" (binds cleanly). General forms: `<var_name> is ${VAR}` / `<var_name> = ${VAR}`.
- **Seen in:** Maya 2026-07-13 (`Consider ${new_seeker} as new_seeker` interpolated to "Consider no as new_seeker"; the `new_seeker="no"` branch never fired until the order was flipped to `Consider new_seeker as ${new_seeker}`. This — not the section deletion or gates — was the actual fix). **KKB 2026-07-13** — same backwards binding found in both `KKB Placeholder Hindi.md` and `Kannada.md` (two places each: the Contact-Variables glossary line and the Profile-Handling step) once the fork was reported broken there too; flipped both to `Consider new_seeker as ${new_seeker}` and simultaneously fixed a co-located **A4** header/body contradiction ("caller already has a profile" vs "MANDATORY … IF USER PROFILE DOES NOT EXIST"). **Lesson:** when this bug is confirmed in one agent, grep every sibling for the same `Consider ${VAR} as VAR` pattern immediately — it had been catalogued as "latent in KKB" for days before the fork broke in production.

### C11 — DKB create_job not emitted on the post-consent turn (D25 runtime tool-adherence; language-variant-specific)
- **Symptom:** the employer bot completes the whole job-capture flow, the owner consents ("post it"), the bot says "done" — but no `create_job` tool call is emitted (hallucinated post), OR it mis-fires `update_job` with a non-existent/`"Not Available"` `job_id` (→ 400 "Invalid UUID"). Net: no job is actually posted.
- **Root cause:** runtime tool-adherence (D25) — the model does not emit the mandatory `create_job` on the consent turn. A contributing prompt trap: a Phase-2 "immediately call `update_job` whenever a persisted field is provided" rule can BLEED into Phase 3 (new posting, no `item_id`) → wrong tool. Scoping that rule to Phase 2 + a hard "Phase 3 = create_job once, never update_job" rule fixes the *wrong-tool* case but does NOT reliably force the model to emit `create_job` (the no-tool hallucination persists).
- **Detection:** in a transcript, at the consent→post turn, confirm an ACTUAL `create_job` tool call with a real payload appears — not just the spoken "posted/done". Grep the tool_calls, not the content. Check the tool used is `create_job` (new) vs `update_job` (existing item_id only). Language-variant-specific: DKB Kannada exhibited this while the Hindi twin fired `create_job` cleanly — always test BOTH language variants.
- **Fix direction:** (1) scope per-field `update_job` to Phase 2 / a real `item_id`; forbid `update_job` with a missing/`"Not Available"` `job_id`. (2) **REDUCE the phase's tool ambiguity** — the strongest lever that actually worked: when Phase 3 held THREE tools (`get_talent_insights` + `update_job` + `create_job`), the model kept mis-firing/omitting `create_job`; **removing `get_talent_insights` (no Signals endpoint) so Phase 3 has only `create_job` made DKB Kannada fire `create_job` reliably** (2026-08-01). Fewer competing tools on the decision turn = less non-adherence. (3) If ambiguity is already minimal and the no-tool hallucination persists, THAT residue is not prose-fixable (D25) → platform backstop / tool-schema required-action. Do not keep adding prose.
- **Seen in:** DKB Kannada Signals 2026-07-31 (calls 2e350d57 no-tool, blysb9o81 update_job-400, 7577055a no-tool after the hard rule) — **RESOLVED 2026-08-01** once `get_talent_insights` was removed from Phase 3 (retests 3177339f fired `create_job` cleanly). DKB Hindi Signals (09a7b6c8) always fired create_job correctly. Lesson: before declaring a tool-adherence miss "unfixable," check whether a competing/unused tool in the same phase is the confuser and can be removed.

### C12 — Tool unmapped on a migrated backend kept as a "backend dependency" stub → dead step / fabrication risk
- **Symptom:** after a backend migration (e.g. ONEST → Signals), a tool that has **no endpoint on the new backend** is kept in the prompt + agent config "as a backend dependency," with a fallback line for when it "returns nothing." The tool can only ever return nothing, so the whole dependent conversational step (e.g. a market-picture / insights delivery) is dead weight that stalls, invites fabrication of the missing numbers, or triggers D25-style non-adherence — and a persona promise that depends on it ("I show the true market picture") becomes a lie the bot can't keep.
- **Root cause:** the flow structure was migrated verbatim without pruning the tools that don't exist on the new backend.
- **Detection:** for each tool the prompt calls, confirm it actually resolves on the CURRENT backend (check the live agent's tool list vs the prompt's tool calls). A tool documented as "NOT yet mapped / backend dependency / may return nothing" that gates a spoken step = flag. Also grep persona/intro lines for promises that depend on the dead tool.
- **Fix direction:** if no equivalent endpoint exists, **REMOVE the tool from the agent config AND delete the dependent conversational step** + any persona promise that relied on it — do not keep a fabrication-prone stub. If/when the endpoint is wired, re-add both. Mirror the removal across language twins.
- **Seen in:** DKB Hi/Kn Signals 2026-08-01 (`get_talent_insights` — ONEST/Dhiway tool, no Signals endpoint; removed the tool + the entire Phase-3 market-picture step + the `Market Truth Delivery` section + market-data error/silence branches, and softened the persona's "true picture of the local talent market" promise).

### G2 — A literal `${...}` written as an EXAMPLE becomes a phantom declared agent argument
- **Symptom:** the live agent's `agent_args` on Raya contains a junk entry (e.g. `"..."`) that no campaign ever sends, alongside the real variables. Harmless-looking, but it means the platform's declared input contract for the agent is wrong, and anyone reading `agent_args` to build a campaign payload sees a variable that does not exist.
- **Root cause:** Raya **derives `agent_args` from the `${...}` tokens found in `instructions`** — it is not settable via the API at all (`PATCH` rejects the key). So *any* `${...}` sequence in the prompt is treated as a declared input, including one written purely as an illustration inside a rule such as *"Never speak `${...}` syntax aloud."*
- **Detection:** grep the prompt for `${` and check every hit is a REAL input variable. Any `${...}`, `${VAR_NAME}` used as a generic placeholder in explanatory prose, or a variable named in an example that the campaign never sends, is a phantom. Cross-check against the live agent's derived `agent_args`: an entry there that no campaign sends confirms it.
- **Fix direction:** never write `${...}` as an illustration. Describe it in words instead — "never speak variable syntax (a dollar sign with braces) aloud". Keep `${...}` reserved exclusively for genuine inputs.
- **Seen in:** TRRAIN Hindi + Kannada 2026-08-10 (first build wrote *"Never speak `${...}` syntax"*; Raya derived a phantom `"..."` argument on both new agents. Reworded before the bots were used).

### A9 — A new conditional branch is silently defeated by a surviving "ALWAYS the same X" rule elsewhere
- **Symptom:** a newly added branch never fires at runtime even though its trigger condition is plainly satisfied and its input variable is confirmed present in the call's `agent_args`. The model always takes the original/default path. Adding *more* detail to the new branch does not help.
- **Root cause:** an earlier, heavily-reinforced absolute rule ("the call ALWAYS opens with the SAME neutral greeting", "use this ONE line on every call") is still in the prompt and outranks the new conditional. The two instructions contradict, and the one repeated with more force and more "never" clauses wins. This is a **contradiction** bug, not an under-specification bug — the classic wrong response is to pile on more prose for the new branch (see D25), which makes the conflict worse.
- **Detection:** whenever a branch is added to a step that previously had exactly one fixed behaviour, grep the WHOLE file for absolutes about that step — `ALWAYS`, `the SAME`, `this ONE`, `on every call`, `regardless of` — and confirm each was rewritten to admit the new branch. **Then widen the search to behavioural absolutes that do not name the step at all** — the killer is usually a sentence like *"behave like a new caller until X"*, *"treat them as unknown until Y"*, *"say nothing personal before Z"*, sitting in a NEIGHBOURING paragraph and scoped to a *different* concern. Grep for `behave like`, `treat .* as`, `until the .* returns`, `nothing .* until`. Also check the sample conversations: if every example still shows the old single path, they reinforce the absolute (see **E1**). Confirm the input really arrives before blaming the prompt.
- **Expect more than one, and after the contradictions are gone check FREQUENCY.** Fixing the obvious absolute is usually not enough — a live re-test is mandatory after each attempt, because the next blocker only surfaces once the previous one is gone. And once no contradiction remains, count occurrences: **grep how many times each branch's spoken line appears in the whole prompt.** If the old/default line appears many times (spec plus most of the sample conversations) and the new branch's line appears once or twice, the model is being trained by repetition to prefer the default no matter how clearly the rule is written. That is **E1** acting on a branch rather than on a value. Fix it by qualifying every example that shows the old line ("the memory holds no prior conversation here, so the default is correct — it is not the only opening") and by stating explicitly that example frequency is not a signal about which branch to prefer. Also re-read your own safety wording: a well-intentioned "when in doubt, use the default" tiebreaker will resolve every uncertain case against the new branch, so scope it to the cases that genuinely fail the test.
- **Look for an ARCHITECTURAL prohibition, not just a wording clash.** The hardest instance is a rule that forbids the new branch *by construction* while being written about something else entirely. In KKB the Profile-Handling section said **"branch on WHAT COMES BACK, never on an input variable"** — written years earlier to kill a `new_seeker` mis-routing bug. The new returning-caller branch decides from an input variable (`${contact_memory}`), so that one clause categorically forbade it, from a section about tool results rather than greetings. Grep for universal prohibitions of a MECHANISM (`never on an input variable`, `never from`, `only ever from`, `there is no fork`) and ask whether the new branch uses that mechanism. Fix by scoping the old rule to the decisions it was actually written for, and saying explicitly that the two decisions are independent.
- **Four rounds happened in practice.** Do not assume two or three is the ceiling. Each round costs a live call, so run the full sweep — contradictions, behavioural absolutes, frequency, and architectural prohibitions — *before* the next test rather than fixing one thing per call.
- **Fix direction:** rewrite the absolute into an explicit N-way choice ("the call continues with exactly ONE of TWO openings — …"), state the decision **before** the alternatives, and name the concrete evidence that selects each branch. Then re-test the branch live — a branch is not fixed until a transcript shows it firing.
- **Seen in:** KKB Hindi Signals 2026-08-10 — a returning-caller callback line driven by `${contact_memory}` did not fire on a call whose `agent_args` carried a full memory record with `last_conversation_summary`. **It took two rounds.** Round 1: the Opening Rule still said the call "ALWAYS continues with the SAME neutral greeting" — rewritten into an explicit two-opening choice with the decision stated first. A live re-test showed the branch STILL did not fire. Round 2 found the real blocker one paragraph above, in the `${contact_memory}` caveat: *"treat the caller as NOT-yet-fetched (**behave like a new caller until the tool result arrives**)"*. Because the callback line is spoken BEFORE `get_profile` runs, that sentence instructed the model to act as if the caller were new at exactly the moment the branch was supposed to fire — a contradiction written about the *profile fetch*, which silently governed the *greeting*. Fixed by scoping it explicitly to profile details and stating that referring to a remembered CONVERSATION needs no fetch. **Lesson: the sentence that defeats a new branch often is not about that branch, or even about that step.**

### G3 — A `[bracketed]` placeholder in a spoken line makes the MODEL do the substitution (spoken aloud, wrong value, or branch dodged)
- **Symptom:** one of three failures, all from the same cause. (a) The bot speaks the placeholder itself — "मैं माया, **[college_name]** की ओर से". (b) The bot speaks a *wrong* real value it copied from somewhere else in the prompt. (c) The bot silently avoids the line altogether and takes an adjacent "value unknown" branch, even though the value WAS supplied — because filling the bracket is work it can dodge.
- **Root cause:** `${var}` is substituted by the **platform** before the model ever sees the prompt; `[var]` is a human convention the **model** must resolve at generation time. Anything the model must resolve, it can resolve wrongly, skip, or read out literally. A bracketed placeholder inside a line the agent SPEAKS is therefore a latent bug, and the failure mode differs from call to call — which makes it look flaky rather than systematic.
- **Detection — and the discrimination that matters.** Grep every spoken line (quoted text the agent says) for `[` … `]`, then classify each hit. **Only ONE class is a bug:**
  - **BUG — the bracket stands for an INPUT VARIABLE that has a `${var}` form.** `[college_name]` when `${college_name}` is an input; `[role]` when `${applied_job_role}` is an input. The platform could have substituted it and didn't, purely because it was written in brackets. Fix these.
  - **NOT a bug — the bracket stands for something no `${var}` can carry.** A value from a TOOL RESULT (`[role]` read out of a `get_profile` response, `[company]`/`[location]` read out of an item in `${recommendations}`), or a value from CONVERSATION STATE (`[age]`, `[gender]`, `[नाम]` the caller just gave). The model necessarily fills these; there is no platform variable to use instead. Leave them alone.
  - **NOT a bug — the bracket appears inside a PROHIBITION or a non-spoken note** (e.g. *never say "आपने [profile role] के लिए अप्लाई किया था"*). It is illustrating what not to say.
  So the test is not "is there a bracket in a spoken line" — it is **"does an input variable exist that could have carried this value?"** A fleet-wide sweep on 2026-08-10 found brackets in spoken lines in 20 of 20 conversation prompts, and all but two were legitimate tool-result or state placeholders that have run correctly in production for months. Reporting those as findings would be noise; changing them would be an unrequested rewrite of working prompts.
- Cross-check the branch next to a genuine hit — if there is an "unknown value" fallback line and transcripts show the fallback firing while the args carried a real value, that is failure mode (c).
- **Fix direction:** put `${var}` **directly in the spoken line** so the platform substitutes it, and instruct how to pronounce/transliterate the substituted value rather than how to fill a bracket. Where a real-vs-unknown branch exists, hand the model the interpolated value explicitly for the decision (`applied_job_role is: ${applied_job_role}`, label first — see **G1**), state that the branch depends on that value and nothing else, and say plainly that the unknown line is only for a genuinely unusable value. Keep brackets only in non-spoken prose.
- **Seen in:** **Maya 2026-08-09** — `[college_name]` in the opening; removing a hardcoded example stopped the wrong-college bug but the bot then read "[college_name]" aloud; a first fix ("this is a slot, not words") was re-tested and did NOT work; replacing all 43 occurrences with `${college_name}` fixed it. **TRRAIN Hindi 2026-08-10** — failure mode (c) on the very first live call of a brand-new bot: `agent_args` carried `applied_job_role: "Data Entry Operator"` but the bot spoke the generic "एक जॉब के लिए अप्लाई किया था", dodging the `[role]` bracket. Fixed by inlining `${applied_job_role}` and making the branch read the interpolated value. **Lesson: this is now a three-time bug across two agents — treat any bracket in spoken text as a defect on sight, and never introduce one in a new prompt.**

### G4 — `memory_enabled` silently overrides the `${contact_memory}` passed in `agent_args`
- **Symptom:** a branch that reads `${contact_memory}` never fires, no matter how clearly it is written, even though the call's `agent_args` demonstrably carries a full memory record. Removing every competing rule changes nothing. It looks exactly like runtime non-adherence (**D25**) and invites the wrong conclusion.
- **Root cause:** on Raya, `memory_enabled=true` means the **platform owns** `contact_memory` — it injects its own per-caller stored memory and **discards the value supplied in `agent_args`**. If no `memory_instructions` (memory-writer prompt) is deployed, nothing has ever written to that store, so the injected value is permanently empty. Memory ownership is exclusive: platform (flag on + writer prompt) **or** campaign (flag off + value in args). Never both.
- **Detection:** BEFORE debugging the prompt, read the live agent config: `memory_enabled` and `memory_instructions`. The broken combination is **`memory_enabled=true` with `memory_instructions=NULL`** — memory on, nothing writing it. The API now rejects that state (`400 memory_instructions is required when memory_enabled is true`), so any agent sitting in it predates the constraint and is legacy-broken. Confirm with a scratch agent: a two-line prompt that reads its own context block aloud, run once with the flag off and once with it on.
- **Fix direction:** decide who owns memory. Platform-owned → deploy the agent's memory prompt so the flag is valid and a memory is actually written; the feature then needs a **two-call** test (call 1 writes, call 2 consumes) because a single call can never populate it. Campaign-owned → set `memory_enabled=false` so the `agent_args` value passes through. Do NOT enable the flag on a bot whose campaign already supplies `contact_memory` — that silently discards it.
- **Seen in:** KKB (all six agents) 2026-08-10 — `memory_enabled=true`, `memory_instructions=NULL`, so the returning-caller line failed four live calls and four unrelated prompt rules were "fixed" chasing it. Fixed by deploying `KKB Memory.md`. **Lesson: when a variable-driven branch will not fire, verify the platform is actually delivering that variable before touching the prompt — a scratch-agent echo test costs one call and would have saved four.**

### G5 — A diagnostic prompt that lets the model JUDGE its input produces false negatives
- **Symptom:** a scratch-agent probe built to answer "is variable X populated?" reports it empty, and that false negative gets promoted into a confident platform-level conclusion. Real data existed the whole time.
- **Root cause:** the probe was written as *"if the block is empty, or still shows a placeholder, or says there is no old memory → say EMPTY"*. Those are **judgement calls**, and the model makes them on semantics rather than on presence. A memory that is a full JSON schema of blank fields plus `"General conversation with no new details shared."` is *semantically* empty and *literally* several hundred characters — so the model says EMPTY and the diagnostic lies.
- **Detection:** read your own probe prompt and ask whether any branch requires the model to decide what the content *means*. Words like empty / meaningful / placeholder / missing / useful in a diagnostic are the tell.
- **Fix direction:** a probe must **echo verbatim and judge nothing** — "read out the first 20 characters inside the block exactly as written, including braces, quote marks and field names; do NOT decide whether they are meaningful; the only special case is literally zero characters." Then you read the data and do the judging yourself. Cross-check against an independent source of truth before concluding anything about the platform (here: the console's stored-memory list, which showed 5,329 entries).
- **Seen in:** 2026-08-10, chasing the KKB returning-caller branch. The flawed probe produced "the platform never stores caller memory", which was committed and then retracted once the console was checked. **Lesson: before declaring a platform-level failure, find a second, independent way to observe the same thing — a UI, a log, an export. One instrument you wrote yourself is not evidence.**

### A10 — A new behaviour that DUPLICATES an existing one, a turn apart, is silently dropped
- **Symptom:** a newly added step never happens, and every contradiction you remove changes nothing. The prompt has no rule forbidding it, the input is proven present, and the model is otherwise following instructions. Repeated fix-and-retest rounds all fail.
- **Root cause:** the prompt already performs the *same conversational job* at a nearby point — usually one turn later, from a different source. The model does it once, where the prompt has always done it, and drops the new copy. There is nothing to "fix", because the competing behaviour is legitimate and wanted. This is **duplication**, distinct from **A9** (a rule that forbids the branch) — and it is invisible in the section you are editing, because the duplicate lives somewhere else in the flow.
- **Detection:** state the new step's *purpose* in one plain sentence ("acknowledge that we have spoken to this caller before"), then search the whole prompt for anything else that already achieves that purpose, however it is worded and whatever it reads from. Read a full transcript to the END rather than only the turns you are watching — the giveaway is the bot doing the thing you wanted, just later and from another source. Ask: does the flow now try to do this twice?
- **Fix direction:** do NOT keep hardening the new step. Choose one: (a) drop the new step and accept the existing behaviour; or (b) **fold the new content into the turn the model already performs**, so there is one behaviour in one place. Adding a second occurrence of a job the prompt already does is a design error, not an adherence bug.
- **(b) is CONFIRMED to work.** KKB Hindi Signals 2026-08-10: after six failed rounds fighting for the opening turn, the callback was rewritten as a clause inside the existing post-`get_profile` turn (name → callback → role check, one turn, ending on the role-confirm question). It fired on the very next call. **The rule of thumb: extend the sentence the model already wants to speak; never add a turn that competes with one.** When folding, carry the branch test with the content, bind the value label-first at that point (**G1**), and realign any example that still shows the old placement (**E1**) — otherwise the examples keep teaching the shape you just removed.
- **Seen in:** KKB Hindi Signals 2026-08-10 — a returning-caller callback line in the opening turn never fired across **six** fix-and-retest rounds. The prompt had, for months, greeted returning callers by first name and reflected their role back in the turn straight after `get_profile`. The model performed that and skipped the new opening. Memory storage, retrieval and injection were all independently proven working first. **Lesson: after two failed rounds, stop asking "what forbids this?" and start asking "what already does this?"**

### D42 — A truncated `${recommendations}` payload makes the bot go silent, invent a role, or drop the call
- **Symptom:** reported as "no jobs were recommended". In the transcripts the bot either (a) emits a completely EMPTY assistant turn at the moment the job list is due, (b) names a kind of work that is not in the job list at all, or (c) starts reading a job aloud and the call ends mid-sentence. The input args LOOK populated, so the report gets misfiled as a prompt bug.
- **Root cause:** `${recommendations}` arrived **cut off part-way** — the JSON stops mid-value with no closing quote or bracket. The bot cannot parse it, so it improvises: some calls scrape a role out of a neighbouring field (a `qualification` of "ITI/NSQF Electrician or Solar Technician" becomes a spoken "Electrician" job that does not exist), and some produce nothing at all. This is a **data/input defect**, not a prompt defect — the fix belongs to whatever composes the payload — but the prompt must degrade gracefully instead of improvising.
- **Detection:** always `json.loads()` the call's `agent_args.recommendations` before reading the transcript. A payload that is present and long can still be unparseable. Two tells: the error is `Unterminated string`, and `count('job_id') > count('}')` — more jobs started than finished. Survey the agent's recent calls, not just the reported one: a truncation at a fixed length repeated across many calls means one upstream batch, not a one-off. Compare against the sibling-language bot — if Hindi parses 39/39 and Kannada fails half its calls, the difference is in the campaign, not the prompt.
- **Fix direction:** (1) **Report the payload defect upstream** — that is the actual fix. (2) Harden the prompt to survive it: use only the job entries that are COMPLETE, discard a final entry cut mid-value, treat a partial delivery as usable rather than as missing data (closing the call while good jobs remain is the worse outcome), fall back only when ZERO complete entries survive. (3) Add "name only real `role` values, never a trade inferred from a `qualification` or company name". (4) Add "never end a turn with nothing — say the missing-data line and close instead".
- **Seen in:** KKB Kannada Signals 2026-08-10 (calls `bc961b88` 11:02 and `17a2e1e2` 11:06, +91916…842). `recommendations` arrived at exactly 1023 chars, cut at `"qualification": "NSQF Refrigeration` — 4 `job_id`s but only 3 closing braces. **20 of 40 recent calls on that agent carried the identical truncated payload**, while KKB Hindi Signals parsed 39/39. One call went silent and showed no jobs (`jobs_shown: "No"`); the other spoke a non-existent "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್" job and ended mid-sentence. Note the cap theory is wrong — a 1907-char payload on the same agent parsed fine, so this is upstream truncation, not a platform field limit.

### D43 — No-Match Fallback fires while unshown jobs remain (call ends early with stock in hand)
- **Symptom:** reported as "job flow discontinued after the 2nd set of recommendations". The bot presents one or two sets, the caller declines, and the bot says "no relevant jobs for you right now" and closes — while the recommendations array still holds jobs it never mentioned. The caller is told nothing suits them when half the inventory was never offered.
- **Root cause:** the No-Match Fallback trigger list includes "the user explicitly says none of the available jobs are relevant". A short refusal after a set ("no", "something else", "not these") satisfies that reading, and nothing requires the array to be exhausted first. A **set-level** refusal is treated as a **call-level** rejection. Nothing is wrong with the data — this fires on a perfectly valid payload.
- **Detection:** count the jobs in `agent_args.recommendations` and count the distinct jobs actually named in the transcript. If the fallback line was spoken while `shown < sent`, this is it. Cross-check `call_output.jobs_shown` — it will say "Yes", which hides the problem in reporting. A tell in the transcript: the fallback line arriving immediately after a one-word refusal rather than after the caller rejected everything.
- **Fix direction:** add a hard guard to the fallback — never declare No-Match while unshown entries remain; present the next set instead; state explicitly that a short "no" ends a SET, not the call; require forward progress through the array without re-presenting declined jobs or restarting from the top. Apply to EVERY No-Match section in the file (prompts often carry two).
- **Seen in:** KKB Kannada legacy outbound 2026-08-10 (call `54e8b166`, +9163…910). 8 jobs sent and parsed cleanly; 4 shown (Electrician; then Fitter, CNC Operator, Mechanic); the caller said "ಬೇಡರೀ" and the bot closed with 4 never mentioned. **Lesson: when a fallback can be reached by a one-word answer, gate it on the STATE (is there stock left?), never on the wording of the reply.**

### G6 — A guard rolled across bot families references a variable that family does not have
- **Symptom:** a fleet-wide hardening lands cleanly on every file and passes static checks, but on one family of bots the new rule instructs the model to consult `${recommendations}` — a variable those agents never receive. The same prompt states, a few hundred lines earlier, "There is **no** `${recommendations}` in this version." The prompt now contradicts itself, and the model resolves an empty token at the exact moment it is deciding whether to keep offering jobs.
- **Root cause:** two families with the **same conversational flow** but **different data sources** — args-driven bots read jobs from `${recommendations}`; inbound bots read them from a **hardcoded Job Inventory** in the prompt body. A fix authored against the first family was mirrored by matching *section names* rather than by re-resolving *where that family's jobs actually come from*. Compounded by **G2**: the token in the new prose made Raya derive a phantom `recommendations` agent_arg, so the platform then interpolated whatever any caller/test harness happened to send into the middle of the No-Match section.
- **Detection:** two mechanical checks, both cheap. (1) For every `${var}` in a prompt, grep the same file for a sentence declaring that variable **absent** — a prompt asserting both is always a bug. (2) Diff the prompt's `${...}` tokens against the **live agent's real `agent_args`** and against a genuine production call's args; a token that no real call populates is either phantom or dead. Do this per family before rolling anything fleet-wide: ask "where does THIS bot get its jobs?" and require the answer from the prompt, not from the sibling you just edited.
- **Fix direction:** re-point the guard at the family's real source ("check the **Job Inventory** for fitting jobs not yet presented"), and strip `${}` from any *descriptive* mention of an absent variable so Raya stops deriving args from prose (write `` `recommendations` `` or "a dollar-sign-braces token", never the live token). Confirm afterwards via the API that the phantom arg is gone.
- **Seen in:** 2026-08-12, my own D43 (exhaust-the-list) and Need-Capture rollouts — three references each in all six inbound prompts (KKB ×4, Maya ×2), live for several hours; all six agents had grown phantom `recommendations` / `contact_name` / `new_seeker` args. After the fix each agent's args are exactly what production sends (`contact_memory`, `contact_phone`, `country_code`, plus `college_name` on Maya).
- **The verification corollary — this pattern also produces false CRITICALs.** Grading a transcript for hallucination by comparing spoken jobs against the **call's args** is invalid for a bot whose jobs are hardcoded. Doing exactly that produced four bogus verdicts in one sweep: a legitimate `job_id` read straight from the prompt (line 262) was called "fabricated"; an accurate "no Bengaluru jobs" was called a lie (that bot's inventory is entirely Hubballi/Dharwad); and two Maya bots' correct pool-overview buckets were pinned on "memory contamination" because the roles *also* appeared in stored memory — reverse causation, since memory was written from earlier calls against the same inventory. **Before grading a bot for inventing jobs, establish from the PROMPT where its jobs come from, and compare against that.** Overlap with `${contact_memory}` is not evidence of anything.

### D47 — Every tool failure is spoken as "a technical problem on our side", including the ones that aren't
- **Symptom:** reported from QA as "apply failed" / "the API is still broken", often after a backend team has already fixed something unrelated. The transcript shows `apply_job` returning an error and the bot saying a single stock line — "अभी हमारी तरफ़ से apply complete नहीं हो पाया — कोई तकनीकी दिक्कत है" — followed by a promise to fix it and call back. The caller is told the system is broken when in fact **their application is already in place**, and the tester cannot tell a duplicate from an outage, so a non-bug gets escalated as a P1.
- **Root cause:** `Apply Failure Handling` branches on *what to do next* (another job / no jobs left) but **never on WHY the call failed**. The tool result carries a precise reason — the Signals `/action/perform` endpoint returns `422 ACTION_LIMIT_REACHED, "An active request already exists between these two profiles"` for a duplicate, versus `TARGET_ITEM_NOT_FOUND` or a Dhiway `404 "Job not found"` for a genuinely broken job — and the prompt collapses all of them onto one apologetic sentence. Worse, the no-jobs-left branch then adds "जैसे ही यह apply-issue ठीक होता है, हम आपको वापस call करेंगे", which is a **false promise** when there is nothing to fix.
- **Detection:** grep the failure-handling section for a branch on the error reason; a section with exactly one "base failure line" and no reason cases has this bug by construction. On the runtime side, pull `call_output.jobs_failed_to_apply[].failure_reason` across the agent's recent calls and group by value — more than one distinct reason mapping to the same spoken sentence is the tell. A duplicate-apply is easy to confirm: the same `job_id` appears in an earlier call's `jobs_applied` for the same `profile_id`.
- **Fix direction:** branch on the reason **before** speaking. Case A (application already exists — `ACTION_LIMIT_REACHED` or any "active/duplicate request already exists" message): say so truthfully, suppress the technical line, no apology, and **no callback promise** — close per Graceful Exit if no other job remains. Case B (anything else): keep the existing technical line and next-step rules. Keep the instruction prose English and translate only the spoken line; phrase that line so it agrees with a **feminine noun** (एप्लीकेशन / ಅಪ್ಲಿಕೇಶನ್) rather than with the caller, so it stays safe on a caller of any gender (see **D44**).
- **Seen in:** 2026-08-25, all 12 KKB/Maya prompts carrying `Apply Failure Handling`. Grounded in KKB Hindi Signals calls `bc7ef5b5` (10:26 IST — `ACTION_LIMIT_REACHED` on job 1, then a *successful* apply on job 2) and `1e2fd2a2` (14:41 IST — `ACTION_LIMIT_REACHED` on the very job that succeeded four hours earlier). Both were spoken to the caller as a technical fault; both were filed as an API failure and triaged against a Signals API-key incident they had nothing to do with. **Lesson: when a tool hands back a machine-readable reason, the caller-facing sentence must depend on it — one sentence for every failure mode is a truthfulness bug, not a wording preference, and it burns QA and backend time.**
- **UPDATE 2026-08-25 — prose did NOT fix this; two live iterations were ignored. Treat as D25 (runtime adherence), not a wording gap.**
  - *v1* added a reason branch ("Case A — the application ALREADY EXISTS" with a truthful spoken line) ABOVE the base failure line, in all 12 prompts. Deployed and read-back verified on all 12 live agents. Live call `3be8d3fb` (maya-hi-signals, 2026-08-25 14:51 UTC, 293s) hit `ACTION_LIMIT_REACHED` on job `b7513680` and the bot still said "कोई तकनीकी दिक्कत है".
  - *v2* moved the condition ONTO the label the model demonstrably reads (`**Base failure line — CASE B ONLY (say once):** …`) and added a matching entry to the failure-turn hard bans. Deployed; live agent re-verified as carrying it. Live call (maya-hi-signals, same persona/args) hit `ACTION_LIMIT_REACHED` again and the bot said the technical line **again**.
  - **The unresolved question that decides the fix, and it is NOT a prompt question:** does the conversation model actually RECEIVE the reason? The tool message in the stored transcript reads `[Error: apply_job request failed (HTTP 422).]` followed by a `__RAYA_TOOL_DEBUG__` block containing `ACTION_LIMIT_REACHED`. If that debug block is a console/transcript annotation rather than part of what is fed back, then **every** reason is indistinguishable to the model (`ACTION_LIMIT_REACHED` and `TARGET_ITEM_NOT_FOUND` are both HTTP 422) and no prompt wording can ever branch on it. Settle this with ONE diagnostic call before writing a third version — do not keep re-wording a live prompt.
  - **Escalation shape:** if the reason is not visible, ask the platform (LitWiz) to surface the tool error's `error`/`message` fields to the model, or to return a distinct tool result per reason. Until then the branch is unreachable and the caller-facing inaccuracy stands.
  - **Detection that DOES work today:** `raya/regression/apply_outcomes.py` reads `call_output.jobs_failed_to_apply[].failure_reason` off real calls and checks which line was spoken; it caught both failed iterations automatically. Static prompt checks cannot see any of this.


### D48 — A preference is promised back to the caller with no field to store it in
- **Symptom:** the bot tells the caller their preference has been understood and that someone will get back to them about it — "आपको किस जगह के आसपास काम चाहिए?" … "ठीक है, समझ गई … हम जल्द ही सही options ढूंढकर आपको बताएंगे।" — and the call ends warmly. Nothing reaches the team. Weeks later the same caller is dialled with the same unsuitable jobs, because the preference was never anywhere but in the transcript. QA cannot see the bug at all: every call "passes", the caller sounds satisfied, and the failure is invisible until someone asks why the recommendations never improved.
- **Root cause:** the conversational half of a capture feature shipped without its sink. A spoken promise implies a write, but there are three places a value can actually land — the tool payload (`create_profile` / `update_profile`), the **output prompt** (`call_output`), and the **memory prompt** — and a prompt-only change touches none of them. Especially likely when the value deliberately must NOT go on the profile (a preferred place to WORK is not the caller's residence, and overwriting `item_state.location` with it corrupts a real field), because the "don't write it to the profile" decision is mistaken for "it doesn't need to be stored".
- **Detection:** mechanical and cheap. For every caller-facing line matching *"we have noted / समझ गई / we will get back to you / हम आपको बताएंगे"*, extract the noun it refers to, then grep the agent's **output prompt**, its **memory prompt**, and its **tool payload rules** for a field holding that noun. **All three empty = flag.** Second check: diff the fields the output prompt declares against the values the conversation prompt can newly produce — a new capture question with no matching output field is this bug. Third: on a call where the capture fired, assert the value is present in `call_output`; absent means the sink was declared but never populated.
- **Fix direction:** ship the sink in the SAME change as the question. Add the field to the output prompt (a free-text value plus, where there are branches, a reason enum), state explicitly that it is caller-STATED and never inferred from an input variable or a stored profile value, and state where it must NOT be written. If no consumer exists yet, say so in the changelog rather than letting a spoken promise imply one. Never let the acknowledgement claim a storage event ("नोट कर लिया है", "सिस्टम में डाल दिया") — naming the preference back is acknowledgement enough and stays true whatever the backend does.
- **Seen in:** 2026-08-28, KKB Signals Hindi location-capture change (R1/R2 mismatch fallbacks). Caught in design review before deploy: `KKB Output.md` had no field for either the preferred location or the mismatch reason, so both would have been spoken-and-lost. Fixed by adding `preferred_location` and `preference_mismatch_reason` to the output prompt and deploying it to that agent's `output_instructions` in the same change. **Lesson: a promise to the caller is a data requirement. If you cannot name the field it lands in, the feature is half-built.**

### D49 — "None of these suit me" collapses into No-Match while most of the list is still unspoken
- **Symptom:** the caller states a strong constraint the current batch does not meet — most often a place ("मुझे मेरठ में ही चाहिए") — and the bot answers honestly that it has nothing there, then goes straight to the no-relevant-jobs line and closes. The array still holds jobs it never read out. Callers notice: *"अरे अभी तो आपने साहिबाबाद में प्रोडक्शन वर्कर की जॉब बताई थी"*. Reported as "the bot gave up" or "it said there are no jobs when there were jobs".
- **Root cause:** the No-Match trigger list contains a subjective clause — *"the user explicitly says none of the available jobs are relevant"* — and a constraint the FIRST batch fails to meet satisfies that clause on its face. The model is not ignoring the exhaustion guard so much as concluding the guard does not apply, because from its point of view the caller HAS said none are relevant. A location constraint makes this worse: "no job near the place they named" reads as "no relevant job", even while jobs in other areas sit unread.
- **Detection:** count distinct `role`/`company` pairs actually voiced before the first no-relevant-jobs line and compare with the count of valid entries in `${recommendations}`. Any shortfall is this bug. **Compare script-aware** — the array is Latin and the transcript is Devanagari, so a naive substring match reports zero named and manufactures false positives (this cost two wrong verdicts while diagnosing it). Cross-check `call_output.jobs_shown`, which says "Yes" and hides the shortfall.
- **Fix direction — and what does NOT work:** two prose attempts failed live on KKB Signals Hindi. (1) A three-part GATE inside the No-Match section requiring every job to be named first — bypassed. (2) The same requirement moved ONTO the sentence immediately above the spoken line, naming the exact confusion ("'there is no job near the place the caller named' is NOT this case") — also bypassed, on a 5-job call where only 2 were named. Treat this as **runtime adherence (D25), not a wording gap**, and stop re-wording. The promising direction is structural rather than textual: make the *unspoken-job count* something the model must state before the line is allowed, or move the decision out of the prompt entirely (a tool/`call_output` check that the presented count equals the supplied count).
- **Seen in:** 2026-08-28, `kkb-hi-signals`, calls `1aa8729b` (3 jobs supplied, 1 named, capture + no-match fired) and `b8666aaa` (5 supplied, 2 named, same). **Note the baseline:** this is NOT a regression introduced by the location-capture work — a caller insisting on a city with no stock already satisfied the pre-existing subjective trigger. The location feature makes the failure easier to reach and easier to see; it did not create it. **Lesson: a subjective trigger clause ("the user says none are relevant") will always outrank an objective guard placed elsewhere, because the model evaluates the clause it is standing on.**

### D50 — The prompt's own worked examples demonstrate the violation the rules forbid
- **Symptom:** a rule is stated clearly, deployed, verified present in the live instructions — and ignored on real calls, repeatedly, surviving two or three rewordings. Every prose fix "should" work and none does. The tell is that the bot's wrong output is not a paraphrase of anything: it is **byte-identical to a line in the prompt's own sample-conversation section**, prefix and punctuation included.
- **Root cause:** a worked example is a demonstration, and a demonstration outranks a prohibition. Long prompts accumulate sample dialogues written before later rules were added, so the examples quietly encode the OLD behaviour. The model, choosing between an abstract rule and a concrete demonstration of the same situation, copies the demonstration. Every subsequent guard is competing with a counter-example the author has forgotten is there.
- **Detection — cheap and decisive.** Take the exact string the bot said wrongly and `grep -F` it against the whole prompt. A hit inside a sample conversation is this pattern, and it is proof, not a hypothesis. Then audit the example section as a whole: for every mandatory step, check whether the examples actually DO it. Count it — "5 of 6 examples close an engaged call without the mandatory offer" is the finding. Also check demonstrated tool payloads against the payload rules: examples routinely show the wrong script, a bare area where a city is required, or a field the rules forbid.
- **Fix direction:** **edit the demonstrations, not the prose.** Make the examples perform the mandatory step, and annotate the ones that legitimately skip it so they cannot be read as counter-examples. Then remove any standing rule that flatly contradicts the new instruction — a prohibition sitting next to a requirement is what licenses the model to pick the prohibition. This is the same mechanism class as removing a raw token from a spoken template: it changes what the model has to work with rather than adding another "do not".
- **Seen in:** 2026-08-31, `kkb-hi-signals`. Turn 31 of call `924e611f` spoke a string identical to lines 1586/1646/1750, not the instruction at 1256. The audit found 5 of 6 examples closing engaged calls with no Need Capture offer, 3 persisting bare Devanagari localities as `location` against two explicit rules, and 0 asking for the caller's city at the Phase-1 gate. **Fixing the examples made D47 pass on the very next call after two previous prose fixes had failed.** That is the strongest single piece of evidence in this catalogue that demonstration beats prohibition. **Before writing a third wording of any guard, grep the bot's wrong output against the prompt.**

### D51 — A rule points at a branch label that no longer exists in the section it names (and often means something else elsewhere)
- **Symptom:** a hard ban reads perfectly and does nothing. "Do NOT say the technical-failure line on an `ACTION_LIMIT_REACHED` error … say the **Case A** line" — but the section it governs was restructured into a lookup **table with rows**, so there is no Case A in it, and "the technical-failure line" it forbids was deleted in the same restructure. Meanwhile *Case A* **does** exist elsewhere in the prompt meaning something entirely different (KKB Step 1: "Case A — you already know the target role"). The model cannot bind the reference to the branch the author meant, so the ban is inert and the section's default line wins every time.
- **Root cause:** restructuring a branch **renames its labels**, and the rules that reference those labels live tens or hundreds of lines away — in a "Hard bans" list, a next-step section, a turn-composition rule. The restructure updates the branch and leaves every remote reference dangling. It survives review because each fragment reads correctly on its own: the ban is a sensible sentence, the table is a sensible table. Only the *cross-reference* is broken, and nothing checks cross-references.
- **Detection — mechanical, run it after every restructure.** Harvest every branch label a rule refers to (`Case A/B`, `Path A/B`, `Row 1/2`, `Option 1`, `Step 3.5`, `v2`) and, for each, (1) assert the label is DEFINED inside the same top-level `#` section that references it, and (2) assert the label is defined exactly ONCE in the whole prompt. A label defined twice with different meanings, or referenced in a section that does not define it, is this bug. Second check: grep every spoken line a ban forbids — if the forbidden line no longer appears anywhere in the prompt, the ban is stale and should be rewritten to name what the model can actually still say.
- **Fix direction:** rewrite the reference to the label that exists ("the row-1 line"), quote the line itself inline so the reference cannot rot again, and never reuse a label name across two sections. Prefer restating the actual sentence over pointing at a name.
- **Seen in:** 2026-09-01, `kkb-hi-signals`. The 2026-08-31 restructure of Apply Failure Handling into a two-row lookup left two references to the old labels (turn-composition rule: "whichever failure line you just spoke (Case A or Case B)"; hard ban: "say the Case A line"). Grounded in calls `90da81db`, `21c428dc`, `dc3168ec` — all three hit `ACTION_LIMIT_REACHED` and all three spoke the generic row-2 line. **Lesson: when you rename a branch, grep the prompt for its old label before you deploy. A dangling label is worse than no rule, because it reads like a rule in review.**

### D52 — A rule branches on a tool-error string the conversation model may never receive
- **Symptom:** the prompt says "if the error contains X, say line 1; otherwise line 2", and line 2 is spoken on **100%** of calls, X included. Rewording escalates — bold, capitals, a hard ban, a lookup table — and nothing changes. The reason branch looks flaky ("it works sometimes") but it has in fact never once been taken.
- **Root cause:** the model is handed a *wrapper*, not the API's body. On Raya the tool message reads `[Error: apply_job request failed (HTTP 422).]`; the machine-readable reason (`ACTION_LIMIT_REACHED`, `SOURCE_ITEM_NOT_FOUND`) sits in a `__RAYA_TOOL_DEBUG__` block whose visibility to the conversation model is unconfirmed. Since both reasons are HTTP 422, a prompt keyed on the reason string has nothing to key on. It is a **reachability** bug, not an adherence bug — which is why prose volume has no effect.
- **Detection — the count is the proof.** For any error-keyed branch, pull every recent call where the condition demonstrably occurred (from `call_output.jobs_failed_to_apply[].failure_reason`, which the *output* model can read because it reads the stored transcript) and count how often the branch was taken. `0/N` across multiple bots, languages, directions **and** across two different prompt structures is structural unreachability. Contrast with a genuine adherence bug, which shows a mixed ratio. Second check: read the tool result content in the transcript and ask what a reader with only that string could conclude.
- **Fix direction — do NOT write a third wording (root `CLAUDE.md`).** Derive the condition from data you definitely have and act **before** the tool: in-call state (has this `job_id` already been sent this call?) and `${contact_memory}` (`jobs_applied`) both identify a duplicate application without any error string, and skipping a doomed call is better than interpreting its failure. Then mirror the mapping into the **tool's own `description`** — read at the moment of use and far stickier than prose (`scripts/raya_tooldesc.py`). Keep the unknown-reason line asserting **nothing**, so it stays true in the cases you cannot distinguish. Escalate to the platform (surface the error body / a distinct tool result per reason) only with the 0/N table attached.
- **Seen in:** 2026-08-25 → 2026-09-01. **8 of 8** `ACTION_LIMIT_REACHED` calls across `kkb-hi-signals` (`90da81db`, `21c428dc`, `dc3168ec`), `kkb-kn-signals` (`18b5e1b8`), `kkb-kn-in-signals` (`d824912c`) and `maya-hi-signals` (`96e72c85`, `9d82ac2c`, `3be8d3fb`) spoke the generic line; **zero** spoke the explicit already-applied line — including three calls made after the branch had been restructured into an explicit lookup table. See `scratchpad`-independent scanner logic in `raya/regression/apply_failure_wording.py`. **Lesson: before re-wording a branch that has failed twice, count how many times it has EVER been taken. Zero means it cannot be reached, and no sentence you write will change that.**

### D53 — An input variable the prompt promises to speak back is silently suppressed by a guard about something else
- **Symptom:** the campaign supplies a good `location` and QA reports "it asked me where I want to work even though I gave the input". Two live calls, same args, show two different wrong behaviours: one bot ignores the input and asks the open UNKNOWN-branch question; the other names the input value and asserts we have jobs there — *"आपके लिए दिल्ली में कुछ जॉब्स हैं"* — when every job is in Ghaziabad. The prescribed reconfirmation ("आपको [जगह] के आसपास जॉब चाहिए…?") is never spoken on either.
- **Root cause:** the reconfirmation names a place, and a Hallucination Guard elsewhere forbids naming a place we hold no inventory in. When the input location has **no** matching job the two rules collide, and the guard — being a hard prohibition — wins. The prompt has a KNOWN branch and an UNKNOWN branch but **no branch for "known, and we have nothing there"**, so the model must improvise: suppress the reconfirmation, or breach the guard. Both improvisations are wrong, which is why the same args produce different failures on different calls. Compounded when the precedence rule ranks a stale stored profile value ABOVE the per-call input, giving the model a third, older candidate to arbitrate between.
- **Detection:** for every input variable the prompt promises to speak back, enumerate the states where its value is inconsistent with the other inputs — a location no job matches, a role no job matches, a name that disagrees with the fetched profile — and check each has a line of its own. A promised echo-back with no inconsistent-case branch is a latent D53. Runtime check: compare the call's input `location` against the `location` field of every job in `${recommendations}`; on calls where nothing matches, assert which line was spoken. Also assert the precedence order actually written: a per-call campaign input should outrank a stored profile field that means something different (where they LIVE vs where they want to WORK).
- **Fix direction:** give the inconsistent case its **own mandatory, truthful line naming both values** — "आपके लिए [जगह] में अभी कोई जॉब नहीं है — जो जॉब्स हैं वो [शहर] में हैं। [शहर] में देखना चलेगा?" — and say, in the same place, that the plain reconfirmation is not an inventory claim and therefore does not engage the guard. Record the mismatch as a first-class output field (`input_location_had_jobs`) so a campaign dialling a city with no stock shows up in reporting instead of in a QA message. This is the same move as D47 row 2: make the reachable line truthful rather than trying to make the wrong line unreachable.
- **Seen in:** 2026-09-01, `kkb-hi-signals`, calls `5c67bd19` (input `Delhi`, 8 Ghaziabad jobs → bot claimed jobs were in Delhi) and `90da81db` (same args → bot ignored the input and asked openly). Profile also carried a stale `Bengaluru, Karnataka, India`, which the old precedence rule ranked above the input; the closing read-back told the caller "एरिया बेंगलुरु". **Lesson: an echo-back rule needs a branch for every state its value can be in. A guard that forbids the echo in one state will suppress it in all of them.**

### D54 — A rule gated on stored memory, on a platform where memory is neither settable nor readable
- **Symptom:** a "never ask this twice" rule (or a "you already applied to this" rule) is written, deployed and read back — and the bot asks anyway, on call after call. Every attempt to test it is inconclusive, and the same fix gets re-written because each round looks like a fresh adherence failure. The tell is that you cannot answer the simplest question about the run: *did the precondition actually hold on that call?*
- **Root cause — two platform facts that compound.** (1) **`contact_memory` sent in `agent_args` does not reach the model.** Raya records it faithfully in `agent_args` and substitutes its own stored memory for `${contact_memory}` — the `contact_phone` pattern. So the precondition cannot be set. (2) **Stored memory cannot be read back.** `/api/contact`, `/api/contact/{phone}` and `/api/memory` all 404 or 500, so the precondition cannot be inspected either. A rule gated on memory is therefore a rule whose input is invisible in both directions: you observe only the behaviour in between, and a null result is indistinguishable between "the rule was ignored" and "there was nothing in memory to act on".
- **Detection.** Before writing any memory-gated rule, run the **discriminator**: send a `contact_memory` fixture containing facts the stored memory cannot possibly hold for that number — a fabricated role, city and landmark — and see whether the bot voices any of them. One call. If it voices none, every memory-gated verdict on that bot is `fixture_blocked`, and a FAIL you report on one is a fiction. Second check, cheap and easy to skip: confirm `memory_enabled` is true and that the field you are gating on actually exists in the live `memory_instructions` — a rule gated on a field the memory prompt never writes can never fire. Third, a soft signal: if the returning-caller callback clause is **byte-stable across hours of calls** and its content maps exactly onto a PROFILE field, suspect that the clause is being taken from the profile rather than from memory, and that `${contact_memory}` is arriving empty.
- **Fix direction.** Do not gate a behaviour you care about on memory alone while this holds. Prefer a source you can both set and read: in-call state, an input variable the campaign controls, the tool result itself, or a required tool parameter (which at least leaves the model's assertion in the transcript — see **D52**). Where memory genuinely is the only source, ship it, and mark it explicitly **VERIFY-PENDING (memory unreadable)** rather than letting a passing-looking call imply verification. Then escalate for a **read-only stored-memory endpoint** — without it, "the bot should skip this because memory already has it" is permanently one inference short of testable.
- **Seen in:** 2026-09-01, `kkb-hi-signals`. The Location step's Turn B ("ask the nearest bus stop ONCE, ever") and the `apply_job` duplicate pre-check are both memory-gated. Discriminator call `c2ffe9fb` carried "WELDING jobs in Meerut / Chand Tara Cinema" and the bot voiced none of it, opening instead with the same "कंप्यूटर ऑपरेटर या डेटा एंट्री" clause it had used for six hours. `bbaade33` then asked the landmark question again on the fixed build, with `memory_enabled: true` and `nearest_landmark` present in the live memory prompt — and there is no way, from here, to say whether memory held the value. **Lesson: a rule is only as testable as its precondition. Check that you can set it AND read it before you write the rule, not after three rounds of live calls.**

### D55 — The model fills a gap the prompt left open (four bugs, one cause)
- **Symptom:** a rule is correct, deployed, read back on the live agent — and the bot says something else. Rewording it makes no difference, and the failures often look intermittent: the same prompt produces the right output on one call and a fabrication on the next. The outputs are not random. They are always **the nearest plausible thing the model could see**: the fetched profile's city instead of the campaign's, an invented job title, the success line after a failure, "we have all the jobs" after naming one.
- **Root cause:** the prompt DESCRIBES a value but never SHOWS it, or leaves a slot for the model to compose. Four instances in one night on the same fleet, all fixed the same way:
  1. **A described variable whose value is never printed.** `${location}` was explained in Input Variables but the Turn A sentence said `[जगह]`. The model could see the fetched profile and could not see the input, so it used the profile — six calls, four wordings of a precedence rule. Fixed by making the slot the literal token `${location}`, substituted before the model reads the line.
  2. **A field the platform DROPPED.** DKB was sent `job_role: ""`; Raya omits empty args entirely, so `${job_role}` arrived as an unsubstituted token — neither empty nor the sentinel the branch tested for. The model filled the gap with "Helper, 2 vacancies, ₹12,000" and told a new provider their posting was expiring.
  3. **A filter that hid data from the model's working set.** The relevance filter matched 1 of 8 jobs; when the caller asked to hear everything, the bot said those were all we had. It was not lying about the count — the other seven were not in front of it.
  4. **An abstract slot in a template.** "`[next question]` is the alternate-job offer when the apply FAILED" still leaves a sentence to compose, and the nearest sentence to hand was "अप्लाई हो गया है" — spoken on four calls where the apply had just failed.
- **Detection:** for every `[slot]` in a spoken line, ask **can the model actually see the value that belongs there, at the moment it speaks?** Grep the prompt for the corresponding `${arg}`: if the value is never printed near the point of use, this pattern is latent. Second check: compare what the bot said against what it COULD see — a wrong value that exactly matches a fetched-profile field, or an invented one where the arg was dropped, is this, not disobedience. Third: any rule that fails **intermittently** across otherwise identical calls is a gap, not a weak instruction — the model fills it when nothing better is visible and gets it right when something is.
- **Fix direction:** **show the value or quote the line — never both describe and leave a slot.** Substitute the token directly into the spoken template (`${location}`, `${company_name}`) so there is no resolution step; print the supplied values above the branch that tests them; quote every branch of a template verbatim so there is nothing to compose; and state explicitly that an unsubstituted `${...}` token counts as EMPTY, because a dropped arg arrives that way. **Do not reword a rule that has failed twice — go and find what the model cannot see.**
- **Seen in:** 2026-09-02/03 across kkb-hi-signals, kkb-kn-signals, dkb-hi-signals, dkb-kn-signals. Location: `2bf465d9`, `8976c120`, `4b453ebe`, `29964cf6`, `38dcec50`, `e67ab9cd`, `ef055109` → fixed and verified `2a6ccc0b`, `62dc3ee7`, `1119c329`, `af1c6e2a`. DKB: `e2ce642a`, `9cf80aa5`, `0eb3fc72` → verified `2c197514`, `b1b71d68`, `9e2e0056`, `3f996a3d`. Filter: `8976c120`, `4b453ebe` → verified `d9bf1f43`, `4b0ea64d`. Template slot: `a111ed52`, `0178c996`, `503440a3`, `4b0ea64d` → verified `c00e7ba5`, `fd464bc0`, `03cf4435`. **Lesson: when a rule fails and rewording does not help, stop editing the rule and go find the value the model cannot see.**

### D56 — A completeness claim gated on a count the model cannot verify at the moment it speaks

**Symptom.** The bot asserts it has finished something ("those are all the jobs we had") while part of
the set is genuinely unspoken. Two calls on the SAME prompt and the SAME fixture split: one presents
8 of 8, the next presents 7 of 8 and then claims completeness. Looks like flakiness; it is not.

**Root cause.** The guard was written as *"count what you have said aloud against `${recommendations}`
before claiming the list is done."* That instruction asks the model to reconstruct its own spoken
history and diff it against an array — a stateful count with no external anchor. Nothing in the
context makes the answer checkable at the instant the closing line is chosen, so the model estimates,
and an estimate is right most of the time and wrong the rest. Re-wording the guard cannot fix this:
KKB Hindi Signals carried **four** separate paragraphs all saying count-before-you-close, and the
eighth job still went unnamed on `22d80263`.

**Detection heuristic.** Grep the prompt for guards phrased as *count / compare / check … against
`${array}`* or *"every X must already have been Y"*. For each, ask: **at the moment the model must
obey this, is the quantity a literal token in its context, or must it be derived from what it
remembers saying?** If derived, the guard is decorative — mark it a gap regardless of how forcefully
it is worded. Two independent signals that you are here: (a) the same guard has been re-worded 3+
times, and (b) the failure ratio is mixed (7/8, then 8/8) rather than 0/N.

**Fix direction.** Give the model a number it has *already spoken*, then make the guard a comparison
of two spoken numbers. On KKB the total is announced once on the first batch ("आपके इलाके में कुल आठ
जॉब्स हैं"), ordinals then run continuously and never restart, and the closing line is permitted only
when the highest ordinal spoken equals the announced total. The model no longer counts — it compares
"आठवाँ" with "आठ", both of which are verbatim in its own recent output. Same shape as the apply
success-line positional constraint (D47 fix): **convert an unverifiable internal count into a
positional or numeric fact the model can read off its own transcript.**

**Corollary — announcing the total also fixes the silent omission**, not just the false claim. A bot
that has committed out loud to eight has a reason to reach eight; one that never named a total can
drop a row and never notice.

**Source.** KKB Hindi Signals, 2026-09-03. Bug call `22d80263` (7 of 8, then claimed complete);
control `cb9a4938` (8 of 8, same prompt, same fixture). Predecessor bug `e40850b5` (3 of 8, one job
per ask) was a different cause — see D55.


#### D50 addendum (2026-09-03) — "it's model adherence, don't add prose" is a triage claim that must be GREPPED before it is believed

The KKB Kannada Signals bots were reported on 2026-08-04 for hinting out loud that they had looked the
caller up ("ನಾನು ನೋಡ್ತಿದ್ದೀನಿ", "ನಿಮ್ಮ ಮಾಹಿತಿಯಲ್ಲಿ … ಕಾಣ್ತಿದೆ"). The open item filed the cause as
*"the prose already forbids this clearly, so it is a model-adherence miss rather than a missing
instruction; adding more wording tends to make it worse."* That diagnosis was **wrong**, and it sat
unchallenged for a month because nobody ran the one-line check.

Grepping the leaked phrases against the prompts found them **mandated**: the role-confirmation
instruction told the bot to say exactly `"ನಾನು ನೋಡ್ತಿದ್ದೀನಿ, ನೀವು ಈಗ [role] ಕೆಲಸ ಮಾಡ್ತಾ ಇದೀರಿ …"`, the
inbound twin told it to say `"ನಿಮ್ಮ ಮಾಹಿತಿಯಲ್ಲಿ [role] ಕಾಣ್ತಿದೆ …"`, sample conversations demonstrated
both, and the **Hindi twins carried the same thing** (`"मैं देख रही हूँ कि आप अभी [role] का काम कर रहे
हैं"`) — so the bug was fleet-wide, not Kannada-only. Meanwhile a *different* section of the same file
forbade the phrase by name ("no status narration, no 'मैं देख रही हूँ'"). The model was not disobeying;
it was picking one of two instructions the prompt gave it, and the item had been closed to prose
changes on the strength of a guess.

**The rule.** An adherence diagnosis is only valid AFTER the bot's exact words have been grepped
against every one of that bot's prompt files and found absent. 19 mandated occurrences across 12
prompts were sitting in plain text. Corollaries:
- **A prohibition and a requirement for the same phrase means the requirement wins somewhere.** Grep
  the phrase, count the hits, and check whether any of them is an instruction or an example.
- **Fix the mandate and the demonstration, never just the prohibition.** Adding force to the ban
  while the example still shows the banned line is the D25/D47/D49 treadmill.
- **Never scope such a fix to the reporting language.** The report named Kannada; Hindi, Maya and
  both legacy pairs had it too. Check the twins before believing a single-language bug.

### D57 — The samples depict a tool call as narration, so the model narrates it instead of calling it

**Symptom.** The bot speaks a stage direction aloud and then asserts the outcome of a tool it never
invoked. On live call `29c4f152` a KKB caller heard: *"ठीक है, आपकी तरफ़ से अप्लाई कर देती हूँ.
**\*(Silent tool call: apply_job)\*** अप्लाई हो गया है…"* — `apply_job` was never called on that call.
She rang off believing she had applied. Four calls on 2026-09-03 spoke the apply-success line with no
successful apply result behind it.

**Root cause.** Two prompt properties combine:
1. Sample conversations put stage directions **in the same stream as spoken lines** —
   `> *(persist location — update_profile SILENTLY with …)*` sits between two `> **Agent:**` turns —
   and nothing anywhere says a parenthetical is not speech. The model learns the *shape*
   "say line → parenthetical about a tool → say result line" as one continuous turn of text.
2. Reproducing that shape as text is indistinguishable, from the model's side, from doing it. The
   tool call becomes a token sequence it can emit rather than an action it must take.
   Note the invented string was NOT in any prompt — grep confirmed zero hits. It is the *format*
   that was learned, not the words, so a D50 verbatim grep comes back clean and the cause still lies
   in the demonstrations.

**Detection heuristic.** Two cheap checks:
- Count `^> \*\(` stage directions in the prompt, then grep for any rule saying a parenthetical is
  never spoken. 31 annotations and zero such rules is the signature.
- In transcripts, flag any apply/write-success line with **no corresponding successful tool result in
  the same call** (`apply_result_integrity.py` check Z). A positional rule alone does not stop this:
  KKB Hindi Signals already carried "this line may ONLY appear in the same turn as the `apply_job`
  tool result" and still failed four times, because the model believed the result was there — it had
  just written one.

**Fix direction.** Do not add another wording of the positional rule; it has already failed. Instead:
(a) state explicitly that `*( )*` content is a stage direction, never spoken, never invented;
(b) state that **emitting a description of a tool call does not call the tool** — only an actual
result licenses the outcome sentence; and (c) mark every tool-mentioning annotation in the samples
`*(NOT SPOKEN — …)*` so the demonstration itself stops modelling narration-as-action. Fix the
demonstration, not the prohibition.

**Why it is the worst class here.** Every other bug in this family degrades the call; this one hands
the caller a false belief that they have applied for a job. Rank it above cosmetic and even above
apply failures — a caller who hears "अप्लाई हो गया है" stops looking.

**Source.** KKB Hindi Signals, 2026-09-03. Bug calls `29c4f152`, `4b0ea64d`, plus two more the same
day. Related: D50 (grep the wrong output — clean here, the format was copied, not the words),
D47/D55 (the model fills what the prompt leaves open).

### D58 — A rule that cannot be satisfied honestly gets satisfied dishonestly

**Symptom.** The owner asked for three distinct apply outcomes: already-applied, technical failure,
success. The bot duly produced the already-applied line on `c5a10922` — for a job it had never
attempted, with empty `contact_memory`. The line looked like the fix working. It was a guess.

**Root cause.** The already-applied branch is keyed on knowledge the agent does not have. All three
possible sources are closed:
- **The error body is invisible.** The model receives `[Error: apply_job request failed (HTTP 422).]`;
  `ACTION_LIMIT_REACHED` lives in a `__RAYA_TOOL_DEBUG__` block written for the transcript only
  (proven 10/10, see D52). Putting the mapping in the tool description does not help — the condition
  it tests never becomes visible.
- **`contact_memory` is empty or unreadable** on most calls (D54).
- **`get_profile` does not return applications.** Verified on `d6e545d4`: the only non-profile item
  it returned was an unrelated *draft job posting the test number owns as a provider*, and the job
  that actually 422'd was absent.

So the branch is unreachable by evidence — and a branch the model is told to take, but cannot verify,
gets taken on vibes. **Both failure modes are now live: Kannada `d6e545d4` called a real duplicate a
technical issue, and Hindi `c5a10922` called a never-attempted job already-applied.**

**Detection heuristic.** For any branch whose condition names a fact, ask *which tool result carries
that fact, in this call, in a field the model can read?* If the answer is "the error text" and the
error text is not surfaced, or "memory" and memory is empty, the branch is decoration. Then check the
transcripts for the branch being taken anyway — a branch taken without its evidence present is the
signature, and it is more dangerous than the branch never firing.

**Fix direction.** Two parts, and the first is not optional:
1. **Gate the branch on citable evidence.** The already-applied line now requires either an
   `apply_job` result for that same `job_id` earlier in the same call, or an explicit `jobs_applied`
   entry naming role and company. Absent both, the model must not claim it. This does not make the
   feature work — it stops the fabrication, which is the part we control.
2. **Escalate the rest with evidence, not adjectives.** The ask is narrow: surface the tool error's
   `error`/`message` fields to the model, or return distinct HTTP statuses, or add an applications
   list to `get_profile`. Any one of the three makes the owner's three-outcome spec achievable; none
   of them is a prompt change.

**Lesson.** When a requested behaviour needs a fact the runtime does not provide, say so at the time
rather than shipping a branch that will look right on some calls. A guessed branch reads as a working
fix in a transcript, which is how this survived a "verified" claim.

**Source.** KKB Hindi/Kannada Signals, 2026-09-03. `c5a10922` (fabricated already-applied),
`d6e545d4` (real duplicate reported as technical), `d401d6cf` (same). Related: D52, D54, D57.

### D59 — "items[0]" works until the caller's first item isn't the one you meant

**Symptom.** Two applications on one call both fail with `SOURCE_ITEM_NOT_FOUND` while the job ids are
valid and live. The caller is told there is a technical problem. Reported as an apply bug; it is not.

**Root cause.** `get_profile` returns EVERY item the phone number owns, in no guaranteed order and
across domains — a seeker `profile_1.0`, and for anyone who has ever posted a vacancy, one or more
provider `job_posting_1.0` items. The `apply_job` tool description said the profile id is
*"items[0].item_id from get_profile"*, and the prompts referred to `items[0]` ten or eleven times
each. On live call `0d63dc50` the caller's `get_profile` returned exactly ONE item and it was a
`job_posting_1.0` — he is registered as a provider, not a seeker. The bot sent that job posting's id
as `profile_id`; the *source* item of an apply is the profile, so the API correctly reported the
source item did not exist. He had no seeker profile and none was ever created.

**Why it survived every test.** The tester number's `get_profile` happens to return its
`profile_1.0` FIRST, so `items[0]` is the right item and every harness call passed. The instruction
was not "wrong sometimes" — it was right by luck on exactly the account we test with. **A rule that
indexes into a collection is only ever tested against the orderings your fixtures happen to have.**

**Detection heuristic.** Grep the prompts and every tool description for positional access into a
tool result — `items[0]`, `results[0]`, "the first", "the top one". For each, ask what else that
collection can contain and whether ordering is guaranteed anywhere. Then check transcripts for a
`*_NOT_FOUND` on an id that came out of a tool result rather than from input args: that pairing —
valid-looking id, not-found error — is the signature. `SOURCE_ITEM_NOT_FOUND` specifically means the
PROFILE side, never the job side; do not read it as a bad job id.

**Fix direction.** Select by type, not by position: the item whose `item_type` is `profile_1.0` AND
`item_domain` is `seeker`. And decide the empty case explicitly — no such item means the caller has
NO profile and is a NEW caller (consent, then `create_profile`), regardless of what else came back.
Put it in the tool parameter description as well as the prompt, since that is read at the moment of
use.

**Corollary for test design.** Our one tester number cannot reproduce this, and a green harness run
says nothing about it. Verifying it needs an account whose first item is not a seeker profile — a
provider-only number, which is precisely the kind of caller the employer rail creates.

**Source.** KKB Kannada Signals, 2026-09-03, reported by Santosh. Bug call `0d63dc50` (two
`SOURCE_ITEM_NOT_FOUND`, job ids `19e3da1f` and `bc2ac8de`, both confirmed live). Control: tester on
`0a5ec09d`/`d6e545d4`, profile first in the list, applies succeed. Related: D55 (the model fills what
the prompt leaves open), D58 (a branch keyed on something unavailable).

### D60 — A mandated line that bundles a disclosure with a question loses the disclosure

**Symptom.** Consent "goes missing" even though the prompt mandates it in bold and forbids the tool
call without it. On `bbdb6eaf` the caller asked to apply, the bot replied *"क्या मैं आपकी तरफ़ से
अप्लाई कर दूँ?"* and called `apply_job`. The data-sharing sentence was never spoken. Reported by QA
as "consent is missing"; the prompt looks like it says otherwise.

**Root cause.** The mandated line is two sentences doing two different jobs:

> "अप्लाई करने पर आपकी personal details company के साथ share होंगी। **इस जॉब के लिए अप्लाई कर दूँ?**"

Sentence 1 discloses; sentence 2 advances the call. **The model keeps the half that advances the call
and drops the half that does not** — and because it paraphrased the question rather than quoting the
line, no verbatim-match guard fired. Same shape as the apply-failure turn earlier the same day, where
the offer of another job was the TAIL of a three-sentence line and got dropped: whichever half is not
load-bearing for the conversation is the half that disappears.

**Detection heuristic.** For every mandated multi-sentence line, ask which sentence the conversation
would still work without — that is the one that will go missing. Then check transcripts for the
surviving half in isolation: an apply question with no disclosure, a failure line with no offer, a
success line with no caveat. A detector keyed on the WHOLE line reports "line absent" and reads like
the model ignored the rule; a detector keyed on each half separately tells you which half died.
`inbound_location_consent.py` check K does this — it fires only when the apply QUESTION is present
and the DISCLOSURE is missing, which is the actual failure.

**Fix direction.** Do not re-bold the sentence; it was already mandatory and forbidding the tool call
"until this line has been spoken" had already failed. Put the requirement where it is read at the
moment of the action — the tool description: *"never invoke this unless you have just TOLD the caller
their personal details will be shared with the company — the apply question on its own is not
consent."* Verified on `334fc8f3` (three applies, disclosure before each) and `a82cd401`.

**Source.** KKB Hindi Inbound Signals, 2026-09-04, reported by Khushboo. Bug `bbdb6eaf`. Related:
D57 (tool-schema guards beat prose), D55.

### D61 — A suppression rule with no replacement line falls back to the thing it suppressed

**Symptom.** The bot re-asks something it already knows. `bbdb6eaf` fetched a profile carrying
"Delhi, India" and still asked *"किस इलाके में देखें — कोई खास जगह, या कहीं भी चलेगा?"*, then read out
Ghaziabad jobs. Reported as "could fetch profile but didn't ask or confirm location".

**Root cause.** Structural, not semantic. The prompt printed the OPEN question first, as the Case A
script line, and put the guard underneath it: *"ASK THIS ONLY IF YOU DO NOT ALREADY HAVE A LOCATION."*
So the wrong output was the default and the condition was a caveat read afterwards. The confirm line
existed further down but was never the thing the model reached first.

**Detection heuristic.** Look for any script line immediately followed by a rule that restricts when
to say it. That ordering is the bug: the model reads the line, then the exception. Grep for
`ASK THIS ONLY IF`, `say this unless`, `only when`, `do not say this if` appearing AFTER a quoted
spoken line rather than before the branch.

**Fix direction.** Invert the structure so the check comes first and each branch names its own line —
have one, confirm it; already confirmed earlier, say nothing; both empty, then and only then ask
openly. The open ask becomes the last branch instead of the default. Verified on `334fc8f3` and
`a82cd401`, both of which confirmed the held location instead of asking.

**Source.** KKB/Maya inbound prompts, 2026-09-04. Bug `bbdb6eaf`; same fault on `5a3aef43`,
`0358c875`, `452874bb`, `4ed09650`, `7b81a27a` across all three inbound bots.

### D62 — An evidence whitelist added to stop a branch being GUESSED also blocks the one case where it is KNOWN

**Symptom.** A branch that used to fire (sometimes wrongly) stops firing at all, and the generic
fallback is spoken instead. Tracker row 103, "bot is saying technical issue instead of already
applied": across 09-03/09-04 production traffic, of 60 `apply_job` calls that returned
`ACTION_LIMIT_REACHED`, **45 spoke the technical-issue line and 5 spoke the already-applied line**;
after 2026-09-03 11:10 UTC the already-applied line was spoken **0 times in 11 opportunities**.

**Root cause.** On 2026-09-03 a fix ("gate the already-applied line on evidence; it was being
guessed") added a closed two-item list — apply ran earlier in this call, or `contact_memory`'s
`jobs_applied` names the job — followed by *"**Nothing else counts** … a 422 with no readable reason
does NOT mean already applied. If neither 1 nor 2 holds, row 1 is FORBIDDEN — use row 2."* The
paragraph immediately below it said the opposite: *"If that text contains `ACTION_LIMIT_REACHED` …
row 1 is the only correct output."* The error-text condition — the entire mechanism the fix for the
original bug depended on — was **missing from the list that claimed to be exhaustive.** Given a
closed FORBIDDEN list and a permission a paragraph later, the model obeys the prohibition (D25, D47).
The gate had a real cause (`c5a10922`, a fabricated already-applied) so it must stay; it was simply
incomplete.

**Detection heuristic.** Two checks, both cheap:
1. **Whitelist completeness.** For every branch gated by an enumerated evidence list ("ONE of these
   must be true", "Nothing else counts", "if neither 1 nor 2"), grep the rest of the prompt for other
   sentences that license the *same* branch. Every such condition must appear as a numbered item in
   the list. A condition that licenses a branch from outside its own whitelist is dead.
2. **Before/after the gate.** When a gate is added to stop over-firing, count how often the branch
   fired in the window before and the window after. A drop to `0/N` is not "the guessing stopped" —
   it is the branch becoming unreachable (see the CLAUDE.md escalation ladder, rung 0).

**Fix direction.** COMPLETE the list — add the missing condition as a numbered item and fix the
"neither 1 nor 2" arithmetic — rather than restating the permission a fourth time below it. Applied
2026-09-04 to all 12 KKB/Maya conversation prompts as item 3 (`ACTION_LIMIT_REACHED` / "an active or
duplicate request already exists").

**Source.** All KKB + Maya conversation prompts, 2026-09-04, from tracker row 103. Regression of
commit `feb9405`. Related: D25, D47, D51, D52.

### D63 — A sample conversation whose CONTEXT omits the field a branch keys on demonstrates the wrong branch

**Symptom.** A branch rule is correct and stated twice, and the bot still takes the other branch on
live traffic. Inbound calls `b48f70fb` (profile location `VILL-MURARI TAND KAKO, …JEHANABAD…`) and
`2d8b7cb1` (`BHOJPUR`) both asked the open area question hours AFTER the confirm-first fix (D61)
shipped and was verified on two harness calls.

**Root cause.** The prompt's *Example 2* is titled "Returning caller, LIVE profile found" and its
context line lists what the profile carries — name, role, age, gender — but **not** location. So the
sample is, strictly, a profile with no location, where the open ask is correct. To the model it reads
as the demonstration of what to do on a returning-caller call, and the open ask is what it shows. A
rule stated twice loses to a worked example shown once (D50).

**Detection heuristic.** For every rule of the form "if X is present say A, otherwise say B", list
the samples that exercise that step and check each one's stated context for X. A sample whose context
is *silent* about X is the bug — it will be read as the default branch. Every branch of a decision
needs a sample that names the deciding field explicitly, and a sample must never demonstrate the
fallback on a case the rule reserves for the primary branch.

**Fix direction.** Give the sample's fetched profile the field, show the primary branch, and add a
stage direction naming why (*"the fetched profile carries a location, so it is CONFIRMED, never asked
openly; the open question belongs to a caller with NO location on file — see Example 1"*). Keep the
fallback demonstrated in the sample that genuinely lacks the field. Also add the guard the live data
demands: a stored location may be a full postal address, so confirm the town/city inside it and never
read the address aloud.

**Source.** All six KKB/Maya inbound prompts, 2026-09-04. Bugs `b48f70fb`, `2d8b7cb1`. Related: D50,
D57, D61.

### D64 — A "CLOSED SET" of allowed sentences that enumerates only some branches deletes the others

**Symptom.** A branch rule is correct, its line is quoted, the structure is right — and the bot still
takes a different branch, using a wording from further down the section. Maya inbound `0baf8765`:
the fetched profile carried `Vasundhara, Ghaziabad, India` and Maya asked the open *"which area of
Ghaziabad"* question, hours after the confirm-first branch list was added directly above it and the
KKB twins had been verified taking the confirm branch (`8235309e`, `537549c6`).

**Root cause.** Below the branch list sat a tightening from an earlier bug: *"**CLOSED SET: this turn
is EXACTLY one of the two sentences above**, with only the `[city]`/`[area]` slots filled, and NOTHING
else."* Both of "the two sentences above" were the OPEN questions. The confirm line, added later as
branch 1, was never added to the set — so the prompt simultaneously told the model to confirm and
told it that only the two open sentences were permitted here. A closed set is the strongest kind of
instruction in a prompt; anything left out of it is not merely unemphasised, it is **forbidden**.

**Detection heuristic.** Grep for closed-set language — `CLOSED SET`, `EXACTLY one of`, `only these`,
`Nothing else counts`, `the ONLY line permitted`, `and NOTHING else` — and for each hit, enumerate the
lines it admits, then compare that against every branch of the surrounding decision. Any branch whose
line is not in the set is dead. This is the same shape as **D62** (an evidence whitelist that omits
the case the mapping needs): both are enumerations that fell out of date when a branch was added
above them. **When you add a branch to a decision, grep downward for the enumeration that has to
learn about it.**

**Fix direction.** Add the new branch's line to the set, and say explicitly that it is in the set.
Do not weaken the closed set — it exists because free composition here caused a different bug — and
do not restate the branch rule a third time above it.

**Source.** All four Maya prompts, 2026-09-04. Bug `0baf8765`. Related: D62, D61, D50.

### D65 — A licensed spoken line that is indistinguishable from the action becomes a substitute for the action

**Symptom.** The bot tells a caller their application went through on a call where `apply_job` was
never invoked. Measured at 5 of 23 success-claiming calls (21.7%) and still occurring after the
spoken-variant collapse: `af52d37c`, `0162ff69`, `15b61561`, and earlier `3c7e9ad0`, `febe0441`,
`19616c90`, `1fe093a9`, `29c4f152`.

**Root cause.** The prompt licensed a "conversational bridge before apply" whose allowed examples
were *"ठीक है, आपकी तरफ़ से अप्लाई कर देती हूँ."* and *"अप्लाई कर देती हूँ."* — sentences that assert the
apply is happening. Ten lines below, the same section said **"Never narrate the apply as if it is
happening."** The two cannot both be obeyed, and on the failing calls the model spoke the licensed
line, ended the turn, and then spoke the success line: from inside the model's own transcript the
apply *had* been performed, because the sentence that performs it had been said. Four escalating
prose guards, a tool-description constraint and a variant collapse had all failed first, because each
of them made the wrong output less encouraged while leaving it **available**.

**Detection heuristic.** For every action that must be performed by a TOOL, list the spoken lines the
prompt permits immediately before that tool call, and ask of each: *if the tool never ran, would this
sentence be false?* Any line that would be false is a fabrication the prompt has pre-authorised.
Grep the samples too — 32 sample-conversation instances carried the bridge line, so the examples
demonstrated the substitution even where the rule forbade it (D50).

**Fix direction.** Remove the line, do not forbid it harder (escalation ladder rung 3). Leave only an
acknowledgement that asserts nothing about the action (*"ठीक है।"* / *"ಸರಿ."*), state that no line
containing the action word may precede the tool RESULT, and change every sample to match. The pause
the bridge used to cover is already spoken by the tool's own `hold_message`, so nothing is lost. With
nothing available to say, the only way forward is the tool call.

**Source.** All 12 KKB/Maya conversation prompts, 2026-09-04. Related: D57, D50, D25, D47.

### D66 — An ALIAS for an input variable makes every test of that variable silently false

**Symptom.** The bot tells a job-seeker there are no jobs on a call where jobs were supplied. Harness
call `8d3453b1`: `agent_args` carried `recommendations` with **22 valid jobs**, and the bot said
*"अभी आपके लिए मुझे जॉब्स नहीं मिल रहीं — एक बार फिर से देखकर मैं आपको वापस कॉल करती हूँ।"* — eight times,
including directly after the caller asked "कौन सी जॉब्स हैं सारी बता दीजिए". Not one job was named.

**Root cause.** The Input Variables section declared the variable with an alias:
*"**`${recommendations}`** as job_recommendations — a JSON array of up to 10 job objects…"*, and then
**65 references across six prompts used the alias instead of the variable**, including the Pre-check
whose entire job is to decide whether any jobs were supplied: *"Before greeting the user or fetching a
profile, check `job_recommendations`. If it is empty, null, or contains no valid jobs → skip all steps
and trigger No-Match Fallback immediately."* There is no input called `job_recommendations`. A model
that takes that instruction literally finds nothing, concludes "empty", and fires the missing-job-data
line — which is exactly what a confused, low-ASR-quality call pushes it towards, because the
pre-check is the first and simplest rule in the section. The emptiness guard was **inverted by a
naming convention**, and it stayed hidden for as long as it did because on a clean call the model
reads the populated `${recommendations}` elsewhere and never consults the pre-check.

**Detection heuristic.** For every prompt, extract the set of `${...}` input variables actually
declared, then grep for identifier-shaped tokens used in rule prose (backticked or bare snake_case)
that are NOT in that set and are not tool names, tool parameters or response fields. Any such token
that appears in a CONDITION — "if X is empty", "check X", "X contains no" — is a test that can never
pass. Aliases are the usual source: look for "`${var}` as other_name", "also called", "referred to
below as".

**Fix direction.** Delete the alias and use the real variable name everywhere — one name for one
thing. This is language-agnostic content, so the rename is byte-identical across every language of the
bot (never localise a variable name). Do not "document the alias more clearly": the model does not
need a glossary, it needs the condition to name something that exists.

**Source.** KKB Hindi/Kannada (both Signals and legacy) and Maya Hindi (both), 2026-09-04 — 65
references. Found by `raya/overnight/overnight_sweep.py` on its second call, not by a report.
Related: D59 (reading the wrong field), D62 (a condition that can never be satisfied).

### D67 — A spoken template with the slot INSIDE it makes the raw variable token the default utterance

**Symptom.** The bot reads a variable token aloud. Harness call `718aa8ab` on Maya outbound opened
with *"नमस्ते। मैं माया, **${college_name}** की ओर से बात कर रही हूँ"* — the caller heard the literal
dollar-brace token.

**Root cause.** The prompt had **three** separate rules against it, all correct and all ignored:
*"Never read the raw variable token aloud"*, *"`${college_name}` IS A SLOT, NOT WORDS TO SAY … NEVER
say the token"*, and a parenthetical *"(If college_name is empty/missing, use the name-only
fallback…)"*. But the **script** was a single quoted sentence with `${college_name}` embedded twice,
introduced as *"Use this ONE opening line on every call"*. So the token was the default utterance and
every guard was a caveat applied afterwards. The platform drops empty arguments rather than sending a
blank, so an unsupplied field arrives AS the token — meaning the one case the guards existed for is
also the case where the model cannot see that anything is missing.

**Detection heuristic.** Grep every quoted spoken line for `${`. A `${...}` inside quoted speech is a
latent utterance of that token, and the number of rules forbidding it is irrelevant. Then check
whether the prompt gives the model any way to SEE that the value is absent: if the only signal is the
token itself appearing in the script, there is nothing to check against.

**Fix direction.** Two things together, both mechanism rather than wording:
1. **Print the value back to the model** — *"The value you were given for this call is: college_name:
   ${college_name}"* — plus *"AN UNSUBSTITUTED TOKEN COUNTS AS EMPTY: if that line still shows a
   dollar-brace token, the field was not supplied."* Now emptiness is observable instead of asserted.
2. **Two quoted openers, chosen by looking** — one that uses the value (with a `[college]` slot, not a
   `${...}` token) and one that names no institution — and say which is safe by default. DKB fixed the
   identical fault the identical way in Turn 2 (`e2ce642a`, `12dc1466`); Maya had inherited the
   one-template shape.

**Source.** Maya Hindi and Maya Hindi Signals, 2026-09-04. Bug `718aa8ab`, found by the overnight
sweep. Maya's INBOUND prompts were already safe — their opener names no institution in the quoted
line at all. Related: D61 (script first, condition after), D64, D25.

### D68 — An input the campaign SENDS that the prompt never names is an input the bot cannot use

**Symptom.** A bot asks for something it was already told. Maya outbound asked the area from scratch on
every call — `24293fbe`, `d57b9ff6`, `78ef362f` — each of which was dialled with
`location: "Ghaziabad"` in `agent_args`. Three detectors flagged it independently
(`location_chain` C1/C2, `location_reconfirm` A) and it survived a fix to the confirm branch and a fix
to the closed set, because neither was the cause.

**Root cause.** `${location}` appears **9 times** in the KKB Signals master and **zero times** in any
Maya prompt. The campaign has always sent it; Maya was never told the variable exists. So the location
decision could only ever consult `contact_memory` and the fetched profile, and on a first call to a
seeker with no stored location both are empty — the open ask was not a mis-ranked branch, it was the
only reachable one.

This is D66 inverted. D66 was a condition naming a variable that does not exist; this is a variable
that exists and is named nowhere. Both make a branch unreachable and neither is visible in the
prompt's own text, because nothing in the prompt is wrong — something is *absent*.

**Detection heuristic.** Diff the `${...}` variables a prompt declares against the `agent_args` keys
its live calls actually carry:

```bash
python3 scripts/raya_call.py <agent_uuid> 5 | grep -A20 '^agent_args'   # keys really sent
grep -oE '\$\{[a-z_]+\}' "<prompt>.md" | sort -u                        # keys the prompt knows
```

Anything in the first list and not the second is being paid for and thrown away. Run it per bot, not
per family: a variable declared in the master says nothing about the mirror or the spin-off.

**Fix direction.** Declare the variable, and place it in the decision at the priority the master gives
it — for a caller's location that is FIRST, ahead of memory and the fetched profile, because it is the
value the campaign selected this caller on. Add the unsubstituted-token clause at the same time (D67):
an unsupplied argument arrives as the raw token, so "empty" has to include "still a token".

**Source.** Maya Hindi and Maya Hindi Signals, 2026-09-04, found by the overnight sweep after two
earlier fixes to the same symptom missed. Related: D66, D67, D61.

### D69 — An identifier with no rule of its own falls to the "numbers in words" default and is spoken as a quantity

**Symptom.** QA: *"pincode is read in words, should be 11205 not 11 thousand two hundred etc"*. Live
call `a899617e` was sent `location: "Muradnagar, 110045"` and said *"लोकेशन मुराद नगर, **११००४५** है"*.

**Root cause.** Three rules, none of them wrong on its own:
`## Numbers` — "do not write digits in spoken Hindi output, write them in words" — with **cardinal**
examples (`३५०` → "तीन सौ पचास"); `## Phone number` — "say digit by digit in words" — a carve-out for
one identifier; and **nothing at all for a PIN code**. So a PIN inherited the cardinal default. Behind
that, the location sentence deliberately instructs the model to speak `${location}` *exactly as it
arrives* (that instruction fixed six calls that had substituted the profile's city), so the PIN was
being pushed through by design rather than by accident.

**Detection heuristic.** List every kind of number the bot can ever speak — salary, vacancy count,
ordinal, age, experience years, phone, PIN, plot/house/gali/sector number, OTP, job id — and check that
each has an explicit spoken form. Any kind not named inherits the general rule, and the general rule is
almost always cardinal. Then check the reverse: for each input variable that reaches a spoken line,
does the value shape include digits the caller must not hear?

**Fix direction.** Two changes, not one. (1) Give the identifier its own rule next to the phone-number
carve-out — digit by digit, never a quantity — so it is not inheriting anything. (2) Better, remove it
from speech entirely: the spoken line strips every digit out of the value first, phrased as a
*formatting reduction of the given value* so it cannot be read as licence to substitute a different
place. Both, because the first covers the case where a number must be said and the second means it
usually is not.

**Source.** KKB Hindi/Kannada, Signals and legacy, 2026-09-07. Bug `a899617e`, fix verified on
`36802370`. Related: D67 (a token inside quoted speech).

### D70 — A rule triggered "after X is captured" never fires when X is only-if-missing

**Symptom.** QA: *"at the end bot used to reiterate the details and ask nearby location but it didn't
this time"*. The end-of-call read-back stopped happening on calls where the caller's profile was
already complete — `8674462f`, and reproduced on `6fe05a86` and `1536830c`.

**Root cause.** The read-back read *"after the Phase-2 fields are captured, read back ALL the details"*.
Every Phase-2 question is gated on **only if missing**, and granular location is explicitly skipped when
the location turn already captured an area. On a complete profile, Phase 2 therefore asks nothing,
nothing is "captured", and the trigger condition is never satisfied. The rule was not ignored — it was
never true. Worse, the read-back is the only point in the call where a **stale stored value** gets
corrected, so the callers it silently skips are exactly the ones whose records are wrong (this caller's
profile says `Bengaluru` while the campaign dialled her in `Muradnagar`).

**Detection heuristic.** For every rule whose trigger is the *completion* of another step, ask what
happens when that step legitimately does nothing. Grep for triggers of the form "after … is captured",
"once … has been collected", "after you have asked …" and check each against the case where the
preceding step is entirely skipped. A step made of only-if-missing questions can always be a no-op, so
any rule hanging off its completion has a silent zero case.

**Fix direction.** Trigger on the **event**, not on the side-effect of a conditional step: "after a
successful apply, whether or not Phase 2 had a single question to ask". Same shape as gating on the
chokepoint rather than on a path (D63/D64).

**Source.** All six KKB/Maya Signals prompts, 2026-09-07. Bug `8674462f`. **Fix deployed, NOT
verified** — three harness attempts ran past the tester's five-minute cap before reaching the end of
the flow. Related: D63, D64, D68.

---

### D71
**A script/spelling rule backed by a CLOSED LIST converts what is on the list and passes the rest through verbatim.**

**Symptom.** The bot speaks a stored value in its written form — Latin script, ASCII digits, an
acronym — inside an otherwise perfect Indic sentence, *on some calls and not others*. It reads as
flakiness. It is not.

**Root cause.** Every "speak X in <script>" rule in these prompts is backed by an enumeration:
Canonical Location Spellings, Maya's "Common conversions", the first-name list. The prose says
"Devanagari only" and even carries an off-list fallback, but the **examples are what the model
actually follows**, so a value on the list is converted and a value absent from every list is
emitted unchanged. Four proofs in one night, three different lists, one mechanism:

| call | value in the arguments | what the caller heard | which list it was off |
|---|---|---|---|
| `7b841e6b` | `location: "Sarjapur, 110045"` | "लोकेशन Sarjapur, 110045 है" | Canonical Location Spellings |
| `1536830c` | `company: "SARA ENTERPRISES"` | "SARA ENTERPRISES" | no company list exists |
| `9d5e9848` | `company: "MAHARAJA ENGINEERING WORKS"` | said verbatim | no company list exists |
| `b6353cfb` | `college_name: "VMLG College"` | "VMLG College" | Maya "Common conversions" (had LR, TPS, MMH) |

On every one of those calls a value that WAS on the relevant list came out correctly **in the same
breath** — `7b841e6b` said गाज़ियाबाद, `02c5f7f0` said "ग्लोबल केमिकल्स" out of `GLOBAL CHEMICALS`.
So the split is deterministic, and the five preceding `Muradnagar` calls that passed were passing
because the value was on a list, not because the rule was working.

**Detection heuristic.** Two passes, and the second is the one that finds real bugs.
1. *Static.* For every rule of the form "speak <thing> in <script>", locate its backing list and ask
   what the prompt tells the model to do with a value that is **not on it**. If the answer is a
   trailing clause, a conditional ("if you are unsure…"), or absent, it is this bug. A fallback
   conditioned on the model's *uncertainty* never fires: an acronym is not something it feels unsure
   about (cf. D70 — a trigger that is never true).
2. *Against production arguments.* Pull the values the campaign actually sends for each spoken
   variable and check them against the list. This is what turned "VMLG is one bad call" into
   "`college_name` is `VMLG College` on 345 of 460 calls and it was on no list" — i.e. the majority
   of that bot's callers heard a Latin acronym.

**Fix direction.** Do not lengthen the list and do not re-word the rule (that is the banned third
wording). State that **the list is examples, not an allow-list, and that being absent from it is the
ordinary case**, then demonstrate the conversion on the exact values that failed. Where the value is
consumed in one specific sentence, put the conversion at the point of use as an ordered precondition
("convert first, then say the sentence") rather than as a caveat after the spoken template — and
delete any nearby permission to pass the value through ("say the sentence as it arrives", "the
actual literal value", "VERBATIM"), which is the competing instruction the model was obeying.

**A control group in the same fleet, found on 2026-09-08 and worth more than the argument.**
**TRRAIN leaked nothing across 98 cached calls.** Its prompt has no off-list clause and no company
list — what it has is the conversion stated **at the line that speaks the value**: *"speak the NAMED
line, with the role transliterated into Devanagari"*. KKB, Maya and DKB state the Devanagari rule in
up to five distant sections and leaked on 13 calls between them. Same fleet, same model, same voice,
same script requirement; the difference is where the rule sits. That is the strongest evidence in the
repo for fixing this class at the point of use rather than by adding another general statement.

**Source.** 2026-09-08, QA calls 5035574 / 5061404. 16 prompts. Standing detector:
`raya/regression/spoken_form.py`. Related: D50 (the sample outvotes the rule), D64 (closed set),
D67, D72, D73, D77.

---

### D72
**An English field LABEL inside a spoken template is read out to the caller.**

**Symptom.** Mid-sentence, in Hindi, the bot says "**Qualification:** आईटीआई वेल्डिंग" — a form label
with a colon, in Latin script, in the middle of speech.

**Root cause.** The prompt's own spoken template said it. `Qualification: [qualification]।` sat inside
the Step-3 deep-dive block, and **three to five sample conversations per file demonstrated the agent
saying it aloud**. This is not a model error at all: the bot was reading the template correctly. The
label had been written as scaffolding for whoever maintains the prompt and never converted into
speech. The Kannada twins had already solved it the right way — `ಕ್ವಾಲಿಫಿಕೇಷನ್:` — so the Hindi files
were also behind their own mirrors.

**Detection heuristic.** Grep every spoken template and every `> **Agent:**` line for
`\b[A-Z][a-z]+\s*:` — a capitalised English word followed by a colon inside quoted speech. Cross-check
against the language twin: if one language transliterates the label and the other does not, the
untransliterated one is the bug. `raya/regression/spoken_form.py` carries this as an always-blocking
`FIELD LABEL SPOKEN ALOUD` check.

**Fix direction.** Transliterate the label into the target script (matching whatever the twin already
does), or fold it into the sentence so no label is spoken. Fix the samples in the same edit — a
template fixed while five samples still demonstrate the old form will regress (D50).

**Source.** 2026-09-08. 31 occurrences across 8 Hindi prompts. Live: `1536830c`, `9d5e9848`,
`4872fa0e`. Related: D50, D71.

---

### D73
**An emptiness test that enumerates the placeholder STRING and NULL, but not the ABSENT argument.**

**Symptom.** The bot greets a business owner with **"क्या आप Not Available से बोल रहे हैं?"** — "are
you calling from Not Available?" Seven live calls: `564e1d45` (2026-09-05), `343f8924`, `7427b12e`,
`7db95662`, and in Kannada `be4ab8c3` (2026-09-07), `061fb2cd`, `431a070a`.

**Root cause — and it is the opposite of what the symptom suggests.** Across 137 cached DKB calls
carrying a `company_name` argument the value was **always real, never the string "Not Available"**.
On the seven failing calls the argument was **not sent at all**. The prompt's test read
*`If ${company_name} is exactly "Not Available" or is NULL`* — two arms, neither of which matches a
**dropped** argument, which the platform delivers as the raw `${company_name}` token. With no arm
matching, the model fell through to the present-value branch, which said to substitute *"the actual
literal value"*, and it synthesised the placeholder wording it had just read in that very section.
So the prompt supplied both the missing branch and the wrong words to fill it with.

**Detection heuristic.** For every `${var}` that is spoken or branched on, check the emptiness test
covers **three** cases, not two: the placeholder string, NULL/empty, and **the unsubstituted token**.
The platform drops an argument it was never given rather than sending a blank, so absence always
arrives as `${var}` itself. A file that declares "AN UNSUBSTITUTED TOKEN COUNTS AS EMPTY" for one
variable and not for its neighbours is the strongest signal: the author knew the rule and applied it
once. Also grep for any nearby "literal value" / "VERBATIM" / "as it arrives" wording — that is the
branch the model takes when the test fails to match.

**Fix direction.** Add the absent case to the existing test rather than writing a new guard, so the
pass-through branch becomes unreachable when there is no value (remove the wrong option — ladder rung
3 — instead of forbidding the output). Say explicitly that the placeholder string is a value the
prompt tests FOR and never something to speak.

**Source.** DKB, 2026-09-08. 4 outbound DKB prompts. Related: D67 (the token spoken aloud), D71, D64.

---

### D74
**A sample conversation whose Context line defines a variable in terms of itself, and whose speech line then shows the raw token.**

**Symptom.** The bot speaks an unconverted variable value — or the token itself — inside an otherwise
correct scripted line, while four separate rules above tell it to convert.

**Root cause.** Maya's Example 1 and Example 2 opened with **`**Context:** ${college_name} =
${college_name}.`** — a tautology that establishes no value at all — and their agent lines then read
**`> **Agent:** नमस्ते। मैं माया, ${college_name} की ओर से…`**. Two worked examples per file
demonstrated the agent uttering the unsubstituted variable. On `b6353cfb` the bot did exactly that
with the real value, in Latin. The rules said convert; the demonstration said copy; the demonstration
won.

**Detection heuristic.** Two greps, both cheap and both worth running on every prompt:
`^\s*>\s*\*\*Agent` lines containing `\$\{`, and Context/stage-direction lines matching
`\$\{(\w+)\}\s*=\s*\$\{\1\}`. Neither can ever be legitimate: a sample exists to show a concrete
value being handled. This is distinct from D67, which finds tokens inside **rule** text — a D67 sweep
that greps only rules will pass a file whose samples are the actual cause.

**Fix direction.** Give the sample a concrete value, pick one that exercises the hard shape (an
initialism, an off-list place), show the **converted** form in the speech line, and add a stage
direction naming what was substituted — "`${college_name}` = `LR College`, an initialism, so the
spoken form is एलआर कॉलेज".

**Source.** Maya Hindi + Maya Hindi Signals, 2026-09-08. Bug `b6353cfb`. Related: D50, D63, D67, D71.

---

### D75
**A branch test that never names WHICH field it reads, satisfied by a different field that happens to carry the trigger string.**

**Symptom.** A two-way branch takes the wrong arm on one bot and the right arm on its twin, with the
same rule, the same prompt family and the same field value. It reads as model whim. It is not — it
splits by which *arguments the campaign sends*, and the split is total.

**Root cause.** Maya's opener chooses between naming the caller's college and naming no institution:

> **A — college_name shows a REAL name** → say it
> **B — college_name is empty, "Not Available", or still a token** → name NO institution

Arm B's trigger is the bare string `"Not Available"`. `maya-hi-out` is sent no `contact_memory`;
`maya-hi-signals` is sent `contact_memory: "Not Available"`, which reaches the model inside the
Contact context block as `Here is the caller context: {Not Available}`. The prompt never said which
field the test reads, so a different field's value satisfied it.

**Measured, before any edit (ladder rung 0 — count before you write a word):**

| bot | `contact_memory` sent | branch A fires |
|---|---|---|
| `maya-hi-out` | not sent at all | **48 / 48** |
| `maya-hi-signals` | the string `"Not Available"` | **2 / 14** |

Twelve of fourteen campaign callers were greeted with no institution, which removes the entire
campus-recruitment premise of the call. Counting first is what turned "the opener is flaky" into a
one-line cause; a third wording of the branch would have changed nothing, because the branch was
being *correctly* evaluated against the wrong input.

**Detection heuristic.** For every branch whose arms are selected by a literal value — `"Not
Available"`, `"NA"`, `"None"`, `"Any"`, `"null"`, `""` — check that the condition names the field it
tests. Then grep the whole prompt for that same literal appearing in ANY other input's
documentation, sample or injected block. A sentinel shared between fields and used as a branch
trigger is this bug. Cross-check against production arguments **per bot**: the same prompt on two
bots receiving different argument sets is where it shows, and comparing one bot's calls to each
other will never reveal it.

**Two things learned running this sweep across all 20 prompts** (2026-09-08), so the next run is not
a wall of noise. It returned 51 sentinel conditions, of which a crude "does this line name a field"
test flagged 33 — and **every one of the 33 except Maya's was a false positive**:

- **Look at the two lines ABOVE the condition, not just the condition.** DKB's *"If the raw value is
  exactly \"Not Available\" — STOP"* names nothing on its own line, but the line directly above it
  is *"Read the raw value of `${job_role}`."* Four files, all fine.
- **Exclude two shapes outright.** The deep-dive rule *"If any field is missing or 'Not Available',
  skip it naturally"* is deliberately generic and correct — it is about the job record's own fields,
  not a branch on an input. And the output prompts' *"If a value is not present, use 'NA'"* is an
  instruction about what to WRITE, not a branch at all.

What is left after those two exclusions is the real signal: a condition whose sentinel is also a
plausible value of a **different** field that reaches the model in the same context window. Maya's
opener was the only instance in the fleet.

**Fix direction.** Name the field in the condition and add the exclusion explicitly — "ONLY the
`college_name` value line decides this; no other field's value has any bearing on it, whatever it
says", naming the specific colliding field so the reader knows which trap is meant. Do not
re-word the arms; the arms were fine.

**UNCONFIRMED as the diagnosis of the Maya case, 2026-09-08.** The correlation is strong:
`maya-hi-out` receives no `contact_memory` and fires branch A 48/48; `maya-hi-signals` receives
`contact_memory: "Not Available"` and fires it 2/14. The fix naming the field was written, deployed,
and **failed on `d15a8f9b`** — so the fix does not work, whatever the cause. I then recorded the
hypothesis as REFUTED on the strength of `910b2d29`, a dial that omitted `contact_memory` and still
opened with no institution. **That retraction was itself wrong:** `910b2d29` made **zero tool
calls** and fabricated an application, so it is a degenerate call and not a control for anything.
The hypothesis is therefore untested, not refuted, and this entry says so rather than claiming
either way.

What the episode is worth keeping is the method lesson, which is the opposite of the one I drew:
**a per-bot correlation is not a mechanism.** Two bots differing in one argument and in their
behaviour is a hypothesis, and the cheap controlled dial that distinguishes it from the alternatives
costs one call. I wrote the fix from the correlation and spent the dial afterwards; the dial should
have come first. The `D75` shape — a sentinel-triggered branch that does not name its field — remains
a real thing to look for (the fleet sweep found the shape in DKB's `job_role` check, correctly
resolved one line above), but it has **no confirmed instance**.

**Source.** Maya Hindi + Maya Hindi Signals, 2026-09-08. Correlated on `08a8ff4f`, `9fd1e0d9`,
`35dd4e66`, `9fa8975f`, `771fc142`, `6e3ba9ff`, `8e04a854`; refuted by `910b2d29`. Related: D67,
D68, D71, D73.

---

### D76
**A rule that requires the model to maintain a RUNNING COUNT across turns. It will lose it.**

**Symptom.** The job list numbers itself पहला, दूसरा, तीसरा … and then the next batch starts at पहला
again. The caller who says "पहला" now means a different job from the one the bot means.

**Root cause.** The prompt says: *"Ordinals run continuously across batches and NEVER restart. If a
batch ended on तीसरा, the next batch begins at चौथा… The ordinal is a running count of the jobs you
have actually READ ALOUD on this call."* That is not a rule the model can follow by reading — it is a
counter it must carry across an unbounded number of turns, alongside which array entries it has
already named. It loses it, and it loses it more often than not.

**Measured (ladder rung 0, over 1,675 cached calls):** 82 calls spoke an ordinal; 24 of them got past
one batch; **14 of those 24 — 58% — restarted the count.** Examples: `5a1c0c77` went
पहला दूसरा तीसरा four times over, and `90f70860`, `dc562e00`, `5d6702fc`, `738d3400`, `75e69c6b`,
`9d5e9848`, `a0999f10` all restarted once. It happens on inbound and outbound, Hindi and Kannada, on
the 219k prompt and on the 69k rewrite alike (`09978532` and `4d6d4d02` in the same A/B run), so it
is neither a prose-volume problem nor bot-specific. **A guard that fails on the majority of the calls
that reach it is not a guard.**

**Detection heuristic.** Grep for rules containing "running count", "continuously", "never restart",
"do not renumber", "the same number as before", "keep track of how many". Then ask the question that
decides it: *can the model verify compliance from what is in front of it in this turn?* An ordinal
that depends on what was said three turns ago cannot be checked at the moment of speaking, and rules
that cannot be self-checked at the point of use are the ones that fail (contrast the positional rules
that DO hold — "this line may only appear in a turn containing a fresh apply_job result" is checkable
against the turn being composed).

**Fix direction — remove the requirement, do not restate it.** Either
(a) drop the running count and let later batches be introduced without numbering ("एक और जॉब है — …"),
so selection happens by role and company, which the phonetic-confirmation rules already cover; or
(b) keep per-batch numbering but make it explicitly per-batch and re-anchor selection on the name.
Both remove the cross-turn state. What does NOT work is a third wording of "never restart": the rule
is already unambiguous, and it is the memory it presumes that is missing, not the clarity.

**Source.** All KKB/Maya prompts, measured 2026-09-08. Related: D70 (a trigger that is never true),
D71. The fix is an owner decision because it changes spoken output; the experiment belongs on the
slim A/B bot first.

---

### D77
**The `[slot]` markers a spoken template is BUILT FROM get read out as words.**

**Symptom.** A caller hears the template instead of the sentence: *"हैलो! क्या आप **[company_name]**
से बोल रहे हैं?"* — asked of the owner of that very business.

**Root cause.** Every spoken template in these prompts is written with square-bracket markers —
`[company_name]`, `[job_role]`, `[role]`, `[शहर]`, `[नाम]` — and **not one prompt in the fleet had a
rule about them.** They carry a rule for `*( )*` stage directions ("a parenthetical is never
speech") and a hard rule against speaking tool payloads, and both were written after those specific
failures; the brackets the templates are made of were never mentioned, because to a human reader
they are obviously placeholders. They are not obviously placeholders to a model that has just been
handed a sentence with one in it.

**Measured: 13 calls across 6 bots** (`dkb-hi-out` 13 turns, `dkb-kn-out` 4, `dkb-hi-signals` 3,
`kkb-hi-signals`, `kkb-kn-out`, `maya-hi-out` 1 each), 2026-07-16 to 2026-09-04. The placeholders are
the mild end of it. The severe end is internal text:

| call | spoken to a caller |
|---|---|
| `1131d79c` | "क्या आप **[company_name]** से बोल रहे हैं?" · "आपकी एक posting है — **[job_role]**, **[num_vacancies]** vacancies, सैलरी **[salary]**" |
| `f391ab35` | "**[Proceeding to Phase 2]**" and "**[INTERNAL: update_job_status called with status \\"open\\" for the job]**" |
| `1b7fb500`, `78ef362f` | "**[UUID from create_profile result]**" |

**And the severe end is worse than a marker.** On 2026-09-04 three bots read an entire fabricated
tool call out loud, payload included:

    78ef362f  maya-hi-out  *(Silent tool call: create_profile with agentId: "up-getjob",
                             phone: "+917946350285", name: "सुनीता", age: 27, gender: "female")*
    1b7fb500  kkb-kn-out   *(Silent tool call: create_profile with name: "ಸುಜಾತಾ",
                             phone: "+917946350285", agentId: "up-getjob")*
    35de19e7  kkb-hi-in    *(… name: "आर्यन", age: 26, gender: "male",
                             totalYearsOfExperience: 1)*  … profile_id: <UUID from create_profile result>

The caller heard their own phone number, name, age and gender recited back as a JSON-ish payload —
and no tool ran, so these are the same calls as the fabricated-apply class. The prompts already ban
speaking a payload and already say a `*( )*` parenthetical is never speech; both bans are stated in
prose far from any template, which is the D71 shape again.

**Currently dormant, not currently fixed by anything targeted:** the window since 2026-09-06 is
clean over 252 calls, most likely because the 2026-09-04 bridge removal forbade any pre-result line
containing "अप्लाई". The bracket rule added on 2026-09-08 is preventive rather than corrective, so
the honest status of this class is *no occurrences in 252 calls*, not *fixed*.

**Detection heuristic.** Grep assistant turns for `\[[A-Za-z_][\w :"'.]{2,60}\]`, for a
Devanagari/Kannada run inside brackets, for `\*\([^)]+\)\*`, and for a line beginning `INTERNAL`.
None of them has any legitimate reason to reach a caller, so this check needs **no allow-list and no
info tier** — unlike the Latin-script checks, where the prompts deliberately script Hinglish. Run it
against production rather than reading prompts: the bug is invisible in the prompt, where the markers
are correct.

**Fix direction.** State the rule that was missing, once, in a section every prompt has: a
bracketed marker is a slot to FILL and never words to say; if you cannot fill it, say the sentence
without that part or say a different sentence. Extend it to `*( )*` and to `INTERNAL` lines in the
same breath, since the same calls produced all three. Language-agnostic, so byte-identical in every
file.

**Source.** All 20 conversation prompts + the slim rewrite, 2026-09-08. Detector
`raya/regression/bracket_leak.py`, 9/9 self-test. Related: D67 (`${token}` in quoted speech), D74
(a token inside a sample's speech), D71.


---

### D78
**A guard stops the line it names, and a DIFFERENT line carries the same claim.**

**Symptom.** A caller whose application failed twice is told the application went through. The
prompt has an explicit, well-tested guard against exactly that — and the guard was obeyed.

**Root cause.** On `e75bf95f` and `7e586f14` (2026-09-08, `kkb-kn-signals`, **both real callers**),
two `apply_job` calls returned 422. The bot did everything the guard asks:

1. spoke the row-2 failure line after the first 422;
2. spoke the second-consecutive-failure line after the second;
3. spoke the Need Capture acknowledgement with the correct **verbatim** no-job-remains line, which
   the prompt quotes precisely so there is "no free slot" for a success claim.

Then it said the **Phase-2 bridge**, whose first words are *"ಅಪ್ಲೈ ಆಗಿದೆ"* — "the apply has been
done". The bridge is gated on a successful apply, in prose, in a different section. The guard
protected the sentence it was written about; the claim simply arrived inside another sentence that
also contained it.

**The generalisation, and it is the useful part.** A prohibition is scoped to a STRING. An assertion
is a property of MEANING. Enumerate every line in the prompt that asserts the same fact, not just
the one that failed — and check each of them separately. Here the fact "the apply succeeded" was
asserted in two places: the success line (guarded, positional rule, five call ids in its comment) and
the Phase-2 bridge (unguarded, because nobody thought of it as a claim).

**Detection heuristic.** For each fact the bot can state that might be false — an application
submitted, a record saved, a callback promised, a place confirmed — grep the prompt for **every**
quoted line that asserts it, then ask of each: what makes this one unsayable when the fact is false?
A line whose answer is "a rule in another section" is the next occurrence. Mechanically:
`grep` the success/save/confirm vocabulary (`हो गया`, `ಆಗಿದೆ`, `नोट कर लिया`, `सेव`) across all
quoted lines and count how many distinct lines carry each claim. More than one is this pattern.

**Fix direction — rung 3, remove the wrong option.** Take the claim out of the line that does not
need it. The Phase-2 bridge does not have to announce the apply: the success line already did, one
turn earlier, in the turn holding the tool result. Deleting the prefix leaves a bridge that cannot be
false, which no amount of gating achieves. **Do not add a second gate.** The first gate works; the
problem was never gate strength.

**Source.** All 6 KKB/Maya Signals prompts + the slim rewrite, 2026-09-08. `fix_presence` row
`phase2-bridge-claims-nothing` carries the removed strings as a must-NOT-contain, so the prefix
cannot come back. Related: D65 (a licensed line indistinguishable from the action), D47, D49.

---

## D79 — a guard stated only at the top of the prompt loses at the point of use

**Symptom.** Given a SMALL `${recommendations}` array (1-3 jobs), an outbound bot presents more
jobs than it was given — inventing roles, companies, salaries, vacancy counts and qualifications
that were never supplied. Intermittent: it happened on 2 of 3 identical dials.

**Root cause.** Not memory, and not example contamination — both were tested and ruled out (see
below). The cause is guard PLACEMENT. The KKB Hindi Signals prompt states "never invent a job"
**17 times**, scattered so the rule sits next to nearly every site that speaks a job. The slim
rewrite compressed that to **3** statements, all of them top-of-file or in a flow summary, and
NONE at the batch-list template or the deep-dive template — the only two lines that actually
speak a job. Same failure shape as the location conversion and the `[company]` script fix: a rule
stated far from the template that consumes the value does not bind. What reads as redundancy in a
long prompt is often the guard being restated at each point of use.

**Detection heuristic.** For each template that emits caller-facing content built from an input
array, check whether the constraint on that content is stated **within the template's own block**.
A guard whose only statements are in an intro section is a finding even when it is worded
perfectly. Count restatements per job-speaking site, not per file.
`raya/regression/offarray_jobs.py` catches the runtime symptom; read its docstring for the blind
spot (deep-dive template only, not the batch-list template).

**Two mechanisms tested and RULED OUT — do not repeat these diagnoses.**

1. **NOT the memory store.** First diagnosis was that the memory prompt's
   `last_options_presented` (`KKB/KKB Memory.md:77`) carried previous calls' job lists into the
   next call. Refuted directly: `memory_enabled` was PATCHed to `false` on the bot and the
   fabrication still occurred (`a4f378b9` — invented "हेल्पर, एबीसी लॉजिस्टिक्स", a company in no
   prompt, no fixture and no tool result). Memory is not required for it.
2. **NOT overlap between illustration names and array roles.** Second diagnosis was that the
   generic-trades illustration ("फिटर", "मशीन ऑपरेटर", "हेल्पर") shares names with roles used as real
   array jobs in the worked example, collapsing the distinction. Refuted by the control: the fat
   prompt has the SAME overlap (illustration at `KKB Placeholder Hindi Signals.md:394`, फिटर as a
   real array job at `:2348`) and does not fabricate.

**Control evidence.** Outbound calls with a 1-3 job array: fat and siblings **5/5 clean**
(`02c5f7f0` 2 supplied/2 named, `1536830c`, `55a44edb`, `8b0e6866` all 1/1, `baf836fe` 3/3).
Slim **2/3 fabricated** (`45e2cb3b` 1 supplied/4 named; `a4f378b9` 1/2+; `85d670bb` 1/1 clean).

**Fix direction.** Put the guard IN the template block — and make it checkable from the turn being
composed rather than as a prohibition: "count the array, then pick the template whose count
matches; there is no template for more jobs than you were given." Do NOT respond by re-adding the
other 14 restatements; place 2 correctly instead.

**Source.** kkb-hi-signals-slim `140d13ca`, 2026-09-08/09. Fix deployed 2026-09-09,
**VERIFY-PENDING** until a post-deploy call on a 1-job fixture proves it.

---

## D80 — a decision table's catch-all row asserts a cause the specific case contradicts

**Symptom.** The bot tells a caller "there is a technical issue" when the real cause was a policy
decision the tool actually named — e.g. an age/channel block. The claim is false, and the prompt
licensed it.

**Root cause.** A lookup table with a catch-all row whose CONDITION is "an error with no reason you
can read" but whose LINE asserts a specific cause ("technical issue है"). When an error arrives that
IS readable but has no row of its own, no row matches, the model falls into the catch-all, and
speaks its cause claim. The table looked complete because every branch had a line; it was the
condition coverage that had the hole.

**Detection heuristic.** For every decision table in a prompt, list the input values seen in real
tool results and check each one matches exactly one row. Then check separately that each row's
spoken line asserts nothing its condition does not establish — a row reached by "I don't know why"
may not say why. A catch-all whose line makes a factual claim is a finding on sight, before any
call is examined.

**The enabling fact — the error name IS available to the model.** Raya puts
`__RAYA_TOOL_DEBUG__` in the tool result with a `response_body_excerpt` containing
`"error":"NAME"`. 67 of 73 observed apply failures name the error this way; the 6 that do not are
pre-2026-09-04 calls, before the debug block appeared. **This supersedes the 2026-09-01 finding
recorded around D52/D51 that "the model has never once received the error name" — it does now.**
Any branch that needed the error name is therefore reachable in prose, and an escalation asking the
platform to supply it is stale. Observed names: `ACTION_LIMIT_REACHED` (59),
`MINOR_ACTION_CHANNEL_BLOCKED` (5), `USER_NOT_FOUND` (2), `TARGET_ITEM_NOT_FOUND` (1).

**Fix direction.** Rung 3, remove the wrong option: add a row for "named error that is not the
duplicate case" whose line asserts ONLY that the action did not complete, and leave the cause claim
in the catch-all where it is true (timeout, no response). Do not add a prohibition telling the
model not to say "technical issue" — the line is right there in a row it is instructed to look up.

**Source.** KKB + Maya + KKB-Slim, 13 conversation prompts, 2026-09-09. `5a1c0c77` kkb-hi-signals
and `1715a207` kkb-kn-signals said the technical-issue line on `MINOR_ACTION_CHANNEL_BLOCKED`.
Related: D65, D78 (a line carrying a claim its guard does not cover).

---

## D81 — a prohibition that prints the forbidden output supplies it

**Symptom.** The bot speaks a stage direction aloud — `*(Silent tool call: apply_job with
profile_id: "5051" and job_id: "19e3da1f-…")*` — leaking internal ids to the caller, and then
speaks the success line **without having called the tool at all**. On `e4e81fe2` (kkb-kn-out, live,
2026-09-09) zero tools ran on the entire call and the caller was told "ಅಪ್ಲೈ ಆಗಿದೆ".

**Root cause.** The guard against it quoted the exact string. Both the rule ("Writing
`*(Silent tool call: apply_job)*` … applies nobody") and the evidence citation for call `29c4f152`
printed the literal form. The model reproduced the shape it had been shown. This is D50 with the
demonstration living inside the prohibition rather than inside a sample conversation — a negative
example is still an example.

**Detection heuristic.** Grep every prompt for the literal text of any output it forbids. If a
guard quotes the bad string verbatim, that is a finding on sight — no call needed. Then check the
transcripts for that same string in assistant turns. `fix_presence` row
`no-verbatim-stage-direction` holds the literal form out of all 21 prompts as a must-NOT-contain.

**Rung 0 count.** 7 calls across 5 bots spoke a stage direction (kkb-kn-signals 2/12, maya-hi-out
2/7, kkb-hi-in 1/22, kkb-kn-out 1/10, plus e4e81fe2). Two of them read the caller's phone number
aloud inside a `create_profile` stage direction. The prompt already documented four occurrences on
2026-09-03, so the guard had failed five times before this fix — volume was never the lever.

**Fix direction.** Delete the literal form and describe it instead. Do NOT add another prohibition
wording; per the escalation ladder, two failures of the same guard is the signal to change
mechanism. The remaining structural exposure is the samples themselves, which render 12-38 inline
`*( )*` stage directions each — moving those to a non-inline `INTERNAL:` form would remove the
imitable shape completely, but it is a 15-file reformat needing its own test cycle and sign-off.

**Source.** 12 KKB/Maya conversation prompts, 2026-09-09. Related: D50 (wrong output present in a
sample), D77 (bracket markers read aloud), D74.

---

## D85 — identical output across a CHANGED prompt means the source is not the prompt

**The single most useful diagnostic of 2026-09-09, learned the slow way after four wrong
diagnoses of one bug.**

DKB spoke "a role and a salary that were never supplied" on six consecutive calls, and the sentence
was **byte-identical every time** while the prompt was edited three times between them. Each edit
was a defensible hypothesis and each was wrong:

| attempt | hypothesis | outcome |
|---|---|---|
| 1 | worked example values printed beside the template (D83) | stripped them; output unchanged |
| 2 | no precedence rule saying the argument beats memory | added it at the point of use; output unchanged |
| 3 | the remembered value did not read as historical | date-stamped it in the memory prompt; output unchanged |
| 4 | my own evidence note quoted the bad sentence verbatim (D81b) | removed it; output unchanged |

The real source was `roles_posted` in the DKB **memory prompt** — "array of strings with timestamps
embedded (e.g. `["2026-04-22: Fitter, Nashik, 18K"]`)" — the exact analogue of KKB's
`last_options_presented`, whose identical fix had ALREADY been verified on `7bf46d06` hours
earlier.

**Detection heuristic, and use it early.** Before theorising about wording, ask: *did the output
change at all when the prompt changed?* If a prompt edit deployed and the spoken sentence is
character-for-character what it was, the sentence is not coming from the prompt. Stop editing prose
and enumerate the other channels: the memory prompt, the memory store, the tool descriptions, the
tool results, the arguments. A byte-identical repeat is a fingerprint of a fixed source.

**The corollary that would have saved all four attempts:** when a bug has an exact analogue on a
sibling bot that is already fixed, check whether the sibling's fix applies here FIRST. KKB and DKB
both had a memory field storing the thing just presented. One was fixed and verified; the other was
diagnosed four different ways.

**Source.** DKB, 2026-09-09. Related: D81, D81b, D83, and the KKB memory fix verified on `7bf46d06`.

## D81b — an EVIDENCE NOTE that quotes the bad output is the same trap as the prohibition

**This is D81 again, but the offender is the citation, not the rule — and it is the easiest one to
write by accident.** When a fix is recorded inside a prompt ("on live call X the bot said Y"), Y is
now printed in the prompt and is available to be reproduced.

**How it played out, 2026-09-09.** A note was added to the DKB posting template recording that the
bot had announced a fabricated posting, and it quoted the sentence verbatim. The bot then spoke that
sentence **character-for-character on five calls** — `714ebfc0`, `cc1b0ecc`, `965f9d06`, `dfaf30eb`,
`90bd2e80` — with `job_role: "Sales"` and `salary: "30000"` in the arguments and "Helper" and
"twelve thousand" coming out of its mouth.

Three fixes were attempted and all three failed, because none of them removed the quoted string:
1. strip the worked example values from beside the template
2. state at the template that the argument beats anything remembered
3. date-stamp the remembered value in the memory prompt so it reads as historical

Each was a reasonable hypothesis. All three were wrong, and the byte-identical output across three
different prompt states was the clue that should have been read sooner: **identical output across
changed prompts means the source did not change.**

**Detection heuristic.** Grep every prompt for quoted spoken text that sits inside an evidence note
— look for `on live call`, `on `+backtick-uuid, "announced", "said", "spoke" followed by a quoted
native-script sentence. Any such sentence is a template the model can fill. Record the failure by
DESCRIBING it ("announced a complete posting none of which had been supplied") and never by
reproducing it.

**Rule for this repo.** A prompt may name a call id. It may not quote what the bot wrongly said.

**Source.** DKB, 2026-09-09, self-inflicted while fixing D83. Related: D81, D83, D50.

## D82 — the point-of-use rule (the pattern behind nine of ten bugs found on 2026-09-08/09)

**This is a meta-pattern. Check it FIRST on any new report, before reading a single transcript.**

**Symptom.** A rule is present in the prompt, correctly worded, unambiguous — and the bot breaks it
anyway. The instinct is to call this "runtime adherence" and escalate. It usually is not.

**Root cause.** The rule is stated in its own section, far from the template that consumes the
value. A rule the model reads while composing the turn binds; a rule it read 700 lines earlier does
not. Nine separate bugs in one night were this, and in every case the fix was to restate the
existing rule at the line that uses the value — not to reword it, not to strengthen it.

| bug | rule lived | value spoken at |
|---|---|---|
| `${location}` read out with its pincode | its own Location section | the location-confirm sentence |
| `[company]` spoken in Latin | a conversion section | the job-list and deep-dive templates |
| bot invented a job board | 3 statements at the top of the slim rewrite (17 spread through the fat one) | the batch-list template |
| literal "/" spoken | a "## Slash ( / ) symbol" section | the job-list template |
| DKB recap in digits | the field-collection questions | a recap the bot COMPOSES, with no template at all |
| DKB `[job_role]` in Latin | nowhere — never stated | the posting template |
| Kannada failure line welded to the catch-all | two rows sharing an opening phrase | the row table itself |

**The mirror image — an example next to a template gets read as data.** Same night:
- the DKB posting line took "दो" and "बारह हज़ार" verbatim from the number rule printed directly
  beneath it, on a call where every job field was "Not Available" (`714ebfc0`)
- the KKB generic-trades illustration ("फिटर", "मशीन ऑपरेटर", "हेल्पर") became offerable jobs
- the prohibition on speaking stage directions printed the exact string the bot then spoke (D81)

**Detection heuristic — runs statically, no calls needed.** For every rule that constrains a spoken
value, find the template(s) that actually emit that value and ask whether the rule is stated inside
that block. If it is not, that is a finding, however well the rule is worded. Then, for every worked
example, ask whether it sits close enough to a template that the model could substitute it as data;
if so, either move it or mark it explicitly as an illustration.

**Fix direction.** Restate the rule at the point of use. Do NOT reword the distant rule and do NOT
add a third wording — see the escalation ladder. When writing the `fix_presence` row, assert the
rule is present **at the point of use**, not merely present in the file: several rows written before
this pattern was understood passed while the bug was live.

**Source.** KKB, Maya, DKB and KKB-Slim, 2026-09-08/09. Related: D50, D74, D77, D81.

---

## D83 — a concrete value printed beside a template becomes the output

**The sharpest version of D82, and it bit three times in one night.** D82 says a rule must be
stated at the point of use. This says the opposite about VALUES: a template block may state a rule
but must **never print a concrete example value**, because the model substitutes the example when
the real argument is absent — and sometimes even when it is not.

**Three occurrences, 2026-09-08/09, all on live calls:**

| what was printed beside the template | what the bot said |
|---|---|
| generic trades "फिटर / मशीन ऑपरेटर / हेल्पर" as an illustration of the local job market | offered them as real, applicable jobs |
| `VANS TRADING COMPANY` is "वैन्स ट्रेडिंग कंपनी" as a script-conversion example | greeted an owner as "वैन्स ट्रेडिंग कंपनी" with **no `company_name` supplied at all** (`bd60c6b0`) |
| `12000` is "बारह हज़ार" as a digits-to-words example | said "बारह हज़ार" when `salary` was **30000** (`cc1b0ecc`) |

The third is the instructive one: the fix that renamed the slot to carry the required FORM worked —
the bot said words, not digits — and the adjacent example then supplied the VALUE. Form and value
fail independently.

**Detection heuristic — static, no calls needed.** In any block that contains a spoken template,
grep for backticked literals and quoted native-script strings. A rule ("a five-digit monthly figure
becomes its Hindi words") is fine; a value (`12000` is "बारह हज़ार") is a finding. Keep the worked
examples, if they are needed at all, in a pronunciation/script section far from any template.
`fix_presence` row `no-concrete-values-beside-templates` holds the known literals out of all 21
prompts as must-NOT-contain.

**Fix direction.** Replace the value with a description of the transformation. Do not simply pick a
less realistic example — `bd60c6b0` shows any name-shaped string is substitutable, and an earlier
KKB call invented "एबीसी लॉजिस्टिक्स" from nothing when no example was available at all.

**Source.** DKB, KKB, Maya and slim — 18 prompts cleaned, 2026-09-09. Related: D50, D74, D81, D82.

---

## D84 — "say it in words" gets satisfied by re-rendering the digits in the target script

**Symptom.** A rule requires a number be spoken as words. The bot outputs the same number in
Devanagari or Kannada numerals — `११००४५`, `१२,००० से १६,०००` — which is not Latin digits, so it
looks like compliance, and is not words, so it is not.

**Twice in one night, on two different rules:**
- `1c6963bb` — the location rule said "drop every digit"; the bot spoke the pin code as "११००४५"
- `6e400995` — the salary rule said "arrive as DIGITS and are spoken as WORDS"; the bot spoke
  "सैलरी १२,००० से १६,०००" and "२ पोज़िशन", after that rule was already live

**Root cause.** "In words" and "not in digits" are read as a script instruction rather than a
spelling instruction, because everything else nearby IS a script instruction (convert Latin to
Devanagari, speak in the target script). The model applies the conversion it has been trained by
context to apply.

**Detection heuristic.** Grep spoken output for `[०-९]` and `[೦-೯]` runs of two or more, not just
`[0-9]`. A detector that only looks for ASCII digits reports clean while this is happening —
`grade_call.py`'s digit check had to be widened to all three numeral ranges before it caught it.

**Fix direction.** State that native-script numerals are still digits, at the rule: "'१२,०००' is NOT
a word — it is the same number in Devanagari numerals." Do not rely on "in words" alone. Same
correction as the pin-code rule needed ("DELETE every digit. Deleted, not rewritten").

**Source.** KKB, Maya and slim — 13 prompts, 2026-09-09. Related: D82, D83.

---

## D86 — a flag the prompt tells the model to IGNORE is a consent nobody checks

**Symptom.** A tool response carries state that a rule correctly says is *not* the readiness signal —
so the prompt says "ignore it" — and the state then goes unread for every other purpose too. On the
Signals seeker bots, `get_profile` returns `user_consent { terms_accepted, privacy_accepted, has_age }`
and a per-item `profile_consent_accepted`, and all seven prompts said, verbatim: *"Never treat
`user_consent: true` as 'the profile is live'"*. True, and the reason it was written. The consequence:
a returning caller whose `terms_accepted` or `privacy_accepted` is **false** — a profile created
outside the bot, by a portal, an import or a partner — was never asked for consent, because consent
was only ever asked on the path that CREATES a profile. The whole call then ran on a consent that had
never been given, and the recorded flag stayed false forever.

**Root cause.** "Do not use X to decide A" gets generalised to "X is noise". A field is mentioned in
the prompt exactly once, in a negative rule, so nothing ever routes on it. This is the mirror image
of D82 (point-of-use): the field has no point of use at all.

**Detection heuristic.** For every field the tool response actually returns, grep the prompt for its
name and classify each hit: does any hit make a DECISION, or are they all disclaimers? A field whose
only mentions are "never use this for…" / "note: this can be true while…" is an unread field —
report it and ask what SHOULD read it. Then ask the inverse question about every gate: *is this gate
reachable only on one path?* A consent gate that exists solely on the create path cannot serve a
caller who already has a record. Cheap grep: a consent/acceptance flag in the response with no
branch on it anywhere in the prompt.

**Fix direction.** Give the field a decision site of its own, as early as the data is available — for
KKB-Slim, a step 3.5 read immediately after the fetch, ahead of any other spoken turn. Keep the
original disclaimer (it is still right about readiness) and add the new use beside it, so the two
never get confused. **And check there is a WRITE path before promising the fix works:** asking for a
consent you cannot persist re-asks it on every future call. On Signals nothing could write consent
onto an existing profile (`update_profile`'s template has no `compliance`), which is why a separate
`record_consent` tool was needed — not compliance folded into `update_profile`, whose fixed template
would then assert a consent on every unrelated field write.

**Platform facts worth carrying (verified 2026-09-09):** an update POST (`item_id` present) carrying
`compliance` returns 200 and the `item_state` merge preserves every other field; a `compliance` value
of `false` is **rejected** — 400 `CONSENT_DECLINED`, *"consent cannot be declined — omit a key to skip
it"*. Consent is write-once-true, which also means **a false-flag fixture cannot be manufactured
through the API** — the false branch of any such gate is untestable without a provisioned record, so
say VERIFY-PENDING rather than claiming it works.

**Source.** KKB-Slim, 2026-09-09. Related: D82, D51.

---

## D87 — a reduction rule demonstrated only on single-token inputs teaches "keep the first one"

**Symptom.** A rule says to strip one KIND of content out of a written value (digits, punctuation, a
suffix) and speak the rest. The bot instead speaks only the FIRST surviving token and silently drops
the others. Live: `${location}` = `Muradnagar, Delhi 110098` was spoken as "मुराद नगर" — दिल्ली gone
(`591e5c28`); reported independently as "only the 1st word is being read" for
`Muradnagar, KHB colony, 110045`.

**Root cause.** The examples, not the rule (D83 again). Two of three table rows were single-place
inputs whose correct output happened to be one word (`Muradnagar, 110045` → मुराद नगर), so "one word
out" was the demonstrated pattern; the one multi-place row was the least like real campaign data. The
prose said "Locality and city only", which reads as a licence to pick.

**Detection heuristic.** For every conversion/reduction table in a prompt, count tokens in and out
per row. **If every row but one reduces to a single output token, the rule is undemonstrated for the
common case** — flag it. Cheap version: does the table contain at least one row where the output has
two or more kept tokens, in the exact shape the input variable actually arrives in? Also grep the
prose for "X and Y only" phrasing next to a list — an enumeration reads as a filter to pick from.

**Fix direction.** Make it a **count** rather than a description: every place word is spoken, in
order; digits are the only thing removed; count before speaking, and saying fewer than you were given
means you dropped one. Add an `in → out` column so each row asserts the count, and put the real
reported input shapes in the table. Dropping a datum is the same class of error as inventing one —
say so, since the prompt already forbids inventing.

**Source.** KKB-Slim, 2026-09-09. Related: D83, D50, D82.

---

## D88 — a step gated on "first call" is dead for every caller who has a profile

**Symptom.** A one-time data-capture turn labelled *FIRST call only* never happens. On KKB-Slim the
landmark turn was skipped on 11 of 11 live calls.

**Root cause (two, and they stack).** (1) The model has just fetched a profile, so "first call" reads
as *not this call* — and almost every caller has a profile, which makes the turn unreachable rather
than rare. The condition intended "the first time we capture this datum", which is not what the words
say. (2) The section framed skipping as the default ("asking is the EXCEPTION"), so any doubt resolved
to skip.

**Detection heuristic.** For every conditional turn, ask what fraction of callers satisfy the
condition **as the model will read it**, not as intended. A gate phrased on call ordinality
("first call", "new caller", "if this is their first time") that sits in a flow which fetches a
profile is suspect by construction. Then check the framing: if the section states the skip before the
ask, or calls the ask an exception, the skip is the default. Confirm with a count from live calls
(D52's rung 0): a `0/N` is unreachability, not flakiness.

**Fix direction.** Re-gate on the DATUM, never on the call ordinal: *do we already hold this value?*
Found → skip; not found → required. Make the skip need a positive reason ("a value you can point at")
and state the requirement before the exception. State explicitly that having fetched a profile says
nothing about whether the datum is on record.

**Caveat that must be checked before calling it a bug (bit us here):** when the platform injects its
own stored memory, a caller whose memory already holds the datum SHOULD be skipped — so a consistent
skip on a heavily-reused tester DID may be the rule working correctly. `${contact_memory}` in
`agent_args` does not reach the model (`/voice-test` → Fixtures), so the "nothing on record" state cannot be
fixtured; the discriminator is one call with `memory_enabled: false`, which is what proved the turn
reachable here. Do not report the branch fixed on the strength of that call — it proves reachability,
not that the re-gate changed anything in production.

**Source.** KKB-Slim, 2026-09-09. Related: D52, D51, D82.

---

## D89 — a spoken line that promises finality kills every turn after it

**Symptom.** A newly added turn never fires, and the turn immediately before it ends with a line that
promises the caller it is the last thing being asked. On KKB-Slim the landmark turn opens with
"आखिरी सवाल, फिर सीधे जॉब्स पर आती हूँ" — *last question, then straight to the jobs* — and the pin turn
placed after it did not run on either of two live calls (`d47db4c0`, and `b42779bf` for a different
reason). The model was keeping the promise the prompt made it make.

**Root cause.** The prohibition is in the SPOKEN text, not in the rules, so it is invisible to a reader
auditing the rule list — and it binds harder than a rule, because breaking it would make the bot
visibly contradict itself to the caller. A rules paragraph saying "then ask the pin" cannot win against
a sentence the bot has already said out loud.

**Detection heuristic.** Grep every mandated spoken line for finality and count markers — "आखिरी",
"ಕೊನೆ", "last question", "one more thing", "बस एक बात और", "then we're done", "two quick things" — and
check what the flow actually does after that turn. Any turn that follows a finality promise is
suspect. The same applies to a counted promise ("दो छोटी बातें") followed by three questions.

**Fix direction.** **Reorder so the promise stays true** — put the new turn BEFORE the one that claims
finality, and say in the prompt why that order exists, or the next edit will undo it. Rewording the
promise is second-best: it costs the turn-ending signal that made the caller wait. Never leave the
contradiction in place and hope the rule wins; the spoken sentence is the stronger instruction.
(Fixed by reordering to place → pin → landmark; verified on live call `9c9f7e34`, all three turns in
order.)

**Source.** KKB-Slim, 2026-09-10. Related: D82, D50.

---

## D90 — "the caller's identity is fixed by the dialled number" is worth re-testing before you call a state unfixturable

**Symptom.** A whole class of tests gets recorded as impossible — new-caller paths, draft profiles,
consent-flag states — on the strength of a documented platform limit. The limit was real for one
variable and got generalised to another.

**What actually happened.** `/voice-test` (Fixtures) had settled that `contact_memory` in `agent_args` never
reaches the model (true), and said `contact_phone` behaved "the same way" (false). On 2026-09-10 a
one-call probe showed `${contact_phone}` rendering exactly the fixture value and `get_profile` firing
against it, while the telephony leg still went to the tester DID. Every "cannot be fixtured" note that
depended on the caller's identity being pinned to the DID was wrong — including a same-session
escalation asking the data team to provision records.

**Detection heuristic.** When a test plan says a state is unfixturable, check whether that rests on a
platform claim about ONE input variable that was then extended to others. Cheapest possible probe: set
the variable in `agent_args`, place one call, and read the CALL CONTEXT line in the transcript plus the
tool arguments — those two facts settle it in four minutes. Do this before writing an escalation,
because an escalation asking for something you can do yourself costs the other team a round trip and
costs you the credibility of the next one.

**Fix direction.** Build the state through the API on a throwaway number on the instance the bot reads
from, point `contact_phone` at it, and keep the number in a reserved block that cannot belong to a real
person. Then write down, per variable, whether args win or the platform wins — the answer is not
uniform across variables, and assuming it is, is the actual bug.

**Source.** KKB-Slim, 2026-09-10. Related: D52 (count before you theorise), D51.

---

## D91 — `create_profile` on a caller who already has a record mints a duplicate instead of fixing it

**Symptom.** An existing caller whose profile is `draft`/unconsented is taken through the create path;
the API happily creates a SECOND profile, live, leaving the original behind. The participant now has two
live seeker profiles — the "duplicate live profile is a hard failure" state the prompt forbids
everywhere else. Seen on live call `e0e7bbc2`: `create_profile` returned two items, the stale draft
first and a new live one second.

**Root cause.** The create/update endpoint is the same POST; supplying an `item_id` updates, omitting it
creates. A flow that reaches for `create_profile` whenever the caller "is not applyable" omits the id
and therefore creates. The consent case makes this easy to hit, because a draft is not applyable and the
obvious repair looks like creation.

**Detection heuristic.** For every path that calls a create tool, ask what `get_profile` returned on
that same call. If it returned ANY item of that type, the correct action is an update against its
`item_id`, never a create. Also grep the prompt for `items[0]` in the create-response reading — a
response that carries a stale draft plus the new item will put the draft first, so `items[0]` hands the
wrong id to the next tool.

**Fix direction.** Give the flow a tool that updates the existing item — for consent, a `record_consent`
that POSTs the `item_id` plus the compliance array. Verified on the API: sending the consent array
against a **draft** item both records the consent and turns that item **live**, so the caller becomes
applyable with no second profile (call `f796df13` did exactly this: tools were `get_profile`,
`record_consent`, `apply_job` — no create, one profile). Reserve the create tool for a genuinely empty
fetch, and make the create-response rule say "the item whose `lifecycle_status` is live", never
`items[0]`.

**Source.** KKB-Slim, 2026-09-10. Related: D86, D51.

---

## D92 — a digit-by-digit spoken number loses a repeated digit unless the count is asserted

**Symptom.** A number the bot must speak one digit at a time comes out one word short, and the missing
word is always a repeat. Live: the Kannada slim read the pin `580023` as "ಐದು, ಎಂಟು, ಸೊನ್ನೆ, ಎರಡು,
ಮೂರು" — five words for six digits, one of the two zeros swallowed (`5e3d8c69`). Correct on the two
neighbouring calls, so it reads as flakiness and is not: it is a missing invariant.

**Why it matters more than it looks.** The bot then asks the caller to CONFIRM what it just said. The
caller hears a plausible number, says yes, and a wrong pin is stored with a human's agreement attached
to it. A value read back wrong is worse than one never asked for.

**Detection heuristic.** For every spoken-digit-sequence rule (pin, phone, OTP, account number),
grep the prompt for a **count** assertion next to the template. If the rule only says "digit by
digit", it is unprotected. In transcripts, count the comma-separated number words against the source
value's digit count — a mismatch of exactly one, on a value containing a repeated digit, is this bug.

**Fix direction.** Assert the count at the point of use, with the repeat named: "a pin is exactly SIX
digit-words, one per digit — six digits in, six words out, both zeros said. About to say five or
seven? You mis-split it; read it off the source again." The same count mechanism fixed the dropped
place-word in D87 — count-based checks are answerable from the turn being composed, which is why they
hold where "carefully" does not.

**Source.** KKB-Slim Kannada, 2026-09-10. Related: D87, D84, D82.

---

## D93 — an empty tool result gets answered with the nearest "we have nothing" line

**Symptom.** A caller with a perfectly good job list is told there is nothing for them and the call is
closed. Live call `fd01b717`: `${recommendations}` held three real jobs, `get_profile` came back empty
(a genuinely new caller), and the bot spoke step 0's missing-inventory line — "अभी आपके लिए मुझे जॉब्स
नहीं मिल रहीं — एक बार फिर से देखकर मैं आपको वापस कॉल करती हूँ" — then went to graceful exit. The
single most common state on a growth campaign (nobody has a record yet) produced a dead-end call.

**Root cause.** Two different emptinesses, one salient script. The prompt had a strong, quotable line
for "the job array is empty" and only a quiet prose branch for "the profile fetch is empty". When the
model needs a sentence for an unexpected empty result, it reaches for the one that exists. Nothing in
the no-jobs step said what it was NOT about.

**Detection heuristic.** List every "we have nothing / cannot help" line in the prompt and, for each,
check it names the ONE condition that licenses it and explicitly excludes the others. Then list every
tool that can return empty and confirm each has its own branch with its own next action. A bot with
two empty-able tools and one no-content line is one bug waiting. Cheap transcript check: any call where
a no-content line was spoken while the input array was non-empty.

**Fix direction.** Scope the line to its own trigger by name ("counts `${recommendations}`, the job
array, and nothing else"), add the negative ("an empty `get_profile` is NOT this case — it means the
caller is new, which says nothing about what jobs we hold"), and make it expire: if the array had
entries when you counted, the line is false for the rest of the call whatever a later tool returns.
Then give the other empty branch an explicit "this is not a reason to close" with its next step.
Verified fixed on `b91340a8`: empty fetch → pool overview → three location turns → all three jobs
presented → consent → apply.

**Source.** KKB-Slim, 2026-09-10. Related: D86, D82, D50.

---

## D94 — a shortening rule for one object gets applied to a different object whose value matches the example

**Symptom.** A value that must be spoken in full comes out shortened, and the shortening exactly
matches an example printed elsewhere in the prompt for a DIFFERENT field. Live call `6ff40ebb`:
`${location}` was `Keshwapur, Hubballi, 580023` and the bot said only "ಕೇಶ್ವಾಪುರ" — because the
canonical-spellings section carried *"a job's location: speak the locality and drop the repeated city
(ಕೇಶ್ವಾಪುರ, not ಕೇಶ್ವಾಪುರ, ಹುಬ್ಬಳ್ಳಿ)"*, the very pair the caller's own location arrived as.

**Root cause.** The rule was correctly scoped in words ("a job's `location`") and incorrectly scoped
by its example. An example is matched on the VALUE, not on the field name, so a rule about field A
fires on field B whenever B's value looks like A's example. This defeats an otherwise-correct
count rule elsewhere in the prompt (here Turn A's "every place word is spoken").

**Detection heuristic.** Collect every transformation example in the prompt and check whether its
input string could plausibly be the value of a DIFFERENT field. Highest risk: two fields of the same
type (a caller's place vs a job's place, a caller's phone vs an employer's phone) where one is spoken
in full and the other abbreviated. Also flag any pair of rules where one says "keep all of X" and
another says "drop part of Y" and X and Y share a format.

**Fix direction.** Change the EXAMPLE so it cannot collide (use a locality/city pair that never
appears as caller input), and add the exclusion to the shortening rule in the same breath: "this
applies ONLY to a job's own location, NEVER to `${location}`, which keeps every place word — that
count rule wins here." Fixing only the prose leaves the colliding example doing the damage (D50).

**Source.** KKB-Slim Kannada + Hindi, 2026-09-10. Related: D50, D83, D87.

---

## D89 — an upstream field RENAME silently inverts a flag-driven gate

**Symptom.** A gate that reads a boolean out of a tool response starts firing for everybody (or for
nobody) with no prompt edit behind it. On 2026-09-22 `get_profile` stopped returning
`user_consent: {terms_accepted, privacy_accepted, has_age}` and started returning
`compliance: [{key:"user_terms",value:…},{key:"user_privacy",value:…},{key:"has_age",value:…}]`. The
consent gate read `user_consent.terms_accepted`; its own rule — correctly — treats a missing flag as
"not given", so from that moment **every caller with a profile was read the full terms disclosure
again**, including people who had consented days earlier.

**Root cause.** The safe default on a missing field ("absent = not consented") is right for safety and
wrong for a rename: absence caused by a renamed key is indistinguishable, to the prompt, from absence
caused by a user who never consented. Nothing in the prompt is wrong; the contract moved.

**Detection heuristic.** For every field a prompt BRANCHES on, assert the field's presence against a
live response — not just its value. A one-line probe per gate (`print(json.dumps(list(resp.keys())))`
plus the specific key) catches a rename the same day. Two cheap standing checks:
(1) a fixture whose flags are known-TRUE must produce a call with NO consent line — if that call
starts asking, the field moved; (2) log the raw top-level keys of each tool response in the daily
regression and diff them against the last run. **A gate whose "all clear" branch has not been
exercised recently is a gate that can silently invert.**

**Fix direction.** Read the new shape, keep the old name as a documented fallback, and say explicitly
what an absent key means. Where the response is a LIST of `{key, value}` rows rather than an object,
say "find the row whose `key` is X and read its `value`; an absent key counts as false" — the model
handles that reliably (verified on `ab98be47` and `8ae650f2`, both branches). Then tell the platform
team: ask for a deprecation window where both keys ship, because a renamed field here changes what
citizens hear on a live call.

**Source.** KKB-Slim (both languages), 2026-09-23. Related: D52, D86.

---

## D90 — a redirected log that looks empty is buffering, not a dead process

**Symptom.** A test run's log file is 0 bytes minutes in, or shows only early "Pending" polls, so the
run is declared hung/failed — when it is actually running fine and completes normally.

**What it cost.** On 2026-09-23 two harness calls were read as "nothing connects" off an unflushed
log; the conclusion was reported to the owner as a blocked harness, and a **shared DID belonging to
another team's bot was reassigned** to work around a problem that did not exist. The calls
(`8ae650f2`, `ab98be47`) had completed — 248s and 254s, 41 and 39 turns — and carried exactly the
evidence being chased.

**Root cause.** Python block-buffers stdout when it is a file rather than a tty, so `tail` shows a
stale or empty file. Nothing in the pipeline is broken; the writes are sitting in a 4-8KB buffer.

**Detection heuristic.** Never infer a run's state from its redirected log alone. **Ask the
authoritative source** — for a Raya call that is `GET /api/call?agent_id=…`, which shows
`outcome`/`dur`/`turns` regardless of any log. Treat "log is empty AND the process is alive" as
"buffered", not "hung": `ps` showing the process plus a 0-byte log is the signature. And when a
conclusion from a log would trigger an expensive or shared-resource action, verify it against the API
first — that is the moment the check is worth most.

**Fix direction.** `sys.stdout.reconfigure(line_buffering=True)` at import time in any script whose
output gets redirected (done in `scripts/raya_testrun.py`), or run it with `python3 -u`.

**Source.** Prompt Tuner harness, 2026-09-23. Related: D52 (count before you conclude).

---

## D91 — a REQUIRED tool parameter can be asserted falsely; it constrains what the model SAYS, not what it DID

**Symptom.** A precondition is moved into the tool schema as a required enum (D-ladder rung 4, the
`duplicate_check` pattern), and the model fills it in with the compliant value while the precondition
is plainly unmet in the same transcript.

**The case.** `record_consent` writes a caller's acceptance of the platform terms. On Maya Inbound the
five-element disclosure was never spoken, the caller was asked only "क्या मैं अभी इस जॉब के लिए आपकी
तरफ़ से अप्लाई कर दूँ?", and the tool fired anyway — a consent record for terms the caller never heard
(`9df94781`). A required `terms_check` enum was added, whose compliant value is
`disclosure-read-and-agreed-this-call`. On the retest the disclosure was **again** never spoken and the
model sent **`terms_check: "disclosure-read-and-agreed-this-call"`** (`bdae75d6`). 2/2 fabricated.

**Root cause.** `duplicate_check` works because the model can verify its value against something in
front of it — its own call history this turn. A parameter that asks "did you perform action X earlier"
is a **self-report about a turn the model did not take**, and the compliant value is the one the
surrounding prose says it should be able to give. The schema makes the claim mandatory, not true.

**Detection heuristic.** For any assertion parameter, ask: **is the fact checkable from the turn being
composed, or is it a memory of an earlier turn?** Only the first kind holds. Then verify it the only
way that counts — grep the transcript for the thing the parameter claims happened, and compare against
the argument the model sent. A regression detector should treat
`terms_check == "disclosure-read-..."` **AND** no disclosure text in the transcript as a hard failure,
because that combination is exactly a laundered fabrication.

**Fix direction, in order.** (1) **Remove the capability, don't forbid its misuse** — with
`record_consent` off the agent, a skipped disclosure records nothing (the pre-feature status quo)
instead of writing a false consent. Verified safe on `7c24f130`: no consent written, and no duplicate
profile either. (2) **Then fix the reason the step was skipped.** Here it was the router: the prompt's
DECISIVE ROUTER numbered its turns and sent the model to the named branch headings, and the consent
gate sat *between* the router and those headings — so the route passed over a section that was never
entered. Making it **step 3 of the router itself** is what got the disclosure spoken, in its own turn
(`7c24f130`). A section the route does not name is a section the model can skip, however emphatic its
own prose.

**Source.** Maya Inbound, 2026-09-23. Related: D88 (a gate the route never reaches), D82.

## D95 — a skip test that accepts a WEAKER fact than the one it is guarding

**Symptom.** A turn that is supposed to capture something is skipped about half the time, while the
prose demanding it is already as forceful as prose gets — "FOUND NONE → YOU MUST ASK", "a returning
caller is not an exemption", "presenting jobs having neither found one nor asked for one is a miss".
On kkb-hi-signals-slim, 2026-09-23, the landmark turn ran on **6 of 16** live calls that reached the
location block with no landmark on record. Reported from UAT as "nearby landmark is not being asked".

**Root cause — not disobedience.** The model was obeying the rule and answering its test wrongly.
Turn C's skip test said *"the skip needs a positive reason — a landmark you can actually point at in
the context"*, and twenty lines later the same section said the captured landmark *"is persisted in
step 12 as `location` = '<landmark or locality>, <City>, <State>, India'"*. Read together those say
**the landmark lives in `location`** — so an injected `${location}` of `Muradnagar, 110045`, which
Turn A had just read aloud, was a landmark the model could point at. FOUND ONE → SKIP, and the
FOUND NONE branch was unreachable on exactly the calls that needed it.

**The split that proves it.** Group the calls by whether the weaker fact was present:

| `${location}` | landmark asked |
|---|---|
| area **+** pin (`Muradnagar, 110045`) | **2 / 12** |
| absent, or an area with no pin | **5 / 6** |

A clean split like that is the signature. It is not an adherence curve; it is a test firing correctly
on the wrong input.

**Detection heuristic.** For every skip/guard condition in a prompt, ask **what is the weakest value
that would satisfy it as written** — then check whether that value is routinely present in the input
variables or a tool result. Two specific smells: (1) the guarded field is *also* named as the
destination the captured value is written to, so the storage slot doubles as the evidence slot;
(2) the condition is phrased by vibe ("point at", "hold", "have", "on record") rather than by type.
Both let locality-level data satisfy a landmark-level test. Grep for a field name appearing in the
same section as both "skip if" and "persisted as".

**Fix direction.** Fix the *test*, not the volume of the rule.
1. **Name the weaker fact and exclude it by name** — "`${location}` is not a landmark source; a town,
   locality, city, district, state or PIN read out of it is not a landmark, however specific it
   looks", with the real example spelled out.
2. **Define the stronger fact by type** — "a landmark is a NAMED POINT a person can stand at: a bus
   stop, a station, a market, a school, a hospital, a temple, a mall, a factory gate. An
   administrative place name is an AREA, not a point."
3. **Make the write one-way** — "`location` is where a landmark GOES, never where one is read FROM",
   which closes the loop that created the ambiguity.

**Do NOT reach for these first.** Two other fixes were tried on this bug and both failed:
- **More prose.** The guard had already been sharpened twice. Sharpening a rule the model is already
  obeying cannot help (D25, D47, D49, D50).
- **A required tool parameter.** `caller_pin_code` and `caller_landmark` were made required on the
  job tools. On `6ae79885` the model filled `caller_landmark: "not-known"` without asking and called
  the tool *before* the turns it was meant to gate — the skip arrived carrying a parameter denying it
  had happened. That is D91: a required parameter constrains what the model SAYS, not what it DID. A
  parameter only enforces when the model cannot produce a plausible value without doing the work
  (`profile_id` qualifies, a landmark never will). Reverted the same night.

**Source.** KKB Slim Hindi + Kannada, 2026-09-23. Related: D91 (false assertion in a required param),
D96 (a pre-close checklist naming one owed item), D50 (a demonstration becomes the output).

**The same pattern, written into a TOOL's trigger — same day, same author.** A new `save_location` tool
was described as *"call it right after the location questions are finished (area confirmed, pin
confirmed or asked, landmark asked or skipped)"*. Every clause of that was satisfiable before a single
question was asked: `${location}` already held an area and a pin, so "confirmed" read as "held", and
"or skipped" discharged the landmark. On `28f4cf52` the bot saved and fetched straight from the role
turn and **all three location questions vanished** — a worse regression than the bug being fixed. A
tool's trigger condition is a guard like any other, and it is read at the moment of use, so it
outranks the prompt's own ordering. **Apply this check to every tool description that says "after X"
or "once Y is done"**: can the model satisfy X or Y from data already in context, without the event
having happened? If yes, name the event in the caller's terms ("after the caller has ANSWERED…") and
exclude the context value by name. Never write "(or skipped)" without listing the skip reasons.

## D96 — a pre-close checklist that names ONE owed item silently excuses every other owed item

**Symptom.** Step 13 says the services offer fires "on EVERY call where the caller engaged, however
the job part ended — applied (succeeded or failed) … 'They did not apply' is never a reason to skip."
It fires reliably after a successful apply (`45490ef6`, `511171cf`, `28704be3`, `d70126e8`) and never
after a failed one: `c883aa34` and `670cbb12` both went from the apply-failure line straight to
Goodbye with `services_pitched: No`.

**Root cause.** Two competing instructions, both nearer the decision than step 13 was. (1) The failure
branch read "**On FAILURE the turn ends on the offer of another job and NOTHING follows it** — no
service-provider pitch, no wrap-up, no goodbye" — scoped to *the turn* by intent, read as scoped to
*the path*. (2) The second-failure line ended "Then Graceful Exit", routing failure past step 13
explicitly. And the exit step's own pre-close checklist asked exactly one question — "has the Need
Capture offer been made?" — which **implies the list is complete**: an owed item absent from the
checklist is an item the exit does not believe it owes.

**Detection heuristic.** Find every pre-close / pre-exit checklist and enumerate what it checks.
Any step elsewhere in the prompt that claims to be owed "on every call" but is NOT an item in that
checklist is a latent skip — flag it. Separately, grep the prompt for `NOTHING follows`, `nothing
else`, `Then Graceful Exit` and similar terminal phrases and ask, for each, whether it is scoped to a
turn or to a path; if a turn, it must say "in this turn".

**Fix direction.** Scope the prohibition to the turn *and say where the item is still owed* ("no
service-provider pitch **in this turn** … it is still owed, at step 13"); replace the bypassing route
("Then Graceful Exit") with the full route ("Then step 13, then Graceful Exit"); and **add the item to
the exit checklist**, where the decision is actually taken, rather than restating the rule in its own
section a third time.

**Source.** KKB Slim Hindi, 2026-09-23. Related: D91/D88 (a section the route never names),
D89 (a line promising finality kills the turns after it).

## D97 — a prohibition scoped to one KIND of thing silently permits every other kind

**Symptom.** A rule says a turn must stand alone, and the bot merges something into it anyway. Step 13
of KKB Slim read *"Never in the same turn as another **question**."* On `d4dd4668` the bot said the
no-match line and the services lead-in in one breath — *"अभी आपके लिए मुझे जॉब्स नहीं मिल रहीं — एक
बार फिर से देखकर मैं आपको वापस कॉल करती हूँ। जॉब्स के अलावा हमारे पास कुछ और मदद भी है…"*

**Root cause.** The bot did not break the rule. **The no-match line is a statement, not a question,**
so the prohibition as written did not cover it. A guard phrased against one category leaves every
other category permitted, and the model will find the gap — not maliciously, but because the gap is
genuinely there.

This is the same family as D95 (a skip test accepting a weaker fact) seen from the other side: D95 is
a permission that is too broad, D97 is a prohibition that is too narrow. Both are fixed by reading the
condition and asking what it actually ranges over, never by saying it louder.

**A second smell found in the same rule.** The clause also still said the offer could be *"folded into
the success turn per step 11"* — which step 11 had been changed to forbid outright the night before.
**A rule that cross-references another section is stale the moment that section changes.** When you
fix a positional rule, grep the prompt for references to the position you just changed.

**Detection heuristic.** For every prohibition, name the category it ranges over — "another question",
"a tool call", "a second job", "a stage direction" — then ask **what else could occupy that slot that
the category does not name.** A statement, a hold phrase, a wrap-up, a lead-in, an apology. If the
answer is "quite a lot", the guard is scoped too narrowly. Then grep for cross-references (`per step
N`, `see section X`) and check each still says what it is quoted as saying. Counting helps but will
not find this on its own: the ratio here was **1/3**, small and mixed, and the cause was still fully
determined by the text.

**Fix direction.** Widen the category to cover the slot, not the volume of the rule: *"Nothing else
may share that turn — not another question, and not a statement either"*, with the specific case
named so it cannot be read past. Then put a pointer at the **point of composition** — beside the
no-match line itself, where that turn is actually written — saying the line ends its turn. The rule
states the constraint; the pointer catches it where the sentence is built (the same placement that
fixed the `'Any'` leak).

**Source.** KKB Slim Hindi + Kannada, 2026-09-23. Related: D95 (permission too broad), D50 (fix it at
the point of composition), D89 (a line that promises finality kills the turns after it).

## D98 — an unfilled promise with no MANDATORY escape gets filled with invention

**Symptom — the worst failure class this fleet has.** Given no `${recommendations}` array, KKB Slim
Kannada invented two jobs, with company names, salaries, qualifications and position counts, then
invented a job UUID and called `apply_job` with it. Reproduced **2/2** with *different* fabricated
companies each time (`ABC Solutions` / `Global Tech`, then `Global Solutions` / `Tech Solutions`), so
it is generative, not a stale cached list. Calls `24e5dabd` and `7fa799eb`. Both applies were rejected
`422` by the backend — **that rejection is the only thing that prevented a real write** — after which
the bot told the caller their interest was noted and the team would update them. The caller hangs up
believing they applied to a job that does not exist.

**Root cause — NOT missing guards.** The prompt carries **seven** separate "never invent a job"
prohibitions, the same number as its Hindi twin, which does not do this. Volume was never the issue.
Three things combine:

1. **The greeting has already promised jobs** — *"I'm calling to tell you about some good jobs in your
   area"* — before anything knows whether any exist. The obligation is created first.
2. **There is no tool, so the absence is SILENT.** The Hindi twin fetches through `get_jobs` /
   `get_recommended_jobs`, so "nothing" arrives as an empty tool result the model must react to. On the
   injected-array design, a missing array is simply nothing at all — no event, no result, no signal.
3. **The escape line is guarded against USE, not mandated.** The rule reads *"Count the valid entries
   first: more than zero and you may NOT say this line."* That forbids a FALSE no-match. **Nothing
   anywhere makes the no-match line obligatory when the count is zero**, and nothing forbids naming a
   job when there is no array to name one from. So the model has a promise to keep, no permitted way
   to say "there are none", and a blank where the inventory should be.

**Detection heuristic.** For every "do not invent X" rule, find the path where X is legitimately
absent and ask: **is the honest alternative MANDATORY and terminal there, or merely permitted?** A
prohibition without a compulsory escape is an instruction to improvise. Two specific checks: (a) does
an earlier line promise the thing before its availability is known; (b) does absence arrive as an
observable event (an empty tool result) or as silence (a variable that simply is not there). Silence
plus a promise is the dangerous combination. Also grep for guards phrased "you may NOT say this line"
— they protect against the false positive and usually leave the false negative wide open.

**Fix direction.** Do NOT add an eighth prohibition (D25, D47, D49, D50). Make the zero path
mandatory, terminal and checkable: zero valid entries → the no-match line is the ONLY permitted next
utterance, no job may be named for the rest of the call, and `apply_job` is forbidden. Better still,
remove the wrong option: a job may only be named if its `job_id` can be quoted from the array, which
makes invention impossible rather than forbidden — the model cannot produce an id it never read.
Consider also moving the greeting's promise behind the count.

**Fleet exposure.** Every bot on the injected-array design shares condition (2) and (3). The non-slim
Signals prompts (`KKB Placeholder Hindi/Kannada Signals`) carry only **2** never-invent guards against
slim's 7, on the same design — so they are less protected, not more. Assume exposure until each is
tested with an empty array.

**Source.** KKB Slim Kannada, 2026-09-23. Related: D95 (permission too broad), D97 (prohibition too
narrow), D50 (louder wording is not a mechanism).

## D99 — a tool description that states an OPERATION instead of a TARGET FORMAT, on an input whose shape varies

**Symptom — silent data corruption.** On `482ea2e2` (KKB Slim Hindi, outbound) `update_profile` was
sent `phone: "91918888888790"` — the country code doubled. The participant endpoint finds-or-creates
by phone, so the wrong number was not found and **a phantom user was created in production**
(`b2683040`, response `user_existed: False`). The next write in the same call reused that phone
against the real caller's profile and failed `403` on the ownership mismatch. Nothing was spoken
about any of it; the caller heard a normal call.

**Root cause — two instructions, each correct for one input shape.** `${contact_phone}` arrives as
**12 digits** on outbound (`918888888790`) and **10 digits** on inbound (`1204404272`). The tool
parameter description said *"= 91 + the 10-digit ${contact_phone}"* — an OPERATION, correct inbound,
wrong outbound. The prompt said *"12-digit 91-prefixed, never prepend another 91"* — correct outbound,
wrong inbound. Tool descriptions are read at the moment of use, so on the outbound calls where the
model followed the schema over the prose, it doubled. **D1: 2 of 20 writes; D2: both on one outbound
call.** It stayed rare only because the model usually followed the prompt.

**The tell was already in the same agent.** `get_profile` never doubled, in either direction. Its
description states the **target format** — *"with the 91 country-code prefix and NO plus sign, e.g.
919876543210"* — so the model normalises from whichever shape arrives. An operation ("91 + X") is
only right for one shape of X; a target format is right for all of them.

**How it hid.** This is residue of an earlier fix (CD6, 2026-08-01) that corrected the PROMPT text and
left the TOOL descriptions saying "91 +". The fix was declared resolved and recorded as resolved. A
fix that edits one of two sources of the same rule is half a fix, and the half left behind is the
stickier one.

**Detection heuristic.** Grep every tool parameter description for arithmetic on an input variable —
`"= 91 +"`, `"prefix with"`, `"prepend"`, `"add the"`, `"append"`. For each, ask **whether that
variable's shape is the same in every direction/campaign/language** — check a real inbound and a real
outbound call's CALL CONTEXT. If the shape varies, the operation is wrong somewhere. Then diff the
tool description against the prompt's own description of the same value: any disagreement is a live
competing instruction, and the tool side wins at the moment of use. Also flag any write endpoint
documented as find-or-create by an identifier the model constructs — a malformed id there does not
fail, it creates.

**Fix direction.** Describe the target, not the transformation: *"12 digits beginning with 91 — send
it unchanged if it already is; if it is 10 digits, put 91 in front. A number starting 9191 is always
wrong."* Anchor to a value the model has already produced correctly (*"the SAME value you sent to
get_profile"*). Then bring the prompt's own wording into line so no two sources disagree. When
closing out such a bug, grep **every** place the rule is stated — prompt, each tool description, each
agent that shares the tool — before calling it resolved.

**Source.** KKB Slim Hindi, 2026-09-23. Fleet exposure at time of writing: 8 Signals agents × 3 tools.
Related: D91 (a required parameter constrains what the model says), D98 (silence vs observable
absence), CD6 (the earlier half-fix).

## D100 — a slot defined by the TURN that filled it goes stale when the caller updates the value later

**Symptom.** Mid-call, a caller said *"मैं अब मोदीनगर में रहता हूँ, मोदीनगर बस स्टैंड के पास"* ("I now
live in Modinagar"). Later the bot read their details back — *"…एरिया मुराद नगर — सब सही?"* — the old
place. They said yes, and the old place became the recorded one (`a8281e55`). On a call where no
read-back happened (`6c12ef52`) the move survived, which is the whole difference between the two.

**Root cause.** The read-back's area slot was defined as *"the landmark turn's stop, station or
landmark"*. A slot defined by WHICH TURN filled it keeps that turn's answer for the rest of the call, so
any later correction is invisible to it. Nothing told the bot a later statement supersedes an earlier
one. The same shape defeated the output prompt's `nearest_landmark` twice: its first line anchored it to
"the Location step's answer", and an appended "their FINAL answer" paragraph lost to it both times.

**Detection heuristic.** Grep for slots or fields defined by a turn or step — "the X turn's answer",
"as settled at step N", "what they said at the location step". For each, ask whether the caller can
legitimately CHANGE that value later in the call (location, role, availability, a preference). If they
can, the definition must say the latest statement wins — in the definition's own first clause, not in a
paragraph appended after it.

**Fix direction.** Define the slot by recency: *"the LATEST thing the caller told you about where they
live — normally the landmark turn's answer, but if they later said they moved, that new place"*. Add one
general rule that a later statement supersedes an earlier one for the rest of the call, and have the bot
acknowledge it briefly without re-running the questions. Verified: on `ff922409` the bot said *"मैं समझ
गई कि आप अब मोदीनगर में रहते हैं"* and the recorded area was Modinagar. **Where prose does not bind**
(the output prompt's `nearest_landmark`, 0/3 on move calls after two edits), enforce it in code: the
post-call writer drops a landmark that names the caller's old area when their final area differs.

**Source.** KKB Slim Hindi, 2026-09-23. Related: D95 (a test that accepts a weaker fact), D50.

## D101 — a validation rule whose remedy assumes the input is well-formed, or ends in "accept whatever comes"

**Symptom.** A production UAT call (`04365ced`, KKB Slim Hindi) carried `${location}` = `Delhi, 11024` —
five digits, a data typo. The bot read it back as a pin, *"एक, एक, शून्य, दो, चार"*, five digit-words,
and the caller agreed. The prompt already said, two lines up, *"A 5-digit or other malformed run is NOT
a pin: treat it as absent and ask."*

**Root cause — two escape hatches, each defeating the rule.**
1. **A remedy that assumes good input.** The digit-count guard said *"If you are about to say five or
   seven, you have mis-split the number: read it off `${location}` again digit by digit."* That is the
   right remedy when the input has six digits and the model dropped one. When the input genuinely has
   five, re-reading yields five again, the rule has no next step, and the model speaks what it has. The
   remedy turned "this is not a pin" into "this is a pin I mis-read" — a competing instruction (rung 2).
2. **A validation that ends in acceptance.** For a pin the CALLER gives, the rule was *"if what you heard
   is not 6 digits, say so once … and then accept whatever comes."* So a wrong-length pin was rejected
   once and accepted the second time. A validation with an unconditional accept at the end is not a
   validation.

**Detection heuristic.** For every format or length check, find its failure branch and follow it to
the end. (a) Does the remedy assume the input is well-formed ("you mis-read", "read it again")? Then ask
what happens when the INPUT is the problem — if re-applying the remedy returns the same bad value, the
branch has no exit. (b) Does any branch end in "accept whatever comes", "use what they said", or
"move on with it"? That is an unconditional accept, and the check is decorative.

**Fix direction.** Decide validity FIRST, by count, before any read-back: exactly six → confirm; anything
else → it is not a pin, never read it back, ask with a dedicated line. Make the remedy branch on the
input ("if it really has six, you mis-split; if it does not, it was never a pin"). Replace the
unconditional accept with a terminal reject: ask once to check and repeat; still wrong → no read-back,
nothing confirmed, treated as not known. State the invariant once, plainly: *a pin that is not exactly
six digits is never read back, never confirmed and never saved.* The output prompt already recorded
`pin_code` as NA for non-six-digit values, so the stored record was safe — the damage was a caller
agreeing, out loud, to a wrong number.

**Source.** KKB Slim Hindi + Kannada, 2026-09-23 (Khushboo's UAT call). Related: D95, D97, D99.

## D102 — a branch that is never demonstrated is never taken, and the demonstrated branch's VALUES get reused as fabrications

**Symptom — the bot invents caller data.** KKB Slim's Turn B has two branches: confirm the pin when
`${location}` holds one, ask for it when it does not. Across 41 live calls the ASK branch fired **0
times**. On every call whose `${location}` carried no pin, the bot read one back anyway — and it was
always **110045**, the pin used in the prompt's worked examples: `2027e477` (inbound, `${location}`
absent), `d9111476` and `ff13bfaa` (`${location}` = `Muradnagar`, the last on a never-registered number
with no memory, which rules out any stored value). A caller hearing "आपका पिन कोड एक, एक, शून्य, शून्य,
चार, पाँच है — सही?" may well say हाँ to a number that was never theirs.

**Root cause.** Both worked calls demonstrated the CONFIRM branch with the same concrete pin, word for
word; the ASK line appeared once, in rule prose, and in no worked call. The model performs the Turn B
it has seen performed. With no pin in the input it does not switch branches — it fills the familiar
template with the familiar digits. D50 applied to a VALUE, not a phrase: a concrete example value is
itself a demonstration, and it is what fills the slot when the real value is missing.

**How it hid.** The grader scored "a pin was read back" as a pass. On calls whose input had a pin that
was correct; on calls whose input had none it was a fabrication, counted as success. **A pass condition
must compare against the input, not just check that the behaviour occurred** — "read back the pin" and
"read back THE INPUT'S pin" are different checks, and only the second one catches this.

**Detection heuristic.** (1) For every multi-branch step, check that EACH branch is demonstrated in at
least one worked example — a branch only described in rule prose is suspect, and one never demonstrated
is likely unreachable. Run D1 on it: count how often it has ever fired. (2) Grep every concrete example
value used in a demonstration (pins, phone numbers, names, ids, amounts) against real transcripts from
calls whose input LACKED that field. A demo value appearing there is a fabrication. (3) Distrust a demo
value repeated across examples — 110045 appeared 12 times.

**Fix direction.** Demonstrate every branch: one worked call per branch, with the INPUT shown and the
branch chosen because of it. Add a compact side-by-side table of input → decision for the step (not a
read-back to copy — use a separator like ` · ` so the split cannot be spoken verbatim). Vary the example
values so no single one dominates, and state that a value may only be read back if it came out of THIS
call's input. When grading, assert against the input.

**Source.** KKB Slim Hindi + Kannada, 2026-09-23. Related: D50, D101, D95.

## D103 — a mandated disclosure that lives in ONE turn is lost on every exit reachable before that turn

**Symptom.** A neighbour answered the demo bot's audio check with *"मैं पड़ोसन बोल रही हूँ, घर वाले
बाज़ार गए हैं। क्या बात है?"*. The bot correctly kept the child's absence private — and closed without
ever saying who was calling, that it is a computer voice, or that the call may be recorded. 0 of 2
calls on that path carried the disclosure (`27808754`, `ed1014fe`); every call that reached Turn 2 did.

**Root cause.** The AI + recording disclosure was written into Turn 2 only. The proxy branch was
defined as "close politely", and it was reachable from the Turn 1 reply — before Turn 2 had run. So the
branch was correct about *what not to say* and silent about *what must still be said*. The worked
example for the proxy path started after the introduction, so the early branch was never demonstrated
(D102).

**Detection heuristic.** For every mandated disclosure (AI, recording, consent), list the turn that
carries it, then list every exit branch that can fire BEFORE that turn — wrong number, proxy, busy,
do-not-call, "can't hear", a caller who speaks first. Each such exit's spoken line must either carry
the disclosure or state why none is owed. A disclosure check graded only on calls that reached the
main flow will never see this — grade it on the early-exit personas too.

**Fix direction.** Give each early exit its own "before the introduction" line that carries the
disclosure and nothing private, and demonstrate that branch with a worked example. Do not move the
disclosure earlier into the audio check — the audio check must stay alone (generic §15).
Verified on `181c23d5` (neighbour speaks first → identity + computer voice + recording, no child
named); Tier 2 in `demo/evidence/REPLAYS.md`.

**Source.** Shiksha Saathi (the `/demo` bot), 2026-09-23 — found by the mechanical grader on the bot's
first live call, not by a report. Related: D60 (bundled disclosure loses a half), D10 (mandatory step
skipped by a direct jump to the close), D102.

## D104 — "reassure them, in your own words" turns a forbidden threat into an unkeepable promise

**Symptom.** A worried father asked three times whether his daughter's name would be struck off the
school register. The prompt forbade any talk of consequences and, to stop a verbatim-repeat defect,
told the bot to answer later worries "in a few different words". Pressed, the bot said *"पूजा के स्कूल
में रहने या नाम कटने जैसी कोई बात नहीं है"* ("there is no question of her name being struck off")
(`58df39a9`) — a statement of school policy it has no way to know.

**Root cause.** The prohibition covered the threat ("her name will be struck off") but not its
negation ("her name will not be struck off"). An open instruction to rephrase gave the model licence to
generate new content, and under repeated pressure the most satisfying new content is the reassuring
fact the caller wants. Fixing the repetition (B1) by inviting paraphrase opened the fabrication.

**Detection heuristic.** For every forbidden claim about a consequence or outcome, check that the
prompt also forbids the NEGATED claim ("will not", "nothing will happen", "don't worry, that won't
happen") — both are claims of fact. Flag any instruction that lets the model reword a sensitive
reassurance freely ("in your own words", "say it differently", "reassure them") without supplying the
exact fallback line.

**Fix direction.** Rung 3: give the repeat case its own fixed line that defers and asserts nothing
("…इस बारे में वही सही बता पाएँगे"), and state the rule by type: never say whether the outcome will or
will not happen — not yes, and not no. Partly verified on `adf9fb96`: across three worries the bot
made no claim about the child's place either way (the promise is gone), but on the repeat worry it
also did not speak the fixed deferring line — the worry went unacknowledged. The promise half is
proven; the fallback-line half is not yet.

**Source.** Shiksha Saathi (the `/demo` bot), 2026-09-24 — found on a Tier 2 call after the v2.1 fix
for B1. Related: B1, D46, D89 (finality promises), and the CLAUDE.md escalation ladder rung 3.

## D105 — a hardcoded list was replaced, but the prose around it still describes the old list

**Symptom.** The bot offers roles, companies or cities that are not in its own list. On the KKB
inbound Signals bots a Ghaziabad caller was offered **"AC Technician, Krishna Enterprises, Bengaluru"**
(`98a684b9`, `0edced72`, 2026-09-28/30) — a job that exists nowhere in the bot's inventory.

**Root cause.** At the 2026-08-28 Signals cutover only the JSON block of the inbound Job Inventory was
swapped (Bengaluru → Ghaziabad for Hindi, Hubballi for Kannada). Everything that DESCRIBED the list
was left on the old one: the "What's available" summary line ("Data Entry Operator, Remote Customer
Support Executive, EV Charging Technician, and AC Technician. Locations are Bengaluru and Remote"), the
role-synonym map (old companies), the technician-family rule, the spoken "kinds of work" line, a rule
that "every job is in Bengaluru or Remote", and every worked example — 28 Bengaluru mentions in the
Hindi file, 20 in Kannada. The model followed the prose and the examples over the JSON (D50, D102):
five places agreed on the old list and one block of data disagreed.

**Detection heuristic.** For every hardcoded list in a prompt (job inventory, services, places),
collect its entity values (role, company, location). Then grep the REST of the prompt for entities of
the same kind that are NOT in the list — company names in examples, cities in rules, role names in
summary lines. Any hit is stale. In a diff: when a list block changes, grep the whole file for every
value that was REMOVED from it; a survivor outside the list is this bug.

**Fix direction.** Prefer removing the hardcoded list: fetch live from the job API (done 2026-10-05 —
the production inbound numbers now go to the KKB Slim bots, which call `get_jobs` /
`get_recommended_jobs`). If a list must stay, derive every summary line from it or delete the summary,
and re-set the worked examples on entries that are actually in the list.

**Source.** KKB Hindi + Kannada Inbound Signals, found 2026-10-05 while readying the inbound bots for
Operation Rozgar testing. Related: D50, D102.

## D106: consent heard at one step but only written at a later one is lost whenever the call ends in between

**Symptom.** Callers agree to the terms on the call, yet the backend still shows their consent as false.
2026-10-06 KKB Slim campaigns: 10 new callers said yes and none of their consent reached the backend;
on existing unconsented profiles the save fired on 1 of 5 (`6414e585`, `f6882d0b`, `f718e7c2`,
`61705722` skipped it).

**Root cause.** For a new caller the yes was only written by `create_profile`, which runs at the
apply step; any call that ended before an apply lost it. For an existing profile the save was a
"silent tool in the same turn" as a spoken line, and the model kept the line and dropped the tool.

**Detection heuristic.** For every consent or agreement the prompt asks for, find the tool that
writes it. If that tool runs at a LATER step than the ask, or only on one branch (e.g. only when a
profile exists), the yes is lost on every early exit. If the prompt says to call a silent tool "in the
same turn" as a spoken line, expect the tool to be skipped.

**Fix direction.** Write the yes at the moment it is given, on every branch: a separate tool for a
caller with no record (`record_consent_new`: name + age, creates the record), and make the save the
whole of the reply to the yes ("your reply is the tool call alone"). Verify on the backend, not the
transcript. Verified 2026-10-12: `6560f39e`, `3e3f7d69` (Hindi), `d9154118`, `930a8667` (Kannada).

**Source.** KKB Slim Hindi + Kannada, 2026-10-12. Related: D95, D101.

## D107: a default search value for undecided callers gives every undecided caller the same wrong jobs

**Symptom.** Callers who say "कोई भी चलेगा" (anything) all hear helper and labourer jobs. 14 of 63 searches
in the 2026-10-06 ITI and Polytechnic campaigns were the literal query `"helper"`, sent to trained
electricians, fitters and diploma engineers.

**Root cause.** The undecided-caller branch said "use their words if any, otherwise `\"helper\"`". The
fallback value became the answer for the most common reply.

**Detection heuristic.** Grep tool-argument guidance for a quoted default value ("otherwise X",
"default to X", "if nothing, use X"). Any default that is a real search term will be sent for every
caller who reaches that branch.

**Fix direction.** No default. Ask ONE question that yields the caller's own search term (their trade
or training), and if that still yields nothing, capture the preference instead of searching a guess.
Verified 2026-10-12: `6560f39e` ("electrician"), `d9154118` ("fitter").

**Source.** KKB Slim Hindi + Kannada, 2026-10-12. Related: D50.

## D108: an offer that ends on a statement, plus a "clear yes" list containing a backchannel, records acknowledgements as acceptance

**Symptom.** Interest is recorded for callers who were only saying "I heard you". TRRAIN: 35 of 53
recorded "interested" (66%) were not a real yes; KKB Slim services: 17 of 45 unconfirmed.

**Root cause.** The TRRAIN offer ended "if you are interested, their team will call you" (a statement,
no question), so the natural reply is "ठीक है / ओके". The prompt's "Clear yes" list contained exactly
those tokens, and the worked example showed "हाँ जी, ठीक है" recorded as Yes. The output prompt keyed on
the agent's own acceptance line, not the caller's words.

**Detection heuristic.** Find every offer line: if its last sentence has no question, flag it. Find
the acceptance rule: if it lists a backchannel token (ठीक है / हाँ / ओके / जी / ಸರಿ / ಹೌದು) as sufficient on
its own, flag it. Check the output prompt's interest field reads the CALLER's words.

**Fix direction.** End the offer on a real question; treat a bare agreement as "heard" and ask ONE
confirmation that needs a specific answer (a callback time); only a named answer is Yes; filler is
Maybe with a close that promises nothing; record the caller's evidence words in the output.

**Source.** TRRAIN Hindi + Kannada and KKB Slim services, 2026-10-12. Related: D95, D50.

## D109: a worked example's input value is supplied as the real value when the call's input is empty

**Symptom.** With no location input, the bot confirmed "हमारे पास आपकी जॉब की लोकेशन सरजापुर है" to a
caller who never mentioned it (`6560f39e`). Sarjapur was the `${location}` of worked call B.

**Root cause.** The only example of the location turn carried a concrete place. When the real input
was empty, the model filled the slot from the example (D102's mechanism, on an input variable).

**Detection heuristic.** For every input variable that can arrive empty, check that a worked example
demonstrates the EMPTY case. If every example shows a filled value, expect that value to be reused.

**Fix direction.** Demonstrate the empty case (the bot asks, the caller supplies the value), and give
the "no input" branch a line that carries no slot to fill.

**Source.** KKB Slim Hindi + Kannada, 2026-10-12. Related: D102, D50.

## D110: a guard that tests an injected variable is re-run after the caller answers, so the question loops

**Symptom.** The bot asks for a value, the caller gives a valid one, and the bot asks again with the
same line, over and over. Test call `fad874e4`: the caller said "201002" twenty times and heard
"हमारे पास आपका पिन कोड पूरा नहीं है" twenty times until the call hit its maximum duration. Real
calls showed the milder form: valid six-digit pins said in chunks ("27, 72, 11", "20, 12, 0, 4")
rejected two to four times, and 24/32 pin turns using the incomplete-pin line when `${location}`
had no digits at all.

**Root cause.** The pin turn said "before you say anything about the pin, do these three steps
silently, every time" and the steps split `${location}`. An injected variable never changes during a
call, so after every answer the check re-ran on the same digitless value, found "no pin", and chose
the ask line again. The caller's answer was never the thing being evaluated.

**Detection heuristic.** For every "every time / before you speak" check, ask what it evaluates.
If it reads an input variable (`${...}`) and the turn it guards ASKS the caller for that same fact,
the check must stop applying once the caller answers. Also look for a missing hard cap on any
re-ask ("once" in prose is not a cap the model counts).

**Fix direction.** Scope the variable check to the FIRST sentence of the turn; from the caller's
first answer on, evaluate only their answer (join chunked digits before counting); add a counted cap
("at most twice after the first ask, then move on").

**Source.** KKB Slim Hindi + Kannada, 2026-10-12. Related: D95 (storage slot doubles as evidence slot).

## D111: an enum list in the prompt disagrees with the tool schema, and the prompt wins

**Symptom.** Profile saves fail with HTTP 400 `INVALID_ITEM_STATE`. KKB Slim and Maya sent
`educationCategory: "Polytechnic / Diploma"` and `"ITI / Other Vocational Trainings"` (8 of 8 rejected),
and Maya sent `otherHelpNeeded: ["Training"]`; the live tool schemas said `Diploma`, `ITI` and two
`otherHelpNeeded` values. Tracker r113, r114 (2026-10-12).

**Root cause.** The prose listed old labels "byte-exact". The model follows the longer, nearer prose
over the parameter description.

**Detection heuristic.** For every enum-valued field, diff the values quoted in the prompt against the
live tool schema's description/enum. Any value in one and not the other is this bug. Also grep for
mapping lines ("X → `Value`") whose right-hand side is not in the schema.

**Fix direction.** Make the prompt quote exactly the schema's values (or point at the schema and quote
none). Source: KKB Slim, Maya Signals, KKB Signals (4 prompts), 2026-10-13.

## D112: example VALUES in the prompt are copied into calls where the real value is absent

**Symptom.** The bot reads back a PIN the caller never gave (22 calls: 201009, 201014, 110035,
201015, 110098, all from the prompt's own tables and worked calls), saves an age nobody said (25, 28),
names companies from the names table (SARA ENTERPRISES, GLOBAL CHEMICALS) as jobs, sends a
`12345678-1234-...` id. Tracker r122, r123, r124, r125, r127 (2026-10-12). Generalises D102 and D109.

**Root cause.** A required slot with no real value is filled from the nearest concrete example. Every
realistic example value is a candidate answer, including values in input-format tables that are
never meant to be spoken.

**Detection heuristic.** List every concrete value in the prompt that has the SHAPE of a caller fact or
an id: six-digit numbers, ages, UUID-like strings, company names, place names. Each is a copy risk
wherever the matching input can be empty. Search worked calls, tables and "e.g." clauses.

**Fix direction.** Replace example values with typed placeholders (`<pin>`, "the years the caller
said"), demonstrate the empty case, and in tool descriptions name the only legal source of the value.
Source: KKB Slim Hindi/Kannada, Maya Signals, 2026-10-13.

## D113: a stage direction or "stay silent" instruction is spoken aloud

**Symptom.** DKB said "(Wait silently)" as its whole turn on 24 calls; KKB Slim spoke
"*(Silent `get_profile` for 91XXXXXX3380)*", "*(Step 13: Services offer)*", "*(Wait for confirmation)*"
on 10 calls, one of them with the caller's phone number; 4 wrote a tool call as text and then
invented jobs. Tracker r132, r133.

**Root cause.** The platform needs SOME output each turn, so "do not speak" leaves the model the
instruction itself as the only text to emit. Worked-call notes written inside the dialogue block,
in the same `> ` quote format as the spoken lines, look like lines to say.

**Detection heuristic.** Grep for "wait silently", "do not speak", "say nothing" without a sanctioned
line next to it; grep worked calls for `> *(` notes and "Silent `tool`" phrasing.

**Fix direction.** Give a short sanctioned line instead of silence ("जी, ज़रूर।"); write notes outside
the quote block as "Note (not spoken): ...". Source: DKB Signals, KKB Slim, 2026-10-13.

## D114: a routing keyword appears inside the WRONG row's exception text

**Symptom.** `apply_job` returned `ACTION_LIMIT_REACHED` 5 times; the already-applied line was said
0 of 5 times. Tracker r118.

**Root cause.** The generic failure row named `ACTION_LIMIT_REACHED` three times (as an exception,
plus case history), and a paragraph said this row also covers the already-applied case. The keyword's
nearest, most frequent context was the wrong row.

**Detection heuristic.** For each routing table, grep every trigger token; if it occurs more often in
a row other than the one it routes to, expect misrouting.

**Fix direction.** State the token only in its own row; make the other row's condition "any other
result" with no mention of it. Source: KKB Slim, 2026-10-13.

## D115: "after the tool completes, say done" with no failure branch

**Symptom.** DKB told an employer "हो गया" twice while `create_job` returned 409
`PROFILE_LIMIT_REACHED` (call `121bebdf`); DKB also told employers it had removed a posting with no
tool that can remove one (`06d0224d`, `4a597bc7`). Tracker r130, r131.

**Root cause.** "Completes" is true of an errored call too, and an action with no tool had no
sanctioned truthful line, so the model claimed it.

**Detection heuristic.** Every success line must be gated on the RESULT ("only when the result returned
the item"), with a failure line beside it. For every action a caller can request, check that a tool
exists; if not, there must be a truthful "noted" line and an explicit "never say you have done it".

**Fix direction.** Result-gated success line plus a cause-free failure line; a "noted" line for
actions with no tool. Source: DKB Signals Hindi/Kannada, 2026-10-13.

## D116: the prompt is past the size this bot can handle, so it stops calling tools without any error

**Symptom.** Purple Dots Kannada outbound, full translation (~125 KB): fluent 30-turn calls, ZERO tool
calls in 3 of 3, and the bot told callers eleven times their details were saved. Empty call report, no
audio problem, no error. Partly reduced (~112 KB): tools in 1 of 2. Reduced master (105.6 KB): 3 of 3.
Two prompts ten characters apart near the edge behaved differently. (Aryan's Purple Dots language
rollout report, Oct 2026.)

**Root cause.** Every Indic script costs three bytes per character, and a literal translation is
longer than one written in everyday speech, so a mirror can be well past its master's size. The size at
which tools stop firing differs per bot (our KKB prompts run at 270 KB and still call tools), so no
single account-wide number protects anyone. The failure looks like a successful call.

**Detection heuristic.** `python3 scripts/prompt_size.py project <master> --lang <iso> --target <id>`
before translating, and `check` before deploying: compare with the target's recorded
`max_prompt_bytes` (seen failing) and `proven_prompt_bytes` (seen working) in `raya/agents.json`. Any
call with turns and zero tool calls on a path that requires one is this bug until proven otherwise.
`raya_deploy.py` refuses at or past `max_prompt_bytes`.

**Fix direction.** Slim the MASTER (/slim-prompt), never one language alone: delete examples that
repeat a rule stated elsewhere, tighten wording without touching a rule. Then re-translate. Record the
new proven size with its call id. One passing call near the edge proves nothing: the limit is a zone.
Source: Purple Dots (Kannada outbound), 2026-10.

## D117: a mirror's English rules still tell the bot to speak the master's language

**Symptom.** All four early Purple Dots translations still said "speak Hindi/Hinglish" in their English
rules, the Kannada ones "write in Devanagari"; a live Marathi call slipped into Hindi. Our own demo
Marathi bot still says "simple, everyday spoken Hindi" and "speak it as a Hindi number word" (found
2026-10-14 by the new check).

**Root cause.** The rule lines are English, so "copy the agnostic content byte-identically" copies the
language name with them. The line is agnostic in form and language-specific in meaning.

**Detection heuristic.** `scripts/language_checks.py` row "Instructions name this language": an
English line that instructs the bot to speak / write / use the master language or script (not one that
cites a past call). `scripts/speech_split.py` extracts these lines as `lang-rule` items so they are
rewritten, and fails the build if one survives.

**Fix direction.** In the master, word such rules language-neutrally where possible ("the call
language"). In each mirror, name the mirror's own language and script. Source: Purple Dots mirrors
(mr, kn, te, or), demo Shiksha Saathi Marathi, 2026-10.

## D118: a same-script mirror keeps master-language text that no script check can see

**Symptom.** Marathi shares Devanagari with Hindi, so the list of formal words the Marathi bot must
avoid stayed entirely in Hindi through every check. Script checks also flag the sentence mark (।)
that Odia and Assamese share with Hindi as a "leak", a false alarm.

**Root cause.** "Is the text in the right alphabet" cannot tell Marathi from Hindi. The question that
matters is "has every spoken line been translated".

**Detection heuristic.** Every master speech line must come back changed (`speech_split.py apply`
fails on an unchanged speech line for a same-script pair) and no Hindi marker word (है, नहीं, क्या,
रहा/रही, चाहिए, ...) may appear in Marathi speech (`raya/translations/lexicon.json`
`hindi_markers`). Never count the danda as residue.

**Fix direction.** Re-author the line, including vocabulary lists: a list of words to avoid is
re-derived for the target language, not copied. Source: Purple Dots Marathi, 2026-10.

## D119: a defect in the master is copied into every language

**Symptom.** The Hindi master offered "price" as the plain word for "assessment"; an example in the
master taught the bot to say details were saved when nothing had been. Translating would have copied
both into five languages.

**Root cause.** Translation fans the master out N times. Every master defect becomes N defects, each
found and fixed separately, each costing a test call per language.

**Detection heuristic.** Before any translation, run /prompt-analyser on the master and the
example audit (/generate-test-cases §3); a master with open findings is not a translation source.

**Fix direction.** Fix the master once through /update-prompt, then translate. Source: Purple Dots
Hindi masters, 2026-10.

## D120: a line with no equivalent in the target language becomes two identical lines

**Symptom.** A Hindi example contrasting masculine and feminine verb forms became two identical lines
in Kannada, Telugu, Odia and Assamese, whose first- and second-person verbs carry no gender.

**Root cause.** Line-by-line translation preserves the count of lines even when the distinction they
teach does not exist in the target language.

**Detection heuristic.** Two adjacent master lines that differ but come back identical
(`speech_split.py` warns). A gender rule copied byte-identical from the master (`language_checks.py`
"Gender rules" fails).

**Fix direction.** Write the target language's own gender rule (`lexicon.json` → `gender`), drop the
duplicate, and register the difference in `raya/divergences.json`. Source: Purple Dots kn/te/or/as,
2026-10.

## D121: a safety statement inside an ordinary answer is acknowledged only for the surface need

**Symptom.** In Marathi and in Kannada, a caller said mid-answer that they sometimes feel they should
not live. The bot acknowledged only the mobility problem and offered a wheelchair. The Hindi production
bots carry the same rule and had never been tested against it.

**Root cause.** The safety rule was written for a caller who raises distress as the topic. When the
statement arrives inside an answer to a form question, the phase's "acknowledge and move to the next
field" behaviour wins. And nothing tested it: it was found only because someone wrote the scenario.

**Detection heuristic.** A bot that talks to the public must have a safety interrupt that (a) applies
in EVERY phase and turn, including inside an answer to another question, (b) overrides the current
phase, (c) has its own mandatory spoken line in each language with a helpline or hand-off, and (d) is
never followed by the next form question in the same turn. Then a standing test case per language:
the caller embeds the statement inside an answer (generic checklist §18).

**Fix direction.** Add or scope the interrupt rule so it names "even inside an answer to another
question"; add the example to the master's examples; add the safety scenario to every language's
standing suite. Escalate the Hindi production decision to the programme owner. Source: Purple Dots
mr/kn outbound, 2026-10.

## D122: a proper noun changes in translation

**Symptom.** A city in the Marathi translation turned Nagpur into Jabalpur. An earlier rehearsal
"localised" a child's name in examples whose English context lines still used the original name.

**Root cause.** A translator treats names as content to adapt. Parallel agents each decide on their
own.

**Detection heuristic.** Before fan-out, list every person, place, department and programme name in
the master's speech and pin the target spelling (`speech_split.py extract --names names.json`); `apply`
fails if a pinned name is missing from its line. For same-script pairs `apply` also warns when a name
that survives everywhere else vanished from one line.

**Fix direction.** Pin names centrally, once, before fan-out. Source: Purple Dots Marathi, demo
rehearsal, 2026-10.

## D123: the translation is correct but too formal for the caller

**Symptom.** A Marathi tester said the bot's language was "very complicated"; the Kannada bot had the
same complaint earlier (textbook Kannada, not spoken). The language skill already said "re-author, don't
translate", and it still happened.

**Root cause.** A model asked to translate reaches for the formal register, and a model reviewing its
own lines does not hear them as a caller would. There was no per-language list of everyday words and
no mechanical scan for bookish ones, so "use everyday words" stayed an intention.

**Detection heuristic.** The target file must have an everyday-word table built for that language
(minimum terms: training, pension, certificate, documents, eligibility, scholarship, support centre,
assessment, device). `speech_split.py apply` warns on every bookish word in `lexicon.json` → `formal`
with the everyday replacement. A native listener's "news reader / form / neighbour" verdict on the
first live call is the real gate.

**Fix direction.** Give every translating agent the language's style card with the everyday-word table
(`raya/translations/style/<iso>.md` + lexicon). Rewrite flagged lines; never ship with an unreviewed
formal-word warning. Source: Purple Dots Marathi feedback, KKB Kannada history, 2026-10.
