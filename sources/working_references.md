# Collected Documentation

## New York State Unemployment Insurance (NY UI) — Implementation

**Collected**: 2026-04-23
**Implementation Task**: Encode New York Unemployment Insurance weekly benefit calculation, eligibility, and partial benefit rules.

---

## Official Program Name

- **Federal Program**: State Unemployment Insurance (Title III Social Security Act / FUTA 26 USC Chapter 23)
- **State's Official Name**: Unemployment Insurance (UI)
- **Administering Agency**: New York State Department of Labor (NYSDOL), Unemployment Insurance Division
- **Statutory Authority**: NY Labor Law Article 18 — Unemployment Insurance Law (sections 500-603)
- **Source**: NY Labor Law § 500 et seq.

**Variable Prefix**: `ny_ui`

---

## Key Statutory Structure (NY Labor Law Article 18)

Article 18 is divided into Titles:
- **Title 2** — Definitions (§§ 510-530): Partial benefit credit, total/partial unemployment, employment, remuneration, etc.
- **Title 3** — Contributions by Employers (§§ 550-584)
- **Title 7** — Benefits and Claims (§§ 590-603):
  - § 590 — Rights to benefits (the main benefit-amount statute)
  - § 591 — Eligibility for benefits
  - § 591-a — Self-Employment Assistance Program (SEAP)
  - § 592 — Suspension of accumulation
  - § 593 — Disqualifications (voluntary quit, misconduct, refusal of work)
  - § 596 — Claim filing, registration, and reporting
  - § 599 — Shared Work Program (STC)

### Key Sections for Benefit Calculation
| Section | Topic | Authority |
|---|---|---|
| § 517 | Remuneration / Wages | Definitions |
| § 522 | Total and Partial Unemployment | Definitions |
| § 524 | Base Period | Definitions |
| § 525 | Partial Benefit Credit | Definitions |
| § 527 | Valid Original Claim (earnings tests) | Eligibility |
| § 590(5) | Weekly Benefit Amount formula | Benefit calc |
| § 591 | Able/Available/Actively Seeking | Eligibility |

---

## Source Information

### Primary Legal Authority (Statutes)

| Section | Title | URL |
|---|---|---|
| NY Lab. § 590 | Rights to benefits | https://www.nysenate.gov/legislation/laws/LAB/590 |
| NY Lab. § 591 | Eligibility for benefits | https://www.nysenate.gov/legislation/laws/LAB/591 |
| NY Lab. § 527 | Valid original claim | https://www.nysenate.gov/legislation/laws/LAB/527 |
| NY Lab. § 525 | Partial benefit credit | https://www.nysenate.gov/legislation/laws/LAB/525 |
| NY Lab. § 522 | Total and partial unemployment | https://www.nysenate.gov/legislation/laws/LAB/522 |
| NY Lab. Article 18 | Unemployment Insurance Law (full) | https://www.nysenate.gov/legislation/laws/LAB/A18 |
| Justia Article 18 | 2025 codified version | https://law.justia.com/codes/new-york/lab/article-18/ |
| FindLaw § 590 | NY Labor Law § 590 | https://codes.findlaw.com/ny/labor-law/lab-sect-590/ |
| FindLaw § 525 | NY Labor Law § 525 (Partial Benefit Credit) | https://codes.findlaw.com/ny/labor-law/lab-sect-525/ |

### NYSDOL Operational Documents

