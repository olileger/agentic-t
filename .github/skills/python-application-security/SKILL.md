---
name: python-application-security
description: Use when threat-modeling, reviewing, testing, or hardening the application security of Python software.
---

# Python application security

## Method

1. Identify protected assets, trust boundaries, entry points, privileged
   actions, external actors, and sensitive data.
2. Describe plausible abuse cases and required attacker preconditions.
3. Trace untrusted data through validation, authorization, processing, storage,
   logging, and output.
4. Review controls at the boundary where the risk is introduced.
5. Rank findings by demonstrated impact, exploitability, exposure, and
   confidence.
6. Recommend the smallest effective mitigation that preserves intended
   behavior.
7. Add or request focused regression tests for confirmed vulnerabilities.
8. State residual risk and any control requiring human authorization or
   operational ownership.

## Python security boundaries

- Validate external input with explicit allowlists, limits, and typed schemas
  where appropriate.
- Keep authentication, authorization, and user-approved trading constraints
  separate and fail closed for consequential actions.
- Avoid dynamic code execution and unsafe deserialization.
- Treat subprocess arguments, SQL, file paths, URLs, templates, logs, and
  serialized messages as injection boundaries.
- Prevent path traversal, unsafe archive extraction, server-side request
  forgery, credential leakage, and confused-deputy behavior.
- Use cryptographic libraries and platform secret stores through established
  project abstractions; never invent cryptographic protocols.
- Preserve auditable decisions without logging secrets or unnecessary personal
  data.

## Quality rules

- Findings require concrete evidence and affected locations.
- Do not present theoretical hardening preferences as exploitable
  vulnerabilities.
- Do not expose secrets or weaponized exploit instructions in routine reports.
- Never weaken authorization, validation, safety rails, or auditability to
  improve usability.
- Do not claim compliance or certification.
