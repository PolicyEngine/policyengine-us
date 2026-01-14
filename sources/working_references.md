# Collected Documentation

## Illinois Home Weatherization Assistance Program (IHWAP) Implementation
**Collected**: 2026-01-14
**Implementation Task**: Research eligibility requirements for Illinois IHWAP

---

## Official Program Name

**Federal Program**: Weatherization Assistance Program (WAP)
**State's Official Name**: Illinois Home Weatherization Assistance Program
**Abbreviation**: IHWAP
**Source**: Illinois Department of Commerce and Economic Opportunity (DCEO), 47 Ill. Adm. Code 100

**Variable Prefix**: `il_ihwap`

---

## Program Overview

The Illinois Home Weatherization Assistance Program (IHWAP) helps low-income residents conserve fuel and reduce energy costs by making their homes more energy efficient. The program also provides health and safety upgrades.

**Administering Agency**: Illinois Department of Commerce and Economic Opportunity (DCEO), Office of Community Assistance (OCA)

**Funding Sources**:
- U.S. Department of Energy (DOE) Weatherization Assistance Program
- U.S. Department of Health and Human Services (HHS) LIHEAP Block Grant (up to 15%)
- State Supplemental Low Income Energy Assistance Fund (SLIHEAP) (up to 10%)

---

## 1. Income Eligibility Requirements

### Primary Income Test: 200% of Federal Poverty Level

Household income must be at or below **200% of the Federal Poverty Level (FPL)**.

**Source**:
- Federal: 42 U.S.C. 6862(7)
- State: 47 Ill. Adm. Code 100

**Income Limits for PY2026 (effective July 1, 2024 - June 30, 2025)**:

| Household Size | 200% FPL Annual Income Limit |
|----------------|------------------------------|
| 1 | $31,300 |
| 2 | $42,300 |
| 3 | $53,300 |
| 4 | $64,300 |
| 5 | $75,300 |
| 6 | $86,300 |
| 7 | $97,300 |
| 8 | $108,300 |

For households exceeding 8 members: Add $11,000 per additional person (at 200% FPL level).

**Source**:
- https://dceo.illinois.gov/communityservices/homeweatherization.html
- DOE WPN 25-3: https://www.energy.gov/sites/default/files/2025-04/wap-wpn-25-3_041625_0.pdf

### Alternative: 60% of State Median Income (SMI)

States may elect to use 60% of State Median Income as an alternative eligibility threshold.

For households exceeding 12 members: Add $2,307 per additional person (at 60% SMI level).

**Source**: U.S. HHS Information Memo LIHEAP-IM-2025-02

---

## 2. Who Qualifies (Dwelling Eligibility)

### Homeowners
- **Eligible**: Yes
- Material and labor are FREE to qualified homeowners
- Must provide proof of ownership (deed, tax bill, mortgage statement, or title)

### Renters
- **Eligible**: Yes, with landlord participation
- The **landlord must agree to program terms**
- A **50% landlord contribution** for weatherization work is required for rental property
- For multifamily buildings: At least **66% of units** must be occupied by income-eligible tenants (or 50% in some circumstances)

### Eligible Dwelling Types
- Single-family residences
- Multi-unit buildings
- Mobile homes
- Townhouses and condos (within association guidelines)

**Source**: https://dceo.illinois.gov/communityservices/homeweatherization.html

### Restriction
- **Cannot have received weatherization services in the last 15 years**

---

## 3. Categorical Eligibility (Automatic Qualification)

Households are **automatically eligible** (categorically eligible) if they meet ANY of the following criteria:

### A. LIHEAP Recipients
- Received LIHEAP assistance **within the last 12 months**
- Source: 42 U.S.C. 6862(7)(B)

### B. Social Security Act Title IV Recipients (TANF)
- Household member received **cash assistance under Title IV of the Social Security Act** (Temporary Assistance for Needy Families - TANF) within the past 12 months
- Source: 42 U.S.C. 6862(7)(A)

### C. Social Security Act Title XVI Recipients (SSI)
- Household member receives **Supplemental Security Income (SSI)**
- Source: 42 U.S.C. 6862(7)(A); 10 CFR 440.3

### D. Aid to Aged, Blind, and Disabled (AABD)
- Household member receives **AABD cash benefits**
- Source: Illinois DCEO program guidance

