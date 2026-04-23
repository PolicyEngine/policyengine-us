# NY UI Implementation Specification

**Program**: New York State Unemployment Insurance (UI)
**Administering Agency**: New York State Department of Labor (NYSDOL)
**Statutory Authority**: NY Labor Law Article 18, §§ 500–603
**Variable Prefix**: `ny_ui`
**Spec Date**: 2026-04-23
**Status**: Pre-implementation spec — no code exists yet

---

## Discovered Reference Implementations

| Implementation | Branch / Location | Key Files |
|---|---|---|
| PA UC (Pennsylvania Unemployment Compensation) | `.claude/worktrees/pa-unemployment-insurance` | `pa/dli/unemployment_compensation/` — 20 variables |
| WA PFML (Washington Paid Family and Medical Leave) | Current branch `issue-8136-wa-pfml` | `wa/pfml/` (empty on current branch; prior commits) |
| Federal `unemployment_compensation` stub | `policyengine_us/variables/gov/states/unemployment_compensation.py` | Input stub, no formula |

**Primary reference**: PA UC (`pa-unemployment-insurance` worktree) — closest structural analog with high-quarter wages test, credit-weeks test, partial benefit credit, WBR floor/cap, and weeks-unemployed input pattern.

---

## Source Citations

All requirements below are cross-referenced against these primary sources:

| ID | Source | URL |
|---|---|---|
| S1 | NY Lab. Law § 590 — Rights to benefits | https://www.nysenate.gov/legislation/laws/LAB/590 |
| S2 | NY Lab. Law § 527 — Valid original claim | https://www.nysenate.gov/legislation/laws/LAB/527 |
| S3 | NY Lab. Law § 525 — Partial benefit credit | https://www.nysenate.gov/legislation/laws/LAB/525 |
| S4 | NY Lab. Law § 522 — Total and partial unemployment | https://www.nysenate.gov/legislation/laws/LAB/522 |
| S5 | NY Lab. Law § 524 — Base period | https://www.nysenate.gov/legislation/laws/LAB/524 |
| S6 | P832 (NYSDOL, Feb 2026) — How Your Weekly UI Benefit Payment Is Calculated | User-supplied PDF: p832-how-your-weekly-ui-benefits-are-calculated-2-26.pdf |
| S7 | P803 (NYSDOL, Oct 2025) — Partial Unemployment FAQs | User-supplied PDF: p803-partial-ui-faqs-10-3-25.pdf |
| S8 | Governor Hochul announcement — Max benefit increase to $869 | https://www.governor.ny.gov/news/governor-hochul-and-labor-leaders-announce-maximum-weekly-benefit-increase-unemployed-workers |

---

## Citation Discrepancies Found

Two values differ between the earlier working notes and the authoritative P832 (Feb 2026) document:

1. **High-quarter cap for 1.5x test**: Working notes cited $11,088 (possibly a 2024 figure). P832 Feb 2026 states $19,118 as the cap above which the 1.5x rule is replaced by a flat $9,559 requirement in other quarters. Use P832 value.

2. **Minimum WBR**: Working notes cited $104. P832 Feb 2026 states $140 as the minimum as of January 2026 (and likely $143 for 4-quarter cases based on formulaic structure; P832 says $143 specifically for the >$3,575 / 4-quarter case). Use $140 as the general statutory floor, noting $143 appears in P832 as a practical floor for the 4-quarter formula.

3. **Partial benefit earnings cap**: P803 (Oct 2025) cites $869 as the gross earnings cap — consistent with the new max WBR effective 2025-10-13. Earlier working notes also cite $869, which is correct.

4. **2-or-3-quarter formula**: P832 (Feb 2026) adds a third tier not present in working notes:
   - HQ > $4,000: avg of 2 highest / 26 (min $143)
   - $3,576–$4,000: HQ / 26 (min $143)
   - ≤ $3,575: HQ / 25
   The working_references.md simplified this to "avg of 2 highest / 26" for all 2/3-quarter cases. The P832 version is authoritative.

