# What a production-ready tuner skill looks like

The bar every skill in `.claude/skills/` is held to, and the lessons from four months of running the
tuner that every skill must already know. Use it when writing a new skill, and when reviewing one.

## The bar

1. **It works as written.** Every command, script, flag, path and file it names exists and does what
   the skill says. Run `--help` or a read-only/dry run to check. A step that silently does nothing (an
   empty grep "passing", a hard-coded name that matches nothing) is the worst kind of bug.
2. **No stale facts.** Nothing that was true once and has since been corrected (see the lessons below).
   No hard-coded bot list (KKB/DKB/Maya), no hard-coded language pair (Hindi/Kannada), no "inbound can't
   be tested". Bots resolve through `raya/agents.json`, languages from its `language` codes.
3. **One source of truth.** A fact lives in one place (root `CLAUDE.md`, a reference file, a script's
   `--help`) and the skill points to it. Two copies drift; duplicated rules contradict each other.
4. **Consistent with the other skills.** Hand-offs name real skills; no two skills give opposite
   instructions; the order of steps matches `docs/WORKFLOW.md`.
5. **A clear start.** The `description` says when to use it, in the words a user would actually type.
   The top of the body says, in a few lines, what the skill produces and the fast path through it.
   Detail and history go lower down or into `reference/`.
6. **Usable by a non-specialist.** The person asking may be programme staff, not a prompt engineer.
   What the skill tells the user is in plain words (root `CLAUDE.md` → "Write for someone who is not a
   prompt engineer"). Internal vocabulary is fine inside the skill; it does not reach the user.
7. **Says how "done" is proved.** Every skill that changes something names the evidence that closes it
   (a call id, a lint pass, a read-back) and what to say when that evidence is missing
   (DEPLOYED, NOT VERIFIED / VERIFY-PENDING).
8. **Safe by default.** Never touches a real person's number or profile, never commits a secret,
   never overwrites someone else's work (live agent ahead of the repo, a filled-in sheet row), asks
   before anything visible to others.
9. **Lean.** Every paragraph earns its place. History ("on 2026-09-23 …") stays only where the story
   is the reason a rule exists, and then in one or two lines with the call id. Repetition is cut.

## Lessons every skill must already know

**Proving things**
- "Fixed" needs a call id and the line that proves it; otherwise DEPLOYED, NOT VERIFIED. One call per
  fix. Deploy + read-back proves the prompt shipped, never that the bot behaves.
- Test every variant on its own: each language, inbound and outbound, each bot. Never extrapolate.
- **Inbound bots ARE testable** (corrected 2026-09-02): PATCH the inbound agent with an integer
  `out_did`, then `POST /api/call` with the inbound agent as `agent_id` and the tester DID as
  `to_number`. Never write "inbound cannot be harness-dialled". The inbound bot looks up the CALLER's
  number, so inbound test data goes on the tester's number.
- Three tiers: the fix itself, the blast radius around it, and the daily standing check.
- "Intermittent" is not a result. Diagnose first (count how often the right branch ever happened,
  split by input, read the guard), then remedy. Two failed wordings means change mechanism, not volume.
  If a fix does not hold across three calls, stop adding text.
- A required tool parameter constrains what the model says, not what it did (D91, D95).
- Locate before you fix: trace the failing call to the section that produced its first wrong turn
  (`scripts/prompt_map.py locate`), and list what that section touches before editing it (`impact`).
- After two failed fixes on one issue, read the whole prompt cold (a fresh subagent, no history) and run
  `scripts/prompt_structure.py`: a rule the bot "ignores" is often a rule a stale step reference never
  lets it reach (D125).
- The prompt's own examples are a defect source: an example that shows the forbidden behaviour beats
  any rule against it (D50). Fix the example.

**Before changing anything**
- Reconcile with the live agent first (`raya_deploy.py diff` / `pull`); the live agent can be ahead.
- Snapshot first (`prompt-version.sh save`); deploy only through `raya_deploy.py` (read-back verified).
- Push back before fixing: wrong inputs, backend errors and platform limits are not prompt bugs. Say
  "the prompt is fine, the inputs were wrong" out loud. Sometimes there is no bug.
- No fix without a transcript. Reproduce before you report: no report made only of "maybe" causes.
- Read the bot's open-issues list first and update it last; group issues by cause and make one fix
  per cause; run a baseline sweep before the first fix.
- Every bug fix teaches the analyser (`bug-patterns.md`) and gets a `CHANGELOG.md` entry.

**Prompts**
- Instructions are always English; only spoken lines are in the call's language.
- Agnostic content is byte-identical across languages; spoken content is re-authored, never
  translated. Deliberate differences go in `raya/divergences.json`.
- The memory block `### Contact context / Here is the caller context: / {${contact_memory}}` is in every
  conversation prompt of a memory-enabled bot, verbatim.
- Surgical edits only; prefer deleting or replacing a line over adding one.
- Size is a per-bot limit; past it a bot stops calling tools without any error (D116,
  `scripts/prompt_size.py`, `max_prompt_bytes` / `proven_prompt_bytes` in `raya/agents.json`).
- A public-facing bot needs a safety interrupt that works even inside an answer (D121).

**Languages**
- `scripts/speech_split.py` (only spoken lines go to translators), `scripts/language_checks.py` (the
  prompt-level language checks), `raya/translations/lexicon.json` (everyday words, insulting words,
  gender and question rules), `raya/voices.json` (language and voice ids per account), `"account"` on a
  target for a second Raya account. A language is verified only after a named native speaker signs off.

**Testing harness**
- One tester agent holds one persona at a time; never overlap two test waves; wait for no Pending call
  before starting another; call creation is rate-limited; bridging flakes (a 0-second call never
  connected: re-dial, don't score it); `GET /api/call` and `call_output` lag; judge a call by its
  transcript turns, not `call_duration`; grade from the full call JSON.
- Test cases are delivered as a sheet in the house layout and must pass `scripts/testcase_sheet.py
  lint`; a sheet can be run and filled in (`pull` / `result` / `add-bug`). Sheets are read through the
  service account `kkb-sheets-writer@operation-rozgar.iam.gserviceaccount.com`, not a browser.
- Real users' numbers and profiles are read-only, always. Test numbers only.

**Copies of the tuner**
- Teams run their own copies; `/upgrade` (`scripts/tuner_upgrade.py`) is the only way shared machinery
  reaches them. Anything a skill adds must be safe to merge into a copy: no bot names, uuids or paths that
  only exist here.

**Repo hygiene**
- The repo is PUBLIC and every commit auto-pushes behind `scripts/push_guard.py`. Never commit
  `*.tools*.json` snapshots (they embed live keys), secrets, or a real person's phone number (cite the
  call uuid; mask as `XXXXXX1234`).

**Reporting**
- Short: Fixed (with call id) · Failed / still open · New bugs · Next. Plain words. Show the few prompt
  lines that changed. End with what is still open from before.
