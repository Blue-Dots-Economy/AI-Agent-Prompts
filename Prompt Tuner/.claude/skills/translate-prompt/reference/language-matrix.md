# Indic Language Matrix — for `/translate-prompt`

Per-language conventions needed to **re-author** (not translate) a voice-agent's spoken content, and
to **re-derive** the spoken-form machinery that makes TTS come out right. One section per language.

## How to use this file

1. Read the target language's section **before** writing a single spoken line.
2. Copy the numerals / money / phone conventions into the new file's `TTS Normalization Rules`
   section, keeping the master's **English** scaffolding and headings identical: only the
   target-language example strings change.
3. Copy the script rule + loanword level into `Language and Script Rules`.
4. Use the honorifics, greeting and place names when re-authoring spoken lines and examples.
5. Treat the pitfalls row as a **test plan**: each pitfall is something to listen for in the first
   live call (`/translate-prompt` step 13).

**Three per-language sources, one job each.** This file holds the conventions (register, numbers,
greetings, places, pitfalls). `raya/translations/lexicon.json` holds the machine-read word lists
(everyday words for the minimum terms, bookish words, Hindi marker words, insulting words, the gender
and question rules, the script range). `raya/translations/style/<iso>.md` holds lessons from earlier
runs in that language. `scripts/speech_split.py extract` compiles all three into the `STYLE.md` card
the translating agents read, so put a fact in the one place it belongs rather than in all three.

**Keep the heading format.** `speech_split.py` finds a language's section by a heading that starts
with `## ` and ends with the ISO code in backticks inside brackets, and reads up to the next `---`. A
section whose heading loses that ending is silently left out of every STYLE.md.

## Honesty rule — read this before trusting a cell

Cells marked **`[needs native review]`** are the author's best understanding and **must be confirmed
by a native speaker** before the language is called verified. They are *not* errors to be quietly
smoothed over — they are the exact places where a confident guess about someone's language does
damage. Carry every flag you rely on into the QA record
(`raya/translations/<bot-id>-<iso>.md`) and mark the language **VERIFY-PENDING** until a named human
signs off (repo `CLAUDE.md` → *Testing is mandatory*).

Coverage is honestly uneven. **Hindi and Kannada** are grounded in this repo's live, call-verified
prompts. **Telugu, Malayalam, Tamil, Marathi, Bengali, Gujarati** rest on well-established general
usage but have not been call-verified here. **Punjabi, Odia, Assamese, Urdu** are the thinnest —
treat most of their cells as provisional. Being explicit about that is more useful than false
precision.

## Rules that apply to EVERY language (do not re-derive these — they never change)

- **Instructions in English.** Only the words the bot speaks are in the target language.
- **Never emit native-script digits** — `౧౨౩`, `১২৩`, `૧૨૩`, `੧੨੩`, `୧୨୩`, `۱۲۳` are all forbidden in
  spoken lines. Numbers appear as **words**.
- **Never voice the "/" symbol** — use the language's word for "or"; for rates, say the per-form
  (bug D6).
- **Never AM/PM** — use the language's day-part words (bug D2).
- **Never speak internal terms** ("profile", "payload", "database", "fetch", "id", tool names) —
  use the friendly everyday word (bug D8).
- **Pin place names** in a `Canonical Location Spellings` section that overrides all dynamic
  transliteration and phonetic matching (bug D26).
- **Payload values stay Latin; spoken output stays in the target script** (bug D3).
- **Phone numbers are read digit-by-digit as words** — and which zero-word real speakers use
  differs by language (the literary word is often not what people say). Every zero cell below is
  flagged for that reason.

---

## Hindi — हिन्दी (`hi`)

| | |
|---|---|
| **Script** | Devanagari only. No Roman Hindi, no mixed script. |
| **Register for a low-literacy phone audience** | Simple spoken Hindustani. Polite **आप** throughout, never तू/तुम to a caller. Avoid Sanskritised administrative vocabulary — bug **D1** (`सेवा प्रदाता`, `प्रशिक्षण`, `मूल्यांकन`, `आवेदन`, `नियोजन`, `वेतन`, `साक्षात्कार` are all bookish here). |
| **Numbers as words** | `2 से 3` → "दो से तीन"; `350–400` → "तीन सौ पचास से चार सौ". |
| **Money (worked)** | `₹13,000–₹17,000` → "तेरह हज़ार से सत्रह हज़ार रुपये"; `₹500/day` → "दिन के पाँच सौ रुपये". |
| **Phone (worked)** | Digit-by-digit: "नौ, आठ, सात, छह, पाँच, चार, तीन, दो, एक, ज़ीरो". Real speakers say **ज़ीरो**; `शून्य` is bookish. |
| **Dates / times** | `29/01/2026` → "उन्तीस जनवरी दो हज़ार छब्बीस". Day-parts: सुबह / दोपहर / शाम / रात. |
| **English code-mixing** | **HIGH.** जॉब, अप्लाई, इंटरव्यू, सैलरी, कंपनी, ऑफिस, मार्केट, स्किल, ऑप्शन, डेटा, व्हाट्सऐप — all natural in speech, written in Devanagari. |
| **Honorifics / address** | आप + plural verb; `जी` after a name (रमेश जी) sparingly; भैया / बहन for strangers, but over-use reads as over-familiar. |
| **Greeting / farewell** | नमस्ते / नमस्कार. Close: धन्यवाद + नमस्ते. |
| **Place names for examples** | गाज़ियाबाद, लखनऊ, कानपुर, मेरठ, वाराणसी, इंदिरापुरम, मोहन नगर. |
| **TTS / ASR pitfalls** | Nukta letters (ज़, ख़, फ़, ग़) are often dropped in data and mispronounced by TTS — **pin one spelling per place** (D26; `गाज़ियाबाद` vs `गाजियाबाद` must not vary). ASR mishears English words spoken with an Indian accent ("female" → "ईमेल", real call `5449910e`) and numbers (age 20 → 24) → always read critical fields back. |
| **Grounding** | Live, call-verified in this repo (`KKB/`, `DKB/`, `Maya/` Hindi prompts). |

