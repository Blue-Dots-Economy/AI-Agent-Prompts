#!/usr/bin/env python3
"""Resolve an 8-char call-uuid prefix to the full uuid, given the agent uuid prefix.

The sweep results TSV keeps only 8 chars, and the per-dial log filenames collide whenever one
target is dialled more than once in a pass -- so the logs are not a reliable source. This asks
Raya instead.
"""
import json
import sys
import urllib.request


def env():
    e = {}
    for line in open('raya/.env'):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            e[k.strip()] = v.strip()
    return e


def main():
    if len(sys.argv) < 3:
        print('usage: resolve_uuid.py <agent-uuid-prefix> <call-uuid-prefix>')
        return 2
    agent_pfx, call_pfx = sys.argv[1], sys.argv[2]
    e = env()
    base = e['RAYA_BASE_URL'].rstrip('/')
    hdr = {'X-API-Key': e['RAYA_API_TOKEN'], 'User-Agent': 'Mozilla/5.0'}

    # find the full agent uuid from agents.json by prefix
    agent = None
    for t in json.load(open('raya/agents.json'))['targets']:
        uid = (t.get('raya_agent_id') or {}).get('prod') or ''
        if uid.startswith(agent_pfx):
            agent = uid
            break
    if not agent:
        return 1
    try:
        req = urllib.request.Request(
            '%s/api/call?agent_id=%s&limit=100' % (base, agent), headers=hdr)
        d = json.load(urllib.request.urlopen(req, timeout=60))
    except Exception:
        return 1
    for c in (d.get('calls') or []):
        if str(c.get('uuid', '')).startswith(call_pfx):
            print(c['uuid'])
            return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
