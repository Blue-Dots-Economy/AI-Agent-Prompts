# Regression harness (Tier-3 daily standing check)

The third testing tier (see repo `CLAUDE.md` → "The three testing tiers"): a standing regression that
runs automatically and mails critical findings, so drift is caught even when nobody is looking.

**Cadence (user-chosen 2026-08-01): daily static + weekly live.** Digest → **parth@ekstepplus.org**.

## Daily — static suite (fast, reliable, no telephony)
`python3 raya/regression/static_regression.py` checks EVERY conversation prompt for the failure classes
we've actually hit, and writes:
- `latest-report.md` — human-readable
- `latest-report.json` — machine-readable; the `critical` array drives the email digest

Checks (tuned for precision — a noisy daily email is worse than none):
- **cross-backend leakage** — a Signals prompt carrying a Dhiway contract token (`up-getjob`, `ONEST-AGENT`,
  `*.dhiway` host, …) or a Dhiway prompt carrying a Signals contract token (`item_state`, `lifecycle_status`,
  `educationCategory`, `compliance`, …). Contract-only tokens (never appear in "never-speak-these-fields" bans).
- **phone-doubling** — the `+91${contact_phone}` (Dhiway) / `91${contact_phone}` (Signals) templates that make
  the model double the country code (the CD6 class).
- **memory-injection block** — the verbatim `{${contact_memory}}` must be present.
- **enum-drift** — the byte-exact Signals Phase-2 enums (`ITI / Other Vocational Trainings`, `3-5 Years`, …);
  a wrong enum 400s the write.
- **missing sections** — Graceful Exit; seeker bots need `get_profile`; DKB needs `create_job`.
- **Hindi↔Kannada sync-drift** — header-skeleton parity per pair.

## Runtime (behaviour) checks — `run_runtime_checks.sh`

`raya/regression/run_runtime_checks.sh [--since YYYY-MM-DD] [--agent <id>]` runs every detector that
reads **real call transcripts** rather than prompt text:

| Detector | What it catches |
|---|---|
| `location_chain.py` | the Location step as a CHAIN: confirm the supplied location (C1/C2), ask the bus-stop/station/landmark question exactly once per caller — required when `nearest_landmark` is absent from memory (C3), forbidden when it is present (C4) — never bundled with another question (C5), and never after the job list (C6). This is the owner-specified flow of 2026-09-01 made checkable instead of judged. |
| `location_reconfirm.py` | the campaign sent a `location` and the bot asked openly anyway (A), claimed jobs exist in a place holding none (B), or never told the caller their place has no jobs (C). Also reports the campaign-targeting signal: how many callers were dialled for a city we hold no inventory in. |
| `apply_result_integrity.py` | one call saying both "the apply didn't go through" and "the apply is done" (X); a narrated write with no `update_profile`/`create_profile` call (Y); the success line with no successful tool result (Z). |
| `apply_failure_wording.py` | the failure line not matching the error, and any line that diagnoses a cause. |
| `location_integrity.py` | a profile written with a location the caller never gave. |
| `apply_outcomes.py` | which caller-facing line was spoken for each real backend failure reason. |

### Runtime checks are NOT in the daily digest yet — this is the gap that hid the 2026-09-01 bugs
The daily GitHub Actions job runs **`static_regression.py` only**, by design: it runs on GitHub's infra
with **zero secrets**, and every detector above needs `RAYA_API_TOKEN` to read call transcripts. So no
*behaviour* check runs unattended. That is why "the location input was ignored" and "already-applied
said the generic line" reached us through a QA WhatsApp message instead of the daily email — there was
nothing looking, not a broken digest.

**Two ways to close it, and the choice is Parth's:**
1. **Put `RAYA_BASE_URL` + `RAYA_API_TOKEN` in GitHub Actions secrets** and add a second daily job that
   runs `run_runtime_checks.sh`. This is the only option that survives the dev machine being off.
   Note the repo is **public**: Actions secrets are not exposed to fork PRs, but a token in a public
   repo's CI is still a deliberate decision, not a default.
2. **Run it locally on a schedule** (launchd / `scheduled-tasks` MCP). No secret leaves the machine, but
   it only runs while the machine is on — which is the requirement that ruled local schedulers out in
   the first place.

