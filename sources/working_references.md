# Collected Documentation

## Washington State Paid Family and Medical Leave (WA PFML)
**Collected**: 2026-04-22
**Implementation Task**: Implement Washington State's Paid Family and Medical Leave wage replacement benefit calculation in PolicyEngine US. The existing codebase already has the employee/employer contribution (premium) side; this task adds the benefit (wage replacement) side.

---

## Official Program Name

**Federal Program**: Paid Family and Medical Leave (state-level — no single federal program; federal FMLA is unpaid)
**State's Official Name**: Washington Paid Family and Medical Leave
**Abbreviation**: PFML (sometimes WPFML)
**Source**: RCW Title 50A — "Family and Medical Leave"
**Administrator**: Washington State Employment Security Department (ESD)

**Variable Prefix**: `wa_pfml`
**Legal Authority**:
- Statute: RCW Title 50A (Chapters 50A.05, 50A.10, 50A.15, 50A.20, 50A.24, 50A.25, 50A.30, 50A.35, 50A.40, 50A.45, 50A.50)
- Regulations: WAC Title 192, Chapters 192-500 through 192-810

**Existing implementation in codebase**:
- `policyengine_us/variables/gov/states/wa/tax/payroll/paid_leave/` — has contribution (premium) side
  - `wa_employee_paid_leave_contribution.py`
  - `wa_employer_paid_leave_contribution.py`
- `policyengine_us/parameters/gov/states/wa/tax/payroll/paid_leave/` — has contribution parameters
  - `total_rate.yaml` (0.92% in 2025, 1.13% in 2026)
  - `employer_share.yaml` (28.48% in 2025, 28.57% in 2026)
  - `employer_headcount_threshold.yaml` (50)

**NEW work**: Benefit (wage replacement) side — does not yet exist for any state in the codebase.

---

## 1. Source Information

### Primary Legal Authorities

| Source | Citation | URL | Notes |
|--------|----------|-----|-------|
| Statute — Eligibility | RCW 50A.15.010 | https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.010 | 820 hours in qualifying period |
| Statute — Benefit amount & duration (pre-2026) | RCW 50A.15.020 (Effective until January 1, 2026) | https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020 | Current law; min claim 8 hours |
| Statute — Benefit amount & duration (2026+) | RCW 50A.15.020 (Effective January 1, 2026) | https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020 | Min claim reduced to 4 hours |
| Statute — Definitions | RCW 50A.05.010 | https://app.leg.wa.gov/rcw/default.aspx?cite=50A.05.010 | AWW, SAWW, qualifying period, typical workweek hours |
| Statute — Premiums | RCW 50A.10.030 | https://app.leg.wa.gov/rcw/default.aspx?cite=50A.10.030 | Contribution rates |
| Regulations — Benefits | WAC Chapter 192-620 | https://app.leg.wa.gov/wac/default.aspx?cite=192-620&full=true | Weekly benefit procedures |
| Regulations — Definitions | WAC Chapter 192-500 | https://app.leg.wa.gov/wac/default.aspx?cite=192-500 | WAC definitions |
| Program website | Washington State Paid Leave | https://paidleave.wa.gov | Official ESD site |
| 2026 official paycheck insert | ESD | https://paidleave.wa.gov/app/uploads/2025/12/Paycheck-insert-2026-1.pdf | Official 2026 values |
| Legislative amendment (2025) | 2025 c 304 (ESSHB 1213) | https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020 | Effective 2026 |

**Effective Dates**: Program began January 1, 2020. Significant amendments via 2025 c 304 (ESSHB 1213) take effect January 1, 2026.

---

## 2. Key Rules and Thresholds

### 2.1 Eligibility — RCW 50A.15.010

Exact statutory text:
> "Employees are eligible for family and medical leave benefits as provided in this title after working for at least eight hundred twenty hours in employment during the qualifying period."

**Single explicit eligibility rule:**
- **820 hours in employment during the qualifying period** (this is the only numeric threshold in the eligibility statute)
- Hours can accumulate across multiple employers
- Federal employees, self-employed (unless opted-in), and employees of tribally-owned businesses on tribal land are excluded (administrative rules / program documentation)

