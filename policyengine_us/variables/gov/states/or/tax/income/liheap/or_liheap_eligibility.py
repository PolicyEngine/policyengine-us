from policyengine_us.model_api import *


class or_liheap_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oregon LIHEAP eligibility"
    definition_period = YEAR
    reference = (
        "https://liheapch.acf.hhs.gov/Directors/Eligibility/OR_Income_def_2013.pdf"
        "https://liheapch.acf.hhs.gov/profiles/Oregon.htm"
    )

    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["irs_gross_income"])
        threshold = spm_unit("or_liheap_income_threshold", period)
        is_subsidized = spm_unit("subsidized_housing", period)
        heat_in_rent = spm_unit("heat_in_rent", period)
        pays_own_heat = ~heat_in_rent

        return (income <= threshold) & (
            (~is_subsidized) | (is_subsidized & pays_own_heat)
        )