---

## Existing Variables to Reuse

| Variable | File | Notes |
|---|---|---|
| `employment_income` | `policyengine_us/variables/input/employment_income.py` | Annual wages — approximation basis for quarterly estimates |
| `employment_income_last_year` | `policyengine_us/variables/household/income/person/employment_income_last_year.py` | Prior-year wages for base-period approximation |
| `weekly_hours_worked` | `policyengine_us/variables/household/income/person/weekly_hours_worked.py` | Average weekly hours — for partial benefit tier lookup |
| `hours_worked_last_week` | `policyengine_us/variables/household/income/person/hours_worked_last_week.py` | Point-in-time hours — alternative to weekly_hours_worked |
| `unemployment_compensation` | `policyengine_us/variables/gov/states/unemployment_compensation.py` | Federal stub — ny_ui should feed into this |
| `self_employment_income` | `policyengine_us/variables/input/self_employment_income.py` | Needed to exclude from gross-earnings cap check |

**PA UC variables as structural patterns** (not reused directly — NY-specific equivalents needed):

| PA UC Variable | NY UI Equivalent | Notes |
|---|---|---|
| `pa_uc_highest_quarter_wages` | `ny_ui_high_quarter_wages` | Input variable, no formula |
| `pa_uc_base_year_wages` | `ny_ui_base_period_wages` | Sum of all 4 quarters |
| `pa_uc_weekly_benefit_rate` | `ny_ui_weekly_benefit_rate` | Formula differs significantly |
| `pa_uc_partial_benefit_credit` | `ny_ui_partial_benefit_credit` | Formula differs (50% vs 30%) |
| `pa_uc_gross_weekly_earnings` | `ny_ui_gross_weekly_earnings` | Input variable, no formula |
| `pa_uc_weeks_unemployed` | `ny_ui_weeks_unemployed` | Input variable, no formula |
| `pa_uc_monetarily_eligible` | `ny_ui_monetarily_eligible` | Logic differs |
| `pa_uc` | `ny_ui` | Top-level benefit variable |

---

## Requirements

### Base Period

**REQ-001** [INCOME] Define standard base period as first 4 of last 5 completed calendar quarters before the quarter in which the claim is filed.
- Source: S5 (§ 524), S6 (P832 "Understanding your base period")

**REQ-002** [INCOME] Define alternate base period as last 4 completed calendar quarters before the quarter of filing.
- Source: S5 (§ 524), S6 (P832 "Two types of base periods")
- Note: Claimant may elect alternate if standard period fails the monetary tests. PolicyEngine simplification: treat as an input flag or use whichever yields higher benefit (approximation acceptable).

**REQ-003** [INCOME] Quarter in which the claim is filed does not count as part of either base period; wages earned in that quarter are excluded.
- Source: S5 (§ 524), S6 (P832 "For all base periods, the quarter in which you file…")
- Implementation note: In a YEAR-period model this is approximated. Implementer should document the limitation.

### Quarterly Wage Inputs

**REQ-004** [INCOME] Accept per-quarter wage inputs for the 4 base-period quarters.
- Suggested variables: `ny_ui_q1_wages`, `ny_ui_q2_wages`, `ny_ui_q3_wages`, `ny_ui_q4_wages` (all `float`, entity=`Person`, period=`YEAR`, unit=`USD`)
- Alternative: `ny_ui_high_quarter_wages` as a single input (direct HQ wages, no formula), plus `ny_ui_base_period_wages` (sum). This is the PA UC approach and is adequate if implementer accepts the limitation that per-quarter breakdown is user-supplied.
- Source: S2 (§ 527), S5 (§ 524)

**REQ-005** [INCOME] Derive `ny_ui_high_quarter_wages` as the maximum of the 4 quarterly inputs.
- Formula: `max(q1, q2, q3, q4)` — or accepted as a direct input following the PA UC pattern.
- Source: S2 (§ 527), S6 (P832 "high quarter wages")