---

## Kannada — ಕನ್ನಡ (`kn`)

| | |
|---|---|
| **Script** | Kannada script only. No Roman Kannada, no mixed script. |
| **Register** | Spoken Kannada + **"Kanglish"** — Kannada mixed naturally with the English words people actually use. Polite **ನೀವು**. |
| **Numbers as words** | `2 ರಿಂದ 3` → "ಎರಡರಿಂದ ಮೂರು"; `350–400` → "ಮುನ್ನೂರ ಐವತ್ತರಿಂದ ನಾನೂರು". |
| **Money (worked)** | `₹13,000–₹17,000` → "ಹದಿಮೂರು ಸಾವಿರದಿಂದ ಹದಿನೇಳು ಸಾವಿರ"; `₹500/day` → "ದಿನಕ್ಕೆ ಐನೂರು ರೂಪಾಯಿ". |
| **Phone (worked)** | "ಒಂಭತ್ತು, ಎಂಟು, ಏಳು, ಆರು, ಐದು, ನಾಲ್ಕು, ಮೂರು, ಎರಡು, ಒಂದು, ಸೊನ್ನೆ" (ಸೊನ್ನೆ is genuinely used; ಝೀರೋ also occurs). |
| **Dates / times** | `29/01/2026` → "ಇಪ್ಪತ್ತೊಂಭತ್ತು ಜನವರಿ ಎರಡು ಸಾವಿರದ ಇಪ್ಪತ್ತಾರು". Day-parts: ಬೆಳಗ್ಗೆ / ಮಧ್ಯಾಹ್ನ / ಸಂಜೆ / ರಾತ್ರಿ. |
| **English code-mixing** | **VERY HIGH.** ಜಾಬ್, ಅಪ್ಲೈ, ಮಾರ್ಕೆಟ್, ಸ್ಕಿಲ್, ಆಪ್ಷನ್, ವೆರಿಫೈಡ್, ಲೊಕೇಷನ್, ಕನ್ಸೆಂಟ್, ಡೇಟಾ, ವಾಟ್ಸ್‌ಆಪ್ — in Kannada script. |
| **Honorifics / address** | ನೀವು; ಸರ್ / ಮೇಡಂ common; ಅಣ್ಣ / ಅಕ್ಕ warm for peers. |
| **Greeting / farewell** | ನಮಸ್ಕಾರ. Close: ಧನ್ಯವಾದ + ನಮಸ್ಕಾರ. |
| **"or" for "/"** | ಅಥವಾ. |
| **Place names for examples** | ಬೆಂಗಳೂರು, ಮೈಸೂರು, ಹುಬ್ಬಳ್ಳಿ, ಧಾರವಾಡ, ಮಂಗಳೂರು, ಕಲಬುರಗಿ, ಬೆಳಗಾವಿ. |
| **TTS / ASR pitfalls** | Heavy conjunct ligatures can be mis-segmented; the obsolete ಱ / ೞ must never appear. Cross-script contamination (a Devanagari fragment left in a Kannada line) is the classic sync bug. Verified live: role labels containing "/" must be spoken with ಅಥವಾ (D6). |
| **Grounding** | Live, call-verified in this repo (`KKB`/`DKB` Kannada prompts). |

---

## Telugu — తెలుగు (`te`)