| Document | URL | Notes |
|---|---|---|
| How Your Weekly UI Benefit Payment is Calculated (P832, 2025 version) | https://dol.ny.gov/system/files/documents/2025/01/how-your-weekly-unemployment-insurance-benefit-payment-is-calculated-p832.pdf | PDF could not be downloaded (bash curl denied); contains worked examples of high-quarter calculation |
| Maximum Benefit Rate explainer | https://dol.ny.gov/mbr | Public-facing page for current MBR |
| How Much Will My Benefit Be? | https://dol.ny.gov/how-much-will-my-benefit-be | Benefit rate overview |
| Estimate Weekly UI Benefits (calculator) | https://ux.labor.ny.gov/benefit-rate-calculator/ | Official benefit-rate calculator |
| Partial Unemployment Benefit Calculator | https://ux.labor.ny.gov/partial-unemployment-ben-calc/ | Official partial benefit calculator |
| Partial Unemployment Eligibility | https://dol.ny.gov/unemployment/partial-unemployment-eligibility | Hours-based tier explainer |
| Workforce Forward: Partial Unemployment FAQs (P803, Oct 2025) | https://dol.ny.gov/system/files/documents/2025/10/p803-partial-ui-faqs-10-3-25.pdf | PDF; not downloaded — HTML version available at https://dol.ny.gov/workforce-forward-partial-unemployment-faqs-p803-english |
| UI Benefits: Employer's Guide (IA 318.2, Dec 2025) | https://forms.labor.ny.gov/UI/IA318.2.pdf | PDF; not downloaded — HTML version at https://dol.ny.gov/employers-guide-unemployment-insurance-benefits-ia3182 |
| Certify for Weekly UI Benefits | https://dol.ny.gov/unemployment/certify-weekly-unemployment-insurance-benefits | Work-day definition |
| Before You File a Claim FAQs | https://dol.ny.gov/you-file-claim-unemployment-faqs | Base-period/earnings-test explainer |
| Governor's Announcement on Max Benefit Increase to $869 | https://www.governor.ny.gov/news/governor-hochul-and-labor-leaders-announce-maximum-weekly-benefit-increase-unemployed-workers | Oct 13, 2025 effective date |

---

## Effective Dates and Recent Changes

- **2020-01-01 through 2025-10-12**: Maximum weekly benefit frozen at **$504** (UI Trust Fund federal loan deficit)
- **2025-10-13**: Maximum weekly benefit increased to **$869** (FY26 enacted budget, $7B repayment of federal UI Trust Fund loan)
- **Annually thereafter**: Max benefit indexed at **50% of the state average weekly wage (SAWW)**
- **2021-08-16**: Partial benefit calculation moved from days-based to **hours-based tiers**
- **High-quarter threshold** ($3,575) — used to determine 1/25 vs 1/26 divisor (indexed over time; historical value)

---

## Key Rules and Thresholds

### 1. Eligibility — § 527 Valid Original Claim (Monetary)

To have a "valid original claim," a claimant must satisfy earnings tests during the base period:

**Basic (Standard) Base Period**: First 4 of last 5 completed calendar quarters before claim effective date
**Alternate Base Period** (§ 527): Last 4 completed calendar quarters (used if basic period fails)

**Monetary Earnings Tests** (all three must be met):
1. **High-quarter minimum**: Claimant must have at least a specified minimum in the highest-earning quarter
   - 2025 claims: **$3,400**
   - 2026 claims (effective Jan 5, 2026): **$3,500**
2. **Work in at least 2 quarters**: Must have remuneration paid in at least 2 calendar quarters of the base period
3. **1.5× ratio**: Total base period wages must be at least **1.5 × high-quarter wages**
   - **Cap**: If high-quarter wages ≥ $11,088, the "1.5×" requirement is replaced with the requirement that the claimant be paid at least half of $11,088 = **$5,544** in the other three quarters (i.e., total ≥ $11,088 + $5,544 = $16,632)

### 2. Non-Monetary Eligibility — § 591

Claimant must be:
- Totally unemployed OR partially unemployed (§ 522)
- Capable of work
- Ready, willing, and able to work
- Actively seeking work ("systematic and sustained efforts")
- Not subject to disqualifications in § 593 (voluntary quit w/o good cause, misconduct, refusal of suitable work)
- Participating in reemployment services if directed (profiled claimants)

**Dismissal pay exclusion**: No benefits if weekly dismissal pay > (weekly benefit rate + partial benefit credit).

### 3. Weekly Benefit Amount (WBA) — § 590(5)

**Standard case (claimant has wages in all 4 base-period quarters)**:

```
If high_quarter_wages > $3,575:
    WBA = high_quarter_wages / 26
Else (high_quarter_wages <= $3,575):
    WBA = high_quarter_wages / 25
```

**2-or-3-quarter case**: If the claimant has wages in only 2 or 3 quarters (not all 4):
```
WBA = (average of TWO highest quarters) / 26
```

**Rounding**: WBA rounded DOWN to the next multiple of $1 (statute: "if not a multiple of one dollar, shall be lowered to the next multiple of one dollar").

**Minimum WBA**: **$104/week** (statutory floor)
**Maximum WBA**:
- **$504/week** (2020-01-01 through 2025-10-12)
- **$869/week** (effective 2025-10-13)
- Thereafter indexed annually at 50% of NY State Average Weekly Wage (SAWW)

### 4. Duration of Benefits

