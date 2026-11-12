# PolicyEngine US Agent Instructions

Follow the repository guidance in `CLAUDE.md` for commands, style, changelog entries, and PolicyEngine modeling conventions.

## Test cost and CI capacity

Follow [Test design and CI cost](CLAUDE.md#test-design-and-ci-cost) before adding or expanding tests. Use variable-named YAML tests for policy calculations; reserve Python tests for behavior YAML cannot exercise. Preserve Core/data compatibility and isolation coverage, avoid repeated full-model construction, and do not add CI runners or parallel heavy processes without explicit authorization. Document the purpose and measured cost of new simulation-heavy Python tests in the PR.

## Statutes against forms, instructions and agency practice

When a statute conflicts with a regulation, form, instructions, manual or stated agency practice, follow the statute; forms and instructions fill gaps where the statute is silent. Register the choice and mark the code as [CONTRIBUTING.md](CONTRIBUTING.md#source-conflicts) describes. Never leave it only in a comment or a PR body.

## Partner API contract tests

Files under `policyengine_us/tests/policy/baseline/partners/**` are API partner contract tests.

Do not rewrite these expected outputs merely to match changed model behavior or make CI pass. If a model change causes one of these tests to fail, treat that as a possible partner-facing API change.

Use one designated editor for each partner test file. The coordinator assigns files to agents or teammates; avoid conflicting parallel writes.

Before changing expected outputs in this folder:

- Identify the causal model change and derive the expected outputs from primary sources independently of the implementation.
- Document each changed case, its old and new expected values, and the source justification in the PR. Explain the partner-facing impact to the user and why the contract change is intentional.
- Preserve the pre-change failing results as evidence.

Before merging, obtain independent automated review of the source derivation, expected outputs, and partner impact at the current head, and pass all required CI checks.

Request human review only for a specific material open question that requires that person's expertise, and name the question in the request. Do not request human review or notify a person to keep them informed or because they own the area.