| | |
|---|---|
| **Script** | Telugu script only. |
| **Register** | Everyday **spoken** Telugu, never *granthika* (literary). **Regional variety matters and must be chosen deliberately:** Telangana speech (e.g. `ఉన్నదా`, `చేస్తున్నా`, `ఏమైంది`) vs Coastal Andhra / Rayalaseema (`ఉందా`, `చేస్తున్నాను`). Pick by the campaign's caller base. `[needs native review]` on which variety to standardise, and on how much Telangana-marked morphology is safe for a state-wide bot. |
| **Politeness** | **మీరు** + honorific verb ending; the particle **అండి** is the workhorse of polite Telugu speech ("సరే అండి", "చెప్పండి") — omitting it sounds curt. |
| **Numbers as words** | `2 నుంచి 3` → "రెండు నుంచి మూడు"; `350–400` → "మూడు వందల ఏభై నుంచి నాలుగు వందలు". |
| **Money (worked)** | `₹13,000–₹17,000` → "పదమూడు వేల నుంచి పదిహేడు వేల రూపాయలు"; `₹500/day` → "రోజుకి ఐదు వందల రూపాయలు". |
| **Phone (worked)** | "తొమ్మిది, ఎనిమిది, ఏడు, ఆరు, ఐదు, నాలుగు, మూడు, రెండు, ఒకటి, సున్నా" — many speakers say **జీరో** for the last digit `[needs native review]`. |
| **Dates / times** | `29/01/2026` → "రెండు వేల ఇరవై ఆరు, జనవరి ఇరవై తొమ్మిది" `[needs native review]` on the most natural spoken order. Day-parts: ఉదయం / మధ్యాహ్నం / సాయంత్రం / రాత్రి. |
| **English code-mixing** | **VERY HIGH** — one of the most English-mixed Indian languages in speech. జాబ్, అప్లై, ఇంటర్వ్యూ, శాలరీ, కంపెనీ, ఆఫీస్, స్కిల్, ఆప్షన్. Native `ఉద్యోగం` is fine and common for "job"; `దరఖాస్తు` for "apply" is bookish — say **అప్లై** (bug D1). |
| **Honorifics / address** | **గారు** after a name is the standard respect marker (రమేష్ గారు); సర్ / మేడం common; అన్నా / అక్కా informal-warm. |
| **Greeting / farewell** | నమస్కారం. Close: ధన్యవాదాలు; "ఉంటాను అండి" is a natural spoken sign-off `[needs native review]`. |
| **"or" for "/"** | లేదా (spoken: often "or" itself). |
| **Place names for examples** | హైదరాబాద్, వరంగల్, కరీంనగర్, నిజామాబాద్, విజయవాడ, విశాఖపట్నం, గుంటూరు, తిరుపతి. |
| **TTS / ASR pitfalls** | Long/short vowel and aspiration contrasts carry meaning; ASR commonly collapses త/థ, ద/ధ, ప/ఫ. The archaic ఱ must never appear. Telugu numerals ౦–౯ must never be emitted. Verify how the chosen voice handles the `అండి` particle at line ends — a wrong prosody there sounds abrupt. |

---

## Malayalam — മലയാളം (`ml`)

| | |
|---|---|
| **Script** | Malayalam script only. |
| **Register** | Spoken Malayalam is markedly different from written Malayalam — use spoken forms (`ചെയ്യാം`, `ഉണ്ടോ`, `വേണോ`, `ശരി`), never the literary/Sanskritic register a machine translation will reach for. |
| **Politeness** | **നിങ്ങൾ** is the safe neutral polite you. `താങ്കൾ` is very formal/written and sounds stiff on a call. **ചേട്ടൻ / ചേച്ചി** ("elder brother/sister") is the genuinely natural warm address for a stranger of similar-or-older age and is worth using `[needs native review]` on how it lands from a government/service bot. |
| **Numbers as words** | `2 മുതൽ 3` → "രണ്ട് മുതൽ മൂന്ന്"; `350–400` → "മുന്നൂറ്റി അമ്പത് മുതൽ നാനൂറ്". |
| **Money (worked)** | `₹13,000–₹17,000` → "പതിമൂന്നായിരം മുതൽ പതിനേഴായിരം രൂപ വരെ"; `₹500/day` → "ദിവസം അഞ്ഞൂറ് രൂപ". |
| **Phone (worked)** | "ഒൻപത്, എട്ട്, ഏഴ്, ആറ്, അഞ്ച്, നാല്, മൂന്ന്, രണ്ട്, ഒന്ന്, പൂജ്യം" — in real speech **സീറോ** is more common than പൂജ്യം `[needs native review]`. |
| **Dates / times** | `29/01/2026` → "രണ്ടായിരത്തി ഇരുപത്തിയാറ് ജനുവരി ഇരുപത്തിയൊൻപത്" `[needs native review]` on spoken order. Day-parts: രാവിലെ / ഉച്ചയ്ക്ക് / വൈകുന്നേരം / രാത്രി. |
| **English code-mixing** | **VERY HIGH.** ജോലി is the natural native word for "job", but അപ്ലൈ, ഇന്റർവ്യൂ, സാലറി, കമ്പനി, ഓഫീസ്, ഓപ്ഷൻ are all normal in speech. |
| **Honorifics / address** | സാർ / മാഡം common; ചേട്ടൻ/ചേച്ചി as above; no strong name-suffix honorific equivalent to గారు/जी. |
| **Greeting / farewell** | നമസ്കാരം as the neutral greeting; many callers simply answer "ഹലോ". Close: നന്ദി; "ശരി, നന്ദി" is natural. |
| **"or" for "/"** | അല്ലെങ്കിൽ. |
| **Place names for examples** | കൊച്ചി, തിരുവനന്തപുരം, കോഴിക്കോട്, തൃശ്ശൂർ, കൊല്ലം, മലപ്പുറം, കണ്ണൂർ, ആലപ്പുഴ. |
| **TTS / ASR pitfalls** | **Old vs reformed orthography** (the `ു`/`ൂ`/`്ര` ligature forms) renders differently across fonts and voices — pick one and be consistent. **Chillu letters** (ൻ ർ ൽ ൾ ൺ) and ZWJ/ZWNJ around chandrakkala are a real corruption risk when text is copied between tools — verify by byte-level diff, not by eye. Malayalam forms very long compounds; break them for TTS. Malayalam numerals must never be emitted. |

