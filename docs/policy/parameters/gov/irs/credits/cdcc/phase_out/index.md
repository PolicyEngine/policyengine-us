# GOV › IRS › CREDITS › CDCC › PHASE_OUT Parameters

This section contains 10 parameters.

## Categories

- [AMENDED_STRUCTURE](amended_structure/index.md) (4 parameters)

## Parameters

### `increment`
*CDCC phase-out increment*

Child and dependent care credit phase-out increment. Income after the phase-out start(s) reduce the CDCC applicable percentage by the rate for each full or partial increment.

**Unit: currency-USD**

Current value (2013-01-01): **$2,000**


### `max`
*CDCC maximum rate*

Child and dependent care credit maximum percentage rate.

**Unit: /1 | Period: year**

Current value (2026-01-01): **0.5**


### `min`
*CDCC minimum rate*

Child and dependent care credit phase-out percentage rate floor. The first phase-out does not reduce the childcare credit rate below this percentage.

**Unit: /1 | Period: year**

Current value (2026-01-01): **0.35**


### `rate`
*CDCC phase-out rate*

Child and dependent care credit phase-out percentage rate. This is the reduction to the applicable percentage for each full or partial increment beyond which AGI exceeds the phase-out start(s).

**Unit: /1**

Current value (2013-01-01): **0.01**


### `second_start`
*CDCC second phase-out start*

Child & dependent care credit second phase-out start.

**Unit: currency-USD**

Current value (2022-01-01): **$inf**


### `start`
*CDCC phase-out start*

Child & dependent care credit phase-out AGI start.

**Unit: currency-USD | Period: year**

Current value (2022-01-01): **$15,000**

