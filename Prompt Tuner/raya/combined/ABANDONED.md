# Combined ${call_direction} bots — RETIRED as an approach, agents REPURPOSED (2026-07-31)

The v1 combined inbound+outbound prompts are retired: `${call_direction}` is not injected on API-triggered
calls (open-items #12), so the branch mis-routes. Rather than delete the 5 experimental Raya agents (no
Raya delete route), we are **repurposing their uuids** as the new Signals bots (see `raya/signals-expansion/PLAN.md`):

| combined agent (uuid) | repurposed into |
|---|---|
| maya-hi-combined 904f333f | Maya Hindi Signals |
| kkb-hi-combined 3f521174  | KKB Hindi Inbound Signals |
| kkb-kn-combined f38da775  | KKB Kannada Inbound Signals |
| dkb-hi-combined fabda71d  | DKB Hindi Signals (Phase 2) |
| dkb-kn-combined 847a85e2  | DKB Kannada Signals (Phase 2) |

Each will have its instructions + tools + name PATCHed to its Signals identity. The `raya/combined/*.md`
v1 prompts are kept here for reference only — do NOT deploy them.
