# Four platform asks for LitWiz (Raya) — 2026-09-03, §3 and §4 added 2026-09-08

Both block behaviour we cannot fix in the prompt. Each has call ids.

---

## 1. Speak the apply confirmation from the runtime, on a real result

**The bug.** The agent sometimes tells a caller their application went through when `apply_job` was
never invoked. On `19616c90` the only tool call in the whole call was `get_profile`; the caller heard
"अप्लाई हो गया है" and rang off. Rate is roughly **1 call in 7** where an apply is discussed.
Instances: `19616c90`, `29c4f152`, `1fe093a9`, `4b0ea64d`.

**Why it is not fixable in the prompt.** Three mechanisms were tried and each held on several calls
then failed:
1. a positional rule that the success line may only appear in the same turn as the tool result;
2. declaring parentheticals non-speech and marking every tool annotation in the samples;
3. moving the constraint into the `apply_job` tool description (it is there now, 902 chars).

On `29c4f152` and `1fe093a9` the model even emitted a fabricated stage direction —
`*(Silent tool call: apply_job)*` — as spoken text. That string appears in no prompt; what was copied
is the *format* of a tool call, not any wording, which is why no amount of rewording reaches it.

**We checked for a configuration-side fix and there is none.** Enumerated on agent
`115b38a5-42ef-4082-be69-84a871bb226a`: agent fields are `instructions`, `memory_instructions`,
`output_instructions`, `output_fields`, `tools`, `agent_args`, `webhook_url`, voice/timing settings.
Tool entries carry only `type`, `function`, `api_details{url, header, method, payload_template}`.
There is no post-tool or on-success message hook to configure.

**The ask — either would close it:**
- **(a)** let the runtime speak the confirmation when `apply_job` returns success, the way
  `hold_message` is already spoken when a tool is invoked; or
- **(b)** have the runtime refuse/flag an assistant turn containing the success line when no
  successful `apply_job` result exists in that turn.

(a) is preferred: it makes the sentence unfabricatable rather than policed.

**We rejected a workaround rather than risk the core flow.** Making `hold_message` a required
parameter with a single-value enum would tie the "I'm applying now" line to actually invoking the
tool — but if Raya validates enums strictly and the model sends any other string, `apply_job` fails
and applying breaks outright. Not worth it on the most important function in the product.

---


### Measured rate, added 2026-09-08 — and why the prompt has run out of moves

Of **41 calls that spoke the apply-success line**, 14 had no successful apply behind them:

| | n |
|---|---|
| `apply_job` never called at all | **5** (+ `910b2d29` today, not in that window) |
| `apply_job` called and errored | 9 |

The five outright-fabricated ones are on five DIFFERENT bots — `kkb-hi-in`, `kkb-hi-signals`,
`kkb-kn-out`, `maya-hi-in-signals`, `maya-hi-out` — so this is not one bot's prompt.

**Three of the six are a form we have now closed.** `35de19e7`, `1b7fb500` and `78ef362f` wrote the
tool call out as prose — *"एक मिनट। \*(Silent tool call: create_profile with agentId: …)\*"* — and a
rule about bracketed markers and stage directions went into all 21 prompts on 2026-09-08.
`bracket_leak` has been clean over the 252 calls since. A fourth, `febe0441`, used the bridge line
("ठीक है, आपकी तरफ़ से अप्लाई कर देती हूँ") that was forbidden on 2026-09-04.

**Two are the bare form, and that is the one we cannot reach.** `4b6aca57` and `910b2d29` (today)
simply say *"अप्लाई हो गया है। आमतौर पर अगर shortlist होता है…"* — no stage direction, no bridge line,
no tell of any kind. On `910b2d29` the bot asked the data-sharing line, asked the consent line, got a
yes, said *"एक मिनट। एक सेकंड।"* and then the success line, **having made zero tool calls on the
entire call** — not even `get_profile`.

**A hypothesis we tested and dropped, so you don't have to:** that the model imitates the surface
form of a tool call, since `hold_message` lands in the post-result turn rather than being played
during it (§3), making "hold phrase + outcome" indistinguishable in the transcript from a real call.
It does not hold — 40% of fabricated success lines carry a hold phrase against 53% of genuine ones.

