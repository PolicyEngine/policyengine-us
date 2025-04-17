from policyengine_us.model_api import *


class ma_liheap_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Massachusetts LIHEAP"
    definition_period = YEAR
    reference = (
        "https://www.mass.gov/info-details/learn-about-home-energy-assistance-heap "
        "https://liheapch.acf.hhs.gov/tables/FY2015/subsidize.htm#MA"
    )
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["irs_gross_income"])
        threshold = spm_unit("ma_liheap_income_threshold", period)
        housing_assistance = spm_unit("housing_assistance", period)
        heat_in_rent = spm_unit("heat_in_rent", period)

        is_subsidized = housing_assistance >= 0.3 * income
        pays_own_heat = ~heat_in_rent

        # Eligible if under income threshold AND:
        # - Not subsidized OR
        # - Subsidized but pays own heat
        return (income <= threshold) & (
            (~is_subsidized) | (is_subsidized & pays_own_heat)
        )