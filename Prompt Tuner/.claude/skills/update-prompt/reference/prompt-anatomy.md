# Conversation Prompt Anatomy

The section taxonomy for conversation prompts, with every section tagged so a change can be
classified and mirrored correctly. Shared by `/update-prompt`, `/port-feature` and `/sync-check`.
Built from the Blue Dots prompts (KKB, DKB, Maya, TRRAIN, KKB-Slim); a new project's prompt maps
onto it by intent, and anything that does not fit is tagged with the test below.

## Tags

- **AGNOSTIC:** copied byte-identical across languages. Logic, structure, variable names, tool rules.
- **SPECIFIC:** re-authored per language. Spoken text, scripts, examples, number-words.
- **MIXED:** both. The rules are AGNOSTIC; the spoken lines and examples inside are SPECIFIC.

## How to classify any edit

Ask: *"If this exact text appeared in the other language's file unchanged, would it be correct?"*
- Yes → AGNOSTIC (copy verbatim).
- No, it must be in the other script or idiom → SPECIFIC (re-author).
- Partly → MIXED (copy the rule, re-author the quoted speech).

Reliable tells: text inside spoken-line quotes, TTS number spellings, script names, tone markers
and sample dialogue are SPECIFIC. Conditions ("if X is Not Available…"), variable names
(`${job_id}`), tool payloads, step order and safety checklists are AGNOSTIC.

