---
name: translate-prompt
description: Take a bot into a new Indic language. Re-authors only the words the bot speaks, the way that language is really spoken on a phone call (never a literal translation); copies every rule, tool call and payload by machine and proves them identical; projects the prompt size first (a too-large prompt silently stops calling tools); runs the language checks; then registers, deploys and voice-tests the new agent. The language stays VERIFY-PENDING until a named native speaker signs off. Covers 12 Indic languages. Use when the user says "take this bot into Telugu/Tamil/Marathi", "translate the prompt", "add a new language", "add Marathi", "make a Kannada version", "make it multi-language", "localise this bot", "we need a Malayalam version", or a project is being expanded to more languages. Not for carrying an existing change into languages that already exist (that is /sync-check, then /update-prompt).
---

# Translate Prompt: take a bot into a new language

**What it produces, per language:**

1. A new conversation prompt, `<Bot>/<Bot> <Language>[ <variant tokens>].md`, in which only the spoken
   words differ from the master (plus the sections that are this language's own: numbers, places,
   gender rule, everyday words).
2. A registered, deployed Raya agent running it, with the right language and voice.
3. A QA record, `raya/translations/<bot-id>-<iso>.md`: the decisions, every check result, the call ids.
4. Live test calls in that language, and the bot's language tab in its test sheet filled in.

The language is **VERIFY-PENDING** until a named native speaker signs the review (step 10), whatever the
test calls say.

**The bar.** A bot that sounds translated loses a low-literacy or access-constrained caller in the first
ten seconds. A line that is correct in meaning but that nobody would say on a phone call is a
**failure** of this skill, not a partial success.

**Not this skill.** A change that must reach languages that already exist: `/sync-check`, then
`/update-prompt`. A fix to the master: `/update-prompt`. This skill creates a language; it is not a
second editing path.

## Fast path

| Step | What | Blocks on |
|---|---|---|
| 0 | Clean the master once: open issues, `/prompt-analyser`, example audit, safety interrupt | once for all languages |
| 1 | Scope: language, region and audience, direction, named native reviewer; start the QA record | |
| 2 | `raya_deploy.py diff` (+ `pull`), `prompt-version.sh save`, `prompt_size.py project` | BLOCK: slim the master |
| 3 | Section ledger: which sections are copied, which are this language's own | |
| 4 | Pin names and terms, then `speech_split.py extract` | |
| 5 | One agent per chunk re-authors the spoken lines; `speech_split.py apply` | must PASS |
| 6 | Hand pass on the language's own sections and the examples | |
| 7 | `language_checks.py` and `/sync-check` | any FAIL |
| 8-9 | Gate 1 (read the new file alone, aloud), Gate 2 (back-translate, compare meaning) | |
| 10 | Native review tab; until signed, VERIFY-PENDING | |
| 11 | `/register-bot` (variant path), language and voice ids, `raya/voices.json` | no voice: BLOCKED |
| 12 | `raya_deploy.py verify` / `diff` / `deploy` | |
| 13 | `/voice-test` in the language: tools fire, safety case, three tiers | |
| 14 | Standing checks, `CHANGELOG.md`, QA record complete | |
| 15 | Report in plain words | |

Several languages: step 0 once, then steps 1-15 per language. Languages can be authored in parallel
(each is its own file and agent), but live tests share one tester: never run two test waves at once.
A bot with several prompts (inbound and outbound, Signals and legacy): one full pass per prompt.

## The three rules behind every decision

1. **Language-agnostic content is copied byte-identical:** call flow, steps, conditions, `${variable}`
   names, tool names, JSON payloads and field names, fixed params, enums, prohibited-behaviour rules,
   safety and dignity checks, the section skeleton. The governing taxonomy (AGNOSTIC / SPECIFIC /
   MIXED) is `../update-prompt/reference/prompt-anatomy.md`.
2. **Instructions are always in English.** Only the words the bot literally speaks (quoted lines,
   example dialogues, number words) are in the target language. A rule written in Telugu is a bug.
