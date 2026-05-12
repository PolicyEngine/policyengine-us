# Agent Lessons Learned

Accumulated from /encode-policy-v2 and /backdate-program runs across all contributors.
Loaded by implementation agents on future runs.

## New Lessons from Oklahoma UI (2026-05-12)

### PARAMETER
- Verify every parameter value against authoritative source PDFs before committing; do not let inferred or rounded values reach the YAML files.
- Keep parameter values and any test/comment references to those values in sync — when a value changes, grep for the old number across params, tests, and docstrings in one sweep.
- Reserve sentinel `0000-01-01` effective dates for parameters that genuinely have no historical variation; whenever the value reflects a real first-year-applicable date, use the actual effective date so future audits can trace it.
- When citing a statute that delegates the actual value to an agency (e.g. board-determined annual rates), put the delegating statute in the reference title rather than relying on a homepage URL that does not display the value.

### REFERENCE
- A single-URL `reference` written as `(string)` is a parenthesized string, not a tuple — write `(string,)` with a trailing comma (or drop parens entirely) to match the multi-reference convention.
- PDF `#page=` anchors should target the file page that contains the cited value or operative text, not the table-of-contents or heading-only page; off-by-one is the common failure mode.
- Statutory citations should be as specific as the value warrants — cite `§X-XXX(A)(1)` when the floor lives in that subsection rather than the broader `§X-XXX(A)`.
- When a cited code section has been repealed, replace the citation with the active replacement section (e.g. updated definitions section) and update the page anchor accordingly; do not leave repealed-section URLs in active references.
- Verify every reference URL actually resolves (no 404s) before merge; keep an alternate authoritative source (e.g. companion agency PDF, statutory text) ready when one URL breaks.

### WORKFLOW
- When parallel agents produce paired artifacts (variables + tests, params + variables), give each agent the same canonical variable-name and parameter-name list so the files line up — do not let one agent follow the spec and another follow the prompt independently.
- Before approving a new program, audit every parameter value against a manifest of source PDFs; do not rely solely on the implementer's claim that values match.
