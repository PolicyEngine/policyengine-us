# Agent Lessons Learned

Accumulated from /encode-policy-v2 and /backdate-program runs across all contributors.
Loaded by implementation agents on future runs.

## New Lessons from Utah UI (2026-05-13)

### PARAMETER
- For annually-recomputed parameters, never use a single dated entry to cover multiple years — create one dated entry per distinct value year so future audits and tests can isolate per-year regressions.
- When two parameters derive from the same underlying statutory quantity (e.g., max WBA and min base-period wages both keyed to the IAFY wage), cross-check them mathematically after entry; an inconsistent ratio reveals a transcription error in one of them.
- When a parameter value is sourced from a year-labeled form, embed the form number AND the effective year in the reference title so rolling-URL drift is detectable on audit.

### REFERENCE
- When citing a document via a URL that the publisher overwrites annually (current-year landing page), pair the live URL with a Wayback Machine snapshot capturing the historical version, and label the live URL as "current year — rolls over annually."
- When the PDF's printed page number differs from the file page number (front-matter offset), annotate both in any human-readable comment (e.g., "page 11 (PDF file p. 13)") and use the file page number in the `#page=` anchor.
- Never let a code comment cite one page number while the adjacent URL anchor uses a different one — readers cannot tell which is correct without rendering the PDF.

### TEST
- For parameters with multiple dated entries, place at least one boundary test inside each distinct year so a value regression in any single year fails its own dedicated test.
- Include a cross-year regression-guard test that uses an old year's threshold against the new year's expected behavior — this catches accidental parameter collapse (single-entry-applied-to-all-years bugs).

### WORKFLOW
- Document-collector agents must fall back to the Read tool on PDF files when sandboxed binaries like `pdftotext`/`pdftoppm` are unavailable, rather than reporting the PDF as unreadable.
- When a parameter value changes during review, grep test files for old-value-anchored case names, header comments, and inline comments — not just numeric inputs — and rewrite the prose so documentation does not drift from the new value.
