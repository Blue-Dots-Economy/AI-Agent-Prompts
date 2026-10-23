#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static regression suite — runs daily (cloud-scheduled), fast + reliable, no telephony.

Checks EVERY conversation prompt for the failure classes we've hit. Precision over recall: a noisy
daily email is worse than none, so checks are tuned to avoid false positives (tokens that only ever
appear as Dhiway/Signals CONTRACT markers, not ones that can show up in a "never speak these field
names" ban). Produces raya/regression/latest-report.md + latest-report.json.

Each finding carries the BOT it belongs to (friendly name + blurb) and a plain-English message, so
build_digest.py can render an email that a reader with no context can act on.

Backend: a filename containing "Signals" -> Signals DPG; else legacy Dhiway/up-getjob.
Agent role: DKB is an employer/provider bot (no get_profile/apply_job); KKB/Maya are seeker bots.

Usage: python3 raya/regression/static_regression.py [--agents PATH]
  --agents  alternate deploy manifest (default raya/agents.json); used to dry-run a new language.
"""
import argparse, json, os, re, sys, io

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AGENTS_JSON = os.path.join(REPO, "raya/agents.json")
FLEET_JSON = os.path.join(REPO, "raya/regression/fleet.json")

# Languages come from each target's ISO `language` code in raya/agents.json, never from a two-way
# Hindi/Kannada default. Unknown codes fall back to the code itself.
LANG_NAMES = {"hi": "Hindi", "kn": "Kannada", "mr": "Marathi", "te": "Telugu", "ta": "Tamil",
              "ml": "Malayalam", "bn": "Bengali", "gu": "Gujarati", "pa": "Punjabi", "or": "Odia",
              "as": "Assamese", "ur": "Urdu"}


def lang_name(code):
    return LANG_NAMES.get(code, code)


def lang_from_name(name):
    """Last resort for a target with no usable `language`: look for any known language name in it."""
    name = name.lower()
    for code, disp in LANG_NAMES.items():
        if disp.lower() in name:
            return code
    return "unknown"

# What each agent is, in words a newcomer understands.
AGENT_BLURB = {
    "KKB": "Government-job matching for workers / job-seekers",
    "DKB": "Job posting & verification for employers (MSMEs)",
    "Maya": "Campus recruitment for UP graduates",
    "TRRAIN": "Follow-up call offering a free support service to seekers who already applied",
}
# Agents whose callers are job-seekers (vs employers) — drives the seeker-only checks.
SEEKER_AGENTS = ("KKB", "Maya", "TRRAIN")
DIRECTION_BLURB = {"outbound": "the bot phones the person", "inbound": "the person phones the bot"}
BACKEND_BLURB = {"signals": "new Signals DPG backend", "dhiway": "older Dhiway/ONEST backend"}


def discover_prompts(agents_path=AGENTS_JSON):
    """Derive the checked set from raya/agents.json — never a hard-coded list.

    Gap G4. This list used to be hand-maintained and twice fell behind reality: the two DKB
    inbound bots (2026-08-05) and then TRRAIN (2026-08-10) were live deploy targets that the
    daily suite silently ignored, while the digest read as full coverage. Deriving it from the
    same manifest the deploys use means a newly registered bot is checked the day it lands.
    coverage_gap() stays as the backstop.
    """
    out = []
    manifest = json.load(io.open(agents_path, encoding="utf-8"))
    for t in manifest.get("targets", []):
        if t.get("kind") != "conversation" or not t.get("deploy"):
            continue
        rel = t["file"]
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            continue
        agent_dir = rel.split("/")[0]
        name = rel.lower()
        code = t.get("language")
        if not code or code == "xx":
            code = lang_from_name(name)
        lang = lang_name(code)
        direction = t.get("direction") or ("inbound" if "inbound" in name else "outbound")
        backend = "signals" if (t.get("signals") or "signals" in name) else "dhiway"
        out.append({
            "path": rel, "agent": agent_dir,
            "lang": code, "master": bool(t.get("master")),
            "direction": direction, "backend": backend,
            "seeker": agent_dir in SEEKER_AGENTS,
            # friendly identity used throughout the email
            "bot": f"{agent_dir} {lang} \u00b7 {direction} \u00b7 {'Signals' if backend=='signals' else 'legacy'}",
            "blurb": (f"{AGENT_BLURB.get(agent_dir, agent_dir)} \u2014 {DIRECTION_BLURB[direction]}, in {lang}, "
                      f"on the {BACKEND_BLURB[backend]}"),
            "text": io.open(p, encoding="utf-8").read()})
    out.sort(key=lambda x: (x["agent"], x["direction"], x["lang"]))
    return out


# CONTRACT-ONLY tokens (never appear in a "never-speak-these-fields" ban) -> unambiguous leakage.
SIGNALS_CONTRACT = ["item_state","lifecycle_status","acting_as_user_id","educationCategory",
                    "workExperienceYearsConditional","otherHelpNeeded","PROFILE_NOT_LIVE",
                    "INVALID_ITEM_STATE","job_posting_1.0","blue_dot"]
DHIWAY_CONTRACT  = ["up-getjob","ONEST-AGENT","onest-lite","jobs-onest-interface","job-up.seeker",
                    "jobs.onest.seeker"]


def check(p):
    """Return findings for one prompt. Messages are written for a non-expert reader."""
    f = []; t = p["text"]; be = p["backend"]
    other = "Dhiway/ONEST" if be == "signals" else "Signals"
    mine = "Signals" if be == "signals" else "Dhiway/ONEST"

    def add(sev, cat, msg, detail=None):
        f.append({"severity": sev, "category": cat, "message": msg, "detail": detail or {}})

    # 1. cross-backend contract leakage (contract-only tokens)
    for tok in (DHIWAY_CONTRACT if be == "signals" else SIGNALS_CONTRACT):
        if tok in t:
            add("critical", "leakage",
                f"This bot talks to the {mine} system, but its script still mentions "
                f"\"{tok}\" — a field or address belonging to the {other} system.",
                {"token": tok, "this_backend": mine, "other_backend": other})

    # 2. phone-doubling template
    if be == "signals" and re.search(r"(?<![+\w])91\$\{contact_phone\}", t):
        add("critical", "phone-doubling",
            "The script puts \"91\" in front of the caller's phone number, but that number already "
            "starts with 91 — so the bot builds 9191… and the caller lookup fails.",
            {"found": "91${contact_phone}", "should_be": "${contact_phone}"})
    if be == "dhiway" and ("+91${contact_phone}" in t or "+91<contact_phone>" in t):
        add("critical", "phone-doubling",
            "The script puts \"+91\" in front of the caller's phone number, but that number already "
            "carries +91 — so the bot builds +91+91… and the caller lookup fails.",
            {"found": "+91${contact_phone}", "should_be": "${contact_phone}"})

    # 3. memory-injection block
    if "{${contact_memory}}" not in t:
        add("critical", "memory-block",
            "The block that feeds in what we already know about the caller is missing, so this bot "
            "starts every call blind and will re-ask things the caller already answered.",
            {"expected_block": "{${contact_memory}}"})

    # 4. Signals seeker enum-exactness (only prompts that carry the new Phase-2 fields)
    if be == "signals" and p["seeker"] and "educationCategory" in t:
        # 2026-10-13 (tracker r113): the backend REJECTS "ITI / Other Vocational Trainings" (5/5) and
        # "Polytechnic / Diploma" (3/3) with INVALID_ITEM_STATE; the live tool schema says `ITI` / `Diploma`.
        # The old list required the rejected wordings, so it flagged every corrected prompt as critical.
        for enum in ["`ITI`", "`Diploma`", "3-5 Years", "B.Tech/B.E."]:
            if enum not in t:
                add("critical", "enum-drift",
                    f"The answer option \"{enum.strip('`')}\" is missing or reworded. The backend accepts only "
                    f"this exact wording, so anything else makes saving the caller's profile fail.",
                    {"expected_option": enum.strip("`")})
        for bad in ["ITI / Other Vocational Trainings", "Polytechnic / Diploma"]:
            if bad in t:
                add("critical", "enum-drift",
                    f"The answer option \"{bad}\" is back in the script. The backend rejects this wording "
                    f"(tracker r113), so saving the caller's profile fails.",
                    {"rejected_option": bad})

    # 5. required sections by role
    if "Graceful Exit" not in t and "graceful exit" not in t.lower():
        add("major", "missing-section",
            "No \"Graceful Exit\" section — the part that tells the bot how to end a call politely when "
            "the caller declines or wants to stop.", {"section": "Graceful Exit"})
    # A toolless bot (e.g. the TRRAIN follow-up campaign) has no profile flow BY DESIGN — it only
    # talks and listens. Requiring get_profile of it is a false positive, so exempt it explicitly.
    toolless = "You have no tools" in t
    if p["seeker"] and not toolless and "get_profile" not in t:
        add("major", "missing-section",
            "This is a job-seeker bot, but its script never looks the caller up (no get_profile), so it "
            "cannot tell a returning caller from a brand-new one.", {"section": "get_profile"})
    if p["agent"] == "DKB" and "create_job" not in t:
        add("major", "missing-section",
            "This is an employer bot, but its script never posts the job (no create_job) — the whole "
            "point of the call would go unsaved.", {"section": "create_job"})
    # 9. step references land where they say (D125): a stale "go to Step N" sends the bot to the wrong step
    sp = os.path.join(REPO, "scripts", "prompt_structure.py")
    if os.path.exists(sp):
        import subprocess, tempfile
        with tempfile.NamedTemporaryFile(suffix=".json") as tf:
            subprocess.run([sys.executable, sp, os.path.join(REPO, p["path"]), "--json", tf.name], capture_output=True)
            try:
                res = json.load(open(tf.name, encoding="utf-8"))
            except ValueError:
                res = {}
        for msg in (res.get("fails") or [])[:5]:
            add("major", "step-reference",
                "A rule in this script points the bot at a step that is wrong or missing, so the bot can end "
                "up at the wrong question: " + msg, {"check": "scripts/prompt_structure.py"})
    return f


def _fleet_masters():
    """sync_group -> master_language from raya/regression/fleet.json, if it is readable."""
    try:
        bots = json.load(io.open(FLEET_JSON, encoding="utf-8")).get("bots", [])
        return {b["sync_group"]: b["master_language"] for b in bots
                if b.get("sync_group") and b.get("master_language")}
    except Exception:
        return {}


def sync_parity(prompts):
    """Compare the master language of each bot against EVERY mirror (one master, N mirrors).

    Master: Hindi when present, else the language whose agents.json target is marked `master`,
    else fleet.json's master_language for the sync group, else the first language. One finding
    per drifting mirror.
    """
    out = []; by = {}
    fleet_master = _fleet_masters()
    for p in prompts:
        by.setdefault((p["agent"], p["direction"], p["backend"]), {})[p["lang"]] = p
    for key, L in by.items():
        if len(L) < 2:
            continue
        agent, direction, backend = key
        if "hi" in L:
            m = "hi"
        else:
            marked = [c for c in sorted(L) if L[c].get("master")]
            fm = fleet_master.get(f"{agent}:{direction}:{backend}")
            m = marked[0] if marked else (fm if fm in L else sorted(L)[0])
        master = L[m]
        h = len(re.findall(r"(?m)^#{1,2} ", master["text"]))
        for c in sorted(L):
            if c == m:
                continue
            mirror = L[c]
            k = len(re.findall(r"(?m)^#{1,2} ", mirror["text"]))
            d = abs(h - k)
            if d > 2:
                sev = "major" if d > 6 else "minor"
                mn, cn = lang_name(m), lang_name(c)
                detail = {f"{mn.lower()}_sections": h, f"{cn.lower()}_sections": k, "difference": d,
                          "master_lang": m, "master_sections": h,
                          "mirror_lang": c, "mirror_sections": k, "mirror_file": mirror["path"]}
                if c == "kn":
                    detail["kannada_file"] = mirror["path"]   # legacy key, kept for old readers
                out.append({
                    "severity": sev, "category": "sync-drift",
                    "file": master["path"], "bot": master["bot"], "agent": agent,
                    "blurb": master["blurb"],
                    "message": (
                        f"The {mn} and {cn} versions of this bot are laid out differently: {mn} has "
                        f"{h} sections, {cn} has {k}. Both languages are meant to follow the same script, "
                        f"so a gap can mean one language is missing a rule the other has. A small gap is "
                        f"usually just formatting."),
                    "detail": detail})
    return out


def coverage_gap(prompts, agents_path=AGENTS_JSON):
    """Self-check: is any LIVE conversation deploy target missing from this suite?

    Added 2026-08-05 after two live bots (dkb-hi-in, dkb-kn-in) sat unchecked for days because
    discover_prompts() hard-codes its file list while raya/agents.json is the real fleet. A suite
    that can silently under-cover the fleet is worse than no suite: the digest reported "16 bots
    checked" and read as full coverage. This makes that failure loud instead of invisible.
    """
    out = []
    try:
        d = json.load(io.open(agents_path, encoding="utf-8"))
        targets = d["targets"] if isinstance(d, dict) and "targets" in d else d
        live = {t["file"]: t.get("id", "?") for t in targets
                if t.get("kind") == "conversation" and t.get("deploy")}
    except Exception as e:
        return [{"severity": "major", "category": "coverage", "file": "raya/agents.json",
                 "bot": "(suite self-check)", "agent": "-", "blurb": "regression suite coverage",
                 "message": f"Could not read the deploy manifest to verify fleet coverage ({e}); "
                            f"this suite cannot prove it checked every live bot.", "detail": {}}]
    checked = {p["path"] for p in prompts}
    for f, tid in sorted(live.items()):
        if f not in checked:
            out.append({"severity": "critical", "category": "coverage", "file": f,
                        "bot": f"(unchecked: {tid})", "agent": "-",
                        "blurb": "a live bot this suite is not checking",
                        "message": (f"'{f}' is a LIVE deploy target ({tid}) but this daily suite is "
                                    f"not checking it — so nothing here says anything about that "
                                    f"bot's health. Add it to discover_prompts()."),
                        "detail": {"target_id": tid}})
    return out


def main():
    ap = argparse.ArgumentParser(description="Daily static regression over every live conversation prompt.")
    ap.add_argument("--agents", default=AGENTS_JSON,
                    help="deploy manifest to discover prompts from (default: raya/agents.json)")
    args = ap.parse_args()
    prompts = discover_prompts(args.agents)
    findings = coverage_gap(prompts, args.agents)
    bots = []
    for p in prompts:
        fs = check(p)
        for x in fs:
            x.update({"file": p["path"], "bot": p["bot"], "agent": p["agent"], "blurb": p["blurb"]})
            findings.append(x)
        bots.append({"bot": p["bot"], "blurb": p["blurb"], "agent": p["agent"], "file": p["path"],
                     "findings": 0})
    findings += sync_parity(prompts)

    counted = {}
    for x in findings:
        counted[x["bot"]] = counted.get(x["bot"], 0) + 1
    for b in bots:
        b["findings"] = counted.get(b["bot"], 0)

    order = {"critical": 0, "major": 1, "minor": 2}
    findings.sort(key=lambda x: order.get(x["severity"], 3))
    crit = [x for x in findings if x["severity"] == "critical"]
    maj  = [x for x in findings if x["severity"] == "major"]
    mino = [x for x in findings if x["severity"] == "minor"]

    outdir = os.path.join(REPO, "raya/regression")
    io.open(os.path.join(outdir, "latest-report.json"), "w", encoding="utf-8").write(
        json.dumps({"prompts_checked": len(prompts), "total_findings": len(findings),
                    "bots": bots, "critical": crit, "major": maj, "minor": mino, "all": findings},
                   ensure_ascii=False, indent=1))

    lines = ["# Static regression report", "",
             f"Prompts checked: **{len(prompts)}** | Findings: **{len(findings)}** "
             f"(critical **{len(crit)}**, major **{len(maj)}**, minor **{len(mino)}**)", ""]
    if not findings:
        lines.append("No static findings — all prompts clean.")
    else:
        for sev in ("critical", "major", "minor"):
            g = [x for x in findings if x["severity"] == sev]
            if g:
                lines.append(f"## {sev.upper()} ({len(g)})")
                for x in g:
                    lines.append(f"- **{x['bot']}** (`{x['file']}`) — {x['message']}")
                lines.append("")
    io.open(os.path.join(outdir, "latest-report.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"Static regression: {len(prompts)} prompts | {len(crit)} critical, {len(maj)} major, {len(mino)} minor")
    return 0


if __name__ == "__main__":
    sys.exit(main())
