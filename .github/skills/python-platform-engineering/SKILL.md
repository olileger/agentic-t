---
name: python-platform-engineering
description: Use when building or maintaining Python developer environments, packaging, CI, artifacts, releases, and operational foundations.
---

# Python platform engineering

## Method

1. Inspect `pyproject.toml`, dependency and lock files, supported Python
   versions, build backend, CI workflows, artifact formats, and release process.
2. Define one reproducible path for local setup, validation, packaging, and
   release.
3. Keep developer commands and CI behavior aligned.
4. Build and test the relevant Python and operating-system matrix.
5. Make caching an optimization only; cache misses or invalidation must not
   change correctness.
6. Verify package metadata, installation, entry points, included files, and
   clean-environment execution.
7. Produce immutable, versioned artifacts and document promotion and rollback.
8. Provide concise diagnostics, logs, and operational signals for failures.

## Python platform expertise

- Follow Python packaging standards and the build backend already selected by
  the repository.
- Prefer isolated, non-interactive, deterministic builds.
- Keep runtime, development, test, and release dependencies intentionally
  scoped.
- Support Windows and Linux without maintaining divergent release processes
  unless platform-specific artifacts require it.
- Treat native extensions, wheels, file permissions, line endings, executable
  entry points, and external system libraries as explicit compatibility risks.
- Use versioning and changelog conventions already adopted by the project.

## Quality rules

- Do not publish or deploy without explicit authorization.
- Do not ignore command failures or mark required checks as optional to obtain a
  green build.
- Do not introduce a second package manager, build backend, or release path
  without a migration decision.
- Do not rely on developer-global state or undeclared tools.
- Keep secrets out of commands, logs, artifacts, and caches.
