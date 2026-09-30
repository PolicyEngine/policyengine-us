from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class in_eap_smi(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Indiana EAP household-adjusted state median income"
    defined_for = StateCode.IN
    reference = "https://www.in.gov/ihcda/files/Indiana-LIHEAP-Intake-and-Operations-Program-Manual-PY2026.pdf#page=69,70,72,73"

    def formula_2026(spm_unit, period, parameters):
        size = spm_unit("in_eap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        # Truncate household-adjusted 100% SMI before applying each income-band rate.
        # This numerical pattern reproduces all 90 published monthly, quarterly and
        # annual table values; the manual does not state an explicit rounding rule.
        return where(size > 0, np.floor(smi(size, state, period, parameters)), 0)