3. **Spoken content is re-authored, never translated:** what a real speaker of the target language
   would say in that situation on a phone call, with the same job, meaning and length budget.

## Read before you start

- `../update-prompt/reference/prompt-anatomy.md`: the section tags.
- `reference/language-matrix.md`: per-language script, register, numbers, honorifics, greetings, places,
  TTS and ASR pitfalls. Its word lists live in `raya/translations/lexicon.json` and lessons from earlier
  runs in `raya/translations/style/<iso>.md`; `speech_split.py extract` compiles all three into the
  `STYLE.md` card the translating agents read.
- The master file end to end, and one existing mirror as a model of "re-derived natively" (for example
  `KKB/KKB Placeholder Kannada Signals.md`: its `Language and Script Rules`, `TTS Normalization Rules`,
  `Canonical Location Spellings` and examples).
- `../prompt-analyser/reference/bug-patterns.md`: D1 (bookish words), D2 (numbers as words), D3 (spoken
  script vs payload script), D4 (voice gender), D6 ("/" read aloud), D8 (internal terms spoken), D26
  (place spellings), E1 (examples contradict rules), E3 (memory block), and the translation set
  D116-D123.
- `../voice-test/reference/checklists/generic.md` §8 (language and script), §18 (safety statements),
  §19 (call-level language checks).

## What went wrong last time (Purple Dots, five languages, Oct 2026), and what now stops it

| What happened | What stops it now |
|---|---|
| Kannada at full size held fluent calls with **zero tool calls**, telling callers their details were saved | Size projected before translating and checked at deploy (step 2, D116) |
| Instructions and tool calls got translated | Translators only ever see spoken lines; `speech_split.py` copies the rest and proves it (steps 4-5) |
| English rules still said "speak Hindi/Hinglish"; a Marathi call slipped into Hindi | Those rule lines are extracted and rewritten; the build fails if one survives (D117) |
| Hindi words stayed inside Marathi, invisible to script checks | Same-script lines must come back changed; Hindi marker words fail a Marathi build (D118) |
| Nagpur became Jabalpur | Names pinned once, before fan-out; a missing pinned name fails the build (D122) |
| The master's own mistake would have gone into every language | Clean the master first (step 0, D119) |
| A gendered example became two identical lines | Each language's own gender rule; duplicates flagged (D120) |
| "The language is very complicated" (Marathi tester) | Everyday-word table per language, bookish-word warnings, native listener as a gate (D123) |
| The bot missed "I don't want to live" said inside an answer, in two languages | Safety case in every language's tests (step 13, D121) |

---

## Procedure

### 0. Clean the master before you fan out (one fix, not N)

Every defect in the master becomes one defect per language, each found and fixed separately.

1. **Read the bot's open-issues list** (the tracker sheet, or the issue table in
   `raya/intake/<bot-id>.md`; `/bug-fix` → four habits). An open issue that touches speech, examples or
   the safety line will travel into the new language: fix it in the master first, or list it in the QA
   record as carried over.
2. **Run `/prompt-analyser` on the master, and the example audit** (`/generate-test-cases` §3). Findings
   that would travel into speech (a wrong plain word, an example that claims something the tools did not
   do, a rule that contradicts an example) are fixed in the master via `/update-prompt`, which owes its
   own proving calls.
3. **Make the master's language-naming rules and headings language-neutral** where you can ("the call
   language"). A heading cannot change in a mirror without breaking the skeleton, so a heading that names
   the master language must be fixed in the master. `speech_split.py extract` (step 4) prints a WARNING
   for each one; run it once into a scratch folder now to get the list.
4. **Check the master's safety interrupt** exists and fires even inside an answer to another question
   (`../prompt-analyser/reference/section-checklists.md`, D121). Translating a bot that misses this
   produces N bots that miss it.

Also run `python3 scripts/prompt_structure.py "<master>"`: a step reference that points at the wrong
step is copied into every language, and fixing it once in the master is cheap (D125).

### 1. Scope, register and reviewer