**REQ-006** [INCOME] Count the number of quarters with non-zero wages (`ny_ui_quarters_with_wages`).
- Formula: `sum([q > 0 for q in [q1, q2, q3, q4]])`
- Required for the 2/3-quarter WBR formula (REQ-014, REQ-015) and the 2-quarter eligibility test (REQ-009).
- Source: S2 (§ 527), S6 (P832)

### Monetary Eligibility — § 527

**REQ-007** [ELIGIBILITY] High-quarter minimum: claimant must have earned at least the indexed minimum in the highest quarter of the base period.
- Parameter: `gov.states.ny.dol.unemployment_insurance.eligibility.high_quarter_minimum`
- Values by date:
  - 2025-01-01: $3,400
  - 2026-01-05: $3,500
- Source: S2 (§ 527), S6 (P832 "For claims filed in 2026, you must have been paid at least $3,500")

**REQ-008** [ELIGIBILITY] High-quarter minimum threshold is indexed; implementer should use a date-keyed parameter to support future annual increases.
- Source: S2 (§ 527)

**REQ-009** [ELIGIBILITY] Work-in-2-quarters test: claimant must have been paid wages in at least 2 calendar quarters of the base period.
- Formula: `ny_ui_quarters_with_wages >= 2`
- Source: S2 (§ 527), S6 (P832 "You must have worked and been paid wages in jobs covered by UI in at least two calendar quarters")

**REQ-010** [ELIGIBILITY] 1.5x total-wages test (standard case): total base-period wages must be ≥ 1.5 × high-quarter wages, when high-quarter wages < the cap.
- Parameter: `gov.states.ny.dol.unemployment_insurance.eligibility.total_wages_multiplier` = 1.5
- Condition: applies when `ny_ui_high_quarter_wages < high_quarter_cap`
- Source: S2 (§ 527), S6 (P832 "The total wages paid to you must be at least 1.5 times the amount paid to you in your high quarter")

**REQ-011** [ELIGIBILITY] 1.5x total-wages test (capped case): when high-quarter wages ≥ cap, other-three-quarters wages must be ≥ cap/2.
- P832 (Feb 2026) cap: $19,118; required in other 3 quarters: $9,559
- Parameter: `gov.states.ny.dol.unemployment_insurance.eligibility.high_quarter_cap` = 19,118 (2026 value)
- Note: Working references.md cited $11,088 / $5,544 — these appear to be 2024/2025 values. P832 Feb 2026 is authoritative for 2026: $19,118 / $9,559.
- Formula: `total_base_wages >= high_quarter_wages + (high_quarter_cap / 2)` when `ny_ui_high_quarter_wages >= high_quarter_cap`
- Source: S2 (§ 527), S6 (P832 "Exception: If your high quarter wages were $19,118 or more, you must have been paid a combined total of at least $9,559 in the other three quarters")

**REQ-012** [ELIGIBILITY] `ny_ui_monetarily_eligible` = all three tests pass: REQ-007 (high quarter minimum), REQ-009 (2+ quarters), and REQ-010/REQ-011 (1.5x test).
- Suggested variable: `ny_ui_monetarily_eligible` (bool, Person, YEAR)
- Source: S2 (§ 527)

### Weekly Benefit Rate — § 590(5)

**REQ-013** [BENEFIT] Standard formula (all 4 quarters): if high-quarter wages > $3,575 → WBR_raw = HQ / 26; if ≤ $3,575 → WBR_raw = HQ / 25.
- Parameter: `gov.states.ny.dol.unemployment_insurance.benefit.divisor_threshold` = 3,575
- Parameter: `gov.states.ny.dol.unemployment_insurance.benefit.divisor_high` = 26
- Parameter: `gov.states.ny.dol.unemployment_insurance.benefit.divisor_low` = 25
- Applies when: `ny_ui_quarters_with_wages == 4`
- Source: S1 (§ 590(5)), S6 (P832 "If you were paid wages in all four quarters of your base period…")

