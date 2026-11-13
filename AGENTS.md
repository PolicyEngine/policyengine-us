# PolicyEngine US Agent Instructions

Follow the repository guidance in `CLAUDE.md` for commands, style, changelog entries, and PolicyEngine modeling conventions.

## Test cost and CI capacity

Follow [Test design and CI cost](CLAUDE.md#test-design-and-ci-cost) before adding or expanding tests. Use variable-named YAML tests for policy calculations; reserve Python tests for behavior YAML cannot exercise. Preserve Core/data compatibility and isolation coverage, avoid repeated full-model construction, and do not add CI runners or parallel heavy processes without explicit authorization. Document the purpose and measured cost of new simulation-heavy Python tests in the PR.

## Statutes against forms, instructions and agency practice

When a statute conflicts with a regulation, form, instructions, manual or stated agency practice, follow the statute; forms and instructions fill gaps where the statute is silent. Register the choice and mark the code as [CONTRIBUTING.md](CONTRIBUTING.md#source-conflicts) describes. Never leave it only in a comment or a PR body.

## Partner API contract tests

The YAML files under `policyengine_us/tests/policy/baseline/partners/**` are API partner contract tests. Never rewrite their expected values merely to make CI pass. Follow [Partner API contract tests](CLAUDE.md#partner-api-contract-tests) before editing them.

Use one designated editor for each partner test file. The coordinator assigns files to agents or teammates; avoid conflicting parallel writes.

Before editing partner tests:

- Identify the causal model change and derive every changed expected value from primary sources independently of the implementation.
- Table every changed value in the PR: file, case, variable, old value, new value and source justification. Compute every output variable of each affected case; the test runner stops at the first failure and can hide other changed outputs. Explain the partner-facing impact and why the change is intentional.
- Check affected boundary cases, failing or not. Compare parameter trees and formula-derived thresholds at the base and head for the cases' periods; uprating can move values outside the diff. Check each case whose name or own comments place it at, just above or just below a moved value. Preserve its stated purpose and justify any input or coverage change from the source. Check partner-flagged cases and any dependency a partner identified in the PR; resolve the compatibility question before merging.
- Preserve the pre-change failing results as evidence. Do not delete, skip, rename or loosen a case merely to make CI pass.

Before merging, obtain independent automated review at the current head from a fresh reviewer who neither made the model change nor edited the expectations. The reviewer recomputes each changed value from the primary source, checks every changed output and confirms that the diff contains only the intended expectation, input, eligibility and coverage changes. Rerunning the changed model alone does not supply an independent expected value. Pass all required CI checks at the current head.

Request human review only for a specific material open question that requires that person's expertise, and name the question in the request. Resolve any source conflict, untraced value or partner compatibility question before merging. Do not request human review or notify a person to keep them informed or because they own the area.
