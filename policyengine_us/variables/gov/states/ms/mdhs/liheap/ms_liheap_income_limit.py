from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit


class ms_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Mississippi LIHEAP annual income limit"
    defined_for = StateCode.MS
    reference = (
        # Rule 6.1 C (page 22) and the Appendix 60% State Median Income table
        # (page 58).
        "https://www.sos.ms.gov/adminsearch/ACCode/00000693c.pdf#page=58",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.mdhs.liheap
        size = spm_unit("ms_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        # The HHS floor order reproduces all 20 published FY2026 rows.
        limit = liheap_smi_limit(size, state, p.income_limit, period, parameters)
        return where(size > 0, limit, 0)