**REQ-014** [BENEFIT] 2/3-quarter formula tier 1: if 2 or 3 quarters with wages AND high-quarter wages > $4,000 → WBR_raw = average of two highest quarters / 26.
- P832 worked example: HQ=$4,500, 2nd=$4,288 → avg=$4,394 → WBR=$169
- Applies when: `ny_ui_quarters_with_wages in [2, 3]` AND `ny_ui_high_quarter_wages > 4_000`
- Source: S1 (§ 590(5)), S6 (P832 "More than $4,000: Your benefit amount is the average wages of your two highest quarter wages, divided by 26")

**REQ-015** [BENEFIT] 2/3-quarter formula tier 2: if 2 or 3 quarters with wages AND $3,576 ≤ HQ ≤ $4,000 → WBR_raw = HQ / 26.
- Applies when: `ny_ui_quarters_with_wages in [2, 3]` AND `3576 <= ny_ui_high_quarter_wages <= 4_000`
- Source: S6 (P832 "$3,576 to $4,000: Your benefit amount is your high quarter wages divided by 26")

**REQ-016** [BENEFIT] 2/3-quarter formula tier 3: if 2 or 3 quarters with wages AND HQ ≤ $3,575 → WBR_raw = HQ / 25.
- Applies when: `ny_ui_quarters_with_wages in [2, 3]` AND `ny_ui_high_quarter_wages <= 3_575`
- Source: S6 (P832 "$3,575 or less: Your benefit amount is your high quarter wages divided by 25")

**REQ-017** [BENEFIT] WBR is rounded DOWN to the nearest whole dollar (floor, not round).
- Formula: `WBR_floored = floor(WBR_raw)`
- Source: S1 (§ 590(5): "if not a multiple of one dollar, shall be lowered to the next multiple of one dollar")

**REQ-018** [BENEFIT] Minimum weekly benefit rate (statutory floor).
- Parameter: `gov.states.ny.dol.unemployment_insurance.benefit.min_amount`
- Values by date:
  - 2020-01-01: 104 (historical)
  - 2026-01-01: 140 (P832 Feb 2026: "The minimum benefit rate is $140 as of January 2026")
- Note: P832 also mentions $143 as a practical floor for the 4-quarter/HQ>$3,575 case (since $3,576/26 ≈ $137.54 floored to $137 < $143). The $140 statutory minimum supersedes this. Encode $140 as min; the $143 figure in P832 likely refers to a formula minimum for that tier specifically, or reflects a slightly different threshold. Use $140 per explicit statement.
- Source: S1 (§ 590), S6 (P832 "minimum benefit rate is $140 as of January 2026")

**REQ-019** [BENEFIT] Maximum weekly benefit rate.
- Parameter: `gov.states.ny.dol.unemployment_insurance.benefit.max_amount`
- Values by date:
  - 2020-01-01: 504 (frozen through 2025-10-12 due to UI Trust Fund loan)
  - 2025-10-13: 869 (FY26 enacted budget; effective first Monday of October 2025)
- Source: S1 (§ 590), S6 (P832 "Effective the first Monday of October 2025 the maximum benefit rate increased to $869"), S8

**REQ-020** [BENEFIT] Maximum WBR indexed annually at 50% of NY State Average Weekly Wage (SAWW) from 2025-10-13 onward.
- Implementation note: Future annual updates require a date-keyed parameter update each year. The SAWW-indexing mechanism itself does not need to be automated in code — a manually-updated parameter per year is correct and consistent with PE patterns.
- Source: S1 (§ 590)

**REQ-021** [BENEFIT] Final WBR = min(max(WBR_floored, min_amount), max_amount).
- Suggested variable: `ny_ui_weekly_benefit_rate`
- Source: S1 (§ 590(5))

