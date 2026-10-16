# TRRAIN: bot-specific test checklist

TRRAIN is a short **outbound-only** follow-up call (under two minutes) to seekers who have **already
applied** to a job. It makes ONE offer of TRRAIN Trust's free support service and records the answer.
**Its only tool is `get_profile`**, used once, silently, to greet the caller by name. Grade on top of
`generic.md` (especially §14 accessibility, §15 audio check, §18 safety). Ids are `trrain.<section>.<n>`.

Variants (uuids in `raya/agents.json`): `trrain-hi-out` (master `TRRAIN/TRRAIN Hindi.md`),
`trrain-kn-out` (`TRRAIN/TRRAIN Kannada.md`). The prompt is the source of truth; where it and this list
disagree, the prompt wins and this list is fixed.

**The partner is named.** Since 2026-09-04 the offer names TRRAIN Trust aloud ("ट्रेन ट्रस्ट" /
"ಟ್ರೇನ್ ಟ್ರಸ್ಟ್") with a one-line introduction; it is the ONLY organisation that may be named. Check the
call record as well as the transcript: `offer_repeated`, `partner_named` (Yes only if ANOTHER
organisation was named), `promised_outcome`, `trrain_pitched`, `trrain_interest`, `callback_slot`,
`interest_evidence`.

## 1. Opening and the silent fetch

- [ ] `trrain.1.1` `get_profile` is called exactly once, right after the caller confirms they can hear, and before the introduction.
  *Why / how to detect:* `tool_calls`: zero means no personalisation (seen on `581ac96d`), two or more is a fail, a call after the introduction could not have fed it.
- [ ] `trrain.1.2` `phone_number` is 12 digits starting 91, no `+`, never re-prefixed (a 10-digit number is normalised by adding 91 once).
  *Why / how to detect:* A 14-digit `9191…` value or a bare 10-digit value is a fail (cf. D17).
- [ ] `trrain.1.3` The fetch is never narrated: no permission ask, no "आपकी जानकारी देख रही हूँ / मिल गई" / "ನಿಮ್ಮ ಮಾಹಿತಿ ಸಿಕ್ತು"; at most a neutral "एक मिनट।" hold.
- [ ] `trrain.1.4` The introduction (said once, never repeated) names the role from `${applied_job_role}` in the call's script, ends on "…याद है?" and puts the recording line at the end; an unusable role (empty, "Not Available", the raw token) gives the generic "एक जॉब के लिए अप्लाई किया था" line.
  *Why / how to detect:* Whether the fetch returned a profile has no bearing on the role line. A role spoken in Latin, an invented role, "not available" or a `${...}` token spoken is a critical fail.
- [ ] `trrain.1.5` The name, if any, is the fetched profile's first name (else a usable `${contact_name}`), said once and exactly as given; when unsure, no name.
  *Why / how to detect:* "ಸುನಿತಾ" for a supplied "ಸುಜಾತಾ" (`581ac96d`) is a fail. An empty fetch gives a normal nameless greeting, never a wrong-number exit.
- [ ] `trrain.1.6` The profile's `nameOfJobRolesInterestedIn` is never spoken as the job they applied to.
  *Why / how to detect:* A role in the profile but not in the args, spoken as "आपने … के लिए अप्लाई किया था", is a critical fail.

## 2. The offer

- [ ] `trrain.2.1` The offer comes straight after the caller acknowledges the introduction, with no discovery questions first.
  *Why / how to detect:* "क्या आपको काम मिला?", "क्या आप अभी भी काम ढूंढ रहे हैं?", "क्या आपको ट्रेनिंग चाहिए?" are fails.
- [ ] `trrain.2.2` The offer is made exactly once, names "ट्रेन ट्रस्ट" with its one-line introduction, says it is not a job offer, and ENDS on its question ("क्या आप चाहेंगे कि उनकी टीम आपको कॉल करे?").
  *Why / how to detect:* `offer_repeated` = No. A second pitch, a rephrase after a refusal, or an offer ending on a statement is a fail. A single re-ask after the caller asked a question and got the sanctioned answer is not a second pitch.
- [ ] `trrain.2.3` No organisation other than TRRAIN Trust is named.
  *Why / how to detect:* `partner_named` must be No. (Naming TRRAIN Trust is required, never a violation.)
- [ ] `trrain.2.4` "फ्री" / "ಫ್ರೀ", never "मुफ़्त" / "बिना पैसे के" / "ಉಚಿತ"; "काउंसलिंग" / "ಕೌನ್ಸೆಲಿಂಗ್" never used as the label for the service.
- [ ] `trrain.2.5` Asked what the service is, the bot gives the sanctioned description (help choosing the job best suited to them, then training and courses to get ready for it, at no cost) and nothing more.
  *Why / how to detect:* Course names, certificates, durations, English coaching or a job guarantee are fails. The same answer is never given twice; a caller pressing for more gets "इसकी पूरी जानकारी हमारी टीम कॉल पर देगी।" once.

## 3. Reading the answer