- **Maximum regular duration**: **26 weeks** within a 52-week benefit year
- Operationalized as **104 "effective days"** (26 weeks × 4 days/week, since NYSDOL uses days-of-unemployment accounting)
- **Maximum benefit amount (MBA)** payable = WBA × 26 weeks

Benefit year = 52 weeks starting the Sunday of the week the claim is filed.

### 5. Partial Unemployment — Hours-Based Tiers (effective Aug 16, 2021)

Claimant with a week of part-time work receives a fraction of WBA based on total weekly hours:

| Hours Worked in Week | "Days" Reported | Benefit Fraction |
|---|---|---|
| 0-10 | 0 | 100% of WBA |
| 11-16 | 1 | 75% of WBA |
| 17-21 | 2 | 50% of WBA |
| 22-30 | 3 | 25% of WBA |
| 31+ | 4 | 0% (no benefit) |

**Hours cap per day**: When totaling hours, maximum 10 hours per calendar day is counted.

**Gross earnings cap**: If weekly gross pay > current max WBA (excluding self-employment earnings), NO benefit is payable for that week regardless of hours.

### 6. Partial Benefit Credit — § 525

Definition (used in "partial employment" test, not in the hours-based reduction above):

```
partial_benefit_credit = max(0.50 × WBA, $100)
```

- Rounded UP to next multiple of $1
- A claimant is "partially employed" under § 522 if:
  ```
  compensation < WBA + partial_benefit_credit
  ```

**Note on relationship to hours-based reduction**: The § 525 partial benefit credit defines the *earnings threshold for partial-unemployment status*. The *reduction* of the weekly payment follows the hours-based tiers (above), with the gross-earnings cap at MBR acting as a backstop.

### 7. Dependent Allowance

**NY does NOT have a dependent/dependency allowance in statute (§ 590)** for regular UI.

Some secondary sources (one claimyr.com forum article) mentioned "$25/dependent"; this appears to be either:
- Confusion with a different state's program (e.g., MA, NJ, CT, PA dependent allowances), or
- A misrepresentation.

NY Labor Law § 590 does not provide a dependent allowance. **Confirmed via review of § 590 subdivisions** on NY Senate, Justia, and FindLaw.

### 8. Self-Employment

Self-employment earnings are **excluded** from the gross-earnings cap (> max WBA disqualifies).
Self-employment "days" still count as work days for hours-based reduction.
NY has a separate **Self-Employment Assistance Program (SEAP)** under § 591-a — not modeled here.

---

## Calculation Formulas

### Base Period (§ 524)

```
basic_base_period = first 4 of last 5 completed calendar quarters before claim effective date
alternate_base_period = last 4 completed calendar quarters
```

### Weekly Benefit Rate (§ 590(5))

```
IF wages paid in all 4 quarters:
    IF high_quarter_wages > 3575:
        wbr_raw = high_quarter_wages / 26
    ELSE:
        wbr_raw = high_quarter_wages / 25
ELIF wages paid in exactly 2 or 3 quarters:
    wbr_raw = (highest_quarter + second_highest_quarter) / 2 / 26
ELSE:
    wbr_raw = 0  (ineligible under § 527)

wbr_floored = floor(wbr_raw)   # "lowered to next multiple of $1"
weekly_benefit_rate = min(max(wbr_floored, min_benefit), max_benefit)
```

### Monetary Eligibility (§ 527)

```
eligible_monetarily = (
    (high_quarter_wages >= high_quarter_minimum)
    AND (number_of_quarters_with_wages >= 2)
    AND (
        IF high_quarter_wages < 11088:
            total_base_wages >= 1.5 * high_quarter_wages
        ELSE:
            total_base_wages >= high_quarter_wages + (11088 / 2)
    )
)
```

### Partial Benefit Credit (§ 525)

```
partial_benefit_credit = ceil(max(0.50 * wbr, 100))
```

### Weekly Payment with Part-Time Work (effective 2021-08-16)

```
IF weekly_gross_earnings (excl. self-employment) > max_benefit:
    weekly_payment = 0
ELIF total_hours_worked >= 31:
    weekly_payment = 0
ELIF total_hours_worked >= 22:
    weekly_payment = 0.25 * wbr
ELIF total_hours_worked >= 17:
    weekly_payment = 0.50 * wbr
ELIF total_hours_worked >= 11:
    weekly_payment = 0.75 * wbr
ELSE:   # 0-10 hours
    weekly_payment = 1.00 * wbr
```

### Total Benefit (Benefit Year)