### Partial Benefit Credit — § 525

**REQ-022** [PARTIAL] Partial benefit credit = ceil(max(0.50 × WBR, $100)).
- Parameter: `gov.states.ny.dol.unemployment_insurance.partial_benefit_credit.rate` = 0.50
- Parameter: `gov.states.ny.dol.unemployment_insurance.partial_benefit_credit.floor` = 100
- Rounding: round UP (ceiling) to next whole dollar.
- Suggested variable: `ny_ui_partial_benefit_credit`
- Note: NY's PBC formula (50% / $100) differs from PA UC (30% / $6). Do not copy PA formula.
- Source: S3 (§ 525), working_references.md section 6

**REQ-023** [PARTIAL] A claimant is "partially employed" for a week if: gross weekly compensation < WBR + partial_benefit_credit. (Used to determine eligibility for any partial payment that week.)
- Source: S4 (§ 522), S3 (§ 525)

### Partial Benefit — Hours-Based Tiers (effective 2021-08-16)

**REQ-024** [PARTIAL] Weekly benefit payment fraction is determined by total weekly hours worked according to a 5-tier bracket (effective 2021-08-16):
- 0–10 hours: 100% of WBR
- 11–16 hours: 75% of WBR
- 17–21 hours: 50% of WBR
- 22–30 hours: 25% of WBR
- 31+ hours: 0% of WBR
- Parameter path: `gov.states.ny.dol.unemployment_insurance.partial.hours_tiers`
- Suggested implementation: bracket parameter keyed on hours thresholds with fraction amounts.
- Source: S7 (P803 hours table), NY Lab. Art. 18 amendment eff. 2021-08-16

**REQ-025** [PARTIAL] When totaling weekly hours, a maximum of 10 hours per calendar day is counted (prevents a single 12-hour day from counting as 12 hours).
- Source: S7 (P803: "When totaling hours for the week, claimants should use a maximum of 10 hours per calendar day")
- Implementation note: At YEAR periodicity this rule cannot be enforced per-day; document the limitation. The input `ny_ui_weekly_hours_worked` should be understood as already capped accordingly if provided correctly.

**REQ-026** [PARTIAL] Gross earnings cap: if weekly gross earnings (excluding self-employment earnings) exceed the current maximum WBR, no benefit is payable for that week.
- Suggested variable: `ny_ui_gross_weekly_earnings` (input, float, Person, YEAR, unit=USD) — covers non-self-employment earnings only.
- Condition: if `ny_ui_gross_weekly_earnings > max_amount`, weekly payment = 0.
- Source: S7 (P803: "Any claimant who earns more than $869 in weekly gross pay excluding earnings from self-employment will not be eligible")

**REQ-027** [PARTIAL] Self-employment earnings are excluded from the gross-earnings cap check (REQ-026), but self-employment hours still count toward the hours-tier calculation.
- Source: S7 (P803), working_references.md section 8

### Duration — § 590

**REQ-028** [DURATION] Maximum benefit duration: 26 weeks within a 52-week benefit year.
- Parameter: `gov.states.ny.dol.unemployment_insurance.duration.max_weeks` = 26
- Source: S1 (§ 590)

**REQ-029** [DURATION] Maximum benefit amount (MBA) = WBR × 26 weeks.
- Suggested variable: `ny_ui_maximum_benefit_amount`
- Source: S1 (§ 590)

**REQ-030** [DURATION] Weeks-unemployed input: number of weeks in the benefit year the claimant certifies as unemployed (0–26).
- Suggested variable: `ny_ui_weeks_unemployed` (int, Person, YEAR, unit="week")
- Following PA UC pattern: `pa_uc_weeks_unemployed`
- Source: S1 (§ 590)

### Top-Level Benefit Variable

