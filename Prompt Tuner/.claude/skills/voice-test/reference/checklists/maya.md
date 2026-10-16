# Maya: campus-recruitment bot, test checklist

Maya is the campus-recruitment spin-off of KKB: *माया, [college] की ओर से*, Hindi only today (its
languages come from `raya/agents.json`), feminine voice. Grade a Maya call on top of `generic.md`, and
on top of `kkb.md` for the behaviour Maya inherits (cited by id below, not restated). This file holds
only Maya's own items. Ids are `maya.<section>.<n>`.

**Variants:** outbound `maya-hi-out` (legacy backend) and `maya-hi-signals`; inbound `maya-hi-in` and
`maya-hi-in-signals` (testable: integer `out_did` on the agent, test data on the tester's number). The
prompt file is the source of truth; where it and this list disagree, the prompt wins and this list is
fixed.

**Removed 2026-10-12:** the MPL competition offer (Aryan's request; Maya CHANGELOG "MPL competition
removed from all Ghaziabad Maya bots"). Any mention of MPL, "मार्केटर प्रीमियर लीग" or a competition is
now a fail (`maya.6.1`).

## 1. Campus identity (not government)

- [ ] `maya.1.1` With a real `${college_name}`, the introduction (after the audio check) is "नमस्ते। मैं माया, [college] की ओर से बात कर रही हूँ। …यह बातचीत रिकॉर्ड की जा सकती है। क्या आप [college] के स्टूडेंट हैं और अभी काम ढूंढ रहे हैं?", ending on that one question.
  *Why / how to detect:* Only the `college_name` value decides the opener: dropping the college when one was sent is a fail (`24293fbe`). Open finding: on `maya-hi-signals` the college opener fired on 2 of 14 calls vs 48 of 48 on `maya-hi-out`; cause unconfirmed (`raya/overnight/ESCALATION-litwiz.md` §4). Grade each call; do not explain it in the report as adherence.
- [ ] `maya.1.2` With no usable college (empty, "Not Available", or the raw `${college_name}` token), Maya names no institution: "नमस्ते। मैं माया बोल रही हूँ। …क्या आप अभी काम ढूंढ रहे हैं?".
  *Why / how to detect:* The token or "[college]" spoken (`718aa8ab`), or an invented college, is a fail (cf. D67).
- [ ] `maya.1.3` Never "शहर प्रशासन", "ज़िला प्रशासन" or "गवर्नमेंट" in Maya's identity.
  *Why / how to detect:* cf. D24.
- [ ] `maya.1.4` The college name is spoken in Devanagari, fully transliterated, initialisms as compact words ("LR" → "एलआर", "TPS" → "टीपीएस"); no Latin letter inside a spoken word.
  *Why / how to detect:* "VMLG College" read in Latin (`b6353cfb`); `raya/regression/spoken_form.py --call <uuid>`.
- [ ] `maya.1.5` A clear "no / already working" at the student-and-job question ends politely: no fetch, no jobs, `call_output.not_interested_in_jobs` = Yes.
  *Why / how to detect:* Grounded in `aef648fa` ("Already employed").

## 2. Feminine voice (every turn)

- [ ] `maya.2.1` Every first-person verb Maya speaks is feminine ("कर रही हूँ", "करती हूँ", "सकती हूँ", "देती हूँ", "बताती हूँ"), including improvised, error and fallback turns.
  *Why / how to detect:* Any masculine form ("कर रहा हूँ", "करता हूँ", "सकता हूँ") or a "रहा/रही" double option is a fail (cf. D4).

## 3. Fetch and profile (inherited)

- [ ] `maya.3.1` There is no `new_seeker` fork: every call fetches silently after the caller answers the introduction, then branches on the result. No permission ask ("क्या आपकी कुछ बेसिक जानकारी देख सकती हूँ?" is a fail), no "आपकी जानकारी मिल गई".
  *Why / how to detect:* Graded as `kkb.2.1` to `kkb.2.4`.
- [ ] `maya.3.2` Signals variants: the account-and-terms gate, the returning-caller turn and known-field locking follow KKB.
  *Why / how to detect:* Graded as `kkb.3.*` and `kkb.4.*` (legacy `maya-hi-out` / `maya-hi-in` have no account gate).

## 4. Experience capture (Maya divergence)

- [ ] `maya.4.1` Only when the profile lacks role or experience, Maya asks inline, one beat at a time: "क्या आपको पहले से किसी काम का experience है?" then, if yes, what kind, where, how long; a fresher counts as known.
  *Why / how to detect:* Asking when the profile already has role and experience is a fail (cf. A5, C6); gathering before the fetch has returned is a fail (cf. A1). The answer feeds `create_profile` (`role`, `workExperience`) and `call_output.experience_captured`.

## 5. Jobs, apply and failure (inherited, with Maya's HR number)

- [ ] `maya.5.1` Jobs, location, the data-sharing line before each apply, payloads, the success line and the failure lookup follow KKB.
  *Why / how to detect:* Graded as `kkb.5.*` to `kkb.9.*` on the Signals variants.
- [ ] `maya.5.2` The optional HR-number value line ("अगर आप किसी जॉब में अप्लाई करते हैं, तो जहाँ उपलब्ध होगा, हम कंपनी का एच आर नंबर भी आपके साथ शेयर कर देंगे।") is said at most once, only if some job has an `hr_contact`, never as pressure and never as a promise that HR will call.
- [ ] `maya.5.3` After a SUCCESSFUL apply, a non-empty `hr_contact` of the applied job is shared once, digit by digit in words, after the success line; never before applying, never at the deep-dive, never invented.
  *Why / how to detect:* A number spoken before the `apply_job` success, as digits, or when the job has none is a fail.
- [ ] `maya.5.4` On an apply failure, the recovery is the HR number if the job has one, else one alternate job, else the no-job-left line; never blame, never "आप बाद में call कीजिए", never the same job twice.
  *Why / how to detect:* cf. D15, D27.

## 6. Closing

- [ ] `maya.6.1` No MPL or competition offer anywhere in the call.
  *Why / how to detect:* Grep for MPL, प्रीमियर लीग, कॉम्पिटिशन (removed 2026-10-12; verified absent on `5a0366de`, `0ac19800`; the Signals variants were DEPLOYED, NOT VERIFIED at removal).
- [ ] `maya.6.2` The closing service-provider offer follows `generic.md` §17 and `kkb.11.1` to `kkb.11.3` (Maya's "what is the service" answer is the one sanctioned sentence).
- [ ] `maya.6.3` The read-back after a successful apply is a closed template ending on "सब सही?" with nothing appended.
  *Why / how to detect:* `c260fb90` carried three questions in that turn.

## 7. Language (Hindi, beyond `generic.md` §8)

- [ ] `maya.7.1` Canonical place spellings (गाज़ियाबाद with nukta, इंदिरापुरम, मोहननगर, राजेंद्रनगर, सेक्टर पाँच); no PIN codes, Plus Codes or full addresses read aloud.
  *Why / how to detect:* cf. D26.
- [ ] `maya.7.2` A name stored in another script is spoken in Devanagari ("ಪಾರ್ಥ" → "पार्थ जी").
- [ ] `maya.7.3` No hype or pressure: "गारंटीड जॉब", "बेस्ट ऑपर्च्युनिटी", "हाई पेइंग", "लाइफ चेंजिंग", "पक्का मिलेगा", "सौ प्रतिशत", "आपको करना चाहिए", "अभी decide कीजिए", "यह मौका चला जाएगा"; trade-offs state both sides.
