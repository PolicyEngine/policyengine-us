from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit


class de_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Delaware LIHEAP annual income limit"
    defined_for = StateCode.DE
    reference = "https://liheapch.acf.gov/docs/2026/benefits-matricies/CO_BenefitMatrix_Heating_2026.pdf#page=1"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.de.dhss.liheap.eligibility
        size = spm_unit("de_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        limit = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        return where(size > 0, limit, 0)
