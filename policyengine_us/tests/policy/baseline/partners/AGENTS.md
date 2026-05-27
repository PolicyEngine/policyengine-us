# Partner API Contract Tests

This directory contains API partner contract tests.

Do not rewrite expected outputs here merely to match changed model behavior or make CI pass. A failure in this directory is evidence of a possible partner-facing API change.

Before changing these tests:

- Flag the partner-facing risk to the user.
- Ask the user for explicit confirmation three separate times before editing partner tests.
- Identify the model change that caused the output change.
- Preserve the failing behavior as evidence unless the change is intentional.
- Explain the partner-facing impact to the user.

Changing these tests without explicit user confirmation is unsafe, even if CI passes afterward.
