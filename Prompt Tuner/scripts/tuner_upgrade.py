#!/usr/bin/env python3
"""tuner_upgrade.py: bring a COPY of the Prompt Tuner up to date with the parent repo, without touching
the copy's own bots.

Teams run their own copies (Purple Dots, Orange Dots). An upgrade made in the parent never reaches a copy
on its own, and copying files across by hand loses either the parent's fixes or the copy's local changes.
This does a three-way merge per file: the version both sides last shared (the base), the copy's version,
and the parent's latest.

  python3 scripts/tuner_upgrade.py status          # what changed upstream since the last sync; no writes
  python3 scripts/tuner_upgrade.py plan            # per-file decision, no writes
  python3 scripts/tuner_upgrade.py apply           # write the clean ones; conflicts go to .tuner-upgrade/
  options: --repo <git url> --branch <name> --base <commit> --allow-deletes --here <path>

What it touches (the TUNER: shared machinery)  .claude/skills/**, scripts/**, raya/regression/*.py,
  raya/regression/README.md, raya/translations/lexicon.json, raya/translations/style/**,
  raya/testcases/sheet-template.json, raya/README.md, raya/endpoints.json, .githooks/**, and the docs
  docs/WORKFLOW.md, docs/WHAT-YOU-CAN-ASK.md, docs/SKILL-STANDARD.md, docs/MULTI-PROJECT-ROADMAP.md.
  CLAUDE.md, .gitignore and raya/voices.json are MERGED: the copy's own lines (its path map, its accounts)
  stay, the parent's new rules come in.
What it never touches (the copy's OWN work)  every bot folder, raya/agents.json, raya/divergences.json,
  raya/intake/, raya/testcases/ (except the template), raya/personas/, raya/translations/<bot> records,
  raya/.env, secrets/, deploy history, reports, snapshots, demo/, .github/.

Per file: parent unchanged since base -> keep the copy's; copy unchanged since base -> take the parent's;
both changed -> merge, and if the same lines changed on both sides it is a CONFLICT: the copy's file is
left as it is and the merged-with-markers version is written to .tuner-upgrade/conflicts/<path> to resolve.
A file the parent deleted is only deleted with --allow-deletes. The base is the commit recorded in
.tuner-upstream.json from the last sync; on a first sync it is found automatically (the parent commit whose
tuner files are closest to the copy's). The parent itself is detected and left alone.
"""
import argparse, datetime, hashlib, json, os, shutil, subprocess, sys, tempfile

DEFAULT_REPO = "https://github.com/parthekstep/Prompt-Tuner.git"
DEFAULT_BRANCH = "control-center"
STATE = ".tuner-upstream.json"
TUNER = [".claude/skills/", "scripts/", ".githooks/", "raya/translations/style/"]
TUNER_FILES = {"raya/regression/README.md", "raya/translations/lexicon.json", "raya/testcases/sheet-template.json",
               "raya/README.md", "raya/endpoints.json", "docs/WORKFLOW.md", "docs/WHAT-YOU-CAN-ASK.md",
               "docs/SKILL-STANDARD.md", "docs/MULTI-PROJECT-ROADMAP.md"}
MERGED = {"CLAUDE.md", ".gitignore", "raya/voices.json"}


def run(*cmd, cwd=None, check=True):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and p.returncode != 0:
        sys.exit(f"{' '.join(cmd)} failed: {p.stderr.strip()[:400]}")
    return p.stdout


NEVER = (".claude/skills/demo/",)        # the parent's own demo, not part of the shared tuner


def owned(path):
    if path.startswith(NEVER):
        return False
    if path in MERGED or path in TUNER_FILES:
        return True
    if path.startswith("raya/regression/") and path.endswith(".py") and path.count("/") == 2:
        return True
    return any(path.startswith(p) for p in TUNER) and "__pycache__" not in path


def blob(path):
    with open(path, "rb") as f:
        data = f.read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def tree(up, commit):
    out = run("git", "ls-tree", "-r", commit, cwd=up)
    files = {}
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        if owned(path):
            files[path] = meta.split()[2]
    return files


def show(up, commit, path):
    return subprocess.run(["git", "show", f"{commit}:{path}"], cwd=up, capture_output=True).stdout


def local_files(here):
    files = {}
    for root, dirs, names in os.walk(here):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__", ".tuner-upgrade")]
        for n in names:
            rel = os.path.relpath(os.path.join(root, n), here)
            if owned(rel):
                files[rel] = blob(os.path.join(here, rel))
    return files


