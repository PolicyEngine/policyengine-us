from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit


class nh_fap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "New Hampshire FAP income limit"
    # PDF pages 17,74.
    reference = "https://www.energy.nh.gov/sites/g/files/ehbemt551/files/inline-documents/sonh/fuel-assistance-program-procedures-manual.pdf#page=17"
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nh.doe.fap
        size = spm_unit("nh_fap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        # The HHS floor order reproduces all eight PY2027 published amounts.
        # Federal size extensions are retained; NH rounding above eight is
        # unverified.
        limit = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        # A household with no qualified member is ineligible.
        return where(size > 0, limit, 0)
