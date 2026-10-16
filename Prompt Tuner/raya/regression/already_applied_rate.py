#!/usr/bin/env python3
"""Track how often ACTION_LIMIT_REACHED gets the already-applied line.

The existing apply_result_integrity check catches the FALSE direction — claiming an application
exists with no evidence. This tracks the opposite and far more common one: the tool says the
application really does already exist, and the bot tells the caller the apply did not go through.

Baseline measured 2026-09-09, before the fix that excluded ACTION_LIMIT_REACHED from the generic
failure row: the correct line fired on 4 of 34 calls (12%). `ESCALATION-litwiz.md` §1 framed the
same defect as 45 of 60. Re-run this after any change to the apply-failure table; a rate that has
not moved means the change did not work, whatever the individual calls looked like.
"""
import glob
import json
import os
import re
import sys

CACHE = os.environ.get(
    'CALLCACHE',
    '/private/tmp/claude-502/-Users-parthbansal-EkStep-Prompt-Tuner/'
    'cad28c14-40a4-477d-993b-eff663bfb052/scratchpad/callcache')

ALREADY = re.compile(r'पहले से लगी|ಈಗಾಗಲೇ ಇದೆ')
# the generic failure line, in every wording it has had tonight
GENERIC = re.compile(r'पूरा नहीं हो पाया|आगे नहीं बढ़ा है|ಪೂರ್ತಿ ಆಗಿಲ್ಲ|ಸಧ್ಯಕ್ಕೆ ಆಗಿಲ್ಲ|ಮುಂದೆ ಹೋಗಿಲ್ಲ')


def main():
    rows = []
    for p in sorted(glob.glob(os.path.join(CACHE, '*.json'))):
        try:
            f = json.load(open(p, encoding='utf-8'))
        except Exception:
            continue
        tr = f.get('call_transcript') or []
        if not any('ACTION_LIMIT_REACHED' in str(t.get('content') or '') for t in tr):
            continue
        said = ' '.join(str(t.get('content') or '')
                        for t in tr if t.get('role') == 'assistant')
        rows.append({
            'uuid': str(f.get('uuid', ''))[:8],
            'bot': str(f.get('_bot') or ''),
            'when': str(f.get('created_at', ''))[:16],
            'correct': bool(ALREADY.search(said)),
            'generic': bool(GENERIC.search(said)),
        })

    if not rows:
        print('already-applied rate: no ACTION_LIMIT_REACHED calls in the cache')
        return 0
    ok = [r for r in rows if r['correct']]
    wrong = [r for r in rows if not r['correct'] and r['generic']]
    other = [r for r in rows if not r['correct'] and not r['generic']]
    pct = 100.0 * len(ok) / len(rows)
    print('ACTION_LIMIT_REACHED returned on %d call(s)' % len(rows))
    print('  said the already-applied line : %d (%.0f%%)' % (len(ok), pct))
    print('  said the generic failure line : %d   <-- told the caller it did not go through'
          % len(wrong))
    print('  said neither                  : %d' % len(other))
    print()
    print('  baseline before the 2026-09-09 fix: 4 of 34 (12%)')
    print()
    print('  NOTE: if this still reads 4 of 34, check the DATES before concluding anything. As of')
    print('  2026-09-09 no ACTION_LIMIT_REACHED call had occurred since the tool-description fix,')
    print('  so an unchanged rate means NO NEW DATA, not a failed fix. The rate only becomes')
    print('  meaningful once a post-fix call actually returns that error.')
    print()
    print('  2026-09-09 UPDATE: 5bbb6ca1 IS that call -- apply_job invoked, ACTION_LIMIT_REACHED')
    print('  returned, all four prompt-side mechanisms live, and it still spoke the generic line')
    print('  three times. The rate is expected to stay at 12% until the runtime owns this.')
    if wrong:
        print()
        print('  most recent wrong-line calls:')
        for r in sorted(wrong, key=lambda x: x['when'], reverse=True)[:6]:
            print('   %s %s %s' % (r['when'], r['uuid'], r['bot']))
    # not a pass/fail gate: this is a RATE. Exit non-zero only if it is worse than baseline.
    return 1 if pct < 12.0 else 0


if __name__ == '__main__':
    sys.exit(main())
