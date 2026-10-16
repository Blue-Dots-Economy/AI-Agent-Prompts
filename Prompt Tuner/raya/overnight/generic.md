# Generic Voice-Agent Test Checklist (Bot-Agnostic)

Behaviors ANY Raya voice agent (KKB / DKB / Maya, Hindi or Kannada, inbound or outbound) must get right regardless of domain. Grade each item from the call transcript (`tool_calls` + spoken turns) and `call_output`. Pattern codes in parentheses point to the analyser's bug-pattern catalog.

---

## 1. Call open / greeting + recording & AI disclosure

- [ ] The very first spoken turn is a clean greeting only — no text prepended, inserted, or appended around it, and no fetch/lookup narration.
  *Why / how to detect:* Turn 1 `content` should be exactly one greeting variant. A clause like "अभी आपकी जानकारी मिल रही है / मैं आपकी जानकारी देख रही हूँ" before or around "नमस्ते" is a fail (cf. B2, D29).

- [ ] The opener contains a real, resolved identity — never a raw template token.
  *Why / how to detect:* Fail if the caller hears a literal placeholder such as `[company_name]` / `${college_name}` / `[college]` in speech (cf. D18 placeholder leak; DKB 64da1027, b362bf46). A graceful generic fallback ("किस कंपनी से बोल रहे हैं?") is a pass.

- [ ] For outbound calls, the bot discloses that it is an automated/AI call and (where applicable) that the call is recorded, before pitching.
  *Why / how to detect:* Look for the AI/recording + free-service framing early in the transcript, before the task pitch (grounded in DKB cf3fc048 "AI/recording disclosure + free-service pitch"). Fail if it launches the task with no disclosure.

- [ ] The greeting matches the call's modality and channel — inbound uses a "welcome"-style opener; outbound identifies the caller.
  *Why / how to detect:* An inbound call opening with an outbound-style "I'm calling you from …" line (or vice-versa) is a fail (cf. D24 outbound-lineage residue in inbound prompts).

## 2. Staying on task when the user goes off-topic (chit-chat / unrelated / abuse)

- [ ] Unrelated questions or small talk get a brief, polite acknowledgement and a redirect back to the task — the bot does not derail into an extended off-topic exchange.
  *Why / how to detect:* After an off-topic user turn, the next bot turn should steer back to the current step. Fail if the bot abandons the flow or answers at length off-domain.

- [ ] In-scope clarifying questions are answered only with known facts; the bot never invents specifics to satisfy them.
  *Why / how to detect:* Grounded in the inquisitive-caller scenario (1fde1677): the bot answered process/timing questions without fabricating dates/numbers and refused to share info it shouldn't. Fail on any invented specific (see also §7).

- [ ] Hostility / anti-AI pushback gets the value framing once, stays polite, and does not argue or loop; the bot exits if the user won't engage.
  *Why / how to detect:* Grounded in the hostile-employer scenario (DKB 1283e4a9). Fail if the bot argues, repeats the same rebuttal multiple times, or keeps pushing after clear refusal.

- [ ] The bot never promises or does anything outside its scope in response to an off-topic ask.
  *Why / how to detect:* Fail if it commits to actions/outcomes it cannot deliver (cf. E4 scope-boundary guard).

## 3. No-response / silence / no-audio

- [ ] On silence / "no audio" / soft-speech / a single monosyllable, the bot issues a bounded number of gentle re-prompts, then ends gracefully — it does not loop forever.
  *Why / how to detect:* Grounded in the silent-caller scenario (d1327a39, ecae68a8, 7c08ad54, f15316b7). Count re-prompt turns against `*No audio*` markers; an unbounded re-prompt loop is a fail.

- [ ] Re-prompts escalate helpfully (e.g. offer concrete example options / a short menu) rather than repeating the identical question.
  *Why / how to detect:* Successive no-response re-prompts should vary and add examples to unstick the caller; verbatim repetition is a fail (see §12).