---

## Tamil — தமிழ் (`ta`)

| | |
|---|---|
| **Script** | Tamil script only; use the **grantha** letters (ஜ ஷ ஸ ஹ க்ஷ) for English loanwords — without them, loanwords are mispronounced. |
| **Register** | **Tamil has the sharpest diglossia of this set and it is the single biggest failure mode.** A phone bot must speak *koduntamizh* (spoken Tamil): `இருக்குங்க`, `சொல்லுங்க`, `வேணுமா`, `பாக்கலாம்` — **never** *sentamizh* (literary): `இருக்கிறது`, `கூறுங்கள்`, `வேண்டுமா`. Literary Tamil on a call sounds like a news bulletin and is the classic machine-translation output. |
| **Politeness** | **நீங்க** (spoken form of நீங்கள்) with the **`-ங்க`** politeness suffix on every imperative: வாங்க, சொல்லுங்க, கேளுங்க, இருங்க. Dropping `-ங்க` is rude. |
| **Numbers as words** | `2 முதல் 3` → "ரெண்டு முதல் மூணு" (spoken) — note spoken `ரெண்டு/மூணு` vs written `இரண்டு/மூன்று` `[needs native review]` on how far to push spoken numeral forms in TTS text. `350–400` → "முந்நூறு ஐம்பது முதல் நாநூறு". |
| **Money (worked)** | `₹13,000–₹17,000` → "பதிமூன்றாயிரம் முதல் பதினேழாயிரம் ரூபாய் வரை"; `₹500/day` → "ஒரு நாளுக்கு ஐந்நூறு ரூபாய்". |
| **Phone (worked)** | "ஒன்பது, எட்டு, ஏழு, ஆறு, ஐந்து, நான்கு, மூன்று, இரண்டு, ஒன்று, ஜீரோ" — **ஜீரோ** is what people say; பூஜ்யம் is bookish. |
| **Dates / times** | `29/01/2026` → "இரண்டாயிரத்து இருபத்தி ஆறு ஜனவரி இருபத்தி ஒன்பது" `[needs native review]`. Day-parts: காலை / மதியம் / மாலை / இரவு. |
| **English code-mixing** | **HIGH in real speech**, even though formal Tamil media is purist. Use ஜாப் / வேலை, அப்ளை, இன்டர்வியூ, சேலரி, கம்பெனி, ஆஃபீஸ். `வேலை` is the natural native word for work/job; `விண்ணப்பம்` for "apply" is bookish — say **அப்ளை** (bug D1). |
| **Honorifics / address** | சார் / மேடம்; அண்ணா / அக்கா warm; `அவர்கள்`-style honorific plural for third-person respect. No `जी`-equivalent name suffix. |
| **Greeting / farewell** | வணக்கம். Close: நன்றி + வணக்கம். |
| **"or" for "/"** | அல்லது. |
| **Place names for examples** | சென்னை, கோயம்புத்தூர், மதுரை, திருச்சி, சேலம், திருப்பூர், தூத்துக்குடி, வேலூர். |
| **TTS / ASR pitfalls** | Tamil script has **no separate voiced stops** — க/ச/ட/த/ப are voiced by context, so loanwords need grantha letters or they come out wrong. ASR routinely collapses **ழ / ள / ல** and **ண / ந / ன**; retroflex **ழ** is a known TTS weak point (பழம்/பலம்). Confirm any spoken line containing ழ in the first live call. Tamil numerals must never be emitted. |

---

## Marathi — मराठी (`mr`)

| | |
|---|---|
| **Script** | Devanagari — but **Marathi Devanagari is not Hindi Devanagari.** Uses ळ, and the ॅ / ॉ vowels for English sounds (सॅलरी, कॅब, ऑफिस). |
| **Register** | Spoken Marathi, polite **तुम्ही** (never तू to a caller). `आपण` is very formal/inclusive — usually too stiff for a service call. |
| **Numbers as words** | `2 ते 3` → "दोन ते तीन"; `350–400` → "साडेतीनशे ते चारशे" (or "तीनशे पन्नास ते चारशे"). |
| **Money (worked)** | `₹13,000–₹17,000` → "तेरा हजार ते सतरा हजार रुपये"; `₹500/day` → "दिवसाला पाचशे रुपये". |
| **Phone (worked)** | "नऊ, आठ, सात, सहा, पाच, चार, तीन, दोन, एक, झिरो" — **झिरो** in speech; शून्य is bookish. |
| **Dates / times** | `29/01/2026` → "एकोणतीस जानेवारी दोन हजार सव्वीस". Day-parts: सकाळी / दुपारी / संध्याकाळी / रात्री. |
| **English code-mixing** | **HIGH.** जॉब, अप्लाय, इंटरव्ह्यू, सॅलरी, कंपनी, ऑफिस, स्किल, ऑप्शन. |
| **Honorifics / address** | तुम्ही + plural verb; साहेब / मॅडम; दादा / ताई for warmth (very natural in Marathi). Name + जी is less Marathi than Hindi — prefer दादा/ताई or plain तुम्ही `[needs native review]`. |
| **Greeting / farewell** | नमस्कार. Close: धन्यवाद + नमस्कार. |
| **"or" for "/"** | किंवा. |
| **Place names for examples** | पुणे, नागपूर, नाशिक, ठाणे, कोल्हापूर, सोलापूर, अमरावती. **छत्रपती संभाजीनगर** (formerly औरंगाबाद) — a renamed city: pick ONE form with the owner and pin it (D26). |
| **TTS / ASR pitfalls** | **A Hindi voice reading Marathi text is an audible, common failure**: ळ, the ॅ/ॉ vowels, and Marathi's affricate च/ज (dental vs palatal) are all wrong in a Hindi voice. Verify the agent's `language_id`/`voice_id` are genuinely Marathi (`/translate-prompt` step 11) before testing. Shared Devanagari also means Hindi text can be left in unnoticed: `speech_split.py apply` and `language_checks.py` fail on unchanged lines and Hindi marker words (D118), but a reader must still check meaning. |