**One trap:** an English rule line that names a language ("speak Hindi/Hinglish", "Devanagari
only") looks AGNOSTIC but is not: copied unchanged it tells the mirror to speak the master's
language (analyser D117). Rewrite it for each mirror; `scripts/language_checks.py` fails the file
if one survives.

## Section taxonomy (shared sections)

Headings differ per bot; match by intent, not exact string.

| Section | Tag | Notes |
|---|---|---|
| Introduction | MIXED | Persona name (काम की बात / ಕೆಲಸದ ಮಾತು / धंधे की बात) SPECIFIC; core principles AGNOSTIC. |
| Core Role | AGNOSTIC | |
| Input Variables (+ Recommendations/Job variables) | AGNOSTIC | Never localize `${...}` names. |
| Contact context (memory block) | AGNOSTIC | The three-line block, verbatim in every language (root `CLAUDE.md` → "Memory injection block"). |
| Hallucination Guard / Never Speak Tool Payloads | AGNOSTIC | |
| No-Match Fallback | MIXED | Trigger logic AGNOSTIC; the spoken fallback SPECIFIC. |
| User Universe / personas | AGNOSTIC | |
| Conversation Principle | AGNOSTIC | |
| Audio check / Call Introduction Rules / Priority / Decision | MIXED | Decision logic AGNOSTIC; opening scripts SPECIFIC. |
| Profile Handling / fetch the profile | AGNOSTIC | |
| Job Presentation Flow | MIXED | Step rules AGNOSTIC; "Spoken format" blocks SPECIFIC. |
| Language and Script Rules | SPECIFIC | Defines the script itself; any English line naming the language is rewritten per mirror (D117). |
| TTS Normalization Rules | SPECIFIC | Spellings differ by language; the categories are AGNOSTIC. |
| Speech Recognition & Phonetic Confirmation | MIXED | Core rule AGNOSTIC; number variants and confirmation examples SPECIFIC. |
| Style Rules | MIXED | Principle AGNOSTIC; example markers (अभी / ಈಗ) SPECIFIC. |
| Prohibited Language | MIXED | Rule AGNOSTIC; banned phrases SPECIFIC (culturally adapted). |
| Conversation State Model / What You Must Always Preserve / Trade-off Rule | AGNOSTIC | |
| Action and Consent Rule | AGNOSTIC | |
| Tool Call Rules (per tool) + payloads | AGNOSTIC | Tool names, JSON payloads and fixed params NEVER change. |
| Apply Success / Failure Handling, Post-Application | MIXED | Logic AGNOSTIC; spoken messages SPECIFIC. |
| Need Capture / Services offer | MIXED | Offer logic AGNOSTIC; offer lines SPECIFIC. |
| Silence Handling | AGNOSTIC | Any spoken bridge line inside is SPECIFIC. |
| Emotional Handling | MIXED | Phrase lists SPECIFIC; the rule AGNOSTIC. |
| Safety interrupt (public-facing bots, D121) | MIXED | Trigger and priority AGNOSTIC; the spoken safety lines SPECIFIC and reviewed first by the native speaker. |
| Special Journey Patterns | MIXED | Pattern logic AGNOSTIC; example lines SPECIFIC. |
| Tool Call General Instructions | AGNOSTIC | |
| Graceful Exit | MIXED | Close logic AGNOSTIC; final words SPECIFIC. |
| Dignity Safety Check | AGNOSTIC | |
| Sample Conversational Patterns / worked calls | SPECIFIC | Whole dialogues; localize place and person names (Pune↔Bengaluru, रमेश↔ರಮೇಶ್). Examples are a defect source: a worked example that shows forbidden behaviour beats the rule (D50). |

### DKB-only sections

| Section | Tag | Notes |
|---|---|---|
| Signals Backend: What Changed (Signals prompts only) | AGNOSTIC | Tool contract and the list of stored fields. |
| Introduction After "Hello", Turns 0-3 | MIXED | Turn logic AGNOSTIC; spoken turn lines SPECIFIC. |
| Phase Entry Rule | AGNOSTIC | `${job_role}` presence routing. |
| Conversation Flow, Phases 1-3 | MIXED | Phase logic AGNOSTIC; spoken examples SPECIFIC. |
| Tool Usage Rules | AGNOSTIC | Legacy: `get_talent_insights`, `update_job_status`, `update_job_details`, `create_job` with ONEST fixed params. Signals: `create_job`, `update_job`, no fixed params. |
| Market Truth Delivery (legacy only) | MIXED | |
| Error and Uncertainty Handling | MIXED | |

### Maya-only sections (never overwritten by a KKB sync)

| Section | Tag | Notes |
|---|---|---|
| Caller Identity (Strict) | MIXED | Campus identity logic; spoken intro SPECIFIC (Hindi only). |
| HR-number value line / HR number sharing (post-apply) | MIXED | |
| Experience Capture | MIXED | |
| Voice gender (always feminine) | SPECIFIC | Hindi feminine verb forms (कर रही हूँ, not कर रहा हूँ). |

The MPL Competition section was removed from every Maya prompt on 2026-10-12 (`Maya/CHANGELOG.md`).

### TRRAIN and KKB-Slim

- **TRRAIN** uses the shared sections plus "What This Call Must Never Become", Turns 1-3 (audio
  check, introduction, the single offer) and "Reading the answer": offer logic AGNOSTIC, offer lines
  SPECIFIC. Its only tool section is `get_profile`.
- **KKB-Slim** is a ground-up rewrite with its own skeleton ("Six hard laws", "The call, in order"
  steps 0-14 and S, "Tools", "Speaking", "Hearing", "Situations", "Four worked calls"). Map by
  intent: laws, steps and Tools are AGNOSTIC except their quoted lines; Speaking is SPECIFIC;
  worked calls are SPECIFIC. It is not a mirror of the KKB Signals prompts.

## Localizing a SPECIFIC change (master → each mirror)

Instructions stay English in every file; only what the bot speaks is localized. For any language,
re-author to the `/translate-prompt` standard: the everyday words in
`raya/translations/lexicon.json` (never the bookish word), that language's gender and question
rules, numbers and times as words, place and person names pinned once, and the phrasing the mirror's
existing section already uses. Never translate word for word, and never leave master-language
text in a same-script mirror (D118).

**Kannada, as used in the Blue Dots mirrors:**
- Kannada script only, no Roman Kannada; English-origin words in Kannada script (ಜಾಬ್, ಮಾರ್ಕೆಟ್).
- "Kanglish" register: Kannada mixed naturally with common English words.
- Numbers, money, time as Kannada words (ಎರಡರಿಂದ ಮೂರು; ಹದಿನೆಂಟು ಸಾವಿರ; ಬೆಳಗ್ಗೆ/ಮಧ್ಯಾಹ್ನ/ಸಂಜೆ/ರಾತ್ರಿ, never AM/PM).
- Tone markers ಈಗ / ಸುಮಾರು / ಸಾಮಾನ್ಯವಾಗಿ rather than अभी / लगभग / आमतौर पर.
- Kannada-region places already used in the file (Bengaluru, Mysuru, Dharwad).
