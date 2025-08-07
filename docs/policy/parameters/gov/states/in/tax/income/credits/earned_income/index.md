# GOV › STATES › IN › TAX › INCOME › CREDITS › EARNED_INCOME Parameters

This section contains 10 parameters.

## Categories

- [CHILDLESS](childless/index.md) (6 parameters)

## Parameters

### `decoupled`
*Whether IN EITC is decoupled from federal EITC*

Indiana has a state EITC that is decoupled from the federal EITC if this parameter is true.

**Unit: bool**

Current value (2023-01-01): **False**


### `investment_income_limit`
*Indiana EITC investment income limit*

Indiana makes any taxpayer with investment income that exceeds this limit EITC ineligible.

**Unit: float | Period: year**

Current value (2022-01-01): **$3,800**


### `match_rate`
*Indiana federal-EITC match rate*

Indiana matches this fraction of the federal earned income tax credit.

**Unit: /1 | Period: year**

Current value (2022-01-01): **0.1**


### `max_children`
*IN EITC maximum allowable children*

Indiana has a state EITC that recognizes at most this maximum number of eligible children.

**Unit: int**

Current value (2023-01-01): **3**