def find_base(up, head, loc):
    """The parent commit whose tuner files match the copy's best (first sync only)."""
    best, score = None, -1
    for c in run("git", "rev-list", "--max-count=400", head, cwd=up).split():
        t = tree(up, c)
        s = sum(1 for p, h in loc.items() if t.get(p) == h)
        if s > score:
            best, score = c, s
    return best, score


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["status", "plan", "apply"])
    ap.add_argument("--repo"); ap.add_argument("--branch"); ap.add_argument("--base")
    ap.add_argument("--allow-deletes", action="store_true"); ap.add_argument("--here", default=".")
    a = ap.parse_args()
    here = os.path.abspath(a.here)
    st = json.load(open(os.path.join(here, STATE))) if os.path.exists(os.path.join(here, STATE)) else {}
    repo, branch = a.repo or st.get("repo") or DEFAULT_REPO, a.branch or st.get("branch") or DEFAULT_BRANCH

    origin = run("git", "remote", "get-url", "origin", cwd=here, check=False).strip()
    norm = lambda u: (u.rstrip("/")[:-4] if u.rstrip("/").endswith(".git") else u.rstrip("/")).split("github.com")[-1].strip(":/").lower()
    if origin and norm(origin) == norm(repo):
        print(f"This IS the parent tuner ({origin}). Nothing to upgrade: copies pull from here.")
        return

    cache = os.path.join(os.path.expanduser("~"), ".cache", "prompt-tuner-upstream", norm(repo).replace("/", "_"))
    if os.path.isdir(os.path.join(cache, ".git")):
        run("git", "fetch", "-q", "origin", branch, cwd=cache)
    else:
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        run("git", "clone", "-q", "--branch", branch, repo, cache)
    head = run("git", "rev-parse", f"origin/{branch}", cwd=cache).strip()
    loc = local_files(here)
    base = a.base or st.get("synced_commit")
    how = "from the last sync" if base and not a.base else "given"
    if not base:
        base, score = find_base(cache, head, loc)
        how = f"first sync: closest parent commit ({score} of {len(loc)} tuner files identical)"
    B, H = tree(cache, base), tree(cache, head)
    since = run("git", "log", "--oneline", f"{base}..{head}", cwd=cache).splitlines()
    print(f"parent  {repo} @ {branch} {head[:8]}")
    print(f"base    {base[:8]} ({how}); {len(since)} parent commits since")
    if a.cmd == "status":
        for l in since[:20]:
            print("   ", l)
        changed = sorted(p for p in set(B) | set(H) if B.get(p) != H.get(p))
        print(f"{len(changed)} tuner files changed in the parent since the base. Run 'plan' to see what happens to each.")
        return

    plan = []
    for p in sorted(set(B) | set(H) | set(loc)):
        b, h, l = B.get(p), H.get(p), loc.get(p)
        if h == b:
            continue                                   # parent did not change it: the copy's version stands
        if l == h:
            continue                                   # already identical to the parent
        if h is None:
            plan.append(("DELETE" if l == b else "KEEP (parent deleted it, the copy changed it)", p))
        elif l is None and b is None:
            plan.append(("ADD", p))
        elif l is None:
            plan.append(("SKIP (the copy deleted it)", p))
        elif l == b:
            plan.append(("UPDATE", p))
        else:
            plan.append(("MERGE", p))
    counts = {}
    for act, _ in plan:
        counts[act.split()[0]] = counts.get(act.split()[0], 0) + 1
    print("plan: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) if plan else "plan: nothing to do, the copy is current")
    if a.cmd == "plan":
        for act, p in plan:
            print(f"  {act:<8} {p}")
        return

    done, conflicts = [], []
    tmp = tempfile.mkdtemp()
    for act, p in plan:
        dst = os.path.join(here, p)
        if act == "ADD" or act == "UPDATE":
            os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
            open(dst, "wb").write(show(cache, head, p)); done.append((act, p))
        elif act == "DELETE":
            if a.allow_deletes:
                os.remove(dst); done.append((act, p))
            else:
                print(f"  kept (parent deleted it; re-run with --allow-deletes): {p}")
        elif act == "MERGE":
            fb, fh = os.path.join(tmp, "base"), os.path.join(tmp, "head")
            open(fb, "wb").write(show(cache, base, p)); open(fh, "wb").write(show(cache, head, p))
            mine = os.path.join(tmp, "mine"); shutil.copyfile(dst, mine)
            r = subprocess.run(["git", "merge-file", "-L", "this copy", "-L", "last shared", "-L", "parent", mine, fb, fh])
            if r.returncode == 0:
                shutil.copyfile(mine, dst); done.append(("MERGED", p))
            else:
                out = os.path.join(here, ".tuner-upgrade", "conflicts", p)
                os.makedirs(os.path.dirname(out), exist_ok=True); shutil.copyfile(mine, out)
                conflicts.append(p)
    for act, p in done:
        print(f"  {act:<8} {p}")
    for p in conflicts:
        print(f"  CONFLICT {p}  (the copy's file is unchanged; merged version with markers: .tuner-upgrade/conflicts/{p})")
    json.dump({"repo": repo, "branch": branch, "synced_commit": head if not conflicts else base,
               "synced_at": datetime.datetime.now().isoformat(timespec="seconds"),
               "pending_conflicts": conflicts}, open(os.path.join(here, STATE), "w"), indent=1)
    if os.path.exists(os.path.join(here, "scripts", "build_fleet_manifest.py")) and \
            os.path.exists(os.path.join(here, "raya", "agents.json")):
        subprocess.run([sys.executable, "scripts/build_fleet_manifest.py"], cwd=here, capture_output=True)
    print(f"\n{len(done)} files updated, {len(conflicts)} conflicts." +
          (" Resolve them, then run apply again (the sync point only moves once there are none)." if conflicts else
           f" Synced to {head[:8]}. Review `git diff`, then commit."))


if __name__ == "__main__":
    main()
