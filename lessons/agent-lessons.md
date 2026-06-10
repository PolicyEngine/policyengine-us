# Agent Lessons Learned

Accumulated from /encode-policy-v2 and /backdate-program runs across all contributors.
Loaded by implementation agents on future runs.

## New Lessons from Kansas CCAP (2026-06-10)

### REFERENCE
- A parent/umbrella section page (e.g., a manual's `chapter6000.htm`) does NOT necessarily render its child subsections (6200/6300/6410); each subsection often lives on its own page. Before citing an umbrella URL as the source for a child-section provision, open it and confirm the child section's body text is actually present — do not infer containment from the URL's numeric prefix or from HTML nesting. When the umbrella lacks the child bodies, cite each child section's own per-section URL (and honor the one-link-per-document convention by splitting a multi-section umbrella cite into distinct per-section links).

### FORMULA
- A signal used as a POSITIVE carve-out trigger must be reachable for the target population. `is_tax_unit_head_or_spouse` is never true for an under-18 person, so using it to fire a teen/child-specific provision (e.g., a teen-parent earnings carve-out) makes the carve-out dead code. Verify the gating signal can be true for the subpopulation it targets; for "is this person a parent/legally-responsible adult" use a reachable test like `is_parent` (own children in household > 0) grounded in the regulation's responsibility wording, not a tax-unit-role flag. (Inverse of the Iowa CCAP rule that uses `~is_tax_unit_head_or_spouse` as a NEGATIVE guard — same flag, opposite reachability trap.)

### FORMULA
- Honor parenthetical scoping qualifiers on a charge/deduction (e.g., a family-share deduction the manual applies only to "Income Eligible (Non-TANF) clients"). A subpopulation the regulation explicitly excludes from the charge (TANF recipients here) must be zeroed out of that charge, not just exempted from the upstream income test. Read the exact scope clause on the deduction itself — an exemption stated elsewhere (e.g., "TANF is exempt from the financial-need test") does NOT automatically waive a separate downstream fee.

### WORKFLOW
- A scope/consolidation document's premise about how a value is CONSTRUCTED (e.g., "the F-1 income-limit column = 250% FPL with an 85% SMI cap baked in") is a derivation claim, not authority — verify it against the primary source before agents build on it. When two agents deadlock by each citing a different authority (one the scope decision, one the arithmetic), the orchestrator must fact-check the underlying PDF/manual itself rather than picking a side; a wrong construction premise silently mis-specifies the gate (here the column was pure 85% SMI and the manual delegated the entire income test to the F-1 schedule).
