# Collected Documentation

## Wisconsin TANF (Wisconsin Works - W-2) Implementation
**Collected**: 2025-11-23
**Implementation Task**: Simplified implementation focusing on income limits, disregards, and benefit amounts
**State**: Wisconsin
**Agency**: Department of Children and Families (DCF)

---

## Program Overview

Wisconsin Works (W-2) is Wisconsin's TANF program, implemented in 1997 to replace AFDC. Unlike most TANF programs, Wisconsin provides **fixed monthly payments** that do not vary by family size - only by placement type. The program is employment-focused with work participation requirements.

**Key Characteristic**: Wisconsin is one of only two states that provides the same amount of TANF benefits to all families with no countable income, regardless of family size.

### Source Information
- **Primary Manual**: [Wisconsin Works (W-2) Manual](https://dcf.wisconsin.gov/manuals/w-2-manual/Production/default.htm)
- **Administrative Code**: Wisconsin Administrative Code, Chapters DCF 101, DCF 102, DCF 103
- **State Statutes**: Wisconsin Statutes §§ 49.141 - 49.161
- **State Plan**: 2024 WIOA Combined Plan TANF Section (PDF - flagged for extraction)

---

## Income Eligibility - 115% Gross Income Test

### Rule
W-2 applicants must have **total countable income less than or equal to 115% of the Federal Poverty Level (FPL)** for their W-2 Group size.

### 2025 Income Limits (115% of FPL - effective February 1, 2025)

| Household Size | Annual Limit | Monthly Limit |
|----------------|--------------|---------------|
| 1 | $18,000 | $1,500 |
| 2 | $24,324 | $2,027 |
| 3 | $30,648 | $2,554 |
| 4 | $36,972 | $3,081 |
| 5+ | Add $527/person | Add $43.92/person |

**Note**: Income limits are updated annually each February based on federal poverty guidelines.

### References for Parameters
```yaml
# Income limit parameter
reference:
  - title: "W-2 Manual - 3.2.1 115 Percent Gross Income Test"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/03.2.1_115_Percent_Gross_Income_Test.htm"
  - title: "Wisconsin Administrative Code DCF 101.09 - Eligibility for Wisconsin Works"
    href: "https://docs.legis.wisconsin.gov/code/admin_code/dcf/101_199/101/09"
```

---

## Asset Limits

### $2,500 Asset Limit
At application, the W-2 group's assets cannot exceed **$2,500 in combined equity value**, with the following exclusions:

**Vehicle Exclusion**: The first **$10,000 of combined equity value** of the W-2 Group's vehicles is disregarded. Only equity exceeding $10,000 counts toward the $2,500 asset limit.

**Homestead Exclusion**: One home that serves as the primary residence is excluded if valued at **200% of the statewide median home value or less**. Homes exceeding this threshold may still be excluded under hardship criteria:
- No legal right to sell
- Recent sudden income loss (death, divorce, separation)
- Incapacitated family member
- Domestic abuse situation

**Other Excluded Assets**:
- Household and personal effects (unless unusually valuable)
- Individual Development Account (IDA) match funds and accrued interest
- Federal income tax refunds for 12 months from receipt date

**Counted Vehicles**: Mopeds, motorized golf carts, snowmobiles, motorcycles, and airplanes count toward asset limit.

**Excluded Vehicles**: Non-motorized camping trailers, trailer homes, non-motorized boats, farm vehicles producing income, and motorized riding garden mowers.

### References for Parameters
```yaml
# Asset limit parameter
reference:
  - title: "W-2 Manual - 3.3.4 Counting Assets"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/03.3.4_COUNTING_ASSETS.htm"
  - title: "Wisconsin Statutes § 49.145 - Wisconsin Works Eligibility"
    href: "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/145"
```

---

## Payment Standards - Fixed Monthly Amounts

Wisconsin W-2 uses **fixed monthly payments** that do NOT vary by household size. Payments depend only on placement type.

### W-2 Placement Types and Monthly Payments

**Community Service Job (CSJ): $653/month**
- For full-time participation (generally 40 hours/week)
- Not prorated if assigned hours are less than 40 hours/week
- Reduced by $5.00 per hour of unexcused absence

**Prorated CSJ Options** (for part-time workers):
- **1/3 CSJ**: $218/month (up to 20 hours of activity per week, working 20-29 hours/week in unsubsidized employment)
- **1/2 CSJ**: $327/month (up to 25 hours of activity per week, working 15-19 hours/week in unsubsidized employment)
- **2/3 CSJ**: $435/month (up to 30 hours of activity per week, working 10-14 hours/week in unsubsidized employment)

**W-2 Transition (W-2 T): $608/month**
- For individuals unable to work due to incapacity or caring for disabled family member
- Not prorated if assigned hours are less than 40 hours/week
- Reduced by $5.00 per hour of unexcused absence

**Custodial Parent of an Infant (CMC): $673/month**
- For custodial parents with infants **8 weeks old or younger**
- Placement lasts exactly 8 calendar weeks (56 days) from birth date
- No participation requirements during the 8-week period

**At Risk Pregnancy (ARP): $673/month**
- For **unmarried women** in their **third trimester** with medically verified at-risk pregnancy
- Must be unable to work due to at-risk pregnancy
- Exempt from employability plans and sanctions
- Pregnant teens under 18 are ineligible

**Trial Employment Match Program (TEMP)**: Wage subsidy
- Participant receives at least minimum wage from employer
- W-2 agency and employer negotiate wage subsidy (e.g., $4.50/hour)
- Employer supplements the difference

### References for Parameters
```yaml
# Payment standards
reference:
  - title: "Wisconsin Statutes § 49.148 - Wisconsin Works Wages and Benefits"
    href: "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/148"
  - title: "W-2 Manual - 7.4.1 Community Service Jobs (CSJ)"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/07/7.4.1_Community_Service_Jobs_(CSJ).htm"
  - title: "W-2 Manual - 7.4.2 W-2 Transition (W-2 T)"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/07/7.4.2_W-2_Transition_(W-2_T).htm"
  - title: "W-2 Manual - 7.4.5 Custodial Parent of an Infant (CMC)"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/07/7.4.5_Custodial_Parent_of_an_Infant_CMC_.htm"
  - title: "W-2 Manual - 7.4.6 At Risk Pregnancy"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/07/7.4.6_At_Risk_Pregnancy.htm"
  - title: "Wisconsin Administrative Code DCF 101.18 - Employment Position Wages and Benefits"
    href: "https://docs.legis.wisconsin.gov/code/admin_code/dcf/101_199/101/18"
```

---

## Income Counting Rules

### General Rule
All W-2 Group members' **earned and unearned income is counted** in determining the 115% gross income test, unless specifically disregarded.

**CRITICAL**: The W-2 Group's income affects **eligibility only** and does NOT affect the amount of the W-2 payment. The payment amount is determined solely by the employment position (placement type).

### Earned Income
- Employment income (wages, salaries)
- Self-employment income - **gross receipts** (expenses NOT deducted)
- Farm income - **gross receipts** (expenses NOT deducted)

**Self-Employment Calculation**: Monthly self-employment income calculated using:
- Prior-year IRS tax forms, OR
- Self-Employment Income Report (Form DHS 00107) if:
  - Business operated less than one full month previously
  - Business has operated fewer than six months
  - Significant circumstances changed

### Unearned Income
- SSI and Caretaker Supplement (CTS) for adults (children's SSI is excluded)
- Social Security benefits
- Unemployment compensation
- Pensions and retirement income
- Interest and dividends
- Rental income (if not actively managing property 20+ hours/week)
- Child support arrears (non-regular collections counted as assets, not income)

### References for Parameters
```yaml
# Income counting rules
reference:
  - title: "W-2 Manual - 3.2.7 Counting Income"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/03.2.7_Counting_Income.htm"
  - title: "W-2 Manual - 3.2.2 Estimating Income"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/508Compliant/03/03.2.2_Estimating_Income.htm"
```

---

## Income Disregards

Wisconsin W-2 has **extensive income disregards** - many types of income are completely excluded from the income test.

### Fully Disregarded Income

**Child Support**:
- Regular collections of current child support
- Maintenance payments
- Family support
- Regular collections of child support arrears

**Tax Credits and Refunds**:
- Federal Earned Income Tax Credit (EITC)
- State EITC
- Federal income tax refunds
- Advanced EITC payments from employers

**W-2 Program Payments**:
- TEMP (Trial Employment Match Program)
- CMF+ (Case Management Follow-Up Plus)
- CSJ (Community Service Jobs)
- W-2 T (W-2 Transition)
- ARP (At Risk Pregnancy)
- CMC (Custodial Parent of an Infant)
- TSP (Stipends for Noncustodial Parents)

**Dependent Children**:
- All earned income of dependent children in W-2 group
- SSI payments received by dependent children

**Loans and Assets**:
- Loans (unless available for current living expenses)
- Job Access Loans
- Reverse mortgage proceeds
- Gifts (unconditional, non-obligatory)

**In-Kind Benefits**:
- Meals, clothing, housing
- Garden produce
- Any gain or benefit not in the form of money paid directly to household

**Government Benefits**:
- Vendor payments made on household behalf
- Kinship care and foster care payments
- Jail/prison employment income

**Educational Aid**:
- Scholarships
- Student loans
- Grants
- Work-study funds

**Federal Benefits** (extensive list including):
- Agent Orange settlements
- Radiation compensation
- Crime victim funds
- Nutrition programs
- Tribal settlements
- Disaster relief

### Limited/Conditional Disregards

**AmeriCorps VISTA**: Disregarded unless volunteers receive minimum wage or more

**Operation Fresh Start**: Similar minimum wage threshold applies

**Tribal Judgment Funds**: Disregard annual income of $2,000 or less

**Rehabilitation Act**: Disregard accommodation-related wages and reimbursements

### References for Parameters
```yaml
# Income disregards
reference:
  - title: "W-2 Manual - 3.2.8 Disregarding Income"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/03.2.8_DISREGARDING_INCOME.htm"
  - title: "Wisconsin Administrative Code DCF 101.09(4)(c) - Income Exclusions"
    href: "https://docs.legis.wisconsin.gov/code/admin_code/dcf/101_199/101/09"
```

---

## Eligibility Criteria

### Demographic Eligibility

**Age Requirements**:
- Applicant must be at least **18 years old**
- Dependent child: under **18 years old**, OR
- Under **19 years old** if full-time student at secondary school or vocational/technical equivalent and reasonably expected to complete program before age 19

**Custodial Parent Status**:
- Must be a custodial parent of a dependent child

**W-2 Group Composition**:
- Custodial parents
- Dependent children
- Spouses/non-marital co-parents (if residing in same household)

### References for Parameters
```yaml
# Age requirements
reference:
  - title: "Wisconsin Administrative Code DCF 101.03(35) - Dependent Child Definition"
    href: "https://docs.legis.wisconsin.gov/code/admin_code/dcf/101_199/101/03/35"
  - title: "W-2 Manual - 2.08.2 Temporary Absence of a Child"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/508Compliant/02/2.08.2_Temporary_Absence_Of_A_Child.htm"
```

### Immigration Eligibility

**U.S. Citizens**: Citizenship verified once per lifetime of case

**Qualified Non-Citizens** (must verify through SAVE):
- Lawful Permanent Residents (LPRs)
- Asylees
- Refugees
- Trafficking victims
- Parolees
- Cuban/Haitian entrants
- Iraqi/Afghan special immigrants
- Various other documented immigrant categories

**Sponsor Deeming**: For sponsored aliens (LPRs), sponsor's income and resources must be counted unless individual belongs to exempt categories (asylees, refugees, parolees, those with deportation withheld, Amerasian immigrants, or Cuban-Haitian entrants).

**Presumptive Eligibility**: Once applicants provide qualifying documentation, they receive presumptive eligibility pending SAVE verification. Agencies must not delay or deny eligibility based on immigration status while verification is pending.

### References for Parameters
```yaml
# Immigration eligibility
reference:
  - title: "W-2 Manual - 2.04.1 Verifying U.S. Citizenship or Qualified Non-Citizen Status"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/02/2.04.1_Verifying_US_Citizenship_Qualified_Non-Citizen_Status.htm"
  - title: "Wisconsin Administrative Code DCF 101.09(2) - Nonfinancial Eligibility Requirements"
    href: "https://docs.legis.wisconsin.gov/code/admin_code/dcf/101_199/101/09"
```

### Other Nonfinancial Requirements

**State Residency**: Must reside in Wisconsin

**Child Support Cooperation**: Must fully cooperate in good faith with efforts to establish paternity and obtain support payments (three failures without cause = 6-month ineligibility)

**Employment Search**: Must demonstrate good faith effort to obtain unsubsidized employment and cannot have refused a bona fide job offer in preceding 180 days

**Income Support Restrictions**: Cannot be receiving SSI, state supplemental payments, or Social Security Disability Insurance

**Social Security Number**: Must apply for or provide a Social Security account number

**Change Reporting**: Must report eligibility changes within 10 days

**Other Assistance Programs**: Must cooperate in applying for available public assistance

### References for Parameters
```yaml
# Other eligibility requirements
reference:
  - title: "Wisconsin Administrative Code DCF 101.09 - Eligibility for Wisconsin Works"
    href: "https://docs.legis.wisconsin.gov/code/admin_code/dcf/101_199/101/09"
  - title: "Wisconsin Statutes § 49.145 - Wisconsin Works Eligibility"
    href: "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/145"
```

---

## Time Limits (NON-SIMULATABLE - Architecture Limitation)

### State 48-Month Lifetime Limit
W-2 participants can receive W-2 services for up to **48 months** over their lifetime. Only months of TANF cash assistance received after September 1, 1996, count toward this limit.

### Federal 60-Month Lifetime Limit
Individuals can receive federal TANF cash assistance for up to **60 months** total.

**Note**: The months that count toward each limit don't always align. Certain placements (e.g., CMC) may count differently toward state vs. federal limits.

### Time Limit Extensions
Extensions may be granted on a case-by-case basis for TEMP, CSJ, W-2 T, and CMC participants based on:
- Barriers to employment
- Local labor market conditions
- Family hardships

### Non-Simulatable Rules
```markdown
### NON-SIMULATABLE RULES (Architecture Limitation)
- **48-Month State Lifetime Limit**: [CANNOT ENFORCE - requires tracking participation history]
- **60-Month Federal Lifetime Limit**: [CANNOT ENFORCE - requires tracking TANF receipt across all states]
- **24-Month Employment Position Time Limits**: [CANNOT ENFORCE - requires tracking time in specific placements]

**Implementation Note**: PolicyEngine's single-period architecture cannot track lifetime or cumulative time limits. These rules are documented for informational purposes only but cannot be enforced in benefit calculations.
```

### References for Parameters
```yaml
# Time limits (informational only - non-simulatable)
reference:
  - title: "W-2 Manual - 2.10.2 State 48-Month Lifetime Limit"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/02/2.10.2_State_60-Month_Lifetime_Limit.htm"
  - title: "W-2 Manual - 2.10.9 Federal 60-Month Lifetime Limit"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/02/2.10.9_Federal_60-Month_Lifetime_Limit.htm"
  - title: "W-2 Manual - 2.10.1 Introduction to Time Limits"
    href: "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/02/2.10.1_Introduction_to_Time_Limits.htm"
```

---

## Work Requirements (NON-SIMULATABLE - Skip for Simplified Implementation)

Wisconsin W-2 has extensive work participation requirements that vary by placement type. However, **for the simplified implementation, we focus only on eligibility and benefit calculation, NOT work requirements**.

**Note**: Work requirements involve tracking hours of participation, activities, and sanctions over time - these are non-simulatable in PolicyEngine's single-period architecture and are outside the scope of benefit eligibility modeling.

---

## Implementation Notes

### Simplified Implementation Approach

For this implementation, we will focus on:

1. **Income Eligibility**: 115% FPL test using gross income
2. **Asset Eligibility**: $2,500 limit with vehicle/homestead exclusions
3. **Payment Standards**: Fixed monthly amounts by placement type
4. **Income Disregards**: Extensive list of excluded income sources
5. **Basic Demographic Eligibility**: Age, custodial parent status

### What We Will NOT Implement (Non-Simulatable)

1. **Time Limits**: Cannot track 48-month or 60-month lifetime limits
2. **Work Requirements**: Cannot track participation hours or activities
3. **Sanctions**: Cannot track progressive sanctions over time
4. **Placement Assignments**: Cannot determine which placement type participant should be assigned to
5. **Case Management**: Cannot model ongoing case reviews and compliance

### Implementation Strategy

**Use Federal Baseline Where Applicable**:
- [x] Use federal demographic eligibility (age 18, age 19 for students - **matches federal baseline**)
- [x] Use federal immigration eligibility (follows federal qualified alien rules - **matches federal baseline**)

**State-Specific Implementation Required**:
- [ ] Create state-specific income test (115% FPL)
- [ ] Create state-specific asset test ($2,500 with exclusions)
- [ ] Create state-specific payment standards (fixed amounts, not family-size-based)
- [ ] Create state-specific income disregards (extensive exclusions)

**Key Difference from Most TANF Programs**:
Wisconsin W-2 is unique because:
1. **Fixed payments** that don't vary by family size
2. **Employment-based placements** with different payment levels based on work capacity, not family composition
3. **Extensive income disregards** including all child support
4. **No benefit reduction rate** - payments are fixed, not calculated based on income

This means the implementation is simpler in some ways (no benefit calculation formulas) but requires modeling multiple placement types.

---

## PDF Documents Requiring Extraction

The following PDF contains critical information that needs extraction:

1. **2024 WIOA Combined Plan TANF Section**
   - URL: https://dcf.wisconsin.gov/files/w2/tanf-state-plans/2024-wioa-combined-plan-tanf-section-for-comment.pdf
   - Purpose: Wisconsin's official TANF State Plan describing program structure, benefit standards, and policy changes
   - Key content: Program overview, benefit calculation methodology, historical context, policy updates
   - Note: May contain additional details on payment standards, eligibility criteria, or state-specific variations not available in HTML sources

**Status**: PDF extraction required - documentation incomplete without this state plan.

---

## Additional Resources

**W-2 Manual Releases**: Wisconsin publishes regular manual releases with policy updates:
- Release 25-01 (February 4, 2025): Most recent
- Release 24-12 (October 29, 2024)
- Release 24-11 (October 17, 2024)
- Release 24-08 (June 3, 2024)
- Release 24-07 (May 1, 2024)
- Release 24-04 (February 20, 2024)

**Administrative Code Navigation**:
- DCF 101: Wisconsin Works program rules
- DCF 102: Child support cooperation for W-2
- DCF 103: W-2 worker training

**Key Statute Sections**:
- § 49.141: Wisconsin Works general provisions
- § 49.145: Eligibility for employment positions
- § 49.148: Wages and benefits
- § 49.149: Education and training
- § 49.151: Sanctions
- § 49.155: Wisconsin Shares child care subsidy

---

## Effective Dates

**Current Rules**: As of 2025
**Income Limits**: Updated annually each February based on federal poverty guidelines
**Payment Standards**: Current as of 2024-2025 (verify for most recent updates)

**Note**: Always verify effective dates when implementing - Wisconsin regularly updates W-2 policies through manual releases.

---

## Documentation Quality Checklist

- [x] Authoritative sources (official DCF manual, administrative code, statutes)
- [x] Current rules (2024-2025)
- [x] Complete coverage (eligibility, benefits, income, assets)
- [x] Specific citations (manual sections, code sections, statute sections)
- [x] Clear explanations with examples
- [x] Structured organization
- [x] Non-simulatable rules flagged
- [x] Implementation approach documented
- [ ] State Plan PDF extracted (pending)

---

## Summary for Implementation

Wisconsin W-2 is unique among TANF programs:

**Eligibility**: 115% FPL income test, $2,500 asset test, standard demographic requirements

**Benefits**: Fixed monthly payments by placement type (CSJ $653, W-2T $608, CMC/ARP $673), NOT based on family size

**Income Rules**: All income counted except extensive disregards (child support, tax credits, W-2 payments, dependent child income, many federal benefits)

**Key Simplification**: No benefit reduction formula - participants receive fixed payment amounts based on placement type, making benefit calculation straightforward once eligibility is determined

**Critical Limitation**: Cannot model placement assignment - would need policy decision on which placement type to assume for eligible families

---

**Documentation Collection Complete** (except State Plan PDF extraction pending)