---

## Bengali — বাংলা (`bn`)

| | |
|---|---|
| **Script** | Bengali script only. |
| **Register** | **cholit-bhasha** (colloquial) — `করছি`, `বলুন`, `আছে`. Never *sadhu-bhasha* (literary: `করিতেছি`, `বলিবেন`), which is the classic machine-translation register and sounds like a 19th-century document. |
| **Politeness** | **আপনি** + the `-উন` honorific imperative (বলুন, শুনুন, দেখুন). `তুমি` only for children/intimates. **দাদা / দিদি** is very natural for addressing a stranger. |
| **Numbers as words** | `2 থেকে 3` → "দুই থেকে তিন"; `350–400` → "সাড়ে তিনশো থেকে চারশো". |
| **Money (worked)** | `₹13,000–₹17,000` → "তেরো হাজার থেকে সতেরো হাজার টাকা"; `₹500/day` → "দিনে পাঁচশো টাকা". |
| **Phone (worked)** | "নয়, আট, সাত, ছয়, পাঁচ, চার, তিন, দুই, এক, জিরো" — **জিরো** in speech; শূন্য is bookish. |
| **Dates / times** | `29/01/2026` → "উনত্রিশে জানুয়ারি দুই হাজার ছাব্বিশ". Day-parts: সকালে / দুপুরে / বিকেলে / রাতে. |
| **English code-mixing** | **HIGH.** চাকরি is the natural native word for "job"; জব, অ্যাপ্লাই, ইন্টারভিউ, স্যালারি, কোম্পানি, অফিস are all normal in speech. |
| **Honorifics / address** | আপনি; বাবু after a male name is older-register; দাদা / দিদি / ভাই / বোন in everyday use. |
| **Greeting / farewell** | **Religiously marked — decide with the owner.** `নমস্কার` reads Hindu-leaning; `আসসালামু আলাইকুম` Muslim-leaning (and the default in Bangladesh). For a neutral government/service bot in West Bengal, `নমস্কার` or a plain "হ্যালো" + self-introduction is the safer opener. Close: ধন্যবাদ / "আচ্ছা, রাখছি". `[needs native review]` — and needs a product decision, not just a linguistic one. |
| **"or" for "/"** | অথবা / বা. |
| **Place names for examples** | কলকাতা, হাওড়া, দুর্গাপুর, আসানসোল, শিলিগুড়ি, বর্ধমান, মুর্শিদাবাদ, খড়গপুর. |
| **TTS / ASR pitfalls** | **Orthography ≠ pronunciation**: inherent `অ` is often realised as "o" (`মন` = "mon"), so a TTS voice and a naive transliteration disagree. য-ফলা / ব-ফলা conjuncts and ৎ (khanda-ta) are frequent corruption points. শ / ষ / স are commonly all read "sh" — avoid minimal pairs in critical fields. Bengali numerals ০–৯ must never be emitted. |

---

## Gujarati — ગુજરાતી (`gu`)

