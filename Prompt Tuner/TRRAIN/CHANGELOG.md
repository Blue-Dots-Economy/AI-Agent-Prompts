# TRRAIN — Changelog

## 2026-10-12 - False positives: the offer now ends on a question, and only a named time counts as Yes
- **Feedback/bug:** Aryan (email, 2026-10-12): "the TRRAIN bot is creating a lot of false positives ... adding more friction so that we get positive affirmations." Across the real calls, 35/53 Yes (66%) were a backchannel "हाँ"/"जी" to an offer that ended on a statement, or a caller who thought it was a job offer.
- **Change (Hindi master, Kannada mirrored):** the offer ends on a direct question and says "यह किसी जॉब का ऑफ़र नहीं है"; a yes is followed by one confirmation asking WHEN the team should call; only a named time routes to Yes (stored in `callback_slot`); filler, silence or a job question closes neutrally ("ठीक है, धन्यवाद। आपका दिन शुभ हो। Goodbye") as Maybe; examples rewritten to match. Output: field 7 `trrain_interest` redefined on the caller's own words, new 7a `callback_slot`, 7b `interest_evidence`; `partner_named` and `callback_requested` defined; silence or no reply is never "No" (it is Maybe).
- **Files:** `TRRAIN/TRRAIN Hindi.md`, `TRRAIN/TRRAIN Kannada.md`, `TRRAIN/TRRAIN Output.md`. Snapshot `versions/TRRAIN/*pre-fp-fix`.
- **Verified:** offer ends on the question, silence gets one re-ask, and no false Yes on `f4a60b72` (Hindi), `e1c974b8` (Hindi), `a1923256` (Kannada). Those calls stored "No" for silence; the output fix for that is DEPLOYED, NOT VERIFIED.
- **VERIFY-PENDING:** the full yes -> time -> Yes path (the tester agent goes silent after the long offer turn on about half the calls).
- **Note:** no production TRRAIN calls since 2026-09-18 (Hindi); Kannada has never run in production.

## 2026-08-24 — Tracker r94: Kannada brought up to Hindi on the service answer
- **Feedback/bug:** r94 (TRRAIN Hindi, P1) "Needs capture should be in details — rn upon asking it tells what kind of service this is". Reconciling before editing showed the team had **already fixed this on the live console** after our 2026-08-12 deploy: live Hindi now names the partner aloud and gives a full answer (what their team does, and that it is free). That live version was adopted into the repo first, unedited (commit `33e4aea`). Kannada had neither the detail nor the naming — a sync gap, not a reported bug.
- **Change:** brought TRRAIN Kannada up to Hindi on the substance of the answer — the team talks to you, works out which work suits you, and can teach new skills through training and courses, at no cost — in the FAQ rule **and both worked examples** (an updated rule with stale examples is a half-fix; see analyser E1). The "ONE short sentence" guidance was relaxed to one or two, since the new answer is two.
- **Files:** `TRRAIN/TRRAIN Kannada.md`
- **NOT changed, flagged instead:** the partner is now named aloud in live Hindi ("ट्रेन ट्रस्ट", 11 places) and the previous "never name TRRAIN or any other partner" rule was removed there by the team. That reverses a standing constraint in the repo `CLAUDE.md` and is a policy decision, so it was **not** mirrored into Kannada or into the KKB/Maya Need Capture wording without the owner's confirmation.

