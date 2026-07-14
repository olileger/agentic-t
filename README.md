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

## Target agent architecture (MVP)

Recommended multi-agent layout:

1. **Orchestrator agent**: coordinates agent workflow and produces final trade intents.
2. **Market specialist agent**: analyzes allowed markets and macro/market-structure signals.
3. **Ticker specialist agent**: analyzes allowed tickers and ranks opportunities.
4. **Business analyst agent**: gathers business context (including website/news crawling) and produces structured qualitative signals.
5. **Risk agent**: validates limits (position sizing, exposure, drawdown) and blocks non-compliant intents.
6. **Ordering agent**: converts approved intents into broker orders and manages lifecycle events (submit/cancel/replace).
7. **Audit/logging agent**: stores full decision traces and execution records.

## Access rights model (RW by default-deny)

Use least-privilege permissions per agent:

- **Business analyst agent**: mostly **Read** on web/external data sources; **Write** only to internal research artifacts.
- **Market specialist agent**: **Read** market data; **Write** market-scoring outputs.
- **Ticker specialist agent**: **Read** ticker fundamentals/price data; **Write** ticker rankings and signal outputs.
- **Risk agent**: **Read** portfolio, limits, and proposed orders; **Write** risk decisions (approve/reject/resize).
- **Ordering agent**: **Read** approved intents + account/execution state; **Write** broker order actions only.
- **Orchestrator agent**: **Read/Write** internal workflow state; no direct broker-write unless explicitly enabled.
- **Audit/logging agent**: **Read** all internal decision artifacts; **Write** immutable audit trails.