### E. HUD Means-Tested Programs (per WPN 22-5)
Enrollment in the following HUD programs confers categorical eligibility:
- Community Development Block Grant (CDBG)
- HOME Investment Partnerships Program
- Lead Hazard Control programs
- Public Housing
- HUD Housing Choice Vouchers (Section 8)
- HUD-VASH (Veterans Affairs Supportive Housing)
- Low-Income Housing Tax Credit (LIHTC) properties

**Source**: DOE Weatherization Program Notice 22-5 (December 2021)
- https://www.energy.gov/scep/wap/articles/weatherization-program-notice-22-5-expansion-client-eligibility-weatherization

### F. USDA Means-Tested Programs
Enrollment in the following USDA housing programs:
- Section 521 (Rural Rental Assistance)
- Section 502 (Direct Loan Program)
- Section 533 (Housing Preservation Grants)
- Section 504 (Home Repair Loans and Grants)

**Source**: DOE WAP Memo 99; referenced in WPN 22-5

### Note on SNAP
While SNAP (food stamps) provides categorical eligibility for LIHEAP in Illinois, the federal WAP regulations do not explicitly list SNAP as providing categorical eligibility for weatherization. However, SNAP households that meet income requirements or receive LIHEAP would still qualify.

---

## 4. Other Eligibility Criteria

### Priority for Services

Eligible applications are prioritized by (per 47 Ill. Admin. Code 100.410):
1. **Protected populations (highest priority)**:
   - Elderly persons
   - Individuals with disabilities
   - Families with children age 5 and under
2. **Financial need**:
   - Households with the lowest incomes
   - Households with the highest utility bills (energy burden)
3. **Additional priority factors**:
   - High residential energy users

**Source**: 47 Ill. Admin. Code 100.410

### Documentation Required
- Gross income for 90 days prior to application for every household member age 18+
- Most recent gas and electric bills
- Proof of ownership (for homeowners) or rental agreement (for renters)
- Benefit verification letters (if claiming categorical eligibility through SSI, TANF, etc.)

---

## 5. Benefits Provided

### Maximum Benefit Amounts (PY2026)

| Benefit Type | Maximum Amount |
|--------------|----------------|
| Energy-related weatherization and repair work | **$20,000** |
| Health and safety measures | **$4,000** |

**Note**: Earlier sources show $15,000/$3,500 limits; the PY2026 amounts ($20,000/$4,000) represent increases.

**Source**: https://dceo.illinois.gov/communityservices/homeweatherization.html

### Covered Services

**Energy Efficiency Improvements**:
- Air sealing (caulking, weatherstripping)
- Insulation (attic, walls, crawl spaces, floors)
- Storm windows and doors
- HVAC repair, tune-up, and replacement
- Water heater repair and replacement
- Lighting and appliance upgrades
- Duct sealing and insulation
- Ventilation improvements

**Health and Safety Measures**:
- Carbon monoxide detectors
- Smoke detectors
- Minor repairs necessary to protect weatherization measures
- Combustion safety testing

**Renewable Energy**:
- Installation of renewable energy systems (where cost-effective)

---

## Legal Authority

### Federal Law
- **Energy Conservation and Production Act (ECPA)**: P.L. 94-385, Title IV (42 U.S.C. 6861 et seq.)
- **42 U.S.C. 6862(7)**: Definition of "low-income" (200% of poverty level)
- **American Recovery and Reinvestment Act of 2009**: P.L. 111-5, Section 407a (raised eligibility from 150% to 200% FPL)

### Federal Regulations
- **10 CFR Part 440**: Weatherization Assistance for Low-Income Persons
- **10 CFR 440.3**: Definition of "low-income"
- **10 CFR 440.22**: Eligible dwelling units

### State Law
- **Energy Assistance Act**: 305 ILCS 20
- **Illinois Administrative Code**: 47 Ill. Adm. Code 100, Subpart C

### Federal Guidance
- **WPN 22-5**: Expansion of Client Eligibility (HUD/USDA programs)
- **WPN 25-3**: Federal Poverty Guidelines (January 2025)

---

## References for Implementation

### Parameters

```yaml
# Income eligibility threshold
reference:
  - title: 42 U.S.C. 6862(7) - Definitions
    href: https://www.law.cornell.edu/uscode/text/42/6862
  - title: Illinois DCEO Home Weatherization Program
    href: https://dceo.illinois.gov/communityservices/homeweatherization.html
```

### Variables

```python
# For eligibility variables:
reference = "https://www.law.cornell.edu/uscode/text/42/6862"

# For categorical eligibility:
reference = (
    "https://www.law.cornell.edu/uscode/text/42/6862",
    "https://www.energy.gov/scep/wap/articles/weatherization-program-notice-22-5-expansion-client-eligibility-weatherization",
)

# For benefit amounts:
reference = "https://dceo.illinois.gov/communityservices/homeweatherization.html"
```

