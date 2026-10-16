#!/usr/bin/env python3
"""fix_presence.py — assert that every fix we have shipped is still present on EVERY bot that needs it.

The failure this closes has happened three times. A fix is worked out on one bot, mirrored by hand,
and lands on some of its twins:

  * 2026-09-03  `duplicate_check` was a required `apply_job` param on 1 of 12 bots; the prompt text
                was mirrored everywhere, so nothing looked wrong.
  * 2026-09-03  the ACTION_LIMIT_REACHED mapping in the tool description: 1 of 6 Signals bots.
  * 2026-09-04  the TRRAIN-naming policy landed in Hindi and never reached Kannada — 7 references
                against 0 — while heading counts matched 54/54, so the sync check saw an aligned pair.

`static_regression.py` checks contracts and structure; `toolschema_parity.py` checks tool schemas;
`sync_check` compares a language pair's skeleton. None of them knows what we FIXED. This does: one
row per shipped fix, naming the token that proves it and the bots that must carry it. A fix that gets
reverted, reworded away, or missed on a mirror shows up here as a hard failure the next time anything
runs.

Adding a row is part of shipping a fix. If a fix cannot be reduced to a token, say so in `note` and
give the closest proxy — a weak check that runs beats a strong one that does not exist.

Usage: python3 raya/regression/fix_presence.py [--verbose]
Exit 1 if any required fix is missing from any bot that should carry it.
"""
import argparse, glob, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

KKB_CONV = sorted(f for f in glob.glob(os.path.join(REPO, "KKB", "*.md")) if "CHANGELOG" not in f)
MAYA_CONV = sorted(f for f in glob.glob(os.path.join(REPO, "Maya", "*.md"))
                   if "CHANGELOG" not in f and "Memory" not in f and "Output" not in f)
TRRAIN_CONV = [os.path.join(REPO, "TRRAIN", "TRRAIN Hindi.md"), os.path.join(REPO, "TRRAIN", "TRRAIN Kannada.md")]
DKB_SIGNALS = [os.path.join(REPO, "DKB", "DKB Hindi Signals.md"), os.path.join(REPO, "DKB", "DKB Kannada Signals.md")]
DKB_ALL_CONV = [os.path.join(REPO, "DKB", n) for n in
                ("DKB Hindi Signals.md", "DKB Kannada Signals.md", "DKB Hindi.md",
                 "DKB Kannada.md", "DKB Inbound Hindi.md", "DKB Inbound Kannada.md")]


def all_conv():
    """EVERY conversation prompt in the repo, all four bots plus the slim A/B rewrite. For rules
    that are fleet-wide by nature -- a marker spoken aloud is wrong on any bot in any language."""
    out = []
    for f in (KKB_CONV + MAYA_CONV + DKB_ALL_CONV + TRRAIN_CONV
              + sorted(glob.glob(os.path.join(REPO, "KKB-Slim", "*.md")))):
        b = os.path.basename(f)
        if "CHANGELOG" in b or "Memory" in b or "Output" in b:
            continue
        if f not in out:
            out.append(f)
    return out


def seeker_conv():
    """KKB + Maya conversation prompts (memory/output excluded — they carry no spoken flow)."""
    return [f for f in KKB_CONV if "Memory" not in f and "Output" not in f] + MAYA_CONV


def inbound_conv():
    return [f for f in seeker_conv() if "Inbound" in os.path.basename(f)]


def outbound_conv():
    return [f for f in seeker_conv() if "Inbound" not in os.path.basename(f)]


