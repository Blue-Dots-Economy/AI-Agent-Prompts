# Improvement ideas — from the overnight run

As of ~03:00 IST 2026-07-30. These are forward-looking ideas to close the gaps the run hit (mostly harness + verification limits), plus demo-packaging notes. None of these are bugs — they are investments that would make the next test/fix loop faster and more complete. Nothing here is auto-applied.

## Testing harness

1. **Multiple tester DIDs → parallel scenario testing.** Today there is ONE tester DID, and the callee gets `agent_args={}`, so one persona runs at a time — parallel calls can only re-run the *same* scenario (concurrency itself is supported; scenario-parallelism is not). Provisioning 2–4 tester DIDs (each a distinct persona/scenario) would let a full regression suite run in parallel instead of the current ~13 s-rate-limited sequential queue, cutting a multi-scenario pass from many minutes to one round.

2. **A way to reset Signals test profiles.** Signals has **no delete route** today, so the tester-DID profile can't be returned to "new". That blocks re-testing every new-seeker Signals path (create_profile → live → apply) on the tester number — after the first run the profile exists forever. Ask the Signals/Admin team for a delete-or-reset endpoint (or a "test" flag that soft-deletes), OR keep a pool of throwaway dummy numbers reserved for new-seeker runs.

3. **Give the tester an `out_did` to harness-test inbound bots.** Inbound bots (KKB in Hi/Kn, DKB in, Maya in) can't be tested today because the tester agent can only RECEIVE. If the tester is given a spare outbound DID (`out_did`) it could DIAL an inbound bot's `in_did` and drive a full inbound scenario — which would let us verify tonight's inbound D31/D34 fixes (currently deploy-only, verify-pending) without waiting for a real human inbound call. Needs Parth's OK to modify the tester config + a spare `out_did`.

4. **Capture the Raya response-variable as a tool-schema backstop for create→apply.** The KKB-inbound apply-404 (D31) had a runtime tool-adherence residue: the model sometimes fabricated/empty the `profile_id` instead of reading it from the `create_profile` result. Prose alone can regress here (cf. analyser D25). The durable fix is a platform lever: have Raya **capture the `create_profile` response's `profile_id` into a response variable** that the `apply_job` step is required to consume — so the id can't be hallucinated. Same idea would harden Signals `create_profile → apply_job`. Raise with LitWiz as a schema/platform feature, not more prompt prose.

5. **Auto-grading via the tester's output prompt.** Each call is currently graded by re-reading the transcript against the 197-item checklists by hand. Give the *tester* agent its own output prompt that emits a structured pass/fail per checklist item (tool-fired? hold neutral? consent asked? job_id verbatim? gender re-asked?) as call variables — so a scenario run returns a machine-readable scorecard instead of a transcript to eyeball. Turns the harness into a real regression gate.

## Demo packaging

6. **Flows solid enough to demo now:**
   - **KKB Signals apply** (Hindi `115b38a5` + Kannada `33037201`) — the happy path is proven end-to-end on live calls: live-profile selection, relevance-filtered job list, consent line, `apply_job` success, Phase-2 enrichment, labelled end-confirm, graceful close (`b83e86de`, `b3ef7abe`). The role-update offer also demos well (`15e3f9d9`).
   - **KKB seeker happy path** (existing seeker) — returning-caller fetch → present → apply is stable across the Signals calls.
   - Keep the demo on a number whose Signals profile is already **live** (avoid the no-reset limitation): a returning-seeker "apply to Data Entry" script is the most reliable.

7. **Do NOT demo cold, and pre-flight these:** new-seeker Signals on a fresh number (no reset → hard to reproduce cleanly), any **inbound** flow (fixes deployed but unverified), and **Maya / KKB-Hindi-outbound** (no completed live call this run). If they must be shown, place one live probe first and confirm the tool calls fire.

8. **Ship a one-page "what's solid vs. what's pending" card with any demo** — mirror REPORT.md sections D (deployed) and F (coverage) so the audience knows which flows are verified vs. deploy-only-verify-pending. Prevents demoing an unverified inbound path as if it were confirmed.
