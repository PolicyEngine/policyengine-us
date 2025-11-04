# Ohio TANF (Ohio Works First) - Documentation Summary

## Documentation Collection Complete

I have completed gathering official Ohio TANF documentation for implementation in PolicyEngine US. All documentation has been saved to `working_references.md` in the repository root.

## Key Findings

### Program Overview
- **Program Name**: Ohio Works First (OWF)
- **Legal Authority**: Ohio Revised Code Chapter 5107, Ohio Administrative Code Title 5101:1
- **Administering Agency**: Ohio Department of Job and Family Services (ODJFS)

### Core Program Rules

#### Eligibility Requirements
- **Household Composition**: Must include minor child with parent/specified relative, OR pregnant woman (6+ months)
- **Income Limit**: 50% of Federal Poverty Guidelines (July 1, 1997) for initial eligibility
- **Resource Limit**: NONE - vehicles and home ownership not counted
- **No Strike Rule**: No household member may be involved in a strike

#### Benefit Calculation
- **Formula**: Payment Standard - Countable Income = Benefit Amount
- **Payment Standard** (Nov 2024): $623/month for family of 3
- **Earned Income Disregard**: $250 + 50% of remainder
- **Minimum Benefit**: $10/month

#### Income Rules
- **Initial Eligibility**: Gross income ≤ 50% of 1997 FPL
- **Ongoing Eligibility**: Countable income < Payment Standard
- **Earned Income**: Includes wages, self-employment (gross - 50%)
- **Unearned Income**: Includes pensions, unemployment, Social Security, child support
- **Exclusions**: SSI, foster care payments, EITC, SNAP-excluded income, student earnings

#### Time Limits
- **State Limit**: 36 months maximum
- **Federal Lifetime Limit**: 60 months total (including reapplication)
- **Reapplication**: After 24-month break with good cause, up to 24 additional months
- **Hardship Exemptions**: Counties may exempt up to 20% of caseload

#### Work Requirements
- **Single Parent**: 30 hours/week
- **Two Parents (no child care)**: 35 hours/week combined
- **Two Parents (with child care)**: 55 hours/week combined
- **Single Parent (child under 6)**: 20 hours/week

#### Sanctions (Three-Tier System)
- **1st Violation**: 1 month benefit loss
- **2nd Violation**: 3 months benefit loss
- **3rd+ Violation**: 6 months benefit loss + Medicaid loss

### Authoritative Sources Documented

#### Statutes (Ohio Revised Code)
- ✅ ORC 5107.10 - Eligibility Determination
- ✅ ORC 5107.18 - Time Limits

#### Regulations (Ohio Administrative Code)
- ✅ OAC 5101:1-1-01 - TANF Definitions
- ✅ OAC 5101:1-23-10 - Assistance Group Determination
- ✅ OAC 5101:1-23-20 - Income and Eligibility
- ✅ OAC 5101:1-23-20.1 - Income Exclusions
- ✅ OAC 5101:1-23-20.2 - Allocation of Income
- ✅ OAC 5101:1-23-40 - Payments
- ✅ OAC 5101:1-3-12 - Work Activities
- ✅ OAC 5101:1-3-15 - Three-Tier Sanctions
- ✅ OAC 5101:1-3-10 - Child Support Requirement

#### Program Parameters (November 2024)
- ✅ Payment standards (partial - family of 3: $623)
- ✅ Income limits (family of 3: $1,076 gross monthly)
- ✅ Resource limits (none)
- ✅ Work hour requirements
- ✅ Time limits and exemptions

### 📄 PDFs Requiring Extraction

The following PDFs need to be downloaded and manually extracted:

1. **Ohio TANF State Plan 2024** (HIGH PRIORITY)
   - URL: https://dam.assets.ohio.gov/image/upload/jfs.ohio.gov/OWF/tanf/2024%20TANF%20State%20Plan%20Combined.pdf
   - Needed for: Comprehensive state policies and procedures

2. **NCCP TANF Profile for Ohio** (MEDIUM PRIORITY)
   - URL: https://www.nccp.org/wp-content/uploads/2024/11/TANF-profile-Ohio.pdf
   - Needed for: Payment standards verification and program statistics

