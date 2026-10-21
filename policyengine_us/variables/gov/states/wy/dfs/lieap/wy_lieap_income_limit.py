from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class wy_lieap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Wyoming LIEAP state median income limit"
    reference = (
        "https://liheapch.acf.gov/profiles/povertytables/FY2026/wysmi.htm",
        "https://dfs.wyo.gov/wp-content/uploads/2026/09/2026-0924-LIEAP-About-handout.pdf#page=1",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wy.dfs.lieap
        size = spm_unit("wy_lieap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        # Flooring the existing federal SMI calculation reproduces the
        # FY2026 and FY2027 published annual ceilings. The rounding method
        # is a numerical inference, not an explicit state instruction.
        limit = np.floor(smi(size, state, period, parameters) * p.smi_rate)
        return where(size > 0, limit, 0)
