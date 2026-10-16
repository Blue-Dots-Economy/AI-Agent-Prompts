# The slim-prompt experiment

`KKB Placeholder Hindi Signals.md` is **219,519 characters**. The team's target for optimal Raya
performance is **under 50,000**. This directory holds the rewrite, the bot it runs on, and the
tooling that decides whether the rewrite is as good as the original.

## What is here

| file | what it does |
|---|---|
| `extract_spec.py` | pulls the behavioural contract out of a prompt — every distinct spoken line, tool, input variable and payload identifier |
| `compare_spec.py` | diffs two prompts' specs and lists what the slim one dropped, drifted or invented |
| `create_slim_bot.py` | clones a live Raya agent field-by-field, changing ONLY `instructions`, so an A/B measures the prompt and nothing else |
| `ab_compare.py` | dials both bots with the same fixture and persona, alternating, and scores every call mechanically — latency proxy plus nine shared invariants |
| `slim-v1-reference.md` | the first draft, kept so later compression passes can be diffed against it |
| `diff-hi.json` | the machine-readable spec diff |

## The bots

| | uuid | prompt | chars |
|---|---|---|---|
| fat (live) | `115b38a5-42ef-4082-be69-84a871bb226a` | `KKB/KKB Placeholder Hindi Signals.md` | 219,518 |
| slim (A/B) | `140d13ca-c80f-47c4-9454-5edb3fd38c96` | `KKB-Slim/KKB Slim Hindi Signals.md` | 68,744 |

Everything else on the two agents is identical and was verified field by field after creation:
language and voice ids, the whole tool schema, the DID, `allow_interruption`,
`min_user_speech_to_interrupt`, `required_silence_after_speech`, the nudge thresholds,
`max_call_duration_mins`, the webhook, and the memory and output prompts. The slim bot carries no
production traffic.

Two incidental differences worth knowing: Raya **derives `agent_args` from the `${...}` tokens in
the instructions**, so the fat bot has a seventh argument, `college_name`, that KKB does not use
(a stray mention somewhere in the 219k), and the slim bot has only the six real ones. And the
create endpoint rejects `agent_args`, `memory_enabled` and `memory_instructions`, so the clone is
POST-then-PATCH, one key per PATCH — the Zod schema rejects the whole body if any single key is
unrecognised.

## Why it is 68,744 and not 50,000

The 219k is not padding. Measured composition of the original: 10% is provenance prose (call ids,
"this used to say", failure anecdotes), 4.9% is exact duplicate paragraphs, **`# No-Match Fallback`
appears twice** (23,723 chars for one section), and 37% of the file sits in 128 paragraphs of over
400 characters each. Removing all of that — every duplicate, every anecdote, one copy of No-Match,
and rewriting the guard prose as tables and single imperatives — lands at **68,744 (a 69% cut)**
with the contract intact.

Getting from there to 50,000 means removing behaviour, not words. The arithmetic, for the record:

| candidate | saves | leaves | what it costs |
|---|---|---|---|
| both worked calls | 5,754 | 62,990 | the samples are what the model actually follows — analyser D50, D63, D74 all describe a sample outvoting a rule |
| the whole ASR/confirmation section | 2,958 | 65,786 | phonetic confirmation on roles, places, option numbers and experience |
| all Situations | 1,472 | 67,272 | silence, distress, proxy callers, do-not-call, "are you a bot" |
| Canonical Location Spellings | 1,777 | 66,967 | the caller hears a mangled version of their own town |

All four at once still leaves **56,657** — and would have removed the samples, the ASR guards, the
dignity handling and the TTS spellings. So 50,000 is not reachable for this bot's current behaviour
surface. The honest options are to cut behaviour deliberately (an owner decision, with the list
above as the menu) or to accept 68,744.

**And the premise is testable.** The 50k target is a proxy for latency. There is a *measured*
latency cause that has nothing to do with prompt size: `hold_message` is never played during a tool
call — **348 of 348** tool calls across 1,152 calls on all 18 bots had no audio at all for the whole
tool round-trip, 189 of them `get_profile`, which fires at the top of every call (see
`ESCALATION-litwiz.md` §3). So before spending more on characters, `ab_compare.py` should say
whether 68k is measurably faster than 219k at all.

