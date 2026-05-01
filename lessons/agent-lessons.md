# Agent Lessons Learned

Accumulated from /encode-policy-v2 and /backdate-program runs across all contributors.
Loaded by implementation agents on future runs.


## New Lessons from Minnesota MSA (2026-04-30)

### FORMULA
- When a state SSP grant formula subtracts the federal benefit separately (e.g., `standard - federal_ssi - countable_income`), applying the $20 general disregard inside the countable-income variable does NOT reduce the federal-benefit portion; the disregard must be applied at the grant-calculation step against the combined `(federal_benefit + other_unearned)`, not against `other_unearned` alone. Otherwise the SSI track under-grants by $20/mo for the dominant cohort with no other unearned income.
- When a state SSP grant formula stacks federal-SSI-style disregards (e.g., $20 general + $65 + 1/2 of remainder), gate the earned-disregard branch on `~receives_ssi`; the federal SSI calculation has already absorbed the earned-side disregards, so reapplying them on the state side double-counts.
- When the federal SSI methodology rolls leftover general-disregard from unearned to earned (`leftover_general = max_(20 - unearned, 0)` added to earned-disregard flat), document explicitly whether the state regulation endorses this rollover; state manuals often only restrict the earned-only disregards and are silent on whether the general $20 rolls — pick a defensible interpretation and add a code comment citing the basis.

### TEST
- For SSP track-specific formulas, always include at least one test case where an SSI recipient also has non-zero non-SSI unearned income (e.g., pension, child support, Social Security); SSI-only test cases mask bugs in disregard handling because the countable-unearned variable correctly returns zero when federal SSI consumed everything, hiding whether the formula works for mixed-income SSI recipients.
- Verify SSP empirical math against the SSA "State Assistance Programs for SSI Recipients" Table 1 state-portion column: compute `combined - federal_FBR` and compare to the listed state portion; a $20 discrepancy in either direction is the signature of a missing-or-double-applied general income disregard at the grant-calculation step.
- When backdating an SSP to multiple eras (e.g., 2011, 2024, 2026), include at least one test case per era; era-specific parameter entries with no matching test silently mis-extrapolate values from adjacent eras and are invisible to the typical "2024 or 2026" test cluster.
- When a parameter introduces a new disregard (e.g., $20 general) into an existing formula, sweep ALL pre-existing test files that reference the affected variable and rebase expected outputs; stale expected values from before the disregard was added cause cascading test failures that look like formula bugs but are actually outdated fixtures.

### REFERENCE
- For multi-era assistance-standard parameters (e.g., 2011 / 2024 / 2026), each era often has a different authoritative source (SSA factsheet for old era, House Research / state manual for current era); since YAML doesn't support date-keyed references, list multiple references and use the title field to indicate which source covers which era (e.g., `"SSA Table 1 ($20 value only, 2011)"`).
- When a state regulation manual section is cited for a parameter but the section's text does not actually authorize that value (e.g., CM 0018.18 covers earned disregards only, not the $20 general disregard), drop the manual cite and use the secondary explanatory source (e.g., House Research) as primary; do not bundle a non-authoritative cite alongside the real authority.
- The SSA "State Assistance Programs for SSI Recipients" series (last published 2011) is hosted on SSA.gov which blocks automated access (403/Akamai); when relying on this source, present it at the user-checkpoint phase for manual download rather than letting document-collector agents repeatedly fail and proceed with incomplete data.

### WORKFLOW
- For SSP programs with grandfathered or closed-cohort categories (e.g., pre-1994 couple eligibility), explicitly present the full-vs-reduced enum scope as a Phase 2 user decision rather than implementing all categories by default; closed cohorts are real regulatory features but rarely affect the modeled population, so the user should choose whether the implementation cost is justified.
- Coverage reports must be regenerated after each round of fixes, not relied on from earlier rounds; a report that still references a pre-fix variable name (e.g., `is_ssi_eligible | (ssi > 0)` when the code now uses `is_ssi_aged_blind_disabled`) wastes review effort and triggers false flags.
