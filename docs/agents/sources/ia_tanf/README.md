# Iowa TANF (FIP - Family Investment Program) Documentation

This folder contains authoritative documentation for implementing Iowa's Family Investment Program (FIP), which is Iowa's implementation of the federal Temporary Assistance for Needy Families (TANF) program.

## Contents

- `eligibility.md` - Eligibility requirements including citizenship, residency, household composition, resource limits, time limits, and work requirements
- `benefit_calculation.md` - Income tests, deductions, payment standards, and benefit calculation formulas
- `sources.md` - Complete list of authoritative sources with URLs and citations

## Quick Reference

### Program Name
- **Official Name**: Family Investment Program (FIP)
- **Federal Program**: Temporary Assistance for Needy Families (TANF)

### Legal Authority
- Iowa Code Chapter 239B
- Iowa Administrative Code 441, Chapters 41 and 93

### Key Parameters (Effective 7/1/2025)

| Parameter | Value |
|-----------|-------|
| Gross Income Limit | 185% of Standard of Need |
| Earned Income Deduction | 20% |
| Work Incentive Disregard | 58% |
| Resource Limit (Applicant) | $2,000 |
| Resource Limit (Recipient) | $5,000 |
| Time Limit | 60 months lifetime |

### Payment Standards (Family of 3)

| Standard | Amount |
|----------|--------|
| Standard of Need | $849/month |
| 185% Gross Limit | $1,570.65/month |
| Payment Standard | $426/month |

## Implementation Checklist

- [ ] Create parameter files for income standards
- [ ] Create parameter files for payment standards
- [ ] Implement gross income eligibility test
- [ ] Implement net income eligibility test (applicants)
- [ ] Implement payment standard test
- [ ] Implement 20% earned income deduction
- [ ] Implement 58% work incentive disregard
- [ ] Implement benefit calculation
- [ ] Create unit tests for each component
- [ ] Create integration tests

## Related Documentation

- See `working_references.md` in the repository root for a consolidated implementation summary
- See existing state TANF implementations (CO, CA, NY, NC) for code patterns