## The flow, which is the point of the rewrite

The 219k prompt describes this same call in 148 sections whose order does not match the order of the
call, with the No-Match handling in two places and the location work spread across four. The rewrite
is 14 numbered steps in the order they happen, so "what do I do next" is never a judgement call.
This is the whole map — a reviewer can check the design without reading the prompt:

| step | one turn each unless noted | what it guarantees |
|---|---|---|
| 0 | pre-check | count the array *before* greeting; an empty array has its own line and never becomes an invented job |
| 1 | audio check | one line, no greeting, at most one repeat, never revisited |
| 2 | introduction | said once per call; ends on the question; **no tool call in this turn** |
| 3 | silent `get_profile` | never revealed; picks the `profile_1.0`+`seeker` item, never `items[0]` blindly |
| 4 | name + memory + role check | one turn, one question; a qualification is not a role; nothing the profile holds is ever re-asked |
| 5 | orient, then the location turn | Case A/B, then CONFIRM → one finer detail (first call only) → jobs. Hard cap of three location turns |
| 6 | present jobs | gated on step 5 having happened; role-relevant only, never padded to three; no counts spoken |
| 7 | deep dive | ends on the doubts question; "no doubts" is a green light, not a decline |
| 8 | minimum fields | validate the set, ask only the gaps; the home city is bounded and never loops |
| 9 | consent | new/draft only, once, and `create_profile` is blocked until it is given |
| 10 | apply | data-sharing line first, duplicate check before the tool, then ONE path — one tool or two, never batched |
| 11 | the result | one line looked up from the result, never chosen; success continues into the offer, failure ends on another job |
| 12 | finish the record | only the missing fields, one per turn, persisted as you go, then the labelled read-back |
| 13 | Need Capture | one offer, owed on every engaged call, immediately before the exit |
| 14 | graceful exit | checks the offer was made, reflects one line, ends on Goodbye |

