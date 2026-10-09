# PolicyEngine US Agent Instructions

Follow the repository guidance in `CLAUDE.md` for commands, style, changelog entries, and PolicyEngine modeling conventions.

## Test cost and CI capacity

Follow [Test design and CI cost](CLAUDE.md#test-design-and-ci-cost) before adding or expanding tests. Use variable-named YAML tests for policy calculations; reserve Python tests for behavior YAML cannot exercise. Preserve Core/data compatibility and isolation coverage, avoid repeated full-model construction, and do not add CI runners or parallel heavy processes without explicit authorization. Document the purpose and measured cost of new simulation-heavy Python tests in the PR.

## Partner API contract tests

Files under `policyengine_us/tests/policy/baseline/partners/**` are API partner contract tests.

Do not rewrite these expected outputs merely to match changed model behavior or make CI pass. If a model change causes one of these tests to fail, treat that as a possible partner-facing API change.

Ziming Hua (@hua7450) approves every edit to these files (Max Ghenis, 2026-10-09). Subagents and agent teammates must not edit partner test files. If a subagent or agent teammate finds that an edit is needed, it must stop and report back; the top-level agent takes the three-question gate to Ziming before any edit is made.

Before changing expected outputs in this folder:

- Flag the partner-facing risk to the user.
- Put these three questions to Ziming on the PR that causes the change (per CLAUDE.md): request his review with `gh pr edit <number> --add-reviewer hua7450`, and post a comment that names each changed case, its old and new expected values, and the model change and law behind it. If Ziming is the person you are working with, show him the changed cases and ask him directly with the `AskUserQuestion` tool instead; record his answer in a PR comment, which counts as his approval of those edits.
  1. Are you sure you want to edit this test file?
  2. Have you notified a team member about this change?
  3. Have you notified the API partner about this change?
- Do not edit partner test files until Ziming has answered yes to all three questions, and do not merge a PR that changes them until he has approved a head that contains the edits.
- Identify the model change that caused the partner output change.
- Preserve the failing behavior as evidence unless the change is intentional.
- Explain the partner-facing impact to Ziming and the user.

Changing these tests without Ziming's explicit approval is unsafe, even if CI passes afterward.
