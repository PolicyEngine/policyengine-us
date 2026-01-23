# Collected Documentation

## Wyoming POWER (TANF) - Implementation
**Collected**: 2026-01-02
**Implementation Task**: Implement Wyoming's TANF cash assistance program (POWER)

---

## Official Program Name

**Federal Program**: Temporary Assistance for Needy Families (TANF)
**State's Official Name**: Personal Opportunities With Employment Responsibilities (POWER)
**Abbreviation**: POWER
**Source**: Wyoming Statute 42-2-103; Wyoming DFS website

**Variable Prefix**: `wy_tanf` or `wy_power`

---

## Program Overview

Wyoming's POWER program is a time-limited, pay-after-performance program funded by federal TANF block grant dollars. The program provides temporary cash assistance to needy families with dependent children.

### Program Types
1. **POWER Work Program** - Assists individuals in finding employment with cash support and child support assistance
2. **POWER Caretaker Relative Program** - Provides cash assistance to relatives (grandparents, aunts, uncles) who are primary caregivers for children whose parents are not in the home

### Administering Agencies
- **Wyoming Department of Family Services (DFS)** - Determines eligibility and provides case management
- **Wyoming Department of Workforce Services (DWS)** - Administers POWER work program and employment/training activities

---

## Demographic Eligibility

### Who Qualifies
- Wyoming resident responsible for daily care of a child under age 18
- Must meet citizenship and alien status requirements
- Must satisfy income and resource limits

### Minor Child Definition
A dependent between birth and 18 years who is not emancipated or a minor parent. The child must reside with a caretaker exercising day-to-day care and control.

**Source**: Wyoming DFS SNAP and POWER Policy Manual Glossary
**URL**: https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/glossary/

### Caretaker Relative Definition
A person who meets the definition of a relative and is exercising the day-to-day care and control of the child(ren).

**Implementation Approach**:
- [x] Use federal demographic eligibility (age 18 threshold matches federal)
- [ ] Create state-specific age thresholds (not needed - state follows federal)

---

## Immigration Eligibility

Wyoming follows federal TANF immigration eligibility requirements under PRWORA.

### Verification
- Immigrant status information obtained through SAVE process (Section 606(G))
- For POWER only: Driver's License from a state requiring proof of citizenship or permanent resident status can be used as documentation

**Source**: Wyoming DFS SNAP and POWER Policy Manual Section 606
**URL**: https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/

**Implementation Approach**:
- [x] Use federal immigration eligibility (state follows federal rules)

---

## Resource/Asset Limits

### Resource Limit
- **Limit**: $5,000 for assistance unit
- **Source**: Wyoming DFS Policy Manual; Wyoming Statute 42-2-103

### Vehicle Exclusion
- Two (2) duly registered and licensed motor vehicles excluded from personal assets
- **Source**: Wyoming Statute 42-2-103

### Countable Resources (Examples)
- Checking and savings accounts
- Income-producing property
- Stocks, bonds, or mutual funds

**Source**: https://dfs.wyo.gov/assistance-programs/cash-assistance/cash-assistance-income-and-resource-requirements/

---

## Income Eligibility

### "Needy" Definition
For POWER, need is measured by "the lack of money to purchase essential items to sustain life and measured by the maximum POWER payment."

A family is considered "needy" when their countable income is less than the maximum benefit level for their household size.

**Example**: A single-parent family of three is needy when countable income is less than $1,469/month (this figure likely varies by year and shelter status).

### Maximum Benefit Level Test (Income Eligibility Test)
The maximum benefit level test must be met by the assistance unit prospectively each month:
1. Calculate anticipated gross earned income (including tips) or net profit from self-employment
2. Apply earned income disregard ($600 or $1,200)
3. Add anticipated unearned income
4. Add any deemed income (stepparent, parent of minor parent, disqualified person)
5. Compare total against maximum benefit level from Table II
6. **Eligible if**: Total countable income < Maximum benefit level

**Source**: Wyoming DFS SNAP and POWER Policy Manual Section 1101
**URL**: https://dfs.wyo.gov/accordions/snap-and-power-policy-manual-1100-extended-menu/

### Income Eligibility Range
Eligibility limits on monthly net income range from $1,176 to $2,038 (55-95% FPL), depending on family structure and shelter status.

**Source**: NCCP Wyoming TANF Profile
**URL**: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-Wyoming-.pdf

---

## Income Disregards and Deductions

### Earned Income Disregard (CRITICAL)

**Statutory Authority**: Wyoming Statute 42-2-103

