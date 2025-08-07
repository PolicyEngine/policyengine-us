# GOV › IRS › DEDUCTIONS › ITEMIZED › SALT_AND_REAL_ESTATE › PHASE_OUT Parameters

This section contains 5 parameters.

## Categories

- [FLOOR](floor/index.md) (2 parameters)

## Parameters

### `in_effect`
*SALT deduction phase out in effect*

The SALT deduction is phased out based on adjusted gross income, if this is true.

**Unit: bool | Period: year**

Current value (2030-01-01): **False**


### `rate`
*SALT deduction phase out rate*

The IRS phases out the SALT deduction at this rate of adjusted gross income over the phase-out threshold.

**Unit: /1 | Period: year**

Current value (2025-01-01): **0.3**


### `threshold`
*SALT deduction phase out threshold*

The IRS phases out the SALT deduction out for filers with adjusted gross income above this amount, based on filing status.

**Unit: currency-USD | Period: year**

