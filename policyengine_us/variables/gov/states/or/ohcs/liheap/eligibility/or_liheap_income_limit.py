from policyengine_us.model_api import *


class or_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Oregon LIHEAP income limit"
    unit = USD
    defined_for = StateCode.OR
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=77"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].ohcs.liheap.eligibility
        # Ceiling reproduces all 12 published limits; the manual does not
        # prescribe a rounding rule. hhs_smi uses the requested year's SMI.
        return np.ceil(spm_unit("hhs_smi", period) * p.smi_rate)
