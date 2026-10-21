from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ne_liheap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Nebraska LIHEAP annual federal poverty guideline"
    defined_for = StateCode.NE
    reference = "https://dhhs.ne.gov/Documents/Low%20Income%20Home%20Energy%20Assistance%20Program%20%28LIHEAP%29%20Guidance%20Document%202026.pdf#page=1"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.liheap
        size = spm_unit("ne_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        # The annual period represents the heating season ending in that year.
        # Household composition is current; only the federal guideline is lagged.
        amount = fpg(
            max_(size, 1), state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        return where(size > 0, amount, 0)
