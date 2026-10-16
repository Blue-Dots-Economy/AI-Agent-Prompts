"""Job prompts for the headless `claude -p` runs. They invoke the repo's own skills
(/bug-fix, /update-prompt, /voice-test) so all discipline is reused. Job A never
deploys (deploy is withheld from its allowlist); Job B deploys after approval/policy."""
from __future__ import annotations
import json


def _issue_block(scope: dict) -> str:
    i = scope.get("issue") or {}
    return (
        f"- Sheet issue title: {i.get('title')!r}\n"
        f"- Bot (target id): {scope.get('target_id') or i.get('target_id')}\n"
        f"- Priority: {i.get('priority')}   Type: {i.get('type')}   D-pattern hint: {i.get('d_pattern')}\n"
        f"- Reported description: {(i.get('description') or '')[:600]}\n"
        f"- Sheet issue_id: {i.get('issue_id')}\n"
    )


def diagnose_prompt(job_id: str, scope: dict, artifacts_dir: str) -> str:
    """Job A: find -> root-cause -> classify -> (fix) -> local verify -> write verdict. No deploy, no sheet write."""
    return f"""You are running the /bug-fix loop for ONE reported issue, in DIAGNOSE+FIX mode (NO deploy, NO sheet write).

## The issue
{_issue_block(scope)}

## Do exactly this (bug-fix skill steps 1-6), then STOP:
1. Root-cause it against a REAL Raya transcript for this bot (use scripts/raya_call.py <agent_uuid>). NO FIX WITHOUT A TRANSCRIPT — if no recent call reproduces it, classify as no-repro.
2. Classify: prompt-fixable | backend | runtime/tool-adherence | no-repro | verbiage | ops.
3. If and only if prompt-fixable: fix surgically via /update-prompt (Hindi source-of-truth, mirror to Kannada, preserve Maya divergences). Snapshot first with scripts/prompt-version.sh save. Reconcile first (scripts/raya_deploy.py diff <target>) — if live is AHEAD, do NOT edit; set a risk flag.
4. Verify nothing broke: sync-check parity + a contradiction/regression scan.
5. DO NOT run scripts/raya_deploy.py deploy. DO NOT write the Google Sheet. Those happen only after human/policy approval.

## Then WRITE these files (this is the contract the control center reads):
- `{artifacts_dir}/verdict.json` — EXACTLY this shape:
  {json.dumps({
    "classification": "prompt-fixable|backend|runtime|no-repro|verbiage|ops",
    "confidence": "high|medium|low",
    "risk_flags": ["e.g. reconcile-drift, regression, broad-propagation, large-diff, irreversible-config, no-repro, low-confidence"],
    "repro_call_uuid": "the Raya call uuid you grounded in (or null)",
    "target_ids": ["bots that would be deployed"],
    "sibling_ports": ["sibling bots the same fix should port to, if any"],
    "diff_stats": {"files": 0, "additions": 0, "deletions": 0},
    "summary": "one-paragraph plain-English what/why/how"
  }, indent=2)}
- `{artifacts_dir}/proposed-change.md` — human-readable: root cause, the exact change, why it's safe.
- `{artifacts_dir}/repro.txt` — the offending transcript turns you grounded in.
- Run `git -C "$PWD" diff > {artifacts_dir}/diff.patch` so the reviewer sees the exact diff.

Set risk_flags truthfully: NOT prompt-fixable, reconcile-drift, a failed verify, broad/agent-agnostic propagation, a large/non-surgical diff, an irreversible tool-config change, no reproducing transcript, or low confidence. An empty risk_flags on a clean prompt-fix means the control center may auto-deploy. Be honest — a wrong "safe" verdict ships a bad change.
Keep edits surgical. Summarize what you did LAST."""


def deploy_prompt(job_id: str, scope: dict, artifacts_dir: str) -> str:
    """Job B: deploy the already-made fix, post-deploy verify, write the sheet. Runs only after approval/policy-clear."""
    return f"""You are completing an APPROVED prompt fix: deploy it, verify, and update the tracker.

The fix has already been made and locally verified (see {artifacts_dir}/proposed-change.md and verdict.json).

## Do exactly this:
1. Reconcile once more (scripts/raya_deploy.py diff <target>); if live drifted since, STOP and report — do not clobber.
2. Deploy each target in verdict.json target_ids: `scripts/raya_deploy.py --env prod deploy <target> --yes` (it snapshots, name-guards, read-back-verifies, appends deploy-history.md). Confirm each is in-sync after.
3. Post-deploy verify: run ONE voice-test against the primary bot with the matching persona (scripts/raya_testcall.py persona/lang + scripts/raya_testrun.py) — this is best-effort; the line may be flaky.
4. Write the Google Sheet: set the issue's STATUS (column B) to `Fixed for UAT` via scripts/gsheets.py update, with a comment (root cause + call uuid + what changed + deploy date + "awaiting post-deploy call to confirm"). Re-resolve the row by matching date|bot|title before writing — row numbers shift.
5. Summarize LAST: what deployed, the post-deploy result, and that `Fixed for UAT` != confirmed."""


def propose_prompt(job_id: str, scope: dict, artifacts_dir: str) -> str:
    """Propose-only: diagnose + write verdict, make NO edits."""
    return diagnose_prompt(job_id, scope, artifacts_dir).replace(
        "in DIAGNOSE+FIX mode", "in PROPOSE-ONLY mode (make NO edits at all)"
    ) + "\n\n## OVERRIDE: Make NO file edits. Do not call /update-prompt or prompt-version.sh save. Only diagnose, classify, and write verdict.json + proposed-change.md + repro.txt describing what the fix WOULD be."


def voicetest_prompt(job_id: str, scope: dict, artifacts_dir: str) -> str:
    sc = scope.get("scenario") or {}
    return f"""Run a /voice-test of bot {scope.get('target_id')} for scenario {sc.get('title')!r}.
Use the tester agent (Testing Agent- Blue Dots). Load the matching persona (scripts/raya_testcall.py persona), match language (lang hi|kn), then fire+poll+dump (scripts/raya_testrun.py). Grade against .claude/skills/voice-test/reference/checklists. Write a graded summary to {artifacts_dir}/voice-test-result.md and, if you find a real prompt gap, note it (do NOT fix here). Respect the 4-min cap; the line is flaky — retry with cooldown."""


PROMPT_FN = {
    "diagnose": diagnose_prompt,
    "deploy": deploy_prompt,
    "propose": propose_prompt,
    "voice-test": voicetest_prompt,
}
