# voice-harness — automated call verification (and, later, auto-dialing)

The point of this directory is to stop verifying agent behaviour by eyeballing
transcripts. It has two halves:

- **Eval half (built, works today):** turn a *real* Raya call into an automated
  PASS/FAIL verdict against a scenario's assertions — from the actual transcript
  + `call_output` tool outcomes. No telephony, no LLM, Python stdlib only. Reuses
  `raya/.env` + `raya/agents.json` + the Raya call API.
- **Dialer half (needs prerequisites — see below):** place the call itself so the
  loop is fully automatic. Blocked on accounts/keys you provision.

## Eval half — `verify_call.py`

```bash
# most recent call on an agent, checked against a scenario
python3 voice-harness/verify_call.py maya-hi-in \
    --scenario voice-harness/scenarios/maya-inbound-mpl.json

# a specific call by uuid
python3 voice-harness/verify_call.py --uuid <call-uuid> \
    --scenario voice-harness/scenarios/maya-inbound-mpl.json

# no scenario — just the facts (MPL offered? age asked? drop_reason? …)
python3 voice-harness/verify_call.py maya-hi-in --facts
```

Exit code `0` = all non-info checks passed, `1` = at least one failed. `--json`
prints a machine-readable verdict (for a cron / the future dialer to consume).

### Workflow it unblocks (today)
1. You place a test call to an agent.
2. `verify_call.py <agent> --scenario <s>` pulls that call and returns a verdict
   tagged to bug-pattern classes (D9, D10, …) — instead of me reading the
   transcript by hand.
3. A FAIL routes to `/update-prompt` → deploy → **re-verify the next call** — a
   measured hit-rate, not a guess. Run a scenario over N calls to get a pass-rate
   (the catalog's "confirm on a live call, don't declare victory once" lesson).

### Scenarios — `scenarios/*.json`
A scenario is `{name, agent, checks:[...]}`. Each check is deterministic:

| type | params | observed |
|---|---|---|
| `transcript_any` | `patterns[]`, `expect` | any pattern in the AGENT turns |
| `transcript_user` | `patterns[]`, `expect` | any pattern in the USER turns |
| `output_truthy` | `field`, `expect` | `bool(call_output[field])` |
| `output_equals` | `field`, `value` | `call_output[field] == value` |
| `output_ge` | `field`, `value` | `call_output[field] >= value` |

Each check may carry `id`, `desc`, `bug_pattern`, and `severity` (`error` default,
or `info` to report without failing). Deterministic-only by design: a fuzzy,
STT-ambiguous check should be `severity:info` or a future LLM-eval type, never a
hard FAIL (false-positive suppression).

## Dialer half — what you need to provision

The eval half verifies calls; it does not place them. To close the loop fully
(the harness dials, converses in Hindi/Kannada, asserts, and re-tests after a
fix), these are the blockers — none of which I can create:

- **Telephony:** an **Exotel** (or Plivo) account with an **Indian DID** + DLT
  registration, and bidirectional **media streaming over WebSocket**.
- **Speech:** **Sarvam** API keys (Saarika STT + Bulbul TTS — best Hindi/Kannada).
- **A host** for the real-time runner (an ap-south-1 / Mumbai box, or ngrok for dev).
- **Anthropic API key** for the per-turn caller-brain + an offline evaluator.
- **A staging Raya agent + test-only DID** — the bots write real records
  (`apply_job`/`create_profile`) to the ONEST registry, so test calls must hit a
  **shadow agent on a sandbox backend**, never a production line, or the loop
  pollutes production data.

Once those exist, the runner (Exotel WS ⇄ Sarvam STT ⇄ Claude caller-brain ⇄
Sarvam TTS) drops in and feeds the same `verify_call.py` verdicts. Secrets go in a
git-ignored `voice-harness/.env`; scenarios stay tracked.

> Note the current blocker the eval half already exposes: **`apply_failed`** —
> every apply is failing at the backend (`applications_count: 0`), which turns
> each call into a failure loop. That's a backend fix, upstream of any prompt or
> test work.
