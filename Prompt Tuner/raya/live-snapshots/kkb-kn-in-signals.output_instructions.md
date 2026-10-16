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

15. consent_status — the outcome of the Part 1 ACCOUNT-AND-TERMS ask (the Blue Dots account, the
    three purposes, the one-year term, Ekstep Foundation). This is asked of ANY caller whose consent
    flags came back false or absent — returning callers included — and of every first-time caller.
   Values:
     "Given"      — it was asked and the caller agreed (record_consent, or create_profile, then ran).
     "Declined"   — it was asked and the caller refused; the call ended there, no account, no apply.
     "Not Needed" — it was NOT asked because the fetched flags were already all true. This is the
                    common, healthy case for a consented returning caller; it is NOT a miss.
     "Failed"     — the caller agreed but the consent write errored, so nothing was recorded.
     "NA"         — the point was never reached (e.g. the call dropped in the greeting).
   Default "NA". **Do not report "NA" for a caller who was asked** — that loses the one number the
   team needs, which is how many people decline. If a terms/account line was spoken at all, the value
   is Given, Declined or Failed.

15f. profile_save_consent — the outcome of the Part 2 SAVE-MY-DETAILS ask (name, age, education,
    experience), which is put only to a caller with no live profile.
   Values: "Given" if they agreed and create_profile ran; "Declined" if they refused (the call
   continued as browse-only, with no application); "Given At Apply" if they first declined and then
   agreed when the save was re-offered at the moment they asked to apply; "NA" if the question did
   not arise (a returning caller with a live profile — the usual case). Default "NA".

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

unbacked_apply_claim — **A RECONCILIATION FLAG.** "Yes" when the agent TOLD the caller their
application had gone through but NO successful apply_job result appears in the transcript for that
job; otherwise "No". A hold phrase, a stage direction, or the agent describing the tool call does
NOT count as a result. When "Yes", the caller hung up believing they applied and they have not —
that is a person to call back, and this flag makes them findable instead of silent. Roughly 1 in 11
real calls that claimed an apply. Set it independently of jobs_applied and jobs_failed_to_apply;
an empty jobs_applied WITH this set to "Yes" is exactly the case to surface. Include it in the JSON
output as "unbacked_apply_claim".