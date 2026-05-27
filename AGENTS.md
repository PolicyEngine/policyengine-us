# PolicyEngine US Agent Instructions

Follow the repository guidance in `CLAUDE.md` for commands, style, changelog entries, and PolicyEngine modeling conventions.

## Partner API Contract Tests

Files under `policyengine_us/tests/policy/baseline/partners/**` are API partner contract tests.

Do not rewrite these expected outputs merely to match changed model behavior or make CI pass. If a model change causes one of these tests to fail, treat that as a possible partner-facing API change.

Before changing expected outputs in this folder:

- Flag the partner-facing risk to the user.
- Ask the user for explicit confirmation three separate times before editing partner tests.
- Identify the model change that caused the partner output change.
- Preserve the failing behavior as evidence unless the change is intentional.
- Explain the partner-facing impact to the user.

Changing these tests without explicit user confirmation is unsafe, even if CI passes afterward.