```
maximum_benefit_amount = weekly_benefit_rate * 26
```

---

## Special Cases and Exceptions

- **Shared Work / Short-Time Compensation (STC)** — § 599: Alternative partial-UI program for employers reducing hours instead of laying off. NOT modeled in initial implementation.
- **Self-Employment Assistance Program (SEAP)** — § 591-a: Not modeled.
- **Extended Benefits (EB)**: Federal/state program triggered by unemployment rate; adds up to 13 weeks. Not part of regular UI calculation.
- **Dismissal pay** — § 591(6): Weeks covered by dismissal pay exceeding (WBR + PBC) are ineligible.
- **Pension offset** — § 600: Reduces WBR if receiving a pension from a base-period employer. Not in scope for initial implementation.
- **Jury service** (§ 591(1)): Not a bar to benefits.
- **Alternate base period election** (§ 527): Claimant may elect if both periods qualify.

---

## Implementation Approach (Simplified)

Because PolicyEngine models annual household tax/benefit calculations rather than week-by-week UI claim processing, a practical implementation will:

1. **Inputs**: A household-level or person-level indicator of unemployment (`ny_ui_eligible` boolean) and/or base-period quarterly earnings.
2. **Derive weekly benefit rate** from highest-quarter wages (or an existing federal `unemployment_compensation` proxy).
3. **Apply min/max bounds** and 1/25 vs 1/26 divisor.
4. **Optional**: Partial-benefit reduction based on current-year earnings / hours worked.
5. **Multiply by weeks of unemployment** (capped at 26) for an annual benefit.

Alternatively, given complexity and the fact that actual UI receipts are typically imputed from CPS microdata in PolicyEngine-US, this program may be represented primarily by:
- A state-level **UI benefit calculator** (public-facing), and
- An imputed annual benefit via `unemployment_compensation` (already in model).

---

## Parameters Required

### Primary parameters (under `gov/states/ny/dol/unemployment_insurance/`)

| Parameter | Type | Value | Unit | Source |
|---|---|---|---|---|
| `benefit/max/amount` | Values by date | 504 (2020-01-01), 869 (2025-10-13) | currency-USD | NY Lab § 590(5); Gov announcement 2025 |
| `benefit/min/amount` | Values by date | 104 (2020-01-01) | currency-USD | NY Lab § 590(5); NYSDOL P832 |
| `benefit/divisor_threshold` | Value | 3575 | currency-USD | NY Lab § 590(5) |
| `benefit/divisor_low` | Value | 25 | /1 | NY Lab § 590(5) |
| `benefit/divisor_high` | Value | 26 | /1 | NY Lab § 590(5) |
| `eligibility/high_quarter_minimum` | Values by date | 3400 (2025-01-01), 3500 (2026-01-05) | currency-USD | NY Lab § 527 (indexed) |
| `eligibility/high_quarter_cap` | Value | 11088 | currency-USD | NY Lab § 527 |
| `eligibility/total_wages_multiplier` | Value | 1.5 | /1 | NY Lab § 527 |
| `duration/max_weeks` | Value | 26 | week | NY Lab § 590 |
| `partial/hours_tiers/rate` | Bracket by hours | (see below) | /1 | NYSDOL partial UI (§ 590, amended 2021) |
| `partial/benefit_credit/rate` | Value | 0.50 | /1 | NY Lab § 525 |
| `partial/benefit_credit/floor` | Value | 100 | currency-USD | NY Lab § 525 |

**Partial UI hours bracket (`partial/hours_tiers/rate.yaml`)**:
```yaml
brackets:
  - threshold: { 2021-08-16: 0 }
    amount:    { 2021-08-16: 1.0 }    # 0-10 hours: full WBR
  - threshold: { 2021-08-16: 11 }
    amount:    { 2021-08-16: 0.75 }   # 11-16: 75%
  - threshold: { 2021-08-16: 17 }
    amount:    { 2021-08-16: 0.50 }   # 17-21: 50%
  - threshold: { 2021-08-16: 22 }
    amount:    { 2021-08-16: 0.25 }   # 22-30: 25%
  - threshold: { 2021-08-16: 31 }
    amount:    { 2021-08-16: 0.0 }    # 31+: 0%
```

### Variables Required

