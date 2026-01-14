# Collected Documentation

## Illinois I-PASS Assist Program Implementation
**Collected**: 2026-01-14
**Implementation Task**: Implement Illinois I-PASS Assist toll assistance program eligibility and benefits

---

## Official Program Name

**Federal Program**: N/A (State transportation program, not federally funded)
**State's Official Name**: I-PASS Assist
**Abbreviation**: None (commonly referred to as "I-PASS Assist")
**Administering Agency**: Illinois State Toll Highway Authority (Illinois Tollway)
**Source**: Illinois Tollway official website

**Variable Prefix**: `il_ipass_assist`

---

## Program Overview

I-PASS Assist is an equity-focused initiative launched by the Illinois Tollway in June 2021 to support underserved communities by making tollway travel more accessible and affordable. The program helps income-eligible individuals and families access I-PASS benefits with reduced financial barriers.

**Key Dates:**
- **Original Launch**: 2020 (limited scope, approximately 2,500 accounts)
- **Expanded Program Launch**: June 23, 2021
- **Current Enrollment**: Over 40,000 active accounts (as of 2024)

**Source**: [Illinois Tollway Significantly Expands I-PASS Assist Program](https://agency.illinoistollway.com/-/illinois-tollway-significantly-expands-i-pass-assist-program-1)

---

## Regulatory Authority

### Legal Framework
- **Statute**: Toll Highway Act (605 ILCS 10/)
- **Administrative Rules**: 92 Ill. Admin. Code Part 2520 (State Toll Highway Rules)
- **Program Authority**: Illinois Tollway Board of Directors resolutions

**Note**: I-PASS Assist is a Board-approved program and is NOT explicitly codified in state statute or administrative code. The program was approved through Board resolutions in April 2021 (incentive approval) and expanded through subsequent Board actions.

**Sources**:
- [Toll Highway Act (605 ILCS 10/)](https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1746&ChapterID=45)
- [92 Ill. Admin. Code Part 2520](https://www.law.cornell.edu/regulations/illinois/title-92/part-2520)

---

## Eligibility Requirements

### Income Eligibility

**Income Limit**: 250% of Federal Poverty Guidelines (FPL)

**2025 Income Thresholds (48 Contiguous States)**:

| Household Size | 100% FPL | 250% FPL (Eligibility Limit) |
|----------------|----------|------------------------------|
| 1 | $15,650 | $39,125 |
| 2 | $21,150 | $52,875 |
| 3 | $26,650 | $66,625 |
| 4 | $32,150 | $80,375 |
| 5 | $37,650 | $94,125 |
| 6 | $43,150 | $107,875 |
| 7 | $48,650 | $121,625 |
| 8 | $54,150 | $135,375 |
| Each additional | +$5,500 | +$13,750 |

**Note**: The Illinois Tollway website showed 2024 values (e.g., $36,450 for 1 person). The program uses current FPL values, so the parameter should be stored as a rate (2.50) rather than fixed dollar amounts.

**Source**: [I-PASS Assist Program - Illinois Tollway](https://agency.illinoistollway.com/assist)

### Implementation Approach for Income Eligibility
- **Value**: 250% of FPL
- **Parameter**: Store as rate (2.50), not dollar amount
- **Why**: Dollar amounts change when HHS updates FPL annually

### Categorical Eligibility

Households currently participating in Illinois Department of Human Services (IDHS) cash and food assistance programs automatically qualify.

**Qualifying Programs** (administered through IDHS):
1. **SNAP** (Supplemental Nutrition Assistance Program) - Explicitly confirmed
2. **TANF** (Temporary Assistance for Needy Families) - Included as "cash assistance"
3. **AABD** (Aid to the Aged, Blind, and Disabled) - Included as "cash assistance"

**Quote from source**: "To be eligible for enrollment in I-PASS Assist, household income must not exceed 250% of Federal Poverty Guidelines as verified by the Illinois Department of Revenue or qualified by the Illinois Department of Human Services for cash and food assistance programs."

**Sources**:
- [I-PASS Assist Program - Illinois Tollway](https://agency.illinoistollway.com/assist)
- [IDHS: I-PASS Assist](https://www.dhs.state.il.us/page.aspx?item=150431)

### Residency Requirement

**Residency**: Illinois residents only

**Quote from source**: "This program covers residents of the state of Illinois."

**Source**: [I-PASS Assist Program - Illinois Tollway](https://agency.illinoistollway.com/assist)

### Verification Process

Eligibility is verified through a secure web form in partnership with:
- **Illinois Department of Revenue** (for income verification)
- **Illinois Department of Human Services** (for categorical eligibility through SNAP/TANF/AABD)

Upon completion of the form, customers receive immediate email notification of eligibility status.

---

## Benefits Provided

### Standard I-PASS Benefits (All Customers)

1. **Toll Discount**: 50% off all Illinois Tollway tolls for passenger vehicles
   - Applies to: Cars, SUVs, Motorcycles (2-axle passenger vehicles)
   - Without I-PASS, customers pay double (Pay Online rate)

**Source**: [I-PASS Account - Illinois Tollway](https://agency.illinoistollway.com/about-ipass)

### I-PASS Assist Additional Benefits

| Benefit | Standard I-PASS | I-PASS Assist | Savings |
|---------|-----------------|---------------|---------|
| Transponder Deposit | $10 | $0 (waived) | $10 |
| Minimum Account Opening | $20 | $4 | $16 |
| Auto-Replenishment Minimum | $10 | $4 | $6 |
| Invoice Fee Dismissal | No | Yes (eligible) | Varies |
| Free Transponder Shipping | No | Yes | Varies |

**Detailed Benefits**:

1. **Waived Transponder Deposit**
   - Standard: $10 refundable deposit required
   - I-PASS Assist: No deposit required
   - **Source**: [Illinois Tollway Expands I-PASS Assist](https://agency.illinoistollway.com/-/illinois-tollway-significantly-expands-i-pass-assist-program-1)

2. **Reduced Account Opening Minimum**
   - Standard: $20 minimum prepaid tolls to open account
   - I-PASS Assist: $4 minimum prepaid tolls
   - **Source**: [I-PASS Assist Program](https://agency.illinoistollway.com/assist)

3. **Reduced Auto-Replenishment Minimum**
   - Standard: $10 minimum replenishment
   - I-PASS Assist: $4 minimum replenishment
   - **Source**: [I-PASS Assist Program](https://agency.illinoistollway.com/assist)

4. **Invoice Fee Dismissal**
   - I-PASS Assist customers may be eligible to have invoice fees dismissed once enrolled
   - Also helps avoid future fees for missed tolls
   - **Source**: [I-PASS Assist Program](https://agency.illinoistollway.com/assist)

5. **Free Transponder Shipping**
   - Upon approval, I-PASS transponder shipped free of charge
   - Customers must add funds to activate the account
   - **Source**: [I-PASS Assist Program](https://agency.illinoistollway.com/assist)

---

## Implementation Notes

### What CAN Be Simulated

**Eligibility determination:**
- Income eligibility (income <= 250% FPL)
- Categorical eligibility (SNAP, TANF, AABD participation)
- State residency requirement

**Benefits eligibility:**
- Whether household qualifies for I-PASS Assist
- Binary eligibility (eligible/not eligible)

### What CANNOT Be Simulated

**Monetary benefit calculation is limited because:**
- Toll savings depend on actual tollway usage (which varies)
- The 50% toll discount applies to ALL I-PASS customers, not just I-PASS Assist
- Invoice fee dismissal amounts vary by individual circumstances

**The primary benefit to simulate is ELIGIBILITY, not a specific dollar benefit amount.**

### Suggested Variable Structure

```
il_ipass_assist/
  eligibility/
    il_ipass_assist_income_eligible.py    # Income <= 250% FPL
    il_ipass_assist_categorically_eligible.py  # SNAP/TANF/AABD recipient
    il_ipass_assist_eligible.py           # Overall eligibility
```

### Suggested Parameters

```yaml
# parameters/gov/states/il/tollway/ipass_assist/eligibility/fpg_limit.yaml
description: Illinois limits household income to this share of federal poverty guidelines for I-PASS Assist eligibility.
values:
  2021-06-23: 2.50  # 250% FPL

metadata:
  unit: /1
  period: year
  label: Illinois I-PASS Assist income limit as share of FPL
  reference:
    - title: I-PASS Assist Program - Illinois Tollway
      href: https://agency.illinoistollway.com/assist
```

---

## Summary of Key Values for Implementation

| Parameter | Value | Type | Source |
|-----------|-------|------|--------|
| Income Limit | 250% of FPL | Rate (2.50) | Illinois Tollway |
| Categorical Eligibility | SNAP, TANF, AABD | Boolean | Illinois Tollway |
| Residency | Illinois only | Boolean | Illinois Tollway |
| Effective Date | June 23, 2021 | Date | Press Release |

---

## References for Metadata

```yaml
# For parameters:
reference:
  - title: I-PASS Assist Program - Illinois Tollway
    href: https://agency.illinoistollway.com/assist
  - title: Illinois Tollway Significantly Expands I-PASS Assist Program
    href: https://agency.illinoistollway.com/-/illinois-tollway-significantly-expands-i-pass-assist-program-1
```

```python
# For variables:
reference = (
    "https://agency.illinoistollway.com/assist",
    "https://www.dhs.state.il.us/page.aspx?item=150431",
)
```

---

## PDFs for Future Reference

The following PDFs contain additional information but could not be fully extracted:

1. **I-PASS Assist One Pager (2023)**
   - URL: https://illinoistollway.com/documents/20184/1344218/2023-011_IPASS+Assist+One+Pager.pdf
   - Expected content: Program overview, eligibility requirements, benefits summary

2. **I-PASS Assist Palm Card (2023)**
   - URL: https://illinoistollway.com/documents/20184/1344218/2023_04_I-PASS+Assist_Palm+Card.pdf
   - Expected content: Quick reference for program eligibility and application

3. **2025 HHS Poverty Guidelines**
   - URL: https://aspe.hhs.gov/sites/default/files/documents/dd73d4f00d8a819d10b2fdb70d254f7b/detailed-guidelines-2025.pdf
   - Expected content: Complete FPL tables for all household sizes and percentages

---

## Additional Sources Consulted

1. **Illinois Tollway Official Website**
   - [I-PASS Assist Program Page](https://agency.illinoistollway.com/assist)
   - [I-PASS Account Information](https://agency.illinoistollway.com/about-ipass)
   - [Toll Rates](https://agency.illinoistollway.com/toll-rates)
   - [Regulations, Rules and Policies](https://agency.illinoistollway.com/about/regulations-rules-policies)

2. **Illinois Department of Human Services**
   - [IDHS I-PASS Assist Page](https://www.dhs.state.il.us/page.aspx?item=150431)
   - [IDHS Additional Benefits](https://www.dhs.state.il.us/page.aspx?item=165001)
   - [IDHS Cash Assistance Programs](https://www.dhs.state.il.us/page.aspx?item=29719)

3. **Legal Resources**
   - [Toll Highway Act (605 ILCS 10/)](https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1746&ChapterID=45)
   - [92 Ill. Admin. Code Part 2520](https://www.law.cornell.edu/regulations/illinois/title-92/part-2520)

4. **Press Releases**
   - [Illinois Tollway Significantly Expands I-PASS Assist Program (June 2021)](https://agency.illinoistollway.com/-/illinois-tollway-significantly-expands-i-pass-assist-program-1)
   - [I-PASS Assist continues to expand relief (2023)](https://agency.illinoistollway.com/-/i-pass-assist-continues-to-expand-relief-for-working-individuals-and-families)
   - [Illinois Tollway offers more income-eligible drivers benefits (2022)](https://agency.illinoistollway.com/-/illinois-tollway-offers-more-income-eligible-drivers-cost-saving-benefits-through-i-pass-assist-program)

5. **Awards and Recognition**
   - [IBTTA 2024 President's Award - I-PASS Assist](https://www.ibtta.org/awards/i-pass-assist)

6. **Federal Poverty Guidelines**
   - [HHS ASPE Poverty Guidelines](https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines)
