# Indiana TANF Documentation

This directory contains comprehensive documentation for Indiana's Temporary Assistance for Needy Families (TANF) program for implementation in PolicyEngine US.

**Documentation Date**: November 23, 2025
**Implementation Status**: Phase 1 Complete (HTML sources); PDF extraction pending

## Directory Contents

- **eligibility.md** - Complete eligibility requirements (demographic, income, resources)
- **benefit_calculation.md** - Benefit calculation methodology and payment standards
- **income.md** - Income definitions, sources, and disregards
- **resources.md** - Asset and resource limits
- **legislation.md** - Recent legislative changes (Senate Enrolled Act 265)

## Quick Reference

### Current Program Parameters (2024)

| Parameter | Value |
|-----------|-------|
| Max Benefit (Family of 3) | $513/month |
| Net Income Limit (Family of 3) | $513/month |
| Gross Income Limit (Family of 3) | $778/month |
| Resource Limit (Application) | $1,000 |
| Resource Limit (Receipt) | $10,000 |
| Vehicle Equity Exclusion | $20,000 |
| Earned Income Disregard (Benefit Calc) | 75% |
| Time Limit (Children) | 60 months |
| Time Limit (Adults) | 24 months |

### Legislative Changes

**Senate Enrolled Act 265 (2023)**
- Signed: May 22, 2023
- Effective: July 2025 (phased implementation)
- Expands eligibility from 16% FPL → 50% FPL by December 2027
- Increases benefit amounts
- Adds annual cost-of-living adjustments

### Critical PDFs Requiring Extraction

1. **SNAP/TANF Policy Manual Chapter 2800** - Income calculation details
   - URL: https://www.in.gov/fssa/dfr/files/2800.pdf

2. **SNAP/TANF Policy Manual Chapter 2400** - Nonfinancial eligibility
   - URL: https://www.in.gov/fssa/dfr/files/2400.pdf

3. **TANF State Plan Renewal (2023)**
   - URL: https://www.in.gov/fssa/dfr/files/TANF-State-Plan-Renewal-eff-Jan-1-2023.pdf
   - Key: Page 10 likely contains income calculation formulas

## Implementation Notes

### Use Federal Baseline For:
- Demographic eligibility (age thresholds)
- Immigration eligibility

### State-Specific Rules Required For:
- Income limits and calculation
- Benefit amounts
- Resource limits (two-tier system)
- Time limits (more restrictive adult limit)

### Outstanding Questions

1. **Earned Income Disregard Methodology**: Conflicting information between sources
   - Version 1: $30 and 1/3 for 4 months, then 75% ongoing
   - Version 2: $120 for 4 months, $120 for 8 months, $90 thereafter
   - **Resolution**: Need Policy Manual Chapter 2800 PDF extraction

2. **Child Support Passthrough**: No explicit passthrough found
   - State retains child support for cost recovery
   - Need State Plan PDF to confirm no passthrough/disregard

3. **SEA 265 Implementation Timeline**: Year-by-year FPL percentages 2025-2027 not found

## Primary Legal Authorities

- **Indiana Code**: IC 12-14 (TANF Statutes)
- **Administrative Code**: 470 IAC 10.3 (TANF Regulations)
- **Recent Legislation**: Senate Enrolled Act 265 (2023)
- **Policy Manual**: ICES Program Policy Manual (integrated SNAP/TANF)

## Contact Information

**Indiana Family and Social Services Administration (FSSA)**
- Division of Family Resources
- Website: https://www.in.gov/fssa/dfr/
- Phone: (800) 403-0864

## Next Steps

1. Extract and analyze critical PDF documents
2. Resolve income disregard methodology discrepancy
3. Confirm child support passthrough status
4. Obtain year-by-year SEA 265 implementation percentages
5. Create parameter files and variables
6. Write YAML tests