### 2.2 Qualifying Period — RCW 50A.05.010(21)

Exact statutory text:
> "'Qualifying period' means the first four of the last five completed calendar quarters or, if eligibility is not established, the last four completed calendar quarters immediately preceding the application for leave."

### 2.3 Employee's Average Weekly Wage (AWW) — RCW 50A.05.010(6)

Exact statutory text:
> "'Employee's average weekly wage' means the quotient derived by dividing the employee's total wages during the two quarters of the employee's qualifying period in which total wages were highest by twenty-six. If the result is not a multiple of one dollar, the department must round the result to the next lower multiple of one dollar."

**Formula:**
```
AWW = floor( (wages in top two quarters of qualifying period) / 26 )
```

### 2.4 State Average Weekly Wage (SAWW) — RCW 50A.05.010(26)

> "'State average weekly wage' means the most recent average weekly wage calculated under RCW 50.04.355 and available on January 1st of each year."

Note: This is the official calculation done by ESD annually; values are fixed for PolicyEngine.

### 2.5 Typical Workweek Hours — RCW 50A.05.010(28)

> "(a) For an hourly employee, the average number of hours worked per week by an employee within the qualifying period; and
> (b) Forty hours for a salaried employee, regardless of the number of hours the salaried employee typically works."

**Key implementation note**: For salaried employees, hard value = 40 hours regardless of actual hours.

---

## 3. Weekly Benefit Formula — RCW 50A.15.020(5)

### Exact Statutory Language

Both current and 2026-effective versions contain identical formula language (percentages unchanged between versions):

> "(5) The weekly benefit for family and medical leave shall be determined as follows: If the employee's average weekly wage is:
> (a) Equal to or less than one-half of the state average weekly wage, then the benefit amount is equal to 90 percent of the employee's average weekly wage; or
> (b) greater than one-half of the state average weekly wage, then the benefit amount is the sum of:
>   (i) Ninety percent of one-half of the state average weekly wage; and
>   (ii) 50 percent of the difference of the employee's average weekly wage and one-half of the state average weekly wage."

### Formula (Mathematical)

Let:
- `AWW` = employee's average weekly wage
- `SAWW` = state average weekly wage
- `H` = 0.5 × SAWW (half the state average weekly wage; the breakpoint)

**Uncapped, unfloored benefit:**
```
if AWW <= H:
    benefit = 0.90 × AWW
else:
    benefit = 0.90 × H + 0.50 × (AWW - H)
```

Then apply ceiling and floor (see next sections).

### Minimum and Maximum — RCW 50A.15.020(6)

**Maximum weekly benefit (RCW 50A.15.020(6)(a)):**
> "The maximum weekly benefit for family and medical leave that occurs on or after January 1, 2020, shall be $1,000. By September 30, 2020, and by each subsequent September 30th, the commissioner shall adjust the maximum weekly benefit amount to 90 percent of the state average weekly wage. The adjusted maximum weekly benefit amount takes effect on the following January 1st."

So `max_weekly_benefit = 0.90 × SAWW` (rounded; value is set by commissioner and takes effect January 1 each year).

**Minimum weekly benefit (RCW 50A.15.020(6)(b)):**
> "The minimum weekly benefit shall not be less than $100 per week except that if the employee's average weekly wage at the time of family or medical leave is less than $100 per week, the weekly benefit shall be the employee's full wage."

### Rounding — RCW 50A.15.020(2)(a)

> "The benefits in this section, if not a multiple of one dollar, shall be reduced to the next lower multiple of one dollar."

Apply `floor()` to the final benefit amount (before comparing to min/max).

### Full Pseudocode

```
def weekly_benefit(AWW, SAWW):
    H = 0.5 * SAWW
    if AWW <= H:
        raw = 0.90 * AWW
    else:
        raw = 0.90 * H + 0.50 * (AWW - H)
    raw = floor(raw)                # to next lower dollar (RCW 50A.15.020(2)(a))
    max_wb = 0.90 * SAWW            # published annually by commissioner
    # Apply min/max floor/ceiling:
    if AWW < 100:                   # special case: if AWW < $100, benefit = full AWW
        return AWW
    return max(100, min(raw, max_wb))
```

