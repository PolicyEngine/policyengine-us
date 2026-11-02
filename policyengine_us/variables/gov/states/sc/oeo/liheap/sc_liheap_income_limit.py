from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit


class sc_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina LIHEAP annual income limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20LIHEAP%20State%20Plan.pdf#page=8",
        "https://oeo.sc.gov/managedsites/prd/oeo/liheap.html",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.oeo.liheap.eligibility
        size = spm_unit("sc_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        # The HHS floor order reproduces all eight OEO annual limits.
        limit = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        return where(size > 0, limit, 0)