| Variable | Entity | Period | Purpose |
|---|---|---|---|
| `ny_ui` | Person | YEAR | Total annual NY UI benefit received |
| `ny_ui_weekly_benefit_rate` | Person | YEAR | Calculated WBR (capped/floored) |
| `ny_ui_monetarily_eligible` | Person | YEAR | Passes § 527 tests |
| `ny_ui_eligible` | Person | YEAR | Overall eligibility |
| `ny_ui_high_quarter_wages` | Person | YEAR | Highest base-period quarter |
| `ny_ui_base_period_wages` | Person | YEAR | Total base-period wages |
| `ny_ui_partial_benefit_rate` | Person | WEEK/MONTH | Fraction based on hours | (if modeled weekly)

---

## References for Metadata

```yaml
# Primary statute reference
reference:
  - title: NY Lab. Law § 590(5) Rights to benefits
    href: https://www.nysenate.gov/legislation/laws/LAB/590
  - title: NY Lab. Law § 527 Valid original claim
    href: https://www.nysenate.gov/legislation/laws/LAB/527
  - title: NY Lab. Law § 525 Partial benefit credit
    href: https://www.nysenate.gov/legislation/laws/LAB/525
  - title: NYSDOL Maximum Benefit Rate
    href: https://dol.ny.gov/mbr
  - title: NYSDOL Partial Unemployment Eligibility
    href: https://dol.ny.gov/unemployment/partial-unemployment-eligibility
```

```python
# Python variable references
reference = (
    "https://www.nysenate.gov/legislation/laws/LAB/590",
    "https://dol.ny.gov/how-much-will-my-benefit-be",
)
```

---

## PDFs for Future Reference

The following PDFs could not be downloaded and extracted in this research session because the environment denied `curl` / `Bash` access. All are authoritative NYSDOL documents that should be consulted when implementing:

1. **How Your Weekly UI Benefit Payment Is Calculated (P832, Jan 2025)**
   - URL: https://dol.ny.gov/system/files/documents/2025/01/how-your-weekly-unemployment-insurance-benefit-payment-is-calculated-p832.pdf
   - Reason: curl/Bash denied — unable to extract text
   - Expected content: Worked examples of high-quarter calculation, 1/25 vs 1/26 divisor illustration, rounding rule, min/max application

2. **Workforce Forward: Partial Unemployment FAQs (P803, Oct 2025)**
   - URL: https://dol.ny.gov/system/files/documents/2025/10/p803-partial-ui-faqs-10-3-25.pdf
   - Reason: curl/Bash denied — unable to extract text
   - Expected content: Detailed Q&A on hours-based partial UI, work-day reporting, self-employment, max-earnings cap
   - HTML alternative (partial content): https://dol.ny.gov/workforce-forward-partial-unemployment-faqs-p803-english

3. **Unemployment Insurance Benefits: An Employer's Guide (IA 318.2, Dec 2025)**
   - URL: https://forms.labor.ny.gov/UI/IA318.2.pdf (also at https://dol.ny.gov/system/files/documents/2025/10/ia318.2.pdf)
   - Reason: curl/Bash denied
   - Expected content: Employer-facing summary of benefit formula, eligibility tests, duration
   - HTML alternative: https://dol.ny.gov/employers-guide-unemployment-insurance-benefits-ia3182

4. **Section 900 — Determination of Benefits (NYSDOL adjudication manual)**
   - URL: https://dol.ny.gov/system/files/documents/2025/10/section-900.pdf
   - Reason: curl/Bash denied
   - Expected content: Detailed adjudication rules for benefit-rate determination, base period, § 527 tests

5. **TC 408 Unemployment Insurance Reference Guide (Oct 2023)**
   - URL: https://dol.ny.gov/system/files/documents/2023/11/tc408-002.pdf
   - Reason: curl/Bash denied
   - Expected content: Summary reference card with thresholds, divisors, and benefit calculations

**Note**: `WebFetch` tool also returned 403 on `codes.findlaw.com` and NYSenate PDFs during this session. All primary statutory text was captured via WebSearch extracts quoting the sources directly.

P803 and P832 have since been provided as user-supplied PDFs and are appended in full at the end of this document.

---

## Complexity Assessment

**Complexity: MEDIUM-HIGH**

Reasons:
- Requires modeling base-period quarterly wage history, which is not a standard PolicyEngine input (typically only annual earnings are available).
- Two divisors (25 vs 26) with a high-quarter threshold.
- Minimum/maximum benefit floors with a recent large change (2025-10-13).
- Partial benefit calculation is hours-based (bracket parameter), not days-based.
- Monetary eligibility test has a piecewise 1.5× rule with a cap.
- Annual vs weekly periodicity mismatch will require simplification (e.g., using annual wages as a proxy for high-quarter wages).

