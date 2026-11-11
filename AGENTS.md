# PolicyEngine US Agent Instructions

Follow the repository guidance in `CLAUDE.md` for commands, style, changelog entries, and PolicyEngine modeling conventions.

## Test cost and CI capacity

Follow [Test design and CI cost](CLAUDE.md#test-design-and-ci-cost) before adding or expanding tests. Use variable-named YAML tests for policy calculations; reserve Python tests for behavior YAML cannot exercise. Preserve Core/data compatibility and isolation coverage, avoid repeated full-model construction, and do not add CI runners or parallel heavy processes without explicit authorization. Document the purpose and measured cost of new simulation-heavy Python tests in the PR.

## Statutes against forms, instructions and agency practice

When a statute conflicts with a regulation, form, instructions, manual or stated agency practice, follow the statute; forms and instructions fill gaps where the statute is silent. Register the choice and mark the code as [CONTRIBUTING.md](CONTRIBUTING.md#source-conflicts) describes. Never leave it only in a comment or a PR body.

## Partner API contract tests

The YAML files under `policyengine_us/tests/policy/baseline/partners/**` are API partner contract tests. Never rewrite their expected values merely to make CI pass. Follow [Partner API contract tests](CLAUDE.md#partner-api-contract-tests) before you edit any of them. In short:

- Anyone, agents and subagents included, may update an expected value when a cited model change in the same PR explains every changed value; the PR body tables every changed value (file, case, variable, old value, new value, cause), computed from every output variable of each affected case, because the test runner stops a case at its first failing variable; you check every case whose name or comments cite a parameter the change moves, failing or not; an independent review posts the value it recomputed from the cited source for each row; and the PR tags Ziming Hua (`@hua7450`) with the table as an FYI before it merges.
- Ziming approves, through the three-question checklist, any edit other than an expected value or a comment that derives it (inputs, name, `period`, error margins, reforms, added or removed cases or output variables), a case whose purpose the model change defeats (such as a boundary case whose boundary moved, even if it still passes), any changed value the review can't trace, and any case marked `# partner-flagged` or named on the PR as one a partner depends on. Until he approves a head that contains the edit, the PR doesn't merge, and nobody deletes, skips, renames or loosens a case to turn CI green. A subagent that reaches one of these cases stops and reports back.
