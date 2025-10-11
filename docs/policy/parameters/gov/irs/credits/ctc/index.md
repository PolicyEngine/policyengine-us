# GOV › IRS › CREDITS › CTC Parameters

This section contains 21 parameters.

## Categories

- [AMOUNT](amount/index.md) (4 parameters)
- [PHASE_OUT](phase_out/index.md) (7 parameters)
- [REFUNDABLE](refundable/index.md) (7 parameters)

## Parameters

### `adult_ssn_requirement_applies`
*Child Tax Credit adult identification requirement applies*

The IRS requires a Social Security Number for at least one of the adults in the household to qualify for the Child Tax Credit, if this is true.

**Unit: bool | Period: year**

Current value (2025-01-01): **True**


### `child_ssn_requirement_applies`
*Child Tax Credit child identification requirement applies*

The IRS requires a Social Security Number for qualifying children for the Child Tax Credit if this is true.

**Unit: bool | Period: year**

Current value (2018-01-01): **True**


### `eligible_ssn_card_type`
*Child tax credit eligible SSN card type*

The IRS limits the child tax credit to filers with one of these SSN Card types.

**Unit: list | Period: year**

Current value (2018-01-01): **[2 items]**

