# GOV › STATES › MN › TAX › INCOME › CREDITS › CDCC Parameters

This section contains 7 parameters.

## Parameters

### `child_age`
*Minnesota CDCC dependent child age*

Minnesota has a child/dependent care credit in which children under this age qualify as a dependent.

**Unit: year | Period: year**

Current value (2021-01-01): **13**


### `expense_fraction`
*Minnesota CDCC expense fraction*

Minnesota has a child/dependent care credit in which the pre-phaseout credit amount is qualified expense times this AGI-related fractional amount.

**Type: single_amount | Period: year**


### `maximum_dependents`
*Minnesota CDCC maximum number of qualified dependents*

Minnesota has a child/dependent care credit in which this is the maximum number of qualified dependents allowed.

**Unit: person | Period: year**

Current value (2021-01-01): **2**


### `maximum_expense`
*Minnesota CDCC maximum allowed care expense per qualified dependent*

Minnesota has a child/dependent care credit in which this is the maximum care expense allowed per qualified dependent.

**Unit: currency-USD | Period: year**

Current value (2021-01-01): **$3,000**


### `phaseout_rate`
*Minnesota CDCC excess AGI phaseout rate*

Minnesota has a child/dependent care credit which is phased out at this rate above a federal AGI threshold.

**Unit: /1 | Period: year**

Current value (2021-01-01): **0.05**


### `phaseout_threshold`
*Minnesota CDCC phaseout threshold*

Minnesota has a child/dependent care credit which begins to be phased out when federal AGI exceeds this threshold.

**Unit: currency-USD | Period: year**

Current value (2024-01-01): **$62,410**


### `separate_filers_excluded`
*Minnesota CDCC separate filers excluded*

Minnesota excludes separate filers from the dependent care credit if this is true.

**Unit: bool | Period: year**

Current value (2023-01-01): **False**

