# Special Supplemental Nutrition Program for Women, Infants, and Children (WIC)

## Overview

WIC provides supplemental nutritious foods, nutrition education, and health care referrals to low-income pregnant women, new mothers, infants, and children up to age 5. PolicyEngine US models WIC eligibility and benefit values based on participant category.

## Program Structure

### Participant Categories

WIC serves specific populations:
- **Pregnant Women**: Through pregnancy and up to 6 weeks postpartum
- **Breastfeeding Women**: Up to infant's first birthday
- **Postpartum Women**: Up to 6 months postpartum
- **Infants**: Birth to first birthday
- **Children**: Ages 1-5

### Benefit Design

WIC provides:
- Food packages tailored to nutritional needs
- Values vary by participant category
- Not cash benefits but food instruments
- Additional services beyond food

## Modeled Variables

### Input Variables
- `age`: For participant category
- `is_pregnant`: Pregnancy status
- `is_breastfeeding`: Breastfeeding status
- `is_wic_at_nutritional_risk`: Risk determination
- Income components for eligibility

### Calculated Variables
- `wic`: Estimated monthly benefit value
- `is_wic_eligible`: Eligibility determination
- `meets_wic_categorical_eligibility`: Auto-qualified
- `meets_wic_income_test`: Under income limit
- `wic_category`: Participant category code
- `would_claim_wic`: Take-up prediction

### Eligibility Components
- `wic_category_str`: Category description
- `receives_wic`: Actual participation indicator
- Categorical eligibility through other programs

### Not Currently Modeled
- State agency priority systems
- Specific food package contents
- Vendor cost variations
- Nutrition education requirements
- Health care referral tracking

## Legislative References

**Primary Authority**: Child Nutrition Act of 1966, Section 17

**Key Regulations**: 7 CFR Part 246

**Program Administration**: USDA Food and Nutrition Service

## Eligibility Requirements

WIC eligibility requires:
- **Categorical**: Must be in eligible category
- **Income**: At or below 185% of poverty
- **Nutritional Risk**: Determined by health professional
- **Residency**: Live in state/jurisdiction

## Categorical Eligibility

Automatic income eligibility through:
- SNAP participation
- TANF participation
- Medicaid participation
- Certain state programs

## Benefit Values

PolicyEngine US uses:
- Average food package costs by category
- National average data
- Does not model state-specific variations
- Updates with USDA cost data

## Program Interactions

WIC coordinates with:
- **SNAP**: Different but complementary
- **Medicaid**: Often co-located services
- **TANF**: Automatic eligibility
- **School Meals**: Transition at age 5
- **Health Programs**: Required referrals

## Priority System

When funding is limited:
- Pregnant and breastfeeding women first
- Infants second
- Children based on nutritional risk
- Postpartum women last

## Data Considerations

The model uses:
- USDA participation data
- Average food package costs
- Income eligibility thresholds
- Take-up rates by category