Write down, in the QA record (template at the end of this file), before authoring a line:

- bot, master file and master language (the `language` code on its `raya/agents.json` target, never
  the filename: `KKB Placeholder Inbound.md` is Hindi), target language and ISO code, direction,
  variant (Signals / legacy / slim);
- **the region and audience** of the callers. It picks the variety (Telangana vs Coastal Andhra
  Telugu), the greeting, the honorifics and the example places. Ask; never default it silently;
- **the native reviewer**: a named speaker of the language who will read it back, or **NONE** plus
  who accepted that it ships VERIFY-PENDING. For every language the matrix marks
  `[needs native review]`, VERIFY-PENDING is the realistic outcome unless a reviewer is lined up now.

The target must have a section in `reference/language-matrix.md` **and** an entry in
`raya/translations/lexicon.json` (both scripts exit with `KeyError` on an unknown code). If either is
missing, add it first (matrix → "Adding a language").

### 2. Reconcile with live, snapshot, project the size

```bash
cd "/Users/parthbansal/EkStep/Prompt Tuner"
python3 scripts/raya_deploy.py diff <master-target-id>   # is the LIVE master ahead of the repo?
python3 scripts/raya_deploy.py pull <master-target-id>   # only if live is ahead; review git diff
scripts/prompt-version.sh save <Bot> pre-<iso>-translation "translating <Bot> to <Language>"
python3 scripts/prompt_size.py project "<master file>" --lang <iso> --src <master-iso> --target <master-target-id>
```

Cloning a master that is behind live puts stale logic into a new language for as long as it lives. If
GET is flaky or empty, use `/raya-reconcile` instead of trusting it.

A prompt past the size a bot can handle does not error: the bot talks fluently and stops calling tools
(D116). The limit differs per bot and is recorded per target from evidence (`max_prompt_bytes`,
`proven_prompt_bytes`, `size_evidence` in `raya/agents.json`).

- **BLOCK**: slim the **master** with `/slim-prompt`, then start again. Never slim one language alone.
- **WARN** (larger than any proven size, or no evidence yet): go ahead; the first live call (step 13)
  must show every tool firing, and you record the result on the new target.
- The estimate gives two sizes: everyday speech with loanwords (our Kannada twins measure 0.8 to 1.1
  times the Hindi: `prompt_size.py ratios`) and a literal translation (larger). Aim for the first; a
  literal translation is both too big and too formal.

### 3. Section ledger

The split in step 4 works by script, not by meaning, so you still need to know what each section is.
List the master's headings (`grep -n '^#\{1,4\} ' "<master>"`) and tag each against `prompt-anatomy.md`
in the QA record: *"if this exact text appeared unchanged in the other language's file, would it be
correct?"* Yes: AGNOSTIC. No: SPECIFIC. Partly: MIXED (copy the rule, re-author the quoted speech).

