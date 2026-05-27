# Partner API Contract Tests

This directory contains API partner contract tests.

Do not rewrite expected outputs here merely to match changed model behavior or make CI pass. A failure in this directory is evidence of a possible partner-facing API change.

Before changing these tests:

- Identify the model change that caused the output change.
- Preserve the failing behavior as evidence unless the change is intentional.
- Document the partner-facing impact in the PR or issue.
- Notify or request review from the API/partner team.

Changing these tests without reporting partner impact is unsafe, even if CI passes afterward.