**Why §1 is the only remaining route.** The prompt states the constraint as explicitly as language
permits: a positional rule ("the success line may ONLY appear in a turn containing a fresh successful
`apply_job` result"), a hard law ("never claim an action you have not performed"), a 7,000-character
section on parentheticals and describing-is-not-calling, and four prior occurrences cited by id. It
has still happened today. **The confirmation line should be emitted by the runtime on a real
`apply_job` success, not composed by the model** — that is the only version of this that cannot be
fabricated.

### Update 2026-09-09 — a post-fix occurrence, and the prose guard has now failed six times

Tonight we removed the last thing the prompt could have been imitating: the guard against speaking
stage directions had been QUOTING the forbidden string verbatim (`*(Silent tool call: apply_job)*`),
in both the rule and its own evidence citation. That string is now gone from all 21 prompts.

**It did not fix this.** Call `6acd1397` (kkb-kn-out, 2026-09-09, after the deploy) contains no stage
direction at all — and still said **"ಅಪ್ಲೈ ಆಗಿದೆ"** at turn 23 with **zero tool calls on the entire
call**. Not `apply_job`, not `get_profile`, nothing. The tools are correctly configured on that agent
(`get_profile`, `apply_job`, `create_profile` all present in its config).

Occurrences of the same failure: `29c4f152`, four calls on 2026-09-03, `910b2d29`, `e4e81fe2`,
`6acd1397`. **Eight.** The prompt states the rule about as directly as language allows — "never speak
the apply-success line unless a successful `apply_job` result is in front of you in this turn" — and
adds that emitting a description of a tool call does not call the tool.

Measured rate across all recent traffic: **45 of 254 real conversations made zero tool calls (18%)**,
and **4 of 254 claimed an apply anyway (1.6%)** — kkb-hi-signals, kkb-hi-in, kkb-kn-out, maya-hi-out.
Most of the 18% is DKB, where a call that never reaches a posting legitimately calls nothing.

We have exhausted the prompt side and we are not going to add a ninth wording. The ask in §1 stands
and is now the only remaining route: **the runtime should emit the apply-confirmation line, on a real
tool result.** A sentence that asserts a state change should not be something the model can produce
without the state change having happened.

## 2. Surface the tool error reason to the model

**The bug.** The agent cannot tell "you have already applied" from "this failed for a technical
reason", so real duplicates are reported to callers as technical faults (`d6e545d4`, `d401d6cf`) and,
before we gated it, a never-attempted job was called already-applied (`c5a10922`).

**Why.** The model receives only `[Error: apply_job request failed (HTTP 422).]`. The reason —
`ACTION_LIMIT_REACHED`, `TARGET_ITEM_NOT_FOUND` — is in a `__RAYA_TOOL_DEBUG__` block written for the
transcript, not given to the model. Proven across 10 calls. Both causes return 422, so status alone
cannot separate them either.

The other two possible sources are also closed: `contact_memory` is empty on the calls where it
matters, and `get_profile` does **not** return the caller's applications (verified on `d6e545d4` —
its only non-profile item was an unrelated draft job posting the test number owns as a provider).

**The ask — any one of:**
- pass the response body's `error` / `message` fields to the model with the tool result; or
- return distinct HTTP statuses per cause; or
- include an applications list in `get_profile`.

Until one lands, the owner's three-outcome spec (already-applied / technical / success) is not
achievable, and the prompt is deliberately gated to say the neutral technical line rather than guess.

### 2026-09-04 — this is now measured, not inferred (tracker row 103)

Row 103 ("bot is saying technical issue instead of already applied") was re-opened. The proof that no
prompt change can close it:

**Every named error class produces the same spoken line.** Across all six Signals bots, 2026-09-01 to
2026-09-04, 133 tool errors carrying a named `error` field in the response body:

| error in the response body | events | what the bot said next |
|---|---|---|
| `ACTION_LIMIT_REACHED` | 95 | the generic failure line ("technical issue है") |
| `TARGET_ITEM_NOT_FOUND` | 20 | the same generic failure line |
| `MINOR_ACTION_CHANNEL_BLOCKED` | 13 | the same generic failure line |
| `SOURCE_ITEM_NOT_FOUND` | 2 | the same generic failure line |
| `INVALID_ITEM_STATE` | 2 | no failure line at all (the write was narrated as done) |
| `PROFILE_LIMIT_REACHED` | 1 | the same generic failure line |