**REQ-031** [BENEFIT] Annual NY UI benefit = sum of weekly payments across `ny_ui_weeks_unemployed` weeks, capped at MBA.
- For full-unemployment weeks: annual benefit ≈ WBR × min(weeks_unemployed, 26)
- For partial-unemployment: annual benefit ≈ (fraction × WBR) × min(weeks_unemployed, 26)
- Suggested variable: `ny_ui` (float, Person, YEAR, unit=USD)
- `defined_for = "ny_ui_monetarily_eligible"`
- Must eventually feed into `unemployment_compensation` (federal stub variable) — check whether `unemployment_compensation` uses `adds` or requires override.
- Source: S1 (§ 590)

### Non-Monetary Eligibility [NOT-MODELED]

**REQ-032** [NOT-MODELED] Claimant must be totally or partially unemployed (§ 522).
- Not modeled in PolicyEngine individual calculations.
- Source: S4 (§ 522), S1 (§ 591)

**REQ-033** [NOT-MODELED] Claimant must be capable of work, ready and willing to work, and actively seeking work (§ 591).
- Source: S1 (§ 591)

**REQ-034** [NOT-MODELED] Disqualifications — voluntary quit without good cause, discharge for misconduct, refusal of suitable work (§ 593).
- Source: NY Lab. § 593

**REQ-035** [NOT-MODELED] Dismissal pay exclusion: weeks where dismissal pay > (WBR + PBC) are ineligible (§ 591(6)).
- Source: NY Lab. § 591(6)

**REQ-036** [NOT-MODELED] Pension offset: WBR reduced if receiving a pension from a base-period employer (§ 600).
- Source: NY Lab. § 600

### Out-of-Scope Programs [NOT-MODELED]

**REQ-037** [NOT-MODELED] Shared Work / Short-Time Compensation (STC) — § 599: employer-sponsored partial-hours alternative.
**REQ-038** [NOT-MODELED] Self-Employment Assistance Program (SEAP) — § 591-a.
**REQ-039** [NOT-MODELED] Extended Benefits (EB): federal/state program triggered by elevated unemployment rate; adds up to 13 weeks.
**REQ-040** [NOT-MODELED] Alternate base period automatic election (§ 527): claimant may request recalculation using alternate base period. PolicyEngine should offer this as an optional flag input.

### Dependent Allowance

**REQ-041** [EXEMPTION] NY does NOT provide a dependent allowance under regular UI (§ 590). No dependent-allowance variable is needed.
- Source: S1 (§ 590) — confirmed no subdivision for dependent allowance; confirmed distinct from PA, NJ, MA, CT which do have dependent allowances.
- Note: Some secondary sources erroneously suggest $25/dependent; this is incorrect.

---

## Suggested Variable Structure

```
policyengine_us/variables/gov/states/ny/dol/unemployment_insurance/
    ny_ui.py                              REQ-031 — annual benefit, defined_for eligible
    ny_ui_monetarily_eligible.py          REQ-012 — AND of 3 sub-tests
    ny_ui_high_quarter_wages.py           REQ-005 — input or derived from 4 quarterly inputs
    ny_ui_base_period_wages.py            REQ-004 — sum of 4 quarterly wages
    ny_ui_quarters_with_wages.py          REQ-006 — count of non-zero quarters
    ny_ui_second_high_quarter_wages.py    REQ-014 — second-highest quarterly wages (for 2/3-quarter formula)
    ny_ui_meets_high_quarter_test.py      REQ-007 — HQ >= minimum
    ny_ui_meets_quarters_test.py          REQ-009 — >= 2 quarters with wages
    ny_ui_meets_total_wages_test.py       REQ-010/011 — 1.5x or capped test
    ny_ui_weekly_benefit_rate.py          REQ-013–021 — WBR with divisor, min, max
    ny_ui_partial_benefit_credit.py       REQ-022 — ceil(max(0.5*WBR, 100))
    ny_ui_weekly_benefit_fraction.py      REQ-024 — fraction from hours-tier bracket
    ny_ui_weekly_payable.py               REQ-026,027 — WBR * fraction, with earnings cap
    ny_ui_maximum_benefit_amount.py       REQ-029 — WBR * 26
    ny_ui_weeks_unemployed.py             REQ-030 — input, int, 0-26
    ny_ui_gross_weekly_earnings.py        REQ-026 — input, non-self-employment earnings
```

