#!/usr/bin/env python3
#
# raya_deploy.py — push local prompt files into the live voice agents on
# Raya Voice AI (LitWiz Labs, getraya.app) over Raya's REST API.
#
# Read-only, safe anytime:
#   scripts/raya_deploy.py targets [--check]        # print the manifest (LOCAL, no network)
#   scripts/raya_deploy.py list                      # GET Raya agents so you can fill agents.json
#   scripts/raya_deploy.py verify [<target>|--all]   # resolve URL + GET each target; the "right URL" gate
#   scripts/raya_deploy.py diff   <target>|--all     # unified diff: local file vs live remote prompt
#   scripts/raya_deploy.py status [--all]            # in-sync | drifted | unmapped | missing-file | unreachable
#
# Gated write path:
#   scripts/raya_deploy.py deploy <target>|--all [--yes] [--dry-run]
#     snapshot -> GET (backup) -> name guard -> diff -> confirm -> PUT -> read-back verify
#
# <target> = a manifest id (kkb-hi-in), a file basename, or an agent[:lang][:dir]
#            selector (kkb, dkb:kn, kkb:hi:inbound). deploy --all stops on first failure.
#
# Config: raya/endpoints.json (API shape, no secrets), raya/agents.json (file->id
# mapping), raya/.env (RAYA_BASE_URL, RAYA_API_TOKEN, RAYA_ENV — git-ignored).
# Reuses scripts/prompt-version.sh for pre-deploy snapshots. Stdlib only.

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAYA_DIR = os.path.join(REPO_ROOT, "raya")
# Config paths default to raya/ but can be overridden (alternate/staging config, tests).
ENDPOINTS_PATH = os.environ.get("RAYA_ENDPOINTS") or os.path.join(RAYA_DIR, "endpoints.json")
AGENTS_PATH = os.environ.get("RAYA_AGENTS") or os.path.join(RAYA_DIR, "agents.json")
ENV_PATH = os.environ.get("RAYA_ENV_FILE") or os.path.join(RAYA_DIR, ".env")
HISTORY_PATH = os.environ.get("RAYA_HISTORY") or os.path.join(RAYA_DIR, "deploy-history.md")
VERSION_SH = os.path.join(REPO_ROOT, "scripts", "prompt-version.sh")

PLACEHOLDER_RE = re.compile(r"^[A-Z][A-Z0-9_]{3,}$")  # e.g. AGENTS_LIST_PATH, SYSTEM_PROMPT_FIELD


# ----------------------------------------------------------------------------- helpers

def die(msg):
    sys.stderr.write("error: %s\n" % msg)
    sys.exit(1)


def load_json(path):
    if not os.path.exists(path):
        die("missing config: %s" % path)
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        die("invalid JSON in %s: %s" % (path, exc))


def load_env():
    env = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                env[key.strip()] = val.strip().strip('"').strip("'")
    for key in ("RAYA_BASE_URL", "RAYA_API_TOKEN", "RAYA_ENV"):
        if not env.get(key) and os.environ.get(key):
            env[key] = os.environ[key]
    return env


def redact(text, token):
    if token and text:
        return text.replace(token, "****")
    return text


def dotted_get(obj, path):
    if path in (None, "", "."):
        return obj
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def dotted_set(obj, path, value):
    parts = path.split(".")
    cur = obj
    for part in parts[:-1]:
        if not isinstance(cur.get(part), dict):
            cur[part] = {}
        cur = cur[part]
    cur[parts[-1]] = value


def seg_is_placeholder(seg):
    return bool(PLACEHOLDER_RE.match(seg))


def path_has_placeholder(path):
    for seg in str(path).strip("/").split("/"):
        if seg in ("",) or (seg.startswith("{") and seg.endswith("}")):
            continue
        if seg_is_placeholder(seg):
            return True
    return False


def field_is_placeholder(field):
    return field is None or bool(PLACEHOLDER_RE.match(str(field).strip()))


def normalize(text):
    if text is None:
        return None
    # strip leading + trailing blank lines: the Raya console prepends a blank line to
    # the stored instructions, so a byte-exact compare would false-flag as drift.
    return text.replace("\r\n", "\n").strip("\n")


def fingerprint(text):
    data = text.encode("utf-8") if isinstance(text, str) else text
    return len(data), hashlib.sha256(data).hexdigest()[:8]


def resolve_profile(endpoints, name):
    profiles = endpoints.get("profiles", {})
    prof = profiles.get(name)
    if prof is None:
        die("unknown profile '%s' in endpoints.json" % name)
    if "inherits" in prof:
        base = resolve_profile(endpoints, prof["inherits"])
        merged = dict(base)
        for key, val in prof.items():
            if key != "inherits":
                merged[key] = val
        return merged
    return dict(prof)


# ----------------------------------------------------------------------------- manifest

def load_targets():
    manifest = load_json(AGENTS_PATH)
    targets = manifest.get("targets")
    if not isinstance(targets, list) or not targets:
        die("no targets in %s" % AGENTS_PATH)
    return targets


def agent_id_for(row, env_name):
    ids = row.get("raya_agent_id", {})
    if isinstance(ids, dict):
        return (ids.get(env_name) or "").strip()
    return str(ids or "").strip()