| | |
|---|---|
| **Script** | Gujarati script only. |
| **Register** | Spoken Gujarati, polite **તમે**. Urban Gujarati speech is heavily English-mixed; do not "purify" it. |
| **Numbers as words** | `2 થી 3` → "બે થી ત્રણ"; `350–400` → "ત્રણસો પચાસ થી ચારસો". |
| **Money (worked)** | `₹13,000–₹17,000` → "તેર હજારથી સત્તર હજાર રૂપિયા"; `₹500/day` → "દિવસના પાંચસો રૂપિયા". |
| **Phone (worked)** | "નવ, આઠ, સાત, છ, પાંચ, ચાર, ત્રણ, બે, એક, ઝીરો" — **ઝીરો** in speech; શૂન્ય is bookish. |
| **Dates / times** | `29/01/2026` → "ઓગણત્રીસ જાન્યુઆરી બે હજાર છવ્વીસ". Day-parts: સવારે / બપોરે / સાંજે / રાત્રે. |
| **English code-mixing** | **VERY HIGH.** જોબ, અપ્લાય, ઇન્ટરવ્યૂ, સેલરી, કંપની, ઓફિસ, સ્કિલ, ઓપ્શન. |
| **Honorifics / address** | **ભાઈ / બહેન suffixed to the name is the defining register marker** — રમેશભાઈ, સવિતાબહેન. Using it makes the bot sound local; omitting it sounds cold. તમે + `-ો` imperative (કહો, સાંભળો). |
| **Greeting / farewell** | નમસ્તે (neutral); "કેમ છો?" is the natural warm opener. **`જય શ્રી કૃષ્ણ` is religiously marked — avoid for a neutral government/service bot.** Close: આભાર + નમસ્તે. |
| **"or" for "/"** | અથવા. |
| **Place names for examples** | અમદાવાદ, સુરત, વડોદરા, રાજકોટ, ભાવનગર, જામનગર, ગાંધીનગર, જૂનાગઢ. |
| **TTS / ASR pitfalls** | ઍ / ઑ carry English vowels — using the plain એ/ઓ mispronounces loanwords. ASR confuses છ / શ / સ and the retroflex ળ / ડ. Gujarati numerals must never be emitted. Voice availability is thinner than for Hindi — confirm the voice before promising a launch date. |

---

## Punjabi — ਪੰਜਾਬੀ (`pa`)

| | |
|---|---|
| **Script** | **Gurmukhi** for Indian Punjab. (Pakistani Punjabi uses Shahmukhi, Perso-Arabic — a different file entirely.) Record the script choice explicitly in the QA record. |
| **Register** | Spoken Punjabi, polite **ਤੁਸੀਂ** + `-ਓ` imperative (ਦੱਸੋ, ਸੁਣੋ, ਕਰੋ). **The particle `ਜੀ` is essential** — "ਹਾਂ ਜੀ", "ਦੱਸੋ ਜੀ", "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਜੀ". Omitting ਜੀ sounds curt to the point of rude. |
| **Numbers as words** | `2 ਤੋਂ 3` → "ਦੋ ਤੋਂ ਤਿੰਨ"; `350–400` → "ਤਿੰਨ ਸੌ ਪੰਜਾਹ ਤੋਂ ਚਾਰ ਸੌ". |
| **Money (worked)** | `₹13,000–₹17,000` → "ਤੇਰਾਂ ਹਜ਼ਾਰ ਤੋਂ ਸਤਾਰਾਂ ਹਜ਼ਾਰ ਰੁਪਏ"; `₹500/day` → "ਦਿਹਾੜੀ ਦੇ ਪੰਜ ਸੌ ਰੁਪਏ" (ਦਿਹਾੜੀ = daily wage, the natural word for wage-work) `[needs native review]`. |
| **Phone (worked)** | "ਨੌਂ, ਅੱਠ, ਸੱਤ, ਛੇ, ਪੰਜ, ਚਾਰ, ਤਿੰਨ, ਦੋ, ਇੱਕ, ਜ਼ੀਰੋ" — **ਜ਼ੀਰੋ** in speech; ਸਿਫ਼ਰ is bookish. |
| **Dates / times** | `29/01/2026` → "ਉਨੱਤੀ ਜਨਵਰੀ ਦੋ ਹਜ਼ਾਰ ਛੱਬੀ" `[needs native review]`. Day-parts: ਸਵੇਰੇ / ਦੁਪਹਿਰੇ / ਸ਼ਾਮ / ਰਾਤ. |
| **English code-mixing** | **HIGH.** ਜੌਬ, ਅਪਲਾਈ, ਇੰਟਰਵਿਊ, ਸੈਲਰੀ, ਕੰਪਨੀ, ਆਫਿਸ. |
| **Honorifics / address** | ਤੁਸੀਂ + ਜੀ; ਭਾਈ ਸਾਹਬ / ਬੀਬੀ ਜੀ; ਵੀਰ ਜੀ / ਭੈਣ ਜੀ are warm and natural. |
| **Greeting / farewell** | **`ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ`** is the standard Punjabi greeting in Indian Punjab (Sikh-origin but in general use); `ਨਮਸਤੇ` also occurs. **Religiously marked → needs a product decision for a mixed audience** `[needs native review]`. Close: ਧੰਨਵਾਦ + ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ. |
| **"or" for "/"** | ਜਾਂ. |
| **Place names for examples** | ਲੁਧਿਆਣਾ, ਅੰਮ੍ਰਿਤਸਰ, ਜਲੰਧਰ, ਪਟਿਆਲਾ, ਬਠਿੰਡਾ, ਮੋਹਾਲੀ, ਪਠਾਨਕੋਟ. |
| **TTS / ASR pitfalls** | **Punjabi is tonal** — the historical voiced aspirates (ਘ ਝ ਢ ਧ ਭ) are realised as tone, and TTS quality on tone varies a lot; a wrong tone can change the word. Nukta letters (ਜ਼ ਸ਼ ਫ਼ ਖ਼ ਗ਼) matter for Perso-Arabic loanwords and are frequently dropped in data. Voice/ASR maturity is below the big four — budget extra read-back confirmations on numbers. |

---

## Odia — ଓଡ଼ିଆ (`or`)

