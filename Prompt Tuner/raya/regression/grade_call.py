#!/usr/bin/env python3
"""Grade one live call against the checks that matter, and print PASS/FAIL per check.

Used to turn a sweep of live calls into a per-scenario verdict table. Each check is
answerable from the transcript plus agent_args alone -- no memory store needed, since
the memory store is unreadable from the API.

A check reports SKIP when its precondition never occurred on that call (no job array,
no apply attempt, no location argument). SKIP is not PASS: a sweep whose checks all
SKIP has verified nothing, and the caller of this script must say so.
"""
import json
import os
import re
import sys
import urllib.request

DEV = r'ऀ-ॿ'
KAN = r'ಀ-೿'

LATIN_RUN = re.compile(r'\b[A-Z][A-Za-z]{3,}(?:\s+[A-Z][A-Za-z]{3,})*\b')
BRACKET = re.compile(r'\[[a-z_]{3,}\]')
DIGITS = re.compile(r'\b\d{3,}\b')
LABEL = re.compile(r'(?:^|\s)(?:Qualification|qualification|role|company|location|salary|vacancy)\s*:')
# D81: a spoken stage direction. On e4e81fe2 the bot emitted one naming apply_job and its
# arguments, leaked a profile_id and a job UUID, and then claimed success with zero tools called.
STAGE = re.compile(r'\*\(|Silent tool call|SILENTLY|\bINTERNAL\b')
# A literal "/" inside spoken Devanagari/Kannada text. Tracker item "Slash is said out loud" was
# closed and regressed: 28 of 438 cached calls emit one, usually the array role
# "Computer Operator / Data Entry" read verbatim.
SLASH = re.compile(r'[ऀ-ॿಀ-೿][^\s]{0,20}\s*/\s*[^\s]{0,20}|[^\s]{0,20}\s*/\s*[^\s]{0,20}[ऀ-ॿಀ-೿]')
# Kannada says ಮಾಹಿತಿ ("information"), not �ವಿವರ — an earlier pattern missed the real line on
# 41a2c19d and reported a consent failure that had not happened. Match on the SHARE verb.
DISCLOSE = re.compile(r'personal details|details.*share|share होंगी|जानकारी.*share'
                      r'|(?:ಮಾಹಿತಿ|ವಿವರ).{0,24}ಶೇರ್|ಶೇರ್.{0,24}(?:ಮಾಹಿತಿ|ವಿವರ)')
SALARY = re.compile(r'सैलरी|ಸಂಬಳ')
ALREADY = re.compile(r'पहले से लगी हुई|ಈಗಾಗಲೇ ಇದೆ')
TECH = re.compile(r'technical issue')
# the Kannada line was reworded to share no opening with the old catch-all, so match both
# forms -- an out-of-date pattern here reported a false FAIL on 29288fd3, whose line was right.
NOTCOMPLETE = re.compile(r'पूरा नहीं हो पाया|ಪೂರ್ತಿ ಆಗಿಲ್ಲ|ಸಧ್ಯಕ್ಕೆ ಆಗಿಲ್ಲ')

# words that legitimately appear in Latin inside spoken Hindi/Kannada
OK_LATIN = {
    'Qualification', 'Not', 'Available', 'Goodbye', 'Hello', 'Namaste', 'HR', 'WhatsApp',
    'Data', 'Entry', 'ITI', 'BTech', 'MBA', 'BA', 'BCom', 'BSc', 'Yes', 'No', 'OK', 'Okay',
}

# English words the bot says as part of its OWN lines (disclosure, service offer, wrap-up).
# They are not job names, so they must not count as a stray job token. Kept separate from
# OK_LATIN so it is obvious which list a word belongs in when this needs extending -- and
# this list HAS needed extending twice, so treat a new stray word as a candidate for it
# before treating it as a finding.
OWN_LINES = {
    'personal', 'details', 'share', 'company', 'service', 'provider', 'free', 'option',
    'note', 'phone', 'exact', 'timing', 'shortlist', 'employer', 'message', 'experience',
    'qualification', 'apply', 'position', 'salary',
}


