Analyse the call transcript and extract the following information. 
If a value is not present, use "NA" for strings, [] for arrays, or 0 for counts.

1. seeker_name — The seeker's name as registered in the contact upload list. 
   Pulled from the input CSV at call initiation. Falls back to "Unknown" if not provided.

2. call_answered — Was the call picked up? 
   Values: "Yes" if the seeker spoke at all, "No" if the call went unanswered or 
   dropped before any user turn.

3. call_engaged — Did the seeker meaningfully engage in the conversation, beyond a 
   one-word reply? 
   Values: "Yes" if the user had three or more substantive turns, "No" otherwise.

4. primary_topic — What was the main subject of the call? 
   Values: "Job search" if the conversation centred on finding work, 
   "Profile update" if the seeker mainly shared/updated profile info, 
   "No engagement" if the call did not progress past greeting.

5. user_intent — What was the user's underlying intent? 
   Values: "Job Application" if they applied, "Job Search" if they explored jobs, 
   "Profile Update" if they only shared profile info, "General" for unclear engaged 
   callers, "NA" for no engagement.

6. jobs_shown — Did the bot present any jobs to the seeker during the call? 
   Values: "Yes" / "No".

7. jobs_recommended — All jobs the bot surfaced to the seeker during the call, 
   in the order they were shown. Array of objects.
   Each object: { job_id, role, company_name, company_location, salary_offered, 
                  qualification_required }

8. applied_to_job — Was at least one job application successfully submitted on 
   this call? 
   Values: "Yes" if any apply_job tool call succeeded, "No" otherwise.

9. applications_count — How many jobs were successfully applied to in this call? 
   Integer; 0 if none.

10. jobs_applied — Jobs the seeker successfully applied to (apply_job tool call 
    succeeded). Array of objects.
    Each object: { job_id, role, company_name, company_location, salary_offered, 
                   qualification_required }

11. jobs_failed_to_apply — Jobs the seeker tried to apply to but the apply_job 
    tool call failed (e.g. HTTP 404, profile not found, system error). 
    Array of objects.
    Each object: { job_id, role, company_name, company_location, salary_offered, 
                   qualification_required, failure_reason }

12. drop_reason — If the seeker dropped off or disengaged from the call before 
    natural completion, what was the behavioral reason? 
    This captures SEEKER behavior, not technical failures. 
    Examples: "Said not looking", "Asked to call later", "Language barrier", 
    "Hung up mid-call", "Already employed", "Frustrated with repeated apply failures". 
    NA if the call completed normally.

13. final_summary — A 2-3 sentence factual summary of the call in English. 
    Cover: (1) whether the seeker was interested in jobs, (2) what role/location/
    salary they discussed, (3) whether they applied or tried to apply. 
    No opinions, no speculation.

14. ready_for_interview — Did the seeker indicate they could attend an interview 
    if an employer shortlists them (a single question asked once before applying)? 
    Values: "Yes" if they said they can attend (including a phone interview), 
    "No" if they said they cannot, "Conditional" if it depends (only by phone, 
    only if nearby, only at certain times), "NA" if the question was not asked 
    (e.g. no application was attempted) or the seeker gave no clear answer.

15. consent_status — On the new-caller path (new_seeker="yes"), did the caller give the consent needed to create their profile and apply?
   Values: "Given" if the caller agreed at the consent gate and create_profile was called; "Declined" if the caller refused consent (no create_profile, no apply_job — call ended at the consent gate); "NA" for a returning caller (already consented) or if the consent gate was never reached. Default "NA".

15a. preferred_location — Did the caller state a place they want to work, when the jobs
    on offer did not suit them (the mismatch preference capture), or when they corrected
    the location the call opened with? Extract the place in the caller's own terms, in
    English/Latin script — a city, a locality, or a station/landmark if that is all they
    gave (e.g. "Vasundhara, Ghaziabad", "Noida", "near Sahibabad station").
    This is where they want to WORK. It is NOT their residence and must never be copied
    from the profile's stored location, from a job's location, or from the call's input
    location. "NA" if the caller never stated a preferred work location.
    **The test is whether the words came out of the CALLER's mouth.** If the bot named a place
    and the caller merely agreed ("हाँ", "सही"), that counts — they confirmed it aloud. If the
    place appears only in the call's input variables, only in their stored profile, or only in a
    job's details, it is "NA" no matter how obviously it looks like their location. A value that
    equals the call's input `location` and was never spoken by the caller is the single most
    common way this field goes wrong: check the caller's turns before filling it.
    A station or landmark the caller offered instead of an area is a valid value — record it as
    they said it.

