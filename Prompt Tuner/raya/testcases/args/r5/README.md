# r5 fixtures (2026-09-08)

Each reproduces a failure that was seen on a real call, so a dial either confirms the fix or does not.
Pass conditions are one line each — no interpretation needed.

| fixture | reproduces | pass condition |
|---|---|---|
| `sarjapur-offlist.json` | `7b841e6b` — `location: "Sarjapur, 110045"`, a place on no list in the prompt, spoken raw in Latin with the PIN. Also carries the 12-job payload with `SARA ENTERPRISES`, `MAHARAJA ENGINEERING WORKS`, `GLOBAL CHEMICALS`, so it exercises the company-name conversion and the deep-dive qualification line in the same call | the location sentence says **सरजापुर**; no Latin and no digits anywhere in a spoken turn |
| `maya-vmlg-offlist.json` | `08a8ff4f` — `college_name: "VMLG College"` (the value on 345 of 460 cached Maya calls) **with** `contact_memory: "Not Available"`, which is what made branch B fire | the opener says **वीएमएलजी कॉलेज**; not "मैं माया बोल रही हूँ" |
| `dkb-no-company-name.json` | `564e1d45`, `be4ab8c3` — no `company_name` argument at all, which the emptiness test did not cover | the opener is **"हैलो, क्या आप एक बिज़नेस ओनर हैं?"**; the words "Not Available" appear nowhere |
| `dkb-latin-business-name.json` | `0da5e1f9` — `company_name: "VANS TRADING COMPANY"` read out in Latin to that business's own owner | the opener says **वैन्स ट्रेडिंग कंपनी**; no `VANS`/`TRADING`/`COMPANY` in Latin, and no `[company_name]` marker |
| `readback-kn.json` (in `r3/`) | the end-of-call read-back, on the Dharwad instance where the tester's applications are not saturated | after a successful apply, name, age, gender, role, qualification and area are read back, then **"ಎಲ್ಲಾ ಸರಿನಾ?"** |

**Which bot to dial each on** — the fixture does not encode it:

```
sarjapur-offlist         115b38a5 (kkb-hi-signals)  and 140d13ca (slim)
maya-vmlg-offlist        904f333f (maya-hi-signals)
dkb-no-company-name      fabda71d (dkb-hi-signals)
dkb-latin-business-name  fabda71d (dkb-hi-signals)   persona: hi-employer-cooperative
readback-kn              33037201 (kkb-kn-signals)   persona: kn-force-apply, language kn
```

Tester agent `f60e0899-aa3a-4be7-9b4f-0296bd28ef48`, inbound DID `7946350285`. Set the persona with
`scripts/raya_testcall.py persona <tester> <persona.md>` and the language with `… lang <tester> hi|kn`
before dialling — the tester keeps whatever was set last, and a Kannada fixture on a Hindi persona
proves nothing.

## A confound in `sarjapur-offlist.json` — read this before quoting a rate from it

`get_profile` on the tester DID returns a profile carrying **`location: "Sahibabad, Ghaziabad,
India"`**. This fixture sends `location: "Sarjapur, 110045"`. So every dial with it creates a
**profile-versus-argument conflict**, and the bot has two ways to be wrong and one to be right:

| what it says | what that means |
|---|---|
| सरजापुर | correct — argument obeyed and converted (`317bd6e0`, `cea642ea`) |
| साहिबाबाद / गाज़ियाबाद | the **profile** beat `${location}` — a precedence failure, not a conversion one |
| `Sarjapur, 110045` | conversion failed — the raw written value |

That makes it a good two-in-one test and a **terrible source of a production rate**: real callers are
generally dialled where their profile says they live, so the conflict this fixture guarantees is rare
in traffic. Ten "substitution" findings were reported as a caller-facing rate before being split by
caller; all ten were dials with this fixture and not one was a real caller.

**So:** use it to test conversion and precedence, read the three outcomes above as three different
findings, and take rates only from `location_said.py`'s REAL CALLERS line.

## Repeated dials on the tester DID are NOT independent — platform memory carries between them

**Proven on `2ea06509`.** That dial sent **two** arguments — `contact_memory` (literally
`"No Old Memory, Mandatory get_profile for the user"`) and `country_code`. No `company_name`. The
call made **zero tool calls**. And the bot opened with
**"हैलो! क्या आप VANS TRADING COMPANY से बोल रहे हैं?"** — the value from `b187ffeb`, dialled ten
minutes earlier on the same tester number.

The path is documented, not inferred: `dkb-hi-signals` has `memory_enabled: True`, and its memory
prompt records **`business_name`** keyed on `business_id` (the phone number). So Raya wrote the
company name after the first dial and injected it into the second — **bypassing the
`${contact_memory}` argument entirely**, which is why saying "No Old Memory" in that argument
changed nothing.

**What this means for every fixture here:**

- **A value you deliberately omit may still reach the bot** from a previous dial on the same number.
  Omission is not a clean negative test.
- **Back-to-back dials are correlated.** Two dials of the same fixture are not two samples; two dials
  of *different* fixtures can contaminate each other.
- **A test of "what happens when field X is absent" needs a phone number with no history**, or the
  memory cleared, or a long enough gap — none of which the harness currently gives you.
- **This invalidated one experiment today.** `910b2d29` was meant to be the control for whether
  `contact_memory` drives Maya's opener; it omitted the field but ran on a number with history, and
  made zero tool calls. It controls nothing, and the conclusion drawn from it was withdrawn.

Corroborated independently on Maya: `d15a8f9b` produced a specific callback claim — *"पिछली बार हमारी
बात एक जॉब में अप्लाई करने के बारे में हुई थी"* — that was **not** in the `contact_memory` sent to it.
Two bots, two mechanisms of the same kind. See `ESCALATION-litwiz.md` §4(a).

## named-error-row2a.json — triggers the D80 Row 2a line
One job carrying a well-formed but nonexistent `job_id` (`00000000-dead-4bee-8fff-000000000001`).
The backend answers `apply_job` with `TARGET_ITEM_NOT_FOUND`, a NAMED non-duplicate error, which
must route to the new row and produce "अप्लाई अभी पूरा नहीं हो पाया" — NOT the Row 2 technical-issue
line and NOT the Row 1 already-applied line. Use it to verify D80 on any seeker bot. Safe: it only
ever touches the tester profile, and a nonexistent job cannot create a real application.

## already-applied.json — reachable on HINDI ONLY

Uses `a8155bee`, which returns `ACTION_LIMIT_REACHED` for the HINDI tester profile (`588a907f`)
because that profile genuinely holds an application to it. Proven on `45e2cb3b`, `764cba1d`,
`6caf1fbe`.

**On Kannada it does NOT reach the condition.** `cf781998` ran the same fixture on kkb-kn-signals
and got `TARGET_ITEM_NOT_FOUND` — the Kannada tester is a different profile and has never applied
to that job. To test the already-applied line on Kannada, first make a successful apply from the
Kannada tester and then reuse that job id here.

This matters because the already-applied line is the 45-of-60 defect
(`ESCALATION-litwiz.md` §1) and the baseline rate is 4 of 34 (12%) — see
`raya/regression/already_applied_rate.py`.
