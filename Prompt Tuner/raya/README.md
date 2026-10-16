# raya/ — Agentic deploy to Raya Voice AI

This directory configures `scripts/raya_deploy.py`, which pushes the local prompt
files into the live voice agents on **Raya Voice AI** (LitWiz Labs, getraya.app)
over Raya's REST API — always against a verified-correct agent/URL.

Prefer the **`/deploy-prompt`** skill for day-to-day use; it wraps the tool with
the sync-check gate, snapshots, diffs, confirmation, and read-back verification.

## ⚠️ CAUTION — do NOT edit/reload/save the Raya console for these agents

Raya's **read path is broken/flaky**: the public `GET /api/agent/{id}` and the
console's on-load fetch often return **empty** instructions, so the console editor
falls back to its default **`"You are a helpful assistant"`** placeholder.

- **Reloading or opening an agent in the console, then Save (or an auto-save), OVERWRITES the live prompt with that placeholder — wiping it.** This happened once: maya-hi-in was clobbered to `"You are a helpful assistant"` on 2026-07-20 after a console reload, and was restored with `scripts/raya_deploy.py deploy maya-hi-in --yes`.
- **Never open, reload, or Save the Raya console for these agents while the read is broken.** Treat the console as display-only-and-unreliable.
- **Deploy ONLY via the API PATCH** (`scripts/raya_deploy.py` / `/deploy-prompt`). PATCH *writes* reliably and self-verifies via the PATCH **response echo**; when GET happens to return content, the tool's `diff: none — remote already matches local` is a bonus positive confirmation.
- **Recover a wiped agent:** `python3 scripts/raya_deploy.py deploy <target> --yes` re-asserts the repo prompt. `deploy --all` (or per-target) re-asserts everything.
- **Output prompt** deploys via the `output_instructions` field (also PATCH-able — same tool pattern). **Memory prompt** now deploys the same way too — via the `memory_instructions` field plus a `memory_enabled` boolean (same PATCH pattern), wired as the `memory` profile; pushing the memory prompt with the tool also sets `memory_enabled: true` (turning the feature ON). GET returns both fields cleanly.

## Reconcile-before-fix (the live agent can be AHEAD of the repo)

The team edits some things directly on the live console — most importantly the **real job inventory / `job_id`s** for the inbound agents (KKB/Maya Inbound), which is not a dependency on us. That makes the LIVE agent ahead of the repo. If you edit + deploy the repo blindly, you overwrite that live-only content — this is exactly how the real Maya Inbound inventory got replaced with placeholder `job_id`s, so every `apply_job` failed.