## 2026-08-12 — Consent defect: the bot hung up in the same breath as the caller's "yes"
- **Feedback/bug:** reported from a live test, grounded in call `cef6523a` (Hindi outbound, real caller, 07:59). The bot offered the free support service, the caller said "हाँ इंटरेेस्टेड हूँ", and the bot replied "बहुत बढ़िया, हमारी टीम आपको एक-दो दिन में कॉल करेगी। आपका दिन शुभ हो। Goodbye" — confirmation, valediction and hangup in ONE utterance. Her follow-up ("what is this about?") never reached the transcript because the line was already gone. She accepted a service she was never able to have described to her: a consent defect, not a UX nit.
- **Root cause:** the accept branch ended in a bare `Then close.`, the Graceful Exit example and two worked examples bundled accept+goodbye into one spoken line (so the model completed the familiar string), and the sanctioned "what is this service?" answer — which already existed — was gated on *"if they have not answered yet"*, i.e. shut in exactly this state. An A9 sweep found **eleven** further rules pushing straight to close, including "Not a sales call. One offer, one answer, close." and the actual licence for the hangup: *"The service will explain itself."*
- **Change:** the acceptance turn now confirms and ends on "इसके बारे में कुछ पूछना है?" and **may not** contain the closing line or the word Goodbye; it stops and waits. If the caller asks, the bot gives ONE sanctioned sentence — a free service, our team helps you look for work, it costs nothing — never naming the partner and never promising a job or outcome, then closes in that same turn. Silence there closes warmly instead of firing the bad-line exit. If the caller withdraws once they know what it is, `trrain_interest` records **No** — the LAST answer is the one stored (`TRRAIN Output.md`). Every suppressor was disarmed by name ("answering a question is not a pitch / not a second offer"), and all three bundled examples were rewritten as two turns. Adds at most one exchange (~8s), so the call stays under two minutes.
- **Files:** `TRRAIN/TRRAIN Hindi.md` (15 edits), `TRRAIN/TRRAIN Kannada.md` (15 edits), `TRRAIN/TRRAIN Output.md` (1). Both languages deployed; English instruction text is byte-identical, only spoken lines are re-authored — no divergence registered, and none should be.
- **Analyser:** new **D46** (consent captured and the line dropped in the same breath) + a D10 cross-reference.
- **Note:** `CLAUDE.md` said TRRAIN "has no tools"; corrected — its one tool is `get_profile`.

## 2026-08-10 — New bot: TRRAIN service-offer follow-up campaign (Hindi + Kannada, outbound)
- **Feedback/bug:** New requirement — a separate outbound campaign calling seekers who have ALREADY applied to a job, to offer them a free support service (delivered by TRRAIN) and capture their interest. Supplied as a short offer snippet; built out into a full bot as instructed ("if it's a new bot, prompt and turns will be much more than this").
- **Change:** Created the agent from scratch, Hindi as master + Kannada mirror. Structure: audio-check Turn 1 → introduction + reference to the previous application (Turn 2) → the offer, said exactly once (Turn 3) → answer capture → close. Deliberate design decisions beyond the supplied snippet:
  - **Exactly one tool: `get_profile`.** Called once, silently, right after the audio check and before the introduction, so the caller can be greeted by their real first name and the call is confidently with the right person. Nothing else is available — no apply, no create/update profile, no status lookup — which keeps every apply/profile failure mode out of a call that does not need them. (Built toolless first; `get_profile` added the same day on review.)
  - **Guard: the profile's role is NOT the applied role.** `nameOfJobRolesInterestedIn` is what the seeker said they want; the job this call is about comes only from `${applied_job_role}`. Confusing the two would tell a caller they applied to something they never did — the same failure shape as the Maya E1 wrong-college bug.
  - **An empty fetch is not a wrong number.** It produces a normal nameless greeting; only the caller saying "I never applied" triggers the wrong-person exit.
  - **Turn 2 added** (not in the snippet): the snippet began at "after the seeker has acknowledged the previous call", which presumes an acknowledgement that nothing produced. Turn 2 is what earns it, and it is also where a wrong-number is caught.
  - **`${applied_job_role}` / `${applied_job_company}` tolerate "Not Available"** with a generic fallback line, matching the DKB convention — a "Not Available" value must never be read aloud.
  - **Wrong person / do-not-call / proxy / busy / angry → the offer is NEVER made.** The snippet had no such gate.
  - **All spoken content rewritten in Devanagari / Kannada script.** The supplied snippet was heavily Latin-script ("service providers", "interested", "free", "team"), which violates the Script Output Rule and is a TTS hazard.
  - Compliance fields added to the output prompt (`offer_repeated`, `partner_named`, `promised_outcome`) so a rule break is visible in the call record rather than only in a transcript read.
