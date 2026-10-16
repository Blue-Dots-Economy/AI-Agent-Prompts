---
name: onboard
description: Friendly first conversation with a NEW user, team or project bringing a voice bot to the Prompt Tuner (Blue Dots, Purple Dots, Orange Dots, a ministry or partner team). Asks a few plain questions one at a time (which project, what the bot does, who the callers are, which languages, the prompt, what a good call looks like, what is going wrong, who gets the daily report), looks up the technical details on Raya itself, writes each reported problem down as its own numbered issue, saves it all to raya/intake/<bot-id>.md (the bot's open-issues list), reproduces each issue on a real call before anyone fixes anything, and hands off to /register-bot (which then builds the test-case Google Sheet). Use when someone says "I have a voice bot I want to improve", "help me get started", "onboard my bot", "we are building a new bot", "here is our bot's prompt and the problems callers complain about", "here are the issues we want fixed", or you don't yet know which bot they mean.
---

# Onboard: welcome a new bot or a new team

**What it produces**
1. `raya/intake/<bot-id>.md`: a filled intake summary (template: `reference/intake-template.md`). Its
   issue table is the bot's **open-issues list** from now on.
2. A verdict on every reported issue, from a real call: reproduced, not reproduced, or not a prompt
   problem (and why).
3. One clear next step, said in a sentence the person could type.

**Fast path**
1. Say what the tuner does, in three lines (below).
2. Ask the questions in *The questions*, **one at a time**. Look the technical details up yourself.
3. Read the summary and the issue list back; save it to `raya/intake/<bot-id>.md`.
4. Step 2: reproduce each issue on a real call.
5. Hand off (normally `/register-bot`), then point them to `docs/WHAT-YOU-CAN-ASK.md`.

**Onboarding changes nothing on the bot.** It does not edit a prompt, `raya/agents.json`, or the
customer's live agent. It writes only the intake file, and for Step 2 the tester's persona file and
the tester agent (our own agent, never theirs).

---

## How to talk (the person is usually not a prompt engineer)

Follow root `CLAUDE.md` → "Write for someone who is not a prompt engineer". In practice:

- **One question at a time.** Ask, wait, say thanks in a few words, ask the next. Never show the list.
- **Plain words.** No "agnostic", "payload", "target id", "uuid", "adherence", "D-number" unless they
  used it first. Say "the bot's main language", not "master"; "the bot's instructions", not "prompt",
  if they look unsure.
- **Do not explain how the tuner works** unless asked. One short line on why you are asking is enough.
- **"I don't know" is a fine answer.** Write TBD and move on; most technical facts you can look up.
- **Promise a test, not a fix.** "We will reproduce that on a real call first." Some problems turn out
  to be wrong inputs or a backend fault, and we say so rather than change the bot.

**What to say first** (in your own warm words, three lines at most): we take your voice bot and make
it better from real calls; we test it by having another AI phone it and checking what it said; we fix
what goes wrong and prove each fix with a call; and we can take it into new languages.

---

## Step 1: The questions

Ask these in order, one at a time. Most people answer in under ten minutes.

| # | Ask (plain words) | Record as | Look up yourself instead of asking |
|---|---|---|---|
| 1 | "Which project or team is this bot for?" (Blue Dots, Purple Dots, or a new name is fine) | `project` (kebab-case, e.g. `orange-dots`) | |
| 2 | "What is the bot called? If you know its name on Raya, that helps." | bot name | Whether we already have it: match the name against `agent` / `raya_name` in `raya/agents.json`. Found → **Branch A**. Not found → **Branch B**. |
| 3 | "What does the bot do, and who is on the other end of the call?" | job, callers, goal of one call | Inbound or outbound: ask only if it is not clear ("does the bot phone people, or do people phone it?"). |
| 4 | "Is there anything about how it should speak to these callers? Slower, patient with pauses, happy to repeat?" | access needs ("nothing special" is a fine answer) | |
| 5 | "Which languages does it speak, and which one is the main version? Any language you would like it to speak that it doesn't yet?" | languages, master, wanted languages | |
| 6 | "Could you paste the bot's instructions (its prompt), or tell me where the file is?" Then: "Does it also have a separate prompt that remembers callers, or one that writes up the call afterwards?" | prompt files; memory / output prompts | Size: `wc -c` on the file (recorded later by `/register-bot`). |
| 7 | "Describe one or two calls that went the way you want. What made them good?" | test scenarios and what success looks like | |
| 8 | "What is going wrong today?" | issue records, one at a time (see below) | |
| 9 | "Who should get the daily test report by email?" | digest email address(es) | |

Then look up on your own (read-only, from `scripts/`):
- **Raya agent ids**: `python3 scripts/raya_deploy.py list` prints `<uuid>  <name>`; match by name,
  one per language and direction. Never guess an id from a file name. Two similar names: ask.
- **Phone numbers, language and voice**: `python3 scripts/raya_testcall.py whoami <uuid>` (prints
  `in_did`, `out_did`, `language_id`, `voice_id`).
- **Tools the bot calls**: read them off the live agent (console, or a GET of the agent). Ask the person
  only for values that must never change and quirks they know about. Never save the tool JSON in the
  repo: it carries live keys.
- **Public-facing?** If members of the public call it or are called by it, note
  `public-facing: yes`. Such a bot needs a safety interrupt (a caller in distress, even mid-answer);
  `/prompt-analyser` (D121) checks it and `/generate-test-cases` adds a safety case per language.
- **Not on Raya?** Tell them plainly: we can still review and improve the prompt, design test cases and
  translate it; we cannot deploy it or place test calls, so fixes need real call transcripts from them.

**About the daily report, say one line:** "The written checks run every morning in the cloud and email
you; live test calls run overnight only while this laptop is switched on." (The email list is the
`GMAIL_TO` repository secret; only the tuner owner can add an address, so record it and tell them.)

