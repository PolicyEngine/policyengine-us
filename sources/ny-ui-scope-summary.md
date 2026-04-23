# NY UI Scope Summary

| Field | Value |
|---|---|
| Program name | New York State Unemployment Insurance (UI) |
| State agency | NYSDOL — Unemployment Insurance Division |
| Variable prefix | `ny_ui` |
| Total requirements | 41 |
| Simulatable requirements | 31 |
| Not-modeled requirements | 9 |
| Complexity | MEDIUM-HIGH |
| Primary reference impl | PA UC (`pa-unemployment-insurance` worktree) |

---

## Reference Implementation Paths

| Item | Path |
|---|---|
| PA UC variables | `.claude/worktrees/pa-unemployment-insurance/policyengine_us/variables/gov/states/pa/dli/unemployment_compensation/` |
| PA UC parameters | `.claude/worktrees/pa-unemployment-insurance/policyengine_us/parameters/gov/states/pa/dli/unemployment_compensation/` |
| Existing NY variables | `policyengine_us/variables/gov/states/ny/` |
| Federal UC stub | `policyengine_us/variables/gov/states/unemployment_compensation.py` |
| Weekly hours input | `policyengine_us/variables/household/income/person/weekly_hours_worked.py` |

---

## Key Decision Points

### 1. Quarterly wage inputs

**Problem**: PolicyEngine models annual household income; NY UI eligibility and WBR calculations require wages broken down by base-period calendar quarter.

**Options**:

| Option | Approach | Tradeoff |
|---|---|---|
| A (Recommended) | Accept `ny_ui_high_quarter_wages`, `ny_ui_base_period_wages`, `ny_ui_second_high_quarter_wages`, `ny_ui_quarters_with_wages` as direct user inputs (no formula). Follows PA UC pattern. | Correct for calculator use; requires user to supply quarterly breakdown. Microsimulation will need to approximate. |
| B | Create 4 quarterly wage inputs (`ny_ui_q1_wages` etc.) and derive HQ, base total, and quarter count. | More granular; still requires manual user input or approximation from microdata. |
| C | Derive HQ ≈ `employment_income / 4`. | Crude approximation; adequate for rough microsimulation policy impact but not for individual accuracy. |

**Recommendation**: Option A for initial implementation. Document Option B as future enhancement. Add a note in variable `documentation` that quarterly wage inputs should be provided by the user or approximated by the microdata layer.

### 2. Partial benefit hours tiers — weekly hours worked input

**Problem**: The 5-tier hours bracket (REQ-024) requires the total hours worked in a specific UI certification week, not an annual average.

**Options**:

| Option | Approach |
|---|---|
| Use `hours_worked_last_week` | Existing YEAR-period input representing the most recent week's hours. Semantically close to certification-week hours. |
| Create `ny_ui_weekly_hours_worked` | New state-namespaced input mirroring `pa_uc_gross_weekly_earnings` pattern — cleaner for NY-specific semantics. |
| Use `weekly_hours_worked` | Existing YEAR-period average hours variable (default 40). Inappropriate for UI partial — this is a labor supply variable, not a partial-unemployment input. |

**Recommendation**: Create `ny_ui_weekly_hours_worked` (float, Person, YEAR, unit="hour") as a state-namespaced input. This follows the same pattern as `pa_uc_gross_weekly_earnings` (state-specific input variable with no formula). Note in documentation that this should represent hours worked in the UI certification week.

### 3. Maximum WBR date change — 2025-10-13

**Problem**: The max WBR changed on October 13, 2025 ($504 → $869), which is a non-January date key. PolicyEngine supports any `YYYY-MM-DD` key.

**Solution**: Use `2025-10-13` as the date key in `benefit/max_amount.yaml`. This is straightforward. Note that `2025-10-13` is a Monday; P832 confirms "effective the first Monday of October 2025."

**Partial earnings cap alignment**: The $869 gross-earnings cap in the partial benefit rule (P803) ties directly to the max WBR. The parameter `benefit/max_amount` can serve double duty — both as the WBR cap and as the partial-earnings disqualification threshold. This avoids duplicating the value.

### 4. High-quarter cap indexing ($11,088 vs $19,118)

**Problem**: The cap used in the 1.5x eligibility test appears to change over time. Working notes cited $11,088 (likely a prior-year figure); P832 (Feb 2026) states $19,118.

**Solution**: Use date-keyed parameter `eligibility/high_quarter_cap.yaml` with at minimum:
- `2026-01-01: 19118` (P832 Feb 2026 value)
- Earlier values should be researched and backfilled when extending coverage years.

**Important**: The $11,088 figure in earlier working notes and the original REQ text should be treated as a stale reference. $19,118 / $9,559 are the 2026 values per the authoritative P832 document.

### 5. Minimum WBR — $104 vs $140

**Problem**: Working notes cited $104 as the statutory minimum; P832 (Feb 2026) states $140 as of January 2026 (and mentions $143 as a practical floor for the 4-quarter/HQ>$3,575 case).

**Solution**: Use date-keyed parameter `benefit/min_amount.yaml`:
- `2020-01-01: 104` (historical, for coverage year backfill)
- `2026-01-01: 140` (P832 Feb 2026)

The $143 figure mentioned in P832 for the HQ>$3,575/4-quarter case likely refers to the formula minimum (i.e., the smallest WBR that would result from HQ=$3,576 using divisor 26: floor(3576/26) = 137, which is below $143; this suggests a higher statutory floor may apply in that case). Encode $140 as the general minimum and flag this ambiguity for legal review.

---

## Complexity Factors

1. **Three-tier WBR formula**: 4-quarter case vs. 2/3-quarter case (with its own 3-tier sub-formula). More complex than most state UI implementations.
2. **Two-pronged eligibility test**: Standard 1.5x rule and capped alternative; both require total base wages vs. HQ comparisons.
3. **Hours-based partial benefit**: Requires a weekly hours input that has no natural analog in PolicyEngine's annual-income model.
4. **Mid-year parameter change**: $504 → $869 max effective 2025-10-13 requires non-January date key.
5. **No rate table**: Unlike PA UC (which uses a statutory lookup table), NY UI uses formulas. The formula-based approach is cleaner in code but requires careful NumPy vectorization.
6. **Partial earnings cap = max WBR**: These two parameters are identical in value, allowing parameter reuse — but the relationship must be documented clearly.
7. **No dependent allowance**: Simpler than PA UC; no dependent-related variables needed.
