from policyengine_us.model_api import *


class hi_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF benefit amount"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf#page=22",
    )
    defined_for = "hi_tanf_eligible"

    def formula(spm_unit, period, parameters):
        maximum_benefit = spm_unit("hi_tanf_maximum_benefit", period)
        countable_income = spm_unit("hi_tanf_countable_income", period)

        # Benefit = SOA - countable income, floored at 0
        return max_(maximum_benefit - countable_income, 0)
