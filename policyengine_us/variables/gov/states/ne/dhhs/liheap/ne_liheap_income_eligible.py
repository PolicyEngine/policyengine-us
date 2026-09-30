from policyengine_us.model_api import *


class ne_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Nebraska LIHEAP income eligibility"
    defined_for = StateCode.NE
    reference = "https://dhhs.ne.gov/Documents/Low%20Income%20Home%20Energy%20Assistance%20Program%20%28LIHEAP%29%20Guidance%20Document%202026.pdf#page=1"

    def formula_2026(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.liheap
        income = spm_unit("ne_liheap_gross_income", period)
        fpg = spm_unit("ne_liheap_fpg", period)
        return (fpg > 0) & (income <= fpg * p.income_limit)
