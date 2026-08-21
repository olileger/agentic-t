---
name: cross-platform-python
description: Use when designing, implementing, testing, packaging, or operating Python software that must behave consistently on Windows and Linux.
---

# Cross-platform Python

## Method

1. Identify every operating-system boundary affected by the change.
2. Use platform-neutral standard-library APIs and existing project abstractions
   where they provide equivalent behavior.
3. Define intentional platform differences explicitly instead of relying on
   incidental behavior.
4. Test shared behavior on Windows and Linux and add platform-specific tests
   only where semantics genuinely differ.
5. Verify installation, execution, cleanup, error reporting, and cancellation
   on the supported platform matrix.

## Platform boundaries

- Use `pathlib` and never construct filesystem paths with hard-coded
  separators.
- Treat path case sensitivity, reserved names, drive letters, UNC paths,
  symlinks, permissions, and atomic replacement as platform-dependent.
- Use explicit text encodings and newline handling.
- Pass subprocess arguments as sequences. Avoid shell execution unless shell
  syntax is an explicit requirement with validated input.
- Account for differences in signals, process groups, file locking, sockets,
  temporary files, executable discovery, and console behavior.
- Use Python APIs instead of invoking platform commands when equivalent APIs
  exist.
- Keep configuration and persisted data portable unless the requirement
  explicitly scopes them to one platform.

## Quality rules

- Do not report cross-platform support from tests run on only one operating
  system.
- Do not silently skip unsupported behavior; fail with an actionable message or
  document an approved limitation.
- Do not use platform detection to mask unrelated defects.
- Avoid timing assumptions and cleanup patterns that depend on immediate file
  deletion or process termination.