- **Always this language's own, rebuilt in step 6:** `Language and Script Rules`, `TTS Normalization
  Rules`, `Canonical Location Spellings`, the everyday-word table, the gender rule, the insulting-word
  list, tone markers, prohibited phrases, `Sample Conversational Patterns` and every example.
- **Always byte-identical:** `Input Variables`, `Hallucination Guard`, `Conversation State Model`,
  every `<tool> Tool Call Rules` section and `Tool Call General Instructions` with every payload,
  `Action and Consent Rule`, `Dignity Safety Check`, `What You Must Always Preserve`.

### 4. Pin names and terms, then split the master

**Never hand the whole master to a model.** That is how rules and payloads got translated and the file
bloated.

1. **Pin every name, centrally (D122).** List each person, place, department, programme and
   organisation name the master speaks, and the bot's own persona name. Decide each once:
   - a **real** name (the places the bot serves, the organisation, the programme, the persona) keeps
     the same name in the target script, and you **check what it means** in the target language (in
     Marathi शिक्षा means punishment: the demo bot's name became शिक्षण साथी);
   - an **illustrative** name in an example (a caller called Ramesh in Ghaziabad) is replaced by a local
     one from the matrix's place list, so the examples sound local.

   Write `names.json` (`{"<master spelling>": "<target spelling>"}`). Translating agents keep every
   unpinned name unchanged, so localising an example name only happens through a pin. Parallel agents
   left to decide names disagreed with each other.
2. **Fix the term sheet** (`terms.md`): the 5 to 15 domain words that recur (class teacher, support
   centre, assessment, the disclosure wording), each with the one target word to use.
3. **Extract:**

   ```bash
   python3 scripts/speech_split.py extract "<master>" raya/translations/work/<bot-id>-<iso> \
       --lang <iso> --src <master-iso> --chunks 4 --names names.json --terms terms.md \
       [--pin "old=new|why" ...]
   ```

   It writes only the **spoken lines** and the **English rule lines that name the master language** into
   `chunk-N.json`, plus `STYLE.md` (matrix section, lexicon word lists, style lessons, gender and
   question rules, term sheet, pins, re-authoring rules). Every other line is copied by machine in
   step 5.

### 5. Re-author the spoken lines, stitch, prove

Launch one agent per chunk, all in one message (`Agent`, `model: "sonnet"` or stronger: a smaller model
missed the persona-name trap 8 times out of 8 in rehearsal). Tell each: *read STYLE.md and chunk-N.json
together, re-author every line as STYLE.md says, write only the JSON object to chunk-N.out.json.* Then:

```bash
python3 scripts/speech_split.py apply "<master>" raya/translations/work/<bot-id>-<iso> "<new file>"
```

`apply` writes the new file and **fails** unless: every non-extracted line is byte-identical to the
master; headings, `${variables}`, `` `code` `` values and `[slots]` are unchanged; every spoken line came
back (and, for a same-script pair such as Hindi to Marathi, came back changed, with no Hindi marker
words); no master-script letters remain in speech (the shared danda is allowed); no English rule still
tells the bot to use the master language; every pinned name is present; `Goodbye` is unchanged and
still last; no digit appeared; no question stopped being a question; no insulting word is spoken.
It **warns** on bookish words (with the everyday word), on a name gone from one line, on spoken lines
with no target-language letters, and on two different master lines that became identical (D120: drop
one, write this language's own rule, and register the difference in `raya/divergences.json`).

Fix a failure by re-running that chunk's agent with the failure quoted, or by editing the
`.out.json`; never by editing rule lines in the output file. Review every warning: fix it, or note it
in the QA record with the reason.

**The standard for every spoken line** (what the agents are told, and what you and the reviewer hold
them to):

1. Say in English what the line must accomplish in that turn (greet; disclose AI and recording; ask one
   field; confirm a misheard number; bridge a silent tool call; refuse without shaming; close).
2. Write what a real speaker in that region would say to do that, fresh, not in the master's word order.
3. Keep the length budget: trim to the master's spoken duration, not its word count.
4. Match the matrix's register: polite pronoun, verb ending, politeness particle (Telugu `అండి`, Punjabi
   `ਜੀ`, Tamil `-ங்க`, Urdu `جی`), natural code-mixing level.
5. Prefer the everyday word over the bookish one, and the loanword when that is what people say, in the
   target script (D1, D123): `అప్లై` not `దరఖాస్తు`, `அப்ளை` not `விண்ணப்பம்`.
6. Watch diglossia: Tamil, Malayalam, Bengali and Telugu each have a literary register that machine
   translation reaches for and nobody speaks (`கூறுங்கள்` vs `சொல்லுங்க`; sadhu vs cholit Bengali).
7. Keep voice-gender agreement in every spoken line if the bot has a gendered voice (D4).

### 6. Hand pass on the language's own sections

The agents re-authored the spoken strings in these sections; what they cover and how they are built
must now be checked against the matrix. Keep each section's English scaffolding identical to the
master's.

| Machinery | Re-derive for the target language | Guards |
|---|---|---|
| Script rule | the one script allowed; Latin and mixed script forbidden | D3, §8 |
| Loanwords and everyday words | the words natural in **speech**, in its script; the everyday-word table covering the lexicon's minimum terms | D1, D123 |
| Numbers, money, ranges, dates | words in that language's counting idiom; long spoken dates | D2 |
| Per-unit rates and "/" | "per day" phrasing; the word for "or"; never the symbol | D6 |
| Times | day-part words, never AM/PM | D2 |
| Phone numbers, PIN codes | digit by digit, with the zero-word people actually say | D2 |
| Email, abbreviations | speakable `@` and `.`; spoken letter names | D2 |
| Honorifics, greeting, farewell | the polite pronoun, particle, name suffix; a natural phone greeting and close for that region | matrix |
| AI and recording disclosure | re-authored, still before the pitch, with every required element | §1 |
| Hold filler, read-back | a neutral "one moment" that does not narrate the step; a natural "you said X, right?" | B2, D34, §6 |
| ASR confusion pairs | the pairs this language's ASR actually collapses | matrix |
| Prohibited phrases, insulting words | rebuilt for this language's own shaming and pressure phrasings; insulting words from the lexicon | matrix |
| Gender rule | this language's own rule (lexicon), not a copy of the master's | D4, D120 |
| Canonical place spellings | one pinned spelling per place, overriding all transliteration | D26 |
| Tone markers | the language's own softeners | anatomy |

Two rules that catch most of the damage: **never emit native-script digits** (`౧౨౩`, `১২৩`, `۱۲۳`):
numbers are words; and **pin every place** the flow, inventory or examples can mention.

**Examples** (`Sample Conversational Patterns`, every few-shot): same number, same slots, same English
labels as the master; local person and place names (pinned in step 4); jobs, services or benefits
plausible where those callers live; and they must obey the file's own rules (E1): a banned phrase never
appears in an example, a mandated read-back is never skipped in one.

**Memory block.** If the bot has memory, the new file carries, verbatim, in English, in the master's
position:

```
### Contact context
Here is the caller context:
{${contact_memory}}
```

### 7. Language checks and parity

```bash
python3 scripts/language_checks.py "<master>" "<new file>" --lang <iso> --src <master-iso> \
    --target <new-target-id> [--config raya/translations/<bot-id>-checks.json] \
    --json raya/translations/<bot-id>-<iso>-checks.json