**Not one call in 133 produced a line that distinguishes one error class from another**, while the
prompt names `ACTION_LIMIT_REACHED` in five separate places and the `apply_job` tool description
carries the mapping. Over the same window the model demonstrably reads *successful* tool results — it
speaks names, roles, ages and locations out of `get_profile` on every call. So it is not that the
model ignores the reason; it is that the reason is not in what it receives.

Confirmed again by harness call `row103-hi-postfix` (tester leg `ae2481e6`), run after two prompt
fixes that removed the last two internal contradictions blocking the branch: `apply_job` returned
`ACTION_LIMIT_REACHED` with the message "An active request already exists between these two profiles"
and the bot still spoke the technical line. Row 2's own definition — *"an error with no reason you can
read"* — is the correct branch on every failure while the body is withheld, so the already-applied
branch is **unreachable by construction**, not intermittent.

### It fails in BOTH directions, which is the part that makes it unfixable in prose

Without the reason, the model is choosing between two lines with no information, and it gets both
wrong:

| direction | measurement |
|---|---|
| says **"technical issue"** when the application really was already in place | **45 of 60** `apply_job` calls that returned `ACTION_LIMIT_REACHED`, 2026-09-03/04 (tracker row 103) |
| says **"your application is already in place"** with no evidence for it | **8 calls** in 668, 2026-09-03/04 — `c5a10922`, `49938255`, `fd464bc0`, `c00e7ba5`, `87427928`, `72112c10`, `537549c6`, and `5f0d3671` where the error was `USER_NOT_FOUND` |

The prompt already gates the second direction: row 1 requires either an `apply_job` retry for the
same job inside the call, or `contact_memory.jobs_applied` naming it. Those eight calls satisfied
neither. Every prose tightening we can make on one direction pushes the failure into the other, which
is what happened when we tried it: the fix that made row 1 reachable off the error name produced
`5f0d3671`, and reverting it restored the 45-of-60. There is no wording that resolves a distinction
the model cannot observe.

**One extra thing you should know about inbound:** inbound calls arrive with **empty `agent_args`**,
so `contact_memory` is never present on them. On an inbound bot the evidence gate can therefore only
ever be satisfied by a same-job retry inside the call — memory evidence is structurally unavailable.
Three of the eight are inbound for exactly that reason.

Standing check: `raya/regression/apply_result_integrity.py`, findings `V` (guessed row 1) and
`W`/`W?` (what the model asserted vs what the API said).

### The endpoint we need ALREADY EXISTS — it is a scoping problem, not a build (2026-09-04, probed)

This part is for the **Signals / Blue Dots API owners**, not LitWiz. Read-only probing of both
production instances found:

- **`GET /api/v1/action/fetch` exists and works.** It returns `{"meta":{"total":…,"limit":20,"offset":0,
  "applied":{"sort":"recent","statuses":[],"types":[],"facets":[]}},"actions":[…]}` and validates
  query params (`types`, `statuses`, `limit`, `offset`, `sort`, `facets`) — a 400 names the bad one.
- **But the acting org cannot see the actions it created itself.** On call `e853e2c0` our apply
  succeeded and returned `action_id: 4fbb97ec-5e2e-4df8-b878-1c0c9262cfaf`. Fetching it back from the
  same instance with the same credentials returns `total: 0` for every filter we tried — no params,
  `acting_as_user_id`, `source_item_id`, `types=apply` — and there is no by-id route
  (`/api/v1/action/{id}` → 404).
- `?item_id=<the seeker profile>` returns **403 `FORBIDDEN_ITEM` — "item_id is not owned by the
  caller"**, which is the scoping rule: `action/fetch` is limited to items the calling org owns, and
  the caller org owns neither side of a seeker→employer application. `admin/participant` has no such
  restriction, which is why profile reads work and action reads do not.

**So the concrete ask is small:** let the org that PERFORMED an apply read that apply back — either by
scoping `action/fetch` on the actor as well as the item owner, or by accepting
`acting_as_user_id` / `source_item_id` as an admin-style filter the way `/api/v1/admin/participant`
already accepts `phone_number`. With that, the **pre-tool** duplicate check runs against real data
instead of `contact_memory`, and both directions of this bug close at once: no "technical issue" on a
real duplicate, and no guessed "already applied", because `apply_job` is simply never called for a job
the caller already applied to. It also removes the need for the error body to be surfaced at all for
this particular case.