### Prorating — RCW 50A.15.020(2)

> "The weekly benefit shall be prorated by the percentage of hours on leave compared to the number of hours provided as the typical workweek hours as defined in RCW 50A.05.010."

For implementation at the weekly level (full-week leave), proration is 1.0. Partial-week proration may be out of scope for the simplified implementation.

### Example Calculations (2026 values)

With **SAWW = $1,830** (2026), `H = $915`:

| AWW | Tier | Formula | Result | After min/max |
|-----|------|---------|--------|---------------|
| $500 | Low | 0.90 × $500 | $450 | $450 |
| $915 | At threshold | 0.90 × $915 | $823 (floor of 823.50) | $823 |
| $1,200 | High | 0.90 × $915 + 0.50 × ($1,200 − $915) = $823.50 + $142.50 | $966 (floor of 966) | $966 |
| $1,500 | High | $823.50 + 0.50 × $585 = $823.50 + $292.50 | $1,116 | $1,116 |
| $2,562 | High | $823.50 + 0.50 × ($2,562 − $915) = $823.50 + $823.50 | $1,647 | $1,647 (at cap) |
| $3,000 | High | $823.50 + 0.50 × $2,085 = $823.50 + $1,042.50 | $1,866 (floor) | **$1,647** (capped) |
| $80 | Very low (AWW < $100) | AWW | $80 | $80 (full wage, not the $100 floor) |

---

## 4. Duration Limits — RCW 50A.15.020(3)

Exact statutory text:
> "(3)(a) The maximum duration of paid family leave may not exceed 12 times the typical workweek hours during a period of 52 consecutive calendar weeks.
> (b) The maximum duration of paid medical leave may not exceed 12 times the typical workweek hours during a period of 52 consecutive calendar weeks. This leave may be extended an additional two times the typical workweek hours if the employee experiences a serious health condition with a pregnancy that results in incapacity.
> (c) An employee is not entitled to paid family and medical leave benefits under this title that exceeds a combined total of 16 times the typical workweek hours. The combined total of family and medical leave may be extended to 18 times the typical workweek hours if the employee experiences a serious health condition with a pregnancy that results in incapacity."

### Summary Table (durations measured in "typical workweek hours")

| Leave Type | Standard Maximum | Pregnancy-Extension Maximum |
|------------|-----------------:|----------------------------:|
| Family leave only | 12× typical workweek hours | 12× (no pregnancy extension for family leave alone) |
| Medical leave only | 12× typical workweek hours | 14× typical workweek hours |
| Combined family + medical | 16× typical workweek hours | 18× typical workweek hours |

**In practical weekly terms** (for full-time workers with a 40-hour typical workweek):
- Family leave: up to 12 weeks
- Medical leave: up to 12 weeks (14 weeks with pregnancy-related incapacity)
- Combined: up to 16 weeks (18 weeks with pregnancy-related incapacity)

Measurement period: 52 consecutive calendar weeks.

---

## 5. Waiting Period — RCW 50A.15.020(1)(a)

Exact text:
> "Following a waiting period consisting of the first seven consecutive calendar days, benefits are payable when family or medical leave is required. However, no waiting period is required for leave for the birth or placement of a child, or for leave because of any qualifying exigency as defined under RCW 50A.05.010(10)(c)."

**Waived for**: birth or placement of a child, qualifying military exigency. Not waived for medical leave or care-for-family-member leave.

---

## 6. Minimum Claim Duration — RCW 50A.15.020(2)(c)

- **Until January 1, 2026**: "The minimum claim duration payment is for **eight consecutive hours** of leave."
- **Effective January 1, 2026** (per 2025 c 304 / ESSHB 1213): "The minimum claim duration payment is for **four consecutive hours** of leave."

---

## 7. Qualifying Events (from RCW 50A.05.010 definitions)

Leave is available for a **qualifying event**, which falls under either family leave or medical leave:

### Family Leave (RCW 50A.05.010(9))
- Care for a family member with a serious health condition
- Bonding with a new child (birth, adoption, or foster placement) during the first 12 months
- Qualifying military exigency (as defined under federal FMLA — 29 U.S.C. § 2612(a)(1)(E) as of Oct 19, 2017)

