---
name: software-supply-chain-security
description: Use when reviewing or changing dependencies, builds, CI permissions, artifacts, provenance, or release security.
---

# Software supply-chain security

## Method

1. Identify dependency manifests, lock files, package indexes, build tools, CI
   workflows, artifact stores, and release identities.
2. Minimize trusted inputs, permissions, credentials, and mutable external
   references.
3. Pin and verify build inputs according to repository conventions.
4. Separate untrusted change validation from privileged publishing and
   deployment contexts.
5. Produce reproducible artifacts with traceable source, version, and build
   metadata.
6. Assess dependency changes for maintenance, licensing, vulnerabilities,
   transitive impact, and platform availability.
7. Define artifact verification, release approval, rollback, and credential
   rotation responsibilities.

## Quality rules

- Use least-privilege workflow and token permissions.
- Never expose secrets to untrusted code, pull requests, logs, caches, or
  artifacts.
- Do not execute downloaded tools or scripts without integrity and source
  controls consistent with repository policy.
- Do not publish from an unreviewed or non-reproducible workspace.
- Do not add security scanners as ceremonial dependencies; integrate only tools
  with an owned response process and actionable output.
- Report unresolved vulnerabilities and provenance gaps explicitly.