**Access needs (question 4) shape how the bot speaks, never what it talks about.** The bot never
raises, names or asks about a caller's disability or condition. They are graded on every bot
(`generic.md` §14) and become this bot's accessibility cases (`/generate-test-cases`, family `X`).

### Branch A: a bot we already look after

Quick. Confirm which versions they mean (language and direction) and read them back by name. Then
read the bot's open-issues list (`raya/intake/<bot-id>.md`, or the tracker sheet if the bot has one)
and say how many issues are open. Add only what is new: a fresh issue, a scenario, a language wanted.
A language the bot does not speak yet is a `/translate-prompt` job; note it.

### Branch B: a new bot

Ask all nine. If they run short of time, see *Minimum to start*.

---

## Writing down each issue

Every problem they report becomes **one record with its own id**, so "is issue 3 fixed?" has a real
answer later. Take them one at a time; a paragraph of complaints cannot be tested.

**Id:** `<bot-key>-i<NN>` (`od-i01`, `pd-i03`). One id per symptom, even if it happens in three
languages. Assigned in the order raised; never renumbered or reused; lowercase.

**Fields** (TBD allowed everywhere except *symptom* and *where*):

| Field | What goes in it |
|---|---|
| `issue-id` | You assign it and read it back: "let's call that one `od-i01`". |
| `symptom` | One line, what the caller hears: "the bot asks for the phone number twice" (not "memory is broken"). |
| `where` | Each affected version, by language and direction (you map these to target ids). Never "all languages". "Not sure" is fine. |
| `trigger` | How to make it happen: new or returning caller, the inputs that matter, the point in the call. |
| `expected` / `actual` | One line each. |
| `call-ref` | Raya call id(s) and date. "None yet" is fine at intake; it blocks the fix, not the intake. |
| `severity` | `blocker` (call fails, wrong action, wrong data saved) · `major` (works but badly) · `minor` (wording) · `wish` (a feature request; say so kindly). |
| `status` | Starts at `reported`. |

**Status ladder:** `reported` → `repro-confirmed` | `no-repro` | `not-a-prompt-bug: data-input |
backend | runtime-adherence` → (after a fix is deployed) `fixed-for-uat` → `verified` (a post-deploy call
per affected version proves it). `fixed-for-uat` is not confirmed. If the issue is also a row in the
tracker sheet, use the same id there.

---

## Save the summary

