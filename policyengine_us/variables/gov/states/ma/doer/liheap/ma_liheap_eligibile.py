from policyengine_us.model_api import *


class ma_liheap_eligibile(Variable):
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
        threshold = spm_unit("ma_liheap_state_median_income_threshold", period)
        heat_in_rent = spm_unit("heat_costs_included_in_rent", period)
        is_subsidized = spm_unit(
            "ma_liheap_subsidized_housing_eligible", period
        )

        return (income <= threshold) & (
            (~is_subsidized) | (is_subsidized & ~heat_in_rent)
        )

    # If income less than threshold, is subisidized, but heat include in rent, then ineligible?