- [ ] Non-interactive lines (voicemail / IVR / answering machine) are recognized within a couple of turns and the call terminates — the bot does not run its whole flow into the void or fire action tools.
  *Why / how to detect:* Grounded in voicemail scenario (74bd1610, 0460001a). Fail if a create/apply/post tool fires with no human present; expect `call_outcome=Early Disconnect` (cf. C1: no action tool on a dead line).

- [ ] The bot never fabricates an answer on the silent caller's behalf.
  *Why / how to detect:* Fail if the transcript shows the bot proceeding as if the caller answered when they never spoke.

## 4. Repetition / re-prompt behavior when unclear or unanswered

- [ ] On an unclear or missing answer at a decision/data gate, the bot re-asks at most once before branching or degrading — it does not nag.
  *Why / how to detect:* Grounded in D14 (register-a-clear-answer + single re-ask). More than ~2 asks of the same field with no progress is a fail.

- [ ] A clear yes/no (or a clear answer) is registered before the bot advances — it does not blow past a stated answer.
  *Why / how to detect:* Fail if the user says a clear yes/no and the bot takes the wrong branch or re-asks anyway (cf. D14; and the "said no but bot continued" bug, f4e85575).

- [ ] One-time lines (a consent ask, a bridge/hand-off line, a confirmation) are said exactly once, not re-emitted at each tool boundary.
  *Why / how to detect:* Count occurrences of a given fixed line; ≥2 is a fail (cf. B1 — one-time utterance fired repeatedly across a multi-tool sequence).

## 5. Interruption / barge-in handling

- [ ] When the user speaks over the bot, the bot yields to the new input rather than talking past it.
  *Why / how to detect:* In the transcript, a user turn that lands mid-bot-utterance should be answered on the next bot turn; fail if the bot ignores the interruption and continues its scripted line as if nothing was said.

- [ ] After an interruption the bot does not restart its line from the top or re-deliver the whole preceding turn verbatim.
  *Why / how to detect:* Fail if the same full line reappears verbatim after a barge-in (relates to §12; cf. B1 on repeated fixed lines).

## 6. ASR mishearing of critical fields (homophones / numbers)

- [ ] Critical fields (numbers, age, gender, names, selections) are read back for confirmation before being committed.
  *Why / how to detect:* Grounded in the ASR-mishearing scenario (5449910e "female"→"ईमेल"; 1fde1677 age 20→24; 34f1f587 option number). Expect a read-back turn ("आपने … कहा, सही?"); its absence on a critical field is a fail.

- [ ] A mis-heard value is NOT written into a tool call / captured field — the corrected value is used.
  *Why / how to detect:* Compare the final captured value (in `tool_calls[].arguments` / `call_output`) against what the user actually said after correction. A persisted mis-heard value is a fail.

- [ ] The clarify-and-confirm loop on a mis-heard field is capped — it does not spin indefinitely.
  *Why / how to detect:* Count back-and-forths on one field; many turns with no resolution and no fallback is a fail (cf. ASR-mishearing scenario "sometimes wastes many turns").

## 7. No fabrication of facts / results

- [ ] The bot never claims a background action succeeded unless the corresponding tool actually fired and returned success.
  *Why / how to detect:* Cross-check spoken success/confirmation lines against `tool_calls`: a "done / found / applied / posted" line with no matching successful tool call is a fabrication (cf. C5, D20 — hallucinated success; C5(b) fabricated fetch narrated from injected memory).

- [ ] Names / roles / IDs / status the bot states come only from a real tool result, never inferred from injected context/memory.
  *Why / how to detect:* If the bot greets by name or states a role but no fetch tool fired this call, the value was fabricated from `${contact_memory}`/context — fail (cf. C5, D32 — memory used as a substitute for the fetch).

- [ ] The bot never invents dates, durations, phone numbers, distances, quantities, or inventory not present in data or the user's own words.
  *Why / how to detect:* Grounded in inquisitive-caller (1fde1677 — no invented timeline/number) and commute (cceba987 — plausible framing, no over-precise fake distance). Any concrete figure with no source is a fail.

