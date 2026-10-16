# loc2 — location/pincode fixtures

The `sweep/` fixtures carry NO `location` argument, so a fleet sweep using them never
exercises the location turn or the pincode conversion — the highest-priority reported
issue. These are the same fixtures with a `location` added, one per case worth testing.

- **kkb-hi-signals-pin-onlist** — `location='Muradnagar, 110045'`
  pincode + a place ON the canonical list -> must speak मुराद नगर, never the digits
- **kkb-hi-signals-pin-offlist** — `location='Sarjapur, 110045'`
  pincode + a place OFF the list -> must still convert, to सरजापुर
- **kkb-kn-signals-pin** — `location='Hubballi, 580020'`
  Kannada pincode case -> must speak ಹುಬ್ಬಳ್ಳಿ, never the digits
- **kkb-kn-signals-pin-offlist** — `location='Sarjapur, 110045'`
  Kannada, off-list place with pincode
- **maya-hi-signals-pin** — `location='Muradnagar, 110045'`
  Maya carries the same location turn -- test it independently, never extrapolate
- **kkb-hi-out-pin** — `location='Muradnagar, 110045'`
  the non-Signals Hindi outbound pair
- **kkb-kn-out-pin** — `location='Hubballi, 580020'`
  the non-Signals Kannada outbound pair
- **kkb-hi-signals-loc-any** — `location='Any'`
  edge: location is the literal "Any" -> must be treated as EMPTY, ask the turn instead
- **kkb-hi-signals-loc-na** — `location='Not Available'`
  edge: "Not Available" -> treated as EMPTY, and never spoken aloud
- **kkb-hi-signals-loc-token** — `location='${location}'`
  edge: an UNSUBSTITUTED token -> treated as EMPTY, never read aloud

## The tester-profile confound — read before trusting a location result

The Kannada tester profile stores `location: "Koramangala, Bengaluru, Karnataka, India"`. Any
fixture that sends a DIFFERENT place stops testing pin-code dropping and starts testing location
precedence (input vs fetched profile) instead, because the model reaches for the profile value.

That precedence guard has now failed three times in prose — `2bf465d9`, `8976c120` (both sent
`location: Hubli`) and `15434ef6` (sent `Hubballi, 580020`), all three spoke "ಕೊರಮಂಗಲ". The prompt
already states the rule as forcefully as prose can ("the profile's stored location is NOT A SOURCE
for this sentence at all") and the spoken template already uses the literal `${location}` token
rather than a bracket slot, so the mechanism fix that worked for DKB's `company_name` has already
been applied here and did not hold. **Do not add a fourth wording** (see CLAUDE.md).

It has never been observed on a real caller: 0 of 432 real-caller calls carrying `${location}`.
Real callers' profile city and campaign location generally agree, so the conflict does not arise.

- `kkb-kn-signals-pin.json` — `Koramangala, 560034`. Place MATCHES the profile, so the only thing
  under test is whether the digits are dropped.
- `kkb-kn-signals-precedence.json` — `Hubballi, 580020`. Place deliberately differs. This is a
  KNOWN-FAILING precedence test, kept so the behaviour is tracked, not a pin-code test.
