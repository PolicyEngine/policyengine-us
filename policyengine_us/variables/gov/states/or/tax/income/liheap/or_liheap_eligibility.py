from policyengine_us.model_api import *


class or_liheap_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oregon LIHEAP eligibility"
    definition_period = YEAR
    reference = "https://liheapch.acf.hhs.gov/profiles/Oregon.htm"
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["adjusted_gross_income"])
        threshold = spm_unit("or_liheap_income_threshold", period)
        return income <= threshold