- [ ] The bot never presents an item that falls outside the user's stated filter as if it matched.
  *Why / how to detect:* Grounded in the no-inventory scenario (5449910e, bf587299, 6d63f47c): it must say the exact ask isn't available and offer a nearby/related option with buy-in — not silently pass an out-of-scope item off as a match.

- [ ] A placeholder / sentinel field value ("Any", "N/A", "Not Available", a generic "उपयोगकर्ता"/"अज्ञात" name) is treated as unknown, never spoken aloud or acted on as real.
  *Why / how to detect:* Fail if a fetched sentinel is read to the caller or confirmed as a real value (cf. C9).

## 8. Language / script consistency

- [ ] The bot speaks the call's own language and script throughout — no leaked English rule-text, headings, or instruction prose.
  *Why / how to detect:* Scan spoken turns for English rule fragments or section labels reaching the caller; any is a fail (repo rule: instructions are English, only spoken content is in-language).

- [ ] No raw JSON, tool payloads, field names, IDs, or `{`/`${...}` tokens appear in spoken text.
  *Why / how to detect:* Fail if a spoken turn contains a payload snippet or template token (cf. D20 — model speaks the `apply_job` JSON as text; "Malformed tool args" scenario b31fa5c9 — literal `items[0].item_id`).

- [ ] Payload/tool-arg values are English/Latin; spoken output is the target script (Devanagari / Kannada) — the two do not cross-contaminate.
  *Why / how to detect:* Fail if Devanagari/Kannada lands in a tool argument, or Roman/mixed Hindi is spoken (cf. D3). A caller's name should be spoken in the call's own script (cf. name-script scenario ce59a84c, 7935ce5a).

- [ ] Internal system words ("profile", "payload", "database", "fetch", "id", tool names) are never spoken to the caller.
  *Why / how to detect:* Grep spoken turns for such terms; a caller-facing "profile"/"प्रोफाइल"/"ಪ್ರೊಫೈಲ್" is a fail (cf. D8) — expect the friendly word ("जानकारी"/"ಮಾಹಿತಿ").

- [ ] Numbers, money, dates, times, and phone numbers are spelled as words (not digits/₹/AM-PM/DD-MM), and "/" is voiced as "या"/"ಅಥವಾ", never "slash".
  *Why / how to detect:* Any digit, `₹`, AM/PM, short-date, or literal "slash"/"स्लैश" in a spoken line is a fail (cf. D2, D6).

- [ ] The bot uses simple, common vocabulary — no hard/Sanskritised administrative words on a low-literacy channel.
  *Why / how to detect:* Flag tatsama/technical terms (सेवा प्रदाता, प्रशिक्षण, मूल्यांकन…) spoken without a plain gloss (cf. D1).

## 9. PII / consent hygiene

- [ ] The bot does not read out IDs, full phone numbers, or other personal identifiers unless the user needs them and it is appropriate.
  *Why / how to detect:* Fail if the bot recites an ID/UUID or spells a phone number digit-by-digit with no reason (contrast the legitimate HR-number fallback in 5449910e).

- [ ] Consent is asked once, before any personal data is shared or a data-writing/sharing action is taken.
  *Why / how to detect:* Expect the share-consent line before the action ("अप्लाई करने पर personal details शेयर होंगी", ce59a84c). A share/write tool firing before consent is a fail (cf. E2).

- [ ] On an explicit consent decline, the bot stops that action cleanly and fires no related tool call.
  *Why / how to detect:* After a "नहीं, शेयर मत करो"-type refusal, there should be no subsequent share/write tool call (cf. E2 hard-stop on decline).

- [ ] Distinct consents (recording/AI vs data-sharing) are kept distinct, not conflated into one.
  *Why / how to detect:* Fail if a single ask is treated as covering both (cf. E2).

