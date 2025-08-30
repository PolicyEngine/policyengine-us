from policyengine_us.model_api import *


class or_liheap_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Oregon LIHEAP"
    definition_period = YEAR
    reference = (
        "https://liheapch.acf.hhs.gov/Directors/Eligibility/OR_Income_def_2013.pdf"
        "https://liheapch.acf.hhs.gov/profiles/Oregon.htm"
        "https://liheapch.acf.hhs.gov/tables/FY2015/subsidize.htm#OR"
    )

    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["irs_gross_income"])
        threshold = spm_unit("or_liheap_income_threshold", period)
        heat_in_rent = spm_unit("heat_in_rent", period)
        pays_own_heat = ~heat_in_rent
        housing_assistance = spm_unit("housing_assistance", period)
        receives_housing_assistance = housing_assistance > 0

        return (income <= threshold) & (
            ~receives_housing_assistance | pays_own_heat
        )