### Medical Leave (RCW 50A.05.010(13))
- Employee's own serious health condition (including pregnancy-related incapacity)

### Family Member — RCW 50A.05.010(8)
Includes: child, grandchild, grandparent, parent, sibling, spouse, **plus** any individual who regularly resides in the employee's home and depends on the employee for care.

### Serious Health Condition — RCW 50A.05.010(23)
Illness, injury, impairment, or physical/mental condition involving:
- Inpatient care; or
- Continuing treatment by a health care provider

---

## 8. Time-Series Values (for parameters)

### 8.1 Maximum Weekly Benefit (published annually by commissioner)

| Effective Date | Max Weekly Benefit | Source |
|---------------:|-------------------:|--------|
| 2020-01-01 | $1,000 | RCW 50A.15.020(6)(a) (statutory initial value) |
| 2021-01-01 | $1,206 | Historical published value |
| 2022-01-01 | $1,327 | Historical published value |
| 2023-01-01 | $1,427 | Historical published value |
| 2024-01-01 | $1,456 | Historical published value |
| 2025-01-01 | $1,542 | ESD 2025 announcement |
| 2026-01-01 | $1,647 | ESD 2026 paycheck insert |

**Derived relationship**: max = 0.90 × SAWW (applied by commissioner each September for following January).

**Source for 2026 value**: https://paidleave.wa.gov/app/uploads/2025/12/Paycheck-insert-2026-1.pdf

### 8.2 State Average Weekly Wage (SAWW) used in formula

The SAWW used in the formula for a given claim year is the SAWW effective January 1 of that year. (Derived from max = 0.90 × SAWW, and confirmed by ESD announcements.)

| Effective Date | SAWW | Notes |
|---------------:|-----:|-------|
| 2020-01-01 | ~$1,111 | Implied from $1,000 max ÷ 0.9 |
| 2021-01-01 | ~$1,340 | Implied |
| 2022-01-01 | ~$1,474 | Implied |
| 2023-01-01 | ~$1,586 | Implied |
| 2024-01-01 | ~$1,618 | Announced as WA 2022 avg wage; applied 2024 |
| 2025-01-01 | ~$1,714 | Announced as WA 2023 avg wage; applied 2025 |
| 2026-01-01 | $1,830 | Confirmed by ESD; max = 0.90 × $1,830 = $1,647 |

**Important**: For the purposes of this implementation, the benefit formula needs both **SAWW** (to define the breakpoint `H = 0.5 × SAWW`) and the **max weekly benefit** (which is itself 0.90 × SAWW). So a single `saww` parameter is sufficient; the max can be computed as `0.90 × saww`, OR store both parameters and derive nothing.

**Recommendation**: Store SAWW as the primary parameter and derive `max = 0.90 × SAWW` in code. This matches how ESD actually operates.

### 8.3 Minimum Weekly Benefit

| Effective Date | Min Weekly Benefit | Source |
|---------------:|-------------------:|--------|
| 2020-01-01 | $100 | RCW 50A.15.020(6)(b) — flat $100 from program start |

