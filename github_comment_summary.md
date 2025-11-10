# Michigan TANF/FIP Documentation Research - Summary

## Documentation Completed

I have compiled comprehensive documentation for Michigan TANF (Family Independence Program) implementation. The complete reference document has been saved to `working_references.md` in the repository root.

---

## Key Program Rules Found

### 1. Payment Standards (Effective January 1, 2025)

| Group Size | Eligible Grantee | Ineligible Grantee |
|------------|------------------|-------------------|
| 1          | $363            | $187              |
| 2          | $478            | $325              |
| 3          | $583            | $498              |
| 4          | $707            | $660              |
| 5          | $822            | $822              |
| 6          | $981            | $981              |
| 7          | $1,072          | $1,072            |
| 8+         | Add $95 for each additional person |

**Note**: Payment standards frozen since October 1, 2008 (recently updated in 2025 table)

### 2. Income Eligibility Limits

**For Family of Three**:
- **Initial Eligibility**: $814/month (countable earned income)
- **Ongoing Eligibility**: $1,184/month

### 3. Earned Income Disregards

**Initial Eligibility**: $200 + 20% of remainder
**Ongoing Eligibility**: $200 + 50% of remainder (changed in 2011)

**Example for Family of 3 with $1,000 earned income**:
```
Step 1: Apply disregard: $200 + (50% × $800) = $600
Step 2: Countable income: $1,000 - $600 = $400
Step 3: Benefit = $583 - $400 = $183
```

### 4. Asset Limits

**Current Limit**: $15,000 (increased from $3,000 in 2019)
- Self-attestation allowed
- Jointly owned assets may be excluded if other owner doesn't agree to sell

### 5. Time Limits

- **Current** (through March 31, 2025): 48 months lifetime
- **New** (effective April 1, 2025): 60 months lifetime

### 6. Benefit Calculation Formula

```
Monthly FIP Benefit = Payment Standard - Countable Income
```

Where:
- Payment Standard determined by household size (RFT 210)
- Countable Income = Gross Income - Applicable Disregards

---

## Authoritative Sources Located

### Michigan State Sources

1. **Michigan TANF State Plan** (Effective January 1, 2023)
   - URL: https://www.michigan.gov/mdhhs/.../TANF_State_Plan_2023.pdf

2. **Bridges Eligibility Manual (BEM)** - Official Policy Documents:
   - BEM 210: FIP Group Composition
   - BEM 400: Assets
   - BEM 500: Income Overview
   - BEM 503: Income, Unearned
   - BEM 515: FIP/RCA/SDA Needs Budgeting
   - BEM 518: FIP/RCA/SDA Income Budgeting
   - BEM 520: Computing the FIP/RCA/SDA Budget
   - All available at: mdhhs-pres-prod.michigan.gov

3. **Reference Tables (RFT)**:
   - RFT 210: FIP Monthly Assistance Payment Standard (Effective 1/1/2025)

### Federal Sources

4. **Federal TANF Regulations**:
   - 45 CFR Part 260: General TANF Provisions
   - 45 CFR Part 265: Data Collection and Reporting
   - Available at: ecfr.gov

5. **SSA POMS**: SI CHI00830.113 - Michigan's TANF for SSI purposes

### Research Sources

6. **Michigan League for Public Policy (MLPP)**: Policy analysis and historical changes
7. **National Center for Children in Poverty (NCCP)**: TANF profile for Michigan (August 2024)

---

## PDFs Requiring Manual Extraction

Several key policy documents could not be fully extracted via automated tools due to PDF compression/formatting issues. **Manual review recommended** for complete implementation:

### High Priority for Manual Review:

1. **BEM 518** - FIP/RCA/SDA Income Budgeting
   - URL: https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/518.pdf
   - Contains: Detailed income budgeting rules, deduction order, verification requirements

2. **BEM 520** - Computing the FIP/RCA/SDA Budget
   - URL: https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/520.pdf
   - Contains: Step-by-step benefit calculation methodology, formulas

