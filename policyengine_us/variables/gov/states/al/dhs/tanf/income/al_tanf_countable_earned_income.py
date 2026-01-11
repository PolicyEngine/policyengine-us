from policyengine_us.model_api import *


class al_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama TANF countable earned income"
    definition_period = MONTH
    reference = "https://dhr.alabama.gov/wp-content/uploads/2022/04/Appendix-N-Sec-2-Public-Assistance-Payment-Manual.pdf#page=30"
    defined_for = StateCode.AL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhs.tanf.income

        # Get employment income from federal baseline
        employment_income = add(spm_unit, period, ["employment_income"])

        # Get self-employment income and apply 40% operating expense deduction
        self_employment_income = add(
            spm_unit, period, ["self_employment_income"]
        )
        self_emp_deduction = (
            self_employment_income * p.self_employment_deduction_rate
        )
        net_self_employment = max_(
            self_employment_income - self_emp_deduction, 0
        )

        # Total gross earned before work expense deduction
        gross_earned = employment_income + net_self_employment

        # Apply work expense deduction
        work_expense = spm_unit("al_tanf_work_expense_deduction", period)

        return max_(gross_earned - work_expense, 0)
