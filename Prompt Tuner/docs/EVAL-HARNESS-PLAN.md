# Eval harness for Blue Dots voice agents: build plan

Response to Amar's `bluedots_agent_spec` (Confluence, 28 Oct 2026). Written 29 Oct 2026.
Shared copy: https://docs.google.com/document/d/1QSIRuR1GJMvpv05_KgWwJ-VRJjxpzvWTL633r-ZfH4I (update that doc in place).

## The short answer

Not all of it is easy. The spec splits into three kinds of work:

| Kind | Share of the spec | Needs from others |
|---|---|---|
| **A. Measure what we already record.** Golden set, domain grounding, rubric judge, safety, task outcome, connection and first-response timing, end reasons, words per second, the agent's speech-recognition error rate, spend caps | about half | the agri knowledge base and a signed-off golden set |
| **B. Read the agent's own telemetry.** Tool calls, retrieved passages, per-stage timings | about a sixth | VoicERA's per-call metrics API access; Kenpath installs a small package |
| **C. An eval agent that speaks over audio streams.** `wss://` calls, the AI4Bharat caller voice, noise and packet loss, timed barge-ins, two-channel recording, barge-in and overlap metrics, and the whole calibration table | about a third | `wss://` URLs and tokens, a sandbox agent, speech endpoints and their quotas |

A is configuration and scripting on top of what the tuner already has. B is a small integration. C is real
engineering: a new caller with its own audio pipeline, and it cannot be bolted onto the current caller,
which is a Raya agent on a phone line that we cannot time, mix noise into or record in two channels.

## The design: one tuner, two kinds of caller

Everything after the call stays shared. Only the way a call is placed changes.

```
  test cases (sheet / golden set) ──▶ CALLER ─────────────▶ CALL RECORD ──────▶ GRADERS ──▶ reports
                                      │                     (one format)        (shared)    sheet, digest,
                                      ├ phone: Raya tester  turns + timestamps               email, issues
                                      │  (today)            per channel,
                                      └ stream: eval agent  tool events,
                                         over wss:// (new)  telemetry, audio
                                                ▲
                          AGENT TELEMETRY ──────┘  VoicERA metrics API · eval-telemetry package (Kenpath)
```

- **The call record** is the contract. Today each harness writes its own shape (`raya_testrun.py`, the
  VoicERA `bench.py`). Step 1 defines one JSON format: turns with start and end times per channel, the
  caller's script and what the agent heard, tool events, retrieved passages, the agent's stage timings,
  the audio files, and which caller and noise profile produced it. Both callers write it; every grader
  reads only it.
