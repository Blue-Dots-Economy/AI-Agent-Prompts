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
- service_provider_interest is "NA" whenever service_provider_pitched is "No" — a 
  response cannot exist for an offer that was never made. Never infer interest from 
  anything other than the caller's answer to that specific offer.
- Do not hallucinate company names, salaries, or contact details — only extract what 
  is actually present in the transcript or input recommendations.
- For final_summary, always write in English regardless of the conversation language.
}