**Add to the ask, in priority order:** an applications list on `get_profile` would also close it
(and would let the pre-tool duplicate check work, which is the only path that has ever produced the
line correctly), but passing `error`/`message` through with the tool result is the smallest change
and fixes all six classes at once.

**One of the six is a data problem, not yours:** `MINOR_ACTION_CHANNEL_BLOCKED` ("This participant is
a minor; actions for minors must be completed in the app") fired 13 times, on profiles whose stored
`age` is 18 — a value that looks like a default rather than a real age (`a5547492` age 18, caller
said 28 on `af52d37c`). Any caller carrying that default can never apply by phone, and today they are
told "technical issue" and then offered more jobs that fail identically. That one is for the data
team.

---


## 3. `hold_message` is accepted and never played — it lands AFTER the tool result

**Added 2026-09-08.** This is the concrete cause of the recurring "prominent latency after each turn
at the start" complaint from QA (reported 2026-09-07 and again 2026-09-08). We had previously told
Parth latency was not measurable from the API. That was wrong: the per-turn *timing* is not exposed,
but the per-turn *ordering* is, and the ordering shows the problem.

**What we measured.** Over **1,152 calls across all 18 conversation bots** (every call the API returns
for each agent), we took every assistant turn that issues a tool call carrying a `hold_message` and
asked one question: is there any assistant turn with content between that tool call and its tool
result?

| | count |
|---|---|
| tool calls carrying a `hold_message` | **348** |
| of those, with audio during the tool round-trip | **0** |
| of those, silent for the entire round-trip | **348** |
| tool calls with no `hold_message` supplied | 6 |

**348 of 348.** Not one. And the hold text is not lost — on the Signals subset it reappears at the
**start of the assistant turn after the result**, in **208 of 217** cases:

```
[assistant → TOOL_CALL] get_profile({"phone_number": "91XXXXXX6073", "hold_message": "एक मिनट।"})
[tool]                  {...profile...}                     <-- caller hears NOTHING for this whole span
[assistant]             एक मिनट। खुशी जी, पिछली बार हमारी…    <-- "one minute" arrives after the wait ended
```
Live examples: `7b841e6b`, `55a44edb`, `1536830c` (KKB Hindi Signals), `09a7b6c8`, `2c197514`
(DKB Hindi Signals).

**Why it is felt at the start of the call specifically.** Of the 348 silent round-trips, **189 are
`get_profile`**, which fires immediately after the greeting on every call. The rest: `apply_job` 88,
`create_job` 26, `update_profile` 21, `create_profile` 11, `update_job` 5, `get_talent_insights` 4,
`update_job_details` 3, `update_job_status` 1. So the very first thing a caller experiences is dead
air for a full API round-trip, followed by a filler phrase telling them to wait for something that
has already happened.

**Corroboration that this is long-standing.** `DKB Hindi Signals.md` carries the instruction
*"`hold_message` stays an EMPTY string `""` on every tool call (the platform SPEAKS whatever is in
it) — DKB uses no spoken 'one moment' filler."* Someone had already noticed the stray post-result
utterance and worked around it by emptying the parameter — which removes the artifact but leaves the
silence.

**The ask.** Play `hold_message` as audio when the tool call is issued, not as text prepended to the
model's next utterance. If that is not feasible, say so explicitly and we will stop supplying it and
instead script a spoken filler turn before the tool call — but that costs an extra model round-trip,
so we would rather not.

**Why this is not ours to fix.** The parameter is the platform's mechanism for exactly this purpose;
the prompt has no other way to emit audio during a tool call, because the tool call and the spoken
turn are the same turn. We are not asking for a guess at timings — we are reporting that a documented
parameter has no observable effect in 348 of 348 uses, with the ordering visible in the transcripts
you serve.

---


## 4. Is the platform's own memory store injected alongside `${contact_memory}`? (added 2026-09-08)

**Two questions, both cheap for you and unanswerable from here.**

**(a) Does `memory_enabled: true` inject a memory record into the model's context in addition to the
`${contact_memory}` argument?** On `d15a8f9b` the fixture set `contact_memory` to the literal string
`"Not Available"` — and the bot nonetheless opened its role check with *"पिछली बार हमारी बात एक जॉब
में अप्लाई करने के बारे में हुई थी"*, a specific claim about a previous conversation. That content is
not in the argument we sent. If there is a second memory source, our prompts do not know about it:
every rule they carry about deciding from memory reads the `${contact_memory}` block, and a caller's
opener, role check and location turn all branch on it.

