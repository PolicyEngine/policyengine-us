# GOV › USDA › SNAP › INCOME › DEDUCTIONS Parameters

This section contains 29 parameters.

## Categories

- [EXCESS_MEDICAL_EXPENSE](excess_medical_expense/index.md) (2 parameters)
- [EXCESS_SHELTER_EXPENSE](excess_shelter_expense/index.md) (6 parameters)
- [SELF_EMPLOYMENT](self_employment/index.md) (2 parameters)
- [UTILITY](utility/index.md) (15 parameters)

## Parameters

### `allowed`
*SNAP deductions allowed*

Deductions available for SNAP calculation

**Unit: list | Period: year**

Current value (2008-01-01): **[7 items]**


### `child_support`
*SNAP child support gross income deduction*

Whether legally mandated child support payments can be deducted from gross income for SNAP.

**Unit: bool**


### `earned_income`
*SNAP earned income deduction*

Share of earned income that can be deducted from gross income for SNAP

**Unit: /1**

Current value (2005-01-01): **0.2**


### `standard`
*SNAP standard deduction*

The USDA deducts this amount from net income when computing SNAP benefits.

**Unit: currency-USD | Period: month**

