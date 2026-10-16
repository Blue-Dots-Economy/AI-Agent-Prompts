# Purple Dots — Inclusive Voice Bot (Disability & Needs) — Prompt Gap Analysis

**Scope:** Pre-flight review of the current system prompt. Flags only — no changes made.
**Method:** Each reported symptom is traced to the exact section that produces it, then the
prompt is swept for related latent gaps. Findings draw on failure patterns observed across
similar low-literacy, multilingual outbound voice agents.

**Key principle behind most findings:** a rule being *present* in the prompt does not mean it
*holds* at runtime. A competing instruction, a few-shot example, or aggressive skip-logic can
quietly override it. Most fixes below are about closing that gap — adding a hard gate, an
explicit bound, or a concrete list — rather than restating an instruction.

---

## Priority summary

| # | Finding | Severity |
|---|---|---|
| 1 | Solution-Enablers step (Phase 3 · Step 2) intermittently skipped | High |
| 2 | Share-with-provider consent asked repeatedly | High |
| 3 | Outbound bot invites callbacks ("you can call me") | Medium |
| 4 | Hard/Sanskritised Hindi despite "simple language" rule | Medium |
| 5 | `get_profile` and Phase 4–5–6 tool calls missed | High |
| 6 | `get_providers_for_location`: lat/lng mapping swapped | High (data bug) |
| 7 | Hardcoded provider `item_id` contradicts dynamic search | High |
| 8 | `solution_enablers` sheet referenced but not declared as a tool | High |
| 9 | Feminine-voice inconsistency (masculine verb form offered) | Medium |
| 10 | Few-shot examples contradict rules / one greeting garbled | Medium |
| 11 | Cross-call memory block — confirm intent | Verify |

---

## Part A — Reported issues (root-caused)

### 1. Flow sometimes skips Solution Enablers (Phase 3 · Step 2) — **High**

The rule is strongly worded ("**Do not skip Step 2 even if the user already knows**"), so the
miss comes from three structural pulls, not a weak instruction:

- **The examples contradict the rule.** Example 1 goes option (परचून की दुकान) → *Phase 2
  challenge probing* → straight to "connect provider" and **never runs the explicit enabler
  inform-and-ask**. Only Example 4 (व्हील चेयर → डिसेबिलिटी कार्ड) models Step 2. Models mimic
  concrete examples over prose, so Example 1 teaches the shortcut.
- **Phase 2 (challenges) and Phase 3 · Step 2 (missing enablers) overlap.** Both capture "what
  the user lacks / barriers." Once a barrier is noted in Phase 2, `[NO-REPEAT]`/`[SKIP-AHEAD]`
  mark Step 2 as already-satisfied.
- **`solution_enablers tool sheet` is referenced but never declared.** The "Source of truth"
  section only wires `Disabilitytypes` and `AssistiveAids`. Step 2 depends on a sheet the model
  can't ground → it skips. *(This also leaves `looking_for` under-populated, since enabler
  categories feed it.)*

