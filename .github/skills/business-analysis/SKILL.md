---
name: business-analysis
description: Use when refining a product problem into actors, workflows, domain rules, User Stories, edge cases, and testable acceptance criteria.
---

# Business analysis

## Method

1. Define actors and a consistent domain vocabulary.
2. Describe the current and desired workflows.
3. Identify triggers, preconditions, postconditions, permissions, and data rules.
4. Write User Stories as `As a ..., I want ..., so that ...`.
5. Add alternate, failure, cancellation, and recovery scenarios.
6. Express acceptance criteria as observable Given/When/Then behavior.
7. Trace every story and rule to the product problem.
8. Record unresolved questions for a human domain expert.

## Quality rules

- Acceptance criteria must be testable and implementation-independent.
- Do not invent regulatory, financial, or trading rules.
- Do not hide uncertainty behind vague terms such as "appropriate" or "fast".
- Avoid technical tasks masquerading as User Stories.
- Keep each rule uniquely identifiable when the request is complex.
