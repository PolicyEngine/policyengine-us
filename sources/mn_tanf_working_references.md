# Minnesota MFIP (Minnesota Family Investment Program) - Working References

**Collected**: 2025-11-24
**Implementation Task**: Simplified Minnesota TANF implementation using federal baseline for income definitions
**Program**: MFIP (Minnesota Family Investment Program) - Minnesota's TANF program
**Jurisdiction**: Minnesota (MN)
**Administering Agency**: Minnesota Department of Children, Youth, and Families (DCYF) - effective July 1, 2024
**GitHub Issue**: #6793

---

## Program Overview

The Minnesota Family Investment Program (MFIP) is Minnesota's Temporary Assistance for Needy Families (TANF) program, providing temporary cash and food assistance to families. MFIP combines cash assistance with SNAP food benefits into a single grant.

**Key Features:**
- Combined cash and food benefit grant
- Earned income disregards to support work
- Housing assistance grant available to eligible families
- 60-month lifetime limit with possible extensions
- Exit threshold at approximately 135% of Federal Poverty Guidelines

**Recent Changes:**
- July 1, 2024: Administration transferred from DHS to new Department of Children, Youth, and Families (DCYF)
- March 1, 2024: U-Visa holders became eligible for state-funded MFIP
- October 1, 2024: Housing assistance grant adjusted for inflation ($117/month)

---

## Demographic Eligibility

### Age Requirements

**Minor Child Definition** (MN Statute 256J.08, Subd. 60 / 142G.08):
- Less than 18 years of age, OR
- Under 19 years of age AND a full-time student in secondary school or vocational/technical training

**Requirements:**
- Minor child must live with parent or caregiver
- Cannot be the parent of a child in the home
- Must be in same home with caregiver (with limited exceptions)

**Implementation Approach:**
- [x] Use federal demographic eligibility baseline (age 18/19 matches federal rules)
- Minor child age limit: 18 years (19 if full-time student)
- Pregnant women: Eligible

### Assistance Unit Composition

**Requirements** (MN Statute 142G.13):
- Must include at least one minor child OR a pregnant woman
- Minor child and caregiver must reside together (with limited exceptions)
- SSI-eligible children may be included but their needs are not counted in benefit calculation

**Caregiver Definition** (MN Statute 256J.08, Subd. 11):
- Natural or adoptive parents
- Stepparents
- Legal custodians
- Grandparents, siblings, aunts, uncles, cousins and their spouses (when living with and caring for minor child)

### Immigration Eligibility

**Implementation Approach:**
- [x] Use federal immigration eligibility baseline
- Recent change: U-Visa holders eligible as of March 1, 2024 (state-funded)

---

## Income Eligibility

### Income Limits - Family Wage Level (FWL)

**Formula**: Family Wage Level = 110% of Transitional Standard

**Purpose**:
- Used for initial eligibility determination
- Families are ineligible when countable income equals or exceeds the Family Wage Level
- Only used for benefit calculation when earned income is present

**Exit Threshold**: Families exit MFIP when income reaches approximately 135% of Federal Poverty Guidelines

**Example (2025 FPG):**
- Family of 3: 135% of FPG = 135% × $26,650 = $35,978 annually

### Income Sources

**Implementation Approach:**
- [x] Use federal baseline income sources (standard employment and self-employment income)
- Income must be "available" to assistance unit (legal access required)
- All payments counted unless specifically excluded

**Earned Income** (MN Statute 256J.08, Subd. 26):
- Cash or in-kind income from wages, salary, commissions
- Profit from employment and similar labor-based payments

**Unearned Income** (MN Statute 256J.08, Subd. 86):
- Unemployment benefits
- Disability payments
- Pensions
- Child support
- Interest income

### Earned Income Disregards

**Formula** (MN Statute 256P.03):
```
Disregarded Amount = $65 + (Remaining Earned Income × 0.5)
Countable Earned Income = Gross Earned Income - Disregarded Amount
```

**Application**:
- $65 disregarded per eligible wage earner per month
- 50% of remaining earnings disregarded
- Applied every month there is earned income
- Applied at gross earnings level (before payroll deductions)

