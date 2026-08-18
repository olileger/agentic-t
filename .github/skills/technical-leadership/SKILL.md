---
name: technical-leadership
description: Use when evaluating technical feasibility, architecture impact, non-functional requirements, dependencies, risks, and implementation readiness for a product request.
---

# Technical leadership

## Method

1. Inspect the repository and cite relevant existing components.
2. Translate functional behavior into system responsibilities and boundaries.
3. Evaluate the smallest viable direction plus meaningful alternatives.
4. Assess security, privacy, safety, reliability, observability, performance,
   cost, and operability.
5. Identify API, data, integration, migration, and compatibility impacts.
6. Expose unknowns requiring a spike or architecture decision record.
7. Classify risks by impact and mitigation.
8. State whether the request is ready for implementation planning.

## Quality rules

- Separate repository facts from inferred or proposed architecture.
- Never claim feasibility without identifying material constraints.
- For trading behavior, prioritize safety rails, auditability, idempotency, and
  human-controlled authorization.
- Do not write implementation code during discovery.
- Reserve consequential architecture decisions for human approval.
