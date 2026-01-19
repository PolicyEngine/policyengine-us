# Rhode Island Governor Dan McKee's 2027 Tax Proposals - Working References

## Official Program Names and Variable Prefixes

| Proposal | Official Name | Legal Citation | Variable Prefix |
|----------|--------------|----------------|-----------------|
| Child Tax Credit | Rhode Island Child Tax Credit | R.I. Gen. Laws § 44-30-104 | `ri_ctc_` |
| Social Security Exemption | Social Security Modification | R.I. Gen. Laws § 44-30-12(c)(8) | `ri_social_security_` |
| Tax Brackets | Personal Income Tax Rates | R.I. Gen. Laws § 44-30-2.6(c)(3)(A) | `ri_income_tax_` |
| Pension Exemption | Retirement Income Subtraction | R.I. Gen. Laws § 44-30-12(c)(9) | `ri_retirement_income_` |

---

## Proposal 1: Rhode Island Child Tax Credit (§44-30-104)

### Effective Date
Tax years beginning on or after January 1, 2027

### Definitions
- **Child**: Individual age 18 or under as of December 31 of tax year
- **Eligible taxpayer**: Natural person domiciled in RI who filed RI personal income tax return

### Credit Amount
- **$320 per claimed child** where exemption amount is zero under §44-30-2.6(c)(3)(C)(II)(2)

### Phaseout Structure (STEPPED - NOT LINEAR)
- **Threshold**: $261,000 modified AGI (per §44-30-12)
- **Reduction**: 20 percentage points per $7,450 (or fraction thereof) over threshold
- **Complete phaseout**: At $261,000 + (5 × $7,450) = $298,250

**Step Calculation:**
| AGI Range | Applicable Percentage | Credit Remaining |
|-----------|----------------------|------------------|
| $0 - $261,000 | 100% | $320 |
| $261,001 - $268,450 | 80% | $256 |
| $268,451 - $275,900 | 60% | $192 |
| $275,901 - $283,350 | 40% | $128 |
| $283,351 - $290,800 | 20% | $64 |
| $290,801+ | 0% | $0 |

### Inflation Adjustment
- Base year: 2026
- Index: CPI-U (12-month average ending August 31)
- Rounding: Down to nearest $5
- Applies to: $320 credit, $261,000 threshold, $7,450 increment

### Child Exemption Zeroing
For tax years 2027+, child dependents claimed for CTC have exemption amount set to zero.

**Source**: Pages 130-131, 148, 150 of Governor's Budget

---

## Proposal 2: Social Security Exemption Expansion (§44-30-12(c)(8))

### Phase-In Schedule

**Current Law (through 2026):**
- Age requirement: Must have attained full SS retirement age
- Income limits: $80,000 (single/HOH/MFS), $100,000 (joint/QW)

**2027:**
- Age requirement: **REMOVED**
- Income limits: $80,000 (single/HOH/MFS), $100,000 (joint/QW) - SAME

**2028:**
- Age requirement: None
- Income limits: $165,200 (single/HOH/MFS), $206,550 (joint/QW)

**2029+:**
- Age requirement: None
- Income limits: **NONE** (universal exemption)

### Inflation Adjustment
- Base year: 2000
- Rounding: $50 (or $25 for MFS)

**Source**: Pages 155-157 of Governor's Budget

---

## Proposal 3: New Top Income Tax Bracket (§44-30-2.6(c)(3)(A))

### Effective Date
Tax years beginning on or after January 1, 2027

### Individual Tax Brackets (2027+)

| RI Taxable Income | Pay | + Rate | On Amount Over |
|-------------------|-----|--------|----------------|
| $0 - $55,000 | $0 | 3.75% | $0 |
| $55,000 - $125,000 | $2,063 | 4.75% | $55,000 |
| $125,000 - $648,398 | $5,388 | 5.99% | $125,000 |
| **$648,398+** | **$36,740** | **8.99%** | **$648,398** |

### Trust/Estate Tax Brackets (2027+)

| RI Taxable Income | Pay | + Rate | On Amount Over |
|-------------------|-----|--------|----------------|
| $0 - $2,230 | $0 | 3.75% | $0 |
| $2,230 - $7,022 | $84 | 4.75% | $2,230 |
| $7,022 - $36,427 | $312 | 5.99% | $7,022 |
| **$36,427+** | **$2,073** | **8.99%** | **$36,427** |

**Source**: Pages 145-146 of Governor's Budget

---

## Proposal 4: Pension/Annuity Exemption Updates (§44-30-12(c)(9))

### Effective Date
Tax years beginning on or after January 1, 2025

### Cap Amount
- **$50,000** maximum exemption (already in effect for 2025)

### Income Thresholds (2025+)
| Filing Status | Income Limit |
|---------------|-------------|
| Single | $107,000 |
| Head of Household | $107,000 |
| Married Filing Separate | $107,000 |
| Married Filing Jointly | $133,750 |
| Qualifying Widow(er) | $133,750 |

### Inflation Adjustment
- Base year: **2025** (changed from 2000)
- Rounding: $50 (or $25 for MFS)

**Source**: Pages 157-160 of Governor's Budget

---

## Implementation Notes

### Existing Infrastructure
- CTC Reform framework exists at `reforms/states/ri/ctc/ri_ctc_reform.py`
- **REQUIRES MODIFICATION**: Current phaseout uses start/end range structure, needs stepped phaseout
- SS and pension exemptions exist with parameter-driven thresholds
- Tax rate structure exists at `parameters/gov/states/ri/tax/income/rate.yaml`

### Key Code Changes Required
1. **Tax Brackets**: Add 4th bracket to `rate.yaml` starting 2027-01-01
2. **SS Exemption**: Add age requirement toggle, update income thresholds for 2027/2028/2029
3. **Pension Exemption**: Update income thresholds and cap for 2025+
4. **CTC**: Modify reform to use stepped phaseout calculation instead of linear
5. **Child Exemption**: Add logic to zero out exemption when CTC claimed

### Files to Modify
- `policyengine_us/parameters/gov/states/ri/tax/income/rate.yaml`
- `policyengine_us/parameters/gov/states/ri/tax/income/agi/subtractions/social_security/limit/`
- `policyengine_us/parameters/gov/states/ri/tax/income/agi/subtractions/taxable_retirement_income/`
- `policyengine_us/reforms/states/ri/ctc/ri_ctc_reform.py`
- `policyengine_us/parameters/gov/contrib/states/ri/ctc/`
