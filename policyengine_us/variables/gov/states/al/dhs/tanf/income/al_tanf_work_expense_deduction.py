from policyengine_us.model_api import *


class al_tanf_work_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama TANF work expense deduction"
    definition_period = MONTH
    reference = "https://dhr.alabama.gov/wp-content/uploads/2022/04/Appendix-N-Sec-2-Public-Assistance-Payment-Manual.pdf#page=30"
    defined_for = StateCode.AL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhs.tanf.income

        # Get total employment income
        employment_income = add(spm_unit, period, ["employment_income"])

        # Get self-employment income after operating expense deduction
        self_employment_income = add(
            spm_unit, period, ["self_employment_income"]
        )
        self_emp_deduction = (
            self_employment_income * p.self_employment_deduction_rate
        )
        net_self_employment = max_(
            self_employment_income - self_emp_deduction, 0
        )

        # Apply work expense rate to total earned income
        total_earned = employment_income + net_self_employment
        return total_earned * p.work_expense_rate