Never changed in statute. Special case: if AWW < $100, the benefit = AWW (employee's "full wage"), not the $100 minimum.

### 8.4 Benefit Formula Percentages (constant since inception)

| Parameter | Value | Source |
|-----------|------:|--------|
| Low-tier replacement rate | 0.90 (90%) | RCW 50A.15.020(5)(a) |
| High-tier base component | 0.90 of 0.5 × SAWW | RCW 50A.15.020(5)(b)(i) |
| High-tier marginal rate | 0.50 (50%) | RCW 50A.15.020(5)(b)(ii) |
| SAWW breakpoint fraction | 0.50 (1/2 of SAWW) | RCW 50A.15.020(5)(a)(b) |

### 8.5 Duration Parameters (constant)

| Parameter | Value | Source |
|-----------|------:|--------|
| Family leave max (× typical workweek hours) | 12 | RCW 50A.15.020(3)(a) |
| Medical leave max (× typical workweek hours) | 12 | RCW 50A.15.020(3)(b) |
| Medical leave max with pregnancy extension | 14 | RCW 50A.15.020(3)(b) |
| Combined max (× typical workweek hours) | 16 | RCW 50A.15.020(3)(c) |
| Combined max with pregnancy extension | 18 | RCW 50A.15.020(3)(c) |
| Measurement period (weeks) | 52 | RCW 50A.15.020(3)(a)(b) |
| Waiting period (days) | 7 | RCW 50A.15.020(1)(a) |

### 8.6 Eligibility Hours Threshold

| Parameter | Value | Source |
|-----------|------:|--------|
| Hours in qualifying period | 820 | RCW 50A.15.010 |

### 8.7 Minimum Claim Duration

| Effective Date | Value (hours) | Source |
|---------------:|--------------:|--------|
| 2020-01-01 | 8 | RCW 50A.15.020(2)(c) (pre-2026) |
| 2026-01-01 | 4 | RCW 50A.15.020(2)(c) as amended by 2025 c 304 |

### 8.8 Typical Workweek Hours (salaried)

| Parameter | Value (hours) | Source |
|-----------|--------------:|--------|
| Hours for salaried employee | 40 | RCW 50A.05.010(28)(b) |

---

## 9. Identifying Derived Values

### Maximum weekly benefit = 90% of SAWW

**Legal citation**: RCW 50A.15.020(6)(a)
**Quote**: "By September 30, 2020, and by each subsequent September 30th, the commissioner shall adjust the maximum weekly benefit amount to 90 percent of the state average weekly wage."

**Implementation implication**: Store SAWW and compute `max = 0.90 * SAWW` in the variable formula. This guarantees the relationship is preserved as SAWW updates. Alternatively, since ESD publishes a specific rounded dollar amount, store both separately.

**Decision for implementation**: Store **both** SAWW and the published max weekly benefit (as the commissioner's published value may differ slightly due to rounding conventions). Cross-check: `0.9 × 1830 = 1647.00` — exact match, confirms no rounding divergence.

### Breakpoint = 50% of SAWW

**Legal citation**: RCW 50A.15.020(5)(a)(b)
**Quote**: "Equal to or less than one-half of the state average weekly wage" / "greater than one-half of the state average weekly wage"

**Implementation implication**: Compute `H = 0.5 * SAWW` in the variable formula. No separate parameter needed — the fraction is statutorily fixed.

---

## 10. Special Cases and Exceptions

### 10.1 Low-wage floor exception
- If `AWW < $100/week`, the benefit = `AWW` (not $100 minimum).
- Source: RCW 50A.15.020(6)(b): "if the employee's average weekly wage at the time of family or medical leave is less than one hundred dollars per week, the weekly benefit shall be the employee's full wage."

### 10.2 Waiting period waivers
- Waived for: birth/placement of a child, qualifying military exigency.
- Not waived for: medical leave (own serious health condition), family leave to care for a family member.
- Source: RCW 50A.15.020(1)(a).

### 10.3 Rounding rules
- Benefit amount: rounded down to next lower dollar. Source: RCW 50A.15.020(2)(a).
- AWW itself: rounded down to next lower dollar. Source: RCW 50A.05.010(6).
- Hours on leave: rounded down to next lower hour. Source: RCW 50A.15.020(2)(b).

### 10.4 Non-eligible worker categories
- Federal government employees
- Self-employed individuals (unless opted in via elective coverage — RCW 50A.10.010)
- Employees of tribally-owned businesses on tribal land (unless tribe opts in)

### 10.5 Prorating for partial-week leave
- Weekly benefit prorated by `(hours on leave) / (typical workweek hours)`.
- Source: RCW 50A.15.020(2).
- **Implementation note**: A simplified annual/weekly implementation can assume full-week leave (proration factor = 1).

---

## 11. Contribution (Premium) Side — Already Implemented

The contribution side is already present in the codebase. Documenting here for completeness/context only; no changes needed unless values need updating.

### Current parameters in `policyengine_us/parameters/gov/states/wa/tax/payroll/paid_leave/`:

**total_rate.yaml** (premium rate — paid by employee + employer combined, as % of wages):
| Effective | Rate | Source |
|-----------|-----:|--------|
| 2025-01-01 | 0.92% | 2025 ESD announcement |
| 2026-01-01 | 1.13% | 2026 ESD paycheck insert |

**employer_share.yaml** (employer share of total premium):
| Effective | Rate | Source |
|-----------|-----:|--------|
| 2025-01-01 | 28.48% | 2025 ESD announcement |
| 2026-01-01 | 28.57% | 2026 ESD paycheck insert |

**employer_headcount_threshold.yaml**: 50 (employers with fewer than 50 employees are exempt from the employer share but still collect the employee share)
- Source: RCW 50A.10.030

**Taxable wages cap**: Social Security wage base ($184,500 for 2026)
- Source: RCW 50A.10.030; aligns with federal SS wage base.

---

## 12. Implementation Approach for PolicyEngine

### 12.1 Variables Needed (benefit side — NEW)

**Design decision**: Since PFML is a wage-replacement benefit that depends on past earnings (during qualifying period) and a leave event, the cleanest implementation models the **maximum potential annual benefit** if the worker took the full allowed leave. This is analogous to how unemployment insurance benefits are modeled in PolicyEngine.

A more modest implementation: given a user-supplied **leave weeks** input variable, compute the benefit.

Required variables (recommended set, Person entity, YEAR period, `defined_for = StateCode.WA`):

1. `wa_pfml_average_weekly_wage` — employee's AWW per RCW 50A.05.010(6). Simplified: `employment_income / 52`. (Note: regulatory definition is more complex; a simplification is acceptable.)
2. `wa_pfml_eligible` — boolean: did employee work 820+ hours in qualifying period?
3. `wa_pfml_weekly_benefit_uncapped` — computes the two-tier formula on AWW without min/max.
4. `wa_pfml_weekly_benefit` — applies floor/ceiling and special low-wage case.
5. `wa_pfml_weeks_of_leave` — user input (default 0): weeks of paid leave taken.
6. `wa_pfml_leave_type` — enum input (default = NONE): FAMILY / MEDICAL / COMBINED / MEDICAL_PREGNANCY / COMBINED_PREGNANCY.
7. `wa_pfml_max_weeks` — based on leave type, returns 12/14/16/18 per leave type.
8. `wa_pfml` — Person-level annual benefit = weekly_benefit × min(weeks_of_leave, max_weeks).

### 12.2 Parameters Needed (benefit side — NEW)

Organize under `policyengine_us/parameters/gov/states/wa/esd/pfml/` (Employment Security Department / PFML):

```
gov/states/wa/esd/pfml/
├── eligibility/
│   └── hours_threshold.yaml          # 820 hours
├── benefit/
│   ├── saww.yaml                      # SAWW annual values
│   ├── max_weekly_benefit.yaml        # Max = 0.9 × SAWW
│   ├── min_weekly_benefit.yaml        # $100
│   ├── low_tier_rate.yaml             # 0.90
│   ├── high_tier_marginal_rate.yaml   # 0.50
│   └── breakpoint_share.yaml          # 0.50 of SAWW
└── duration/
    ├── family_leave_weeks.yaml        # 12
    ├── medical_leave_weeks.yaml       # 12
    ├── medical_leave_weeks_pregnancy.yaml   # 14
    ├── combined_weeks.yaml            # 16
    └── combined_weeks_pregnancy.yaml  # 18
```

Alternative (cleaner): use a single `duration/by_type.yaml` breakdown by leave-type enum, rather than separate files.

### 12.3 Reference Implementation Note

No existing state in policyengine-us implements the **benefit** side of a PFML program — only contributions (DC, MA, NY, CT, DE, ME, OR, NJ, WA). So this implementation does not have a direct state analog to follow; model after how other wage-replacement benefits are implemented (e.g., unemployment compensation).

Suggested analogs to study:
- Unemployment compensation variables (federal and state level)
- `ca_sdi` (California State Disability Insurance) if it exists
- `ny_paid_family_leave` benefit variables if they exist

---

## 13. References for Metadata

### For Parameters (YAML format)

**Primary eligibility (820 hours):**
```yaml
reference:
  - title: RCW 50A.15.010 Employee eligibility
    href: https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.010
```

**Weekly benefit formula & amounts:**
```yaml
reference:
  - title: RCW 50A.15.020 Benefit—Amount and duration (Effective January 1, 2026)
    href: https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020
  - title: Washington Paid Family and Medical Leave 2026 Paycheck Insert
    href: https://paidleave.wa.gov/app/uploads/2025/12/Paycheck-insert-2026-1.pdf
```

**Duration limits:**
```yaml
reference:
  - title: RCW 50A.15.020(3) Benefit—Amount and duration
    href: https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020
```

**AWW definition:**
```yaml
reference:
  - title: RCW 50A.05.010(6) Employee's average weekly wage
    href: https://app.leg.wa.gov/rcw/default.aspx?cite=50A.05.010
```

**SAWW definition:**
```yaml
reference:
  - title: RCW 50A.05.010(26) State average weekly wage
    href: https://app.leg.wa.gov/rcw/default.aspx?cite=50A.05.010
```

**Qualifying period:**
```yaml
reference:
  - title: RCW 50A.05.010(21) Qualifying period
    href: https://app.leg.wa.gov/rcw/default.aspx?cite=50A.05.010
```

### For Variables (Python format)

```python
reference = (
    "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020",
    "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.05.010",
    "https://paidleave.wa.gov/app/uploads/2025/12/Paycheck-insert-2026-1.pdf",
)
```

---

## 14. Quality Gate Checklist

- [x] Benefit calculation formula — RCW 50A.15.020(5) with exact statutory text
- [x] Eligibility thresholds — 820 hours in qualifying period (RCW 50A.15.010)
- [x] Maximum weekly benefit amounts — values for 2020–2026 documented
- [x] Minimum weekly benefit — $100 (with low-wage exception) from RCW 50A.15.020(6)(b)
- [x] Duration limits — family (12x), medical (12x or 14x), combined (16x or 18x) from RCW 50A.15.020(3)
- [x] Waiting period — 7 days, with exceptions for birth/placement/military (RCW 50A.15.020(1)(a))
- [x] Qualifying events — family leave and medical leave definitions (RCW 50A.05.010)
- [x] Authoritative sources — RCW Title 50A, WAC Title 192, ESD official PDF
- [x] Official program name — Washington Paid Family and Medical Leave (WA PFML)
- [x] Legal citations for percentages — confirmed 90%/50%/50% all in RCW 50A.15.020(5)
- [x] Legal citation for max = 90% SAWW — RCW 50A.15.020(6)(a)

---

## 15. Additional Notes for Implementers

### 15.1 Simplification Guidance

Given the complexity of the actual program (quarterly wage analysis, leave event types, prorating, waiting periods), PolicyEngine's implementation should focus on what can be modeled from available household variables:

**Reasonable simplifications:**
- Use annual `employment_income / 52` as a proxy for AWW (exact quarterly calculation requires quarterly wage data not available in PolicyEngine)
- Use hours-worked proxy (e.g., `max_(employment_income, 0) > 0`) or assume eligibility for any worker with positive earnings as a baseline, then refine
- Model at the **Person** entity level (benefits are individual) with YEAR period
- Default leave weeks = 0 (user input activates the benefit)

### 15.2 Contribution Side Integration

The existing `wa_employee_paid_leave_contribution` and `wa_employer_paid_leave_contribution` variables should remain as-is. The benefit (new) is a **separate concept** — most people pay in but never collect; the benefit is triggered by a specific leave event.

### 15.3 Out-of-Scope Items

The following are documented in the statute but should likely be OUT of a simplified PolicyEngine implementation:
- Voluntary/employer-sponsored equivalent plans (RCW 50A.30)
- Supplemental employer benefit payments (WAC 192-620-030)
- Child support deductions from benefits (WAC 192-620-045)
- Overpayment recovery (RCW 50A.45)
- Appeals procedures (RCW 50A.50)
- Waiting period mechanics within a claim year
- Conditional benefit payments during eligibility disputes

### 15.4 Values Are Annual / Calendar-Year

Per RCW 50A.15.020(6)(a), the max weekly benefit "takes effect on the following January 1st." The SAWW "available on January 1st of each year" per RCW 50A.05.010(26). So all parameter effective dates should be `YYYY-01-01`.

---
