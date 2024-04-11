from policyengine_us.model_api import *

class al_tanf_applicable_income(Variable):
    value_type = float
    entity = Person
    label = "AL TANF Gross Earned Income"
    defined_for = StateCode.AL
    definition_period = MONTHS_IN_YEAR

    def formula(person, period, parameters):
         # Sum of earned income
        total_earned_income = person('al_tanf_earned_income', period)
         # Application deductions
        p = parameters(period).dhs.income.earned.values.deductions.deduction_percentage
        applicable_earned_income = total_earned_income * (1 - p)
        # Sum of unearned income
        total_unearned_income = person('al_tanf_unearned_income', period)
        # Total applicable income
        total_applicable_income = applicable_earned_income + total_unearned_income

        return total_applicable_income