def env():
    e = {}
    for line in open('raya/.env'):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            e[k.strip()] = v.strip()
    return e


def get(path):
    e = env()
    req = urllib.request.Request(
        e['RAYA_BASE_URL'].rstrip('/') + path,
        headers={'X-API-Key': e['RAYA_API_TOKEN'], 'User-Agent': 'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(req, timeout=60))


def grade(call):
    aa = call.get('agent_args') or {}
    tr = call.get('call_transcript') or []
    said = [str(t.get('content') or '') for t in tr if t.get('role') == 'assistant']
    allsaid = '\n'.join(said)
    out = []

    # --- job array integrity -------------------------------------------------
    recs = aa.get('recommendations')
    arr = []
    if recs:
        try:
            arr = json.loads(recs) if isinstance(recs, str) else recs
        except Exception:
            arr = []
    if arr:
        supplied = set()
        for j in arr:
            for k in ('role', 'company'):
                for w in re.findall(r'[A-Za-z]{4,}', str(j.get(k) or '')):
                    supplied.add(w.lower())
        spoke_latin = set()
        for line in said:
            if not SALARY.search(line):
                continue
            for w in re.findall(r'[A-Za-z]{4,}', line):
                spoke_latin.add(w.lower())
        stray = spoke_latin - supplied - {w.lower() for w in OK_LATIN} - OWN_LINES
        out.append(('jobs-from-array-only', 'FAIL' if stray else 'PASS',
                    'stray Latin job tokens: %s' % sorted(stray)[:4] if stray else
                    '%d job(s) supplied' % len(arr)))
    else:
        out.append(('jobs-from-array-only', 'SKIP', 'no job array on this call'))

    # --- Latin script leaking into spoken Devanagari/Kannada ----------------
    leaks = []
    for line in said:
        if not re.search('[%s%s]' % (DEV, KAN), line):
            continue
        for m in LATIN_RUN.findall(line):
            if m.split()[0] in OK_LATIN or m in OK_LATIN:
                continue
            leaks.append(m)
    out.append(('no-latin-in-speech', 'FAIL' if leaks else 'PASS',
                'spoke Latin: %s' % sorted(set(leaks))[:4] if leaks else 'clean'))

    # --- bracket markers read aloud (D77) -----------------------------------
    br = sorted({m for line in said for m in BRACKET.findall(line)})
    out.append(('no-bracket-markers', 'FAIL' if br else 'PASS',
                'spoke %s' % br[:4] if br else 'clean'))

    # --- field labels read aloud (D72) --------------------------------------
    lab = sorted({m.strip() for line in said for m in LABEL.findall(line)})
    out.append(('no-field-labels', 'FAIL' if lab else 'PASS',
                'spoke label %s' % lab[:3] if lab else 'clean'))

    # --- raw digit runs where words are required ----------------------------
    dg = sorted({m for line in said for m in DIGITS.findall(line)})
    out.append(('numbers-in-words', 'FAIL' if dg else 'PASS',
                'spoke digits %s' % dg[:4] if dg else 'clean'))

    # --- literal slash spoken (closed tracker item, regressed) --------------
    sl = sorted({m.strip() for line in said for m in SLASH.findall(line)})
    out.append(('no-literal-slash', 'FAIL' if sl else 'PASS',
                'spoke %s' % sl[:3] if sl else 'clean'))

    # --- stage directions spoken aloud (D81) --------------------------------
    st = sorted({m for line in said for m in STAGE.findall(line)})
    out.append(('no-stage-directions', 'FAIL' if st else 'PASS',
                'spoke a stage direction %s' % st[:3] if st else 'clean'))

    # --- claimed an apply with no apply_job call at all (the worst failure) --
    claimed = re.search(r'अप्लाई हो गया|अप्लाई कर दिया|ಅಪ್ಲೈ ಆಗಿದೆ|ಅಪ್ಲೈ ಮಾಡಿದ್ದೀನಿ', allsaid)
    ran = any((tc.get('function') or {}).get('name') == 'apply_job'
              for t in tr for tc in (t.get('tool_calls') or []))
    if claimed and not ran:
        out.append(('apply-claim-backed-by-tool', 'FAIL',
                    'said the application succeeded but apply_job was NEVER called'))
    elif claimed:
        out.append(('apply-claim-backed-by-tool', 'PASS', 'claim backed by an apply_job call'))
    else:
        out.append(('apply-claim-backed-by-tool', 'SKIP', 'no success claim made'))

    # --- announced the apply more often than it applied ---------------------
    # Tracker: "apply kr rhi hu should appear once only". 52ef63d2 said it 4x for 2 real
    # applies; baf836fe 3x for 2. Announcing without acting is the mild form of the
    # fabricated-apply class.
    ANNOUNCE = re.compile(r'अप्लाई कर रही|अप्लाई कर देती|अप्लाई करती हूँ'
                          r'|ಅಪ್ಲೈ ಮಾಡ್ತೀನಿ|ಅಪ್ಲೈ ಮಾಡ್ತಿದ್ದೀನಿ')
    n_say = sum(1 for line in said if ANNOUNCE.search(line))
    n_ran = sum(1 for t in tr for tc in (t.get('tool_calls') or [])
                if (tc.get('function') or {}).get('name') == 'apply_job')
    if n_say:
        out.append(('apply-announced-once-per-apply', 'FAIL' if n_say > n_ran else 'PASS',
                    'announced %d time(s), applied %d time(s)' % (n_say, n_ran) if n_say > n_ran
                    else 'announced %d, applied %d' % (n_say, n_ran)))
    else:
        out.append(('apply-announced-once-per-apply', 'SKIP', 'never announced an apply'))

    # --- location argument spoken, not substituted --------------------------
    loc = str(aa.get('location') or '').strip()
    if loc and loc.lower() not in ('not available', 'na', 'n/a', 'none', 'null', '-', 'any'):
        base = re.split(r'[,\d]', loc)[0].strip().lower()
        # distinguish the two failure modes: the whole argument read verbatim, versus the
        # place converted correctly with the pin code still attached (29288fd3 was the latter,
        # and calling it "spoke the raw argument" was misleading).
        verbatim = loc.lower() in allsaid.lower()
        digits = bool(re.search(r'[0-9\u0966-\u096f\u0ce6-\u0cef]{5,6}', allsaid))
        if verbatim:
            out.append(('location-not-raw', 'FAIL', 'read the whole argument verbatim: %r' % loc))
        elif digits:
            out.append(('location-not-raw', 'FAIL',
                        'place converted but the pin code was kept (arg %r)' % loc))
        else:
            # NOTE: substitution -- pin code gone, script right, but a DIFFERENT place named
            # (baf0aa57 said "Bengaluru" for "Hubballi, 580020") -- is deliberately NOT checked
            # here. Detecting it means comparing a Latin argument against native-script speech,
            # which needs the transliteration map that location_said.py already carries. A naive
            # substring check false-FAILED the two calls that were actually correct
            # (2bb68def "सरजापुर", aae2e523 "ಸರ್ಜಾಪುರ"). Use location_said.py for substitution.
            out.append(('location-not-raw', 'PASS', 'not raw and no pin code, arg=%r' % loc))
    else:
        out.append(('location-not-raw', 'SKIP', 'no usable location argument'))

    # --- consent before apply ----------------------------------------------
    applies, errs = [], []
    for t in tr:
        for tc in (t.get('tool_calls') or []):
            fn = tc.get('function') or {}
            if fn.get('name') == 'apply_job':
                applies.append(t)
        body = str(t.get('content') or '')
        m = re.search(r'"error":"([A-Z_]+)"', body)
        if m:
            errs.append(m.group(1))
    if applies:
        out.append(('disclosure-before-apply', 'PASS' if DISCLOSE.search(allsaid) else 'FAIL',
                    'disclosure line present' if DISCLOSE.search(allsaid) else 'no disclosure line'))
    else:
        out.append(('disclosure-before-apply', 'SKIP', 'no apply attempted'))

    # --- apply failure wording matches the error actually returned ----------
    if errs:
        e0 = errs[-1]
        if e0 == 'ACTION_LIMIT_REACHED':
            ok = bool(ALREADY.search(allsaid)) and not TECH.search(allsaid)
            why = 'already-applied line' if ok else 'did NOT say already-applied'
        else:
            ok = bool(NOTCOMPLETE.search(allsaid)) and not TECH.search(allsaid)
            why = 'not-complete line (no cause claim)' if ok else 'said technical-issue or wrong line'
        out.append(('failure-line-matches-error', 'PASS' if ok else 'FAIL', '%s -> %s' % (e0, why)))
    else:
        out.append(('failure-line-matches-error', 'SKIP', 'no apply error returned'))

    # --- DKB-specific: it posts jobs, it does not apply to them -------------
    # Without this branch a DKB call grades as "PASS" on four SKIPs, which verifies nothing.
    # The platform DROPS empty arguments, so a DKB call with nothing supplied arrives with
    # only country_code + contact_memory -- bd60c6b0 was exactly that and the whole DKB
    # branch was skipped, hiding an invented business name. Detect by what it SAYS too.
    is_dkb = bool(aa.get('company_name') or aa.get('job_role') or aa.get('num_vacancies')) or (
        re.search(r'बिज़नेस ओनर|ಬಿಸಿನೆಸ್ ಓನರ್|posting है|posting ಇದೆ|से बोल रहे हैं'
                  r'|ನಿಂದ ಮಾತಾಡ್ತಾ', allsaid) is not None)
    if is_dkb:
        created = [t for t in tr
                   for tc in (t.get('tool_calls') or [])
                   if (tc.get('function') or {}).get('name') == 'create_job']
        POSTED = re.compile(r'post कर|पोस्ट कर दिया|ಪೋಸ್ಟ್ ಮಾಡಿ|ಪೋಸ್ಟ್ ಆಗಿದೆ')
        CONSENT = re.compile(r'post कर दूँ|ಪೋಸ್ಟ್ ಮಾಡ್ಲಾ|पोस्ट कर दूँ')
        claimed_post = bool(POSTED.search(allsaid))
        if claimed_post and not created:
            out.append(('post-claim-backed-by-tool', 'FAIL',
                        'said the job was posted but create_job was NEVER called'))
        elif claimed_post:
            out.append(('post-claim-backed-by-tool', 'PASS', 'claim backed by create_job'))
        else:
            out.append(('post-claim-backed-by-tool', 'SKIP', 'no posting claim made'))

        if created:
            out.append(('consent-before-create-job', 'PASS' if CONSENT.search(allsaid) else 'FAIL',
                        'consent line present' if CONSENT.search(allsaid)
                        else 'create_job ran with no spoken consent question'))
        else:
            out.append(('consent-before-create-job', 'SKIP', 'create_job never ran'))

        # the business name must be spoken in the target script, not Latin
        biz = str(aa.get('company_name') or '').strip()
        if biz and re.search('[A-Za-z]{4,}', biz):
            latin_biz = biz.lower() in allsaid.lower()
            out.append(('business-name-in-script', 'FAIL' if latin_biz else 'PASS',
                        'spoke the Latin name %r' % biz if latin_biz
                        else 'converted, arg=%r' % biz))
        elif not biz or biz.lower() in ('not available', 'none', 'null', '-'):
            # company_name ABSENT: the greeting must take the no-name branch. bd60c6b0 graded
            # PASS while the bot greeted the owner with a business name that was never supplied
            # (it came from a worked example printed under the template).
            NAMED = re.compile(r'(?:क्या आप|नीವು|ನೀವು)\s+(.{3,40}?)\s*(?:से बोल|ನಿಂದ ಮಾತಾಡ)')
            m = NAMED.search(allsaid)
            if m and not re.search(r'बिज़नेस ओनर|ಬಿಸಿನೆಸ್ ಓನರ್', m.group(1)):
                out.append(('no-invented-business-name', 'FAIL',
                            'no company_name was supplied yet it greeted %r' % m.group(1).strip()))
            else:
                out.append(('no-invented-business-name', 'PASS',
                            'took the no-name branch'))
        else:
            out.append(('business-name-in-script', 'SKIP', 'no Latin business name supplied'))

    # --- TRRAIN-specific: outbound follow-up, get_profile is its ONLY tool ---
    is_trrain = bool(aa.get('applied_job_role') or aa.get('applied_job_company')) or (
        re.search(r'ट्रेन ट्रस्ट|ಟ್ರೇನ್ ಟ್ರಸ್ಟ್', allsaid) is not None)
    if is_trrain:
        names = [(tc.get('function') or {}).get('name')
                 for t in tr for tc in (t.get('tool_calls') or [])]
        forbidden = [n for n in names if n and n != 'get_profile']
        out.append(('trrain-only-get_profile', 'FAIL' if forbidden else 'PASS',
                    'called %s -- TRRAIN has no other tool' % sorted(set(forbidden))
                    if forbidden else 'get_profile only (%d call(s))' % names.count('get_profile')))

        # TRRAIN Trust is the ONLY partner that may be named, and it must be introduced
        PARTNER = re.compile(r'ट्रेन ट्रस्ट|ಟ್ರೇನ್ ಟ್ರಸ್ಟ್')
        INTRO = re.compile(r'चैरिटेबल|ಚಾರಿಟಬಲ್|ट्रस्ट है|ಟ್ರಸ್ಟ್ ಆಗಿದೆ')
        if PARTNER.search(allsaid):
            out.append(('trrain-partner-introduced', 'PASS' if INTRO.search(allsaid) else 'FAIL',
                        'named with an introduction' if INTRO.search(allsaid)
                        else 'named the partner with no one-line introduction'))
        else:
            out.append(('trrain-partner-introduced', 'SKIP', 'partner never named'))

        # one offer per call, and the call stays short
        OFFER = re.compile(r'फ्री सर्विस|ಫ್ರೀ ಸರ್ವಿಸ್')
        n_off = sum(1 for line in said if OFFER.search(line))
        out.append(('trrain-one-offer', 'FAIL' if n_off > 2 else 'PASS',
                    'offer line spoken %d times' % n_off if n_off > 2 else 'offer spoken %d time(s)' % n_off))

    return out


def main():
    if len(sys.argv) < 2:
        print('usage: grade_call.py <call-uuid> [<call-uuid> ...]')
        return 2
    worst = 0
    for u in sys.argv[1:]:
        try:
            call = get('/api/call/' + u)
        except Exception as exc:
            print('%s  COULD NOT FETCH (%s)' % (u[:8], str(exc)[:60]))
            worst = max(worst, 1)
            continue
        tr = call.get('call_transcript') or []
        rows = grade(call)
        fails = [r for r in rows if r[1] == 'FAIL']
        skips = [r for r in rows if r[1] == 'SKIP']
        # THIN means "this call verified almost nothing", which is about how many checks
        # actually RAN -- not how many skipped. A TRRAIN or DKB call legitimately skips every
        # KKB check, and counting those as thinness hid three passing TRRAIN checks.
        passes = [r for r in rows if r[1] == 'PASS']
        verdict = 'FAIL' if fails else ('PASS' if len(passes) >= 3 else 'THIN')
        print('%s  turns=%-3d  %-4s  (%d checked, %d skipped)'
              % (u[:8], len(tr), verdict, len(passes) + len(fails), len(skips)))
        for name, st, why in rows:
            if st == 'PASS':
                continue
            print('    %-4s %-28s %s' % (st, name, why))
        if fails:
            worst = 1
    return worst


if __name__ == '__main__':
    sys.exit(main())
