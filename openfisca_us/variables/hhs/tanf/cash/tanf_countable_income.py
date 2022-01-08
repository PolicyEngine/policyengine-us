from openfisca_us.model_api import *


class tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF countable income"
    documentation = "Countable income for calculating Temporary Assistance for Needy Families benefit."
    unit = USD

    def formula(spm_unit, period, parameters):
        tanf_gross_income = spm_unit("tanf_total_gross_income", period)
        state = spm_unit.household("state_code_str", period)
        earned_income_deduction = parameters(
            period
        ).hhs.tanf.earned_income_deduction
        return tanf_gross_income * (1 - earned_income_deduction[state])
