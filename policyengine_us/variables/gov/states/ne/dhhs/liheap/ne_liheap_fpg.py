from policyengine_us.model_api import *


class ne_liheap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Nebraska LIHEAP annual federal poverty guideline"
    defined_for = StateCode.NE
    reference = "https://dhhs.ne.gov/Documents/Low%20Income%20Home%20Energy%20Assistance%20Program%20%28LIHEAP%29%20Guidance%20Document%202026.pdf#page=1"

    def formula_2026(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.liheap
        size = spm_unit("ne_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        # Annual 2026 represents the heating season ending in 2026. Household
        # composition is current; only the federal guideline is lagged.
        fpg_year = period.start.year - int(p.fpg_year_lag)
        fpg = parameters(f"{fpg_year}-01-01").gov.hhs.fpg
        amount = fpg.first_person[state_group] + fpg.additional_person[
            state_group
        ] * max_(size - 1, 0)
        return where(size > 0, amount, 0)