| Recipient Type | Monthly Disregard |
|---------------|------------------|
| Single individual | $600 |
| Married couple with child in common | $1,200 |

**Key Rules**:
1. **$600 Disregard**: Flat amount deducted from gross earned income of:
   - Each eligible working applicant/recipient in a two-parent assistance unit
   - Single parent assistance unit
   - Caretaker relative included in the performance payment
   - Stepparent

2. **$1,200 Disregard**: Flat amount for eligible married couple applying for or receiving POWER with a child in common, regardless of the number of employed individuals

3. **Application**: Disregard applied to anticipated gross earned income including tips, or anticipated net profit from self-employment

**Source**: Wyoming Statute 42-2-103
**URL**: https://codes.findlaw.com/wy/title-42-welfare/wy-st-sect-42-2-103.html

### Individual Earned Income Disregard (Additional - Discretionary)
The department MAY establish an additional individual earned income disregard as part of a person's self-sufficiency plan with conditions:
- Only available when working enough hours to qualify under Section 407 of P.L. 104-193
- Amount not to exceed $6.50/hour ($7.50/hour in high-cost areas)
- Structured to allow 1/2 of preemployment POWER grant for up to 6 months, then 1/4 for another 6 months
- Discretionary - not subject to judicial review

**NOTE**: This discretionary disregard is likely NOT implemented in the base model as it requires case-by-case determination.

### Overpayment Exception
Disallow any earned income disregards when establishing an overpayment due to client error or IPV relating to earned income and the overpayment occurred prior to 8/1/97.

---

## Benefit/Payment Standards

### Shelter Qualification Categories

Wyoming has TWO benefit schedules based on shelter costs:

#### Shelter Qualified (Higher Benefit)
Applies when the assistance unit:
- Is responsible for paying all or a portion of shelter costs
- Does NOT meet shelter disqualified criteria
- Shelter code "N"

#### Shelter Disqualified (Lower Benefit)
Applies when the assistance unit:
- Has no obligation to pay any portion of shelter costs (shelter code "Y")
- Lives in government housing subsidy (shelter code "R")
- Is a minor parent living with parent(s), supervised adult relative, or court-appointed guardian (shelter code "M")
- Excludes an individual due to receiving SSI (shelter code "S")

**Source**: Wyoming DFS SNAP and POWER Policy Manual Section 905

### Maximum Benefit Amounts (2024-2025)

#### Payment Standards by Household Size (Shelter Qualified)

| Household Size | Maximum Monthly Benefit | Income Limit |
|----------------|------------------------|--------------|
| 1 | $512 | $1,112 |
| 2 | $847 | $1,447 |
| 3 | $902 | $1,502 |
| 4 | $902 | $1,502 |
| 5 | $959 | $1,559 |
| 6 | $959 | $1,559 |
| 7 | $1,015 | $1,615 |
| 8 | $1,015 | $1,615 |
| 9+ | Add $57 per person | Add $56 per person |
| 12+ | Add $5,500 per person (July 2025-June 2026) | - |

**Note**: Values repeat for some household sizes (3-4, 5-6, 7-8) which is the actual Wyoming schedule.

#### Shelter Disqualified Amounts (Lower Benefit)

Based on NCCP profile:
- Family of 3: ~$576/month (27% FPL) vs $902 shelter qualified (42% FPL)
- Approximately 64% of shelter-qualified amount

**Estimated Shelter Disqualified Schedule:**
| Household Size | Estimated Monthly Benefit |
|----------------|--------------------------|
| 1 | ~$328 |
| 2 | ~$542 |
| 3 | ~$576 |
| 4 | ~$576 |
| 5 | ~$614 |
| 6 | ~$614 |
| 7 | ~$650 |
| 8 | ~$650 |

**Note**: Shelter disqualified amounts are estimates based on the ratio from family of 3. Official Table II values in embedded image at DFS website.

**Source**:
- Wyoming DFS: https://dfs.wyo.gov/assistance-programs/cash-assistance/cash-assistance-monthly-benefit-amount/
- Wyoming DFS Table II: https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/table-ii-power-income-limits/
- singlemotherguide.com: https://singlemotherguide.com/state/wyoming/TANF
- NCCP Profile: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-Wyoming-.pdf

### Benefit Purpose
The maximum benefit amount is intended to cover:
- Shelter
- Personal care items
- Utilities
- Housekeeping supplies
- Telephone
- Home furnishings/maintenance
- Apparel and upkeep
- Miscellaneous medical
- Travel costs
- Reading and education