**Before ANY prompt change, reconcile first:**
1. `python3 scripts/raya_deploy.py diff <target>` — who is ahead? (GET now reads most conversation prompts; if it's flaky/empty, use `/raya-reconcile` via the browser.)
2. If **Raya is ahead**, adopt the live prompt into the repo: `python3 scripts/raya_deploy.py pull <target>` — it requires TWO agreeing GETs, rejects the empty / `"You are a helpful assistant"` default and implausibly-small reads, snapshots the repo file first, then writes live → repo. Review `git diff`, commit the reconciliation.
3. Only THEN apply your fix on top of the reconciled base, and deploy.

**Guardrail:** `deploy` **refuses** to push any prompt still carrying placeholder `job_id`s (`…000000000NNN`) or a `[PLACEHOLDER SAMPLE DATA]` flag — so a stale/sample inventory can never overwrite the real one. If you hit that refusal, `pull` the real inventory first.

## Files

| File | Tracked? | What |
|---|---|---|
| `agents.json` | yes | **The source of truth** — explicit file → Raya agent-ID manifest. Never inferred from filenames. |
| `endpoints.json` | yes | API shape (endpoints, auth, prompt-field). **No secrets.** Fill CAPITALISED placeholders from Raya's docs. |
| `.env.example` | yes | Keys for `raya/.env`, empty values. |
| `.env` | **no (git-ignored)** | Real base URL + token. Never commit. |
| `deploy-history.md` | yes | Append-only log of what went live, when, and the rollback snapshot. |

## Setup (once)

1. `cp raya/.env.example raya/.env` and fill `RAYA_BASE_URL`, `RAYA_API_TOKEN`, `RAYA_ENV`.
2. Fill the CAPITALISED placeholders in `endpoints.json` from the Raya REST API docs (checklist below).
3. `scripts/raya_deploy.py list` → copy each agent's ID into the matching `raya_agent_id.<env>` in `agents.json`.
4. `scripts/raya_deploy.py verify --all` → confirms every mapped URL resolves and the live agent name matches its guard.

## Commands

```
scripts/raya_deploy.py targets [--check]        # print the manifest; --check errors on missing deploy:true files (LOCAL, no network)
scripts/raya_deploy.py list                      # GET Raya agents so you can fill agents.json
scripts/raya_deploy.py verify [<target>|--all]   # resolve URL + GET each target; confirm it exists + name matches (READ-ONLY) — the "right URL" gate
scripts/raya_deploy.py diff   <target>|--all     # unified diff: local file vs live remote prompt (READ-ONLY)
scripts/raya_deploy.py status [--all]            # per-target: in-sync | drifted | unmapped | missing-file | unreachable
scripts/raya_deploy.py deploy <target>|--all     # GATED write path: snapshot → GET backup → name guard → diff → confirm → PUT → read-back
```

`<target>` = a manifest `id` (`kkb-hi-in`), a file basename, or an `agent[:lang][:dir]`
selector (`kkb`, `dkb:kn`, `kkb:hi:inbound`). `deploy` requires an interactive
confirmation (type the target id) unless `--yes` is passed after a human has approved.
`deploy --all` stops on the first failure — never a silent partial batch.

## Safety

- **Secrets never committed** — `.env` is git-ignored; `agents.json`/`endpoints.json` hold no secrets.
- **Explicit mapping, never filename inference** — the #1 wrong-URL risk (`KKB Placeholder Inbound.md` is *Hindi*).
- **Every deploy**: auto-snapshot (`prompt-version.sh save`) → GET current remote (a backup of what you're about to overwrite) → name guard → dry-run diff → confirm → PUT → **read-back verify** (remote must byte-equal local).
- **Rollback**: `scripts/prompt-version.sh restore <agent> <pre-deploy-label>` (auto-snapshots current first) → `scripts/raya_deploy.py deploy <target>`.
- **Staging vs prod** is selected by `RAYA_ENV`. Test the voice harness against **staging**, never a production line — the prompts fire live backend writes (`create_profile`/`apply_job`).
- **Sync gate**: never deploy one language of a drifted KKB/DKB pair — run `/sync-check` first (the `/deploy-prompt` skill does this).

## API details to get from LitWiz (fills `endpoints.json`)

- **Base URL(s)** — prod and **staging/sandbox** (staging is required for voice testing).
- **Auth** — Bearer token vs API-key header; exact header name; how the token is scoped/rotated.
- **List agents** — endpoint + method; response shape: where the array lives (`list_items_path`), the id field (`item_id_field`), the name field (`item_name_field`); pagination?
- **Get agent** — endpoint + method; **does a GET return the current live prompt?** (needed for verify/backup/diff); where the object sits in the response (`get_item_path`); which field (or dotted path) holds the prompt (`prompt_field`).
- **Update** — endpoint + method (PUT/PATCH); **replace vs patch** (`update_mode`); required fields on update; UTF-8/Devanagari+Kannada safety; max prompt size (largest file ≈ 84 KB → set `request.max_prompt_bytes`).
- **Topology** — are inbound/outbound and Hindi/Kannada **separate agent objects/IDs**? How are phone numbers bound to agents?
- **Post-call prompts** — where do **Memory/Output** prompts live (separate fields/objects, or not in Raya)? **Memory is now confirmed** — it lives on the SAME agent object as the conversation prompt, deployed via `memory_instructions` + `memory_enabled` (the `memory` profile), so the two Maya memory targets are now `deploy:true`. Output (`output_instructions`) and the remaining memory targets (KKB/DKB) stay `deploy:false` until their uuids are confirmed.
- **Ops** — rate limits; idempotency-key support; does Raya keep its own prompt version history?