**A second, cleaner instance — and this one is unambiguous.** `2ea06509` (`dkb-hi-signals`,
2026-09-08 16:14) was sent exactly two arguments: `contact_memory` set to the literal string
`"No Old Memory, Mandatory get_profile for the user"`, and `country_code`. No `company_name`. The
call made **zero tool calls**. It opened with **"हैलो! क्या आप VANS TRADING COMPANY से बोल रहे हैं?"**
— the value from a dial ten minutes earlier on the same number. `dkb-hi-signals` has
`memory_enabled: True` and its memory prompt records `business_name` keyed on the phone number, so
the path is documented rather than guessed: **memory prompt → platform store → next call's context,
bypassing `${contact_memory}`.**

That is confirmation, not a hypothesis. What we need from you is the shape of it: **is the store
injected as text in the system prompt, as a separate message, or into the model's state? And can it
be read or cleared per number?** Three things depend on the answer — our prompts' memory rules all
read `${contact_memory}` and are therefore reading half the picture; our harness cannot run a clean
negative test, because omitting an argument does not remove the value; and a value arriving this way
bypasses the conversion rules attached to argument slots, which is exactly how `2ea06509` came to
speak a business name in Latin script.

**(b) What decides Maya's opener?** Same prompt block, byte-equivalent between two bots, and:

| bot | `college_name` | branch A (names the college) |
|---|---|---|
| `maya-hi-out` | `VTU`, `Ghaziabad Institute of Technology` | **48 / 48** |
| `maya-hi-signals` | `VMLG College` (345 of 460 calls), `LR College` | **2 / 14** |

Twelve of fourteen campus callers were greeted with no institution, which removes the entire premise
of the call. We have ruled out, by controlled dial rather than by reading:

- **`contact_memory`** — `910b2d29` omitted it entirely and still opened with no institution;
- **the prompt text** — the two files' opener blocks are byte-equivalent, same length, same order;
- **a duplicate demonstration** — the institution-free line appears exactly once in the prompt, the
  named line twice;
- **an unsubstituted token** — `b6353cfb` spoke `VMLG College` aloud, so the value does reach the
  model on this bot.

Three prompt framings have now failed (the first made branch A never fire, `24293fbe`). We are not
writing a fourth. **What differs between these two agents other than their instructions?** If the
answer is the memory store, or argument delivery, or anything else in the agent config, that is the
thing to change — and if `college_name` is reliably supplied on the campaign, the cleanest fix is to
stop making the bot choose: send a value that is always speakable and let the opener be one line.

## What we did on our side

- Gated the already-applied line on citable evidence, so the agent can no longer invent it
  (`e654b215`, `a5a68701`: three failing applies, no false duplicate claim).
- `raya/regression/apply_result_integrity.py` check Z detects every fabricated success, and
  `fleet_report.py` treats it as blocking — the fleet reads FAIL while ask 1 is open, by design.

---

## A fourth prompt attempt we considered and rejected

The obvious next move is to **invert the default**: instruct that unless a successful `apply_job`
result is visible in this turn, the line the agent says is the technical-issue line. That is
mechanically different from the three attempts above — it changes which output is the fallback rather
than forbidding the wrong one — so it is not merely a fourth wording.

We are not doing it, because **its downside is symmetric with the bug it fixes.** If the model fails
to "see" a result that did arrive, it tells a caller their application failed when it actually
succeeded. That caller re-applies (and hits `ACTION_LIMIT_REACHED`, which we cannot explain to them
either) or gives up on a job they already hold a live application for. Trading a false success for a
false failure is not an improvement; it just moves who gets hurt.

This is why the ask is a runtime one. The runtime is the only place that knows, with certainty,
whether the write happened — and a confirmation spoken from that knowledge cannot be wrong in either
direction. Everything a prompt can do here is a guess about what the model can see.

---

## 5. We need a way to clear a contact's memory store (added 2026-09-09)

**The bug.** `dkb-hi-signals` announced the same fabricated posting on **eight consecutive calls**,
byte-identical every time — a role and a salary that were never supplied — while the arguments
carried different values (`job_role: "Sales"`, `salary: "30000"`, and on one call every field
`"Not Available"`).