**Recommendation:** add a hard negative gate ("Phase 4 may **not** begin until Step 2 has run
for every option"); sharpen the Phase 2 vs Step 2 distinction; fix Example 1 to model Step 2;
declare the enabler sheet as a real tool.

### 2. Share-with-provider consent asked repeatedly (Phase 6) — **High**

`connect_provider` says "**Execute this tool call once for each provider discovered**", and
search can return many providers (`get_providers_for_location` ≤20 + `match_providers_for_text`
≤20). The consent gate is glued to the per-provider tool call ("*Only upon receiving consent,
trigger connect_provider*"), so the bot re-asks consent per provider — a one-time human-facing
ask trapped inside a per-record backend loop.

**Recommendation:** state explicitly "**ask sharing-consent exactly once** for all providers; on
a single 'yes', loop `connect_provider` **silently** per provider." Also resolve the Step-3
hardcoded `item_id` vs the dynamic search (finding 7) — it muddies how many providers exist and
therefore how many asks.

### 3. Outbound bot says "you can call me" at the end — **Medium**

Modality is declared once ("**You are an outbound voice caller… Users do not call you**"), but
there is **no closing script and no prohibition** on inbound-framed language. Phase 6 ends with
a bare "Close the call", so the model falls back to trained call-center endings that include
"call us back."

**Recommendation:** add a **Graceful Exit** section with a fixed closing script — the correct
frame is already implied ("the support center will contact you") — plus an explicit ban on
"आप मुझे कॉल कर सकते हैं / फिर कॉल कीजिए"-type phrasing.

### 4. Hard / Sanskritised Hindi (सेवा प्रदाता, प्रशिक्षण, पुनर्वास…) — **Medium**

The "use simple Hindi, no technical terms" rule is stated ~4×, but there is **no concrete
banned→preferred lexicon**. The "Prohibited Language (Strict)" list only covers
promotional/emotional phrases, not administrative/tatsama vocabulary. Abstract instructions
underperform explicit substitution lists over a low-literacy voice channel.

**Recommendation:** add a do/don't table — e.g. सेवा प्रदाता → *सपोर्ट सेंटर / मदद करने वाली
संस्था*; प्रशिक्षण → *ट्रेनिंग*; पुनर्वास → *ठीक होने में मदद*; मूल्यांकन → *जाँच* — with the rule
"prefer the common English/Hinglish loanword over the pure-Hindi equivalent." The prompt already
uses the right gloss pattern ("विकलांगता यानि डिसेबिलिटी"); make that the standard.

### 5. Misses `get_profile` / Phase 4–5–6 tool calls — **High**

Two distinct causes:

- **`get_profile`:** the gating logic is correct, but Examples 2 & 4 don't model the
  fetch-and-verify path (Ex 2 asks the name cold; its greeting is also garbled — see finding
  10), so the examples teach that `get_profile` is optional. Heavy prompts shedding tool steps
  is a known failure mode, and this prompt is very heavy.
- **Phases 4–5–6 are entirely silent background calls** with no conversational anchor and **no
  "do not close the call before X has run" gate.** `update_profile` being missed cascades —
  Phase 5 is gated on it, so Phase 6 never runs. The aggressive
  `[SKIP-AHEAD]`/`[ORDER-FLEX]`/"move silently to the next phase" logic has strong skip-forward
  pressure but no backpressure requiring the terminal tool sequence.

**Recommendation:** add explicit "**MUST call `<tool>` before proceeding**" gates on Phases
4–5–6 and a hard "**never end/close the call before `connect_provider` (or the decline path) has
run**" gate; mark the background calls as mandatory-but-silent; align/repair the example
greetings.

---

## Part B — Additional gaps found in review

### 6. `get_providers_for_location`: lat/lng swapped — **High (data bug)**

The mapping reads `searchlng ← item_locations.lat` and `searchlat ← item_locations.lng` — the
two are swapped. GeoJSON coordinates are `[longitude, latitude]`, so this will search the wrong
point (or a mirrored one) and return wrong/empty providers.
**Recommendation:** `searchlng ← lng`, `searchlat ← lat`, coordinates `[lng, lat]`.

### 7. Hardcoded provider `item_id` contradicts dynamic search — **High**

Phase 5 · Step 3 pins a fixed provider (`item_id: 3947037c-…`) while Steps 1–2 search
dynamically. It's unclear which provider `connect_provider` actually targets
(`target_item.item_id` says "extract from outcome of Match Provider phase").
**Recommendation:** reconcile — decide whether the flow is dynamic-search or fixed-provider, and
remove the contradiction.

### 8. `solution_enablers` sheet referenced but not declared — **High**

See finding 1. It is used in Phase 3 · Step 2 but not declared in "Source of truth" alongside
`Disabilitytypes` and `AssistiveAids`. An ungrounded reference is skipped.

### 9. Feminine-voice inconsistency — **Medium**

Persona is "You are female", but §7 offers "समझ रहा हूँ/**रही हूँ**" (masculine option), and
there is no explicit feminine-only rule. Voice-gender drift over a spoken channel is jarring.
**Recommendation:** add a "use feminine verb forms only" rule; remove the masculine option.

### 10. Few-shot examples contradict rules / greeting garbled — **Medium**

Examples are behaviour references and are mimicked over prose. Issues: Example 1 skips the
mandatory Solution-Enablers step (finding 1); Example 2's greeting is grammatically broken
("मै आपकी मदद के आपकी विकलांगता यानि की डिसेबिलिट लिए…") and skips the profile fetch; example
greetings drift from the canonical PRE-ROUTING greeting.
**Recommendation:** repair examples to model the mandatory path and match the canonical greeting
verbatim.

---

## Part C — Verify (confirm before acting)

- **11. Cross-call memory:** the bot uses `get_profile` (live profile fetch) but has no
  cross-call memory block. Confirm whether this agent is meant to carry memory across calls; if
  yes, a memory-injection block / memory prompt is missing.
- **`{${contact_phone}}` double-brace:** confirm the outer braces are intended (plain variable
  references are usually `${...}`).

---

## Quick wins (lowest effort, high impact)
1. Fix the lat/lng swap (finding 6) — one-line data correction.
2. Declare the `solution_enablers` sheet as a tool (finding 8).
3. Add the "ask share-consent once, then loop silently" bound (finding 2).
4. Add the closing script + callback ban (finding 3).
5. Remove the masculine verb option in §7 (finding 9).
