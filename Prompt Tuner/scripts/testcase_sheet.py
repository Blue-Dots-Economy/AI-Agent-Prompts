#!/usr/bin/env python3
#
# testcase_sheet.py: write tuner-generated test cases into a Google Sheet in the same
# tester-ready layout as "Blue Dots Voice Agents - Test Cases (Oct 2026)", and drive a
# test run from that sheet (pull rows, record results, add newly found bugs).
#
#   scripts/testcase_sheet.py lint  <rows.json>
#   scripts/testcase_sheet.py write <rows.json> --sheet-id ID [--replace-tabs] [--only-tab NAME ...]
#   scripts/testcase_sheet.py pull  --sheet-id ID --tab NAME [--out file.json]
#   scripts/testcase_sheet.py result --sheet-id ID --tab NAME --id DK-03 --verdict PASS --actual "..." \
#                                    [--notes "..."] [--calls "uuid1, uuid2"]
#   scripts/testcase_sheet.py add-bug --sheet-id ID --tab NAME --after-phase "Turn 1 - Opening" \
#                                    --scenario ... --tester-says ... --expected ... --language Hindi \
#                                    --direction Outbound --priority P0 [--type Manual] [--actual ...] \
#                                    [--verdict FAIL] [--notes ...] [--run-date YYYY-MM-DD]
#
# rows.json shape (see raya/testcases/sheet-template.json):
#   {"readme": [[topic, text], ...],
#    "bots": [{bot, language, direction, how_to_reach, console, what_it_does, notes}],
#    "bot_tabs": {"<tab>": [{id, phase, scenario, tester_says, expected, language, direction,
#                            type, priority, [actual, verdict, notes]}]},
#    "language_checks": {"<tab>": [{scenario, level, how, pass_criteria, [result]}]}}
#
# Auth and HTTP are reused from gsheets.py (service account, no extra deps).

import argparse
import collections
import datetime
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gsheets  # noqa: E402  (reuse access_token / load_key / api / die)

die = gsheets.die

# ---------------------------------------------------------------- layout

README_TAB = "Read Me"
BOTS_TAB = "Bots to Test"

BOT_COLS = [  # (key, header, width px), widths copied from the reference DKB tab
    ("id", "#", 62),
    ("phase", "Phase", 150),
    ("scenario", "Scenario", 210),
    ("tester_says", "What the tester should say", 300),
    ("expected", "Expected Response", 430),
    ("language", "Language", 80),
    ("direction", "Direction", 85),
    ("type", "Type", 70),
    ("priority", "Priority", 65),
    ("actual", "Actual Response", 300),
    ("verdict", "Verdict", 95),
    ("notes", "Call time · number used (last 4) · notes", 220),
]
BOTS_COLS = [
    ("bot", "Bot", 200),
    ("language", "Language", 75),
    ("direction", "Direction", 80),
    ("how_to_reach", "How to reach it", 260),
    ("console", "Raya console", 330),
    ("what_it_does", "What it does", 330),
    ("notes", "Notes", 330),
]
LANG_COLS = [
    ("scenario", "Scenario", 200),
    ("level", "Prompt/Call", 100),
    ("how", "What should be tested and how", 430),
    ("pass_criteria", "Pass criteria", 360),
    ("result", "Test Result", 110),
]
README_WIDTHS = [190, 900]

BOT_REQUIRED = ["id", "phase", "scenario", "tester_says", "expected", "language", "direction", "type", "priority"]
BOTS_REQUIRED = ["bot", "language", "direction", "how_to_reach", "console", "what_it_does"]
LANG_REQUIRED = ["scenario", "level", "how", "pass_criteria"]

TYPES = ("Smoke", "Manual", "Stress")
PRIORITIES = ("P0", "P1", "P2")
VERDICTS = ["PASS", "FAIL", "PARTIAL", "BLOCKED", "NOT TESTED"]
LEVELS = ("Prompt", "Call", "Prompt / Call")
CALLS_HEADERS = {"calls", "call ids", "call id", "call uuids", "call uuid"}

