# Collected Documentation

## Maine TANF Implementation
**Collected**: 2025-12-28
**Implementation Task**: Implement Maine's Temporary Assistance for Needy Families (TANF) program

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Temporary Assistance for Needy Families (TANF)
**Abbreviation**: TANF
**Source**: 22 M.R.S. Section 3762; 10-144 C.M.R. Chapter 331

**Variable Prefix**: `me_tanf`

---

## Regulatory Authority

### Primary Legal Sources
1. **Maine Revised Statutes Title 22, Section 3762** - Temporary assistance for needy families; promotion of economic self-support
   - URL: https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html

2. **Maine Revised Statutes Title 22, Section 3763** - Program requirements
   - URL: https://legislature.maine.gov/legis/statutes/22/title22sec3763.html

3. **10-144 C.M.R. Chapter 331** - Public Assistance Manual, Temporary Assistance for Needy Families (TANF) Manual
   - URL: https://www.law.cornell.edu/regulations/maine/10-144-C-M-R-ch-331-app-Charts

### Administrative Agency
- **Agency**: Maine Department of Health and Human Services (DHHS)
- **Division**: Office for Family Independence (OFI)
- **URL**: https://www.maine.gov/dhhs/ofi/programs-services/tanf

---

## Demographic Eligibility

### Age Thresholds
- **Minor child age limit**: Under 18
- **Full-time student age limit**: Under 19 (for youth in secondary school)
- **Pregnant women**: Eligible (up to 90 days before expected delivery date)
- **Minor parents under 18**: Must reside with parent, guardian, or other adult relative (with specific exceptions)

**Source:** 22 M.R.S. Section 3762

**Implementation approach:**
- [x] Use federal demographic eligibility (age thresholds match federal rules)
- [ ] Create state-specific age thresholds

---

## Immigration Eligibility