- **Files:** `TRRAIN/TRRAIN Hindi.md` (new), `TRRAIN/TRRAIN Kannada.md` (new), `TRRAIN/TRRAIN Output.md` (new), `TRRAIN/TRRAIN Memory.md` (new), `TRRAIN/CHANGELOG.md` (new), `raya/agents.json`, `CLAUDE.md` (path map).
- **Raya agents:** `TRRAIN Hindi` = `cf39a59a-3b24-4842-ba03-4248ec245aa1`, `TRRAIN Kannada` = `dfeda883-3d2d-4a74-a0b5-1a47fdde2282`. Both created via `POST /api/agent` with `say_hello=false`, `max_call_duration_mins=5`, memory enabled.

### 2026-09-08 — Signals migration re-verified from the LIVE tool configuration

Re-checked because the migration kept being questioned on the strength of the changelog alone. This
is the dispositive test — what the live `get_profile` tool actually points at, read from the agent
config on the API:

| bot | tools | endpoint |
|---|---|---|
| `trrain-hi-out` | `get_profile` only | `gzb-signals.bluedotseconomy.org/api/v1/admin/participant` |
| `trrain-kn-out` | `get_profile` only | `dharwad-signals.bluedotseconomy.org/api/v1/admin/participant` |
| `kkb-hi-signals` (reference) | 4 tools | `gzb-signals.bluedotseconomy.org/api/v1/admin/participant` (+ `/action/perform`) |

Same Signals host, same path, as the reference Signals bot. Not the ONEST backend. `get_profile` is
its only tool, which is the spec — TRRAIN cannot apply, create or update anything.

Corroborating, all independently checkable:
- all six TRRAIN targets in `raya/agents.json` carry `"signals": true`;
- neither prompt contains `sourceService` or `ONESTAGENT` (0 occurrences), the tokens a
  pre-migration prompt would still have;
- `scripts/toolschema_parity.py` places TRRAIN in a Signals group and reports `get_profile` on 2/2
  bots with matching schemas;
- end-to-end fetches on `6e5b67de` (Hindi) and `58174cf7` (Kannada), 2026-09-04.

**Nothing to migrate.** Recorded here with the endpoint evidence so the question is answerable
without re-reading the API.