def resolve_selector(targets, selector):
    """Resolve a selector to a list of manifest rows.

    selector: exact id | file basename | agent[:lang][:dir] | None/--all handled by caller.
    """
    sel = selector.strip()
    # exact id
    hits = [t for t in targets if t["id"] == sel]
    if hits:
        return hits
    # file basename (with or without .md)
    base = sel[:-3] if sel.endswith(".md") else sel
    hits = [t for t in targets if os.path.basename(t["file"]) in (sel, base + ".md")]
    if hits:
        return hits
    # agent[:lang][:dir] selector — tokens after the agent are order-free:
    # a 2-letter language code (hi, kn, mr, te, ...) or xx is read as language; in/out as direction.
    parts = [p for p in sel.lower().split(":") if p]
    agent = parts[0] if parts else ""
    lang = None
    direction = None
    for tok in parts[1:]:
        if tok in ("in", "inbound", "out", "outbound"):
            pass
        elif re.fullmatch(r"[a-z]{2}", tok):
            lang = tok
        if tok in ("in", "inbound"):
            direction = "inbound"
        elif tok in ("out", "outbound"):
            direction = "outbound"

    def match(t):
        if t["agent"].lower() != agent:
            return False
        if lang and t.get("language", "").lower() != lang:
            return False
        if direction and t.get("direction", "").lower() != direction:
            return False
        return True

    hits = [t for t in targets if match(t)]
    if hits:
        return hits
    die(
        "no target matches '%s'. Try an id (e.g. kkb-hi-in), a filename, or an "
        "agent[:lang][:dir] selector (e.g. kkb, dkb:kn, kkb:hi:inbound).\n"
        "Known ids: %s" % (selector, ", ".join(t["id"] for t in targets))
    )


def selected_rows(targets, args, include_undeployable=False):
    if getattr(args, "all", False):
        rows = targets
    elif getattr(args, "target", None):
        rows = resolve_selector(targets, args.target)
    else:
        die("specify a <target> or --all")
    if not include_undeployable:
        rows = [r for r in rows if r.get("deploy", False)]
        if not rows:
            die("no deployable targets selected (deploy:false rows are skipped)")
    return rows


# ----------------------------------------------------------------------------- http

def base_url_or_die(env):
    base = (env.get("RAYA_BASE_URL") or "").strip().rstrip("/")
    if not base:
        die("RAYA_BASE_URL is empty — set it in raya/.env (copy raya/.env.example).")
    return base


def auth_header(endpoints, env, row=None):
    auth = endpoints.get("auth", {})
    token_env = auth.get("token_env", "RAYA_API_TOKEN")
    # A bot on another Raya account carries "account" in agents.json; its key lives in raya/.env as
    # RAYA_API_TOKEN__<ACCOUNT>. Switching keys by hand made a moved bot fail as "agent not found".
    if row and row.get("account"):
        token_env = "RAYA_API_TOKEN__" + re.sub(r"\W", "_", row["account"]).upper()
    token = (env.get(token_env) or "").strip()
    if not token:
        die("no API token — set %s in raya/.env%s." % (token_env, " (target %s is on account '%s')"
                                                       % (row["id"], row["account"]) if row and row.get("account") else ""))
    scheme = auth.get("scheme", "")
    value = ("%s %s" % (scheme, token)).strip() if scheme else token
    return {auth.get("header", "Authorization"): value}, token


USER_AGENT = "Mozilla/5.0 (compatible; raya-deploy/1.0; +prompt-tuner)"


def api(method, url, headers, token, body_obj, timeout, retries):
    hdrs = dict(headers)
    hdrs.setdefault("User-Agent", USER_AGENT)
    hdrs.setdefault("Accept", "application/json")
    data = None
    if body_obj is not None:
        data = json.dumps(body_obj, ensure_ascii=False).encode("utf-8")
        hdrs["Content-Type"] = "application/json; charset=utf-8"
    attempts = (retries + 1) if method == "GET" else 1
    for attempt in range(attempts):
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
                parsed = json.loads(raw) if raw.strip() else {}
                return resp.status, parsed, raw
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", "replace")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = None
            return exc.code, parsed, raw
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt < attempts - 1:
                time.sleep(1.0 * (attempt + 1))
                continue
            reason = getattr(exc, "reason", exc)
            die("network error calling %s: %s" % (redact(url, token), redact(str(reason), token)))


# ----------------------------------------------------------------------------- remote ops

def require_endpoint_configured(prof, keys):
    """keys: subset of ('list','get','update','prompt_field'). Die with guidance if unfilled."""
    for key in keys:
        if key == "prompt_field":
            if field_is_placeholder(prof.get("prompt_field")):
                die(
                    "prompt_field is still a placeholder in endpoints.json — fill it from the "
                    "Raya API docs (the field/dotted-path that holds the system prompt)."
                )
            continue
        ep = prof.get(key, {})
        if not ep.get("path") or path_has_placeholder(ep["path"]):
            die(
                "the '%s' endpoint is still a placeholder in endpoints.json — fill it from the "
                "Raya API docs before running network commands. See raya/README.md." % key
            )