**State Immigration Rules:**
- Citizenship requirement: Required (U.S. citizen or qualified immigrant)
- Legal permanent residents: Eligible after qualifying period
- Refugees/Asylees: Eligible
- COFA citizens: Eligible (per TANF Rule #124, effective 2025)

**Source:** 10-144 C.M.R. Chapter 331, Chapter II; 42 U.S.C. Section 602; 45 C.F.R. Section 260

**Implementation approach:**
- [x] Use federal immigration eligibility (state follows federal rules)
- [ ] Create state-specific immigration rules

---

## Income Eligibility Tests

### Gross Income Test (Applicants Only)
- **Applies to**: Applicants only (NOT recipients)
- The department may apply a gross income test only to applicants and not to recipients.
- If gross income exceeds the threshold, the applicant is not eligible.

**Source:** 22 M.R.S. Section 3762(3)(B)(7-F)

**Quote from statute:**
> "In determining eligibility and benefit levels, the department may apply a gross income test only to applicants and not to recipients."

### Net Income Test (Eligibility Determination)
- The department deducts income less any applicable income disregards from the Standard of Need.
- May not apply any other income test.

**Source:** 22 M.R.S. Section 3762(3)(B)(7-F)

**Implementation approach:**
- [ ] Use federal baseline income test
- [x] Create state-specific income eligibility (uses Standard of Need comparison)

---

## Income Deductions & Exemptions

### Earned Income Disregards (Step Disregard)

**CRITICAL: Time-limited disregards - cannot fully simulate**

Per 22 M.R.S. Section 3762(3)(B)(7-D), earned income disregards are:

| Employment Month | Disregard |
|------------------|-----------|
| Months 1-3 | 100% of all earned income |
| Months 4-6 | 75% of all earned income |
| Month 7+ | $108 plus 50% of remaining earnings |

**NOTE**: PolicyEngine cannot track employment duration across periods. The Month 7+ formula should be implemented as the default, with documentation noting that new employees receive higher disregards.

**Source:** 22 M.R.S. Section 3762(3)(B)(7-D); 10-144 C.M.R. Chapter 331, Chapter IV

### Standard Earned Income Deduction (Month 7+)
1. **Flat deduction**: $108 per month from wages/self-employment
2. **Percentage disregard**: 50% of remaining earnings after flat deduction

**Level**: Per UNIT (not per person)

**Source:** 22 M.R.S. Section 3762(3)(B)(7-D)

### Child Care Deduction
- **Standard**: Up to $175 per month per child
- **Under age 2 or special needs**: Up to $200 per month per child

**Level**: Per CHILD

**Source:** 22 M.R.S. Section 3762(3)(B)(7-D)

### Child Support Pass-Through
- **Amount**: First $50 per month of child support
- **Treatment**: Passed through to family AND excluded from income calculations

**Source:** 22 M.R.S. Section 3762; Pine Tree Legal Assistance Guide

### Unearned Income
- Generally counted dollar-for-dollar
- No disregards apply to unearned income except child support pass-through

---

## Asset/Resource Limits

### Asset Limit
- **Amount**: $10,000 per family
- **Vehicle exemption**: One vehicle per licensed driver is exempt

**Source:** 22 M.R.S. Section 3762; P.L. 2023 Ch. 366 (effective October 25, 2023)

---

## Income Standards (FFY 2025)

### Standard of Need (SON) and Maximum Benefit by Household Size

**Effective FFY 2025 (October 1, 2024):**

| Household Size | Adult Included - SON | Adult Included - Max Benefit | Child Only - SON | Child Only - Max Benefit |
|----------------|---------------------|------------------------------|------------------|--------------------------|
| 1 | $489 | $425 | $290 | $254 |
| 2 | $769 | $669 | $553 | $483 |
| 3 | $1,030 | $895 | $817 | $712 |
| 4 | $1,296 | $1,127 | $1,077 | $936 |
| 5 | $1,557 | $1,352 | $1,344 | $1,169 |
| 6 | $1,820 | $1,580 | $1,607 | $1,396 |
| 7 | $2,085 | $1,811 | $1,870 | $1,625 |
| 8 | $2,349 | $2,040 | $2,131 | $1,851 |
| Each additional | $263 | $228 | $263 | $228 |

**Source:** 10-144 C.M.R. Chapter 331, Appendix Charts (Table 2)
**URL:** https://www.law.cornell.edu/regulations/maine/10-144-C-M-R-ch-331-app-Charts

### Historical Values (FFY 2024)

| Household Size | Adult Included - SON | Adult Included - Max Benefit | Child Only - SON | Child Only - Max Benefit |
|----------------|---------------------|------------------------------|------------------|--------------------------|
| 1 | $407 | $343 | $241 | $205 |
| 2 | $640 | $540 | $460 | $390 |
| 3 | $858 | $723 | $680 | $575 |
| 4 | $1,079 | $910 | $897 | $756 |
| 5 | $1,297 | $1,092 | $1,119 | $944 |
| 6 | $1,516 | $1,276 | $1,338 | $1,127 |
| 7 | $1,736 | $1,462 | $1,557 | $1,312 |
| 8 | $1,956 | $1,647 | $1,775 | $1,495 |
| Each additional | $219 | $184 | $219 | $184 |

---

## Benefit Calculation Formula

### Standard Benefit Formula
Per 22 M.R.S. Section 3762(3)(B)(8):

```
Monthly TANF Benefit = min(Maximum Payment Level, Standard of Need - Countable Income)
```

**Steps:**
1. Calculate countable income:
   - Apply earned income disregards to earned income
   - Add unearned income (minus $50 child support pass-through)
   - Subtract child care deductions
2. Calculate benefit:
   - `Benefit = Standard of Need - Countable Income`
   - Cap at Maximum Payment Level
   - If negative, benefit = $0

**Source:** 22 M.R.S. Section 3762(3)(B)(8)

### Special Housing Allowance
- **Eligibility**: Shelter costs (rent, mortgage, insurance, taxes) >= 50% of monthly income
- **Amount**: Up to $300 per month per family
- Added to Standard of Need and Maximum Benefit amounts

**Source:** 22 M.R.S. Section 3762

---

## Non-Simulatable Rules (Architecture Limitation)

### Time Limit
- **60-month lifetime limit** on TANF benefits
- CANNOT ENFORCE - requires tracking benefit history across periods

**Source:** 22 M.R.S. Section 3762(18)

### Step Disregard Time Limits
- The 100%/75% disregards for months 1-6 of employment CANNOT be tracked
- **Implementation**: Use Month 7+ formula ($108 + 50%) as default
- Document that new employees receive higher disregards

### Work Requirements
- Recipients must participate in ASPIRE-TANF program
- Work participation tracking CANNOT be simulated

**Source:** 22 M.R.S. Section 3763

---

## Implementation Notes

### Assistance Unit Types
1. **Adult Included** - Standard household with at least one adult
2. **Child Only** - Household where only children receive benefits (adult income not counted)

### Differences from Federal Baseline
1. **Asset limit**: $10,000 (higher than many states)
2. **Step disregard**: Time-based earned income disregards (100%/75%/standard)
3. **Child support pass-through**: $50/month excluded
4. **Special housing allowance**: Up to $300/month
5. **Two benefit schedules**: Different amounts for Adult Included vs Child Only cases

### Key Implementation Variables Needed
1. `me_tanf` - Main benefit variable
2. `me_tanf_eligible` - Overall eligibility
3. `me_tanf_income_eligible` - Income eligibility
4. `me_tanf_resources_eligible` - Resource/asset eligibility
5. `me_tanf_countable_income` - Total countable income
6. `me_tanf_countable_earned_income` - Earned income after disregards
7. `me_tanf_earned_income_disregard` - $108 + 50% disregard calculation
8. `me_tanf_child_care_deduction` - Child care deduction
9. `me_tanf_standard_of_need` - Standard of Need by household size
10. `me_tanf_maximum_benefit` - Maximum payment level by household size

---

## References for Metadata

### For Parameters
```yaml
reference:
  - title: 22 M.R.S. Section 3762
    href: https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html
  - title: 10-144 C.M.R. Chapter 331, Appendix Charts
    href: https://www.law.cornell.edu/regulations/maine/10-144-C-M-R-ch-331-app-Charts
```

### For Variables
```python
reference = (
    "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
    "https://www.law.cornell.edu/regulations/maine/10-144-C-M-R-ch-331-app-Charts",
)
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

1. **Maine TANF State Profile Summary (NCCP 2024)**
   - URL: https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Maine.pdf
   - Expected content: Complete state profile with eligibility, benefits, and policy options

2. **50-State TANF Benefit Amounts Comparison (NCCP 2024)**
   - URL: https://www.nccp.org/wp-content/uploads/2024/11/TANF-Benefit-Amounts-2024-FINAL.pdf
   - Expected content: Comparison of benefit amounts across all states

3. **Maine Equal Justice TANF/ASPIRE Program Guide**
   - URL: https://maineequaljustice.org/site/assets/files/4265/doc_2_2_tanf_aspire_program_guide.pdf
   - Expected content: Detailed program guide with eligibility and benefit information

4. **Maine Legislature Final Report on TANF**
   - URL: https://legislature.maine.gov/doc/2356
   - Expected content: Legislative analysis and program recommendations

---

## Additional Sources Consulted

- [Maine DHHS TANF Program Page](https://www.maine.gov/dhhs/ofi/programs-services/tanf)
- [Pine Tree Legal Assistance - Guide to TANF in Maine](https://www.ptla.org/Maine-TANF-Guide)
- [SSA POMS: SI BOS00830.404 - Maine TANF](https://secure.ssa.gov/apps10/poms.nsf/lnx/0500830404BOS)
- [Maine Morning Star - TANF Benefit Increase Article (2024)](https://mainemorningstar.com/2024/06/17/for-some-maine-families-upcoming-increase-to-tanf-benefits-could-be-a-lifeline/)