Then four reference sections the steps point into rather than repeat: **No-Match Fallback** (once, not
twice), **Tools** (four payloads and their enums), **Speaking** (script, canonical places, TTS),
**Hearing** (ASR and confirmation), and **Situations** (silence, emotion, proxy, do-not-call, "are you
a bot"). Two worked calls at the end, chosen for disjoint paths: an apply that succeeds, and a
no-match that ends in a preference capture.

## A/B results — 10 calls, 5 per side, same fixture and persona

Run alternating so line conditions hit both sides.

| | median s per agent turn | turn counts | applies | invariant failures |
|---|---|---|---|---|
| fat, 219,518 chars | **16.00** | 14, 6, 18, 16, 16 | 6 | 7 |
| slim, 68,744 chars | **14.75** | 12, 12, 70, 17, 10 | 4 | 5 |

**A 69% prompt cut bought about 7% per turn.** The fat bot's figure is strikingly consistent across
calls of very different lengths — 16.0, 16.0, 16.5, 16.06, 13.44 — which says the metric is measuring
something real and that the per-turn cost is nearly independent of how long the call is. Slim's set
contains one 70-turn outlier at 4.43 s/turn; excluding it the median is 14.97, so the conclusion does
not rest on it.

That is not the step change a 219k → 50k target implies, and it is consistent with the measured
cause: `hold_message` is never played, so **348 of 348** tool calls sit in silence for a whole API
round-trip whatever the prompt length (`ESCALATION-litwiz.md` §3).

### Quality: the two prompts fail on the same things, at similar rates

Both sides produced the same failure classes. **This corrected a conclusion I had drawn from a single
call.** After the first run I recorded that slim had regressed on speaking payload company names
raw, because slim's `90658584` did it and the fat prompt had got it right on `02c5f7f0`. The second
run's fat call `ea0477f4` then did it **five times in one call** — `SARA ENTERPRISES`, `BayLink`,
`GLOBAL CHEMICALS` — so it is a shared bug of both prompts and not a cost of the rewrite.

| failure | fat | slim |
|---|---|---|
| payload value spoken in Latin | `ea0477f4` (×5) | `90658584` (×3), `f90a0b97` (×1, a salary in digits) |
| ordinals restarted at पहला | `09978532` | `4d6d4d02` (four restarts) |
| introduction spoken twice | `891ff246` | — |
| caller's place substituted in the location sentence | `1450f797` (गाज़ियाबाद) | `8eb83bc2` (साहिबाबाद) |

**What that means for the rewrite.** The 219k of extra prose is not buying adherence on any of the
classes the harness can see. It also is not the *cause* of them: the location substitution and the
company-name leak occur at the same rate on both. Both findings point the same way — these are
mechanism problems (a competing instruction, a rule stated nowhere near the line that consumes the
value), and neither more prose nor less changes them.

The company-name leak has since been fixed the way D71 says to fix this class — the conversion is now
stated **at the point of use**, in the job-presentation format itself, in all 12 KKB/Maya prompts and
in the slim prompt. That is the one place the rule was never stated, despite being stated five times
elsewhere. Both sides need re-dialling to confirm it.

### Post-fix round: three fixes verified on the slim prompt in one run

Four more calls after the point-of-use conversion shipped to both bots.

**`317bd6e0` (slim) is the cleanest call either bot has produced.** Same fixture that had produced
the leaks:

> हमारे पास आपकी जॉब की लोकेशन **सरजापुर** है, और अभी जॉब्स गाज़ियाबाद, नोएडा और ग्रेटर नोएडा में हैं …
> पहला: **टेली मार्केटिंग फीमेल**, **ग्लोबल केमिकल्स**, गाज़ियाबाद, सैलरी **बीस हज़ार से पच्चीस हज़ार**.
> दूसरा: मार्केटिंग, **सारा एंटरप्राइज़ेज़**, गाज़ियाबाद …
> मार्केटिंग, सारा एंटरप्राइज़ेज़ में, गाज़ियाबाद — … **क्वालिफिकेशन:** एक से दो साल का अनुभव।

Four separate fixes visible in one call: the off-list location converted (`Sarjapur, 110045` →
सरजापुर), the payload company and role names in Devanagari (`GLOBAL CHEMICALS`, `SARA ENTERPRISES`,
`Tele Marketing Female`), the salary in words, and the qualification label in Devanagari where it
used to read `Qualification:`.

| | post-fix calls | invariant failures |
|---|---|---|
| slim | `317bd6e0`, `69155e23` | **0** |
| fat | `fa9a16c0`, `9d479905` | 3 (ordinal reuse, a location substitution, a short call) |

The payload-name conversion is verified on both prompts; the fat proof is the `ea0477f4` →
`fa9a16c0` before/after twelve minutes apart. What is **not** fixed on either is the location
substitution — `69155e23` still said साहिबाबाद — and the ordinal restart.

**One thing found here that argues against a habit I applied all day.** On `69155e23` the slim bot
said **"आप अभी 'Any' का काम देख रहे हैं"** — which is, verbatim, the sentence the prompt quotes in
order to forbid it: *never "आप Any का काम देख रहे हैं"*. Naming the exact wrong string is usually
what makes a ban stick (D50), but for a **template** prohibition — one containing a slot the model
fills — the quote is also a ready-made sentence.

It is one occurrence, and the counting rule cuts the other way here: `role: "Any"` appears on **144**
of the cached calls and the forbidden line was spoken on **none** of them, so the guard holds on
about 144 of 145 observed cases. **No edit was made.** Recorded so that if it recurs there is a prior
occurrence to count from, rather than re-worded on the strength of one call.

### Experiment 1 on the slim bot: naming the attractor — FAILED, and the diagnosis was wrong

The location sentence's caller-place slot has failed three wordings. The fourth is not another way
of saying "say the value you were given" — it names the thing none of the three mentioned.

**The evidence that suggested it.** Of the five substitutions on record, four said **साहिबाबाद** and
one **गाज़ियाबाद**, for a `${location}` of `Sarjapur, 110045`. Both are entries in the prompt's own
Canonical Location Spellings list, which sits directly beneath the conversion step. So the model is
not picking a place at random — it is picking one off the list. The instruction *"use Canonical
Location Spellings for a place on that list; a place NOT on the list is converted the same way"*
makes list-membership the salient operation, and the off-list clause reads as "find the nearest
listed place".

**What was added** (slim only, 70,668 chars):

> **THE CANONICAL LIST IS A SPELLING TABLE, NEVER A MENU.** You consult it to learn how a name you
> ALREADY HAVE is written — you never pick a place out of it. … **If the place you are about to say
> is a list entry and the words in `${location}` are not, you have taken a name off the menu and
> must stop.**

The last sentence is the part that matters: it is a check the model can run against the turn it is
composing, which is the property the rules in these prompts that actually hold all share. "Say the
value you were given" is not checkable in that way — it requires comparing against something the
model believes it already did.

**Deliberately slim-only.** The fat prompts keep the failing wording, so the next A/B round measures
this change and nothing else.

**Result: 0 of 3. Reverted.** All three dials still said साहिबाबाद. The reason is that the diagnosis
was wrong: **साहिबाबाद is not only a Canonical-list entry, it is the tester profile's stored city**
(`get_profile` returns `location: "Sahibabad, Ghaziabad, India"` for the tester DID), and गाज़ियाबाद
on `1450f797` is the city half of the same string. The model was not picking a name off a list — it
was preferring the fetched profile over `${location}`, which is the mechanism already documented and
already guarded. I read the list coincidence and missed the profile one.

The rule was removed rather than left in place (slim back to 69,974 chars). A prompt carrying a
plausible rule aimed at the wrong mechanism is worse than one carrying nothing, because the next
reader takes that mechanism as ruled out.

**And the failure it was chasing is not a production rate.** Split by caller over 449 calls: real
callers 3 RAW and **0 SUBSTITUTED**; harness dials 10 SUBSTITUTED and 0 RAW. Every substitution is a
harness dial, manufactured by a fixture that deliberately disagrees with the tester's stored profile.
The precedence weakness is real and reproducible; the caller-facing rate I quoted was my own test
setup.

### Experiment 2 on the slim bot: remove the counter instead of restating the rule

The ordinal running count fails on **14 of 24** multi-batch calls (58%). The rule is unambiguous —
*"Ordinals run continuously across batches and NEVER restart"* — so this is not a clarity problem.
It asks the model to carry a counter across an unbounded number of turns and to know, at the moment
it composes a batch, how many jobs it has read out several turns earlier. That is the one property
every rule in these prompts that reliably holds does **not** require: the apply-success positional
rule asks "is there a fresh result in this turn?", the Turn-B landmark check asks "is this text in
the context block?". Both are answerable from what is in front of the model. A running count is not.

**What was changed (slim only, 72,069 chars).** The first batch keeps पहला / दूसरा / तीसरा, because
the caller needs some way to pick one of three. **From the second batch on there is no numbering at
all** — the jobs are introduced as more jobs and chosen by name:

> "इनके अलावा ये जॉब्स भी हैं — [role], [company], [location]। और: [role], [company], [location]।
> किसी के बारे में और जानना चाहेंगे?"

Both चौथा-and-upward and restarting at पहला are forbidden, for the same stated reason: each requires
the count. With no numbering after the first batch there is no count to keep and nothing to get
wrong. Selection by role and company is already covered by the phonetic-confirmation rules, and if a
caller does say a number after the first batch the prompt now tells the bot to ask which one by
naming two rather than guessing.

**Why slim only.** This changes what the caller hears, so it is not something to ship to production
bots unattended — it is precisely the decision the EOD note flags as the owner's. The fat prompts
keep the counter, so the next A/B round measures this change and nothing else.

**Result: it works.** `43e7e5e4` (`morejobs-22.json`, 22 jobs, `hi-asks-for-all-jobs`, 197 s):

> आपके लिए जॉब्स हैं — **पहला**: बिलिंग इंजीनियर … **दूसरा**: टेली मार्केटिंग … **तीसरा**: …
> **इनके अलावा ये जॉब्स भी हैं** — कमर्शियल मैनेजर, ग्रे फैशन … **और**: फील्ड सेल्सपर्सन …
> **इनके अलावा ये जॉब्स भी हैं** — क्रू मेंबर, मैकडॉनल्ड्स … **और**: सेल्स रिप्रेज़ेंटेटिव …
> **इनके अलावा ये जॉब्स भी हैं** — कस्टमर सपोर्ट एग्जीक्यूटिव, सी वाई फ्यूचर …

**Ordinal sequence spoken across the whole call: पहला दूसरा तीसरा. Four further batches, zero
numbering, zero restarts.** The same bot on `4d6d4d02`, before this change, ran पहला दूसरा तीसरा
**four times over**.

One apparent defect on that call is not one: it named "क्रू मेंबर - मैकडॉनल्ड्स, मैकडॉनल्ड्स" twice.
The payload contains **four distinct McDonald's crew-member postings** with four different
`job_id`s (and two CY FUTURE ones); all 22 ids are unique. The bot was walking the array faithfully
— the same payload-duplication case `jobs_presented` was taught to downgrade to info rather than
report as repetition.

**So the recommendation to the owner is now evidenced rather than theoretical:** dropping the
cross-turn counter fixes a 58% failure with no loss of selectability, because the caller picks by
name from the second batch on and the confirmation rules already cover that. It is ready to port to
the four KKB/Maya Signals prompts on your word.

## Running the comparison

```
python3 raya/slim/compare_spec.py "KKB/KKB Placeholder Hindi Signals.md" \
    "KKB-Slim/KKB Slim Hindi Signals.md"

python3 raya/slim/ab_compare.py --selftest
python3 raya/slim/ab_compare.py --pairs 3 \
    --fixture raya/testcases/args/r5/sarjapur-offlist.json \
    --persona raya/personas/hi-detail-then-apply.md
python3 raya/slim/ab_compare.py --score-only
```

`ab_compare.py` alternates fat and slim so line conditions hit both sides, and prints
`FEWER THAN 2 CALLS ON A SIDE — this is not yet a comparison, it is an anecdote` rather than
reporting a median off one call. Its scorer self-tests against four hand-built transcripts,
including the real `7b841e6b` leak.

## Latency baseline, from real traffic

Scored over the fat bot's 7 most recent calls with a measurable turn count: **median 13.4 seconds
per agent turn** (turn counts 12, 2, 3, 2, 5, 13, 4). That is the number the slim bot has to beat.
Same scorer, same fixture, same persona, so the comparison is like-for-like.

## Contract coverage of the slim prompt

`compare_spec.py` reports 181 of the fat prompt's 306 distinct spoken lines kept, 7 drifted and 118
dropped. Every one of the 118 was classified by hand; none is a live agent line. They are:

- **lines the fat prompt quotes in order to FORBID them** — "क्या मैं आपकी प्रोफाइल fetch कर सकती हूँ",
  "आपकी जानकारी देख रही हूँ", "ठीक है, आपकी तरफ़ से अप्लाई कर देती हूँ", "मैंने report कर दिया है", and
  the deleted "आपके लिए relevant jobs अभी नहीं दिख रहीं…". The slim prompt bans these as classes and
  keeps verbatim only the ones whose exact wording is the failure.
- **quotes of past bugs** — "आप अभी बी०टेक०(ई०सी०एस) का काम कर रहे हैं", "अभी बेंगलुरु के लिए … उपलब्ध
  नहीं हैं", "मुराद नगर, ११००४५ है". Those live in `CHANGELOG.md` and `bug-patterns.md`.
- **caller utterances** from sample dialogues — "और कोई जॉब है क्या", "हाँ अप्लाई कर दो".
- **TTS and canonical-spelling table cells** the extractor reads as speech — "₹५००/day", "सेक्टर पाँच".
- **Kannada lines** cited from the twin's bugs.

Two real drops were found by grep after the spec diff and restored: **"पक्का call आएगा"** and
**"selection हो जाएगा"**, both named bans. Naming the exact wrong string is what makes a ban stick,
so they are quoted rather than paraphrased.

The extractor had a bug worth knowing about: it originally paired quotes across the whole file, so
one stray unmatched quote shifted every pairing after it and **three spoken lines that were present
in the slim prompt were reported as dropped**. It now scans per block (a run of `> ` lines, or a
single line), so a stray quote can only corrupt its own block.

## Known open item in both prompts

The location sentence's caller-place slot is **not prose-fixable** and the slim prompt carries the
same conflict as the fat one, deliberately, so the A/B measures size rather than a behaviour change.
Three wordings have failed: `a899617e` spoke the PIN as a quantity, `7b841e6b` and `a5ba6894` read
the raw Latin value, and `1450f797` substituted the jobs' city for the caller's place. See
`KKB/CHANGELOG.md` (2026-09-08, later entry) and `ESCALATION-data-team.md` §5.