Calls: `714ebfc0`, `cc1b0ecc`, `965f9d06`, `dfaf30eb`, `90bd2e80`, `71c66134`, `0c870680`,
`9ba6186a`.

**What we ruled out, in order, each with a deploy and a live call after it:**

| # | hypothesis | change made | result |
|---|---|---|---|
| 1 | worked example values printed beside the template | stripped them from 18 prompts | unchanged |
| 2 | no rule saying the argument beats memory | added at the point of use, 4 prompts | unchanged |
| 3 | the remembered value did not read as historical | date-stamped `budget_per_hire` in the memory prompt | unchanged |
| 4 | our own evidence note quoted the bad sentence | removed the verbatim quote | unchanged |
| 5 | `roles_posted` stored the posting itself | changed to store a COUNT, all 4 agents | unchanged |

The sentence does not appear in any prompt — verified against the LIVE instructions, not the repo
copy. `contact_memory` is **absent from `agent_args`** on every one of those calls, and
`memory_enabled` is true.

**What we think is happening.** Fix 5 changes what the memory prompt WRITES from now on. It cannot
touch what is already in the store. Entries written before the fix are still there and are still
being injected, and the store keeps winning over the arguments.

**What we need.** Either an endpoint to clear (or read) a contact's memory for an agent, or
confirmation of how long entries persist and whether a write replaces or appends. We probed
`/api/memory`, `/api/contact`, `/api/contacts`, `/api/contact_memory`,
`/api/agent/{id}/memory` and `/api/agent/{id}/contacts` — all 404. Without one of those we cannot
verify any memory-related fix, because every test call reads a store we cannot inspect or reset.

**Note on the equivalent KKB bug**, for contrast: the same field shape
(`last_options_presented`) caused the same failure on the seeker bots, and the same fix verified
clean on the second call (`7bf46d06`, 1 job supplied and 1 offered, after a 12-job call). So the
memory-prompt lever DOES work — which is why the DKB case reads as stale store contents rather than
a wrong rule.

### PROVEN 2026-09-09 — memory OFF makes the same call correct

`59a87113`, same agent, same fixture, same arguments, `memory_enabled: false`:

> "आपकी एक posting है — **सेल्स**, दो vacancies, सैलरी **तीस हज़ार**"

`job_role: "Sales"` spoken as "सेल्स", `salary: "30000"` spoken as "तीस हज़ार", and with
`company_name` absent it took the no-name branch instead of greeting with an earlier caller's
business. **Every field correct.** One call with memory off, against eight byte-identical wrong
calls with it on.

That closes the diagnosis: the prompts are right, the memory STORE contents are the bug, and the
five prompt-side fixes could never have worked because they only affect what is written from now on.
`memory_enabled` has been restored to `true` — turning it off is a product decision, not ours.

**The ask is now specific:** clear the stored memory for this contact/agent pair, or give us an
endpoint to do it. Every DKB memory test until then reads a store polluted by earlier calls.

**Likely lower severity for real owners than these numbers suggest**, and worth saying: our tester
DID has been used across many different businesses, so its store holds several owners' postings. A
real owner's store holds only their own, where remembering the last posting is closer to correct
than wrong. The mechanism is proven; the production blast radius is probably smaller than 8/8.

### 2026-09-09 — the fabricated apply is now ISOLATED: three causes tested and ruled out

The claim "you have been applied" with **zero tool calls on the entire call** survives all three
things it could plausibly have been. Each was tested with a deploy and a live call after it:

| hypothesis | test | result |
|---|---|---|
| the memory store licenses the claim (`jobs_applied` makes the model believe an application exists) | `memory_enabled: false` on kkb-kn-out | `557fbeb0` — still claimed it, still zero tools |
| the bot narrates the tool call instead of making it, and the narration substitutes for the call | removed the marker form from the rule | `2126a5bc` — still narrated, still claimed it |
| the SAMPLES demonstrate a speech-shaped stage direction the model reproduces | converted all 151 `*(NOT SPOKEN …)*` annotations to `INTERNAL:` lines | `f31e1587` — **narration and the phone-number leak are GONE**, and the claim REMAINS with zero tools |

That last row is the useful one: it fixed a real caller-facing privacy leak and proved the two
behaviours are independent. The fabricated claim is not a side effect of the narration.

