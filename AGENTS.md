# PolicyEngine US Agent Instructions

Follow the repository guidance in `CLAUDE.md` for commands, style, changelog entries, and PolicyEngine modeling conventions.

## Partner API Contract Tests

Files under `policyengine_us/tests/policy/baseline/partners/**` are API partner contract tests.

Do not rewrite these expected outputs merely to match changed model behavior or make CI pass. If a model change causes one of these tests to fail, treat that as a possible partner-facing API change.

Subagents must not edit partner test files. If a subagent finds that an edit is needed, it must stop and report back; the top-level agent runs the three-question gate with the user before any edit is made.

Before changing expected outputs in this folder:

- Flag the partner-facing risk to the user.
- Ask these three questions separately, one at a time, waiting for the user's response after each question:
  1. Are you sure you want to edit this test file?
  2. Have you notified a team member about this change?
  3. Have you notified the API partner about this change?
- Identify the model change that caused the partner output change.
- Preserve the failing behavior as evidence unless the change is intentional.
- Explain the partner-facing impact to the user.

Changing these tests without explicit user confirmation is unsafe, even if CI passes afterward.