15c. input_location_had_jobs — Did the call's input `location` actually have any job in
    the list the bot was given? Compare the call's input location against the `location`
    field of the jobs offered.
    Values: "Yes" if at least one job sat in that place or its city; "No" if the input
    location was a real place and NOT ONE job was there (e.g. the call opened on "Delhi"
    and every job was in Ghaziabad); "NA" if the input location was empty or a sentinel
    ("Any", "NA", "-", a pincode, campaign metadata).
    **Compare the INPUT location string to the job list. Do NOT follow what the bot talked
    about.** On call d3521a89 the input was "Delhi", every job was in Ghaziabad, and the bot
    confirmed "गाज़ियाबाद" to the caller — the correct value is "No", because the question is
    whether the place the caller was DIALLED for had any job, not which place got discussed.
    Reading it off the conversation hides exactly the targeting problem this field exists to
    surface. It went wrong the other way on call 2bf465d9: the input was "Hubli", SIX of the
    eight jobs were in Hubli, the bot happened to talk about Dharwad, and this field was
    recorded as "No". Match the input string against every job's `location` field — a job
    listed as "Keshwapur, Hubli" IS in Hubli — and ignore which city got discussed.
    This is a CAMPAIGN-TARGETING signal, not a bot verdict: "No" means the caller was
    dialled for a city we hold no inventory in, which is worth surfacing even when the
    call otherwise went perfectly. Judge it from the input location and the job list only
    — never from what the caller said they wanted.

15d. nearest_landmark — Did the caller name a nearest bus stop, railway/metro station, or
    well-known landmark near where they live? This is the Location step's Turn B answer.
    Extract it in the caller's own terms, transliterated to English/Latin script
    (e.g. "Nashik Road station", "near Sabzi Mandi", "Sahibabad station").
    "NA" if they were never asked (because it was already known from a previous call) or
    gave no usable answer. Never fill it from the input location, a job's location, or the
    stored profile — only from what the caller said on THIS call.
    **If the BOT supplied the landmark rather than the caller, this is "NA".** That has happened:
    on call d3521a89 the bot asked for the nearest station, the caller answered "जी बताइए"
    (a non-answer), and the bot said "साहिबाबाद स्टेशन है।" itself. Nothing was learned on that
    call, so the correct value is "NA" — recording it as though the caller gave it launders a
    bot fabrication into a stored caller fact.

15b. preference_mismatch_reason — Why the caller rejected the jobs, when they did.
    Values: "Location" if they turned them down because of distance/area/city;
    "Role" if they turned them down because it was not the kind of work they want;
    "NA" if they did not reject the jobs, or applied, or gave no reason.
    Exactly one value — if they objected on both, use the one the bot actually acted on.

16. service_provider_pitched — Was the Need Capture service-provider offer actually 
    spoken to the caller on this call? 
    Values: "Yes" if the offer was made (either path), "No" if the call ended before 
    that step was reached or the call did not qualify for it.

17. service_provider_interest — How did the caller respond to that offer? 
    Values: "Yes" for a clear acceptance, "No" for a clear refusal, "Maybe" if the 
    answer was unclear or they gave no real answer, "NA" if the offer was never made 
    (service_provider_pitched = "No").

18. EXAMPLE OUTPUT — Below is an example of how all the above fields should be 
    aggregated and returned for a single call. Use this exact structure:

