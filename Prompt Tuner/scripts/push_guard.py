#!/usr/bin/env python3
"""push_guard.py - refuse a push that would publish a secret or a new personal phone number.

This repo is PUBLIC (github.com/parthekstep/Prompt-Tuner), and it has leaked live API keys once
before (see memory: secret-leak-e2e-snapshots). Every push is scanned first, by the pre-push hook in
.githooks/. It looks only at lines ADDED by the commits being pushed.

Blocks on:
  * any secret value found in raya/.env or secrets/**/*.json (compared by value, never printed)
  * key-shaped strings: sk-..., ghp_/gho_..., AIza..., private keys, x-api-key / Bearer values
  * a Raya tool snapshot file (*.tools*.json), which embeds live keys
  * a 10-digit Indian mobile number that is not one of our test lines AND is not already public
    in the remote branch (a number already on GitHub is not a new leak; mask it at the source)

Usage:
  python3 scripts/push_guard.py [<remote_ref>]      # default: origin/<current branch>
Exit 0 = clean, 1 = blocked (prints file + what, never the secret itself).
Bypass for a reviewed false positive: git push --no-verify
"""
import glob, json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout


branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
base = sys.argv[1] if len(sys.argv) > 1 else f"origin/{branch}"
if subprocess.run(["git", "rev-parse", "--verify", "-q", base], capture_output=True).returncode != 0:
    base = git("merge-base", "HEAD", "origin/main").strip() or "HEAD~1"

# our own test lines and dummies; anything else must already be public to pass
ALLOW = {"1204404272", "1204404273", "1204404274", "1204413383", "7946350283", "7946350285",
         "8037006352", "9876543210"}

secrets = set()
if os.path.exists("raya/.env"):
    for line in open("raya/.env"):
        if "=" in line and not line.strip().startswith("#"):
            v = line.split("=", 1)[1].strip().strip('"').strip("'")
            if len(v) > 12 and not v.startswith("http"):
                secrets.add(v)


def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and len(v) > 16 and any(w in k.lower() for w in ("key", "secret", "token", "private")):
                secrets.add(v)
            walk(v)
    elif isinstance(o, list):
        for x in o:
            walk(x)


for p in glob.glob("secrets/**/*.json", recursive=True):
    try:
        walk(json.load(open(p)))
    except Exception:
        pass

RX = {"OpenAI/Anthropic-style key": r"\bsk-[A-Za-z0-9_\-]{16,}", "GitHub token": r"\bgh[opsu]_[A-Za-z0-9]{20,}",
      "Google API key": r"AIza[A-Za-z0-9_\-]{20,}", "private key": r"BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY",
      "x-api-key value": r"(?i)x-api-key['\"]?\s*[:=]\s*['\"][A-Za-z0-9._\-]{16,}", "Bearer token": r"Bearer\s+[A-Za-z0-9._\-]{24,}"}
MOB = re.compile(r"(?<![0-9A-Za-z])(?:\+?91[\s-]?)?([6-9]\d{9})(?![0-9])")

diff = git("diff", "-U0", f"{base}..HEAD")
added, cur = {}, None
for l in diff.splitlines():
    if l.startswith("+++ b/"):
        cur = l[6:]
    elif l.startswith("+") and not l.startswith("+++") and cur:
        added.setdefault(cur, []).append(l[1:])

problems = []
for f in added:
    if re.search(r"tools.*\.json$", f) and "toolspecs/" not in f:
        problems.append(f"{f}: looks like a Raya tool snapshot (these embed live keys)")
public_cache = {}
for f, lines in added.items():
    text = "\n".join(lines)
    for s in secrets:
        if s in text:
            problems.append(f"{f}: contains a secret value from raya/.env or secrets/ (value not shown)")
    for name, rx in RX.items():
        if re.search(rx, text):
            problems.append(f"{f}: {name}")
    for m in MOB.finditer(text):
        n = m.group(1)
        if n in ALLOW or n.startswith("8888"):
            continue
        if n not in public_cache:
            public_cache[n] = subprocess.run(["git", "grep", "-q", n, base, "--"], capture_output=True).returncode == 0
        if not public_cache[n]:
            problems.append(f"{f}: new phone number ending {n[-4:]} (mask it, e.g. XXXXXX{n[-4:]}, unless it is a test number)")

if problems:
    print(f"push_guard: BLOCKED ({len(problems)} finding(s)) for {base}..HEAD")
    for p in sorted(set(problems)):
        print("  -", p)
    print("Fix and amend, or if reviewed as a false positive: git push --no-verify")
    sys.exit(1)
print(f"push_guard: clean ({len(added)} files scanned, {base}..HEAD)")