### Annual Cost-of-Living Adjustment
Beginning July 1, 2009 and annually thereafter, the maximum payment level is adjusted for the percentage change in the Wyoming cost-of-living index for the previous fiscal year as determined by the division of economic analysis of the department of administration and information.

**Source**: Wyoming Statute 42-2-103

### Large Households
For assistance units over 12 persons, add $5,500 per each additional member (July 2025 - June 2026 guidelines).

---

## Benefit Calculation Formula

### Performance Payment Computation
1. Start with Maximum Benefit Level (from Table II based on household size and shelter status)
2. Determine anticipated countable income:
   - Gross earned income - $600/$1,200 earned income disregard
   - Plus unearned income
   - Plus deemed income (if applicable)
3. **Performance Payment = Maximum Benefit Level - Total Countable Income**
4. Round down to nearest whole dollar
5. If payment equals or is less than anticipated child support collections, terminate case

**Source**: Wyoming DFS SNAP and POWER Policy Manual Section 1101

---

## Time Limits

### WARNING: Non-Simulatable Rules (Architecture Limitation)

- **60-Month Lifetime Limit**: Maximum of five (5) years of federally funded cash assistance in any individual's lifetime [CANNOT ENFORCE - requires history tracking]
- **Minimum 24 Months**: All eligible families receive at least 24 months of assistance [CANNOT TRACK]

Time spent on assistance funded with federal funds AND state funds are added together in determining total time on assistance.

Adults who previously received assistance as a dependent child (excluding minor parents) are allowed up to the 5-year lifetime limit under their own assistance unit.

**Source**: Wyoming Statute 42-2-103

---

## Special Rules

### No Family Cap
Wyoming does NOT enforce a "family cap" on assistance for additional children born while a family already receives assistance.

### Drug Felony Eligibility
Wyoming has ELIMINATED the eligibility ban for those convicted of drug-related felonies.

### Child-Only Cases
For the POWER Caretaker Relative program, only the child's financial situation is evaluated, not the guardian's. The caretaker's income and resources are not counted.

**Example**: POWER Caretaker Relative Program for one child with no income or resources could receive ~$259/month.

---

## Income Sources

### Earned Income Definition
Payment received in cash or in-kind for wages, salary, tips, commissions, as an employee or net-profit from activities in which the individual is engaged as self-employed.

### Unearned Income Definition
All money received that is not earned by providing goods and services or defined as an asset.

### Income Counting Methodology
- Income counted only in the month it is expected to be received
- Best estimates using prior 30-day history
- Conversion multipliers: 4.3 for weekly, 2.15 for biweekly, 2 for semi-monthly
- Prospective budgeting applies income anticipated during certification period

**Implementation Approach**:
- [x] Use federal baseline income sources (standard definitions apply)

---

## Deemed Income

### Stepparent Computation
Income of stepparent is considered available in determining eligibility beginning with month of marriage:
1. Anticipated gross earned income (including tips) or net self-employment profit
2. Deduct $600 for earned income disregard
3. Add anticipated unearned income available to stepparent
4. Deduct maximum benefit level for household size of stepparent's own household

### Parent of Minor Parent Computation
Similar calculation - participation code "DP" on SEPA

### Disqualified Person Computation
Income of disqualified person is partially attributed to assistance unit:
1. Gross earned income or net self-employment profit
2. Deduct $600 ($1,200 for married couple)
3. Add unearned income

