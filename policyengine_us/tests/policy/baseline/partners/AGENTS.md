# Partner API contract tests

This directory contains API partner contract tests.

Do not rewrite expected outputs here merely to match changed model behavior or make CI pass. A failure in this directory is evidence of a possible partner-facing API change.

Use one designated editor for each partner test file. The coordinator assigns files to agents or teammates; avoid conflicting parallel writes.

Before changing these tests:

- Identify the causal model change and derive the expected outputs from primary sources independently of the implementation.
- Document each changed case, its old and new expected values, and the source justification in the PR. Explain the partner-facing impact to the user and why the contract change is intentional.
- Preserve the pre-change failing results as evidence.

Before merging, obtain independent automated review of the source derivation, expected outputs, and partner impact at the current head, and pass all required CI checks.

Request human review only for a specific material open question that requires that person's expertise, and name the question in the request. Do not request human review or notify a person to keep them informed or because they own the area.