Until one is chosen, run it by hand after every behaviour change; the `/bug-fix` and `/voice-test`
skills both call for it.

### The deeper half of the same gap: the detectors need TRAFFIC, and nothing was generating it

Even run by hand, every detector above is a reader. It can only find a fault on a bot that somebody
happened to call. Production traffic is uneven — on 2026-09-04 the Kannada outbound bot took 500 calls
and DKB took three — so a bot with no campaign that day is effectively unchecked however often the
detectors run. That is the other reason this week's regressions were found by hand: not only was
nothing looking unattended, nothing was *dialling*.

**`raya/overnight/overnight_sweep.py` closes that half.** It generates the traffic and then hands it
to these same detectors:

```bash
python3 raya/overnight/overnight_sweep.py --hours 6     # run it overnight
python3 raya/overnight/overnight_sweep.py --dry-run     # print the queue, dial nothing
```

- **Phase A** — 28 cases covering **all 18 testable bots** (every conversation target with a prod
  uuid). Per case it PATCHes the tester agent's persona and language, triggers the bot to dial the
  tester DID, and records the bot-leg uuid. The persona/fixture pair for each case is chosen to walk
  the part of the flow that has actually broken before, not a happy path.
- **Phase B** — the static suite, `toolschema_parity.py`, every detector in this directory with
  `--since <sweep start>`, and `fab_rate.py --append`. The detectors grade the traffic phase A just
  made, so a rule still only has to be written once, here.
- **Loop** — repeat until the deadline. Re-testing the same bot across passes is what turns "one
  lucky clean call" into a rate, which is the only honest way to read an intermittent fault.

Output lands in `raya/overnight/sweep-<date>/`: `calls.tsv` (one row per attempt), `pass-<n>.txt`
(detector output), and `REPORT.md`, rewritten after every pass so a partial night is still readable.

**Known limits.** One tester DID means phase A is strictly serial: ~4-5 minutes per case, and the
bridge rate depends on how long the line has been idle (19% at 30-90s, 62% after 10 minutes idle —
measured over 115 dials, see `raya_testrun.CONNECT_BACKOFF`). Budget ~2 hours per pass and expect
some cases to report `NO-BRIDGE` rather than a finding. `dkb-hi-in` / `dkb-kn-in` have no prod uuid
and are skipped. It needs `raya/.env`, so like the detectors it cannot run in the zero-secrets CI
job — it is the thing you start before going to bed, not a substitute for choosing option 1 or 2
above.

