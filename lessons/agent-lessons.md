# Agent Lessons Learned

Accumulated from /encode-policy-v2 and /backdate-program runs across all contributors.

## New Lessons from New York UI (2026-04-23)

### PARAMETER
- When a program has multiple divisor paths (e.g., divisor-25 vs. divisor-26), each path may carry its own regulatory floor distinct from the global minimum; encode per-path floors as a separate parameter (e.g., `formula_min_amount`) rather than relying on the global `min_amount` to cover all cases.
- When a parameter's effective date is described as a day-of-week in statute (e.g., "first Monday of October"), compute the actual calendar date rather than assuming a round number; off-by-one-week errors produce incorrect benefit amounts for every claim in the gap period.
- Parameters that serve two distinct regulatory purposes (e.g., WBR ceiling and partial-employment earnings cap) should be split into separate parameter files; using one parameter for both creates silent drift risk when the two values are updated independently by the agency.

### FORMULA
- When a partial benefit calculation is specified as `ceil(max(...))`, the `ceil` is load-bearing: omit it and any odd-number input produces a fractional result rather than a whole dollar. Always match the exact rounding direction (floor vs. ceil) specified in the regulation for each formula step.
- For a variable with three or more mutually exclusive outcomes, use `select()` rather than nested `where()` calls. Nested `where()` has implicit fall-through to the last arm, which can silently assign the wrong outcome to cases that match none of the explicit conditions.
- When wiring a new state benefit variable, add it to the relevant federal aggregator (e.g., `unemployment_compensation`) as an explicit step; omitting this prevents the benefit from flowing into AGI and federal tax calculations.

### REFERENCE
- Before writing any `#page=` anchor for a multi-page PDF, verify which physical page contains the actual parameter value — not the printed page number and not the page implied by the document title. A cover page or diagram can shift every subsequent page number by one.
- When a single PDF URL is copy-pasted as the source for multiple parameters, verify the page anchor independently for each parameter; bulk-copy of the base URL propagates the same wrong anchor to every file simultaneously.
- When a regulatory citation uses section numbers (e.g., §§ 522–523), confirm those sections govern the specific rule encoded, not just adjacent concepts. Statutory definitions and administrative computation rules often live in different sections.

### VARIABLE
- Test cases for rounding-sensitive formulas must include inputs that produce non-integer intermediate values (e.g., odd WBR for a 0.5× calculation). Test cases using only even-divisor inputs will pass both the correct and the buggy (missing ceil/floor) implementations.
- When two parameters are mathematically coupled by construction (e.g., `rate_b = rate_a − 1`), either derive one from the other in the formula or add an explicit comment documenting the coupling and the requirement to update them together; silent coupling is a future maintenance hazard.