HEADER_BG = {"red": 0.11764706, "green": 0.30980393, "blue": 0.54901963}
WHITE = {"red": 1, "green": 1, "blue": 1}
GRID_ROWS = 1000
GRID_COLS = 26

# ---------------------------------------------------------------- lint

VAGUE = ["handles gracefully", "appropriately", "properly", "looks right", "as expected", "correctly handles"]
NEGATIVE = ["never", "no ", "not ", "does not", "must not"]
QUOTED = re.compile(r'[“"]([^”"]{6,})[”"]')
TOOL_ONLY = re.compile(r"no tool (is )?called|no tool call|ends the call|call ends|hangs up|console:", re.I)

SCRIPTS = {  # language -> (lo, hi) code point range
    "devanagari": (0x0900, 0x097F), "kannada": (0x0C80, 0x0CFF), "telugu": (0x0C00, 0x0C7F),
    "tamil": (0x0B80, 0x0BFF), "malayalam": (0x0D00, 0x0D7F), "bengali": (0x0980, 0x09FF),
    "gujarati": (0x0A80, 0x0AFF), "gurmukhi": (0x0A00, 0x0A7F), "odia": (0x0B00, 0x0B7F),
}
LANG_SCRIPT = {
    "hi": "devanagari", "hindi": "devanagari", "mr": "devanagari", "marathi": "devanagari",
    "kn": "kannada", "kannada": "kannada", "te": "telugu", "telugu": "telugu",
    "ta": "tamil", "tamil": "tamil", "ml": "malayalam", "malayalam": "malayalam",
    "bn": "bengali", "bengali": "bengali", "bangla": "bengali", "as": "bengali", "assamese": "bengali",
    "gu": "gujarati", "gujarati": "gujarati", "pa": "gurmukhi", "punjabi": "gurmukhi",
    "or": "odia", "odia": "odia", "oriya": "odia",
}
NO_SCRIPT_CHECK = {"en", "english", "both", "all", "any", "mixed"}


def _blank(v):
    return v is None or str(v).strip() == ""


def _has_script(text, scripts):
    for ch in text:
        cp = ord(ch)
        for s in scripts:
            lo, hi = SCRIPTS[s]
            if lo <= cp <= hi:
                return True
    return False


def lint_bot_row(tab, row):
    """Return list of (severity, message) for one bot-tab row."""
    out = []
    for f in BOT_REQUIRED:
        if _blank(row.get(f)):
            out.append(("ERROR", "required field '%s' is empty" % f))
    typ = str(row.get("type", "")).strip()
    if typ and typ not in TYPES:
        out.append(("ERROR", "type '%s' not in Smoke|Manual|Stress" % typ))
    pri = str(row.get("priority", "")).strip()
    if pri and pri not in PRIORITIES:
        out.append(("ERROR", "priority '%s' not in P0|P1|P2" % pri))
    expected = str(row.get("expected") or "")
    tester = str(row.get("tester_says") or "")
    if expected:
        if "Pass criteria:" not in expected:
            out.append(("ERROR", "expected lacks the literal 'Pass criteria:'"))
        if not QUOTED.search(expected):
            if TOOL_ONLY.search(expected):
                out.append(("WARN", "expected has no quoted spoken line (tool-only wording found)"))
            else:
                out.append(("ERROR", "expected has no quoted spoken line (6+ chars inside quotes)"))
    for field, text in (("tester_says", tester), ("expected", expected)):
        low = text.lower()
        for w in VAGUE:
            if w in low:
                out.append(("ERROR", "%s uses vague grading words '%s'" % (field, w)))
    if pri == "P0" and expected:
        low = expected.lower()
        if not any(n in low for n in NEGATIVE):
            out.append(("WARN", "P0 expected has no negative assertion (never / no / not / does not / must not)"))
    lang = str(row.get("language") or "").strip()
    if lang and tester:
        tokens = [t.strip().lower() for t in re.split(r"[,/+&]| and ", lang) if t.strip()]
        if not any(t in NO_SCRIPT_CHECK for t in tokens):
            scripts = {LANG_SCRIPT[t] for t in tokens if t in LANG_SCRIPT}
            unknown = [t for t in tokens if t not in LANG_SCRIPT]
            if unknown:
                out.append(("WARN", "language '%s' not recognised; script check skipped" % lang))
            elif scripts and not _has_script(tester, scripts):
                out.append(("WARN", "tester_says has no %s-script characters for language '%s'"
                            % ("/".join(sorted(scripts)), lang)))
    verdict = str(row.get("verdict") or "").strip()
    if verdict and verdict.upper() not in VERDICTS:
        out.append(("WARN", "verdict '%s' not one of %s" % (verdict, ", ".join(VERDICTS))))
    return out