---

## Implementation Approach

### Eligibility Variables Needed

1. **`il_ihwap_income_eligible`** - Income at or below 200% FPL
2. **`il_ihwap_categorically_eligible`** - Receives LIHEAP, SSI, TANF, AABD, or enrolled in HUD/USDA means-tested programs
3. **`il_ihwap_eligible`** - Combined eligibility (income OR categorical)
4. **`il_ihwap`** - Final benefit amount (binary: eligible or not, since it's a service program)

### Categorical Eligibility Variables to Reference

The following existing variables may be used for categorical eligibility:
- `il_liheap` or `is_liheap_eligible` (if exists)
- `ssi` (Supplemental Security Income)
- `tanf` or state TANF variable
- `receives_section_8_housing_choice_voucher` (if exists)
- `is_in_public_housing` (if exists)

### Parameters Needed

1. **`income_limit/rate.yaml`** - 2.0 (200% of FPL)
2. **`max_benefit/weatherization.yaml`** - $20,000
3. **`max_benefit/health_safety.yaml`** - $4,000

### Notes for Implementation

- [ ] Use federal poverty level (FPL) from existing parameters
- [ ] Use federal demographic eligibility (follows federal rules)
- [ ] Categorical eligibility can be modeled as boolean checks
- [ ] Benefit is not a cash payment - it's a service (may model as binary eligibility rather than dollar amount)

---

## Non-Simulatable Rules (Architecture Limitation)

### Cannot Enforce (Requires History)
- **15-year wait period**: Cannot have received weatherization services in the last 15 years
- **12-month lookback for categorical eligibility**: Requires checking if household received LIHEAP/TANF in past 12 months

### Implementation Approach
- Model as if household qualifies (current point-in-time eligibility)
- Document limitations in variable comments

---

## Sources Used

1. **Illinois DCEO Home Weatherization Program**
   - URL: https://dceo.illinois.gov/communityservices/homeweatherization.html

2. **42 U.S.C. 6862 - Definitions (Weatherization Assistance Program)**
   - URL: https://www.law.cornell.edu/uscode/text/42/6862

3. **10 CFR Part 440 - Weatherization Assistance for Low-Income Persons**
   - URL: https://www.ecfr.gov/current/title-10/chapter-II/subchapter-D/part-440

4. **DOE Weatherization Program Notice 22-5 (Client Eligibility Expansion)**
   - URL: https://www.energy.gov/scep/wap/articles/weatherization-program-notice-22-5-expansion-client-eligibility-weatherization

5. **DOE Weatherization Program Notice 25-3 (2025 Poverty Guidelines)**
   - URL: https://www.energy.gov/sites/default/files/2025-04/wap-wpn-25-3_041625_0.pdf

6. **DOE How to Apply for Weatherization Assistance**
   - URL: https://www.energy.gov/scep/wap/how-apply-weatherization-assistance

7. **Illinois Administrative Code 47 Ill. Adm. Code 100.410**
   - URL: https://www.law.cornell.edu/regulations/illinois/IL-Admin-Code-47-100-410

8. **Illinois OMB GATA - IHWAP Program**
   - URL: https://omb.illinois.gov/public/gata/csfa/Program.aspx?csfa=87

---

## PDFs for Future Reference

The following PDFs contain additional information:

1. **Illinois LIHEAP State Plan FY2026**
   - URL: https://dceo.illinois.gov/content/dam/soi/en/web/dceo/communityservices/utilitybillassistance/documents/fy26-liheap-state-plan--accepted--detailed-model-plan-liheap-10-01-2025.pdf
   - Expected content: Detailed LIHEAP and weatherization program rules for FY2026

2. **LIHEAP Flyer 2025-26**
   - URL: https://dceo.illinois.gov/content/dam/soi/en/web/dceo/communityservices/homeweatherization/communityactionagencies/documents/liheap-flyer.pdf
   - Expected content: Current income guidelines and program overview

3. **Illinois IHWAP Standards 2018**
   - URL: https://www.cedaorg.net/wp-content/uploads/2021/01/IHWAP-Standards-2018.pdf
   - Expected content: Technical weatherization standards and procedures

4. **Illinois PY20 Operations Manual**
   - URL: https://nascsp.org/wp-content/uploads/2019/09/IL_PY20-Operations-Manual.pdf
   - Expected content: Detailed program operations and eligibility procedures
