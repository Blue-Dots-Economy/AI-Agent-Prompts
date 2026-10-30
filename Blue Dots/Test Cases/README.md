# Test cases for the Blue Dots voice agents

One file per agent family. Each row is one test: what part of the call it covers, what the tester says, and what the agent must do. They are written for the agents in this repository and run on any voice platform.

| File | Agent |
|---|---|
| [KKB Inbound and Slim.csv](KKB%20Inbound%20and%20Slim.csv) | Kaam Ki Baat, the job-seeker agent ([KKB-Slim](../KKB-Slim)), inbound and outbound |
| [KKB Outbound.csv](KKB%20Outbound.csv) | Kaam Ki Baat, the earlier outbound campaign agent ([KKB](../KKB)) |
| [DKB.csv](DKB.csv) | Dhandhe Ki Baat, the employer agent ([DKB](../DKB)) |
| [Maya.csv](Maya.csv) | Maya, the campus-recruitment agent ([Maya](../Maya)) |
| [TRRAIN.csv](TRRAIN.csv) | TRRAIN, the follow-up agent ([TRRAIN](../TRRAIN)) |

## Columns

| Column | Meaning |
|---|---|
| # | Test id |
| Phase | The part of the call being tested, in the agent's own order |
| Scenario | What is being tested |
| What the tester should say | The exact words, in the agent's language. Text in [square brackets] says how to start the call or set up the case |
| Expected Response | What the agent must say and do, with the pass criteria |
| Language, Direction | Hindi or Kannada; inbound, outbound or both |
| Type | **Smoke**: run first, proves the agent works end to end. **Manual**: full coverage. **Stress**: silence, noise, talking over the agent, changing topic, long answers |
| Priority | **P0**: breaks the call or misleads the caller (an invented or wrong job, "applied" when it was not, wrong data saved, consent skipped). **P1**: a visible quality problem. **P2**: polish |

To record results, copy a file into a spreadsheet and add three columns: Actual response, Verdict (Pass, Fail, Partial, Blocked, Not tested) and Notes (call time and the last four digits of the number you called from).

## Before you start

1. Test only on a test copy of an agent, or from phones that are never real users. An application or a posting made during a test is real: it creates a real record on the jobs registry.
2. Keep one test phone with no record on the registry, for the new-caller cases.
3. Check every call in the voice platform's call log, not only what was said: the tool calls between the turns show whether a lookup ran, whether consent was saved and whether an application really went through.
4. Where a test case and the agent's current prompt disagree, the prompt is correct. Some DKB opening lines here were written before the 26 October 2026 update that lets one DKB agent take inbound and outbound calls.
