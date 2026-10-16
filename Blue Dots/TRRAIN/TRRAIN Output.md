Analyse the call transcript and extract the following information. 
If a value is not present, use "NA" for strings, [] for arrays, or 0 for counts.

1. seeker_name — The seeker's name as supplied by the campaign at call initiation. 
   Falls back to "Unknown" if not provided.

2. call_answered — Was the call picked up? 
   Values: "Yes" if the seeker spoke at all, "No" if the call went unanswered or 
   dropped before any user turn.

3. audio_check_confirmed — Did the seeker confirm they could hear the agent at the 
   opening audio check? 
   Values: "Yes" if they answered the audio check affirmatively or otherwise showed 
   they could hear, "No" if they could not hear and the call was closed for a bad 
   line, "NA" if the audio check was never reached.

4. right_person — Was this the person who had actually applied? 
   Values: "Yes" if they acknowledged the application or did not dispute it, 
   "No" if they said they had not applied / it was the wrong number, 
   "Proxy" if someone else answered on their behalf, 
   "NA" if the call did not get that far.

5. remembered_application — Did the seeker recall the earlier application when it 
   was mentioned? 
   Values: "Yes", "No" if they said they did not remember, "NA" if not reached.

6. trrain_pitched — Was the service offer actually spoken to the seeker on this call? 
   Values: "Yes" if the offer was made, "No" if the call ended before it (wrong 
   person, do-not-call, busy, angry, bad line, or silence).

7. trrain_interest: the caller's FINAL answer to the offer.
   "Yes" ONLY when ALL of these hold in the transcript:
     (1) the offer was spoken;
     (2) the caller agreed to the offer question;
     (3) the caller then NAMED a callback time in their own words (morning / afternoon /
         evening / anytime / a day or hour) when asked;
     (4) they did not later decline, say "not now", or reveal they wanted a job and then
         fail to re-confirm after being told it is not a job.
   "Maybe" when the caller agreed but did not name a time (filler such as "ठीक है"/"ओके"/
     "हम्म"/"जी" or "ಸರಿ"/"ಓಕೆ"/"ಹ್ಮ್"/"ಹಾಂ", silence, noise, hang-up), or never gave a real
     answer.
   "No" for a refusal at any point, in the CALLER's words ("नहीं", "नहीं चाहिए", "रहने दो", "ಬೇಡ").
   Silence, "*No audio*", a dropped line or no reply at all is NEVER "No"; it is "Maybe". The LAST answer wins.
   "NA" if trrain_pitched is "No".
   NOT answers, never evidence of interest: replies to the audio check or to "आप सुन रहे हैं?" /
   "ನೀವು ಕೇಳಿಸ್ಕೊಳ್ತಾ ಇದ್ದೀರಾ?"; "*No audio...*" and "*Unclear Speech*" markers; single
   syllables; speech addressed to someone else; call-screening or voicemail assistants. Never
   infer Yes from the AGENT's words ("बहुत बढ़िया..." / "ತುಂಬಾ ಒಳ್ಳೆದು...", including the agent
   repeating a time back). Infer it only from the caller's.

7a. callback_slot: the time the CALLER named: "Morning" | "Afternoon" | "Evening" | "Anytime" |
    "Other: <their words in English>" | "NA". Must come from a caller turn. "NA" whenever the
    caller did not say one, even if the agent suggested one. If this is "NA", trrain_interest
    cannot be "Yes".

7b. interest_evidence: the caller's own words, verbatim in the original script, for (i) their
    answer to the offer and (ii) their answer to the time question, separated by " || ".
    "NA" if not pitched.

8. offer_repeated — Did the agent make the offer more than once (a second pitch, a 
   rephrase, or a push after a refusal)? This is a RULE VIOLATION — the prompt allows 
   exactly one offer per call. A single one-sentence clarification given because the 
   seeker asked "what is this service?" does NOT count as a repeat. 
   Values: "Yes" / "No".

9. partner_named: Did the agent name any partner organisation OTHER than TRRAIN Trust
   aloud? That is a RULE VIOLATION. Naming TRRAIN Trust ("ट्रेन ट्रस्ट" / "ಟ್ರೇನ್ ಟ್ರಸ್ಟ್") is
   required, not a violation, and never makes this "Yes".
   Values: "Yes" only if another organisation was named / "No".

10. promised_outcome — Did the agent promise a job, a shortlist, an interview, or any 
    guaranteed outcome? This is a RULE VIOLATION. 
    Values: "Yes" / "No".

11. questions_asked — Questions the seeker asked during the call, as plain strings 
    in English. Array of strings; [] if none.

12. do_not_call — Did the seeker ask not to be contacted again? 
    Values: "Yes" / "No".

12a. callback_requested: Did the seeker ask to be called back at another time because they
     could not talk now (busy, travelling, "call me later")? Values: "Yes" / "No".
     This is NOT interest in the offer: agreeing to the TRRAIN Trust team's call is captured
     only by trrain_interest and callback_slot.

13. drop_reason — If the seeker disengaged before the call completed naturally, what 
    was the behavioural reason? Captures SEEKER behaviour, not technical failures. 
    Examples: "Wrong number", "Said busy", "Hung up mid-call", "Could not hear", 
    "Angry about being called". "NA" if the call completed normally.

14. final_summary — A 2-3 sentence factual summary of the call in English. 
    Cover: (1) whether the right person was reached, (2) whether the offer was made, 
    (3) how they responded. No opinions, no speculation.

15. EXAMPLE OUTPUT — Below is an example of how all the above fields should be 
    aggregated and returned for a single call. Use this exact structure:

{
  "seeker_name": "Sunita Devi",
  "call_answered": "Yes",
  "audio_check_confirmed": "Yes",
  "right_person": "Yes",
  "remembered_application": "Yes",
  "trrain_pitched": "Yes",
  "trrain_interest": "Yes",
  "callback_slot": "Evening",
  "interest_evidence": "हाँ जी, ठीक है। || शाम को।",
  "offer_repeated": "No",
  "partner_named": "No",
  "promised_outcome": "No",
  "questions_asked": [
    "What is this service?",
    "Does it cost anything?"
  ],
  "do_not_call": "No",
  "callback_requested": "No",
  "drop_reason": "NA",
  "final_summary": "The right seeker was reached and confirmed she remembered applying to the Data Entry Operator role. The free support service was offered once and she accepted it. She asked what the service was and was given a one-sentence answer."
}

Rules:
- Use the exact field names listed above. Do not rename.
- Use "NA" for any string field where the answer is absent.
- Use [] for empty arrays, not "NA".
- trrain_interest is "NA" whenever trrain_pitched is "No" — a response cannot exist 
  for an offer that was never made. Never infer interest from anything other than 
  the seeker's answer to that specific offer.
- offer_repeated, partner_named and promised_outcome are compliance checks. Set them 
  from what the AGENT actually said in the transcript, not from what it should have 
  said. A "Yes" on any of them means the call broke a rule and must be reviewed.
- do_not_call is "Yes" only on an explicit request not to be contacted again — not 
  merely a refusal of the service offer.
- drop_reason captures seeker behaviour only, not technical failures.
- Do not hallucinate job titles, company names, or contact details — only extract 
  what is actually present in the transcript or the input variables.
- For final_summary, always write in English regardless of the conversation language.