Optional (for full quarterly wage decomposition):
```
    ny_ui_q1_wages.py  ny_ui_q2_wages.py  ny_ui_q3_wages.py  ny_ui_q4_wages.py
```

Simpler approach (following PA UC pattern): accept `ny_ui_high_quarter_wages` and `ny_ui_base_period_wages` as direct inputs; add `ny_ui_second_high_quarter_wages` for the 2/3-quarter formula; add `ny_ui_quarters_with_wages` as input.

---

## Suggested Parameter Structure

```
policyengine_us/parameters/gov/states/ny/dol/unemployment_insurance/
    index.yaml                            metadata: economy: false; household: true
    benefit/
        max_amount.yaml                   504 → 869 (2025-10-13)
        min_amount.yaml                   104 (hist.) → 140 (2026-01-01)
        divisor_threshold.yaml            3575
        divisor_high.yaml                 26
        divisor_low.yaml                  25
        two_quarter_threshold_high.yaml   4000  (for 2/3-quarter tier 1 vs 2)
        two_quarter_threshold_low.yaml    3575  (same as divisor_threshold; reuse or unify)
    eligibility/
        high_quarter_minimum.yaml         3400 (2025) → 3500 (2026-01-05)
        high_quarter_cap.yaml             19118 (2026; was ~11088 in earlier years)
        total_wages_multiplier.yaml       1.5
        min_quarters.yaml                 2
    duration/
        max_weeks.yaml                    26
    partial_benefit_credit/
        rate.yaml                         0.50
        floor.yaml                        100
    partial/
        hours_tiers.yaml                  bracket: 0→1.0, 11→0.75, 17→0.50, 22→0.25, 31→0.0
```

---

## Key Decision Points for Implementer

### Decision 1: Quarterly wage inputs vs. annual approximation

PolicyEngine's standard inputs are annual. Options:

**Option A** (Recommended — follows PA UC): Accept `ny_ui_high_quarter_wages` and `ny_ui_base_period_wages` as direct user inputs (no formula). The user or microdata layer supplies quarterly estimates. This is what PA UC does for `pa_uc_highest_quarter_wages` — it is a plain `Variable` with no `formula`.

**Option B** (Full quarterly decomposition): Create 4 quarterly input variables and derive HQ from max. More correct but adds 4 new inputs with no automatic formula.

**Option C** (Annual approximation): Derive HQ ≈ max(employment_income / 4, 0). This is a rough approximation and should be noted as a limitation. Acceptable for microsimulation; less accurate for individual use.

Recommendation: Implement Option A for launch. Document Option B as future enhancement.

### Decision 2: 2/3-quarter formula requires second-highest quarter wages

The 2/3-quarter formula (REQ-014) needs the second-highest quarterly wage. If using Option A/B, add `ny_ui_second_high_quarter_wages` as a direct input. If using Option C (annual approx), this cannot be derived and the 2/3-quarter case defaults to the standard HQ/26 or HQ/25 formula.

### Decision 3: Partial benefit hours tiers (REQ-024–027) require weekly hours worked

`weekly_hours_worked` exists already as an annual average variable (default 40). For partial benefit calculation, the intent is hours worked in a given certification week, not annual average. Options:

- Use `hours_worked_last_week` (already exists as YEAR-period input) as the input for partial benefit calculation. Accept that users input a representative week's hours.
- Accept a new `ny_ui_weekly_hours_worked` input specific to UI certification.

Recommendation: Use `hours_worked_last_week` or create `ny_ui_weekly_hours_worked` mirroring the PA UC `pa_uc_gross_weekly_earnings` pattern (state-namespaced input).

