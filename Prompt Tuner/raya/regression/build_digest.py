#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render latest-report.json (+ open-items.json) into a self-explanatory HTML email digest.

Written for a reader with NO context on this project: every finding says what it means, why it
matters, and what to do — never just a category tag and a filename. Layout:

  1. What this email is           (one short paragraph)
  2. Health summary               (counters + one-line verdict)
  3. Start here                   (cross-bot, priority-ordered actions)
  4. Bot-by-bot breakdown         (all 16 bots; auto-findings + known open items per bot)
  5. Applies to every bot         (open items that aren't bot-specific)
  6. What this check looks for     (plain-English glossary)

Email-client-safe: inline styles only, tables for layout, no external assets, no flex/grid.

Usage: python3 raya/regression/build_digest.py [daily|weekly|nightly] > digest.html
       python3 raya/regression/build_digest.py nightly --headline     # one-line email subject

`nightly` adds the live test calls from raya/regression/live-report.json (built by live_results.py
from that night's overnight_sweep.py run) as the first section: which bots were called, how many
calls connected, each check per call with its call id and recording link.
"""
import json, os, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KIND = (sys.argv[1] if len(sys.argv) > 1 else "daily").lower()

R = json.load(open(os.path.join(REPO, "raya/regression/latest-report.json"), encoding="utf-8"))
try:
    OPEN = json.load(open(os.path.join(REPO, "raya/regression/open-items.json"), encoding="utf-8"))
except Exception:
    OPEN = {"items": []}

LIVE = None
if KIND == "nightly":
    try:
        LIVE = json.load(open(os.environ.get("LIVE_REPORT") or
                              os.path.join(REPO, "raya/regression/live-report.json"), encoding="utf-8"))
    except Exception:
        LIVE = {"calls": [], "detectors": [], "attempts": 0, "connected": 0, "passed": 0,
                "failed": 0, "thin": 0, "not_dialled": 0, "missing": True}

CRIT, MAJ, MINO = R.get("critical", []), R.get("major", []), R.get("minor", [])
BOTS = R.get("bots", [])
N = R.get("prompts_checked", 0)
ITEMS = OPEN.get("items", [])

# ---------- palette (explicit light background: email clients vary wildly) ----------
INK, MUTED, LINE, PANEL = "#1a1a1a", "#5f6368", "#e3e5e8", "#f7f8fa"
SEV = {
    "critical": ("#b3261e", "#fdecea", "Critical"),
    "major":    ("#8a5300", "#fff4e5", "Major"),
    "minor":    ("#4a5568", "#eef1f5", "Minor"),
    "high":     ("#b3261e", "#fdecea", "High priority"),
    "medium":   ("#8a5300", "#fff4e5", "Medium priority"),
    "low":      ("#4a5568", "#eef1f5", "Low priority"),
}

GLOSSARY = [
    ("Wrong system's field names in the script", "leakage",
     "Each bot is wired to exactly one backend — either the newer <b>Signals</b> platform or the older "
     "<b>Dhiway/ONEST</b> one. The two use different field names and web addresses.",
     "If a script mentions the other system's fields, the bot can send data in a shape its backend "
     "refuses — showing up as failed profile saves or failed job applications on real calls."),
    ("Doubled country code on the caller's number", "phone-doubling",
     "The phone number handed to the bot already includes the country code (91).",
     "If the script adds \"91\" again, it looks the caller up as 9191… — the lookup fails, so a "
     "returning caller is treated as brand new and is asked everything again."),
    ("Caller history not wired in", "memory-block",
     "A small block in each script injects what we already know about the caller from past calls.",
     "Without it the bot starts every call blind and re-asks answered questions, which callers "
     "experience as the bot not remembering them."),
    ("Answer option no longer matches the backend", "enum-drift",
     "For choice questions (education level, years of experience) the backend accepts only an exact "
     "list of wordings.",
     "One reworded option and saving the caller's profile fails with a validation error, losing "
     "everything captured in that call."),
    ("A required part of the call script is missing", "missing-section",
     "Some sections must always exist: how to end a call politely, how to look a caller up, how to "
     "post a job.",
     "A missing section means the bot has no instructions for that moment and will improvise — "
     "or skip the step entirely."),
    ("Language versions of a bot have drifted apart", "sync-drift",
     "Most bots exist in more than one language (a master, usually Hindi, plus mirrors such as "
     "Kannada or Marathi) and every version is meant to follow the same script, differing only in "
     "the words spoken.",
     "If one language has extra or missing sections, a rule may have been added in one language and "
     "forgotten in another. Small differences are usually harmless formatting."),
]


# Curated items carry `priority` (high/medium/low); some newer ones carry only `severity`
# (critical/major/minor). Map rather than crash — a KeyError here silently kills the daily email.
_SEV_TO_PRIO = {"critical": "high", "major": "medium", "minor": "low"}


def prio(it):
    return it.get("priority") or _SEV_TO_PRIO.get(it.get("severity", ""), "low")


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def chip(text, kind):
    fg, bg, _ = SEV.get(kind, (MUTED, PANEL, kind))
    return (f'<span style="display:inline-block;padding:2px 8px;border-radius:10px;background:{bg};'
            f'color:{fg};font-size:11px;font-weight:700;letter-spacing:.3px;'
            f'text-transform:uppercase">{esc(text)}</span> ')


def counter(num, label, alert=False):
    fg = SEV["critical"][0] if (alert and num) else INK
    bg = SEV["critical"][1] if (alert and num) else PANEL
    return (f'<td width="25%" style="padding:12px 6px;background:{bg};border:1px solid {LINE};'
            f'text-align:center"><div style="font-size:26px;font-weight:700;color:{fg};'
            f'line-height:1.1">{num}</div>'
            f'<div style="font-size:11px;color:{MUTED};text-transform:uppercase;'
            f'letter-spacing:.4px;margin-top:3px">{label}</div></td>')


FAMILIES = [a for a in ("KKB-Slim", "KKB", "DKB", "Maya", "TRRAIN") if any(b["agent"] == a for b in BOTS)] + \
    sorted({b["agent"] for b in BOTS} - {"KKB-Slim", "KKB", "DKB", "Maya", "TRRAIN"})


# ---------- 2b. Live test calls (nightly only) ----------
VCOL = {"PASS": ("#137333", "#e6f4ea", "Passed"), "FAIL": (SEV["critical"][0], SEV["critical"][1], "Problem found"),
        "THIN": ("#8a5300", "#fff4e5", "Too short to judge"),
        "DID NOT CONNECT": ("#4a5568", "#eef1f5", "Did not connect"),
        "NOT DIALLED": ("#4a5568", "#eef1f5", "Not called"),
        "NO CALL ID": ("#4a5568", "#eef1f5", "Did not connect"),
        "COULD NOT FETCH": ("#8a5300", "#fff4e5", "Could not read the call")}


def vchip(v):
    fg, bg, txt = VCOL.get(v, (MUTED, PANEL, v))
    return (f'<span style="display:inline-block;padding:2px 8px;border-radius:10px;background:{bg};'
            f'color:{fg};font-size:11px;font-weight:700">{esc(txt)}</span>')


def render_live():
    if LIVE is None:
        return ""
    if LIVE.get("missing"):
        return section("Tonight's test calls",
                       f'<p style="margin:0;color:{SEV["critical"][0]};font-size:13px">The live test calls did not '
                       f'produce a report tonight, so this email shows the script check only. Open the run page '
                       f'for the reason.</p>', "")
    calls = LIVE.get("calls", [])
    called = [c for c in calls if c["verdict"] != "NOT DIALLED"]
    bots_called = list(dict.fromkeys(c["bot"] for c in called))
    att, con = LIVE.get("attempts", 0), LIVE.get("connected", 0)
    intro = (f'We placed test calls to <b>{len(bots_called)} bot(s)</b> tonight. A test caller (another AI '
             f'playing a job seeker or an employer) answered each call. <b>{con} of {att}</b> call(s) connected. '
             f'Of the connected calls, <b style="color:#137333">{LIVE.get("passed", 0)} passed</b> every check, '
             f'<b style="color:{SEV["critical"][0]}">{LIVE.get("failed", 0)} had a problem</b>, and '
             f'{LIVE.get("thin", 0)} were too short to judge.')
    body = (f'<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px"><tr>'
            f'{counter(len(bots_called), "Bots called")}{counter(f"{con}/{att}", "Calls connected")}'
            f'{counter(LIVE.get("passed", 0), "Passed")}{counter(LIVE.get("failed", 0), "Problem found", alert=True)}'
            f'</tr></table><p style="margin:0 0 12px;font-size:13px;color:{INK};line-height:1.55">{intro}</p>')
    for c in called:
        fails = [x for x in c.get("checks", []) if x["result"] in ("FAIL", "ERROR")]
        passes = [x for x in c.get("checks", []) if x["result"] == "PASS"]
        dets = [x for x in c.get("detector_findings", []) if not x.get("info")]
        link = ""
        if c.get("call_id"):
            link = (f'<div style="font-size:12px;color:{MUTED};margin-top:5px">Call id '
                    f'<span style="font-family:monospace;color:{INK}">{esc(c["call_id"])}</span>'
                    + (f' &middot; <a href="{esc(c["recording"])}" style="color:#1a56db">Listen to the recording</a>'
                       if c.get("status") == "CALL" and c.get("recording") else "")
                    + (f' &middot; {int(c["duration"])}s' if isinstance(c.get("duration"), (int, float)) else "")
                    + '</div>')
        detail = ""
        if c.get("status") == "CALL":
            if fails or dets:
                detail += '<div style="margin-top:6px;font-size:12.5px;color:%s;line-height:1.5">' % INK
                for x in fails:
                    detail += f'&#10007; <b>{esc(x["title"])}</b>: {esc(x["detail"])}<br>'
                for x in dets:
                    detail += f'&#10007; <b>{esc(x["title"])}</b>: {esc(x["finding"])}<br>'
                detail += '</div>'
            if c.get("short_reason"):
                detail += (f'<div style="margin-top:6px;font-size:12.5px;color:#8a5300;line-height:1.5">'
                           f'{esc(c["short_reason"])}</div>')
            if passes:
                detail += (f'<div style="margin-top:4px;font-size:12px;color:{MUTED};line-height:1.5">'
                           f'&#10003; Passed: {esc(", ".join(x["title"] for x in passes))}</div>')
        elif c["verdict"] in ("DID NOT CONNECT", "NO CALL ID"):
            detail = (f'<div style="margin-top:5px;font-size:12px;color:{MUTED}">The call was placed but the line '
                      f'did not connect after several tries, so nothing could be checked.</div>')
        body += (f'<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:9px">'
                 f'<tr><td style="padding:10px 13px;background:#fff;border:1px solid {LINE};'
                 f'border-left:3px solid {VCOL.get(c["verdict"], (MUTED,))[0]}">'
                 f'<div>{vchip(c["verdict"])} <span style="font-size:13px;font-weight:700;color:{INK};'
                 f'margin-left:6px">{esc(c["bot"])}</span></div>'
                 f'<div style="font-size:12.5px;color:{MUTED};margin-top:4px">What we tested: '
                 f'{esc(c.get("scenario", ""))}</div>{link}{detail}</td></tr></table>')
    skipped = [c for c in calls if c["verdict"] == "NOT DIALLED"]
    if skipped:
        body += (f'<div style="font-size:12px;color:{MUTED};line-height:1.55;margin:6px 0 4px"><b style="color:{INK}">'
                 f'Not called tonight:</b> ' + "; ".join(f'{esc(c["bot"])} ({esc(c.get("skip_reason", ""))})'
                                                         for c in skipped) + '</div>')
    dets = LIVE.get("detectors", [])
    if dets:
        bad = [d for d in dets if d["status"] == "findings"]
        body += (f'<div style="font-size:12px;color:{MUTED};line-height:1.55;margin-top:8px"><b style="color:{INK}">'
                 f'Wider checks over every call since the run started</b> (tonight\'s test calls plus any real '
                 f'callers): {len(dets) - len(bad)} of {len(dets)} clean.'
                 + (" Found something: " + "; ".join(f'{esc(d["title"])} ({d["findings"]})' for d in bad) + "."
                    if bad else "") + '</div>')
    if LIVE.get("run_url"):
        body += (f'<div style="font-size:12px;margin-top:8px"><a href="{esc(LIVE["run_url"])}" '
                 f'style="color:#1a56db">Full run log and the call-by-call files</a></div>')
    return section("Tonight's test calls", body,
                   "Real phone calls to the live bots, each graded automatically.")


def headline():
    bits = []
    if LIVE is not None and not LIVE.get("missing"):
        bits.append(f'{LIVE.get("connected", 0)}/{LIVE.get("attempts", 0)} calls connected')
        bits.append(f'{LIVE.get("failed", 0)} with a problem')
        if LIVE.get("thin"):
            bits.append(f'{LIVE["thin"]} too short to judge')
    elif LIVE is not None:
        bits.append("live calls did not run")
    if CRIT:
        bits.append(f"{len(CRIT)} critical")
    highs = len([i for i in ITEMS if prio(i) == "high"])
    if highs:
        bits.append(f"{highs} high-priority open")
    return ", ".join(bits) if bits else "all clear"


# ---------- 3. Start here: one ranked action list across every bot ----------
def bots_label(bots):
    """'all' is a marker, not a bot name — render it for humans."""
    if "all" in bots:
        return "All bots"
    return ", ".join(bots) if len(bots) <= 2 else f"{len(bots)} bots ({bots[0]}, …)"


def priority_rows():
    rows = []
    for f in CRIT:
        rows.append(("critical", f["bot"], f["message"],
                     "Fix before the next production run — this breaks calls.", f.get("file", "")))
    for it in [i for i in ITEMS if prio(i) == "high"]:
        rows.append(("high", bots_label(it["bots"]), it["title"] + " — " + it["what"], it["next"], ""))
    for f in MAJ:
        rows.append(("major", f["bot"], f["message"],
                     "Worth fixing soon — the bot works, but a step is missing or unclear.",
                     f.get("file", "")))
    for it in [i for i in ITEMS if prio(i) == "medium"]:
        rows.append(("medium", bots_label(it["bots"]), it["title"] + " — " + it["what"], it["next"], ""))
    return rows


def render_priority():
    rows = priority_rows()
    later = len(MINO) + len([i for i in ITEMS if prio(i) == "low"])
    if not rows:
        body = (f'<p style="margin:0;color:{INK}">Nothing needs action today. '
                f'{later} low-priority item(s) are listed further down for information.</p>')
    else:
        body = ""
        for i, (kind, bot, what, action, fpath) in enumerate(rows, 1):
            body += (
                f'<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px">'
                f'<tr><td style="padding:12px 14px;background:#fff;border:1px solid {LINE};'
                f'border-left:3px solid {SEV[kind][0]}">'
                f'<div style="margin-bottom:5px">{chip(SEV[kind][2], kind)}'
                f'<span style="font-size:13px;font-weight:700;color:{INK};margin-left:8px">'
                f'{i}. {esc(bot)}</span></div>'
                f'<div style="font-size:13px;color:{INK};line-height:1.55;margin-bottom:6px">'
                f'{esc(what)}</div>'
                f'<div style="font-size:12.5px;color:{MUTED};line-height:1.5">'
                f'<b style="color:{INK}">What to do:</b> {esc(action)}</div>'
                + (f'<div style="font-size:11px;color:{MUTED};margin-top:5px;font-family:monospace">'
                   f'{esc(fpath)}</div>' if fpath else "")
                + '</td></tr></table>')
        if later:
            body += (f'<p style="margin:4px 0 0;font-size:12.5px;color:{MUTED}">Plus {later} '
                     f'low-priority item(s), listed further down.</p>')
    return section("Start here — what to prioritise", body,
                   "Ranked across every bot: most urgent first.")


# ---------- 4. Bot-by-bot ----------
def items_for(bot):
    return [i for i in ITEMS if bot in i.get("bots", [])]


def findings_for(bot):
    return [f for f in R.get("all", []) if f["bot"] == bot]


AGENT_TAGLINE = {
    "KKB-Slim": "Kaam Ki Baat Slim: the job-seeker bots that take the live Ghaziabad and Dharwad calls",
    "TRRAIN": "TRRAIN follow-up: offers one free support service to people who already applied",
    "KKB": "Kaam Ki Baat — helps workers find & apply to government jobs",
    "DKB": "Dhandhe Ki Baat — helps employers post & verify job openings",
    "Maya": "Maya — campus recruitment for graduates in UP",
}


def agent_stats(agent):
    group = [b for b in BOTS if b["agent"] == agent]
    fs = len([f for f in R.get("all", []) if f.get("agent") == agent])
    its = len([i for i in ITEMS if any(b in [g["bot"] for g in group] for b in i.get("bots", []))])
    return group, fs, its


def render_tabbar():
    """Tab-styled jump links. Real click-to-toggle tabs need JS/:checked CSS, which Gmail strips,
    so these are anchors — and the sections stay readable even where anchors don't jump."""
    cells = ""
    for agent in FAMILIES:
        group, fs, its = agent_stats(agent)
        if not group:
            continue
        total = fs + its
        dot = ("#137333", "&#10003; clear") if total == 0 else (SEV["critical"][0], f"{total} to review")
        cells += (
            f'<td width="{100 // max(1, len(FAMILIES))}%" style="padding:0 4px">'
            f'<a href="#agent-{agent.lower()}" style="display:block;text-decoration:none;'
            f'padding:11px 12px;background:{PANEL};border:1px solid {LINE};border-top:3px solid '
            f'{dot[0]};border-radius:6px 6px 0 0">'
            f'<div style="font-size:14px;font-weight:700;color:{INK}">{esc(agent)}</div>'
            f'<div style="font-size:11px;color:{MUTED};margin-top:2px">{len(group)} bots</div>'
            f'<div style="font-size:11px;font-weight:700;color:{dot[0]};margin-top:3px">{dot[1]}</div>'
            f'</a></td>')
    return (f'<table width="100%" cellpadding="0" cellspacing="0" style="margin:6px 0 2px">'
            f'<tr>{cells}</tr></table>'
            f'<div style="font-size:11.5px;color:{MUTED};margin:6px 0 0">Tap a bot family to jump to '
            f'its section below.</div>')


def render_bots():
    body = render_tabbar()
    for agent in FAMILIES:
        group, fs_n, its_n = agent_stats(agent)
        if not group:
            continue
        total = fs_n + its_n
        hdr = "#137333" if total == 0 else SEV["critical"][0]
        body += (f'<a name="agent-{agent.lower()}"></a>'
                 f'<table id="agent-{agent.lower()}" width="100%" cellpadding="0" cellspacing="0" '
                 f'style="margin:20px 0 10px"><tr>'
                 f'<td style="padding:12px 14px;background:{INK};border-left:4px solid {hdr}">'
                 f'<div style="font-size:15px;font-weight:700;color:#fff">{esc(agent)}'
                 f'<span style="font-weight:400;color:#c8ccd2;font-size:12px"> — {len(group)} bots · '
                 f'{fs_n} check finding(s) · {its_n} open item(s)</span></div>'
                 f'<div style="font-size:12px;color:#c8ccd2;margin-top:3px">'
                 f'{esc(AGENT_TAGLINE.get(agent, ""))}</div>'
                 f'</td></tr></table>')
        for b in group:
            fs, its = findings_for(b["bot"]), items_for(b["bot"])
            clean = not fs and not its
            status = ('<span style="color:#137333;font-weight:700;font-size:12px">No issues found</span>'
                      if clean else
                      f'<span style="color:{SEV["critical"][0] if fs else SEV["medium"][0]};'
                      f'font-weight:700;font-size:12px">'
                      f'{len(fs)} from this check · {len(its)} open item(s)</span>')
            body += (f'<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px">'
                     f'<tr><td style="padding:11px 13px;background:{"#fff" if clean else PANEL};'
                     f'border:1px solid {LINE}">'
                     f'<div style="font-size:13px;font-weight:700;color:{INK}">{esc(b["bot"])}</div>'
                     f'<div style="font-size:12px;color:{MUTED};margin:3px 0 6px;line-height:1.45">'
                     f'{esc(b["blurb"])}</div><div>{status}</div>')
            for f in fs:
                body += (f'<div style="margin-top:9px;padding-top:9px;border-top:1px dashed {LINE}">'
                         f'{chip(SEV[f["severity"]][2], f["severity"])}'
                         f'<div style="font-size:12.5px;color:{INK};line-height:1.55;margin-top:5px">'
                         f'{esc(f["message"])}</div></div>')
            for it in its:
                body += (f'<div style="margin-top:9px;padding-top:9px;border-top:1px dashed {LINE}">'
                         f'{chip(SEV[prio(it)][2], prio(it))}'
                         f'<div style="font-size:12.5px;font-weight:700;color:{INK};margin-top:5px">'
                         f'{esc(it["title"])}</div>'
                         f'<div style="font-size:12.5px;color:{INK};line-height:1.55;margin-top:3px">'
                         f'{esc(it["what"])}</div>'
                         f'<div style="font-size:12px;color:{MUTED};line-height:1.5;margin-top:4px">'
                         f'<b style="color:{INK}">Why it matters:</b> {esc(it["why"])}</div>'
                         f'<div style="font-size:12px;color:{MUTED};line-height:1.5;margin-top:3px">'
                         f'<b style="color:{INK}">Next step:</b> {esc(it["next"])}</div></div>')
            body += '</td></tr></table>'
    return section("Bot-by-bot breakdown", body,
                   f"All {N} bot scripts checked. Each bot shows what this automated check found, "
                   f"plus any known open work.")


def render_global_items():
    glob = [i for i in ITEMS if "all" in i.get("bots", [])]
    if not glob:
        return ""
    body = ""
    for it in glob:
        body += (f'<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px">'
                 f'<tr><td style="padding:11px 13px;background:#fff;border:1px solid {LINE}">'
                 f'{chip(SEV[prio(it)][2], prio(it))}'
                 f'<div style="font-size:13px;font-weight:700;color:{INK};margin-top:5px">'
                 f'{esc(it["title"])}</div>'
                 f'<div style="font-size:12.5px;color:{INK};line-height:1.55;margin-top:3px">'
                 f'{esc(it["what"])}</div>'
                 f'<div style="font-size:12px;color:{MUTED};line-height:1.5;margin-top:4px">'
                 f'<b style="color:{INK}">Why it matters:</b> {esc(it["why"])}</div>'
                 f'<div style="font-size:12px;color:{MUTED};line-height:1.5;margin-top:3px">'
                 f'<b style="color:{INK}">Next step:</b> {esc(it["next"])}</div>'
                 f'</td></tr></table>')
    return section("Applies to every bot", body,
                   "Open work that isn't specific to one bot.")


def render_glossary():
    body = ""
    for title, cat, what, why in GLOSSARY:
        hits = len([f for f in R.get("all", []) if f["category"] == cat])
        flag = (f'<span style="color:{SEV["critical"][0]};font-weight:700"> — {hits} found today</span>'
                if hits else
                f'<span style="color:#137333;font-weight:700"> — none found today</span>')
        body += (f'<div style="margin-bottom:11px;padding-bottom:11px;border-bottom:1px solid {LINE}">'
                 f'<div style="font-size:12.5px;font-weight:700;color:{INK}">{esc(title)}{flag}</div>'
                 f'<div style="font-size:12px;color:{MUTED};line-height:1.55;margin-top:3px">{what}</div>'
                 f'<div style="font-size:12px;color:{MUTED};line-height:1.55;margin-top:3px">'
                 f'<b style="color:{INK}">Why it matters:</b> {why}</div></div>')
    return section("What this check looks for", body,
                   "Six failure patterns, each one learned from a real bug we hit before.")


def section(title, body, sub=""):
    return (f'<tr><td style="padding:22px 0 0">'
            f'<div style="font-size:16px;font-weight:700;color:{INK}">{esc(title)}</div>'
            + (f'<div style="font-size:12.5px;color:{MUTED};margin:3px 0 12px;line-height:1.45">'
               f'{esc(sub)}</div>' if sub else '<div style="height:10px"></div>')
            + body + '</td></tr>')


def main():
    highs = [i for i in ITEMS if prio(i) == "high"]
    clean = not CRIT and not MAJ
    if CRIT or MAJ:
        verdict = (f"{len(CRIT)} critical and {len(MAJ)} major issue(s) need attention before the next "
                   f"production run.")
    elif highs:
        # scripts pass, but curated tracking says something important is still unresolved
        verdict = (f"The scripts themselves are clean, but {len(highs)} high-priority item(s) from live "
                   f"testing are still open — see “Start here” below.")
    else:
        verdict = "All bot scripts are healthy and no high-priority work is outstanding."
    if LIVE is not None and not LIVE.get("missing") and LIVE.get("failed"):
        verdict = (f"{LIVE['failed']} of tonight's connected test call(s) found a problem (see "
                   f"\u201cTonight's test calls\u201d). " + verdict)
        clean = False
    elif LIVE is not None and not LIVE.get("missing") and not LIVE.get("connected"):
        verdict = "None of tonight's test calls connected, so no bot behaviour was checked. " + verdict
        clean = False
    vcol = "#137333" if (clean and not highs) else SEV["critical"][0]
    label = {"weekly": "Weekly", "nightly": "Nightly"}.get(KIND, "Daily")
    if LIVE is not None and not LIVE.get("missing"):
        what_this_is = (
            "Phone-based AI assistants help people find jobs and help employers post them. Each one runs "
            "from a written script (a &ldquo;prompt&rdquo;). Every night this job does two things: it "
            "<b>places real test calls</b> to the live bots and grades each call, and it reads all "
            f"{N} scripts for {len(GLOSSARY)} known failure patterns that have broken real calls before. "
            "The test calls go to our own test number, never to a real caller.")
    else:
        what_this_is = (
            "Phone-based AI assistants help people find jobs and help employers post them. Each one runs "
            "from a written script (a &ldquo;prompt&rdquo;) that tells it what to say and which system to "
            f"save data into. This job reads all {N} scripts and looks for {len(GLOSSARY)} known failure "
            "patterns, the kinds of mistakes that have previously broken real calls. It does "
            "<b>not</b> place phone calls; it inspects the scripts only.")

    html = f"""<div style="margin:0;padding:0;background:#eef0f3">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#eef0f3;padding:20px 10px">
<tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0" style="max-width:680px;width:100%;background:#fff;
 border:1px solid {LINE};font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
<tr><td style="padding:22px 26px 0">

<div style="font-size:20px;font-weight:700;color:{INK}">Voice-bot health check</div>
<div style="font-size:12.5px;color:{MUTED};margin-top:4px">{label} automated report · Prompt Tuner
 ({" · ".join(FAMILIES)}) · {time.strftime("%d %b %Y", time.gmtime(time.time() + 19800))}</div>

<table width="100%" cellpadding="0" cellspacing="0" style="margin:16px 0 4px">
<tr><td style="padding:13px 15px;background:{PANEL};border:1px solid {LINE};font-size:12.5px;
 color:{INK};line-height:1.6">
<b>What this is.</b> {what_this_is}
</td></tr></table>

<table width="100%" cellpadding="0" cellspacing="0" style="margin:14px 0 6px">
<tr>{counter(len(CRIT), "Critical", alert=True)}{counter(len(MAJ), "Major")}{counter(len(MINO), "Minor")}{counter(N, "Bots checked")}</tr>
</table>
<div style="font-size:13.5px;font-weight:700;color:{vcol};line-height:1.5;margin:10px 0 2px">
{esc(verdict)}</div>

</td></tr>
{render_live()}
{render_priority()}
{render_bots()}
{render_global_items()}
{render_glossary()}
<tr><td style="padding:18px 26px 24px">
<div style="border-top:1px solid {LINE};padding-top:12px;font-size:11.5px;color:{MUTED};line-height:1.6">
Sent automatically by the Prompt Tuner regression job (GitHub Actions, {label.lower()}). Severity means:
<b>critical</b> = will break calls, <b>major</b> = a step is missing or unclear, <b>minor</b> =
cosmetic or informational. Full technical report and history live in the repository under
<span style="font-family:monospace">raya/regression/</span>. Known open work is curated in
<span style="font-family:monospace">open-items.json</span> &mdash; last updated {esc(OPEN.get('updated','n/a'))}.
</div>
</td></tr>
</table></td></tr></table></div>"""
    sys.stdout.write(html)
    return 0


if __name__ == "__main__":
    if "--headline" in sys.argv:
        print(headline())
        sys.exit(0)
    sys.exit(main())