**Key simplifications likely needed for PolicyEngine**:
- Approximate high-quarter wages from annual wages (e.g., using W2 data or a seasonality assumption)
- Represent weeks of unemployment as an exogenous input (number of weeks)
- Partial benefit reduction may be optional/simplified to the earnings-based formula

---

## P803: Partial UI FAQs (NYSDOL, Oct 2025)

Source: User-provided PDF: p803-partial-ui-faqs-10-3-25.pdf

UPDATED PARTIAL UNEMPLOYMENT FAQS
UPDATED: OCTOBER 2025

On January 18, 2021, Former Governor Andrew M. Cuomo announced that under his direction NYS DOL will implement a new rule that redefines how part-time work impacts unemployment benefits. This change makes New York's partial unemployment system fairer and more equitable for New Yorkers who have the opportunity to work part-time while collecting unemployment and pandemic benefits.

Effective August 16, 2021, New York State has modified the rules for partial unemployment eligibility. This update will apply to the benefit week of Monday, August 16, 2021 to Sunday, August 22, 2021 and all benefit weeks going forward. When certifying for benefits, New Yorkers should refer the new guidelines for reporting part-time work, available below.

**Q: What changes have been made to partial unemployment?**

A: NYS DOL's new partial unemployment system uses an "hours-based" approach. Under the new rules, claimants can work up to 7 days per week without losing full unemployment benefits for that week if they work 30 hours or fewer and earn $869 or less in gross pay excluding earnings from self-employment. With this change, claimants' benefits will not be reduced for each day they engage in part-time work and will be reduced in increments based on total hours of work for the week.

For comparison, NYS DOL's previous system for partial UI counted part-time work in full-day increments. Under this approach, a claimant who worked part-time would lose 25% of their weekly benefits for each day worked regardless of the number of hours worked on each of those days. For example, a claimant who earned just $45 during a three-hour shift would have lost a quarter of their weekly benefits.

**Q: What has changed with my weekly certification?**

A: This system update modifies how claimants calculate the number of days they report working each week. Claimants should refer to the chart below to determine how their weekly hours worked translates to the number of days to report. For example, if a claimant works 10 hours or fewer in a week, they should report they worked 0 days when certifying. A claimant who works 30 hours, would report 3 days worked.

Another change is that claimants are only required to report up to 10 hours worked each day.

| Hours Worked Per Week | Number of Days to Report | % Reduction in UI |
|---|---|---|
| 0 - 10 | 0 days | 0% |
| 11 - 16 | 1 day | 25% |
| 17 - 21 | 2 days | 50% |
| 22 - 30 | 3 days | 75% |
| 31+ | 4 days | 100% |

When calculating your hours worked, round up to the nearest whole hour.

**Q: What has not changed with my weekly certification?**

A: Claimants are still required to certify their weekly claims for benefits online or through the automated phone system. When certifying, the system will still ask for the number of days worked. Claimants should refer to the chart above to determine how their weekly hours worked translated to the number of days to report.

In addition, claimants will still be required to report the amount of money earned during the week for which they are claiming. Any claimant who earns more than $869 in weekly gross pay (excluding earnings from self-employment) will not be eligible for unemployment or pandemic benefits regardless of hours worked.

**Q: How should I calculate my hours if I work more than 10 hours on one day?**

A: When totaling hours for the week, claimants should use a maximum of 10 hours per calendar day. To determine how many days of work to report to UI, claimants should add together all hours worked for each calendar day (with a maximum of 10 hours for any day claimants worked more than 10 hours) and refer to the chart above.

For example, a claimant who works a total of 11 hours in a week should report one day of employment, and a claimant who works a total of 17 hours in a week should report two days of employment if they worked more than one day. If the 17 hours of work occurred on one calendar day, then that claimant should report one day of employment because of the 10-hour maximum rule.

Note: This formula does not change the $869 gross weekly payments rule — claimants must still report their total earnings for the week. Any claimant who earns more than $869 in weekly gross pay (the amount of money earned before taxes and deductions are taken out) excluding earnings from self-employment will not be eligible for unemployment or pandemic benefits regardless of hours worked.

**Q: When does this change to partial unemployment go into effect?**

A: Starting Sunday, January 24, 2021, New Yorkers will report using the new method for the benefit week of Monday, January 18, 2021 to Sunday, January 24, 2021 — and all benefit weeks forward.

