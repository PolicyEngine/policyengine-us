from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit


class ga_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Georgia LIHEAP annual income limit"
    defined_for = StateCode.GA
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/GA_Plan_2026.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/GA_BenefitMatrix_Heat-Cool_2026.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.liheap.eligibility
        size = spm_unit("ga_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        # The HHS floor order reproduces all 16 published FY2026 limits.
        limit = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        return where(size > 0, limit, 0)
