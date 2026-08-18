---
name: python-engineering
description: Use when designing, implementing, debugging, testing, reviewing, or optimizing production Python software.
---

# Python engineering

## Method

1. Inspect `pyproject.toml`, dependency files, supported Python versions, source
   layout, tests, and configured quality tools before changing code.
2. Follow the repository's established architecture, naming, formatting, and
   dependency-management conventions.
3. Model responsibilities with cohesive modules and small, explicit public APIs.
4. Use precise type annotations and narrow data models at system boundaries.
5. Validate external input and surface actionable errors without leaking secrets.
6. Write deterministic tests for normal behavior, edge cases, and failure paths.
7. Use the smallest configured formatter, linter, type checker, and test command
   that covers the change.
8. Optimize only after identifying a real bottleneck, then measure the result.

## Python expertise

- Write idiomatic modern Python using context managers, iterators, comprehensions,
  protocols, dataclasses, and standard-library utilities where they improve clarity.
- Prefer composition and simple functions over deep inheritance or speculative
  abstractions.
- Keep imports acyclic and package boundaries explicit.
- Use `pathlib`, timezone-aware datetimes, explicit encodings, and safe resource
  lifecycle management.
- Distinguish synchronous, threaded, multiprocessing, and `asyncio` workloads;
  never block an event loop with synchronous I/O.
- Preserve exception context, catch only errors that can be handled meaningfully,
  and define domain exceptions only when callers need stable failure semantics.
- Treat mutable defaults, shared state, serialization, subprocesses, SQL, file
  paths, and untrusted input as correctness and security boundaries.
- Maintain compatibility with the Python versions and dependency constraints
  declared by the project.

## Agentic solutions

- Use Microsoft Agent Framework for any Python implementation that requires AI
  agents, tool-using agents, multi-agent coordination, or agentic workflows.
- Install and import the official `agent-framework` package; verify current
  package names and APIs against Microsoft Learn before coding because the
  framework evolves.
- Use an agent for open-ended reasoning or autonomous tool use. Use an Agent
  Framework `Workflow` when execution order, multiple participants,
  checkpoints, durable state, or human approval must be controlled explicitly.
- Prefer deterministic Python functions over agents when ordinary code can
  solve the requirement reliably.
- Do not combine Microsoft Agent Framework with AutoGen, Semantic Kernel,
  LangGraph, CrewAI, or another orchestration framework unless a documented
  incompatibility requires an exception approved by a human Tech Lead.
- Preserve explicit authorization boundaries, typed inputs and outputs,
  observability, resumability, idempotency, and auditable human-in-the-loop
  decisions.

## Quality rules

- Do not use bare `except`, broad exception swallowing, or success-shaped
  fallbacks.
- Do not use `Any`, unchecked casts, global mutable state, monkey-patching, or
  reflection to bypass a design or typing problem without documented necessity.
- Do not add a dependency when the standard library or an existing dependency
  provides a clear solution.
- Do not mix unrelated refactoring with a behavioral change.
- Tests must assert externally meaningful behavior, not implementation details.
- Public APIs, configuration changes, migrations, and operational requirements
  must be documented when they change.