3. **Ohio Legal Aid OWF Guide** (MEDIUM PRIORITY)
   - URL: https://www.lascinti.org/wp-content/uploads/BI-04-Ohio-Works-First-OWF-Cash-Assistance.pdf
   - Needed for: Real-world examples and practical guidance

4. **Ohio Public Program Eligibility Guide 2024** (LOW PRIORITY)
   - URL: https://uhcanohio.org/wp-content/uploads/2024/09/AOFEligibilityInfographic2024.pdf
   - Needed for: Quick reference and verification

## Additional Research Needed

### High Priority
1. **Complete Payment Standards Table**: Need all family sizes (1-10+)
   - Source: ODJFS Cash Assistance Manual (currently down for maintenance)
   - URL: http://emanuals.jfs.ohio.gov/CashFoodAssist/CAM/ACT/

2. **Federal Poverty Guidelines (July 1, 1997)**: Required for initial eligibility test
   - Need complete table for all family sizes
   - This is a static historical value referenced in statute

### Medium Priority
3. **COLA History**: Annual adjustments to payment standards
4. **Self-Sufficiency Contract Template**: Standard form and requirements

### Low Priority
5. **County-Level Variations**: Determine if discretion exists in implementation
6. **Support Services**: Additional benefits beyond cash assistance

## Implementation Recommendations

### For Simplified TANF Implementation

**Priority 1 - Core Eligibility & Benefits**:
- ✅ Household composition rules (documented)
- ✅ Income eligibility test (documented)
- ✅ Earned income disregard (documented)
- ✅ Benefit calculation formula (documented)
- ⚠️ Payment standards table (partial - needs completion)

**Priority 2 - Income Calculation**:
- ✅ Earned vs. unearned income definitions (documented)
- ✅ Income exclusions (documented)
- ✅ Income allocation rules (documented)
- ✅ Conversion factors for periodic income (documented)

**Not Needed for Simplified Implementation**:
- ❌ Time limit tracking (requires longitudinal data)
- ❌ Work requirement compliance (requires case management data)
- ❌ Sanction modeling (requires violation history)
- ❌ Child support cooperation (assume compliance)

### Key Variables to Implement

```python
# Eligibility
oh_owf_eligible
oh_owf_categorically_eligible
oh_owf_income_eligible

# Income
oh_owf_gross_earned_income
oh_owf_gross_unearned_income
oh_owf_allocated_income
oh_owf_earned_income_disregard
oh_owf_countable_income

# Benefits
oh_owf_payment_standard  # By family size
oh_owf_benefit_amount
```

### Parameters to Create

```yaml
# gov/states/oh/odjfs/tanf/payment_standard.yaml
# gov/states/oh/odjfs/tanf/income_eligibility_threshold.yaml (1997 FPL)
# gov/states/oh/odjfs/tanf/earned_income_disregard.yaml
```

## Testing Recommendations

Create test cases for:
1. Single parent with 2 children (most common case)
2. Two-parent household
3. Pregnant woman with no children
4. Family with only earned income
5. Family with only unearned income
6. Family with mixed income sources
7. Family at income threshold boundaries
8. Specified relative caretaker

## Documentation Quality

✅ **Authoritative**: All sources are official Ohio government documents (ORC, OAC, ODJFS)
✅ **Current**: Rules reflect 2024 effective dates
✅ **Complete**: All major program components documented for simplified implementation
✅ **Cited**: Every fact has specific citation with URL
✅ **Structured**: Information organized logically by topic
⚠️ **Partial Data**: Payment standards table incomplete (only family of 3 confirmed)

## Next Steps

1. **User Action Required**: Extract the 4 PDFs listed above (especially TANF State Plan)
2. **Research**: Obtain complete payment standards table from ODJFS
3. **Research**: Find 1997 Federal Poverty Guidelines for all family sizes
4. **Implementation**: Begin creating Python variables for eligibility and benefit calculation
5. **Testing**: Create comprehensive YAML test suite

## Files Created

- `/Users/ziminghua/vscode/policyengine-us/working_references.md` (43KB, comprehensive documentation)
- `/Users/ziminghua/vscode/policyengine-us/github_issue_6774_summary.md` (this file)

---

**Document Collector Agent**: Task Complete ✅
**Date**: November 4, 2025
**Total Sources Documented**: 15+ official sources (statutes, regulations, agency websites)
**Ready for Implementation**: Yes (with noted data gaps)
