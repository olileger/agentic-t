---
name: python-testing
description: Use when planning, implementing, reviewing, or executing risk-based automated tests for Python software.
---

# Python testing

## Method

1. Trace requirements and acceptance criteria to observable behaviors and
   failure modes.
2. Inspect the configured test runner, fixtures, markers, coverage settings, and
   CI matrix before changing tests.
3. Select the lowest test level that provides sufficient confidence: unit,
   integration, contract, system, or end-to-end.
4. Cover representative normal cases, boundaries, invalid input, dependency
   failures, cancellation, recovery, and concurrency where applicable.
5. Keep tests deterministic by controlling time, randomness, external I/O, and
   mutable state at explicit boundaries.
6. Reproduce defects with a failing regression test before or alongside the
   fix.
7. Run the smallest relevant configured test set, then expand only when the
   affected boundary requires it.
8. Report residual risks that automation cannot establish.

## Python testing expertise

- Prefer public behavior over private implementation details.
- Use fixtures with narrow scope and explicit lifecycle management.
- Use fakes for stable domain collaborators and mocks at external side-effect
  boundaries; assert outcomes rather than incidental call sequences.
- Test asynchronous code without blocking the event loop.
- Isolate filesystem and environment changes and restore process state.
- Treat flaky tests as defects requiring a root-cause investigation.
- Add property-based, fuzz, performance, or soak testing only when the risk
  justifies it and compatible tooling already exists or is approved.

## Quality rules

- Do not weaken assertions, broaden tolerances, add sleeps, or retry tests to
  conceal failures.
- Do not duplicate production algorithms in expected-value calculations.
- Do not make tests depend on execution order, developer machines, public
  network availability, or real credentials.
- Coverage is supporting evidence, not a quality target by itself.
- Distinguish product defects, test defects, and environment defects.
