# Texas LIHEAP Documentation Summary for Implementation

## Documentation Collected on 2025-01-28

I have gathered comprehensive official documentation for the Texas Low Income Home Energy Assistance Program (LIHEAP), administered as the Comprehensive Energy Assistance Program (CEAP) by the Texas Department of Housing and Community Affairs (TDHCA).

## Sources Located

### Federal Framework
- **42 USC 8621**: Federal statute authorizing LIHEAP grants to states
  - URL: https://www.law.cornell.edu/uscode/text/42/8621
- **45 CFR Part 96 Subpart H**: Federal regulations governing LIHEAP
  - Key section: 45 CFR 96.85 - Income eligibility formulas
  - URL: https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-96/subpart-H

### Texas State Implementation
- **Agency**: Texas Department of Housing and Community Affairs (TDHCA)
- **Program**: Comprehensive Energy Assistance Program (CEAP)
- **Main URL**: https://www.tdhca.texas.gov/comprehensive-energy-assistance-program-ceap
- **Guidance**: https://www.tdhca.texas.gov/comprehensive-energy-assistance-program-ceap-program-guidance
- **State Plan**: 2025 LIHEAP State Plan - Revision No. 1 (approved 01-21-2025)

## Key Implementation Details

### Income Eligibility
Texas uses **150% of Federal Poverty Level** as the income eligibility threshold.

**2025 Income Limits (effective January 27, 2025):**
| Household Size | Annual Limit | Monthly Limit |
|---|---|---|
| 1 | $23,475 | $1,956 |
| 2 | $31,725 | $2,644 |
| 3 | $39,975 | $3,331 |
| 4 | $48,225 | $4,019 |
| 5 | $56,475 | $4,706 |
| 6 | $64,725 | $5,394 |
| 7 | $72,975 | $6,081 |
| 8 | $81,225 | $6,769 |
| Each additional | +$8,250 | +$688 |

### Benefit Amounts (FY 2025)
- **Regular Assistance**: $1 minimum, $12,300 maximum
  - Base benefit range: $200 - $1,000
- **Crisis Assistance**: $2,400 maximum
- **Weatherization**: $12,000 maximum

### Priority Groups
1. **Elderly** (age 60+)
2. **Disabled** individuals
3. **Households with children** age 5 and under
4. **High energy burden** households (>10% of income on energy)

### Benefit Calculation Method

The benefit calculation considers:
1. **Household income level** (as % of FPL)
2. **Household size** (using SMI adjustment percentages per 45 CFR 96.85)
3. **Energy burden** (energy costs / income)
4. **Priority group status**

**SMI Adjustments for Household Size:**
- 1 person: 52% of 4-person baseline
- 2 persons: 68%
- 3 persons: 84%
- 4 persons: 100% (baseline)
- 5 persons: 116%
- 6 persons: 132%
- Each additional: +3%

### Special Rules

#### Categorical Eligibility
Recipients of these programs may be automatically eligible:
- SNAP
- TANF
- SSI

#### Household Definition (42 USC 8622(5))
"Any individual or group of individuals who are living together as one economic unit for whom residential energy is customarily purchased in common or who make undesignated payments for energy in the form of rent"

#### Crisis Eligibility
Qualifying situations include:
- Utility disconnection notice
- Past due bills
- Broken heating/cooling equipment
- Empty fuel tank (propane/oil)
- Other documented emergencies

### Application and Payment Process
- Applications processed through local subrecipients covering all 254 Texas counties
- Benefits paid directly to utility vendors (no cash to recipients)
- Once per program year for regular assistance
- Year-round availability for crisis assistance
- No retroactive payments for bills before application date

## Documentation Files Created

Full documentation has been saved in the repository at:
- `/docs/agents/sources/texas_liheap/overview.md` - Program overview and authoritative sources
- `/docs/agents/sources/texas_liheap/eligibility.md` - Detailed eligibility requirements and documentation
- `/docs/agents/sources/texas_liheap/benefit_calculation.md` - Benefit calculation formulas and methods
- `/working_references.md` - Consolidated implementation reference (repository root)

## Implementation Notes

### Key Variables Needed
1. `tx_liheap_eligible` - Boolean for income eligibility
2. `tx_liheap_priority_group` - Categorical for priority status
3. `tx_liheap_energy_burden` - Float for energy cost percentage
4. `tx_liheap_regular_benefit` - Float for regular assistance amount
5. `tx_liheap_crisis_benefit` - Float for crisis assistance amount
6. `tx_liheap_total_benefit` - Float for combined benefits

### Key Parameters Needed
1. Income limits by household size
2. SMI adjustment percentages
3. Benefit minimums and maximums
4. Priority group definitions (age thresholds, etc.)

### Testing Considerations
- Test various household sizes (1-8+ members)
- Test priority group combinations
- Test income at various percentages of FPL
- Test crisis vs. regular assistance scenarios
- Test benefit caps and minimums

## Questions/Gaps

1. **Exact benefit formula**: While we have ranges and factors, the exact mathematical formula used by TDHCA for calculating benefits within the $200-$1,000 base range is not publicly documented. The state likely uses a proprietary matrix or tool.

2. **Cooling vs. Heating split**: The $12,300 maximum covers both, but the split between cooling and heating seasons is not specified in public documents.

3. **Vendor payment mechanics**: Implementation may need to track vendor relationships, but this is likely outside scope for PolicyEngine.

## Next Steps

This documentation provides sufficient detail to implement a reasonable approximation of Texas LIHEAP benefits in PolicyEngine. The implementation should:

1. Focus on eligibility determination (clear rules available)
2. Calculate energy burden (energy costs / income)
3. Identify priority groups (clear definitions available)
4. Estimate benefits using available ranges and factors
5. Apply appropriate caps

The implementation team can reference the detailed documentation files and use the federal regulations (45 CFR 96.85) as the authoritative source for household size adjustments and other calculation methods.