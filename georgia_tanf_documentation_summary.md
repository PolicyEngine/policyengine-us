# Georgia TANF Documentation Summary - Phase 3A Complete

## Overview
Comprehensive documentation for Georgia TANF implementation has been gathered and compiled. All sources are official government documents from Georgia DFCS and state statutes.

## Key Findings

### Program Parameters (Effective March 2025)

**Financial Standards:**
- Maximum benefit (family of 3): **$280/month** (unchanged since 1990)
- Gross income limit (family of 3): **$784/month**
- Resource limit: **$1,000**
- Vehicle value limit: **$4,650**

**Time Limits & Work Requirements:**
- Lifetime limit: **48 months**
- Work requirement: **30 hours/week** (20 hours if child under 6)

**Earned Income Deductions:**
- Standard work expense: **$90/month**
- $30 + 1/3 disregard for first **4 months**
- $30 disregard for months **5-12**
- Dependent care: **$200/month** (child under 2), **$175/month** (child 2+)

### Complete Tables from PAMMS Appendix A

**Gross Income Ceiling by AU Size:**
| AU Size | GIC |
|---------|-----|
| 1 | $435 |
| 2 | $599 |
| 3 | $784 |
| 4 | $1,088 |
| 5 | $1,384 |
| 6+ | $1,487 + $44 per additional member |

**Standard of Need by AU Size:**
| AU Size | SON |
|---------|-----|
| 1 | $235 |
| 2 | $324 |
| 3 | $424 |
| 4 | $529 |
| 5 | $639 |
| 6+ | $749 + $24 per additional member |

**Family Maximum (Benefit Amount) by AU Size:**
| AU Size | Max Benefit |
|---------|-------------|
| 1 | $155 |
| 2 | $188 |
| 3 | $280 |
| 4 | $364 |
| 5 | $447 |
| 6+ | $530 + $17 per additional member |

## Legal Authority

### State Law
- **O.C.G.A. § 49-4-182:** Creates Georgia TANF program
- **O.C.G.A. § 49-4-186:** Family cap provision
- **Ga. Comp. R. & Regs. R. 290-2-28:** Complete TANF regulations

### Policy Manual
- **PAMMS (Policy and Manual Management System):** https://pamms.dhs.ga.gov/dfcs/tanf/
- **Last Updated:** Manual Transmittal 79 (March 2025)

## Benefit Calculation Formula

```
1. Calculate Countable Earned Income:
   Countable Earned = Gross Earned - $90 - Disregard - Dependent Care

   Where Disregard =
   - Months 1-4: $30 + (1/3 × [Gross - $90])
   - Months 5-12: $30
   - Months 13+: $0

2. Add Unearned Income:
   Total Countable = Countable Earned + Unearned

3. Gross Income Test:
   IF Total Countable > GIC[AU_Size] THEN Ineligible

4. Net Income Test:
   IF Total Countable >= SON[AU_Size] THEN Ineligible

5. Benefit Calculation:
   Benefit = MIN(SON[AU_Size] - Total Countable, Family_Max[AU_Size])
```

## Documentation Completeness

### ✅ Obtained
- [x] Complete income limit tables by family size
- [x] Complete benefit payment schedules by family size
- [x] Standard of Need values by family size
- [x] Resource limits (assets and vehicle)
- [x] Earned income deduction structure
- [x] Dependent care expense deductions
- [x] Work requirement details
- [x] Lifetime limit information
- [x] State statute citations (O.C.G.A.)
- [x] State regulation citations (290-2-28)
- [x] Policy manual structure (PAMMS)
- [x] Non-financial eligibility requirements

### ⚠️ Partially Obtained
- [~] Complete PAMMS Section 1615 text (referenced but PDF not fully extractable)
- [~] Georgia TANF State Plan full text (PDF access limited)
- [~] Official benefit calculation examples

### ❓ Open Questions
1. **Simplified disregard:** Multiple sources cite "$250/month" disregard but regulations show complex structure. Need clarification.
2. **Income ceiling formula:** PAMMS shows GIC = 185% of SON, but some values don't match exactly. Rounding rules?
3. **Historical values:** When did current benefit levels become effective?

## Authoritative Sources

### Primary Sources (Official)
1. **Georgia DFCS PAMMS** - https://pamms.dhs.ga.gov/dfcs/tanf/
2. **Georgia Statutes** - O.C.G.A. Title 49, Chapter 4, Article 9
3. **Georgia Regulations** - Ga. Comp. R. & Regs. R. 290-2-28
4. **Georgia DFCS Website** - https://dfcs.georgia.gov/tanf
5. **Georgia TANF State Plan** - https://dfcs.georgia.gov/document/document/georgia-tanf-state-plan-renewal-fy2023/download

### Secondary Sources (Verification)
1. **Georgia Budget and Policy Institute** - Policy analysis and historical context
2. **National Center for Children in Poverty** - 50-state comparison data
3. **Georgia Legal Aid** - Consumer-oriented program guide

## Files Created

1. **`/Users/ziminghua/vscode/policyengine-us/working_references.md`**
   - Comprehensive 14-section reference document
   - All sources with URLs and citations
   - Complete parameter tables
   - Benefit calculation methodology
   - Implementation notes

## Implementation Readiness

**Ready for Implementation:**
- ✅ Income eligibility determination
- ✅ Basic benefit calculation
- ✅ Resource tests
- ✅ Earned income deductions
- ✅ Dependent care deductions

**Requires Further Research:**
- Two-parent family special rules
- Hardship extension criteria
- Sanction calculation details
- Minor parent budgeting
- P-TANF (Grandparents) variations

## Recommended Next Steps

1. **Review working_references.md** for completeness
2. **Clarify open questions** with DFCS or through deeper policy manual review
3. **Proceed to Phase 3B** - Parameter extraction and structuring
4. **Create YAML parameter files** matching PolicyEngine structure
5. **Develop calculation logic** based on documented formulas

## Contact for Questions
- **Georgia DFCS:** (877) 423-4746
- **PAMMS System:** https://pamms.dhs.ga.gov/

---

**Phase Status:** ✅ Phase 3A Complete - Document Gathering
**Next Phase:** Phase 3B - Parameter Extraction and Structuring
**Date Completed:** November 5, 2025