So what is left is exactly what §1 asks for: the model emits a sentence asserting a state change
without the state change having happened, and no prompt-side construct we have found prevents it.
Latest occurrence `f31e1587`, 2026-09-09, on a prompt with the guard stated, the demonstration
removed, and memory irrelevant.

### 2026-09-09 — the already-applied line: four mechanisms, one clean test, no movement

`5bbb6ca1` is the test we had been unable to construct all night: `apply_job` invoked once,
`ACTION_LIMIT_REACHED` returned, and every prompt-side lever live on that agent at the same time.

The bot said the generic failure line — "इस जॉब के लिए अप्लाई अभी पूरा नहीं हो पाया" — **three times.**
The caller has an application and was told the apply had not gone through.

What was live on that agent when it did that:

1. Row 1's condition names `ACTION_LIMIT_REACHED` explicitly, and has for weeks.
2. The generic failure row was rewritten tonight to EXCLUDE `ACTION_LIMIT_REACHED` and the duplicate
   case in so many words — "Those go to Row 1 and this row does NOT apply to them."
3. The `apply_job` tool description was corrected tonight from "an error whose reason you usually
   CANNOT read" to "an error NAMING its reason in `"error":"..."` - READ IT. ACTION_LIMIT_REACHED
   ... means the caller ALREADY APPLIED: say so plainly, never call it a failure."
4. There is now exactly ONE generic failure line, so there is no second wording competing.

Measured rate, unchanged: **4 of 34 calls (12%)** get the correct line when `ACTION_LIMIT_REACHED`
comes back. `ESCALATION-litwiz.md` §1 framed the same thing as 45 of 60.

One observation that may help you: the 4 that DO get it right are all INBOUND agents, which arrive
with empty `agent_args` and therefore no `${recommendations}` in context. Every failure is on an
agent carrying a job array. That is a context-competition pattern, not a wording problem, and it is
not something we can fix from the prompt.

**We are done trying on our side.** Four mechanisms, each deployed and each tested against a live
call that reached the condition. This needs the runtime to select the line off the tool result.

### 2026-09-09 — BOTH routes to the already-applied line fail independently

Row 1 has two documented routes and neither works. That is the complete picture, and it is why we
cannot fix this from the prompt.

**Route A — the duplicate pre-check.** Reads `jobs_applied` out of `${contact_memory}` and is
supposed to prevent the redundant apply entirely. Two separate failures:
- the array is almost always empty — non-empty on **2 of 76** calls that carried it, because the
  memory prompt never said a successful `apply_job` result is what writes it (now fixed);
- and it does not fire even when the array IS populated. On `7f2e3928` we injected
  `contact_memory` with `jobs_applied: ["2026-09-08: Field Salesperson, Shree Krishna Industrie,
  Ghaziabad"]` and put that same job in `${recommendations}`. The agent called `apply_job` anyway.

**Route B — recognising the error name.** `ACTION_LIMIT_REACHED` in the tool result. Succeeds on
**4 of 34** calls (12%), and all 4 are inbound agents with empty `agent_args`. Four prompt-side
mechanisms were deployed against it and each failed against a live call (`6caf1fbe`, `513a1d01`,
`5bbb6ca1`).

So: the prevention path ignores memory it is told to read, and the recovery path ignores an error
name it is told to read. Both are stated plainly in the prompt and in the tool description. We have
no further lever.

**One more data point that closes it.** `ff6accc0`, immediately after the successful apply on
`7f2e3928`: `apply_job` called again, `ACTION_LIMIT_REACHED` returned — so the application really
was on record — and the agent still spoke the generic failure line. On that call `contact_memory`
was absent from `agent_args` entirely, so the only memory channel is the platform store, which we
cannot read.

Net: we can neither observe what memory holds nor make either route fire. Three specific asks, in
priority order:

1. **The runtime should select the apply-outcome line from the tool result** (this is §1). A
   sentence asserting a state change should not be producible without the state change.
2. **An endpoint to read and clear a contact's memory store** (this is §5). Without it, no
   memory-related fix on any bot can be verified — we hit this on DKB too.
3. Confirmation of whether the duplicate pre-check is expected to work at all, given it ignored a
   `jobs_applied` entry naming the exact job in `${recommendations}` on `7f2e3928`.
