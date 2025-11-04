from policyengine_us.model_api import *


class pa_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF"
    documentation = "Pennsylvania Temporary Assistance for Needy Families (TANF) cash assistance benefit amount, calculated as the Family Size Allowance minus countable income."
    unit = USD
    definition_period = MONTH
    defined_for = "pa_tanf_eligible"
    reference = "55 Pa. Code Chapters 175, 183"

    def formula(spm_unit, period, parameters):
        # Get maximum benefit (annual)
        maximum_benefit = spm_unit("pa_tanf_maximum_benefit", period)

        # Get countable income (annual)
        countable_income = spm_unit("pa_tanf_countable_income", period)

        # Benefit = Maximum benefit - countable income (cannot be negative)
        return max_(maximum_benefit - countable_income, 0)