{
  "seeker_name": "Rajesh Kumar",
  "call_answered": "Yes",
  "call_engaged": "Yes",
  "primary_topic": "Job search",
  "user_intent": "Job Application",
  "jobs_shown": "Yes",
  "jobs_recommended": [
    {
      "job_id": "f493b9d2-1625-48af-a20d-95e95f56fd2f",
      "role": "Electrician",
      "company_name": "Sigmatek Industrial Electronics",
      "company_location": "Modinagar, Ghaziabad",
      "salary_offered": "₹20,000–40,000",
      "qualification_required": "ITI Electrical"
    },
    {
      "job_id": "0eb6e86c-6a9e-4b37-8a1e-2d15f5573b5c",
      "role": "Machine Operator (PCB Electroplating Line)",
      "company_name": "Vishwakarma Auto Pipes",
      "company_location": "Sahibabad, Ghaziabad",
      "salary_offered": "₹15,000–18,000",
      "qualification_required": "10th pass"
    },
    {
      "job_id": "9098465107",
      "role": "Solar Energy Consultant",
      "company_name": "NA",
      "company_location": "Ghaziabad",
      "salary_offered": "₹18,000–25,000",
      "qualification_required": "Graduate"
    }
  ],
  "applied_to_job": "Yes",
  "applications_count": 2,
  "jobs_applied": [
    {
      "job_id": "f493b9d2-1625-48af-a20d-95e95f56fd2f",
      "role": "Electrician",
      "company_name": "Sigmatek Industrial Electronics",
      "company_location": "Modinagar, Ghaziabad",
      "salary_offered": "₹20,000–40,000",
      "qualification_required": "ITI Electrical"
    },
    {
      "job_id": "0eb6e86c-6a9e-4b37-8a1e-2d15f5573b5c",
      "role": "Machine Operator (PCB Electroplating Line)",
      "company_name": "Vishwakarma Auto Pipes",
      "company_location": "Sahibabad, Ghaziabad",
      "salary_offered": "₹15,000–18,000",
      "qualification_required": "10th pass"
    }
  ],
  "jobs_failed_to_apply": [
    {
      "job_id": "9098465107",
      "role": "Solar Energy Consultant",
      "company_name": "NA",
      "company_location": "Ghaziabad",
      "salary_offered": "₹18,000–25,000",
      "qualification_required": "Graduate",
      "failure_reason": "HTTP 404 — profile not found"
    }
  ],
  "ready_for_interview": "Yes",
  "consent_status": "NA",
  "preferred_location": "Vasundhara, Ghaziabad",
  "preference_mismatch_reason": "Location",
  "input_location_had_jobs": "No",
  "nearest_landmark": "Sahibabad station",
  "service_provider_pitched": "Yes",
  "service_provider_interest": "Yes",
  "drop_reason": "NA",
  "final_summary": "Seeker was actively looking for work and engaged in a detailed conversation about three roles. Successfully applied to Electrician and Machine Operator positions but the third application (Solar Energy Consultant) failed due to a profile not found error."
}

Rules:
- Use the exact field names listed above. Do not rename.
- Use "NA" for any string field where the answer is absent.
- Use [] for empty arrays, not "NA".
- Use 0 for empty counts, not "NA".
- For all job arrays (jobs_recommended, jobs_applied, jobs_failed_to_apply), each 
  entry must be a complete object — do not flatten into strings.
- jobs_applied and jobs_failed_to_apply are mutually exclusive at the job level — 
  a single job either succeeded or failed to apply, never both.
- drop_reason captures seeker behavior only, not technical apply failures. If apply 
  failed but the seeker stayed engaged, drop_reason = "NA".
- ready_for_interview is "NA" when the interview-readiness question was never asked 
  or the seeker did not give a clear Yes/No/Conditional answer.
- preferred_location and preference_mismatch_reason describe the caller's STATED
  preference only. Never infer them: if the caller did not say where they want to work,
  preferred_location is "NA" even when the call's input location or their profile carries
  a place. preference_mismatch_reason is "NA" whenever the caller applied to a job or never
  rejected the options. A preferred work location is never written to the caller's profile.
- service_provider_interest is "NA" whenever service_provider_pitched is "No" — a 
  response cannot exist for an offer that was never made. Never infer interest from 
  anything other than the caller's answer to that specific offer.
- Do not hallucinate company names, salaries, or contact details — only extract what 
  is actually present in the transcript or input recommendations.
- For final_summary, always write in English regardless of the conversation language.
}