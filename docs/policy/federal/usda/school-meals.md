# National School Lunch and School Breakfast Programs

## Overview

The National School Lunch Program (NSLP) and School Breakfast Program (SBP) provide nutritious meals to children at participating schools. PolicyEngine US models eligibility for free and reduced-price meals and calculates the value of meal subsidies based on participation.

## Program Structure

### Benefit Categories

School meals operate with three tiers:
- **Free Meals**: For lowest income families
- **Reduced-Price Meals**: For moderate income families  
- **Paid Meals**: Full price with small federal subsidy

### Program Components

The programs include:
- Regular school year meals
- Summer meal programs
- After-school snacks
- Fresh fruit and vegetable program

## Modeled Variables

### Input Variables
- `age`: Child's age
- `is_in_k12_school`: School enrollment
- Income for eligibility determination
- Categorical eligibility indicators
- School meal participation rates

### Calculated Variables
- `free_school_meals`: Value of free meals
- `reduced_price_school_meals`: Value of reduced meals
- `school_meal_daily_subsidy`: Per-meal federal subsidy
- `school_meal_net_subsidy`: Net benefit value
- `school_meal_tier`: Eligibility tier

### Eligibility Variables
- `meets_school_meal_categorical_eligibility`: Auto-qualified
- `school_meal_countable_income`: Income for determination
- `school_meal_fpg_ratio`: Income as percent of poverty

### Not Currently Modeled
- Community Eligibility Provision (CEP)
- Summer meal programs separately
- State-specific supplements
- Meal quality standards
- Participation by meal type

## Legislative References

**Primary Authority**: 
- National School Lunch Act (1946)
- Child Nutrition Act (1966)

**Key Regulations**: 7 CFR Parts 210, 220

## Eligibility Determination

Income eligibility thresholds:
- **Free Meals**: At or below 130% of poverty
- **Reduced-Price**: Between 130% and 185% of poverty
- **Paid Meals**: Above 185% of poverty

## Categorical Eligibility

Automatic eligibility through:
- SNAP participation
- TANF participation  
- FDPIR participation
- Foster care status
- Head Start enrollment
- Homeless, migrant, runaway status

## Benefit Values

PolicyEngine US calculates:
- Federal reimbursement rates per meal
- Number of school days
- Assumed participation rates
- Net value after any fees

## Program Interactions

School meals coordinate with:
- **SNAP**: Direct certification
- **TANF**: Direct certification
- **WIC**: Transitions at age 5
- **Summer Programs**: Year-round nutrition

## Direct Certification

Process features:
- Automatic enrollment from SNAP/TANF
- No application required
- Reduces administrative burden
- Improves program access

## Special Provisions

Programs include:
- Severe need breakfast payments
- Special milk program
- Afterschool snack program
- Weekend backpack programs (local)

## Data Considerations

The model uses:
- USDA reimbursement rates
- School year calendar assumptions
- Average participation rates
- Direct certification rates by state