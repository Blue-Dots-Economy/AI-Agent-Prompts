# Bot Intake Summary

> Filled by `/onboard`, saved to `raya/intake/<bot-id>.md` (existing target id for a bot we already
> have; a short key unique across projects for a new one). Write **TBD** for anything not known yet: a
> TBD is a to-do, not a blocker. Sections 1 to 7 are what the person told us, in their words. Section 8
> is for the tuner and is filled from our own look-ups. The issue table in 7 is the bot's
> **open-issues list**: every later fixing or testing session reads it first and updates it last.

- **Date:**
- **Onboarded by:**
- **Project:**  <!-- kebab slug + label: blue-dots / Blue Dots, purple-dots / Purple Dots, orange-dots / Orange Dots -->
- **Bot key:**  <!-- short, lowercase, unique across projects; used in issue ids and target ids, e.g. od, pd -->
- **Branch:** A (we already look after it) | B (new bot)
- **Daily report email(s):**  <!-- passed to the tuner owner for the GMAIL_TO secret; told: cloud checks every morning, live overnight calls need the laptop on -->

## 1. What the bot does
- **Bot name / persona:**
- **What it does, and the goal of one call:**
- **Who is on the other end:**
- **Direction:** the bot phones people (outbound) | people phone the bot (inbound) | both
- **Public-facing?** yes / no  <!-- yes = a safety interrupt is required (analyser D121) and a safety test case per language -->

## 2. How it should speak to callers (access needs)
> Shapes how the bot speaks; never a topic the bot raises. "Nothing special" is a valid answer.

- **In their words:**
- **Needs:**  <!-- slower pace, patient with pauses, repeat on request, short turns, spoken menu, no rushed decisions -->

## 3. Languages
- **Languages it speaks today:**
- **Main language (edited first):**
- **Languages wanted but not built yet:**  <!-- each is a /translate-prompt job -->

## 4. Prompts
- **Conversation prompt per language:**  <!-- pasted, or file path -->
- **Memory prompt (remembers callers)?** yes / no
- **Output prompt (writes up the call)?** yes / no

## 5. Platform
- **Runs on Raya?** yes / no  <!-- not Raya: we can review, design tests and translate; no deploy, no test calls -->
- **Name(s) on Raya:**

## 6. What a good call looks like
| Scenario | What makes it a good call |
|---|---|
|  |  |

## 7. Open issues
> One row per issue. `issue-id` = `<bot-key>-i<NN>`, in the order raised, never renumbered or reused.
> `where` = the affected target ids, listed (never "all languages"). `severity`: blocker · major ·
> minor · wish. `status`: reported → repro-confirmed | no-repro | not-a-prompt-bug: data-input /
> backend / runtime-adherence → fixed-for-uat → verified (a post-deploy call per affected version).
> Reused by `/generate-test-cases` (repro persona `raya/personas/<lang>-repro-<issue-id>.md`) and
> `/voice-test` (run label `repro-<issue-id>-<target-id>`).

| issue-id | symptom (one line, what the caller hears) | where (target ids) | trigger | expected | actual | call-ref (id + date) | severity | status | proving call (id + date) |
|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |

## 8. For the tuner (from our own look-ups; do not ask the person for these)
- **Proposed target ids:**  <!-- <bot-key>-<iso>-<out|in>[-<variant>], e.g. od-hi-out -->

| target id | prompt file | language (ISO) | direction | name on Raya | Raya uuid (from `raya_deploy.py list`, by name) | in_did / out_did (`raya_testcall.py whoami`) |
|---|---|---|---|---|---|---|
|  |  |  |  |  | `<FILL BY HAND>` |  |

- **Language + voice ids per language** (`whoami`; goes in `raya/voices.json`):
- **Raya account** (if not the default):
- **Tools the bot calls** (read off the live agent; never save the tool JSON in the repo):

| Tool | What it does | Values that must never change | Known quirks |
|---|---|---|---|
|  |  |  |  |

- **Prompt size (bytes, `wc -c`)** per file:
- **Backend tag:** signals | other | none
- **Bot role:** seeker | provider | service-navigator | other
- **Reproduction verdicts (Step 2):**  <!-- one line per issue: id → status → call id → next -->
- **Next action:**  <!-- /register-bot · /voice-test · /bug-fix · /translate-prompt · /update-prompt -->
