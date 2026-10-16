# DKB Employer: bot-specific test checklist

Grade a DKB call (धंधे की बात: verifying and capturing an employer's job postings) on top of
`generic.md`, which already covers the audio check (§15), disclosure position (§1), wrong number and
voicemail (§3, §13), yes/no gates (§4), safety (§18) and language and TTS (§8). Ids are `dkb.<section>.<n>`.

**Variants** (uuids and files in `raya/agents.json`; each graded on its own calls): legacy ONEST
outbound `dkb-hi-out`, `dkb-kn-out`; legacy inbound `dkb-hi-in`, `dkb-kn-in`; Signals outbound
`dkb-hi-signals`, `dkb-kn-signals`. The tool contract differs by backend (§7 legacy, §8 Signals). The
prompt file is the source of truth; where it and this list disagree, the prompt wins and this list is fixed.

## 1. Opening and identity (outbound)

- [ ] `dkb.1.1` Turn 1 (after the audio check) is the identity question only: with a real `${company_name}`, "हैलो! क्या आप [company] से बोल रहे हैं?" with the company spoken in the call's script; with none, "हैलो, क्या आप एक बिज़नेस ओनर हैं?" (Kannada mirror equivalents). No pitch in that turn.
  *Why / how to detect:* A company read in Latin letters (`0da5e1f9`, `199a3b20`), a company taken from an example or from memory when none was sent (`bd60c6b0`, `2ea06509`), or "Not Available" / `[company_name]` / `${company_name}` spoken (`564e1d45`, `be4ab8c3`, 64da1027, b362bf46) is a fail. A missing arg arrives as the raw token and must take the no-name branch.
- [ ] `dkb.1.2` Identity is the city administration's employment initiative, never the government.
  *Why / how to detect:* "गवर्नमेंट एम्प्लॉयमेंट प्रोग्राम", "गवर्नमेंट के साथ मिलकर" (or the Kannada equivalents) anywhere is a fail (`4b2d7dca`).
- [ ] `dkb.1.3` Turn 2 follows a clear yes to Turn 1 and is chosen by `${job_role}` alone: a real role gives the expiry line ("…आपने हमारे प्लेटफॉर्म पर एक जॉब पोस्ट की थी — वो आज एक्सपायर हो जाएगी…"), no real role gives the new-vacancy line (free service, sixteen thousand active seekers in words); both end on the two-minute question.
  *Why / how to detect:* "आपने एक जॉब पोस्ट की थी" when `${job_role}` is empty or "Not Available" is a fail; a company name alone does not mean a job was posted.
- [ ] `dkb.1.4` The AI and recording line ("मैं एक AI assistant हूँ — यह बातचीत record की जा सकती है।") comes once, in Turn 3, only after the owner agrees to two minutes, followed directly by the first phase question with no bridge.
  *Why / how to detect:* The line before the two-minute yes, twice, or missing is a fail.
- [ ] `dkb.1.5` Wrong person: the bot asks to be connected, waits in silence (no "जी" / "हाँ" filler), restarts from Turn 1 for the new person, or closes with "कोई बात नहीं। Goodbye".
- [ ] `dkb.1.6` "Who are you / what is this about" before confirming gets the one sanctioned explanation line and a request to speak to the owner.

## 2. Availability

- [ ] `dkb.2.1` "Talk now" proceeds to Turn 3 and the phase questions; it never gets a callback offer.
  *Why / how to detect:* "कल call कर सकती हूँ?" + Goodbye after a "talk now" answer is a fail (b362bf46; cf. D14).
- [ ] `dkb.2.2` Only a genuine "no time / busy" gets the callback question, with no committed time.

## 3. Which flow: existing postings or a new vacancy

- [ ] `dkb.3.1` With real posted jobs (`${job_role}` present), the first phase question is the freshness check about that real role; the bot does not ask "do you have any postings?".
  *Why / how to detect:* Grounded in 893c8441, 6732681a.
- [ ] `dkb.3.2` With no posted job, the bot goes straight to the new-vacancy line ("…ब्लू डॉट पर आपकी जॉब पोस्टिंग्स लिस्ट करने में हेल्प कर रहे हैं। क्या आपके यहाँ अभी कोई vacancy है?") without explaining the skip or saying "Not Available".
  *Why / how to detect:* "कोई posting नहीं मिली" or "आपके पास कोई data नहीं" before it is a fail.

## 4. Capturing a vacancy

- [ ] `dkb.4.1` Ambiguous or short values (role, salary, vacancy count, experience) get one read-back; clear answers are not re-confirmed.
- [ ] `dkb.4.2` Freshers-or-experienced is its own question whenever experience is missing, never folded into the qualification question and never skipped because years were volunteered; years are asked only when the owner wants experienced people.
  *Why / how to detect:* Grounded in `1be4fc6c` (cf. D23).
- [ ] `dkb.4.3` Working hours and benefits are asked once per new or active job, and never sent in any tool call.
- [ ] `dkb.4.4` Each job's values stay with that job; a new role in a multi-job call is confirmed as new, never overwritten by an earlier job's value or a similar-sounding one.
- [ ] `dkb.4.5` Salary and vacancy numbers are spoken in words (`9c256bb` verified on b187ffeb).

## 5. Posting consent

- [ ] `dkb.5.1` `create_job` fires only after a clear yes to "क्या मैं यह post कर दूँ?".
  *Why / how to detect:* A `create_job` with no consent yes before it is a fail (cf. E2, D14).
- [ ] `dkb.5.2` "हो गया।" only after a real `create_job` success, then the question about more postings.
  *Why / how to detect:* cf. C5; `raya/regression/dkb_employer_integrity.py`.

## 6. Tool silence

- [ ] `dkb.6.1` No tool call is narrated ("मैं update कर रही हूँ", "record हो रहा है", "system"), and `hold_message` is an EMPTY string on every tool call.
  *Why / how to detect:* Spoken turns around each tool call, and `tool_calls[].function.arguments.hold_message` (cf. B2, D34).

## 7. Legacy ONEST tools (`dkb-hi-out`, `dkb-kn-out`, `dkb-*-in`)

- [ ] `dkb.7.1` `get_talent_insights` fires once role and city are known, with English `role` and `location`; the answer is hedged ("यह नंबर बदलता रहता है"), never a guarantee.
  *Why / how to detect:* Low or wrong-city supply (cf3fc048: a Hubli role returned Ghaziabad candidates) gets an honest scarcity line and is routed as a backend issue, not a prompt fix.
- [ ] `dkb.7.2` Phase 1 fires `update_job_status` per discussed job (open or closed; unsure counts as open) before moving on; Phase 2 fires `update_job_details` per turn with only the newly given fields.
  *Why / how to detect:* cf. C1.
- [ ] `dkb.7.3` `create_job` fixed params exact: `sourceService: "ONESTAGENT"`, `eventType: "JOB"`, `app_instance: "up-postjob"`; payload values match what the owner said (one salary figure fills both min and max; `workExperienceYears` only with "Worked before"); `phoneNumber` single-prefixed; all values Latin.
  *Why / how to detect:* cf. C3, C4, D3, D17.

## 8. Signals tools (`dkb-hi-signals`, `dkb-kn-signals`)

- [ ] `dkb.8.1` There is no market-insights step: no candidate count, supply level or salary benchmark is spoken.
  *Why / how to detect:* Any market figure on a Signals call is invented.
- [ ] `dkb.8.2` `create_job` carries `domain: "provider"`, `channel: "voice"`, `network: "blue_dot"`, `item_type: "job_posting_1.0"`, the company in top-level `name`, `phone_number` single-prefixed, the `compliance` array (three consents true, only after the spoken yes), and in `item_state` ONLY `title`, `role`, `natureOfJob`, `positions`, `jobProviderLocation`, `lastRoleHeld`, `hiringManagerName`, `hiringManagerEmail`.
  *Why / how to detect:* Any ONEST param (`sourceService`, `eventType`, `app_instance`, `orgName`, `companyName`, `location`) or a dropped field (salary, qualification, experience, benefits, working hours) returns 400 `INVALID_ITEM_STATE`.
- [ ] `dkb.8.3` `update_job` (with `item_id` = `${job_id}`) fires only for a newly given persisted field (role, vacancies, city), one turn at a time; never for salary, qualification or experience, and never as a made-up status call.
- [ ] `dkb.8.4` Salary, qualification and experience are still asked and acknowledged in conversation, just not sent.
- [ ] `dkb.8.5` The Kannada Signals payload carries the same fields as the Hindi one.
  *Why / how to detect:* Open finding (2026-10-14): `DKB Kannada Signals` lacks `hiringManagerEmail`, `hiringManagerName` and `lastRoleHeld` in its job-posting payload. Grade both on their own calls.

## 9. Inbound (`dkb-hi-in`, `dkb-kn-in`)

- [ ] `dkb.9.1` The first turn is the welcome with the AI and recording line and ONE discovery question; no "we are calling you", no expiry, no two-minute ask; the returning-owner version names only a role from memory's `roles_posted`.
  *Why / how to detect:* Tested by PATCHing an integer `out_did` on the inbound agent and dialling the tester; the bot looks up the caller's number (`/voice-test` → Inbound bots).

## 10. Closing

- [ ] `dkb.10.1` The call ends only when the owner has nothing more, with one recap line and "धन्यवाद। आगे कोई नई जॉब या कोई अपडेट हो, तो हमारी टीम आपसे फिर बात करेगी। Goodbye" (or the mirror's equivalent); the last word is Goodbye.
- [ ] `dkb.10.2` No committed callback date or time, no promise of candidates.
  *Why / how to detect:* "पक्का मिल जाएगा", "गारंटीड", "perfect fit" are fails (Prohibited Language).
