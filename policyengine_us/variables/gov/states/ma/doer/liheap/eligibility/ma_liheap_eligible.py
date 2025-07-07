from policyengine_us.model_api import *


class ma_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Massachusetts LIHEAP"
    definition_period = YEAR
    defined_for = "ma_liheap_income_eligible"
    reference = (
        "https://www.mass.gov/info-details/learn-about-home-energy-assistance-heap",
        "https://liheapch.acf.gov/tables/subsidize.htm#MA",
    )

    def formula(spm_unit, period, parameters):
        eligible_subsidized_housing = spm_unit(
            "ma_liheap_eligible_subsidized_housing", period
        )
        is_subsidized = spm_unit("receives_housing_assistance", period)
        return eligible_subsidized_housing | ~is_subsidized
