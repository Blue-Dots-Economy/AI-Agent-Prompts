#!/usr/bin/env python3
"""Correct the stale premise in the apply_job tool description.

The description told the model the failure reason is one it "usually CANNOT read". That was true
when it was written and is not true now: `__RAYA_TOOL_DEBUG__` carries
`response_body_excerpt={"error":"NAME"}` and 67 of 73 observed apply failures name the error.

The stale clause primes the model to treat every failure as unreadable, which is exactly the
45-of-60 defect: `ACTION_LIMIT_REACHED` comes back, the model does not look, and the caller is
told the apply did not go through. Two prompt-side mechanisms were tried first (naming the error
in Row 1; excluding it from the generic row) and both failed -- `6caf1fbe` and `513a1d01`. A tool
description is read at the moment of use, which is why D52/D51 got 9/9 with the same move.

Usage: fix_applyjob_desc.py plan|apply
"""
import copy
import json
import os
import sys
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD = ('on failure an error whose reason you usually CANNOT read (if it IS readable and names '
       'ACTION_LIMIT_REACHED or a duplicate, the caller already applied - say so plainly, never '
       'call it technical)')
NEW = ('on failure an error NAMING its reason in "error":"..." - READ IT. ACTION_LIMIT_REACHED, '
       'or any message that a request already exists, means the caller ALREADY APPLIED: say so '
       'plainly, never call it a failure')

# Raya caps a tool description at 1024 characters ("Tool description is required and must be 1024
# characters or fewer"), and these run at ~968, so the replacement has to fit the space the old
# clause occupied plus the ~56 chars of headroom.
MAX_DESC = 1024


def env():
    e = {}
    for line in open(os.path.join(REPO, 'raya/.env')):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            e[k.strip()] = v.strip()
    return e


def raya(path, method='GET', body=None):
    e = env()
    req = urllib.request.Request(
        e['RAYA_BASE_URL'].rstrip('/') + path,
        data=json.dumps(body).encode() if body else None,
        method=method,
        headers={'X-API-Key': e['RAYA_API_TOKEN'], 'Content-Type': 'application/json',
                 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()[:300].decode('utf8', 'replace')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'plan'
    targets = [t for t in json.load(open(os.path.join(REPO, 'raya/agents.json')))['targets']
               if t.get('kind') == 'conversation'
               and t['id'].startswith(('kkb', 'maya'))]
    done = skipped = failed = 0
    for t in targets:
        uuid = (t.get('raya_agent_id') or {}).get('prod')
        if not uuid:
            continue
        s, d = raya('/api/agent/' + uuid)
        if s != 200:
            print('  %-22s GET %s' % (t['id'], s)); failed += 1; continue
        d = d.get('data', d)
        tools = d.get('tools') or {}
        new = copy.deepcopy(tools)
        hit = False
        for tool in (new.get('llm_tools') or []):
            fn = tool.get('function') or {}
            if fn.get('name') != 'apply_job':
                continue
            cur = fn.get('description') or ''
            if NEW[:60] in cur:
                print('  %-22s already corrected' % t['id']); skipped += 1; hit = True; break
            if OLD not in cur:
                print('  %-22s stale clause NOT found (description differs)' % t['id'])
                skipped += 1; hit = True; break
            cand = cur.replace(OLD, NEW)
            if len(cand) > MAX_DESC:
                print('  %-22s would exceed the %d-char cap (%d) - not sent'
                      % (t['id'], MAX_DESC, len(cand)))
                skipped += 1; hit = True; break
            fn['description'] = cand
            hit = True
            if mode != 'apply':
                print('  %-22s would update' % t['id']); done += 1; break
            s2, _ = raya('/api/agent/' + uuid, 'PATCH', {'tools': new})
            s3, d3 = raya('/api/agent/' + uuid)
            d3 = d3.get('data', d3)
            ok = s2 == 200 and json.dumps(d3.get('tools'), sort_keys=True) == json.dumps(
                new, sort_keys=True)
            print('  %-22s PATCH=%s readback_ok=%s' % (t['id'], s2, ok))
            done += 1 if ok else 0
            failed += 0 if ok else 1
            break
        if not hit:
            print('  %-22s no apply_job tool' % t['id']); skipped += 1
    print('\n%s: %d updated, %d skipped, %d failed' % (mode, done, skipped, failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