| | |
|---|---|
| **Script** | Odia script only. Note the nukta letters **ଡ଼ / ଢ଼** — even the language's own name carries one (ଓଡ଼ିଆ). Getting these wrong is a visible machine-translation tell. |
| **Register** | Spoken Odia, polite **ଆପଣ** + `-ନ୍ତୁ` imperative (କୁହନ୍ତୁ, ଶୁଣନ୍ତୁ). `ତୁମେ` is semi-formal/familiar — probably too familiar for a stranger `[needs native review]`. |
| **Numbers as words** | `2 ରୁ 3` → "ଦୁଇରୁ ତିନି"; `350–400` → "ତିନି ଶହ ପଚାଶରୁ ଚାରି ଶହ". |
| **Money (worked)** | `₹13,000–₹17,000` → "ତେର ହଜାରରୁ ସତର ହଜାର ଟଙ୍କା"; `₹500/day` → "ଦିନକୁ ପାଞ୍ଚ ଶହ ଟଙ୍କା". |
| **Phone (worked)** | "ନଅ, ଆଠ, ସାତ, ଛଅ, ପାଞ୍ଚ, ଚାରି, ତିନି, ଦୁଇ, ଏକ, ଜିରୋ" — **ଜିରୋ** likely more natural than ଶୂନ୍ୟ `[needs native review]`. |
| **Dates / times** | `29/01/2026` → "ଅଣତିରିଶ ଜାନୁଆରୀ ଦୁଇ ହଜାର ଛବିଶ" `[needs native review]`. Day-parts: ସକାଳେ / ଦିନେ / ସନ୍ଧ୍ୟାରେ / ରାତିରେ `[needs native review]`. |
| **English code-mixing** | **MODERATE–HIGH.** ଚାକିରି is the natural native word for "job"; ଆପ୍ଲାଏ, ଇଣ୍ଟରଭିୟୁ, ସାଲାରୀ, କମ୍ପାନୀ, ଅଫିସ୍ are normal in speech `[needs native review]` on the exact spellings. |
| **Honorifics / address** | ଆପଣ; ବାବୁ after a male name (older register); ଭାଇ / ଅପା; ସାର୍ / ମାଡାମ୍ common. |
| **Greeting / farewell** | ନମସ୍କାର. Close: ଧନ୍ୟବାଦ + ନମସ୍କାର. |
| **"or" for "/"** | କିମ୍ବା. |
| **Place names for examples** | ଭୁବନେଶ୍ୱର, କଟକ, ରାଉରକେଲା, ବ୍ରହ୍ମପୁର (Berhampur), ସମ୍ବଲପୁର, ପୁରୀ, ବାଲେଶ୍ୱର. |
| **TTS / ASR pitfalls** | **TTS/ASR maturity is thin.** Expect worse ASR on numbers and names → add read-back confirmations beyond the master's. Odia conjuncts are heavily ligatured and can render wrong in some fonts/voices. Odia numerals ୦–୯ must never be emitted. Confirm a genuine Odia voice exists on the platform **before** committing to this language. Most of this section is `[needs native review]`. |

---

## Assamese — অসমীয়া (`as`)

| | |
|---|---|
| **Script** | Assamese script = the Bengali script **plus ৰ (ra) and ৱ (wa)**. **Using Bengali র / ব instead of ৰ / ৱ is the single clearest sign a file was machine-translated from Bengali.** Grep the finished file for `র` and `ব` in Assamese words and fix every one. |
| **Register** | Spoken Assamese; honorific **আপুনি** with its own verb forms (কওক = "say", শুনক = "listen"); `তুমি` familiar; `তই` intimate/rude — never to a caller `[needs native review]`. |
| **Numbers as words** | `2 ৰ পৰা 3` → "দুইৰ পৰা তিনি"; `350–400` → "তিনি শ পঞ্চাশৰ পৰা চাৰি শ" `[needs native review]`. |
| **Money (worked)** | `₹13,000–₹17,000` → "তেৰ হাজাৰৰ পৰা সোতৰ হাজাৰ টকা"; `₹500/day` → "দিনে পাঁচ শ টকা" `[needs native review]`. |
| **Phone (worked)** | "ন, আঠ, সাত, ছয়, পাঁচ, চাৰি, তিনি, দুই, এক, জিৰো" `[needs native review]` — including whether ন or নয় is used for 9 in digit-reading. |
| **Dates / times** | `[needs native review]` — do not guess the spoken date order. Day-parts: ৰাতিপুৱা / দুপৰীয়া / আবেলি / ৰাতি `[needs native review]`. |
| **English code-mixing** | **MODERATE–HIGH.** চাকৰি (job), এপ্লাই, ইন্টাৰভিউ, চেলাৰী, কোম্পানী `[needs native review]` on spellings — note Assamese renders English "s" with চ, reflecting its pronunciation. |
| **Honorifics / address** | আপুনি; ডাঙৰীয়া (formal, may be too formal); ককাইদেউ / বাইদেউ for elder brother/sister `[needs native review]`. |
| **Greeting / farewell** | নমস্কাৰ. Close: ধন্যবাদ + নমস্কাৰ. |
| **"or" for "/"** | বা / অথবা. |
| **Place names for examples** | গুৱাহাটী, ডিব্ৰুগড়, শিলচৰ, জোৰহাট, তেজপুৰ, নগাঁও, তিনিচুকীয়া. |
| **TTS / ASR pitfalls** | **Assamese `স / শ / ষ` are all pronounced as a velar fricative /x/: a Bengali voice reading Assamese text pronounces them wrong, audibly, on every occurrence.** Confirm the platform has a genuinely Assamese voice, not a Bengali one, before committing (`/translate-prompt` step 11). Lowest TTS/ASR maturity of this set: expect weak number ASR and add extra read-backs. **Treat this whole section as provisional; a native reviewer is effectively mandatory here.** |