Fill `reference/intake-template.md` and save it as `raya/intake/<bot-id>.md` (create the folder if
needed). For a Branch A bot use its existing target id as `<bot-id>`; for a new bot use a short key
that is unique across projects (`od`, `pd`). Show it, and **read the issue table back line by line**:
that is what they will hold us to.

---

## Step 2: Reproduce the issues (before anyone edits anything)

Start the moment they confirm the summary. One reproduction per issue, per affected version, in
severity order. Full mechanics, platform limits and the tester setup are in `/voice-test`; do not
restate them here.

1. **Existing call first (free).** If they gave a call id, find it in
   `python3 scripts/raya_call.py <bot_uuid> [limit]` (prints the inputs, tool calls and transcript).
   Read the call's inputs (`agent_args`) as well as the words: many reported bugs are wrong inputs.
2. **Otherwise place a call** with a persona built from the `trigger` (`/voice-test`; the persona goes
   in `raya/personas/<lang>-repro-<issue-id>.md`, the run label is `repro-<issue-id>-<target-id>`).
   **Inbound bots are testable too:** the inbound agent needs an integer `out_did`, then it dials the
   tester (`/voice-test` → Inbound bots). If their agent has no `out_did` yet, setting one changes their live agent:
   ask first. The inbound bot looks up the caller's number, so its test data goes on the tester's number.
   Never use a real caller's number or profile.
3. **Grade** against `.claude/skills/voice-test/reference/checklists/generic.md` plus the bot's own
   checklist if it has one.
4. **Every affected version separately.** A repro in one language says nothing about another.
5. **Classify honestly, and push back when it is not the prompt:**
   - real prompt gap → `repro-confirmed` → `/update-prompt` (or `/port-feature` if a sibling bot has the fix)
   - inputs were wrong → `not-a-prompt-bug: data-input`; say "the prompt is fine, the inputs were wrong"
   - backend error or bad data on the server → `not-a-prompt-bug: backend`; escalate
   - the bot ignores a rule the prompt already states clearly → `not-a-prompt-bug: runtime-adherence`;
     do not pile on more words (root `CLAUDE.md` → diagnose first, then the remedy ladder)
   - did not happen → `no-repro`; ask for a call id that shows it. **Never fix on a hunch.**
6. **Report one line per issue:** id → status → call id → what happens next. Update the issue table.

---

## Minimum to start

If they are short of time, three things are enough: what the bot does, the prompt (one language is
fine), and one example of a good call. Add the project name (one word) and, if something is broken,
one issue record (symptom + where + trigger). Mark the rest TBD and tell them, in one line each, what a
missing piece would unlock (a Raya name lets us test; a call id lets us fix; the main language lets us
translate).

---

## Hand-off (where onboarding ends)

Route by what they need (the full chain is `docs/WORKFLOW.md`; point there, do not explain it):

- **New bot** → **`/register-bot`**. It files the bot so every tool can find it, then runs
  `/prompt-analyser` and `/generate-test-cases` on its own. **What the person gets:** a Google Sheet of
  test cases in the house layout (the exact words a tester says, the exact line the bot should say back,
  how to tell pass from fail, a safety case and a language tab per language), plus a short list of risks
  found in the prompt. Then `/voice-test` runs the first calls (we confirm before dialling).
- **Existing bot** → `/voice-test` for a first graded call, or `/bug-fix` if their issues are rows in the
  tracker sheet.
- **A language it does not speak yet** → `/translate-prompt` (it checks size, translates only the spoken
  lines, runs the language checks and registers the new version).
- **Reproduced issues** → `/update-prompt` (or `/port-feature`). Each fix is proved by its own call.
- **Issues that did not reproduce, or are not prompt problems** → hand back the verdict, not a fix.
- **A digest email** → tell the tuner owner to add it to the `GMAIL_TO` secret; say it was passed on.

Close with: what happens next and who does it (one line), then two or three sentences from
`docs/WHAT-YOU-CAN-ASK.md` they can type next, for example "make the test cases for this bot", "run the
test cases in this sheet, three calls each", "show me exactly what you changed". Then stop.

From here on, `raya/intake/<bot-id>.md` is the bot's open-issues list: every fixing or testing session
reads it first and updates it last (`/bug-fix` → four habits).
