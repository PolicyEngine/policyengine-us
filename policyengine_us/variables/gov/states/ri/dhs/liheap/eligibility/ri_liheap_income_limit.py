from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit


class ri_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Rhode Island LIHEAP annual income limit"
    defined_for = StateCode.RI
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/RI_Plan_2026.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf",
        # DHS FFY2027 income eligibility sheet.
        "https://dhs.ri.gov/media/12266/download?language=en",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.liheap.eligibility
        size = spm_unit("ri_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        # The HHS floor order reproduces all 14 FY2026 and FY2027 rows.
        limit = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        return where(size > 0, limit, 0)
