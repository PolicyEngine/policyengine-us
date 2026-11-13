# Partner API contract tests

The YAML files in this directory are API partner contract tests. Never rewrite an expected value merely to make CI pass. Treat a model-caused failure as a possible change to what partners see.

Follow [Partner API contract tests](../../../../../CLAUDE.md#partner-api-contract-tests) before editing them.

Use one designated editor for each partner test file. The coordinator assigns files to agents or teammates; avoid conflicting parallel writes.

Before editing partner tests:

- Identify the causal model change and derive every changed expected value from primary sources independently of the implementation.
- Table every changed value in the PR: file, case, variable, old value, new value and source justification. Compute every output variable of each affected case; the test runner stops at the first failure and can hide other changed outputs. Explain the partner-facing impact and why the change is intentional.
- Check affected boundary cases, failing or not. Compare parameter trees and formula-derived thresholds at the base and head for the cases' periods; uprating can move values outside the diff. Check each case whose name or own comments place it at, just above or just below a moved value. Preserve its stated purpose and justify any input or coverage change from the source. Check partner-flagged cases and any dependency a partner identified in the PR; resolve the compatibility question before merging.
- Preserve the pre-change failing results as evidence. Do not delete, skip, rename or loosen a case merely to make CI pass.

Before merging, obtain independent automated review at the current head from a fresh reviewer who neither made the model change nor edited the expectations. The reviewer recomputes each changed value from the primary source, checks every changed output and confirms that the diff contains only the intended expectation, input, eligibility and coverage changes. Rerunning the changed model alone does not supply an independent expected value. Pass all required CI checks at the current head.

Request human review only for a specific material open question that requires that person's expertise, and name the question in the request. Resolve any source conflict, untraced value or partner compatibility question before merging. Do not request human review or notify a person to keep them informed or because they own the area.