- **The graders** are the tuner's existing checks plus the new metric modules. A grader that needs data
  a caller cannot provide reports SKIP with the reason, never PASS (the tuner's existing rule).
- **The prompt tuner supports every step**, through the skills people already use (see "In the tuner"
  below), so a programme person can say "run the golden set on the Marathi agri bot with the noisy
  personas" and get a sheet and a report back.

## Phases

### Phase 1: the conversation layer and the cheap call metrics (A)

| Deliverable | How |
|---|---|
| Call record format + a converter for both existing harnesses | `eval/call_record.py`; `raya_testrun.py` and `raya/voicera/bench.py` write it |
| Golden set as a sheet tab: question, expected answer, knowledge-base reference, must-not-say | `/generate-test-cases` adds a "Golden set" tab; `testcase_sheet.py lint` checks it |
| Domain grounding: each factual claim in the agent's answer checked against the knowledge base | `eval/grounding.py`: retrieve from the KB, judge each claim supported / contradicted / not in KB |
| Rubric judge: correctness, groundedness, language and register fit, escalation | `eval/judge.py` with a written rubric per bot; the score names the turn it is about |
| Safety as a hard fail; task outcome per call | existing safety and tool checks, reported per run as pass rate and distribution |
| Connection rate and setup time; time to first agent audio; end reason in the spec's 11 categories | from call attempts and the recording; end reason classified from the last turns and the call outcome |
| Agent speech recognition: WER, CER, entity error rate, language detected | the caller's script against what the agent heard (Raya bots expose it; VoicERA via its transcript) |
| TTS speaking rate against the configured target | words per second per agent turn, from the recording alignment |
| Spend caps | a per-run budget of calls and minutes; the run stops at the cap |

Done when: a golden-set run on one Blue Dots bot produces a report with every Phase 1 metric and a call
id behind every number. **Can start today on the Raya bots, before any agri input arrives.**

### Phase 2: agent telemetry (B)

| Deliverable | How |
|---|---|
| VoicERA adapter | read `GET /api/v1/calls/{id}/metrics` (speech-recognition, LLM and TTS first-byte times, turn detection, tool durations) into the call record |
| `eval-telemetry`, a small PyPI package for the agent's host (Kenpath) | three calls: `tool_call(name, args, result, ms)`, `retrieved(chunks)`, `turn(stage, ms)`; it posts to a collector with the call id; off by default, no caller audio, no personal data |
| Collector | a small HTTPS endpoint that stores events per call id; the call record joins them after the call |
| Graders that use it | right tool with right arguments; right passage retrieved; per-stage latency split |

Done when: one VoicERA call shows its tool calls and stage timings in the call record, joined by call id.

### Phase 3: the audio eval agent (C)

| Deliverable | How |
|---|---|
| A caller that connects over `wss://` and over phone (CPaaS) | built on Pipecat (VoicERA is Pipecat, so its stream format is already supported); the persona drives an LLM; the caller hears through its own speech recognition |
| Caller voice from AI4Bharat models | through the Bhashini TTS API first (no GPU to run); self-hosted Indic Parler-TTS later if quotas bite |
| Behaviour script per test case | barge in at a set time, pause N seconds, repeat a question, go silent, ask for a human: scheduled, not left to the LLM |
| Noise and line conditions | mix noise into the caller's audio by profile (animals, machinery, traffic, from open sound sets) at a set level; drop or delay frames for packet loss |
| Two-channel recording with exact timestamps | the caller writes its own and the agent's audio as separate tracks, so no alignment guessing |
| Speech metrics | turn latency per caller turn, barge-in stop time, no-stop and resumed rates, overlap and cut-in rate, words per second, agreement between the agent's transcript and ours |
| The eval agent's own delays | logged per turn and excluded from the agent's numbers |

Done when: the same golden set runs over `wss://` against a VoicERA sandbox agent with two noise profiles
and a barge-in schedule, and the report shows every speech metric.

### Phase 4: calibration (C)

A reference "offline agent" we control (a Pipecat bot that replies with known delays, overlaps at set
moments and records exactly what it received). Running the eval agent against it measures the eval agent
itself: injected against measured latency, barge-in timing, overlap, protocol conformance (frame size,
rate, codec, no dropped frames), its own audio quality, graceful call end, and transcript agreement.
**The speech metrics are not trusted on a real agent until the calibration run passes**, the same way a
tuner fix is not "fixed" without a call id.

## In the tuner

| Today | After this plan |
|---|---|
| `/generate-test-cases` writes test rows and personas from the prompt | also writes the golden set from the knowledge base, and gives each row a behaviour script and a noise profile |
| `/voice-test` places calls through the Raya tester | `--caller phone` (today) or `--caller stream` (the eval agent); same sheet, same grading, same report |
| graders read Raya call JSON | graders read the call record, so they work on any agent, on any platform |
| VoicERA benchmark lives apart in `raya/voicera/` | becomes a preset of `/voice-test`: two targets, same personas, comparison report |
| daily static check plus weekly live sweep | the same schedule, plus "after every vendor change" (open question 1) |
| no self-check of the harness | `/voice-test calibrate`: the Phase 4 run, required before speech metrics are reported |
| `docs/WHAT-YOU-CAN-ASK.md` | new plain sentences: "run the golden set on the agri bot", "test it with tractor noise", "how fast does it stop when the farmer interrupts?" |

The pieces that are general (call record, graders, eval agent, telemetry package) go into the shared
tuner, so every copy (Purple Dots, Orange Dots) gets them through `/upgrade`.

## What we need, and from whom

| Need | From | Blocks |
|---|---|---|
| Agri knowledge base, and the golden set signed off with PoCRA / OAN | programme team | Phase 1 grounding and golden set (everything else in Phase 1 can start now) |
| Call recordings and transcripts as scenario seeds | VoicERA / Kenpath | better scenarios; not blocking |
| Access to VoicERA's per-call metrics API | VoicERA | Phase 2 adapter |
| Kenpath installs `eval-telemetry` on the tool host | Kenpath | Phase 2 tool and retrieval grading |
| `wss://` URLs with tokens, a sandbox agent, test numbers | VoicERA | Phase 3 |
| Speech endpoints (ASR, TTS) with rate limits and quotas | VoicERA / Bhashini | Phase 3 caller voice and our own transcript |
| A small server for the eval agent and the collector (not GitHub Actions: calls need a long-running process) | EkStep | Phase 2 collector, Phase 3 |

## Proposed answers to the open questions

1. **Run cadence:** both. The cheap Phase 1 checks nightly; the full audio run after every vendor change
   and weekly.
2. **Golden set refresh and hidden subset:** refresh monthly and whenever the KB changes; keep 20% hidden
   from the vendor so a tuned-to-the-test agent shows up.
3. **Spend caps:** per run (calls, minutes, LLM tokens) and per month, set in the run config; the harness
   stops at the cap and says so in the report.

## Risks

- **Our own caller adds delay.** Until Phase 4 passes, speech timings carry the eval agent's own error.
  The report says so on every speech number.
- **Bhashini quotas** may limit how many calls a run can make with the AI4Bharat voice.
- **Kenpath adoption** of the telemetry package is outside our control; without it, tool and retrieval
  grading falls back to judging from the transcript, and is marked as inferred.
