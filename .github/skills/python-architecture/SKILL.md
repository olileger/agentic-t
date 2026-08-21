---
name: python-architecture
description: Use when defining or reviewing Python system boundaries, contracts, dependency direction, architecture decisions, and evolution strategy.
---

# Python architecture

## Method

1. Inspect the existing package layout, entry points, public APIs, persistence,
   integrations, deployment model, and dependency graph.
2. Translate required behavior into cohesive responsibilities and explicit
   system boundaries.
3. Define dependency direction, ownership of state, failure semantics, and
   typed contracts between components.
4. Prefer the smallest architecture that satisfies current requirements while
   preserving identified extension points.
5. Evaluate synchronous, asynchronous, event-driven, and workflow-based designs
   against actual reliability and operability needs.
6. Record consequential, cross-cutting, costly, or difficult-to-reverse choices
   as Architecture Decision Record candidates.
7. Identify compatibility, migration, rollout, rollback, and deprecation needs.
8. Validate the design against security, testability, observability,
   performance, and Windows/Linux constraints.

## Python architecture expertise

- Prefer cohesive packages, explicit public APIs, dependency inversion at
  external boundaries, and composition over framework-driven inheritance.
- Keep domain logic independent from transport, storage, operating-system, and
  vendor-specific adapters.
- Treat processes, threads, event loops, files, databases, networks, and agent
  workflows as explicit consistency and failure boundaries.
- Use typed data models for external and inter-component contracts.
- Avoid shared mutable global state and import cycles.
- For agentic workflows, use Microsoft Agent Framework and prefer `Workflow`
  when ordering, checkpoints, durable state, multiple participants, or human
  approval must be explicit.

## Quality rules

- Separate repository facts, assumptions, recommendations, and human decisions.
- Do not introduce services, queues, repositories, plugins, or abstraction
  layers without a concrete current requirement.
- Do not encode product rules in infrastructure adapters.
- Do not claim portability without identifying operating-system boundaries.
- Preserve backward compatibility unless a breaking change and migration are
  explicitly approved.
