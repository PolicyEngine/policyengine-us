from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class de_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Delaware LIHEAP annual income limit"
    defined_for = StateCode.DE
    reference = "https://liheapch.acf.gov/docs/2026/benefits-matricies/CO_BenefitMatrix_Heating_2026.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.de.dhss.liheap.eligibility
        federal = parameters(period).gov.hhs.smi
        size = spm_unit("de_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        # Rounding the four-person limit first and then truncating the adjusted
        # limit reproduces all 12 FY2026 amounts. This order is inferred from
        # the published table, not an express legal rounding instruction.
        base = np.round(federal.amount[state] * p.smi_rate)
        size_share = smi(size, state, period, parameters) / federal.amount[state]
        return where(size > 0, np.floor(base * size_share), 0)