# (id, description, files, must_contain, must_NOT_contain)
FIXES = [
    ("memory-injection", "the verbatim contact_memory injection block",
     seeker_conv(), ["{${contact_memory}}"], []),

    ("no-jobrec-alias", "the job_recommendations ALIAS is gone — the empty-jobs test named a variable "
                        "that does not exist, so it read as empty on every call (D66, call 8d3453b1)",
     seeker_conv(), [], ["job_recommendations"]),

    ("apply-bridge-dropped", "no licensed spoken line asserts the apply before the tool result (D65) — "
                             "the bridge line was what the model said INSTEAD of calling apply_job",
     seeker_conv(), ["are now FORBIDDEN in this position"],
     ["Allowed examples:\n- \"ठीक है, आपकी तरफ़ से अप्लाई कर देती हूँ.\"",
      "Allowed examples:\n- \"ಸರಿ, ನಿಮ್ಮ ಪರವಾಗಿ ಅಪ್ಲೈ ಮಾಡ್ತೇನೆ.\""]),

    ("row1-evidence-gate", "the already-applied line requires evidence you can point at (c5a10922)",
     seeker_conv(), ["REQUIRES EVIDENCE YOU CAN POINT AT"], []),

    ("failure-offers-another-job", "an apply that did not go through never ends the job conversation",
     outbound_conv(), ["ENDS ON THE OFFER OF ANOTHER JOB", "ENDS ON THE NEED CAPTURE QUESTION"], []),

    ("no-spoken-job-count", "the caller is never told how many jobs we hold",
     seeker_conv(), ["NEVER say how many jobs you have"], []),

    ("inbound-confirm-first", "a held location is CONFIRMED, never re-asked (D61, bbdb6eaf)",
     inbound_conv(), ["CONFIRM it, never ask openly"], []),

    ("inbound-caseB-location", "Case B has its own copy of the location check — the rule living in "
                               "Case A never reached a profile whose role is the placeholder 'Any' (D63, 7a98b7a0)",
     inbound_conv(), ["This branch is why Case B needs its own copy of the check"], []),

    ("no-postal-address-aloud", "only the town/city part of a stored location is spoken (b48f70fb)",
     inbound_conv(), ["never read a full postal address aloud"], []),

    ("maya-confirm-in-closed-set", "the confirm line is inside the location closed set (D64, 0baf8765)",
     MAYA_CONV, ["The confirm line is inside this closed set."], []),

    # Scoped to DKB_SIGNALS when first written, which is exactly why it passed while the LEGACY pair
    # still SCRIPTED the government line — live call 4b2d7dca on 2026-09-04 opened with "मैं गवर्नमेंट
    # एम्प्लॉयमेंट प्रोग्राम की तरफ से". A row that checks only the bots you happened to fix is not a
    # guard. Now every DKB conversation prompt, and the forbidden wording must be gone from the
    # SPOKEN lines (the rule itself quotes it, so the must-not list cannot be used here).
    ("dkb-not-government", "DKB is the city administration's initiative, never a government programme "
                           "— all SIX conversation prompts, not just the Signals pair (4b2d7dca)",
     DKB_ALL_CONV, ["never claim to be the government"], []),

    ("dkb-expiry-needs-a-role", "the expiry opener requires a real job_role (e2ce642a, 0eb3fc72)",
     DKB_SIGNALS, ["THE NEW-VACANCY OPENING IS THE DEFAULT"], []),

    ("trrain-names-the-partner", "TRRAIN Trust is introduced by name in BOTH languages — it landed in "
                                 "Hindi on 2026-08-12 and never reached Kannada until 2026-09-04",
     TRRAIN_CONV, ["TRRAIN Trust is the ONLY partner you may name"],
     ["Never name TRRAIN or any other partner organisation aloud"]),

    ("maya-college-two-openers", "the opener is TWO lines chosen by looking at the value, not one "
                                 "template with ${college_name} inside it (harness call 718aa8ab read "
                                 "the raw token aloud despite three rules forbidding it)",
     [f for f in MAYA_CONV if "Inbound" not in os.path.basename(f)],
     ["AN UNSUBSTITUTED TOKEN COUNTS AS EMPTY"], []),

    ("token-counts-as-empty", "every prompt with a ${token} inside a QUOTED SPOKEN line says that an "
                              "unsubstituted token counts as EMPTY — the platform drops empty args, so "
                              "an unsupplied field arrives as the raw token and is read aloud (D67, 718aa8ab)",
     [os.path.join(REPO, "KKB", "KKB Placeholder Hindi Signals.md"),
      os.path.join(REPO, "KKB", "KKB Placeholder Kannada Signals.md"),
      os.path.join(REPO, "TRRAIN", "TRRAIN Hindi.md"),
      os.path.join(REPO, "TRRAIN", "TRRAIN Kannada.md")] + DKB_SIGNALS
     + [f for f in MAYA_CONV if "Inbound" not in os.path.basename(f)],
     ["UNSUBSTITUTED TOKEN COUNTS AS EMPTY"], []),

    ("no-item-state-in-dhiway", "the Dhiway prompts must never mention item_state — it is a Signals-only "
                                "contract token and leaked twice",
     [f for f in seeker_conv() if "Signals" not in os.path.basename(f)], [], ["item_state"]),

    # ---- 2026-09-08, the written-value-spoken-verbatim family (D71-D74) ----

    ("offlist-value-still-converted", "a name that is on NO list in the prompt is converted exactly "
                                      "like one that is — the off-list branch of every script rule "
                                      "(D71; 7b841e6b said 'Sarjapur, 110045', b6353cfb said 'VMLG College')",
     seeker_conv(), ["not an exemption"], []),

    ("location-converted-before-spoken", "`${location}` is reduced to place words and written in the "
                                         "target script BEFORE the sentence is said — and the old "
                                         "'say the sentence as it arrives' permission is gone (D71)",
     [os.path.join(REPO, "KKB", "KKB Placeholder Hindi Signals.md"),
      os.path.join(REPO, "KKB", "KKB Placeholder Kannada Signals.md")],
     ["a written value is not sayable"],
     ["**Say the sentence as it arrives — but speak only the PLACE WORDS in it.**"]),

    ("no-latin-field-label-spoken", "no English field label is left inside a Hindi spoken template or "
                                    "sample — the Kannada twins already transliterated it (D72, 9d5e9848)",
     [f for f in seeker_conv() if "Kannada" not in os.path.basename(f)], [], ["Qualification: "]),

    ("dkb-absent-company-name", "the company-name emptiness test covers the ABSENT argument, not just "
                                "the string 'Not Available' and NULL — 7 live calls greeted owners as "
                                "'Not Available' because the arg was never sent (D73, 564e1d45, be4ab8c3)",
     DKB_SIGNALS + [os.path.join(REPO, "DKB", "DKB Hindi.md"),
                    os.path.join(REPO, "DKB", "DKB Kannada.md")],
     ["AN UNSUBSTITUTED TOKEN COUNTS AS ABSENT"], []),

    ("no-token-in-sample-speech", "no sample conversation shows the agent speaking a raw ${token} — the "
                                  "samples outvoted four rules and taught the pass-through (D74, b6353cfb)",
     MAYA_CONV, [], ["> **Agent:** नमस्ते। मैं माया, ${college_name} की ओर से"]),

    ("qualification-not-an-occupation", "an education qualification in the profile `role` field is NOT a "
                                        "usable role — QA heard 'आप अभी बी०टेक०(ई०सी०एस) का काम कर रहे हैं' "
                                        "(D64/D71, QA call 5035574; reproducing call id still pending)",
     seeker_conv(), ["never what they DO"], []),

    ("disclosure-checked-on-the-turn", "the data-sharing disclosure is checked against the turn "
                                       "being composed, and the caller's own apply request is named "
                                       "as NOT being the disclosure — 18 of 105 apply_job calls had "
                                       "no disclosure before them, all on inbound bots or Maya "
                                       "(73764d9d)",
     [f for f in seeker_conv() if "Placeholder Hindi.md" not in os.path.basename(f)
      and "Placeholder Kannada.md" not in os.path.basename(f)],
     ["CHECK IT ON THE TURN YOU ARE COMPOSING"], []),

    ("apply-failure-row-excludes-duplicate", "the single failure row explicitly EXCLUDES "
                                             "ACTION_LIMIT_REACHED and the duplicate case -- when "
                                             "the merged row said \"any error\" it swallowed the "
                                             "case Row 1 owns, and 6caf1fbe told a caller who "
                                             "really did already have the application that the "
                                             "apply had not gone through",
     [f for f in all_conv() if os.path.basename(f).startswith(("KKB Placeholder", "Maya", "KKB Slim"))
      and "Memory" not in f and "Output" not in f],
     ["Those go to Row 1 and this row does NOT apply"],
     []),

    ("apply-failure-single-row", "there is exactly ONE apply-failure line and it claims no cause -- "
                                 "with two rows available the bot spoke both back to back "
                                 "(b4e34994) and welded them into one sentence (41a2c19d), and the "
                                 "cause-claiming half was false on policy blocks and on 45 of 60 "
                                 "ACTION_LIMIT_REACHED calls",
     [f for f in all_conv() if os.path.basename(f).startswith(("KKB Placeholder", "Maya", "KKB Slim"))
      and "Memory" not in f and "Output" not in f],
     ["do NOT re-add a second"],
     ["technical issue"]),

    ("location-token-outside-sentence", "the location sentence takes a DERIVED slot, with the "
                                        "${location} token on its own line above -- with the token "
                                        "inside the sentence the bot read \"Sarjapur, 110045\" out "
                                        "verbatim (a9039634), and the paragraph claiming there was "
                                        "\"no resolution step\" contradicted the conversion rule",
     ["KKB/KKB Placeholder Hindi Signals.md", "KKB/KKB Placeholder Kannada Signals.md"],
     ["location_written is:"],
     ["there is no resolution step, no comparison"]),

    ("pincode-never-spoken", "no prompt explains HOW to pronounce a PIN code -- the instruction "
                             "\"say it digit by digit\" sat three paragraphs from \"drop every "
                             "digit\" and was taken as permission (1c6963bb spoke it in Devanagari "
                             "numerals)",
     [f for f in all_conv() if "Memory" not in f and "Output" not in f],
     [],
     ["digit by digit in words** exactly like a phone number", "is an identifier, not a number"]),

    ("dkb-argument-beats-memory", "the DKB posting template says the ARGUMENT wins over remembered "
                                  "values -- 965f9d06 had salary=30000 and spoke a figure carried "
                                  "over from an earlier call; DKB memory stores budget_per_hire",
     [f for f in all_conv() if os.path.basename(f).startswith("DKB")
      and "Inbound" not in f and "Memory" not in f and "Output" not in f],
     ["The ARGUMENT wins over anything you remember"],
     []),

    ("dkb-posting-precondition", "the existing-posting template is guarded by a job_role check, and "
                                 "says its worked values are illustrations -- 714ebfc0 announced "
                                 "\"Helper, दो vacancies, सैलरी बारह हज़ार\" with every job field "
                                 "\"Not Available\", using the number rule's own examples as data",
     [f for f in all_conv() if os.path.basename(f).startswith("DKB")
      and "Inbound" not in f and "Memory" not in f and "Output" not in f],
     ["ILLUSTRATIONS OF THE NUMBER RULE"],
     []),

    ("dkb-no-substitutable-business-name", "no DKB prompt PRINTS a business name that could be "
                                           "substituted when company_name is absent -- bd60c6b0 "
                                           "greeted an owner with the worked example printed under "
                                           "the greeting template, and 2ea06509 did the same; D82",
     [f for f in all_conv() if os.path.basename(f).startswith("DKB")
      and "Memory" not in f and "Output" not in f],
     [],
     ["VANS TRADING COMPANY", "YOGITA CLOTH EMPORIUM"]),

    ("dkb-number-slots-named-for-speech", "the posting template's number slots are named for the "
                                          "SPOKEN form -- with them named for the raw argument, "
                                          "290d8e5c said \"3 vacancies, salary 14,000\" with the "
                                          "conversion rule on the very next line",
     [f for f in all_conv() if os.path.basename(f).startswith("DKB")
      and "Inbound" not in f and "Memory" not in f and "Output" not in f],
     ["named for the SPOKEN form on purpose"],
     ["[num_vacancies] vacancies"]),

    ("dkb-role-name-script", "DKB states that [job_role] and [company_name] arrive in Latin and are "
                             "spoken in the target script -- no DKB prompt said this, and 714ebfc0 "
                             "said \"Helper\" in Latin",
     [f for f in all_conv() if os.path.basename(f).startswith("DKB")
      and "Inbound" not in f and "Memory" not in f and "Output" not in f],
     ["a role or a business name never does"],
     []),

    ("dkb-kn-business-name-script", "the DKB Kannada prompts say VERBATIM is about WHICH business, "
                                    "not which script -- 3e9590d2 asked \"Sharma Traders\" in Latin "
                                    "on a Kannada call while the Hindi twin converts",
     ["DKB/DKB Kannada Signals.md", "DKB/DKB Kannada.md"],
     ["Converting the script is your job"],
     []),

    ("dkb-recap-numbers-in-words", "the consent step says the RECAP obeys the number rule too -- "
                                   "3e9590d2 said the hours and vacancy count in words while "
                                   "collecting them, then recapped them as digits",
     [f for f in all_conv() if os.path.basename(f).startswith("DKB")
      and "Memory" not in f and "Output" not in f],
     ["recap is a sentence you build"],
     []),

    ("slash-rule-present", "every conversation prompt has the Slash ( / ) section -- it was absent "
                           "from all DKB, both TRRAIN and slim, and dkb-kn-out and trrain-hi-out "
                           "both spoke a literal slash",
     [f for f in all_conv() if "Memory" not in f and "Output" not in f],
     ["## Slash"],
     []),

    ("no-spoken-stage-direction-form-in-samples", "the samples do NOT demonstrate a speech-shaped "
                                                  "stage direction. 151 *(NOT SPOKEN ...)* "
                                                  "annotations were converted to INTERNAL: lines; "
                                                  "three rule-wordings had failed first and "
                                                  "f31e1587 was clean after the demonstrations went",
     [f for f in all_conv() if os.path.basename(f).startswith(("KKB Placeholder", "Maya"))
      and "Memory" not in f and "Output" not in f],
     [],
     ["*(NOT SPOKEN", "phone: +91"]),

    ("not-spoken-marker-is-a-marker", "the marker rule names the *(NOT SPOKEN ...)* form too -- "
                                      "557fbeb0 read one out loud INCLUDING the caller's phone "
                                      "number and profile fields; the rule had named [ ], *( ) and "
                                      "INTERNAL but not this one",
     [f for f in all_conv() if os.path.basename(f).startswith(("KKB Placeholder", "Maya"))
      and "Memory" not in f and "Output" not in f],
     ["has actually been read out loud"],
     []),

    ("no-quoted-bad-output-in-evidence-notes", "no prompt QUOTES a sentence the bot wrongly said. "
                                               "A note quoting the fabricated DKB posting was "
                                               "reproduced character-for-character on five calls "
                                               "while three other fixes were tried; D81b",
     [f for f in all_conv() if "Memory" not in f and "Output" not in f],
     [],
     ["announced \"आपकी एक posting है", "बारह हज़ार रुपये\" —"]),

    ("no-concrete-values-beside-templates", "no template block PRINTS a concrete value -- an "
                                            "example next to a template becomes the output. Three "
                                            "times tonight: generic trades became offerable jobs, a "
                                            "business name became the greeting (bd60c6b0), and a "
                                            "salary figure became the spoken salary (cc1b0ecc said "
                                            "\"twelve thousand\" when salary was 30000). D82",
     [f for f in all_conv() if "Memory" not in f and "Output" not in f],
     [],
     ["`12000` is", "`14000-20000` is", "`14000` is", "`3` is \"तीन\"", "`3` is \"ಮೂರು\""]),

    ("native-numerals-are-not-words", "the number rule says explicitly that Devanagari/Kannada "
                                      "numerals are still digits -- twice tonight the model "
                                      "re-rendered digits in the target script to satisfy \"in "
                                      "words\": 1c6963bb spoke a pin code as \"११००४५\" and 6e400995 "
                                      "spoke a salary as \"१२,००० से १६,०००\"",
     [f for f in all_conv() if os.path.basename(f).startswith(("KKB Placeholder", "Maya", "KKB Slim"))
      and "Memory" not in f and "Output" not in f],
     ["Words, not native-script digits"],
     []),

    ("no-jobs-line-has-no-role-branch", "the no-matching-role line has a branch for when the "
                                        "caller never named a role -- ea4972de had only been asked "
                                        "about location, so [role] had nothing to fill and the bot "
                                        "spoke the marker itself to the caller",
     [f for f in all_conv() if "की जॉब अभी नहीं है" in open(f, encoding="utf-8").read()],
     ["this sentence does NOT apply"],
     []),

    ("salary-in-words-at-point-of-use", "[salary] and [vacancy] are required in WORDS at the job "
                                        "template itself -- the rule lived ~700 lines away in the "
                                        "Numbers section and 33 of 399 salary phrases across KKB "
                                        "and Maya carried digits (f5a40741 said \"12,000\"); D82",
     [f for f in all_conv() if os.path.basename(f).startswith(("KKB Placeholder", "Maya", "KKB Slim"))
      and "Memory" not in f and "Output" not in f],
     ["spoken as WORDS.**"],
     []),

    ("slash-rule-at-point-of-use", "the slash rule is ALSO stated at the template that speaks "
                                   "[role] -- 21 of 28 leaks were the array role \"Computer "
                                   "Operator / Data Entry\" on bots that already had the section",
     [f for f in all_conv() if os.path.basename(f).startswith(("KKB Placeholder", "Maya", "KKB Slim"))
      and "Memory" not in f and "Output" not in f],
     ["in place of the slash"],
     []),

    ("no-verbatim-stage-direction", "no prompt PRINTS the stage-direction form it forbids -- the "
                                    "guard quoted `*(Silent tool call: apply_job)*` and the bot "
                                    "emitted exactly that on e4e81fe2 with zero tools called, "
                                    "fabricating an application; D81",
     [f for f in all_conv() if "Memory" not in f and "Output" not in f],
     [],
     ["*(Silent tool call"]),

    ("returning-caller-callback-clause", "the returning-caller callback clause exists in every "
                                         "OUTBOUND seeker prompt -- it was fixed on Hindi and Maya "
                                         "Signals and never mirrored, leaving both Kannada prompts "
                                         "with zero occurrences (tracker: Missing returning call "
                                         "user)",
     ["KKB/KKB Placeholder Hindi Signals.md", "KKB/KKB Placeholder Hindi.md",
      "KKB/KKB Placeholder Kannada Signals.md", "KKB/KKB Placeholder Kannada.md",
      "Maya/Maya Hindi Signals.md", "Maya/Maya Hindi.md"],
     ["Callback-clause rules:"],
     []),

    ("kn-failure-line-asserts-nothing", "the Kannada failure line asserts NOTHING about whether the "
                                       "application exists -- the routing between it and Row 1 is "
                                       "broken on both routes (7f2e3928, 5bbb6ca1), so the line "
                                       "itself must be true in every case it is reached for",
     [f for f in all_conv() if "Kannada" in os.path.basename(f)
      and os.path.basename(f).startswith("KKB Placeholder")
      and "Memory" not in f and "Output" not in f],
     ["ನಿಮ್ಮ ಆಸಕ್ತಿ ನಾವು ನೋಟ್ ಮಾಡ್ಕೊಂಡಿದೀವಿ"],
     ["ಸಧ್ಯಕ್ಕೆ ಆಗಿಲ್ಲ", "ಮುಂದೆ ಹೋಗಿಲ್ಲ"]),

    ("slim-neverinvent-deep-dive", "the deep-dive template block itself says a job absent from the "
                                   "array has no deep dive, so its salary/vacancy/qualification "
                                   "cannot be supplied; D79",
     ["KKB-Slim/KKB Slim Hindi Signals.md"],
     ["has no deep dive"],
     []),

    ("phase2-bridge-claims-nothing", "the Phase-2 bridge does NOT assert the apply succeeded — "
                                     "e75bf95f and 7e586f14 told real callers \"ಅಪ್ಲೈ ಆಗಿದೆ\" after "
                                     "two 422s, via this line rather than the guarded success line",
     [f for f in seeker_conv() if "Signals" in os.path.basename(f)],
     ["asserts NOTHING about the application"],
     ["अप्लाई हो गया है। आपकी जानकारी पूरी", "ಅಪ್ಲೈ ಆಗಿದೆ. ನಿಮ್ಮ ಮಾಹಿತಿ"]),

    ("readback-age-gender-in-words", "the read-back template itself says [age] is spoken in words and "
                                     "[gender] in the target language — 08449995 said "
                                     "\"ವಯಸ್ಸು 38, Male\", and 8 of 28 read-backs carried a raw "
                                     "digit or an English enum (D71 at the point of use)",
     [f for f in seeker_conv() if "Signals" in os.path.basename(f)],
     ["come off the profile as a NUMBER and an English enum"], []),

    ("dkb-salary-in-words", "the DKB posting recap itself says [num_vacancies] and [salary] are "
                            "spoken in words — 56 of 389 salary lines fleet-wide used digits, almost "
                            "all on this one template",
     DKB_SIGNALS + [os.path.join(REPO, "DKB", "DKB Hindi.md"),
                    os.path.join(REPO, "DKB", "DKB Kannada.md")],
     ["arrive as DIGITS and are spoken in WORDS"], []),

    ("brackets-are-slots-not-speech", "every conversation prompt says a [slot] marker is filled, "
                                      "never spoken — 13 live calls read one out, including two that "
                                      "said '[UUID from create_profile result]' to a caller (D77)",
     all_conv(), ["A square-bracket marker is a SLOT TO FILL"], []),

    ("dkb-business-name-in-script", "\"literal\"/\"VERBATIM\" on the DKB opener means the same "
                                   "business, NOT the same script — 0da5e1f9 asked an owner "
                                   "\"क्या आप VANS TRADING COMPANY से बोल रहे हैं?\"",
     DKB_SIGNALS + [os.path.join(REPO, "DKB", "DKB Hindi.md"),
                    os.path.join(REPO, "DKB", "DKB Kannada.md")],
     ["the same business, spoken in"], []),

    ("company-converted-at-point-of-use", "the job-presentation format itself says [role]/[company]/"
                                          "[location] arrive in Latin and are converted — the "
                                          "Devanagari rule was stated five times elsewhere and the "
                                          "payload still went out raw, 5x in one call (D71, ea0477f4, "
                                          "90658584)",
     seeker_conv(), ["arrive from `${recommendations}` in LATIN script"], []),

    ("maya-collegename-only-decides", "ONLY the college_name value line picks Maya's opener — the bare "
                                      "string 'Not Available' in `contact_memory` was satisfying branch B, "
                                      "so branch A fired 48/48 on maya-hi-out and 2/14 on maya-hi-signals "
                                      "(D75, 08a8ff4f)",
     [f for f in MAYA_CONV if "Inbound" not in os.path.basename(f)],
     ["No other field's value has any bearing on it"], []),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    cache = {}
    fails = []
    print("fix-presence check | %d fixes" % len(FIXES))
    for fid, desc, files, must, must_not in FIXES:
        missing, leaked = [], []
        for f in files:
            if f not in cache:
                if not os.path.exists(f):
                    missing.append((os.path.basename(f), "FILE MISSING")); continue
                cache[f] = open(f, encoding="utf-8").read()
            text = cache[f]
            # must_contain is satisfied by ANY of the tokens: a fix may be worded per language, and
            # the point is that the fix is present, not that one exact spelling is.
            # NOTE: `must` is ANY-of, not all-of. That is deliberate: a fix mirrored across
            # languages has a different spoken string per language, and a given file can only
            # contain its own. A row needing TWO things present in the SAME file cannot be
            # expressed here -- split it into two rows instead. (2 of 31 rows are multi-token.)
            if must and not any(t in text for t in must):
                missing.append((os.path.basename(f), must[0][:60]))
            for t in must_not:
                if t in text:
                    leaked.append((os.path.basename(f), t.splitlines()[0][:60]))
        status = "OK" if not (missing or leaked) else "FAIL"
        print("  %-4s %-28s %d bot(s)  %s" % (status, fid, len(files), desc if a.verbose else ""))
        for b, t in missing:
            print("        MISSING   %-46s expected: %s" % (b, t)); fails.append(fid)
        for b, t in leaked:
            print("        REGRESSED %-46s must not contain: %s" % (b, t)); fails.append(fid)
    print("")
    if fails:
        print("FIX PRESENCE: %d failure(s) across %d fix(es)" % (len(fails), len(set(fails))))
        sys.exit(1)
    print("FIX PRESENCE CLEAN — every shipped fix present on every bot that needs it")


if __name__ == "__main__":
    main()
