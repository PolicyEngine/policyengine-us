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
        # Ceiling reproduces every published limit for program years 2025 to
        # 2027; the manual does not prescribe a rounding rule. The product is
        # rounded to cents in float64 first: float32 0.6 is slightly above 0.6,
        # which lifts a whole-dollar product above the integer and would add $1.
        # hhs_smi uses the requested year's SMI.
        smi = spm_unit("hhs_smi", period).astype(np.float64)
        return np.ceil(np.round(smi * p.smi_rate, 2))