- [ ] The bot refuses to share info it must not (e.g. an employer's direct number) rather than inventing or leaking it.
  *Why / how to detect:* Grounded in 1fde1677 (refused to share the employer's direct number). Fail on any leak of withheld data.

## 10. Latency / hold-message behavior during tool calls

- [ ] Background tool calls are silent or covered by a neutral hold ("एक मिनट"/"ಒಂದು ನಿಮಿಷ"/"one moment") — the bot never narrates what it is doing ("प्रोफाइल देख रही हूँ…").
  *Why / how to detect:* Fail if a spoken line or the tool's `hold_message` argument names a lookup/creation/fetch (cf. B2, D34 — `hold_message` narrating a silent step). Read `tool_calls[].arguments` for a revealing `hold_message`.

- [ ] The hold filler does not leak internal terms or claim a result before the tool returns.
  *Why / how to detect:* A hold that says "आपकी जानकारी मिल गई" before the fetch returns is a fail (cf. B2, D8, and §7 fabrication).

## 11. Graceful exit + correct end/drop reason

- [ ] The call ends with a polite closing line appropriate to the outcome — not an abrupt cut and not an endless tail.
  *Why / how to detect:* Grounded in the not-looking exit (328a7fd0 "कोई बात नहीं, सोचिए… Goodbye") and early-hangup handling. Fail on no closing line where the caller was still engaged.

- [ ] A clear "no" / "not interested" at an interest gate ends the call politely — the bot does NOT proceed to fetch/pitch after an explicit decline.
  *Why / how to detect:* Grounded in the correct 328a7fd0 vs the bug f4e85575 (caller said "ಇಲ್ಲ" but the bot kept pushing). Any task step after an explicit decline is a fail.

- [ ] `call_output` records a correct, specific end/drop reason that matches the transcript.
  *Why / how to detect:* Check `drop_reason` / `call_outcome` (e.g. "Said not looking", "Commute distance too far; no personal transport", "Early Disconnect", "Already employed") against what actually happened; a mismatched or generic reason is a fail.

- [ ] An outbound bot does NOT invite callbacks or use inbound-framed closings ("call me/us back when you need").
  *Why / how to detect:* Grounded in D5 (modality leak). On an outbound call, any "you can call me back" ending is a fail; expect "the center will contact you"-style closing.

- [ ] Any mandatory end-of-call step is performed before the goodbye line, at every exit path (success, failure, decline) — not skipped by jumping straight to "Goodbye".
  *Why / how to detect:* Fail if a required pre-goodbye action's output field is still false at the closing line (cf. D10, D19).

## 12. Not repeating the same line verbatim

- [ ] The bot does not repeat an identical utterance across turns (greeting, re-prompt, confirmation, or bridge line).
  *Why / how to detect:* Diff consecutive/near bot turns; the same line appearing verbatim ≥2 times (outside a legitimately-varied re-prompt) is a fail (cf. B1). Re-prompts on silence must be reworded, not copy-pasted (see §3, §4).

## 13. "Who are you / real person or AI?" and "do not call me again"

- [ ] Asked whether it is a real person or AI, the bot answers honestly that it is an automated/AI assistant, without derailing.
  *Why / how to detect:* Look for a truthful AI self-identification; a dodge, a claim to be human, or a long tangent is a fail (relates to the §1 disclosure and the anti-AI scenario 1283e4a9).

- [ ] On "do not call me again" / a clear request to stop, the bot acknowledges, closes politely, and does not continue pitching.
  *Why / how to detect:* Any task/pitch turn after a do-not-call request is a fail; expect a polite close and an end/drop reason reflecting it (cf. D10 do-not-call as a hard suppressor of further steps).

- [ ] On reaching the wrong person / wrong number, the bot confirms identity once and then exits — it does not launch the task flow at an unaffiliated party.
  *Why / how to detect:* Grounded in the wrong-number scenario (DKB e6fdf9e5). Fail if the pitch/flow proceeds after a "wrong number"/"not that person" signal; expect a graceful exit and an Unverified/wrong-number outcome.
