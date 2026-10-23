# What you can ask the Prompt Tuner

The Prompt Tuner looks after voice bots: it builds them, tests them by phoning them with another AI,
fixes what goes wrong, and takes them into new languages. You do not need to know any commands. Open
Claude in this folder and say what you want in a normal sentence. A few examples of what works:

## Starting with a bot

- "I have a voice bot I want to improve." (it asks you a few questions, one at a time)
- "Here is our bot's prompt and the three problems callers complain about."
- "What does the Orange Dots bot do, and what is still broken on it?"

## Testing

- "Make the test cases for this bot." You get a Google Sheet with the exact words a tester should say,
  the exact line the bot should say back, and how to tell pass from fail.
- "Run the test cases in this sheet, three calls each, and fill in the results." (paste the sheet link;
  if it says it cannot open the sheet, share the sheet with
  `kkb-sheets-writer@operation-rozgar.iam.gserviceaccount.com` as an editor)
- "Test the Marathi bot on the safety case." (a caller who says they do not want to live)
- "Set up a nightly test run and email me the results at <your email>." (the laptop has to stay on for
  live calls; the written checks run in the cloud)

## Fixing

- "The bot keeps reading ages out as digits. Fix it." It finds a real call that shows the problem
  first, fixes the prompt, places a test call, and tells you the call id that proves it.
- "Fix the open issues on the tracker."
- "Show me exactly what you changed in the prompt." It shows the few lines before and after.

## Languages

- "Take the Hindi bot into Telugu." It checks the prompt will not get too large first, translates only
  the words the bot speaks (never the rules or tool calls), checks the result, and tests it.
- "Check the Kannada version against the Hindi one."
- "Make a review sheet for a native Marathi speaker." Safety lines come first.

## When something will not get fixed

- "Which part of the prompt made the bot say this?" (give the call id). It walks the call turn by turn
  and names the section each line came from, so you can see where it went wrong first.
- "If I change the location step, what else could break?" It lists the other rules that point at it,
  the steps that use what it collects, the same step in the other languages, and the test rows to re-run.

- "Look at this prompt fresh, as if you had never seen it." If a fix has failed twice, the tuner reads
  the whole prompt cold (no memory of the earlier attempts) and checks that every "go to step N" lands
  where it says. A wrong step number once sent a bot to the wrong question for hours of fixing.
- `/goal every Smoke row in this sheet passes on 3 calls, or stop after 25 turns` keeps it fixing and
  testing on its own until the condition is met. End the sentence with a stop.

## Keeping your copy of the tuner up to date

- "/upgrade" (or "upgrade the prompt tuner"). If your team runs its own copy, this pulls the newest
  skills and scripts from the main tuner and merges them in. Your bots, sheets and settings are never
  touched. Run it in each copy.

## Two Raya accounts

- "Copy the Purple Dots inbound agent from the EkStep account to the ALIMCO account." Each account's key
  goes in `raya/.env`; the language and voice ids for the new account are recorded once in
  `raya/voices.json` first.

## Asking about results

- "What is still open on this bot?"
- "Why did that call fail?" (give the call id or the time and the last four digits of the number)
- "Explain that in simpler words." Always fine to ask.

## Three things that are always true

1. **"Fixed" comes with a call id.** If you are told something is fixed, you are also told which call
   proves it. Otherwise it says "deployed, not yet verified".
2. **Every language is tested on its own.** A fix that works in Hindi is not assumed to work in Kannada.
3. **Real people's phone numbers are never used for testing.** Only test numbers.

For the full step-by-step picture (for whoever maintains the tuner), see `docs/WORKFLOW.md`.
