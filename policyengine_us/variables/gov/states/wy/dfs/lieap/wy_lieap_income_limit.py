from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit


class wy_lieap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Wyoming LIEAP state median income limit"
    reference = (
        "https://liheapch.acf.gov/profiles/povertytables/FY2026/wysmi.htm",
        # HHS LIHEAP IM 2025-02, Attachment 4, PDF pages 3,6.
        "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf#page=3",
        "https://dfs.wyo.gov/wp-content/uploads/2026/09/2026-0924-LIEAP-About-handout.pdf#page=1",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wy.dfs.lieap
        size = spm_unit("wy_lieap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        limit = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        return where(size > 0, limit, 0)
