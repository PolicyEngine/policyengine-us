# PolicyEngine US Agent Instructions

Follow the repository guidance in `CLAUDE.md` for commands, style, changelog entries, and PolicyEngine modeling conventions.

## Partner API Contract Tests

Files under `policyengine_us/tests/policy/baseline/partners/**` are API partner contract tests.

Do not rewrite these expected outputs merely to match changed model behavior or make CI pass. If a model change causes one of these tests to fail, treat that as a possible partner-facing API change.

Before changing expected outputs in this folder:

- Identify the model change that caused the partner output change.
- Preserve the failing behavior as evidence unless the change is intentional.
- Document the partner-facing impact in the PR or issue.
- Notify or request review from the API/partner team.

Changing these tests without reporting partner impact is unsafe, even if CI passes afterward.
