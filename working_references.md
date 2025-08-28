# Collected Documentation

## Texas LIHEAP - Federal/State Implementation
**Collected**: 2025-01-28
**Implementation Task**: Implement Texas Low Income Home Energy Assistance Program (LIHEAP/CEAP)

### Source Information

#### Federal Law
- **Title**: 42 U.S. Code § 8621 - Home energy grants
- **Citation**: 42 USC 8621
- **URL**: https://www.law.cornell.edu/uscode/text/42/8621
- **Effective Date**: Current (last amended 2005)

#### Federal Regulations
- **Title**: 45 CFR Part 96 Subpart H - Low-income Home Energy Assistance Program
- **Citation**: 45 CFR 96.85 - Income eligibility
- **URL**: https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-96/subpart-H
- **Effective Date**: Current

#### State Program
- **Title**: Texas Comprehensive Energy Assistance Program (CEAP)
- **Agency**: Texas Department of Housing and Community Affairs (TDHCA)
- **URL**: https://www.tdhca.texas.gov/comprehensive-energy-assistance-program-ceap
- **State Plan**: 2025 LIHEAP State Plan - Revision No. 1 (approved 01-21-2025)
- **Effective Date**: Program Year 2025 (Income limits effective January 27, 2025)

### Key Rules and Thresholds

#### Income Eligibility (150% FPL for Texas)
- 1 person: $23,475 annual / $1,956 monthly
- 2 persons: $31,725 annual / $2,644 monthly
- 3 persons: $39,975 annual / $3,331 monthly
- 4 persons: $48,225 annual / $4,019 monthly
- 5 persons: $56,475 annual / $4,706 monthly
- 6 persons: $64,725 annual / $5,394 monthly
- 7 persons: $72,975 annual / $6,081 monthly
- 8 persons: $81,225 annual / $6,769 monthly
- Each additional: +$8,250 annual / +$688 monthly

#### State Median Income Adjustments (45 CFR 96.85)
- 1 person: 52% of 4-person SMI
- 2 persons: 68% of 4-person SMI
- 3 persons: 84% of 4-person SMI
- 4 persons: 100% of 4-person SMI
- 5 persons: 116% of 4-person SMI
- 6 persons: 132% of 4-person SMI
- Each additional: +3% per person

#### Benefit Amounts (FY 2025)
- **Regular Assistance**: $1 minimum, $12,300 maximum
- **Base Benefit Range**: $200 - $1,000
- **Crisis Assistance**: $2,400 maximum
- **Weatherization**: $12,000 maximum

### Calculation Formulas

#### Income Eligibility Test
```python
# Texas uses 150% FPL
fpl_limit = federal_poverty_level[household_size] * 1.5
eligible = household_income <= fpl_limit
```

#### Benefit Calculation (Simplified)
```python
# Step 1: Calculate energy burden
energy_burden = annual_energy_costs / annual_household_income

# Step 2: Determine priority points
priority_points = 0
if age >= 60: priority_points += 20
if disabled: priority_points += 20
if has_child_under_6: priority_points += 20
if energy_burden > 0.10: priority_points += 30
if income < (fpl * 0.75): priority_points += 30

# Step 3: Calculate base benefit
base_benefit = min(200 + (priority_points * 10), 1000)

# Step 4: Apply household size adjustment
smi_adjustment = [0.52, 0.68, 0.84, 1.00, 1.16, 1.32]  # for sizes 1-6
if household_size > 6:
    adjustment = 1.32 + (0.03 * (household_size - 6))
else:
    adjustment = smi_adjustment[household_size - 1]
    
adjusted_benefit = base_benefit * adjustment

# Step 5: Apply caps
final_benefit = min(adjusted_benefit, 12300)
```

#### Crisis Assistance Eligibility
```python
crisis_eligible = (
    has_shutoff_notice or
    past_due_amount > 0 or
    broken_equipment or
    fuel_tank_empty or
    other_emergency
)
crisis_benefit = min(amount_needed_to_resolve, 2400)
```

### Special Cases and Exceptions

#### Priority Groups
- **Elderly**: Age 60 and over - receive priority and potentially higher benefits
- **Disabled**: Documented disability - receive priority and potentially higher benefits
- **Young Children**: Households with children age 5 and under - receive priority
- **High Energy Burden**: Households spending >10% income on energy - receive priority

#### Categorical Eligibility
- SNAP recipients may be automatically eligible
- TANF recipients may be automatically eligible
- SSI recipients may be automatically eligible

#### Household Definition
- "Any individual or group of individuals living together as one economic unit for whom residential energy is customarily purchased in common" (42 USC 8622(5))
- Includes renters who pay for utilities directly or indirectly through rent

#### Benefit Limitations
- Once per program year for regular assistance
- Available year-round for crisis assistance
- No cash payments - paid directly to utility vendors
- No retroactive payments for bills before application

### References for Metadata

```yaml
# For parameters:
reference:
  - title: "42 U.S. Code § 8621 - Home energy grants"
    href: "https://www.law.cornell.edu/uscode/text/42/8621"
  - title: "45 CFR 96.85 - Income eligibility"
    href: "https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-96/subpart-H/section-96.85"
  - title: "Texas CEAP Program Guidance"
    href: "https://www.tdhca.texas.gov/comprehensive-energy-assistance-program-ceap-program-guidance"
```

```python
# For variables:
reference = "42 USC 8621, 45 CFR 96.85"
documentation = "https://www.tdhca.texas.gov/comprehensive-energy-assistance-program-ceap"
```

---