Note: Starting Sunday, August 22, 2021, New Yorkers will report using the updated hours matrix for the benefit week of Monday, August 16, 2021 to Sunday, August 22, 2021 — and all benefit weeks going forward.

**Q: Is there still an earnings cut-off for partial unemployment benefits?**

A: Yes, if a claimant earns more than $869 in weekly gross pay (the amount of money earned before taxes and deductions are taken out excluding earnings from self-employment), then they will not be eligible for unemployment or pandemic benefits for that week no matter how few hours they worked.

**Q: Does this change also apply to weekly certifications for Pandemic Unemployment Assistance (PUA) benefits?**

A: Yes. Claimants who are eligible for PUA benefits will report their days of work using the new calculation method. Unlike regular UI benefits (or extended benefits), PUA claimants must report earnings in self-employment over $869 as per Federal requirements.

**Q: If I work four hours in a week over four days, should I still report that I worked 0 days?**

A: Yes, under NYS DOL's new partial unemployment system, four hours of work in a week — regardless of the total days worked — is equivalent to less than one day worked for certification purposes, as long as the claimant does not earn more than $869 in gross pay (excluding earnings from self-employment) for those hours worked.

**Q: How does this change impact my benefits if I am not working part-time?**

A: NYS DOL's change in how partial unemployment benefits are calculated will not impact claimants who work 0 hours in a week.

**Q: How will this change to partial unemployment impact the overall time that I can receive unemployment benefits?**

A: NYS DOL's change in how partial unemployment benefits are calculated will not impact the number of weeks of unemployment available to New Yorkers.

**Q: I'm on Shared Work. How does this change affect my benefits?**

A: Partial unemployment benefits for claimants enrolled in the Shared Work program are calculated differently. Click here for additional information about certifying for Shared Work benefits.

**Q: What should I do if I reported the wrong number of hours worked while certifying?**

A: If a claimant mistakenly reports the number of days worked for weeks starting January 18, 2021 or later, instead of using the new formula, or if you use the outdated reporting guidelines for weeks starting August 16, 2021 or later, they should let NYS DOL know so we can ensure they are paid all the benefits they are entitled to.

**Q: What should I do if I'm certifying for back payments for weeks that I was partially unemployed between January 18, 2021 and August 16, 2021?**

To certify for part-time work between January 18, 2021 and August 16, 2021, you should refer to the previous partial employment guidelines below.

- 0 – 4 hours of work (equivalent to 0 days worked): 100% of weekly benefit rate
- 5 – 10 hours of work (equivalent to 1 day worked): 75% of weekly benefit rate
- 11 – 20 hours of work (equivalent to 2 days worked): 50% of weekly benefit rate
- 21 – 30 hours of work (equivalent to 3 days worked): 25% of weekly benefit rate
- 31+ hours of work (equivalent to 4 days worked): 0% of weekly benefit rate

P803 (10/25)

The New York State Department of Labor is an Equal Opportunity Employer/Program. Auxiliary aides and services are available upon request and free of charge to individuals with disabilities TTY/TDD 711 or 1-800-662-1220 (English) / 1-877-662-4886.

---

## P832: How Your Weekly UI Benefit Is Calculated (NYSDOL, Feb 2026)

Source: User-provided PDF: p832-how-your-weekly-ui-benefits-are-calculated-2-26.pdf

HOW YOUR WEEKLY UNEMPLOYMENT INSURANCE BENEFIT PAYMENT IS CALCULATED

### Understanding your "base period"

Your weekly benefit payment amount depends on how much you were paid during a "base period." A base period represents one year of your work and wages (four calendar quarters). Calendar quarters are the three-month blocks of time shown in the chart below. Wages earned in your base period are used to calculate your benefit. Your benefit rate is the amount of money you receive if you are eligible for a full week of Unemployment Insurance benefits.

Two types of base periods are shown in the chart below. The Basic Base Period is the first four of the last five completed calendar quarters before the quarter in which you file for benefits. If you have enough wages in your Basic Base Period, we use it when we calculate your benefit payment.

If you do not have enough wages in your Basic Base Period, we use your Alternate Base Period to calculate your benefit payment. The Alternate Base Period is the last four completed calendar quarters before the quarter in which you file for benefits.