---

## Urdu — اُردُو (`ur`)

| | |
|---|---|
| **Script** | Perso-Arabic (Nastaliq), **right-to-left**. |
| **Register** | For a low-literacy phone audience, spoken Urdu and spoken Hindi are near-identical — the difference is the **script** and a lexical lean toward Persian/Arabic loanwords. **Do not reach for heavy Persianised vocabulary**; use the everyday word people actually say (bug D1 applies in mirror image: over-Persianising is Urdu's version of over-Sanskritising). |
| **Politeness** | **آپ** + `یے`/`یں` imperative (بتائیے / بتائیں، سنیے / سنیں). The particle **جی** ("جی ہاں") carries politeness, as in Hindi/Punjabi. |
| **Numbers as words** | `2 سے 3` → "دو سے تین"; `350–400` → "تین سو پچاس سے چار سو". |
| **Money (worked)** | `₹13,000–₹17,000` → "تیرہ ہزار سے سترہ ہزار روپے"; `₹500/day` → "دن کے پانچ سو روپے". |
| **Phone (worked)** | "نو، آٹھ، سات، چھ، پانچ، چار، تین، دو، ایک، زیرو" — **زیرو** in speech; صفر is bookish. |
| **Dates / times** | `29/01/2026` → "انتیس جنوری دو ہزار چھبیس". Day-parts: صبح / دوپہر / شام / رات. |
| **English code-mixing** | **HIGH.** جاب، اپلائی، انٹرویو، سیلری، کمپنی، آفس، اسکل. |
| **Honorifics / address** | آپ; صاحب / صاحبہ; بھائی / بہن; میڈم / سر common. |
| **Greeting / farewell** | **`السلام علیکم`** is the default for Urdu-speaking audiences; **`آداب`** is the neutral, secular alternative and is the safer choice for a government/service bot with a mixed audience. Close: شکریہ; خدا حافظ / اللہ حافظ (the latter is more religiously marked). **Needs a product decision, not just a linguistic one** `[needs native review]`. |
| **"or" for "/"** | یا. |
| **Place names for examples** | (India) لکھنؤ، حیدرآباد، دہلی، بھوپال، علی گڑھ، مراد آباد، رام پور. |
| **TTS / ASR pitfalls** | **Bidi hazard — this one bites in the editor, not on the call.** An RTL Urdu spoken line on the same source line as English instruction text can *display* reordered, so you edit the wrong characters and a diff looks clean when it isn't. **Keep every Urdu spoken line on its own line**, and verify changes with a byte-level `diff` / `grep -c`, never by eye. Short vowels (zabar/zer/pesh) are normally unwritten, so TTS mispronounces ambiguous words — add diacritics on critical words (names, numbers, place names) and confirm in the first live call. Urdu-Indic digits ۱۲۳ must never be emitted. **Urdu ASR frequently returns Devanagari or Roman output** — the prompt's script rule must state the expected script explicitly, and the read-back logic must survive a transliterated ASR result. |

---

## Adding a language that is not in this file

Do not improvise inline. Before translating, add **both**: a section here (template below, heading
format exactly as shown), and an entry for the ISO code in `raya/translations/lexicon.json` (copy an
existing entry's keys: `name`, `aliases`, `script`, `range`, `question`, `gender`, `formal`,
`min_terms_everyday`, `denylist`, `hindi_markers`, `review: "needs-native"`). `speech_split.py` and
`language_checks.py` stop with `KeyError` on a code the lexicon does not have, and without a matrix
section the translators get no spoken-form conventions and produce a literal translation.

```markdown
## <English name> — <endonym> (`<iso-639-1>`)

| | |
|---|---|
| **Script** | |
| **Register for a low-literacy phone audience** | (incl. the diglossia trap, if any) |
| **Politeness** | (polite pronoun, verb ending, particle) |
| **Numbers as words** | |
| **Money (worked)** | range example + per-day rate example |
| **Phone (worked)** | full digit-by-digit read, incl. the zero-word people actually say |
| **Dates / times** | long spoken date + the four day-part words |
| **English code-mixing** | level + the natural loanwords, in-script |
| **Honorifics / address** | |
| **Greeting / farewell** | flag anything religiously or regionally marked |
| **"or" for "/"** | |
| **Place names for examples** | 6–8 real places from that language's region |
| **TTS / ASR pitfalls** | script hazards, confusable phonemes, voice availability |
```

Fill what you know, mark the rest **`[needs native review]`**, and say in your report which cells are
provisional. A flagged gap is useful; a confident guess about someone's language is a liability.
