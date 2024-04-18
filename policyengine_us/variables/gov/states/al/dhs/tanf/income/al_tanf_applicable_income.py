from policyengine_us.model_api import *

class al_tanf_applicable_income(Variable):
    value_type = float
    entity = Person
    label = "Alabama TANF Gross Earned Income"
    defined_for = StateCode.AL
    definition_period = YEAR

    def formula(person, period, parameters):
        # Get the total earned income.
        total_earned_income = person("al_tanf_earned_income", period)
        # Get work expense deductions
        work_expense_deduction = person("al_tanf_work_expense_deduction", period)
        # Calculate earned income after deductions
        applicable_earned_income = max(total_earned_income - work_expense_deduction, 0)
        # Get the total unearned income.
        total_unearned_income = person("al_tanf_unearned_income", period)
        # Total applicable income is earned income after deductions plus unearned income
        return applicable_earned_income + total_unearned_income  