**Example Calculation**:
```
Gross Earnings: $1,000/month
Step 1: $1,000 - $65 = $935 remaining
Step 2: $935 × 0.5 = $467.50 disregarded
Step 3: $1,000 - ($65 + $467.50) = $467.50 countable earned income
```

### Unearned Income Deductions

**Child Support Passthrough/Disregard**:
- $100/month disregarded for family with 1 child
- $200/month disregarded for family with 2+ children
- Amounts above disregard reduce benefits dollar-for-dollar
- 100% of current child support passed through to families
- Reduction in MFIP occurs two months after child support is collected

**Other Unearned Income**:
- Generally counted dollar-for-dollar
- Exception: RSDI disregarded up to SSI standard per household member

**Child Support Paid**:
- Court-ordered spousal support payments are fully disregarded
- Child support paid for children not in assistance unit is fully disregarded

### Dependent Care Deduction

**Initial Eligibility Determination** (MN Statute 256J.21):
- Actual amount paid for dependent care deducted from gross earned income
- Maximum $200/month per child under age 2
- Maximum $175/month per child age 2 and older

---

## Asset Limits

**Asset Limit**: $10,000 (MN Statute 256P.02)

**Assets Counted**:
- Cash
- Bank accounts
- Liquid stocks and bonds (accessible without penalty)
- Some vehicles

**Vehicle Exclusion**:
- One vehicle per eligible household member age 16 or older is excluded
- Additional vehicles count toward the $10,000 asset limit

---

## Benefit Calculation

### Transitional Standard (Full Benefit)

**Definition**: The basic standard for families without earned income, combining cash and food portions.

**2025 Transitional Standards** (Published by DCYF):
| Family Size | Monthly Benefit |
|-------------|-----------------|
| 1           | (Not found in search - check Combined Manual) |
| 2           | (Not found in search - check Combined Manual) |
| 3           | $1,394 |
| 4           | $1,675 |
| 5+          | (Check Combined Manual 0020.09) |

**Annual Adjustment**:
- Adjusted October 1 each year based on SNAP COLA
- Commissioner publishes adjusted standards for unit sizes 1-10 in State Register
- Food portion adjusted to reflect SNAP adjustments

**Note**: For complete table of all family sizes, see Minnesota DHS Combined Manual section 0020.09 (MFIP/DWP Assistance Standards)

### Payment Standards Calculation

**For Families WITHOUT Earned Income**:
```
Monthly Grant = Transitional Standard
```

**For Families WITH Earned Income**:
```
Step 1: Calculate Net Earned Income
   Gross Earned Income
   - $65 per wage earner
   - 50% of remaining earnings
   = Net Earned Income

Step 2: Calculate Family Wage Level
   Family Wage Level = Transitional Standard × 1.10

Step 3: Calculate Grant Amount
   Monthly Grant = Family Wage Level - Net Earned Income

   If Monthly Grant ≥ Transitional Standard:
      Payment = Transitional Standard
   Else:
      Payment = Monthly Grant
```

**For Families WITH Unearned Income**:
```
Monthly Grant = Transitional Standard - Unearned Income (dollar-for-dollar)

Exception for Child Support:
   - First $100 (1 child) or $200 (2+ children) disregarded
   - Only amount above disregard reduces benefits
```

**Benefit Composition**:
- Cash portion reduced first when income present
- Food portion reduced second
- Both portions issued via electronic debit card

**Minimum Benefit**:
- $10 minimum monthly grant if eligible
- Must have at least $1 result from eligibility computation to be eligible

### MFIP Housing Assistance Grant

**Amount**: $117/month (as of October 1, 2024)

**Eligibility**:
- Available to qualifying MFIP families
- Not all families qualify
- No proration - eligible for full amount if eligible any day in the month

**Key Features**:
- Additional cash benefit beyond regular MFIP grant
- Income does not affect the housing grant amount
- Not subject to 10% or 30% sanctions (but ends with 100% sanctions)
- Counts toward 60-month lifetime limit
- Adjusted annually for inflation each October 1 based on CPI-U

**Inflation Adjustment**:
- Previous amount: $110/month
- October 1, 2024 adjustment: Increased to $117/month (+$7)
- Statute requires annual adjustment based on Consumer Price Index

---

## Time Limits and Work Requirements

### Time Limits

