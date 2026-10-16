# AI-Agent-Prompts
Prompts of all Bluedots network

## What is here

- **`Blue Dots/`**: the live voice-bot prompts for the employment rail: KKB (job seekers), DKB (employers), Maya (campus recruitment), TRRAIN (follow-up offers) and KKB-Slim. One file per language, plus each bot's memory and output prompts.
- **`Orange Dots/`**: prompts for the Orange Dots rail.
- **`Prompt Tuner/`**: the toolkit we use to build, translate, test and maintain these bots on Raya. Open that folder in Claude Code and its skills are available (`/onboard`, `/register-bot`, `/update-prompt`, `/translate-prompt`, `/generate-test-cases`, `/voice-test` and more). Start with `Prompt Tuner/docs/WHAT-YOU-CAN-ASK.md`, then `Prompt Tuner/docs/WORKFLOW.md`.

## Using the Prompt Tuner for your own bot

1. Open `Prompt Tuner/` in Claude Code.
2. Add your Raya credentials to `raya/.env` (copy `raya/.env.example`; this file is never committed).
3. Say "I have a voice bot I want to build" (or run `/onboard`) and share your use-case document.

Phone numbers in this repository are masked (`XXXXXX1234`); test fixtures use the `9188888888xx` block.