def lint(data):
    """Return list of (tab, id, severity, message)."""
    v = []
    if not any(data.get(k) for k in ("bot_tabs", "bots", "readme", "language_checks")):
        v.append(("<file>", "-", "ERROR", "no bot_tabs, bots, readme or language_checks found"))
    for i, pair in enumerate(data.get("readme") or [], 1):
        if not isinstance(pair, list) or len(pair) != 2 or any(_blank(x) for x in pair):
            v.append((README_TAB, "row %d" % i, "ERROR", "readme row must be [topic, text], both non-empty"))
    for i, b in enumerate(data.get("bots") or [], 1):
        rid = b.get("bot") or "row %d" % i
        for f in BOTS_REQUIRED:
            if _blank(b.get(f)):
                v.append((BOTS_TAB, rid, "ERROR", "required field '%s' is empty" % f))
    for tab, rows in (data.get("bot_tabs") or {}).items():
        if not rows:
            v.append((tab, "-", "ERROR", "tab has no rows"))
            continue
        seen = collections.Counter(str(r.get("id", "")).strip() for r in rows)
        for rid, n in seen.items():
            if rid and n > 1:
                v.append((tab, rid, "ERROR", "duplicate id (%d rows)" % n))
        for i, r in enumerate(rows, 1):
            rid = str(r.get("id") or "").strip() or "row %d" % i
            for sev, msg in lint_bot_row(tab, r):
                v.append((tab, rid, sev, msg))
        if not any(str(r.get("type", "")).strip() == "Smoke" for r in rows):
            v.append((tab, "-", "WARN", "tab has zero Smoke rows"))
    for tab, rows in (data.get("language_checks") or {}).items():
        if not rows:
            v.append((tab, "-", "ERROR", "tab has no rows"))
        for i, r in enumerate(rows or [], 1):
            rid = str(r.get("scenario") or "").strip() or "row %d" % i
            for f in LANG_REQUIRED:
                if _blank(r.get(f)):
                    v.append((tab, rid, "ERROR", "required field '%s' is empty" % f))
            lvl = str(r.get("level") or "").strip()
            if lvl and lvl not in LEVELS:
                v.append((tab, rid, "ERROR", "level '%s' not in Prompt|Call|Prompt / Call" % lvl))
    return v


def print_lint(viol):
    for tab, rid, sev, msg in viol:
        print("%s %s: %s %s" % (tab, rid, sev, msg))
    ne = sum(1 for x in viol if x[2] == "ERROR")
    nw = sum(1 for x in viol if x[2] == "WARN")
    print("lint: %d ERROR, %d WARN" % (ne, nw))
    return ne