## Weekly — live voice regression (sampled)
A fuller live pass over more bots via the tester agent + the `/voice-test` checklists (generic + bot-specific).
Not daily (one tester = serial calls; 100+ live calls/day isn't feasible). The weekly routine picks a rotating
set of bots, fires the harness calls, grades, and appends live findings to the digest.

## The scheduler — GitHub Actions (`.github/workflows/regression.yml`)
The requirement was "runs even if my system is shut off." The two **local** schedulers can't do that:
`scheduled-tasks` MCP only runs "while this app is open"; `CronCreate` is "session-only, gone when Claude
exits." The only mechanism that survives the dev machine being off is a **cloud** runner — and since this
repo is on GitHub (`parthekstep/Prompt-Tuner`), that's **GitHub Actions**: it runs on GitHub's infra, checks
out the repo, runs the suite with **zero secrets**, and notifies.

### What actually runs, and when (as of 2026-08-04)
- **One job, once a day.** Cron `7 1 * * *` (nominally 06:37 IST). **GitHub's shared cron queue delays
  scheduled runs** — observed arrival ~04:20–04:40 UTC (~09:50–10:10 IST), i.e. up to ~3.5 h late. Treat the
  time as "each morning", not a guaranteed clock time. Anything time-critical should not depend on this.
- **Every run checks all 16 bot scripts.** No per-bot rotation, no sampling, no ordering — one pass over the
  full inventory (8 KKB, 4 DKB, 4 Maya). Runtime ~6 s.
- **No run ever places a phone call.** This tier reads scripts only.
- **The weekly live voice regression does not exist yet** — no live-call script, and the Raya/Signals keys
  aren't in repo secrets. A second `7 1 * * 1` cron used to sit here; because it matched the same minute as
  the daily one, Mondays fired **twice** (observed 2026-08-03 04:35:58Z + 04:37:09Z = duplicate emails). It
  has been removed. When the live test is built it gets its own job at its own distinct time.
- `workflow_dispatch` — manual "Run workflow" button, any time.

Two independent email paths:
1. **Guaranteed, zero-config** — on any critical finding the job **exits non-zero**, so GitHub emails the repo
   owner about the failed run; the run page shows the full digest (`build_digest.py` → job summary + artifact).
2. **Well-formatted HTML email** (`send_digest.py`) — multi-provider, auto-detected from whichever secret is
   present. Skipped cleanly (exit 0) when none is set, so the workflow never fails just because email isn't
   wired up. Priority order:

| # | Provider | Secrets | Needs Workspace admin? |
|---|---|---|---|
| 1 | **Gmail API as you** (OAuth refresh token) | `GMAIL_OAUTH_CLIENT_ID` + `_CLIENT_SECRET` + `_REFRESH_TOKEN` | **No** — your own consent |
| 2 | **Resend** HTTP API | `RESEND_API_KEY` | No — no Google at all |
| 3 | **Generic SMTP** (app password, Mailgun, SES…) | `SMTP_HOST/_PORT/_USER/_PASS` | No (app passwords can be org-blocked) |
| 4 | Service account + domain-wide delegation | `GMAIL_SA_JSON_BASE64` | **Yes** — admin must grant `gmail.send` |

`build_digest.py [daily|weekly]` renders `latest-report.json` to HTML; `send_digest.py` sends it;
`test_email.py` does a one-command local end-to-end send using `secrets/*`.

### ✅ LIVE — Gmail via Google Cloud Console (set up 2026-08-03, no admin needed)
Provider #1 is **configured and verified end-to-end**: the daily cloud run emails the digest to
parth@ekstepplus.org, sent as parth@ekstepplus.org.

- GCP project `operation-rozgar`; Gmail API **enabled**; OAuth consent screen app
  *"Prompt Tuner Regression Digest"*, audience **Internal** (deliberate: an External app in testing mode
  expires refresh tokens every 7 days, which would silently break the daily digest).
- OAuth client (Desktop) `prompt-tuner-regression-digest`, client id `1066399042934-…`; single scope
  `gmail.send` (send only — no mailbox read access).
- Repo secrets `GMAIL_OAUTH_CLIENT_ID` / `_CLIENT_SECRET` / `_REFRESH_TOKEN` are set.
  Local copies: `secrets/gmail-oauth.json` + `secrets/oauth-client.json` (git-ignored, chmod 600).
- Verified: local send → inbox ✓, and cloud run 30816144239 "Email digest" step → inbox ✓
  (subject `[Prompt Tuner] Daily regression — 0 critical, 0 major`).

To redo it (new project, rotated token, or a different sender), the steps are:

1. **console.cloud.google.com** → pick/create a project (e.g. `operation-rozgar`)
2. *APIs & Services → Library* → enable **Gmail API**
3. *OAuth consent screen* → **Internal** (or External + add yourself as a Test user); add scope
   `https://www.googleapis.com/auth/gmail.send`
4. *Credentials → Create credentials → OAuth client ID* → **Desktop app** → **Download JSON**
5. `python3 raya/regression/setup_gmail_oauth.py ~/Downloads/client_secret_*.json`
   — opens a browser for consent, stores the refresh token in `secrets/gmail-oauth.json` (git-ignored), and
   offers to set the three GitHub secrets via `gh`. The token is never printed.
6. Test end to end: `python3 raya/regression/test_email.py`

`GMAIL_SENDER` / `GMAIL_TO` override the from/to (both default to `parth@ekstepplus.org`).
For Resend without a verified domain, the from-address **must** be `onboarding@resend.dev`.

- **Weekly live** needs the Raya token + Signals keys as GitHub secrets to fire real calls from the cloud
  (they're git-ignored locally by design). Until then the weekly run is static-only.
