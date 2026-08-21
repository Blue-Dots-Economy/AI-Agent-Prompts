Analyse the call transcript and extract the following information.
If a value is not present, use "NA" for strings, [] for arrays, or 0 for counts.

1. seeker_name — The student's name as registered in the contact upload list.
   Pulled from the input CSV at call initiation. Falls back to "Unknown" if not provided.

2. call_answered — Was the call picked up?
   Values: "Yes" if the student spoke at all, "No" if the call went unanswered or
   dropped before any user turn.

3. call_engaged — Did the student meaningfully engage in the conversation, beyond a
   one-word reply?
   Values: "Yes" if the user had three or more substantive turns, "No" otherwise.

4. primary_topic — What was the main subject of the call?
   Values: "Job search" if the conversation centred on finding work,
   "Profile update" if the student mainly shared/updated profile info,
   "No engagement" if the call did not progress past greeting.

5. user_intent — What was the user's underlying intent?
   Values: "Job Application" if they applied, "Job Search" if they explored jobs,
   "Profile Update" if they only shared profile info, "General" for unclear engaged
   callers, "NA" for no engagement.

6. college_confirmed — Did the student confirm they are associated with the college
   named in the introduction?
   Values: "Yes" / "No" / "NA" (not asked or call ended before this point).

7. experience_captured — Did the agent capture the student's prior work experience
   (because the profile was new or sparse)?
   Values: "Yes" if experience info was gathered, "No" if not needed or not gathered.

8. jobs_shown — Did the agent present any jobs to the student during the call?
   Values: "Yes" / "No".

9. jobs_recommended — All jobs the agent surfaced to the student during the call,
   in the order they were shown. Array of objects.
   Each object: { job_id, role, company_name, company_location, salary_offered,
                  qualification_required, benefits }
   benefits is "NA" if no perks were mentioned for that job.

10. applied_to_job — Was at least one job application successfully submitted on
    this call?
    Values: "Yes" if any apply_job tool call succeeded, "No" otherwise.

11. applications_count — How many jobs were successfully applied to in this call?
    Integer; 0 if none.

12. jobs_applied — Jobs the student successfully applied to (apply_job tool call
    succeeded). Array of objects.
    Each object: { job_id, role, company_name, company_location, salary_offered,
                   qualification_required }

13. jobs_failed_to_apply — Jobs the student tried to apply to but the apply_job
    tool call failed (e.g. HTTP 404, profile not found, system error).
    Array of objects.
    Each object: { job_id, role, company_name, company_location, salary_offered,
                   qualification_required, failure_reason }

14. hr_contact_shared — Did the agent share an HR contact number with the student
    (only happens after a successful apply, and only if the job had one)?
    Values: "Yes" / "No".

15. benefits_mentioned — Did the agent surface non-monetary benefits/perks for any
    job during the deep-dive?
    Values: "Yes" / "No".

16. drop_reason — If the student dropped off or disengaged from the call before
    natural completion, what was the behavioral reason?
    This captures SEEKER behavior, not technical failures.
    Examples: "Said not looking", "Asked to call later", "Language barrier",
    "Hung up mid-call", "Not a student of this college", "Already employed".
    NA if the call completed normally.

17. final_summary — A 2-3 sentence factual summary of the call in English.
    Cover: (1) whether the student was interested in jobs, (2) what role/location/
    salary they discussed, (3) whether they applied or tried to apply, (4) whether
    HR contact was shared.
    No opinions, no speculation.

18. mpl_registration — Did the student register for the MPL Competition (Ghaziabad
    Marketer Premiere League)?
    "Yes" if the student agreed to participate / accepted the follow-up competition call.
    "No" if the offer was made and the student declined.
    "Not offered" if the MPL Competition was never brought up in this call.

19. mpl_presented — Was the MPL Competition offered/presented to the student at all
    in this call — the combined "any other jobs, or shall I tell you about MPL?" line,
    or any other MPL mention?
    Values: "Yes" if MPL was brought up, "No" if it was never mentioned.

20. not_interested_in_jobs — Did the student explicitly say they are NOT looking for a
    job / not interested in jobs during this call (an unambiguous decline, not mere
    hesitation or "maybe")?
    Values: "Yes" only on a clear, explicit decline of job-seeking; "No" otherwise
    (including when the student engaged, was unsure, or the topic never came up).

21. service_provider_pitched — Was the Need Capture service-provider offer actually
    spoken to the student on this call?
    Values: "Yes" if the offer was made (either path), "No" if the call ended before
    that step was reached or the call did not qualify for it.

22. service_provider_interest — How did the student respond to that offer?
    Values: "Yes" for a clear acceptance, "No" for a clear refusal, "Maybe" if the
    answer was unclear or they gave no real answer, "NA" if the offer was never made
    (service_provider_pitched = "No").

23. EXAMPLE OUTPUT — Below is an example of how all the above fields should be
    aggregated and returned for a single call. Use this exact structure:

{
  "seeker_name": "Anjali Verma",
  "call_answered": "Yes",
  "call_engaged": "Yes",
  "primary_topic": "Job search",
  "user_intent": "Job Application",
  "college_confirmed": "Yes",
  "experience_captured": "Yes",
  "jobs_shown": "Yes",
  "jobs_recommended": [
    {
      "job_id": "f493b9d2-1625-48af-a20d-95e95f56fd2f",
      "role": "Sales Executive",
      "company_name": "BrightRetail Pvt Ltd",
      "company_location": "Lucknow",
      "salary_offered": "₹18,000–25,000",
      "qualification_required": "Graduate",
      "benefits": "PF, health insurance"
    },
    {
      "job_id": "0eb6e86c-6a9e-4b37-8a1e-2d15f5573b5c",
      "role": "Customer Support Associate",
      "company_name": "Helpdesk Solutions",
      "company_location": "Kanpur",
      "salary_offered": "₹15,000–18,000",
      "qualification_required": "12th pass",
      "benefits": "NA"
    }
  ],
  "applied_to_job": "Yes",
  "applications_count": 1,
  "jobs_applied": [
    {
      "job_id": "f493b9d2-1625-48af-a20d-95e95f56fd2f",
      "role": "Sales Executive",
      "company_name": "BrightRetail Pvt Ltd",
      "company_location": "Lucknow",
      "salary_offered": "₹18,000–25,000",
      "qualification_required": "Graduate"
    }
  ],
  "jobs_failed_to_apply": [],
  "hr_contact_shared": "Yes",
  "benefits_mentioned": "Yes",
  "mpl_registration": "Not offered",
  "mpl_presented": "No",
  "not_interested_in_jobs": "No",
  "service_provider_pitched": "Yes",
  "service_provider_interest": "Yes",
  "drop_reason": "NA",
  "final_summary": "Student confirmed she studies at the named college and was actively looking for work. She discussed two roles and successfully applied to a Sales Executive position in Lucknow. The company's HR contact number was shared after the application."
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
  failed but the student stayed engaged, drop_reason = "NA".
- hr_contact_shared can only be "Yes" if an application succeeded AND the job had an
  HR contact — never infer it otherwise.
- Do not hallucinate company names, salaries, benefits, HR numbers, or contact details
  — only extract what is actually present in the transcript or input recommendations.
- service_provider_interest is "NA" whenever service_provider_pitched is "No" — a
  response cannot exist for an offer that was never made. Never infer interest from
  anything other than the student's answer to that specific offer.
- service_provider_pitched and mpl_presented are INDEPENDENT — they are two different
  offers. Never set one from the other.
- For final_summary, always write in English regardless of the conversation language.
