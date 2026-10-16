# `agent_args` files for live test calls

Every live test call needs an **`agent_args` JSON file** — the inputs the bot would receive on a real
production call. Without it the bot runs with empty variables and you end up "testing" a flow that
never happens in production.

```bash
python3 scripts/raya_testrun.py <bot_uuid> <tester_10digit_DID> <this_args_file> <tester_uuid> "<label>"
```

## How to build one for a bot you have never tested

**Do not guess the shape — copy it from a real call.** Read a known-good past call for that agent:

```bash
python3 scripts/raya_call.py <bot_uuid> 3
```

That prints `agent_args:` with every key and value the platform actually sent (it prints the full
dict, so nothing is hidden). Copy those keys into a new file here, named `<bot-id>-<scenario>.json`
— e.g. `kkb-kn-out-returning.json`, `pd-hi-out-new.json`.

If the bot has never run, get the arg names from its prompt's **Input Variables** section: every
`${variable}` the prompt reads must appear in the args, or the bot will improvise around an empty value.

## Two things that surprise everyone

1. **The tester never receives `agent_args`.** They reach the `agent_id` you pass to `POST /api/call`
   — i.e. the bot under test — only. So you cannot select a persona or scenario per call through
   args; the tester's behaviour is swapped by PATCHing its prompt
   (`scripts/raya_testcall.py persona ...`).
2. **The bot looks up the DIALLED number,** not any phone number you put in the args.
   `${contact_phone}` binds to `to_number` (the tester's DID). To test a "returning caller", the
   backend record must exist **under the tester's number**. Signals has no delete route, so once a
   profile exists for that number it cannot be reset to "new".

## Files here

- `example.json` — an annotated template (the `_comment*` keys are ignored by the platform; strip
  them if you prefer). Modelled on a real KKB Signals outbound call.
