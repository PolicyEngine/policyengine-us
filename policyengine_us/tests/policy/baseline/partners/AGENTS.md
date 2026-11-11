# Partner API contract tests

This directory holds API partner contract tests. Never rewrite an expected value here merely to make CI pass: a failing case may mean partners see a changed answer.

Follow [Partner API contract tests](../../../../../CLAUDE.md#partner-api-contract-tests) before you edit any file here. In short:

- Anyone, agents and subagents included, may update an expected value when a cited model change in the same PR explains every changed value; the PR body tables every changed value (file, case, variable, old value, new value, cause), computed from every output variable of each affected case, because the test runner stops a case at its first failing variable; an independent review recomputes the values from the cited source; and the PR tags Ziming Hua (`hua7450`) with the table as an FYI.
- Ziming approves first, through the three-question checklist, any change to a case's inputs or name, any added or removed case or output variable, a case whose purpose the model change defeats (such as a boundary case that leaves its boundary), any changed value the review can't trace, and any case marked `# partner-flagged`.
