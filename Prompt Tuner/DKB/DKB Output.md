You are extracting structured data from a job verification and capture call with an Indian MSME employer. The call may be in Hindi, Hinglish, or Kannada.
Extract the following fields:
PHASE 1 — JOB FRESHNESS
job_status
Did the employer confirm the job is still open?

Active — employer explicitly confirmed the vacancy is still open
Closed — employer explicitly confirmed the vacancy is no longer available
Unverified — call dropped before confirmation, or employer was unclear
N/A — this is a New Blue Dots contact with no existing job on the platform

PHASE 2 — JOB DETAILS UPDATE
job_role_value
The job role as confirmed or corrected by the employer. Leave blank if not mentioned.
num_vacancies_value
The number of vacancies as confirmed or updated by the employer. Leave blank if not mentioned.
salary_value
The salary range as confirmed or updated by the employer. Leave blank if not mentioned.
location_value
The job location as confirmed or updated by the employer. Leave blank if not mentioned.
qualification_value
The qualification requirement as confirmed or updated by the employer. Leave blank if not mentioned.
fields_updated
Count of how many of the above 5 fields the employer provided or corrected. Enter a number from 0 to 5.
PHASE 3 — NEW JOB CAPTURE
new_job_mentioned
Did the employer mention a new job opening not already on the platform?

Yes — employer mentioned at least one new requirement
No — employer did not mention any new requirement

new_job_role
Role for the new job. Leave blank if not mentioned.
new_job_vacancies
Number of vacancies for the new job. Leave blank if not mentioned.
new_job_salary
Salary for the new job. Leave blank if not mentioned.
new_job_location
Location for the new job. Leave blank if not mentioned.
new_job_qualification
Qualification requirement for the new job. Leave blank if not mentioned.
new_job_posted
Was the new job successfully posted to the platform during the call? Decide from the create_job tool result only.

Yes: A create_job tool call returned a successful result.
No: create_job was never called, or every create_job call returned an error, even if the bot told the employer it was posted.

POSTING CONSENT
posting_consent
Did the employer give consent to post the job to the platform (the "shall I post this?" gate that
precedes create_job)?

Given — employer agreed to post (even if create_job then failed)
Declined — employer was asked and refused, so nothing was posted
NA — the consent gate was never reached (no new job to post, or the call ended earlier)

PHASE 4 — TALENT INSIGHTS
talent_insights_shown
Did the bot share seeker demand data or talent availability insights with the employer?

Yes — insights were shared
No — insights were not shared or call ended before this phase

SUMMARY
final_summary
Write 2–3 sentences in plain English summarising what happened on the call. Include: whether the job is active or closed, any updates made, and any new jobs captured. If the call dropped early, state that no confirmation was obtained.

TOOL RESULTS ARE THE SOURCE OF TRUTH

The transcript contains the assistant's tool calls and each tool's result (messages with role "tool").

- Any field recording whether an action happened (a job posted or updated, a profile created or updated, an application submitted, or consent saved) must be decided from the tool result, never from what the assistant or caller said.
- An action happened only if its tool was called AND the result shows success, such as a returned ID or success status.
- A tool result starting with "[Error" means the action did NOT happen, even if the assistant told the caller it was done.
- If the tool was never called, the action did not happen.
- IDs (job_id, user_id, action IDs) must be copied from a tool result. If no tool result contains one, use "NA".
- Fields recording what the person said or agreed to, such as posting consent, still come from the conversation. A failed tool call does not change whether consent was given.

Rules:

Never infer or assume — only extract what was explicitly stated by the employer
If the employer was unclear or the call dropped before a field could be confirmed, leave that field blank or use Unverified
Do not use the bot's own words to fill output fields — only use what the employer said
job_status must always be filled — never leave it blank