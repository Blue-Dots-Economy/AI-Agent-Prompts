# -*- coding: utf-8 -*-
"""compare_spec.py — what did the slim prompt DROP relative to the fat one?

The rewrite is only safe if every contractual thing survived. This diffs the two prompts'
extracted specs and reports:

  * spoken lines present in FAT and absent from SLIM   <- the thing that must be near-zero
  * tools, input variables and payload identifiers dropped
  * spoken lines that are NEW in slim (should be none — the rewrite invents no speech)

Not every dropped line is a defect: the fat prompt contains six wordings of one rule, five sample
conversations and lines it explicitly DELETES ("this line must never be spoken"), and the whole
point of the rewrite is to keep one of each. So every dropped line is printed for a human to
classify, and the exit code keys off the ones that look contractual.

Matching is on the normalised form from extract_spec.py (whitespace collapsed, `[slots]` and
`${tokens}` reduced), so two wordings of the same line with different slot names still match.

Usage: python3 raya/slim/compare_spec.py <fat.md> <slim.md> [--json out.json]
"""
import argparse, io, json, os, re, sys, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_spec import extract, norm_spoken   # noqa: E402


def close_match(line, pool, cutoff=0.90):
    """Did a near-identical line survive? Guards against a one-word drift being read as a drop."""
    m = difflib.get_close_matches(line, pool, n=1, cutoff=cutoff)
    return m[0] if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fat"); ap.add_argument("slim")
    ap.add_argument("--json", default="")
    ap.add_argument("--max-dropped", type=int, default=0,
                    help="exit 1 if more than this many spoken lines are dropped with no close match")
    a = ap.parse_args()

    fat, slim = extract(a.fat), extract(a.slim)
    fs, ss = set(fat["spoken_lines"]), set(slim["spoken_lines"])

    dropped, drifted = [], []
    for line in sorted(fs - ss):
        near = close_match(line, list(ss))
        (drifted if near else dropped).append((line, near))
    added = sorted(ss - fs)

    print("=" * 78)
    print("FAT : %-52s %7d chars" % (os.path.basename(a.fat), fat["chars"]))
    print("SLIM: %-52s %7d chars   (%.0f%% smaller)"
          % (os.path.basename(a.slim), slim["chars"], 100.0 * (1 - slim["chars"] / fat["chars"])))
    print("=" * 78)

    print("\nSPOKEN LINES  fat=%d  slim=%d  kept=%d  drifted=%d  dropped=%d  new=%d"
          % (len(fs), len(ss), len(fs & ss), len(drifted), len(dropped), len(added)))

    if drifted:
        print("\n  DRIFTED (a near-identical line survived — check the wording is deliberate):")
        for line, near in drifted[:40]:
            print("    fat : %s" % line[:96])
            print("    slim: %s" % near[:96])

    if dropped:
        print("\n  DROPPED (no close match in slim) — classify each:")
        for line, _ in dropped:
            print("    - %s" % line[:150])

    if added:
        print("\n  NEW IN SLIM (the rewrite should invent no speech — check each):")
        for line in added:
            print("    + %s" % line[:150])

    print("\nCONTRACTS")
    for key, label in (("tools", "tools"), ("input_variables", "input variables")):
        lost = sorted(set(fat[key]) - set(slim[key]))
        gained = sorted(set(slim[key]) - set(fat[key]))
        print("  %-16s kept %d/%d%s%s" % (label, len(set(fat[key]) & set(slim[key])), len(fat[key]),
                                          ("   LOST: %s" % lost) if lost else "",
                                          ("   NEW: %s" % gained) if gained else ""))
    fid, sid = set(fat["identifiers"]), set(slim["identifiers"])
    lost_ids = sorted(fid - sid)
    print("  %-16s kept %d/%d" % ("identifiers", len(fid & sid), len(fid)))
    if lost_ids:
        print("     dropped: %s" % ", ".join(lost_ids))

    if a.json:
        io.open(a.json, "w", encoding="utf-8").write(json.dumps(
            {"fat_chars": fat["chars"], "slim_chars": slim["chars"],
             "dropped_spoken": [d[0] for d in dropped], "drifted_spoken": drifted,
             "new_spoken": added, "lost_identifiers": lost_ids}, ensure_ascii=False, indent=1))
        print("\n  -> %s" % a.json)

    sys.exit(1 if len(dropped) > a.max_dropped else 0)


if __name__ == "__main__":
    main()
