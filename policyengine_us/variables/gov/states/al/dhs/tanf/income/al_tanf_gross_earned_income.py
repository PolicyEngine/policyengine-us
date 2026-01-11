from policyengine_us.model_api import *


class al_tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama TANF gross earned income"
    definition_period = MONTH
    reference = "https://dhr.alabama.gov/wp-content/uploads/2022/04/Appendix-N-Sec-2-Public-Assistance-Payment-Manual.pdf#page=30"
    defined_for = StateCode.AL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhs.tanf.income

        # Get employment income
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

        return employment_income + net_self_employment