def build_url(base, ep, agent_id=None):
    path = ep["path"]
    if agent_id is not None:
        path = path.replace("{id}", urllib.request.quote(str(agent_id), safe=""))
    return base + path


def fetch_remote(base, endpoints, env, headers, token, row):
    """GET a target's live agent object; return (url, agent_obj, remote_prompt, live_name)."""
    prof = resolve_profile(endpoints, row.get("profile", "conversation"))
    require_endpoint_configured(prof, ("get", "prompt_field"))
    env_name = env.get("RAYA_ENV", "staging")
    agent_id = agent_id_for(row, env_name)
    if not agent_id:
        die("target '%s' has no raya_agent_id for env '%s' — fill raya/agents.json (see `list`)."
            % (row["id"], env_name))
    url = build_url(base, prof["get"], agent_id)
    timeout = endpoints.get("request", {}).get("timeout_s", 30)
    retries = endpoints.get("request", {}).get("read_retries", 2)
    if row.get("account"):
        headers, token = auth_header(endpoints, env, row)
    status, parsed, raw = api(prof["get"]["method"], url, headers, token, None, timeout, retries)
    if status == 404:
        die("GET %s returned 404: agent %s not found on account '%s'. If this bot moved to another Raya account, set "
            "\"account\" on target '%s' in raya/agents.json and RAYA_API_TOKEN__<ACCOUNT> in raya/.env."
            % (redact(url, token), agent_id, row.get("account", "default"), row["id"]))
    if status >= 300 or parsed is None:
        die("GET %s returned HTTP %s\n%s" % (redact(url, token), status, redact(raw, token)[:800]))
    agent_obj = dotted_get(parsed, prof.get("get_item_path", ""))
    if agent_obj is None:
        die("could not find the agent object at get_item_path='%s' in the GET response for %s"
            % (prof.get("get_item_path", ""), row["id"]))
    remote_prompt = dotted_get(agent_obj, prof["prompt_field"])
    live_name = dotted_get(agent_obj, prof.get("item_name_field", "name"))
    return url, agent_obj, remote_prompt, live_name


def read_local(row):
    path = os.path.join(REPO_ROOT, row["file"])
    if not os.path.exists(path):
        die("local file missing: %s (target %s)" % (row["file"], row["id"]))
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if not text.strip():
        die("local file is empty: %s (target %s)" % (row["file"], row["id"]))
    return text


def name_guard_ok(row, live_name):
    tokens = row.get("expected_name_contains", [])
    if not tokens:
        return True
    if not live_name:
        return False
    low = str(live_name).lower()
    if not any(tok.lower() in low for tok in tokens):
        return False
    return not other_language_in_name(row, live_name)


_LANG_NAMES = {"hi": "hindi", "kn": "kannada", "mr": "marathi", "te": "telugu", "ta": "tamil", "ml": "malayalam",
               "bn": "bengali", "gu": "gujarati", "pa": "punjabi", "or": "odia", "as": "assamese", "ur": "urdu"}


def other_language_in_name(row, live_name):
    """The live agent's name names a DIFFERENT language than the target's (e.g. a Hindi prompt about to be
    PATCHed onto "KKB Placeholder- Kannada Signals API"). expected_name_contains matches ANY token, so a
    shared token like "KKB" or "Signals" alone never protected against a language swap."""
    lang = row.get("language")
    if lang not in _LANG_NAMES:
        return None
    low = str(live_name).lower()
    for code, name in _LANG_NAMES.items():
        if code != lang and re.search(r"\b%s\b" % name, low):
            return name
    return None


# ----------------------------------------------------------------------------- commands

def cmd_targets(args, endpoints, env):
    targets = load_targets()
    env_name = env.get("RAYA_ENV", "staging")
    print("# manifest (raya/agents.json) — env: %s" % env_name)
    print("%-13s %-8s %-9s %-13s %-7s %s" % ("id", "deploy", "lang/dir", "agent-id", "file?", "file"))
    problems = 0
    for t in targets:
        path = os.path.join(REPO_ROOT, t["file"])
        exists = os.path.exists(path)
        deployable = t.get("deploy", False)
        agent_id = agent_id_for(t, env_name) or "-"
        file_ok = "ok" if exists else "MISSING"
        if deployable and (not exists):
            problems += 1
        print("%-13s %-8s %-9s %-13s %-7s %s" % (
            t["id"], "yes" if deployable else "no",
            "%s/%s" % (t.get("language", "?"), (t.get("direction", "?")[:3])),
            agent_id, file_ok, t["file"]))
    unmapped = [t["id"] for t in targets if t.get("deploy") and not agent_id_for(t, env_name)]
    if unmapped:
        print("\nunmapped (deploy:true, no id for env '%s'): %s" % (env_name, ", ".join(unmapped)))
    if args.check:
        if problems:
            die("%d deployable target(s) point at a missing file." % problems)
        print("\nOK: every deploy:true target's file exists.")


