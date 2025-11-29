from policyengine_us.model_api import *


class pa_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF income eligibility"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html"

    def formula(spm_unit, period, parameters):
        # Get countable income (monthly)
        countable_income = spm_unit("pa_tanf_countable_income", period)

        # Get maximum benefit (monthly)
        maximum_benefit = spm_unit("pa_tanf_maximum_benefit", period)

        # Eligible if countable income is less than the benefit standard
        return countable_income < maximum_benefit