### Decision 4: Max WBR date boundary — 2025-10-13

Standard PE parameter date keys are `YYYY-MM-DD`. The October 13, 2025 effective date is a Sunday (first Monday = October 13 in some years — confirm: 2025-10-13 is a Monday). Use `2025-10-13` as the date key in `max_amount.yaml`.

### Decision 5: `high_quarter_cap` value — $11,088 or $19,118

The working_references.md cited $11,088 (from an earlier year's § 527 reading). P832 (Feb 2026) states $19,118. This strongly suggests the cap is indexed. Use $19,118 for 2026. Prior years' values ($11,088 likely for 2025 or earlier) should be encoded with their effective dates if backfilling.

---

## Worked Example Verification (from P832)

Claimant earns $4,500 in Q1 and $4,288 in Q3 (only 2 quarters with wages).

1. Quarters with wages: 2 → triggers 2/3-quarter formula
2. High quarter: $4,500 > $4,000 → REQ-014 applies: avg of 2 highest / 26
3. Average = ($4,500 + $4,288) / 2 = $4,394
4. WBR_raw = $4,394 / 26 = $169.0
5. WBR_floored = $169
6. Apply min ($140) / max ($869): $169 is within range → WBR = $169/week
7. Expected result: $169 ✓ (matches P832 example)

Monetary eligibility check:
- High quarter $4,500 ≥ $3,500 minimum ✓
- 2 quarters with wages ≥ 2 ✓
- Total wages = $4,500 + $4,288 = $8,788; 1.5 × $4,500 = $6,750; $8,788 ≥ $6,750 ✓ (high quarter < $19,118 cap so standard 1.5x applies)
- Result: monetarily eligible ✓

---

## Tests to Write

The following YAML test cases should be created at `policyengine_us/tests/policy/baseline/gov/states/ny/dol/unemployment_insurance/`:

1. `ny_ui_weekly_benefit_rate.yaml` — 4-quarter case HQ>$3,575 (HQ/26), 4-quarter case HQ≤$3,575 (HQ/25), 2-quarter case HQ>$4,000 (avg/26), 2-quarter case $3,576–$4,000 (HQ/26), min floor ($140), max cap ($504 pre-Oct-2025, $869 post)
2. `ny_ui_monetarily_eligible.yaml` — pass all 3 tests, fail each individually, cap test edge
3. `ny_ui_partial_benefit_credit.yaml` — PBC = max(0.5*WBR, 100) with ceiling
4. `ny_ui_weekly_payable.yaml` — earnings cap disqualification, hours tier reductions
5. `ny_ui.yaml` — full benefit with weeks_unemployed × WBR, cap at MBA

P832 worked example should be a required test case for `ny_ui_weekly_benefit_rate`.

---

## Reference Implementation Paths

- PA UC variables: `/Users/daphnehansell/Documents/GitHub/policyengine-us/.claude/worktrees/pa-unemployment-insurance/policyengine_us/variables/gov/states/pa/dli/unemployment_compensation/`
- PA UC parameters: `/Users/daphnehansell/Documents/GitHub/policyengine-us/.claude/worktrees/pa-unemployment-insurance/policyengine_us/parameters/gov/states/pa/dli/unemployment_compensation/`
- Existing NY variables: `/Users/daphnehansell/Documents/GitHub/policyengine-us/policyengine_us/variables/gov/states/ny/`
- Federal unemployment stub: `/Users/daphnehansell/Documents/GitHub/policyengine-us/policyengine_us/variables/gov/states/unemployment_compensation.py`
- Weekly hours input: `/Users/daphnehansell/Documents/GitHub/policyengine-us/policyengine_us/variables/household/income/person/weekly_hours_worked.py`
- Hours worked last week input: `/Users/daphnehansell/Documents/GitHub/policyengine-us/policyengine_us/variables/household/income/person/hours_worked_last_week.py`
