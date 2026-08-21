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
4. **Business analyst agent**: gathers business context (including website/news crawling with robots.txt compliance and rate limits) and produces structured qualitative signals.
5. **Risk agent**: validates limits (position sizing, exposure, drawdown) and blocks non-compliant intents.
6. **Ordering agent**: converts approved intents into broker orders and manages lifecycle events (submit/cancel/replace).
7. **Audit/logging agent**: stores full decision traces and execution records.

## Access rights model (Read/Write with default-deny)

Use least-privilege permissions per agent:

- **Business analyst agent**: **Read** on web/external data sources with zero external-write permissions; **Write** only to internal research artifacts.
- **Market specialist agent**: **Read** market data; **Write** market-scoring outputs.
- **Ticker specialist agent**: **Read** ticker fundamentals/price data; **Write** ticker rankings and signal outputs.
- **Risk agent**: **Read** portfolio, limits, and proposed orders; **Write** risk decisions (approve/reject/resize).
- **Ordering agent**: **Read** approved intents + account/execution state; **Write** broker order actions only.
- **Orchestrator agent**: **Read/Write** internal workflow state; no direct broker-write permissions.
- **Audit/logging agent**: **Read** all internal decision artifacts; **Write** immutable audit trails.

## Product discovery workflow

Product discovery starts through the structured **User Feedback** Issue Form and
is managed by the compiled GitHub Agentic Workflows in
`.github/workflows/product-discovery.lock.yml` and
`.github/workflows/product-refinement.lock.yml`.

1. Create a **User Feedback** issue.
2. The `user-feedback` label starts the workflow automatically.
3. The workflow coordinates the Product Owner, Business Analyst, and Tech Lead
   custom agents.
4. The agents create a draft **Product Request** labeled
   `needs-human-review`.
5. Humans add clarifications as comments on the Product Request, then post
   `/refine` to have the agents revise the existing request from those comments.
6. Humans approve product scope, business rules, and technical feasibility
   before implementation planning starts.

**Bug** issues remain outside this automatic product-discovery path. Agent
definitions live in `.github/agents/` and their reusable methods live in
`.github/skills/`. Product Requests are created only by the workflow; no public
Product Request form or blank Issue entry is available.

## Product Request implementation workflow

Implementation starts manually from an approved Product Request:

1. In GitHub, assign an Issue carrying the `product-request` label to the
   **engineering-orchestrator** custom agent.
2. The orchestrator checks that product decisions are no longer blocking,
   coordinates the Tech Lead, Senior Software Engineer, QA Engineer, Software
   Security Engineer, and Platform Engineer, and creates one dedicated branch
   and draft pull request.
3. The engineering team implements the request, adds and executes tests,
   assesses and mitigates security risks, and validates packaging and required
   Windows and Linux behavior.
4. Reviewers request further work by mentioning `@copilot` on the pull request.
   The same orchestrator continues on the existing branch, delegates the
   affected work, reruns the relevant validations, and updates the pull request.
5. Final validation, approval, marking the pull request ready, and merging
   remain manual human responsibilities.

The Product Request `/refine` command remains dedicated to product refinement.
Engineering refinement uses the native Copilot pull-request session and does
not require another Agentic Workflow.

## Engineering agents

- **engineering-orchestrator**: coordinates implementation and refinement of an
  assigned Product Request across the complete engineering team and maintains
  its draft pull request.
- **tech-lead**: combines Tech Lead and Software Architect responsibilities for
  feasibility, system boundaries, architecture decisions, non-functional
  requirements, and Windows/Linux compatibility. The existing name remains
  stable for Product Discovery workflows.
- **sr software engineer**: designs, implements, reviews, tests, and maintains
  production-grade Python software on Windows and Linux.
- **qa-engineer**: owns risk-based test strategy, automated test implementation,
  regression evidence, and cross-platform quality assessment.
- **software-security-engineer**: owns threat modeling, application-security
  review, security regression testing, and software supply-chain assessment.
- **platform-engineer**: owns reproducible setup, packaging, CI, artifacts,
  releases, and their operational and security foundations.

Technology expertise is supplied through composable skills in
`.github/skills/`. Shared skills cover Python architecture, engineering,
testing, application security, supply-chain security, platform engineering, and
cross-platform Windows/Linux behavior.
