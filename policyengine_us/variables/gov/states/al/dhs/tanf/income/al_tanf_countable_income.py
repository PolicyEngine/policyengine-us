from policyengine_us.model_api import *


class al_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama TANF countable income"
    definition_period = MONTH
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/10/DHR-FAD-595-Oct.23.pdf#page=2"
    defined_for = StateCode.AL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhs.tanf
        countable_earned = spm_unit("al_tanf_countable_earned_income", period)
        unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])

        # Apply 30% disregard for childcare and care expenses
        care_expenses = add(
            spm_unit, period, ["childcare_expenses", "care_expenses"]
        )
        expense_disregard = care_expenses * p.expense_disregard_rate

        total_income = countable_earned + unearned
        return max_(total_income - expense_disregard, 0)
