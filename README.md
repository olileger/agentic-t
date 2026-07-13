# agentic-t

An agentic trading system for personal use that can invest on behalf of the user in user-approved markets and tickers.

## Project goal

Build a full end-to-end trading workflow where an autonomous agent can:

1. Understand user investment preferences and constraints.
2. Restrict execution to an explicit allowlist of markets and tickers.
3. Generate and execute investment decisions on the user's behalf.
4. Keep an auditable decision and execution trail for every trade.

## Scope baseline

This repository is the starting point for implementing:

- **Market scope control**: only configured markets are tradable.
- **Ticker scope control**: only configured tickers are tradable.
- **Agentic execution**: autonomous decision + order execution loop.
- **Personal-use safety rails**: position limits, risk checks, and logging.