**Lifetime Limit**: 60 months of assistance (MN Statute 142G)

**Extensions**: Some families may qualify for extensions beyond 60 months if they meet criteria for:
- Ill or incapacitated
- Hard-to-employ
- Employed participants

**DWP (Diversionary Work Program)**:
- Short-term benefit (maximum 4 consecutive months)
- Does NOT count toward 60-month TANF time limit
- Non-recurrent benefit to address family crisis

### Work Requirements

**Note**: This simplified implementation focuses on eligibility and benefit calculation only. Work participation requirements are NOT modeled in PolicyEngine's single-period architecture.

---

## Residency Requirements

**Residency Requirement** (MN Statute 256J.12 / 142G.12):
- Must have established residency in Minnesota
- "Established residency" = present in state with intent to remain
- Must reside in state for at least 30 consecutive days
- Time in battered women's shelter counts toward 30-day requirement
- Birth of child in Minnesota does NOT automatically establish residency

**Intent to Remain**:
- Person who entered state with job commitment or to seek employment meets criteria
- Employment status (employed/unemployed) does not affect residency determination

---

## Special Rules and Exceptions

### Minor Parents

**Living Arrangement Requirements**:
- Minor parent and their child must reside in household of:
  - Parent of minor parent
  - Legal guardian
  - Other adult relative
  - Adult-supervised supportive living arrangement
- Exceptions may apply in certain circumstances

### SSI Recipients in Assistance Unit

- Assistance unit can include SSI-eligible minor children
- SSI recipient's needs NOT counted in MFIP benefit calculation
- Family still eligible for MFIP

### Application Processing

**Timeline** (MN Statute 256J.09):
- County must process application within 30 days
- If unable to process, must inform applicant of delay in writing
- Cannot deny solely because 30-day period expired if applicant unable to provide verification

---

## Program Statistics (FY 2024)

**Participation**:
- Average monthly: 22,739 families, 62,137 participants
- Estimated FY 2025: 23,755 families, 65,858 participants

**Expenditures (FY 2024)**:
- Cash portion: $164.1 million
- Food portion: $132.7 million
- Total: $296.8 million

**Program Duration**:
- Most families receive MFIP for 12 months or less
- Most participants are children or infants

---

## Non-Simulatable Rules (Architecture Limitation)

### Cannot Be Fully Simulated (Single-Period Architecture):

- **60-Month Lifetime Limit**: Cannot track cumulative months of assistance across time
- **Time-Limited Extensions**: Cannot track ill/incapacitated or hard-to-employ status over time
- **Work History Requirements**: Cannot verify work participation or compliance
- **Sanctions**: Cannot track progressive sanctions or compliance over time
- **DWP 4-Month Limit**: Cannot track consecutive months of DWP receipt
- **Child Support Collection Timing**: "Reduction happens two months after collection" cannot be modeled
- **Application Processing Delays**: Cannot model 30-day processing timelines

### Can Be Simulated (Current Point-in-Time):

- Current income eligibility (Family Wage Level test)
- Current asset limits ($10,000)
- Current household composition
- Benefit calculation for current month
- Earned income disregards
- Child support disregards
- Housing assistance grant eligibility and amount

---

## Key References for Implementation

### Primary Legal Authorities

