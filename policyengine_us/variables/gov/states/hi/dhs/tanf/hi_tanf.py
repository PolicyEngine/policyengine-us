from policyengine_us.model_api import *


class hi_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF benefit amount"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://law.justia.com/codes/hawaii/title-20/chapter-346/section-346-53/",
        "https://humanservices.hawaii.gov/bessd/tanf/",
    )
    defined_for = "hi_tanf_eligible"

    def formula(spm_unit, period, parameters):
        maximum_benefit = spm_unit("hi_tanf_maximum_benefit", period)
        countable_income = spm_unit("hi_tanf_countable_income", period)

        # Benefit = SOA - countable income, floored at 0
        return max_(maximum_benefit - countable_income, 0)