def load_rows(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def cmd_lint(args):
    errors = print_lint(lint(load_rows(args.rows)))
    sys.exit(1 if errors else 0)

# ---------------------------------------------------------------- sheet helpers


def a1(tab, rng=None):
    q = "'%s'" % tab.replace("'", "''")
    return q + ("!" + rng if rng else "")


def col_letter(idx):  # 0-based
    s = ""
    idx += 1
    while idx:
        idx, r = divmod(idx - 1, 26)
        s = chr(65 + r) + s
    return s


def qrange(rng):
    return urllib.parse.quote(rng, safe="!:$")


def get_values(token, sid, rng):
    return gsheets.api(token, "/%s/values/%s" % (sid, qrange(rng))).get("values", [])


def sheet_props(token, sid):
    d = gsheets.api(token, "/%s?fields=sheets.properties(sheetId,title,gridProperties)" % sid)
    return {s["properties"]["title"]: s["properties"] for s in d.get("sheets", [])}


def batch_update(token, sid, requests):
    if not requests:
        return {}
    return gsheets.api(token, "/%s:batchUpdate" % sid, method="POST", body={"requests": requests})


def values_batch_update(token, sid, data):
    return gsheets.api(token, "/%s/values:batchUpdate" % sid, method="POST",
                       body={"valueInputOption": "RAW", "data": data})


def has_data(values, header_rows):
    for row in values[header_rows:]:
        if any(str(c).strip() for c in row):
            return True
    return False

# ---------------------------------------------------------------- write


def planned_tabs(data):
    """[(tab, kind, header_rows, matrix)] in sheet order."""
    plan = []
    if data.get("readme"):
        plan.append((README_TAB, "readme", 0, [list(p) for p in data["readme"]]))
    if data.get("bots"):
        m = [[h for _, h, _ in BOTS_COLS]]
        m += [[str(b.get(k) or "") for k, _, _ in BOTS_COLS] for b in data["bots"]]
        plan.append((BOTS_TAB, "bots", 1, m))
    for tab, rows in (data.get("bot_tabs") or {}).items():
        m = [[h for _, h, _ in BOT_COLS]]
        m += [[str(r.get(k) or "") for k, _, _ in BOT_COLS] for r in rows]
        plan.append((tab, "bot", 1, m))
    for tab, rows in (data.get("language_checks") or {}).items():
        m = [[h for _, h, _ in LANG_COLS]]
        m += [[str(r.get(k) or "") for k, _, _ in LANG_COLS] for r in rows]
        plan.append((tab, "lang", 1, m))
    return plan


def format_requests(gid, kind, nrows, grid_rows):
    base_fmt = {"verticalAlignment": "TOP", "wrapStrategy": "WRAP",
                "textFormat": {"fontFamily": "Arial", "fontSize": 10}}
    if kind == "readme":
        widths, ncols = README_WIDTHS, 2
    else:
        cols = {"bots": BOTS_COLS, "bot": BOT_COLS, "lang": LANG_COLS}[kind]
        widths, ncols = [w for _, _, w in cols], len(cols)
    reqs = [{"repeatCell": {
        "range": {"sheetId": gid, "startRowIndex": 0, "endRowIndex": grid_rows,
                  "startColumnIndex": 0, "endColumnIndex": ncols},
        "cell": {"userEnteredFormat": base_fmt},
        "fields": "userEnteredFormat(verticalAlignment,wrapStrategy,textFormat)"}}]
    for i, w in enumerate(widths):
        reqs.append({"updateDimensionProperties": {
            "range": {"sheetId": gid, "dimension": "COLUMNS", "startIndex": i, "endIndex": i + 1},
            "properties": {"pixelSize": w}, "fields": "pixelSize"}})
    if kind == "readme":
        reqs.append({"repeatCell": {
            "range": {"sheetId": gid, "startRowIndex": 0, "endRowIndex": max(nrows, 1),
                      "startColumnIndex": 0, "endColumnIndex": 1},
            "cell": {"userEnteredFormat": {"textFormat": {"fontFamily": "Arial", "fontSize": 10, "bold": True}}},
            "fields": "userEnteredFormat.textFormat"}})
        return reqs
    reqs.append({"repeatCell": {
        "range": {"sheetId": gid, "startRowIndex": 0, "endRowIndex": 1,
                  "startColumnIndex": 0, "endColumnIndex": ncols},
        "cell": {"userEnteredFormat": dict(base_fmt, backgroundColor=HEADER_BG,
                                           textFormat={"fontFamily": "Arial", "fontSize": 10,
                                                       "bold": True, "foregroundColor": WHITE})},
        "fields": "userEnteredFormat(backgroundColor,verticalAlignment,wrapStrategy,textFormat)"}})
    reqs.append({"updateSheetProperties": {
        "properties": {"sheetId": gid, "gridProperties": {"frozenRowCount": 1}},
        "fields": "gridProperties.frozenRowCount"}})
    if kind in ("bot", "lang"):
        vcol = [k for k, _, _ in (BOT_COLS if kind == "bot" else LANG_COLS)].index(
            "verdict" if kind == "bot" else "result")
        reqs.append({"setDataValidation": {
            "range": {"sheetId": gid, "startRowIndex": 1, "endRowIndex": grid_rows,
                      "startColumnIndex": vcol, "endColumnIndex": vcol + 1},
            "rule": {"condition": {"type": "ONE_OF_LIST",
                                   "values": [{"userEnteredValue": x} for x in VERDICTS]},
                     "showCustomUi": True, "strict": False}}})
    return reqs


def cmd_write(args, token):
    data = load_rows(args.rows)
    if print_lint(lint(data)):
        die("lint ERRORs: refusing to write.")
    plan = planned_tabs(data)
    if args.only_tab:
        known = {p[0] for p in plan}
        missing = [t for t in args.only_tab if t not in known]
        if missing:
            die("--only-tab not in rows file: %s" % ", ".join(missing))
        plan = [p for p in plan if p[0] in args.only_tab]
    if not plan:
        die("nothing to write.")
    sid = args.sheet_id
    props = sheet_props(token, sid)

    # 1. safety: refuse to overwrite filled-in tabs unless --replace-tabs
    blocked = []
    for tab, kind, hdr, matrix in plan:
        if tab in props:
            vals = get_values(token, sid, a1(tab, "A1:Z"))
            if has_data(vals, hdr) and not args.replace_tabs:
                blocked.append(tab)
    if blocked:
        for t in blocked:
            print("BLOCKED: tab '%s' already has data beyond the header (pass --replace-tabs to overwrite)" % t)
        die("refusing to write; nothing was changed.")

    # 2. create missing tabs
    adds = []
    for tab, kind, hdr, matrix in plan:
        if tab not in props:
            adds.append({"addSheet": {"properties": {
                "title": tab, "gridProperties": {"rowCount": max(GRID_ROWS, len(matrix) + 50),
                                                 "columnCount": GRID_COLS}}}})
    if adds:
        rep = batch_update(token, sid, adds)
        for r in rep.get("replies", []):
            p = r["addSheet"]["properties"]
            props[p["title"]] = p
            print("created tab '%s' (gid=%s)" % (p["title"], p["sheetId"]))

    # 3. clear (only when replacing) then write values
    for tab, kind, hdr, matrix in plan:
        if args.replace_tabs:
            gsheets.api(token, "/%s/values/%s:clear" % (sid, qrange(a1(tab))), method="POST", body={})
    values_batch_update(token, sid, [{"range": a1(tab, "A1"), "values": matrix}
                                     for tab, kind, hdr, matrix in plan])

    # 4. formatting
    reqs = []
    for tab, kind, hdr, matrix in plan:
        p = props[tab]
        grid_rows = p.get("gridProperties", {}).get("rowCount", GRID_ROWS)
        reqs += format_requests(p["sheetId"], kind, len(matrix), grid_rows)
    batch_update(token, sid, reqs)
    for tab, kind, hdr, matrix in plan:
        print("wrote '%s': %d row(s) + %s" % (tab, len(matrix) - hdr, "header" if hdr else "no header"))

# ---------------------------------------------------------------- pull / result / add-bug


def header_map(header):
    """Map a sheet header row to (kind, {key: col_index})."""
    norm = [str(h).strip() for h in header]
    by_header = {}
    for cols in (BOT_COLS, LANG_COLS):
        for k, h, _ in cols:
            by_header.setdefault(h.lower(), k)
    idx = {}
    for i, h in enumerate(norm):
        lk = h.lower()
        if lk in CALLS_HEADERS:
            idx["calls"] = i
        elif lk in by_header and by_header[lk] not in idx:
            idx[by_header[lk]] = i
        elif lk.endswith("notes") and "notes" not in idx:
            idx["notes"] = i
    if "id" in idx and "expected" in idx:
        return "bot", idx
    if "level" in idx and "pass_criteria" in idx:
        return "lang", idx
    return None, idx


def read_tab(token, sid, tab):
    props = sheet_props(token, sid)
    if tab not in props:
        die("tab '%s' not found. Tabs: %s" % (tab, ", ".join(props)))
    vals = get_values(token, sid, a1(tab, "A1:Z"))
    if not vals:
        die("tab '%s' is empty." % tab)
    kind, idx = header_map(vals[0])
    if not kind:
        die("tab '%s' header is not a bot-tab or language-checks header: %s" % (tab, vals[0]))
    return props[tab], vals, kind, idx


def row_dict(row, idx):
    return {k: (row[i] if i < len(row) else "") for k, i in idx.items()}


def cmd_pull(args, token):
    _, vals, kind, idx = read_tab(token, args.sheet_id, args.tab)
    keys = [k for k, _, _ in (BOT_COLS if kind == "bot" else LANG_COLS)] + ["calls"]
    rows = []
    for r in vals[1:]:
        if not any(str(c).strip() for c in r):
            continue
        d = row_dict(r, idx)
        rows.append({k: d[k] for k in keys if k in d})
    out = {("bot_tabs" if kind == "bot" else "language_checks"): {args.tab: rows}}
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print("pulled %d row(s) from '%s' to %s" % (len(rows), args.tab, args.out))
    else:
        print(text)


def cmd_result(args, token):
    verdict = args.verdict.strip().upper()
    if verdict not in VERDICTS:
        die("verdict must be one of %s" % ", ".join(VERDICTS))
    _, vals, kind, idx = read_tab(token, args.sheet_id, args.tab)
    if kind != "bot":
        die("'%s' is not a bot tab (needs '#' and 'Expected Response' columns)." % args.tab)
    for k in ("actual", "verdict", "notes"):
        if k not in idx:
            die("tab '%s' has no %s column." % (args.tab, k))
    hits = [n for n, r in enumerate(vals) if n > 0 and len(r) > idx["id"] and r[idx["id"]].strip() == args.id]
    if not hits:
        die("id '%s' not found in tab '%s'; nothing written." % (args.id, args.tab))
    if len(hits) > 1:
        die("id '%s' appears %d times in '%s'; fix the duplicate first." % (args.id, len(hits), args.tab))
    n = hits[0]
    cur = row_dict(vals[n], idx)
    notes = cur.get("notes", "").strip()
    add = (args.notes or "").strip()
    if args.calls and "calls" not in idx:
        add = (add + " · " if add else "") + "calls: " + args.calls.strip()
    if add and add not in notes:
        notes = (notes + " | " + add) if notes else add
    writes = [("actual", args.actual), ("verdict", verdict), ("notes", notes)]
    if args.calls and "calls" in idx:
        writes.append(("calls", args.calls.strip()))
    data = [{"range": a1(args.tab, "%s%d" % (col_letter(idx[k]), n + 1)), "values": [[v]]} for k, v in writes]
    values_batch_update(token, args.sheet_id, data)
    if cur.get("actual") or cur.get("verdict"):
        print("previous: verdict=%r actual=%r" % (cur.get("verdict"), cur.get("actual")))
    print("'%s' %s (sheet row %d): verdict=%s, notes=%r" % (args.tab, args.id, n + 1, verdict, notes))


def cmd_add_bug(args, token):
    p, vals, kind, idx = read_tab(token, args.sheet_id, args.tab)
    if kind != "bot":
        die("'%s' is not a bot tab." % args.tab)
    want = args.after_phase.strip().lower()
    phase_rows = [n for n, r in enumerate(vals) if n > 0 and len(r) > idx["phase"]
                  and r[idx["phase"]].strip().lower() == want]
    if not phase_rows:
        phases = []
        for r in vals[1:]:
            if len(r) > idx["phase"] and r[idx["phase"]] and r[idx["phase"]] not in phases:
                phases.append(r[idx["phase"]])
        die("phase '%s' not found in '%s'. Phases: %s" % (args.after_phase, args.tab, " | ".join(phases)))
    ids = [r[idx["id"]].strip() for r in vals[1:] if len(r) > idx["id"] and r[idx["id"]].strip()]
    parsed = [m.groups() for m in (re.match(r"^(.*?)(\d+)$", i) for i in ids) if m]
    if not parsed:
        die("no numbered ids in '%s' to derive a prefix from." % args.tab)
    prefix = collections.Counter(pfx for pfx, _ in parsed).most_common(1)[0][0]
    nums = [(int(num), len(num)) for pfx, num in parsed if pfx == prefix]
    width = max(w for _, w in nums)
    new_id = "%s%0*d" % (prefix, width, max(x for x, _ in nums) + 1)

    run_date = args.run_date or datetime.date.today().isoformat()
    row = {"id": new_id, "phase": args.phase or vals[phase_rows[-1]][idx["phase"]],
           "scenario": args.scenario, "tester_says": args.tester_says, "expected": args.expected,
           "language": args.language, "direction": args.direction, "type": args.type,
           "priority": args.priority, "actual": args.actual or "", "verdict": (args.verdict or "").upper(),
           "notes": "NEW BUG found in run %s: %s" % (run_date, args.notes or "")}
    viol = [(args.tab, new_id, s, m) for s, m in lint_bot_row(args.tab, row)]
    if print_lint(viol):
        die("lint ERRORs on the new row: refusing to add.")

    insert_at = phase_rows[-1] + 1  # 0-based index of the new sheet row
    batch_update(token, args.sheet_id, [{"insertDimension": {
        "range": {"sheetId": p["sheetId"], "dimension": "ROWS",
                  "startIndex": insert_at, "endIndex": insert_at + 1},
        "inheritFromBefore": True}}])
    ncols = max(idx.values()) + 1
    line = [""] * ncols
    for k, i in idx.items():
        if k in row:
            line[i] = row[k]
    values_batch_update(token, args.sheet_id, [{"range": a1(args.tab, "A%d" % (insert_at + 1)), "values": [line]}])
    print("added %s to '%s' at sheet row %d (after phase '%s')" % (new_id, args.tab, insert_at + 1, args.after_phase))

# ---------------------------------------------------------------- cli


def build_parser():
    p = argparse.ArgumentParser(prog="testcase_sheet.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("lint", help="lint a rows.json file")
    s.add_argument("rows")
    s = sub.add_parser("write", help="write rows.json into a spreadsheet")
    s.add_argument("rows")
    s.add_argument("--sheet-id", required=True)
    s.add_argument("--replace-tabs", action="store_true", help="overwrite tabs that already hold data")
    s.add_argument("--only-tab", action="append", help="write only this tab (repeatable)")
    s = sub.add_parser("pull", help="read a tab back into rows.json shape")
    s.add_argument("--sheet-id", required=True)
    s.add_argument("--tab", required=True)
    s.add_argument("--out")
    s = sub.add_parser("result", help="record a result for one row, found by its # id")
    s.add_argument("--sheet-id", required=True)
    s.add_argument("--tab", required=True)
    s.add_argument("--id", required=True)
    s.add_argument("--verdict", required=True)
    s.add_argument("--actual", required=True)
    s.add_argument("--notes")
    s.add_argument("--calls")
    s = sub.add_parser("add-bug", help="insert a new row for a newly found bug")
    s.add_argument("--sheet-id", required=True)
    s.add_argument("--tab", required=True)
    s.add_argument("--after-phase", required=True)
    s.add_argument("--phase", help="phase for the new row (default: the --after-phase value)")
    s.add_argument("--scenario", required=True)
    s.add_argument("--tester-says", required=True)
    s.add_argument("--expected", required=True)
    s.add_argument("--language", required=True)
    s.add_argument("--direction", required=True)
    s.add_argument("--type", default="Manual", choices=TYPES)
    s.add_argument("--priority", required=True, choices=PRIORITIES)
    s.add_argument("--actual")
    s.add_argument("--verdict")
    s.add_argument("--notes")
    s.add_argument("--run-date", help="YYYY-MM-DD (default today)")
    return p


def main(argv):
    args = build_parser().parse_args(argv)
    if args.cmd == "lint":
        return cmd_lint(args)
    token = gsheets.access_token(gsheets.load_key())
    {"write": cmd_write, "pull": cmd_pull, "result": cmd_result, "add-bug": cmd_add_bug}[args.cmd](args, token)


if __name__ == "__main__":
    main(sys.argv[1:])