**Minnesota Statutes - Current (Chapter 142G)**:
- [Chapter 142G - Minnesota Family Investment Program](https://www.revisor.mn.gov/statutes/cite/142G/pdf)
- [Sec. 142G.01 - Citation and General Provisions](https://www.revisor.mn.gov/statutes/cite/142G.01)
- [Sec. 142G.13 - Assistance Unit Composition](https://www.revisor.mn.gov/statutes/cite/142G.13)

**Minnesota Statutes - Legacy (Chapter 256J) - RENUMBERED to 142G**:
- [Ch. 256J - Full Chapter](https://www.revisor.mn.gov/statutes/2021/cite/256J/full)
- [Sec. 256J.08 - Definitions](https://www.revisor.mn.gov/statutes/cite/256J.08)
- [Sec. 256J.21 - Income Exclusions and Benefit Calculation](https://www.revisor.mn.gov/statutes/cite/256J.21)

**Minnesota Statutes - Chapter 256P (Income Provisions)**:
- [Ch. 256P - Income and Asset Provisions](https://www.revisor.mn.gov/statutes/cite/256P/full)
- [Sec. 256P.03 - Earned Income Disregard](https://www.revisor.mn.gov/statutes/cite/256P.03)
- [Sec. 256P.02 - Asset Limits](https://www.revisor.mn.gov/statutes/cite/256P.02)

### Administrative Resources

**Minnesota DHS Combined Manual**:
- [Combined Manual 0020.09 - MFIP/DWP Assistance Standards](https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&dDocName=cm_002009&RevisionSelectionMethod=LatestReleased)
- [Combined Manual 0018.18 - Earned Income Disregards](https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=cm_001818)
- [Combined Manual 0022.12 - How to Calculate Benefit Level](https://www.dhs.mn.gov/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=cm_002212)
- [Combined Manual 0013.03.09 - MFIP Housing Assistance Grant](https://www.dhs.mn.gov/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=CM_00130309)

**Employment Services Manual (ESM)**:
- [ESM 3.9 - Income and Asset Limits for MFIP/DWP](https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=ESM_000309)
- [ESM 3.12 - MFIP Benefit Amounts](https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=ESM_000312)
- [ESM 24.3 - MFIP Initial Eligibility Threshold Guide](https://www.dhs.mn.gov/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=ESM_002403)

### Policy Documentation

**Minnesota House Research Department**:
- [MFIP Short Subject (PDF)](https://www.house.mn.gov/hrd/pubs/ss/ssmfip.pdf) - **[PDF REQUIRES EXTRACTION]**
- [MFIP Program at a Glance (PDF)](https://www.house.mn.gov/hrd/pubs/pap_mfip.pdf) - **[PDF REQUIRES EXTRACTION]**

**Federal TANF State Plan**:
- [Minnesota PYs 2024-2027 TANF State Plan](https://wioaplans.ed.gov/node/544926)

**Agency Information**:
- [Minnesota DCYF - MFIP Program Page](https://dcyf.mn.gov/programs-directory/minnesota-family-investment-program-mfip)
- [Minnesota DHS - MFIP Information](https://mn.gov/dhs/people-we-serve/children-and-families/economic-assistance/income/programs-and-services/mfip.jsp)

### Third-Party Resources (For Verification Only)

- [DB101 Minnesota - MFIP: The Basics](https://mn.db101.org/mn/programs/income_support/mfip/program.htm)
- [DB101 Minnesota - MFIP: The Details](https://mn.db101.org/mn/programs/income_support/mfip/program2.htm)

---

## References for Parameter Metadata

### For Parameters (YAML):

```yaml
reference:
  - title: "Minnesota Statute 256P.03 - Earned Income Disregard"
    href: "https://www.revisor.mn.gov/statutes/cite/256P.03"
  - title: "Minnesota DHS Combined Manual 0018.18 - Earned Income Disregards"
    href: "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=cm_001818"
```

### For Variables (Python):

```python
reference = "https://www.revisor.mn.gov/statutes/cite/256P.03"  # Full clickable URL
# NOTE: Do NOT use documentation field - use reference URL instead
```

---

## Implementation Notes

### Simplified Implementation Approach

This is a **simplified implementation** that:
1. Uses federal baseline for income source definitions
2. Uses federal demographic eligibility rules (age thresholds match)
3. Uses federal immigration eligibility baseline
4. Models only current point-in-time eligibility and benefits
5. Does NOT model work requirements or time limits

### Key Implementation Requirements

**Age Thresholds**:
- Minor child: Under 18 (or under 19 if full-time student)
- Matches federal TANF baseline

**Income Calculations**:
- Earned income disregard: $65 + 50% of remainder
- Apply to gross earned income
- Child support disregard: $100 (1 child) / $200 (2+ children)

**Benefit Structure**:
- Transitional Standard = Full benefit (no earnings)
- Family Wage Level = 110% of Transitional Standard
- Use FWL for eligibility test when earned income present
- Separate cash and food portions (cash reduced first)

**Parameters to Implement**:
1. Transitional Standard by family size (1-10+)
2. Earned income disregard amounts ($65, 50%)
3. Child support disregard amounts ($100, $200)
4. Asset limit ($10,000)
5. Housing assistance grant ($117 as of Oct 2024)
6. Exit threshold (135% FPL)

### Data Gaps Requiring Follow-Up

1. **Complete Transitional Standard Table**: Need amounts for family sizes 1, 2, 5, 6, 7, 8, 9, 10
   - Source: Combined Manual 0020.09 or State Register publication
   - Only found: Family of 3 = $1,394, Family of 4 = $1,675

2. **Historical Benefit Amounts**: For testing and validation
   - Pre-2025 amounts (if implementation needs historical data)
   - Old cash-only amounts: $437 (family of 2), $532 (family of 3), $621 (family of 4)

3. **Cash vs. Food Portion Breakdown**: For accurate benefit composition
   - Need breakdown of transitional standard into cash and food components
   - Source: Combined Manual 0020.09

---

## PDFs Requiring Extraction

The following PDFs contain critical information but could not be extracted automatically:

1. **Minnesota House Research - MFIP Short Subject**
   - URL: https://www.house.mn.gov/hrd/pubs/ss/ssmfip.pdf
   - Purpose: Comprehensive MFIP program overview with benefit tables
   - Key Information Expected: Complete transitional standard table, historical context, program statistics

2. **Minnesota House Research - MFIP Program at a Glance**
   - URL: https://www.house.mn.gov/hrd/pubs/pap_mfip.pdf
   - Purpose: Concise program summary with benefit amounts
   - Key Information Expected: Current benefit levels, eligibility rules, policy changes

3. **50-State TANF Comparison (NCCP)**
   - URL: https://www.nccp.org/wp-content/uploads/2024/11/TANF-Benefit-Amounts-2024-FINAL.pdf
   - Purpose: Cross-state comparison of TANF benefit amounts
   - Key Information Expected: Minnesota's benefit amounts as % of FPL and absolute dollars

**Note**: These PDFs may contain the complete transitional standard table for all family sizes (1-10) which was not found in HTML sources.

---

## Documentation Completeness Assessment

**Status**: Substantially Complete for Simplified Implementation

**What We Have**:
- [x] Legal authority (Minnesota Statutes 142G, 256J, 256P)
- [x] Eligibility requirements (age, residency, household composition)
- [x] Income disregards formula ($65 + 50%)
- [x] Child support disregard ($100/$200)
- [x] Asset limits ($10,000)
- [x] Benefit calculation methodology
- [x] Housing assistance grant ($117)
- [x] Exit thresholds (135% FPL)
- [x] 2025 benefit amounts for families of 3 and 4
- [x] Administrative agency information
- [x] References for parameter metadata

**What We Need**:
- [ ] Complete transitional standard table (all family sizes 1-10)
- [ ] Cash/food portion breakdown of transitional standards
- [ ] Extracted content from House Research PDFs
- [ ] Historical benefit amounts (if needed for testing)
- [ ] State Plan PDF content (if contains additional formulas)

**Ready for Implementation**: YES
- Sufficient information for simplified implementation
- Can proceed with known benefit amounts (families 3-4)
- Can add remaining family sizes when data obtained
- All formulas and eligibility rules clearly documented

**For Complete Implementation**:
- Request manual extraction of PDFs listed above
- Access Combined Manual 0020.09 directly for complete table
- Or contact DCYF for official benefit standards publication

---

## Change Log

**2025-11-24**: Initial documentation collection
- Gathered primary legal authorities (Chapter 142G, 256P)
- Documented benefit calculation methodology
- Identified 2025 benefit amounts for families of 3 and 4
- Compiled administrative references
- Flagged PDFs requiring extraction

---

## Contact Information

**Minnesota Department of Children, Youth, and Families (DCYF)**
- Website: https://dcyf.mn.gov
- MFIP Program: https://dcyf.mn.gov/programs-directory/minnesota-family-investment-program-mfip

**Minnesota Department of Human Services (DHS)** - Legacy
- Combined Manual: https://www.dhs.state.mn.us
- Employment Services Manual: https://www.dhs.state.mn.us

**Legislative Information**
- Minnesota Revisor of Statutes: https://www.revisor.mn.gov/statutes
- Minnesota House Research: https://www.house.mn.gov/hrd/
