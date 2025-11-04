from policyengine_us.model_api import *


class pa_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF income eligibility"
    documentation = "Pennsylvania TANF requires countable income to be less than the Family Size Allowance (FSA) for the household size."
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapter 183, working_references.md"

    def formula(spm_unit, period, parameters):
        # Get countable income (annual)
        countable_income = spm_unit("pa_tanf_countable_income", period)

        # Get maximum benefit (monthly), convert to annual
        maximum_benefit = spm_unit("pa_tanf_maximum_benefit", period)
        annual_maximum = maximum_benefit * 12

        # Eligible if countable income is less than the benefit standard
        return countable_income < annual_maximum
