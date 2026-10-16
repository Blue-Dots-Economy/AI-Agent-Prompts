# Section Checklists

What a conversation prompt **must contain** to be safe to run. A missing critical section is a
top-severity flag. Two parts: (1) use-case archetypes with their required sections, (2) the
universal rule checklist that applies to every voice agent here.

Match sections by **intent, not exact heading string** (agents name them differently — see
`../update-prompt/reference/prompt-anatomy.md`). "Critical" = its absence causes a live failure
or a safety/compliance gap.

---

## Part 1 — Use-case archetypes

Pick the closest archetype (or combine). State which one you matched and why.

### Universal core (every voice agent, all archetypes)
Critical:
- **Identity & persona** — name, role, audience, tone; **modality** (inbound vs **outbound**) stated.
- **Core voice rules** — one-question-per-turn, short responses, acknowledge-then-proceed.
- **Input variables** — declared, with presence/"Not Available" rules; `${...}` names never localized.
- **Conversation pipeline / phase structure** — ordered, with entry conditions.
- **Language & script rules** + **TTS normalization** (numbers/money/date/time/phone as words).
- **Prohibited language** — including a domain **banned→preferred vocabulary list** (not just abstract "simple words").
- **Guardrails** — forbidden topics, dignity/safety, eligibility/age hard-stop, relevance + functional-sanity.
- **Tool section** — every tool used is **declared** here (referenced-but-undeclared = flag), with exact payloads, fixed params, and enum lists (English/Latin).
- **Graceful exit / closing** — a fixed closing script consistent with the modality.
- **Memory-injection block** — `### Contact context / {${contact_memory}}` **iff** memory is enabled.
- **Few-shot examples** — present, and they model the **mandatory** flow (don't skip gated steps).
- **Safety interrupt** (any bot that talks to the public; critical for vulnerable callers) — a rule that
  applies in EVERY phase and turn, **including when the statement arrives inside an answer to another
  question**, overrides the current phase, has its own mandatory spoken line in each language (with the
  helpline or hand-off), and is never followed by the next form question in the same turn (D121).
- **Per-language speech rules** (every non-master language file) — the instructions name THIS language
  and script, never the master's (D117); an everyday-word table built for this language covering at
  least training, pension, certificate, documents, eligibility, scholarship, support centre, assessment,
  device (D123); a gender rule written for this language, not copied (D120); a list of words never to
  say where the domain has insulting terms (e.g. disability words), mirrored in the agent's recognition
  vocabulary. `scripts/language_checks.py` checks all four.

### Archetype: Outbound data-collection / profiling bot
*(the Purple Dots disability-needs bot; any bot that calls a user, fetches a profile, collects/verifies fields, and connects them onward)*
Add, and treat as critical:
- **Opening consent gate** (recording/data) — asked once; **hard-stop on decline** with no tool calls.
- **Silent profile fetch** — gated behind consent; not announced; name confirmation from the fetched record.
- **Profile completion/verification** — field-by-field, single-question, with skip-if-already-correct.
- **Mandatory-but-silent terminal tool sequence** (update → match/search → connect) with:
  - a **must-run gate** per step, and a **"do not close the call before <terminal tool> (or the decline path)"** gate (C1);
  - **cascade awareness** — downstream phases gated on an upstream tool must note the upstream miss risk.
- **Second consent gate** (share/hand-off) — distinct from the opening consent; asked **exactly once** even when N downstream records exist (B1).
- **Uncertain-user framework** — how to guide someone who can't name their need (open, in-context questions; no forced mapping).
- **Scope boundaries** — explicit list of what the bot must never promise/do/simulate.
- **Voice-gender rule** — if the persona has a gender, an explicit verb-form rule (D4).

### Archetype: Job-matching / recommendation bot (KKB, Maya)
Add, and treat as critical:
- **`new_seeker` (or equivalent) branch** — new vs returning caller drives fetch-vs-create; no re-fetch at action time.
- **Reading the fetched profile** — a "reading the response" section: field map, most-recent-record rule when the response is an array, and "present ⇒ known ⇒ never re-ask"; the profile is actually *used* (address by first name, confirm role) not fetched-and-ignored (C6); the record's `id` is bound as the reusable `profile_id` and the create path is forbidden when a profile was found (C7).
- **Recommendation presentation flow** — steps for 1/2/3+ options; company/role/location/salary spoken format; results **ranked by the caller's known signals** (role → location → salary), not raw array order, with an orient/overview turn when the target role is unknown (C8).
- **Primary action (apply) + success/failure handling** — bridge line spoken **once** (B1); silent tool call; single result.
- **Post-action info gathering / profile update** (if the agent completes profile after the action).
- **Introduction priority rule** — opening line chosen from prior-call memory state.
- (Maya) its divergences: campus identity/`${college_name}`, `hr_contact`/`benefits`, Experience Capture, HR-number sharing, feminine voice. (The MPL competition offer was removed from every Ghaziabad Maya bot on 2026-10-12, `Maya/CHANGELOG.md`; a Maya prompt that still pitches it is a finding.)

### Archetype: Employer / verification & capture bot (DKB)
Add, and treat as critical:
- **Turn-based introduction** (1–3 turns) and **phase-entry routing** on whether records already exist.
- **Freshness / completeness phases** — per-record internal tool discipline ("call <tool> for every record before proceeding").
- **Consent-gated create** — never create before explicit consent; never skip the insight/lookup step.
- **Market/insight delivery** — data logic separate from phrasing.

---

## Part 2 — Universal rule checklist (run on every prompt)

Tick each; flag misses. (Each ties to a pattern in `bug-patterns.md`.)

**Flow & gates**
- [ ] Every "mandatory" step has a **negative gate** on its competing action (A1).
- [ ] Skip logic (SKIP-AHEAD/ORDER-FLEX/"move silently") is balanced by a never-skippable list (A2).
- [ ] No two sections capture overlapping content without a sharp distinction + independent gate (A3).
- [ ] No header/body or intra-branch contradiction (A4).
- [ ] Adjacent askable steps have an explicit wait / separate-turn boundary; no two questions fused into one turn (A7).

**Repetition**
- [ ] Every consent/bridge/confirmation line is bounded to **"ask/say once"** (B1).
- [ ] Nothing human-facing sits inside a "for each <record>" loop (B1).
- [ ] Background tool calls are marked silent; no fetch/waiting narration allowed (B2).

**Tools & payloads**
- [ ] Every tool/sheet **named in the body is declared** in the tool section (C2).
- [ ] Terminal/background tool calls have must-run + "don't close before terminal tool" gates; cascades noted (C1).
- [ ] Every payload value traces to a source; coordinate order is `[lng, lat]`; field names match schema exactly (C3).
- [ ] No `${...}` with unbalanced/stray brackets; no hardcoded id contradicting a dynamic search (C3).
- [ ] All fixed params present & unchanged; all enum fields constrained to exact English/Latin allowed values (C4).

**Language, script & voice**
- [ ] A concrete **banned→preferred vocabulary list** exists (not just "use simple words") (D1).
- [ ] TTS section present AND examples obey it (words for numbers/money/date/time/phone) (D2).
- [ ] Script boundary stated: the call language's own script for spoken text, English/Latin for payloads, plus transliteration rules (D3).
- [ ] If persona is gendered, an explicit verb-form rule; no mixed/opposite forms in any line (D4).
- [ ] If outbound: a closing script + a ban on "call me/us back" phrasing (D5).

**Examples, consent, guards, memory**
- [ ] Examples model the mandatory path; greetings match the canonical one; no garbled text; names localized (E1).
- [ ] When a control variable (e.g. `new_seeker`) selects the opening/path, every example is labelled with its value and no example's opening can bleed onto the other branch; re-test the other branch after adding an example (E1).
- [ ] Each distinct consent gate asked once, with a clean decline hard-stop; distinct consents kept distinct (E2).
- [ ] Memory-injection block present verbatim iff memory enabled (else flag Verify) (E3).
- [ ] Guard sections all present: forbidden topics, dignity/safety, eligibility/age, relevance + functional sanity, scope boundaries (E4).

**Size, safety and access**
- [ ] The file is within this bot's size limit: `python3 scripts/prompt_size.py check <file> --target <id>`
  says OK (WARN: the first test call must prove every tool fires; BLOCK: slim the master first) (D116).
- [ ] A public-facing bot has the safety interrupt from Part 1, worded to apply "even inside an answer to
  another question", with its own spoken line in this file's language (D121).
- [ ] Access needs are handled for callers who are slow to answer, ask for a repeat, or hand the phone to
  someone else: silence is treated as needing time, a repeat is given on request, and the caller's
  disability is never made the topic of the call (voice-test `generic.md` §14).

**Languages (every non-master file)**
- [ ] `python3 scripts/language_checks.py <master> <this file> --lang <iso>` has no FAIL. It covers: no
  master-language text left in speech (D118), rules that name this language and not the master's (D117),
  the everyday-word table (D123), the gender rule (D120), the insulting-words list, digits, Goodbye
  token, payload fields and structure.
- [ ] Every person, place and programme name in speech matches the master's pinned spelling (D122).
- [ ] Open findings on the master are fixed in the master first, not separately per language (D119).

**Cross-language (pointer)**
- [ ] Any change that looks AGNOSTIC is noted for a `/sync-check` against every mirror (F).

## Seeker bots — the missing-job-data fallback (added 2026-09-04, D66)

Any seeker prompt that carries a "no jobs were supplied to this call" fallback line must satisfy all
four of these. The line is the most damaging thing the bot can say to a job-seeker short of a fake
application, and on 2026-09-04 it was spoken on five calls that had been sent 3, 22, 28, 29 and 29
jobs — three of them real production callers.

1. **Its condition names a REAL input variable.** Grep the condition for identifier-shaped tokens and
   check each against the `${...}` variables the prompt actually declares. An alias ("`${recommendations}`
   as job_recommendations") is the usual killer: the test then names something that does not exist and
   reads as empty on every call.
2. **The empty case and the wrong-role case have DIFFERENT lines.** "No jobs were supplied" and "none
   of these fit what you asked for" are different facts. One line for both guarantees the wrong one
   gets spoken.
3. **The wrong-role line names what IS available.** It has two mandatory slots (the role asked for,
   and the kinds of work we do have); there is no version of it that names nothing.
4. **A count guard sits in front of any "nothing left" claim** — the jobs actually said aloud on this
   call, against the valid entries in the recommendations array. Without it the bot claims the list is
   exhausted with most of it unnamed.

Standing check: `raya/regression/nojobs_integrity.py`.
