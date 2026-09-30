from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class ms_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Mississippi LIHEAP annual income limit"
    defined_for = StateCode.MS
    reference = "https://www.sos.ms.gov/adminsearch/ACCode/00000693c.pdf#page=58"

    def formula_2026(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.mdhs.liheap
        size = spm_unit("ms_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        federal = parameters(period).gov.hhs.smi
        base = federal.amount[state]
        # The published FY2026 limits truncate the four-person 60% SMI amount
        # first, then the household-adjusted amount. This reproduces all 20 rows;
        # it is a reconciled numerical pattern, not an explicit rounding rule.
        amount = (
            smi(size, state, period, parameters)
            * np.floor(base * p.income_limit)
            / base
        )
        return where(size > 0, np.floor(amount), 0)