def cmd_list(args, endpoints, env):
    base = base_url_or_die(env)
    headers, token = auth_header(endpoints, env)
    prof = resolve_profile(endpoints, "conversation")
    require_endpoint_configured(prof, ("list",))
    url = build_url(base, prof["list"])
    timeout = endpoints.get("request", {}).get("timeout_s", 30)
    retries = endpoints.get("request", {}).get("read_retries", 2)
    status, parsed, raw = api(prof["list"]["method"], url, headers, token, None, timeout, retries)
    if status >= 300 or parsed is None:
        die("list %s returned HTTP %s\n%s" % (redact(url, token), status, redact(raw, token)[:800]))
    items = dotted_get(parsed, prof.get("list_items_path", ""))
    if not isinstance(items, list):
        die("could not find an array at list_items_path='%s'. Raw response:\n%s"
            % (prof.get("list_items_path", ""), redact(raw, token)[:1200]))
    id_field = prof.get("item_id_field", "id")
    name_field = prof.get("item_name_field", "name")
    print("# Raya agents (%d) — copy each id into the matching raya_agent_id.%s in agents.json"
          % (len(items), env.get("RAYA_ENV", "staging")))
    print("%-40s %s" % ("id", "name"))
    for it in items:
        print("%-40s %s" % (str(dotted_get(it, id_field)), dotted_get(it, name_field)))


def cmd_verify(args, endpoints, env):
    base = base_url_or_die(env)
    headers, token = auth_header(endpoints, env)
    targets = load_targets()
    rows = selected_rows(targets, args)
    env_name = env.get("RAYA_ENV", "staging")
    ok = True
    for row in rows:
        print("== %s  (%s)" % (row["id"], row["file"]))
        agent_id = agent_id_for(row, env_name)
        if not agent_id:
            print("   UNMAPPED: no raya_agent_id for env '%s' — fill agents.json" % env_name)
            ok = False
            continue
        url, agent_obj, remote_prompt, live_name = fetch_remote(base, endpoints, env, headers, token, row)
        local = read_local(row)
        guard = name_guard_ok(row, live_name)
        rlen, rsha = fingerprint(remote_prompt or "")
        llen, lsha = fingerprint(local)
        synced = normalize(remote_prompt) == normalize(local)
        print("   url:        %s" % redact(url, token))
        print("   agent-id:   %s" % agent_id)
        print("   live name:  %s   [name guard: %s]" % (live_name, "OK" if guard else "MISMATCH"))
        print("   remote:     %d bytes  sha256:%s" % (rlen, rsha))
        print("   local:      %d bytes  sha256:%s   -> %s"
              % (llen, lsha, "in sync" if synced else "DRIFTED"))
        if not guard:
            ok = False
    if not ok:
        die("one or more targets failed verification (unmapped or name-guard mismatch).")