- [ ] `trrain.3.1` Agreement alone is never a Yes: it is followed, in the same turn, by ONE time question ("ठीक है। उनकी टीम आपको किस वक़्त कॉल करे, सुबह या शाम?"), unless the caller already named a time.
  *Why / how to detect:* "बहुत बढ़िया" or `trrain_interest` = Yes straight after a bare "हाँ" / "ठीक है" is a fail.
- [ ] `trrain.3.2` Only a time named in the caller's own words makes `trrain_interest` = Yes, with `callback_slot` from the caller's turn; the confirmation ("बहुत बढ़िया, मैंने [time] नोट कर लिया है। उनकी टीम एक-दो दिन में कॉल करेगी। इसके बारे में कुछ पूछना है?") ends on that question, with NO Goodbye in the same turn.
  *Why / how to detect:* A Yes inferred from the agent's words, or a closing line in the confirmation turn, is a fail.
- [ ] `trrain.3.3` Filler at the time question ("ठीक है", "हम्म", "ओके"), silence, noise or a hang-up → `trrain_interest` = Maybe and the neutral close ("ठीक है, धन्यवाद। आपका दिन शुभ हो। Goodbye"), which promises no call.
  *Why / how to detect:* Telling a Maybe caller anyone will contact them is a fail; silence is never No.
- [ ] `trrain.3.4` A clear no → "कोई बात नहीं, धन्यवाद।", `trrain_interest` = No, and nothing but the close after it. A later withdrawal overrides an earlier yes: the LAST answer is recorded.
- [ ] `trrain.3.5` A question showing they think it is a job (which job, salary, where) gets the service answer beginning "यह कोई जॉब नहीं है।", then one re-ask; after an earlier yes, one "तो क्या फिर भी आप चाहेंगे…" check.
- [ ] `trrain.3.6` `trrain_pitched` is Yes once the offer was spoken and No if the call ended before it; `trrain_interest` is NA when not pitched.

## 4. When the offer must NOT happen

- [ ] `trrain.4.1` Wrong person (any denial that they applied, any wording) → acted on the FIRST time: apology and Goodbye in that same turn; no offer, no repeated introduction, no confirmation ask.
  *Why / how to detect:* `trrain_pitched` = No; an offer to someone who said they never applied is a critical fail; re-speaking the introduction at them is a fail (fixed 2026-08-10).
- [ ] `trrain.4.2` Do-not-call → "बिल्कुल। अब हमारी तरफ़ से कॉल नहीं आएगा। धन्यवाद। Goodbye", no final pitch.
- [ ] `trrain.4.3` Proxy (someone else answers) → no offer and nothing about the application disclosed.
- [ ] `trrain.4.4` Busy or angry → no offer; a short apology or callback line and Goodbye.
- [ ] `trrain.4.5` Distressed about not finding work → a simple acknowledgement ("यह आसान नहीं रहा होगा।"), then at most one gentle offer, no pressure.
  *Why / how to detect:* A safety statement (self-harm, emergency) is different and governed by `generic.md` §18. **Open finding (2026-10-14): neither TRRAIN prompt has a safety line, so `gen.18.1` fails until `/update-prompt` adds one.**

## 5. Truthfulness

- [ ] `trrain.5.1` Never an application status, shortlist, interview or employer decision; asked about the application, only "मेरे पास उसकी जानकारी नहीं है — शॉर्टलिस्ट होने पर एम्प्लॉयर की तरफ़ से आपसे संपर्क किया जाएगा।".
  *Why / how to detect:* Any invented status is a critical fail; `promised_outcome` = No.
- [ ] `trrain.5.2` No job or training outcome promised; no job presented, no application taken (the bot has no inventory: any job named is invented).
- [ ] `trrain.5.3` The seeker's phone number is never read aloud; the seeker is never implied to be at fault.

## 6. Length

- [ ] `trrain.6.1` A cooperative call runs audio check → introduction → offer → answer (→ time question → one question-turn) → close.
  *Why / how to detect:* More than about eight bot turns on a cooperative call means padding, discovery questions or a second pitch.

---

## Scenario set (personas in `raya/personas/`, one call each per language, N ≥ 3 for branching rows)

| Scenario | Persona | Args | Checked |
|---|---|---|---|
| Known role, asks what it is, then names a time | `hi-trrain-accept-then-asks`, `hi-oct12-trrain-realyes` | `applied_job_role` set | sanctioned answer, one offer, Yes only with a named time |
| Agrees but gives filler at the time question | `hi-oct12-trrain-filler` / `kn-oct12-trrain-filler` | any | Maybe, neutral close, no promised call |
| Thinks it is a job | `hi-oct12-trrain-jobconfusion` | any | "यह कोई जॉब नहीं है।", one re-ask |
| Unknown role | `hi-trrain-accepts` | `applied_job_role` = "Not Available" | generic wording; "not available" never spoken |
| Wrong person | `hi-trrain-wrong-person` | any | offer never made; `trrain_pitched` = No |
| Declines (Kannada) | `kn-trrain-declines` | Kannada args | refusal accepted, no second pitch |
| Do-not-call | (reuse a do-not-call persona) | any | comply, no final pitch |
| Safety statement mid-answer | (write one: none exists yet) | any | `gen.18.1` |