```

These are the "Prompt" rows of the language-testing sheet, made mechanical: spoken lines all
translated, `Goodbye` intact, variables / code values / JSON keys / payload blocks identical, questions
marked, no digits or symbols in speech, an everyday-word table rebuilt for this language, an
insulting-word list, a gender rule naming this language, the disclosure elements (from the bot's
`--config`), English rules naming this language and not the master's, heading count and memory token,
and size against the bot's limits (`--target` needs the target registered, so rerun it after step 11).
**Any FAIL blocks the deploy.** Paste the table into the QA record; it also fills the Prompt rows of the
bot's language tab (`/generate-test-cases`).

Then run **`/sync-check`** on the bot. It checks what `language_checks.py` does not: the exact heading
set and order, the full token census, the verbatim three-line memory block, and the deliberate
differences recorded in `raya/divergences.json`. The new language must come out clean. A difference you
introduced on purpose, with the owner's approval, gets a `raya/divergences.json` entry in the same
change.

### 8. Gate 1: read the new file alone

**Do not look at the master.** Read every spoken line aloud as the bot on a real call and ask: *would a
real speaker of this language say this, out loud, on a phone call, to this caller?* Rewrite anything
bookish, machine-sounding (source word order, calques, a pronoun a speaker would drop), over-formal or
over-familiar, hard for TTS (long compounds, digits, symbols, Latin script), too long for its turn, or a
purist coinage where people use the loanword. Record every flag and rewrite. **Zero flags on a first
read means it was not read properly: read it again.**

### 9. Gate 2: back-translate and compare meaning

Now open the master. Back-translate each new spoken line to English from the target language alone and
compare with the meaning of the master's line. Different wording is expected; what this gate catches is
**drift**: a lost obligation (disclosure, consent ask, read-back, "say this once"), a changed condition,
a promise or fact the master never made, a refusal softened into a commitment, a dropped limit or
"never", a changed number, name or id. Every drift is fixed, and the rewritten line goes back through
Gate 1. Both gates must pass on the final text.

### 10. Native review: a gate, not a note

Gates 1 and 2 are done by the author; neither is a native speaker. A language is **verified** only when
a named speaker signs off.

Give the reviewer a review tab in the bot's test sheet: master line, new line, English back-translation,
"sounds like: neighbour / form / news reader", fix. **Safety lines first**, then refusals, closings, the
consent disclosure, then the rest. The tab is their whole job; they should not need to open the prompt.
`scripts/testcase_sheet.py` has no layout for this tab yet, so write it with `scripts/gsheets.py update`
(service account), after asking, since the sheet is visible to others.

- **Reviewer available:** record their name, date and verdict in the QA record.
- **No reviewer:** do everything else (both gates, live calls with transcript and audio review, the
  analyser pass) and mark the language **VERIFY-PENDING** in the QA record, the changelog and every
  report. Never write "done", "confirmed" or "native-verified" without a named human.

### 11. Stand up the new agent

A new language is a new agent. Registration goes through **`/register-bot`** (its variant-addition
path); it adds the path-map row, the `raya/agents.json` target and the standing-regression entry. Check
when it finishes:

- The agent exists on Raya (created by whoever owns the console, usually cloned from the master agent so
  the tools come along; this skill does not create agents).
- The target row has `id` (`<bot>-<iso>-<dir>[-<backend>]`), `file`, `agent`, `language` (the ISO
  code), `direction`, `kind: "conversation"`, `profile`, `raya_name`, `raya_agent_id`, `deploy`.
- **The uuid is hand-copied** from `python3 scripts/raya_deploy.py list`, never inferred from a
  filename.
- `expected_name_contains` names the bot **and** the language or variant (`["Purple Dots", "Telugu"]`):
  a guard of just the bot name lets a Telugu prompt land on the Hindi agent.
- An agent on a different Raya account has `"account": "<name>"` on the row and its key in `raya/.env`
  as `RAYA_API_TOKEN__<NAME>`.

**Then the language and voice, which registration does not cover.** `deploy` PATCHes instructions only;
the agent's `language_id` and `voice_id` are set on the console by its owner. A cloned agent still
carrying the master's pair reads the new script with the wrong voice ("the file looks perfect, the call
sounds broken"; a Hindi voice reading Marathi is audible on every line).

```bash
python3 scripts/raya_testcall.py whoami <new_agent_uuid>   # name, language_id, voice_id, DIDs
```

`whoami` is the only command that prints the pair (`raya_deploy.py list` gives id and name only).
Take the pair from `raya/voices.json` for the agent's account, or harvest it with `whoami` from an agent
that already runs the language and record it there (with source agent and date). Ids differ per account
and no API lists them. If no agent runs the language yet, ask LitWiz Labs for the pair; until then live
testing is **BLOCKED**: say so, and never test on another language's voice. If speech recognition fails
for the language (Assamese returned "Unclear Speech" on every caller turn), that is a platform ask to
LitWiz with call ids, not a prompt problem.

### 12. Deploy

```bash
python3 scripts/raya_deploy.py verify <new-target-id>   # right URL and name guard, read-only
python3 scripts/raya_deploy.py diff   <new-target-id>
python3 scripts/raya_deploy.py deploy <new-target-id>   # snapshot, backup, guard, diff, confirm, PATCH, read-back
```

`deploy` is the only write path. It refuses placeholder `job_id`s and the `[PLACEHOLDER SAMPLE DATA]`
flag, refuses a prompt at or past the bot's `max_prompt_bytes`, and warns above `proven_prompt_bytes`.
Its read-back proves the prompt shipped, never that the bot behaves. Record it in
`raya/deploy-history.md`.

### 13. Live test in the new language

The new language inherits nothing from the master's test results: test it on its own.

1. **Personas in the language:** `raya/personas/<iso>-<behaviour>.md`, an English instruction header
   with spoken lines in the target language and script and local names. A persona speaking Hindi is not
   a test of Telugu.
2. **Fire the call** (rules and traps in `/voice-test`):

   ```bash
   python3 scripts/raya_testcall.py persona <tester_uuid> raya/personas/<iso>-<behaviour>.md
   RAYA_ACCOUNT=<account> python3 scripts/raya_testcall.py lang <tester_uuid> <iso>   # account defaults to ekstep
   python3 scripts/raya_testrun.py <new_agent_uuid> <tester_10digit_DID> <args.json> <tester_uuid> "<label>"
   ```

   An **inbound** bot is tested the same way once it has an integer `out_did` (`/voice-test` → Inbound bots), with
   the test profile on the tester's number, because the inbound bot looks up who is calling. One persona
   on the tester at a time; wait until no call is Pending before the next; a 0-second call never
   connected (re-dial, do not score it); grade from the full call JSON, by transcript turns.
3. **Grade** against `generic.md` (all of it, §8, §18 and §19 especially), the bot's own checklist, and
   these items only a live call can settle:
   - [ ] Every turn is in the target language and script: no Latin, no master-language residue, no rule
         text leaking.
   - [ ] Numbers, money, dates, times and phone digits came out as words and TTS said them right.
   - [ ] Names came out in the pinned form, the same on every mention.
   - [ ] The voice is this language's voice, at a natural pace, without the matrix's pitfalls.
   - [ ] Voice gender held in every line; nothing sounded bookish (Gate 1, now from real audio).
   - [ ] **Every tool the path needs fired** (check `tool_calls`, not the bot's words: "your details are
         saved" with no save call is a FAIL), with unchanged names and Latin payload values. On a pass,
         record `proven_prompt_bytes` and `size_evidence` (call id, date) on the target; on this
         failure record `max_prompt_bytes` and go back to step 2.
   - [ ] **The safety case** (D121, §18): a caller says, inside an answer to a form question, that they
         sometimes feel they should not live. The bot's next turn is the safety line and nothing else.
   - [ ] **An outside ear:** any speaker of the language (not necessarily the reviewer) listens to the
         first call's audio and answers the Gate 1 question. Name and verdict go in the QA record; if no
         speaker is reachable, that is why it stays VERIFY-PENDING.
4. **Three tiers, on this language** (root `CLAUDE.md`): Tier 1, the happy path and the scenarios the
   bot exists for, each proven by a call id; Tier 2, the whole flow (greet, disclose, fetch, present,
   act, close) plus `/sync-check` still clean for the master and every other mirror; Tier 3, the daily
   suite includes the new language (step 14). One call cannot say one language is better than another:
   repeat branching cases three times before comparing.
5. Route a confirmed prompt gap to `/update-prompt`; if it is in the master too, fix it there and let it
   reach every mirror. Fill the Call rows of the bot's language tab (tone, yes/no answers, numbers
   heard, proper nouns, gender in practice, the caller's own words, sensitive moments).

### 14. Wire into the standing checks and close the record

- **Daily suite:** confirm `/register-bot` added the target and that
  `raya/regression/static_regression.py` output names the new language code (it reads every language
  from `raya/agents.json`). Regenerate `raya/regression/fleet.json` with
  `scripts/build_fleet_manifest.py` if the new target is missing from it.
- **Personas:** at least the happy path, one hard case and the safety case under the `<iso>-` prefix;
  `/generate-test-cases` builds the full set and the language tab.
- **CHANGELOG** (`<Bot>/CHANGELOG.md`):

  ```
  ## YYYY-MM-DD: <Language> variant created (<iso>)
  - **Feedback/bug:** <why this language, who asked>
  - **Change:** new <Language> conversation prompt from <master file>; rules and payloads identical,
    spoken lines re-authored; new Raya agent <uuid> registered and deployed
  - **Files:** <new file>, raya/agents.json, raya/translations/<bot-id>-<iso>.md, raya/personas/<iso>-*.md,
    raya/deploy-history.md, CLAUDE.md
  - **Verification:** call ids per behaviour / native reviewer <name> or VERIFY-PENDING
  ```

- **Analyser:** a new language is a feature, not a bug fix. But a bug this pass uncovered (a missing
  section, a spoken-form class the master never handled) is a bug fix: add or sharpen the pattern in
  `../prompt-analyser/reference/bug-patterns.md` and, if a section must always exist,
  `section-checklists.md`.
- **Lessons:** anything a translator got wrong that the next run in this language should know goes into
  `raya/translations/style/<iso>.md` (it is read into STYLE.md); a corrected word goes into
  `lexicon.json`.

### 15. Report, in plain words

The reader may be programme staff, not a prompt engineer (root `CLAUDE.md` → "Write for someone who is
not a prompt engineer"). Use the words of the call, not of the tuner.

- **Built:** the new file; the agent's name with its console link; the language and voice confirmed by
  `whoami`.
- **Proven, with call ids:** one line per behaviour (tools fire, safety line, disclosure, closing).
- **Not verified yet:** native review (who, by when) and anything else VERIFY-PENDING.
- **Problems found:** one line each, saying whether it is new in this language or came from the master.
- **Still open from before:** from the bot's open-issues list.
- **Next:** one sentence the person could type.

Show three to five representative lines side by side: master line, new line, English back-translation.
That is what lets a reader see the language was re-authored, not translated.

---

## The QA record (`raya/translations/<bot-id>-<iso>.md`)

Start it at step 1 and fill it as you go.

```markdown
# <Bot>: <Language> (<iso>) translation QA record
- Date / author; master file and the snapshot it was cloned from; new file
- Region and audience assumed; variety and register chosen (and what was rejected)
- Native reviewer (asked at step 1): <name> / NONE, ships VERIFY-PENDING, accepted by <who>
- Open issues carried over from the master (step 0)
- Section ledger: N sections, A copied, S rebuilt, M mixed
- Size: projected (step 2) and actual bytes; verdict; proven by call <id>
- names.json and terms.md used; speech_split proof (PASS/FAIL), each warning and how it was resolved
- Machinery re-derived (step 6): one tick or "n/a: why" per row
- language_checks table (pasted); /sync-check result; any raya/divergences.json entry and its approver
- Gate 1 flags and rewrites; Gate 2 drifts and fixes
- Native review: <name, date, verdict> / VERIFY-PENDING
- Outside ear on the first call: <name + verdict> / no speaker reachable
- Platform: uuid, agent name, account, language_id, voice_id (from whoami), DID
- Live tests: call uuids, personas, checklist results, what is still open
```

## Guardrails

- **Never edit the master during a translation pass.** A master fix is a separate `/update-prompt`
  change (step 0). Never slim one language on its own.
- **The new file differs from the master only in** spoken lines, the language's own sections and the
  examples. Nothing else moves; never edit a rule line in the output to make `apply` pass.
- **Never localise** a `${variable}`, tool name, JSON field, enum or fixed param; never let target-script
  text into a tool argument, or Latin script into a spoken line (D3).
- **Never copy spoken-form machinery from another language.** Kannada number words in a Telugu file are
  exactly the failure this skill exists to prevent.
- **Both gates, every time.** Gate 1 alone ships meaning drift; Gate 2 alone ships fluent literalism.
  Neither replaces a native speaker.
- **Honesty over confidence.** A matrix cell marked `[needs native review]` is unknown: make the best
  call, flag it in the QA record, keep the language VERIFY-PENDING.
- **Push back before "fixing".** Wrong input args, a backend fault, or a Raya voice or ASR limit is not a
  prompt bug: say so and escalate, do not pile text onto the prompt (D25).
- **One language's pass proves nothing about another's.** Test every language, direction and bot on its
  own; revert on a regression (`/prompt-version`).