def cmd_diff(args, endpoints, env):
    import difflib
    base = base_url_or_die(env)
    headers, token = auth_header(endpoints, env)
    targets = load_targets()
    rows = selected_rows(targets, args)
    any_drift = False
    for row in rows:
        url, agent_obj, remote_prompt, live_name = fetch_remote(base, endpoints, env, headers, token, row)
        local = read_local(row)
        if normalize(remote_prompt) == normalize(local):
            print("== %s: in sync" % row["id"])
            continue
        if len((remote_prompt or "").strip()) < max(200, len(local) // 5):
            # An empty or stub GET is an unreadable live prompt, not proof of drift (pull already refuses it).
            any_drift = True
            print("== %s: UNREADABLE — the GET returned %d chars vs %d local; not a diff. Re-run, or use "
                  "/raya-reconcile's browser path." % (row["id"], len((remote_prompt or "").strip()), len(local)))
            continue
        any_drift = True
        print("== %s: DRIFTED (remote %s vs local %s)" % (row["id"], row["file"], row["file"]))
        diff = difflib.unified_diff(
            (remote_prompt or "").splitlines(keepends=True),
            local.splitlines(keepends=True),
            fromfile="remote:%s" % row["id"],
            tofile="local:%s" % row["file"],
        )
        sys.stdout.writelines(diff)
        print("")
    if not any_drift:
        print("all selected targets in sync.")


def cmd_status(args, endpoints, env):
    base = base_url_or_die(env)
    headers, token = auth_header(endpoints, env)
    targets = load_targets()
    rows = selected_rows(targets, args) if (args.all or args.target) else [t for t in targets if t.get("deploy")]
    env_name = env.get("RAYA_ENV", "staging")
    for row in rows:
        agent_id = agent_id_for(row, env_name)
        if not agent_id:
            print("%-13s unmapped" % row["id"])
            continue
        if not os.path.exists(os.path.join(REPO_ROOT, row["file"])):
            print("%-13s missing-file" % row["id"])
            continue
        try:
            _, _, remote_prompt, _ = fetch_remote(base, endpoints, env, headers, token, row)
        except SystemExit:
            print("%-13s unreachable" % row["id"])
            continue
        local = read_local(row)
        state = "in-sync" if normalize(remote_prompt) == normalize(local) else "drifted"
        print("%-13s %s" % (row["id"], state))


def snapshot_local(row):
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    label = "pre-deploy-%s-%s" % (row["id"], stamp)
    note = "auto snapshot before Raya deploy of %s" % row["file"]
    result = subprocess.run(
        # Snapshot the folder the file actually lives in: KKB Slim targets carry agent "KKB" but their
        # files are in KKB-Slim/, so snapshotting by row["agent"] saved the wrong folder.
        [VERSION_SH, "save", os.path.dirname(row["file"]) or row["agent"], label, note],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        die("pre-deploy snapshot failed (no snapshot, no push): %s" % result.stderr.strip())
    return label


def append_history(env_name, row, agent_id, sha, label, result):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "%s · %s · %s · %s · %s · sha256:%s · snapshot:%s · %s\n" % (
        stamp, env_name, row["id"], agent_id, row["file"], sha, label, result)
    with open(HISTORY_PATH, "a", encoding="utf-8") as fh:
        fh.write(line)


def warn_if_stale_agent(base, headers, token, agent_id, timeout):
    """Freshness guard: warn (do not block) if the target agent has no recent calls — a strong
    sign it is a dead placeholder while live traffic is on a DIFFERENT agent id. Learned the hard
    way on 2026-07-22: KKB inbound fixes were deployed to a placeholder (last call 07-14) while the
    live number was bound to another agent."""
    try:
        status, parsed, _ = api("GET", "%s/api/call?agent_id=%s&limit=1" % (base, agent_id),
                                 headers, token, None, timeout, 1)
        calls = (parsed.get("calls") or parsed.get("data") or []) if isinstance(parsed, dict) else []
        if not calls:
            print("   ⚠️  FRESHNESS: this agent has NO calls on record — is it the LIVE agent? "
                  "Live traffic may be on a different agent id (run `list` and compare).")
            return
        ts = (calls[0].get("created_at") or "")[:10]
        try:
            days = (datetime.utcnow() - datetime.strptime(ts, "%Y-%m-%d")).days
        except Exception:
            print("   freshness:  last call %s" % ts); return
        if days >= 10:
            print("   ⚠️  FRESHNESS: last call was %s (%d days ago) — verify this is the LIVE agent, "
                  "not a dead placeholder (live traffic may be on a different agent id)." % (ts, days))
        else:
            print("   freshness:  OK — last call %s (%d days ago)" % (ts, days))
    except Exception as exc:
        print("   freshness:  (check skipped: %s)" % exc)


def deploy_one(row, endpoints, env, base, headers, token, args):
    import difflib
    if row.get("account"):
        headers, token = auth_header(endpoints, env, row)
    env_name = env.get("RAYA_ENV", "staging")
    prof = resolve_profile(endpoints, row.get("profile", "conversation"))
    require_endpoint_configured(prof, ("get", "update", "prompt_field"))

    agent_id = agent_id_for(row, env_name)
    if not agent_id:
        die("target '%s' has no raya_agent_id for env '%s' — fill agents.json." % (row["id"], env_name))

    local = read_local(row)

    # 1a. Placeholder guardrail — NEVER push sample/placeholder job data to a live agent.
    #     The real job inventory may be maintained ON the live agent (the team edits it there),
    #     so a repo file still carrying placeholder job_ids means WE are behind — reconcile first.
    _ph_ids = [v for v in re.findall(r'"job_id"\s*:\s*"([^"]*)"', local) if "00000000" in v]
    _ph_flag = "PLACEHOLDER SAMPLE DATA" in local
    if _ph_ids or _ph_flag:
        die("REFUSING to deploy %s — local prompt still carries %d placeholder job_id(s)%s.\n"
            "The REAL job inventory was likely updated on the live agent (it is AHEAD). Reconcile "
            "the real inventory into %s first (pull the live prompt), then deploy.\n"
            "See raya/README.md -> 'Reconcile-before-fix'."
            % (row["id"], len(_ph_ids), " + a [PLACEHOLDER SAMPLE DATA] flag" if _ph_flag else "", row["file"]))

    # Size gate. A prompt past the size a bot can handle does not error: the bot keeps talking fluently and
    # stops calling tools (Purple Dots Kannada, Oct 2026). The limit differs per bot, so it is recorded per
    # target from evidence (scripts/prompt_size.py): max_prompt_bytes = seen failing, proven_prompt_bytes =
    # seen working.
    max_bytes = row.get("max_prompt_bytes") or endpoints.get("request", {}).get("max_prompt_bytes")
    llen, lsha = fingerprint(local)
    if max_bytes and llen >= max_bytes:
        die("REFUSING: %s is %d bytes, at or past %d bytes where this bot stopped calling tools (%s). Slim the "
            "MASTER first (/slim-prompt), then re-translate." % (row["id"], llen, max_bytes, row.get("size_evidence", "")))
    if row.get("proven_prompt_bytes") and llen > row["proven_prompt_bytes"]:
        print("   SIZE WARNING: %d bytes is bigger than any size proven to call tools on this bot (%d). The first "
              "post-deploy test call must confirm every tool fires." % (llen, row["proven_prompt_bytes"]))

    print("\n=== deploy %s  [env: %s]" % (row["id"], env_name))

    # 1. GET current remote (read-only): proves the URL, is the backup, drives the diff + name guard.
    url, agent_obj, remote_prompt, live_name = fetch_remote(base, endpoints, env, headers, token, row)
    update_url = build_url(base, prof["update"], agent_id)
    print("   GET url:    %s" % redact(url, token))
    print("   PUT url:    %s  (%s, mode=%s)"
          % (redact(update_url, token), prof["update"]["method"], prof.get("update_mode", "replace")))
    print("   agent-id:   %s" % agent_id)
    print("   live name:  %s" % live_name)

    # 2. name guard — refuse a wrong target BEFORE any write or snapshot.
    if not name_guard_ok(row, live_name):
        other = other_language_in_name(row, live_name)
        if other:
            die("REFUSING: live agent name %r names %s, but target %s is language '%s' — wrong agent? "
                "(fix the raya_agent_id in raya/agents.json)." % (live_name, other.title(), row["id"], row.get("language")))
        die("REFUSING: live agent name %r does not contain any of %s — wrong target? "
            "(fix raya/agents.json or expected_name_contains)."
            % (live_name, row.get("expected_name_contains")))
    print("   name guard: OK (contains one of %s)" % row.get("expected_name_contains"))
    warn_if_stale_agent(base, headers, token, agent_id, endpoints.get("request", {}).get("timeout_s", 30))

    # 3. dry-run diff. In sync -> nothing to push, no snapshot needed.
    #    "In sync" requires BOTH the prompt content AND any extra_body fields (e.g. memory_enabled)
    #    to match remote — otherwise a toggle like memory_enabled=true would never get pushed when
    #    the prompt text already matches (which is exactly the memory-enable case).
    _extra = prof.get("extra_body", {})
    _extra_in_sync = all(isinstance(agent_obj, dict) and agent_obj.get(k) == v for k, v in _extra.items())
    if normalize(remote_prompt) == normalize(local) and _extra_in_sync:
        print("   diff:       none — remote already matches local. Skipping PUT (idempotent no-op).")
        append_history(env_name, row, agent_id, lsha, "-", "skip-in-sync")
        return
    if normalize(remote_prompt) == normalize(local) and not _extra_in_sync:
        print("   diff:       prompt text matches; extra fields differ -> pushing to set them: %s"
              % ", ".join("%s: %r->%r" % (k, (agent_obj.get(k) if isinstance(agent_obj, dict) else None), v)
                          for k, v in _extra.items() if not (isinstance(agent_obj, dict) and agent_obj.get(k) == v)))
    diff = list(difflib.unified_diff(
        (remote_prompt or "").splitlines(keepends=True),
        local.splitlines(keepends=True),
        fromfile="remote:%s" % row["id"], tofile="local:%s" % row["file"]))
    rlen, rsha = fingerprint(remote_prompt or "")
    print("   diff:       size %d -> %d bytes (sha %s -> %s):" % (rlen, llen, rsha, lsha))
    sys.stdout.writelines(diff)
    print("")

    if args.dry_run:
        print("   DRY RUN: stopping before snapshot/PUT.")
        append_history(env_name, row, agent_id, lsha, "-", "dry-run")
        return

    # 4. explicit confirm (unless --yes, which the skill passes only after human approval).
    if not args.yes:
        try:
            answer = input('   Type the target id "%s" to PUSH LIVE (anything else aborts): ' % row["id"])
        except EOFError:
            die("no confirmation available (non-interactive) — re-run with --yes after human approval.")
        if answer.strip() != row["id"]:
            die("aborted by user (no changes pushed).")

    # 5. snapshot right before the write — no snapshot, no push.
    label = snapshot_local(row)
    print("   snapshot:   %s (rollback: scripts/prompt-version.sh restore %s %s)"
          % (label, row["agent"], label))

    # 6. build body + PUT.
    if prof.get("update_mode", "replace") == "patch":
        body = {}
        dotted_set(body, prof["prompt_field"], local)
    else:
        body = copy.deepcopy(agent_obj)
        dotted_set(body, prof["prompt_field"], local)
    # extra_body: profile-level fixed fields sent alongside the prompt (e.g. memory profile
    # sends {"memory_enabled": true} so pushing the memory prompt also turns the feature ON).
    for _k, _v in prof.get("extra_body", {}).items():
        body.setdefault(_k, _v)
    timeout = endpoints.get("request", {}).get("timeout_s", 30)
    status, parsed, raw = api(prof["update"]["method"], update_url, headers, token, body, timeout, 0)
    if status >= 300:
        append_history(env_name, row, agent_id, lsha, label, "FAILED-http-%s" % status)
        die("PUT %s returned HTTP %s\n%s\nRollback: scripts/prompt-version.sh restore %s %s"
            % (redact(update_url, token), status, redact(raw, token)[:800], row["agent"], label))

    # 7. read-back verify — against the UPDATE RESPONSE, which echoes the saved prompt.
    #    (Raya's GET currently returns an empty instructions field, so a re-GET is unreliable;
    #    the PATCH/PUT response is the trustworthy confirmation.)
    echoed = dotted_get(parsed, prof["prompt_field"]) if isinstance(parsed, dict) else None
    if echoed is None or normalize(echoed) != normalize(local):
        append_history(env_name, row, agent_id, lsha, label, "FAILED-readback")
        die("READ-BACK MISMATCH for %s — the update response prompt does NOT equal local.\n"
            "Rollback local: scripts/prompt-version.sh restore %s %s\n"
            "STOPPING the batch." % (row["id"], row["agent"], label))
    print("   read-back:  OK — update response echoes local (%d bytes, sha %s)." % (llen, lsha))
    # soft-confirm extra_body fields (e.g. memory_enabled) from the response, if it echoes them.
    for _k, _v in prof.get("extra_body", {}).items():
        if isinstance(parsed, dict) and _k in parsed:
            ok = "OK" if parsed.get(_k) == _v else "MISMATCH (got %r)" % parsed.get(_k)
            print("   extra:      %s=%r %s" % (_k, _v, ok))
    append_history(env_name, row, agent_id, lsha, label, "deployed")
    print("   DEPLOYED %s -> %s" % (row["id"], agent_id))


def cmd_deploy(args, endpoints, env):
    base = base_url_or_die(env)
    headers, token = auth_header(endpoints, env)
    targets = load_targets()
    rows = selected_rows(targets, args)
    print("Deploying %d target(s) to env '%s'. Batch stops on first failure."
          % (len(rows), env.get("RAYA_ENV", "staging")))
    for row in rows:
        deploy_one(row, endpoints, env, base, headers, token, args)
    print("\nDone.")


def cmd_reconcile(args, endpoints, env):
    """Compare a downloaded LIVE prompt (from the Raya console) against the repo file.
    Local-only: no network (the API returns empty instructions; the console is the source of truth).
    Token-cheap: the caller downloads the live prompt to a file; only the diff prints here."""
    import difflib
    import glob
    targets = load_targets()
    rows = resolve_selector(targets, args.target)
    if len(rows) != 1:
        die("reconcile takes exactly one target; '%s' matched %d (%s)"
            % (args.target, len(rows), ", ".join(r["id"] for r in rows)))
    row = rows[0]
    if args.live:
        live_path = os.path.expanduser(args.live)
    else:
        pattern = os.path.expanduser("~/Downloads/raya-live-%s*.md" % row["id"])
        matches = sorted(glob.glob(pattern), key=os.path.getmtime)
        if not matches:
            die("no live download found matching %s\n"
                "Pull it first: open the agent in the Raya console (Instructions tab) and run the download "
                "snippet from the /raya-reconcile skill (saves raya-live-%s.md to ~/Downloads)." % (pattern, row["id"]))
        live_path = matches[-1]
    if not os.path.exists(live_path):
        die("live file not found: %s" % live_path)
    with open(live_path, encoding="utf-8") as fh:
        live = fh.read()
    repo = read_local(row)
    rlen, rsha = fingerprint(repo)
    llen, lsha = fingerprint(live)
    print("target:    %s  (raya: %s)" % (row["id"], row.get("raya_name") or "?"))
    print("repo:      %d bytes  sha256:%s   %s" % (rlen, rsha, row["file"]))
    print("live:      %d bytes  sha256:%s   %s" % (llen, lsha, live_path))
    if normalize(live) == normalize(repo):
        print("\nVERDICT: IN SYNC — the live agent matches the repo exactly. Nothing to reconcile.")
        return
    diff = list(difflib.unified_diff(
        live.splitlines(), repo.splitlines(),
        fromfile="live:%s" % row["id"], tofile="repo:%s" % row["file"], lineterm=""))
    only_repo = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    only_live = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    print("\nVERDICT: DRIFT — %d line(s) only in repo (+), %d line(s) only in live (-)." % (only_repo, only_live))
    print("  - repo already contains every live change (repo = live + your fixes) -> REPO is ahead; deploy repo.")
    print("  - live has content the repo lacks               -> RAYA is ahead; pull live into the repo FIRST")
    print("    (cp the download over %s via /update-prompt), then re-apply the fix and deploy.\n" % row["file"])
    print("\n".join(diff))


def cmd_pull(args, endpoints, env):
    """Consume the LIVE prompt into the repo file — reconcile when Raya is AHEAD (e.g. the real job
    inventory / job_ids were updated directly on the console, independent of us).

    GET is flaky, so this is defensive: require TWO agreeing reads; reject the empty / 'helpful
    assistant' default and implausibly-small reads; snapshot the repo file first (reversible).
    After pulling, review `git diff`, commit the reconciliation, THEN apply any fix on top."""
    base = base_url_or_die(env)
    headers, token = auth_header(endpoints, env)
    targets = load_targets()
    rows = resolve_selector(targets, args.target)
    if len(rows) != 1:
        die("pull takes exactly one target; '%s' matched %d (%s)"
            % (args.target, len(rows), ", ".join(r["id"] for r in rows)))
    row = rows[0]
    _, _, live1, name1 = fetch_remote(base, endpoints, env, headers, token, row)
    _, _, live2, _ = fetch_remote(base, endpoints, env, headers, token, row)
    if not live1 or not live2:
        die("GET returned no prompt for %s — cannot pull (read path still broken)." % row["id"])
    if normalize(live1) != normalize(live2):
        die("GET is UNSTABLE for %s — two reads differ (%d vs %d bytes). Refusing to pull a flaky read; "
            "retry, or use the browser /raya-reconcile path."
            % (row["id"], fingerprint(live1)[0], fingerprint(live2)[0]))
    live = normalize(live1)
    if live in ("", "You are a helpful assistant"):
        die("GET returned the empty/default placeholder for %s — refusing to pull (would wipe the prompt)." % row["id"])
    repo = read_local(row)
    rlen, rsha = fingerprint(repo)
    llen, lsha = fingerprint(live)
    if llen < max(2000, rlen // 2):
        die("live prompt for %s is implausibly small (%d bytes vs repo %d) — refusing to pull." % (row["id"], llen, rlen))
    print("target:    %s  (raya: %s)" % (row["id"], name1 or "?"))
    print("live:      %d bytes  sha256:%s  (stable across 2 GETs)" % (llen, lsha))
    print("repo:      %d bytes  sha256:%s   %s" % (rlen, rsha, row["file"]))
    if normalize(repo) == live:
        print("\nIN SYNC — live already matches the repo. Nothing to pull.")
        return
    ph_live = [v for v in re.findall(r'"job_id"\s*:\s*"([^"]*)"', live) if "00000000" in v]
    if ph_live:
        print("WARNING: the LIVE prompt ALSO carries %d placeholder job_id(s) — the live agent is not the real "
              "inventory either. Pulling will not fix apply; get the real inventory from the team." % len(ph_live))
    if getattr(args, "dry_run", False):
        import difflib
        diff = list(difflib.unified_diff(repo.splitlines(), live.splitlines(),
                    fromfile="repo:%s" % row["file"], tofile="live:%s" % row["id"], lineterm=""))
        sys.stdout.write("\n".join(diff[:400]))
        if len(diff) > 400:
            print("\n... (%d more diff lines)" % (len(diff) - 400))
        print("\nDRY RUN: not written. Re-run without --dry-run to adopt the live prompt into %s." % row["file"])
        return
    label = snapshot_local(row)
    print("snapshot:  %s (rollback: scripts/prompt-version.sh restore %s %s)" % (label, row["agent"], label))
    with open(os.path.join(REPO_ROOT, row["file"]), "w", encoding="utf-8") as fh:
        fh.write(live + "\n")
    print("PULLED live -> %s (%d bytes). Review `git diff`, commit the reconciliation, THEN apply fixes on top." % (row["file"], llen))


# ----------------------------------------------------------------------------- cli

def build_parser():
    parser = argparse.ArgumentParser(
        prog="raya_deploy.py",
        description="Deploy Prompt Tuner prompts to live Raya Voice AI agents (config-driven, gated).",
    )
    parser.add_argument("--env", help="override RAYA_ENV for this run (staging|prod)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_targets = sub.add_parser("targets", help="print the manifest (local, no network)")
    p_targets.add_argument("--check", action="store_true", help="error if any deploy:true file is missing")

    sub.add_parser("list", help="GET Raya agents so you can fill agents.json")

    for name, helptext in (("verify", "resolve URL + GET each target (read-only)"),
                            ("diff", "unified diff local vs remote (read-only)")):
        sp = sub.add_parser(name, help=helptext)
        sp.add_argument("target", nargs="?", help="target id / file / agent[:lang][:dir]")
        sp.add_argument("--all", action="store_true", help="all deployable targets")

    p_status = sub.add_parser("status", help="per-target in-sync|drifted|unmapped|missing-file|unreachable")
    p_status.add_argument("target", nargs="?", help="target id / selector (default: all deployable)")
    p_status.add_argument("--all", action="store_true", help="all deployable targets")

    p_deploy = sub.add_parser("deploy", help="GATED write path: snapshot->GET->guard->diff->confirm->PUT->read-back")
    p_deploy.add_argument("target", nargs="?", help="target id / file / agent[:lang][:dir]")
    p_deploy.add_argument("--all", action="store_true", help="all deployable targets (stops on first failure)")
    p_deploy.add_argument("--yes", action="store_true", help="skip interactive confirm (only after human approval)")
    p_deploy.add_argument("--dry-run", action="store_true", help="do everything except the PUT")

    p_recon = sub.add_parser("reconcile", help="diff a downloaded live prompt vs the repo file (who is ahead?)")
    p_recon.add_argument("target", help="target id / file / agent[:lang][:dir]")
    p_recon.add_argument("--live", help="path to the downloaded live prompt (default: newest ~/Downloads/raya-live-<target>*.md)")

    p_pull = sub.add_parser("pull", help="consume the LIVE prompt into the repo file (reconcile when Raya is ahead)")
    p_pull.add_argument("target", help="target id / file / agent[:lang][:dir]")
    p_pull.add_argument("--dry-run", action="store_true", help="show the diff; do not write the repo file")
    return parser


def main(argv):
    args = build_parser().parse_args(argv)
    endpoints = load_json(ENDPOINTS_PATH)
    env = load_env()
    if args.env:
        env["RAYA_ENV"] = args.env
    env.setdefault("RAYA_ENV", "staging")

    handlers = {
        "targets": cmd_targets,
        "list": cmd_list,
        "verify": cmd_verify,
        "diff": cmd_diff,
        "status": cmd_status,
        "deploy": cmd_deploy,
        "reconcile": cmd_reconcile,
        "pull": cmd_pull,
    }
    handlers[args.cmd](args, endpoints, env)


if __name__ == "__main__":
    main(sys.argv[1:])