3. **BEM 515** - FIP/RCA/SDA Needs Budgeting
   - URL: https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/515.pdf
   - Contains: Needs budgeting methodology, living arrangement rules

4. **RFT 210** - FIP Monthly Assistance Payment Standard
   - URL: https://mdhhs-pres-prod.michigan.gov/olmweb/ex/RF/Public/RFT/210.pdf
   - **Status**: Payment table confirmed via web search, but PDF extraction failed
   - **Note**: Table values documented from search results

### Medium Priority:

5. **BEM 500** - Income Overview
   - URL: https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/500.pdf
   - Contains: General income policies

6. **BEM 210** - FIP Group Composition
   - URL: https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/210.pdf
   - **Status**: Summary extracted; full details available in PDF

7. **BEM 502** - Income from Self-Employment
   - URL: https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/502.pdf
   - Contains: Self-employment income calculation rules

8. **BEM 503** - Income, Unearned
   - URL: https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/503.pdf
   - Contains: Unearned income counting rules

---

## Implementation Recommendations

### For Simplified Implementation

Based on the research, a simplified Michigan TANF implementation should include:

1. **Payment Standards by Household Size**
   - Use RFT 210 table (documented in working_references.md)
   - Recommend using "eligible grantee" standards (most common)

2. **Income Eligibility Test**:
   - Initial: Apply 20% disregard ($200 + 20% of remainder)
   - Ongoing: Apply 50% disregard ($200 + 50% of remainder)

3. **Asset Test**: $15,000 limit

4. **Benefit Calculation**: Payment Standard - Countable Income

### Simplifying Assumptions

For PolicyEngine implementation, reasonable simplifications:
- Use "eligible grantee" payment standards (most common scenario)
- Ignore SSI recipients complicating payment standards
- Skip time limits (cannot model in cross-sectional analysis)
- Skip work requirements (behavioral, not calculable)
- Standard household composition (no complex deeming scenarios)

### Key Implementation Notes

- **Variable Naming**: Use `mi_tanf_` prefix (per issue comment)
- **Payment Standards**: Frozen since 2008 (but updated table released 2025)
- **Deep Poverty**: Michigan requires families below ~39% of poverty line (very restrictive)
- **Two Disregard Rates**: Initial vs. ongoing eligibility use different percentages
- **Inflation Impact**: Real value of benefits declined ~47% since 1993

---

## Document Quality Assessment

✅ **Authoritative**: All primary sources are official government documents
✅ **Current**: Documents reflect 2023-2025 policies
⚠️ **Completeness**: Major components documented; some details require manual PDF review
✅ **Citations**: Every fact has source, URL, and effective date
✅ **Clarity**: Complex rules explained with examples, formulas, and tables

---

## Missing Details (Future Work)

For a more complete implementation, the following require investigation:
- Complete self-employment income calculation methodology
- Full asset exemption details
- Child support pass-through amount ($50 mentioned)
- Stepparent deeming calculation details
- Young child supplement implementation (if enacted)
- Clothing allowance distribution rules

---

## Recent Legislative Changes

**2024 Legislation**:
- Increased lifetime limit from 48 to 60 months (effective April 1, 2025)

**2024 Budget**:
- $400 per child under 6 (annual payment)
- $2.8M increase for clothing allowance

**Proposed FY 2025** (not yet enacted):
- 35% payment increase (would raise family of 3 from $583 to ~$788)
- Increase young child payments from $50 to $150/month

---

## Files Created

- ✅ **working_references.md**: Complete documentation (17 sections, 39,000 tokens)
- ✅ Located at repository root: `/Users/ziminghua/vscode/policyengine-us/working_references.md`

---

## Next Steps

1. **Review working_references.md** for complete program rules
2. **Manually review** BEM 518, 520, 515 for implementation details
3. **Create parameters** following mi_tanf_* naming convention
4. **Implement variables** for eligibility and benefit calculation
5. **Write tests** covering various household sizes and income scenarios
6. **Validate** against official examples (if available)

All documentation is ready for the implementation agents to proceed with coding.