**IMPORTANT:** If you have enough wages in your Basic Base Period, we do not automatically check to see if your benefit rate would be higher if your Alternate Base Period is used instead. If you think your benefit payment would be higher using your Alternate Base Period, you can ask us to use your Alternate Base Period to calculate your benefit amount. However, if you choose to use the alternate quarter (5th quarter as shown in the chart below) wages for your current claim, you cannot use these wages again in the future. This may affect your ability to qualify for a future claim. For more information, see the section "Requesting a benefit rate recalculation based on Alternate Base Period" in the claimant handbook. Or, see the Frequently Asked Questions section on our website under, "What if I think my rate will be higher using the Alternate Base Period?"

For all base periods, the quarter in which you file for benefits does not count as part of your base period. Wages earned during the quarter you filed will not be used to calculate your benefit rate.

### How base periods work

This is an example only. Your base period quarters may differ from those shown.

| Quarter | Dates | Notes |
|---|---|---|
| 1st Quarter (Previous Year) | January 1 – March 31 | Part of Basic Base Period |
| 2nd Quarter (Previous Year) | April 1 – June 30 | Part of Basic Base Period |
| 3rd Quarter (Previous Year) | July 1 – September 30 | Part of Basic Base Period |
| 4th Quarter (Previous Year) | October 1 – December 31 | Part of Basic Base Period and Alternate Base Period |
| 5th Quarter (Current Year) | January 1 – March 31 | Part of Alternate Base Period only |
| Quarter you filed for benefits (Current Year) | April 1 – June 30 | Does not count as part of base period |

Basic Base Period: Wages paid to you during the first four quarters above make up your Basic Base Period.

Alternate Base Period: Wages paid to you during quarters 2–5 above make up your Alternate Base Period.

### Earnings required to qualify for benefits

To qualify for benefits, you must meet all three of the following earnings requirements during your base period (basic or alternate):

- You must have worked and been paid wages in jobs covered by Unemployment Insurance in at least two calendar quarters
- For claims filed in 2026, you must have been paid at least $3,500 in one calendar quarter (this amount increased from $3,400 for claims filed in 2025)
- The total wages paid to you must be at least 1.5 times the amount paid to you in your high quarter. Your high quarter is the quarter of your base period in which you were paid the most money. Exception: If your high quarter wages were $19,118 or more, you must have been paid a combined total of at least $9,559 in the other three quarters of your base period.

To be eligible for benefits, you must also have lost work through no fault of your own; be ready, willing, and able to work; and be actively looking for work.

### How we calculate your weekly benefit rate

If you were paid wages in all four quarters of your base period and your high quarter wages are:

- **More than $3,575**: Your benefit amount is your high quarter wages divided by 26. If this calculation is less than $143, your benefit rate is $143.
- **$3,575 or less**: Your benefit amount is your high quarter wages divided by 25.

If you were paid wages in only two or three quarters of your base period and your high quarter wages are:

- **More than $4,000**: Your benefit amount is the average wages of your two highest quarter wages, divided by 26. If this calculation is less than $143, your benefit amount is $143. For example, your high quarter wages are $4,500 and your next highest quarter wages are $4,288, an average of $4,394 ($4,500 + $4,288 = $8,788; $8,788 ÷ 2 = $4,394). Your benefit amount is $169 ($4,394 ÷ 26 = $169).
- **$3,576 to $4,000**: Your benefit amount is your high quarter wages divided by 26. If this calculation results in less than $143, your benefit amount is $143.
- **$3,575 or less**: Your benefit amount is your high quarter wages divided by 25.

There are maximum and minimum benefit rates. Effective the first Monday of October 2025 the maximum benefit rate increased to $869. The minimum benefit rate is $140 as of January 2026.

For more information and more examples of the information contained in this fact sheet, please see the claimant handbook at dol.ny.gov/unemployment-insurance-claimant-handbook.

### Estimate your weekly benefit rate

You can estimate your weekly benefit rate by using the online calculator located at ux.labor.ny.gov/benefit-rate-calculator.

NOTE: The calculator gives an estimate only. It does not guarantee that you will be eligible for benefits or a specific amount of benefits. You must file an Unemployment Insurance claim to find out if you are eligible and learn your actual benefit amount.

P832 (2/26)

The New York State Department of Labor is an Equal Opportunity Employer/Program. Auxiliary aides and services are available upon request and free of charge to individuals with disabilities TTY/TDD 711 or 1-800-662-1220 (English) / 1-877-662-4886. The Unemployment Insurance Program is funded by a federal grant of $172,710,563 which constitutes 100% of its budget. 0%, or $0 is funded by state or non-governmental sources.

---