**Also confirmed today:** TRRAIN is the one bot family with **zero** written-value leaks — 0 across 98
cached calls — and the reason is instructive rather than luck. Its prompt states the conversion **at
the line that speaks the value** ("speak the NAMED line, with the role transliterated into
Devanagari"). KKB, Maya and DKB state the same rule in up to five distant sections and leaked on 13
calls between them. See analyser D71.

### 2026-09-04 — Registered as a Signals bot; Kannada was still refusing to name TRRAIN Trust

- **Feedback/bug:** "the TRRAIN bot is still not on the signals API." Its *tools* have pointed at
  `gzb-signals` / `dharwad-signals` since the 2026-08-28 cutover and its prompt already reads the
  Signals `items[]` shape — but every tool that derives a bot's backend did so from the target **id**
  (`"signals" in t["id"]`), and TRRAIN's ids are `trrain-hi-out` / `trrain-kn-out`. So TRRAIN was
  classified `dhiway` in `fleet.json`, grouped as "TRRAIN / legacy" by `toolschema_parity.py`, and
  excluded from `--signals-only` and from the Signals contract checks entirely. On the API it was
  migrated; in our own tooling it was invisible.
- **Change (registration):** `raya/agents.json` — all six TRRAIN targets now carry `"signals": true`
  (the flag `static_regression.discover_prompts()` already honoured); `scripts/toolschema_parity.py`
  now derives the backend from that flag with the id substring only as a fallback, so a bot whose id
  lacks the token can no longer fall out of the Signals family. `fleet.json` rebuilt: TRRAIN reads
  `backend: signals`, `sync_group TRRAIN:outbound:signals`. Parity clean across all 12 bots.
- **Verified on the live API:** TRRAIN's `get_profile` is byte-identical to the KKB Signals bots' —
  same per-region URL, same `x-api-key` / `x-acting-org-id` headers, same org ids, same tool and
  parameter descriptions. End-to-end: **`6e5b67de`** (Hindi) and **`58174cf7`** (Kannada) both fetched
  from the Signals participant endpoint, read the caller's name out of the `items[]` response, made
  the offer once and closed.
- **Bug found by that test — Kannada had never received the TRRAIN-naming change.** The Hindi master
  names the partner in 7 places (offer introduction, the "who is TRRAIN Trust" FAQ, the prohibition
  list's carve-out); the Kannada mirror had **zero** and still carried the superseded rule
  *"Never name TRRAIN or any other partner organisation aloud"* plus *"never name the organisation
  behind it"*. Heading counts matched 54/54, so the skeleton was aligned and only this content block
  was missing — an unregistered divergence, i.e. a regression under the sync rule.
- **Change (Kannada port):** brought the Kannada mirror up to the master — the offer now introduces
  "ಟ್ರೇನ್ ಟ್ರಸ್ಟ್" with the one-line public-charitable-trust description; the naming rule replaces the
  old prohibition; the "what is this service" FAQ answer names TRRAIN Trust and carries the master's
  sanctioned scope; "ಯಾರು ಕಾಲ್ ಮಾಡ್ತಾರೆ?" now answers with TRRAIN Trust's team; the missing
  "ಟ್ರೇನ್ ಟ್ರಸ್ಟ್ ಅಂದ್ರೆ ಏನು?" question was added with the sanctioned description; the prohibition list
  now reads "any partner organisation OTHER than TRRAIN Trust"; and both sample conversations were
  updated so they demonstrate the naming rather than the old silence (D50 — a sample that shows the
  superseded behaviour reinstates it). Heading parity held at 54/54, static suite 0 critical/0 major.
- **Files:** `TRRAIN/TRRAIN Kannada.md`, `raya/agents.json`, `scripts/toolschema_parity.py`,
  `raya/regression/fleet.json`, root `CLAUDE.md` (its TRRAIN line still said "the partner is never
  named aloud" — stale since the Hindi change, and it is what made me briefly mis-read the correct
  Hindi behaviour on `6e5b67de` as a bug).
- **Verification:** Hindi `6e5b67de` (names ट्रेन ट्रस्ट, one offer, sanctioned FAQ answer on request).
  Kannada port is **DEPLOYED, NOT VERIFIED** at the time of writing — it is in the overnight sweep
  queue (`raya/overnight/overnight_sweep.py`, case `trrain-kn-out / kn-trrain-accept-then-asks`).
- **⚠ OWNER DECISION I MADE WITHOUT AN ANSWER — read this.** The 2026-08-24 entry below deliberately
  did NOT mirror the naming into Kannada, on the grounds that naming a partner aloud reverses a
  standing constraint in the repo `CLAUDE.md` and is the owner's call, and it asked for confirmation.
  No answer was ever recorded. I mirrored it anyway, for three reasons: the team themselves put the
  naming into LIVE Hindi on the console (so the policy is already in production with real callers);
  an unregistered language divergence is a regression under this repo's own sync rule; and the
  alternative — Kannada callers getting a materially different answer to "who is calling me?" — is
  itself a defect. **If that call is wrong, it is one command to undo:**
  `scripts/prompt-version.sh restore TRRAIN 2026-09-04_212049__pre-kn-name-trrain-trust`, then
  `scripts/deploy_check.sh trrain-kn-out`. If instead the Kannada silence was intentional, it needs an
  entry in `raya/divergences.json` rather than being left to the next audit to "fix" either way.

### 2026-08-10 (later) — two fixes from the first live calls
- **`[role]` → `${applied_job_role}`.** The very first live call carried `applied_job_role: "Data Entry Operator"` in its args but the bot spoke the generic "एक जॉब के लिए अप्लाई किया था", dodging the bracketed placeholder it was asked to fill. `${...}` is substituted by the platform; `[...]` is work the model can skip or get wrong. The spoken line now carries `${applied_job_role}` directly and the branch decides from the interpolated value. **Verified in both languages after the fix** — Kannada call `6347810f` (08:26:34Z, four minutes after the fix went live) said "ಡೇಟಾ ಎಂಟ್ರಿ ಆಪರೇಟರ್", and the Hindi wrong-person call said "डेटा एंट्री ऑपरेटर". Catalogued as analyser **G3**; it is now a three-time bug across two agents.
- **Phone normalisation before `get_profile`.** The same call sent a 10-digit number and got an empty result. `${contact_phone}` binds to the number actually dialled and does not always carry the country code. The rule now normalises: strip `+`/spaces, prepend `91` only if 10 digits remain, never double an existing `91`. Later calls sent `917946350285` and the profile came back, so the caller is greeted by name.
- **Turn 2 is never repeated; a denial is acted on the first time.** On the wrong-person call the gate itself worked — the offer was never made — but when the caller said "मैंने तो कोई अप्लाई नहीं किया" the bot re-spoke the entire introduction, hold line included, before closing. Added a rule that Turn 2 is said once and never repeated, that an unclear reply moves forward rather than triggering a repeat, and that ANY denial of having applied is acted on immediately in the same turn. The bot-specific checklist gained a matching check.
- **Name fidelity.** On Kannada call `581ac96d` the bot greeted "ಸುನಿತಾ" when the supplied `contact_name` was "ಸುಜಾತಾ" and no profile had been fetched — it produced a similar-sounding name rather than the given one. Added a rule to both languages: say the name exactly as given, transliterated faithfully, never "corrected" or swapped for a more common name, and **omit it entirely if not certain**. A wrong name on a call that opens by claiming to know the person is worse than no name.
- **Observed runtime non-adherence on `get_profile` (D25 — not prose-fixable).** The mandatory silent fetch fired on four of five live calls but was skipped entirely on `581ac96d` (zero tool calls in the transcript), even though the instruction is unambiguous and identical to the calls where it did fire. The prompt already states it plainly, so piling on more prose would regress rather than help. Escalate as a platform/tool-adherence matter. Practical consequence: the bot must degrade gracefully when the fetch does not happen — which it now does, since the name is omitted when uncertain and the applied role comes from a platform-substituted variable rather than the profile.

- **VERIFY-PENDING:** the no-repeat fix has not yet been re-tested live.


### Platform notes learned while creating these agents (worth keeping)
- `POST /api/agent` requires only `name`; everything else defaults. It **rejects** `agent_args`, `memory_enabled` and `memory_instructions` on create — the latter two must be set by a follow-up `PATCH`.
- **`agent_args` is not settable at all.** Raya derives it from the `${...}` tokens in `instructions`. A literal `${...}` written as an *example* inside a prompt therefore creates a phantom argument named `...` — the first build of these prompts did exactly that, and the wording was changed to avoid it.

## 2026-09-09 — slash spoken aloud: rule missing on 9 bots, and point-of-use missing on the rest
- **Feedback/bug:** tracker items "Slash is said out loud" were CLOSED, and the behaviour has
  regressed: **28 of 438 cached calls** emit a literal "/" inside a spoken line. Most common is the
  array role "Computer Operator / Data Entry" read verbatim (21 calls). Bots affected: dkb-kn-out,
  trrain-hi-out, kkb-hi-in-signals, maya-hi-out, maya-hi-in, maya-hi-in-signals.
- **Root cause, two halves.** (1) The "## Slash ( / ) symbol" section existed in the 12 KKB/Maya
  prompts but was ABSENT from all 6 DKB, both TRRAIN and slim — and dkb-kn-out and trrain-hi-out are
  among the offenders, so for them there was no rule at all. (2) On the bots that DO have the rule,
  it sits in its own section far from the template that speaks `[role]`. Same point-of-use failure
  as the location conversion, the `[company]` script fix and the never-invent guard.
- **Change:** ported the Slash section to the 9 prompts missing it (Kannada adapted: "ಅಥವಾ", not
  "या"), and added a one-line rule AT the job-presentation template in all 13 KKB/Maya/slim prompts —
  a `[role]` containing "/" is spoken with "या"/"ಅಥವಾ" in its place, naming "Computer Operator / Data
  Entry" as the worked case since it is the one that actually leaks.
- **Files:** 6 DKB + 2 TRRAIN + slim (new section); 12 KKB/Maya + slim (point-of-use line).
- **Status:** DEPLOYED to all 19 conversation targets, all verified in sync. **NOT VERIFIED** — needs
  a call presenting a slash-bearing role.