### Immigrant Sponsor Deeming
100% of income and assets of sponsor (and sponsor's spouse) deemed to immigrants until:
- Naturalization
- 40 qualifying work quarters
- Sponsor's death

---

## Recent Policy Updates (2024-2025)

| Date | Update |
|------|--------|
| Sept 27, 2024 | Removed additional application requirements for POWER (aligned with SNAP) |
| Sept 6, 2024 | Updated income guidelines and allotments for 10/1/24 - 9/30/25 |
| Aug 12, 2024 | Added panhandling as countable contribution (Section 901) |
| July 1, 2024 | Added TPQY as acceptable identification; added Tribal TANF codes |
| May 2, 2024 | Extended Ukrainian humanitarian parolee eligibility |
| Jan 22, 2024 | Updated SSN requirements for POWER |

**Source**: https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/cm-updates/

---

## Legal Citations

### Wyoming Statutes (Title 42 - Welfare)
- **W.S. 42-2-103** - POWER program eligibility, earned income disregard ($600/$1,200), time limits, COLA adjustment
- **W.S. 42-2-104** - Assistance payable, maximum payment levels

**URL**: https://codes.findlaw.com/wy/title-42-welfare/wy-st-sect-42-2-103.html

### Wyoming DFS Policy Manual Sections
| Section | Topic |
|---------|-------|
| 606 | Citizenship/Alien Status |
| 901 | Countable/Available Income |
| 903 | Self-Employment Income Treatment |
| 904 | Determining Best Estimate |
| 905 | Benefit Levels |
| 906 | Income Disregards/Deductions |
| 1101 | POWER Payment Tests/Computations |
| 1203 | Initial POWER Eligibility Determination |
| 1204 | POWER Payment Process |
| 1701 | POWER Five Year Benefit Limit |

**Base URL**: https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/

---

## Parameter Structure Recommendations

Based on research, the following parameters are needed:

### Income
- `income/disregard/individual.yaml` - $600 flat disregard
- `income/disregard/married_couple.yaml` - $1,200 flat disregard
- (Note: Wyoming uses flat dollar disregards, NOT percentage disregards)

### Benefit
- `benefit/payment_standard/shelter_qualified.yaml` - Bracket by household size
- `benefit/payment_standard/shelter_disqualified.yaml` - Bracket by household size
- `benefit/additional_person.yaml` - $5,500 for households over 12

### Resources
- `resources/limit.yaml` - $5,000
- `resources/vehicle_exemptions.yaml` - 2 vehicles

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

1. **NCCP Wyoming TANF Profile**
   - URL: https://www.nccp.org/wp-content/uploads/2024/08/TANF-profile-Wyoming-.pdf
   - Expected content: Detailed benefit amounts by household size, income limits, policy comparisons

2. **Wyoming TANF Work Requirements Summary**
   - URL: https://wyoleg.gov/InterimCommittee/2019/10-2019092324-TANFWorkRequirementsSummary.pdf
   - Expected content: Work requirement details, exemptions, historical context

3. **Wyoming TANF Interim Committee Report**
   - URL: https://wyoleg.gov/InterimCommittee/2019/S15-20190930TANF.pdf
   - Expected content: Legislative analysis of TANF program

4. **Wyoming Title 42 Welfare Statutes (Full)**
   - URL: https://wyoleg.gov/statutes/compress/title42.pdf
   - Expected content: Complete statutory text for W.S. 42-2-103, 42-2-104

5. **NCCP 50-State TANF Benefit Comparison**
   - URL: https://www.nccp.org/wp-content/uploads/2024/11/TANF-Benefit-Amounts-2024-FINAL.pdf
   - Expected content: Wyoming benefit amounts in context of all states

6. **Table II: POWER Income Limits (Official)**
   - URL: https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/table-ii-power-income-limits/
   - Expected content: Complete benefit and income limit table by household size
   - Note: This is an HTML page but contains an embedded image/PDF with the actual table values

---

## Key Implementation Notes

1. **Unique Flat Disregard**: Wyoming uses a flat $600/$1,200 earned income disregard instead of a percentage. This is different from many states that use percentage-based disregards.

2. **Shelter Qualification**: Wyoming has two benefit schedules based on whether the family pays shelter costs. Both need to be parameterized.

3. **Annual COLA**: Benefit amounts are adjusted annually based on Wyoming cost-of-living index. Historical values needed.

4. **Caretaker Relative Program**: Child-only cases where guardian income is NOT counted - may need separate handling.

5. **Table II Values Required**: The actual benefit amounts by household size for both shelter-qualified and shelter-disqualified categories need to be obtained from Table II (official DFS source).

---

## References for Metadata

### For Parameters
```yaml
reference:
  - title: "Wyoming Statute 42-2-103"
    href: "https://codes.findlaw.com/wy/title-42-welfare/wy-st-sect-42-2-103.html"
  - title: "Wyoming DFS SNAP and POWER Policy Manual"
    href: "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/"
```

### For Variables
```python
reference = "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/"
```

---

## Data Gaps / Items Needing Follow-up

1. **Complete Table II Values**: Need actual dollar amounts by household size for both shelter-qualified and shelter-disqualified categories (1-12+ persons)

2. **Effective Dates**: Need historical effective dates for benefit amounts and disregard amounts

3. **COLA History**: Need historical values showing how benefits have changed with annual COLA adjustments

4. **Unearned Income Deductions**: Research did not identify any specific deductions for unearned income (e.g., child support passthrough) - verify this

5. **Work Expense Deductions**: Research did not identify separate work expense deductions beyond the $600/$1,200 flat disregard - verify if Wyoming has additional work expense deductions

6. **Dependent Care Deductions**: Research did not identify dependent care deduction amounts - verify if Wyoming has specific dependent care deductions
