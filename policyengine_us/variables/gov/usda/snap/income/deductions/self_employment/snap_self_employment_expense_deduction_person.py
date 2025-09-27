from policyengine_us.model_api import *


class snap_self_employment_expense_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "SNAP self-employment expense deduction per person"
    unit = USD
    definition_period = YEAR
    reference = "https://www.snapscreener.com/blog/self-employment"

    def formula(person, period, parameters):
        self_employment_income = person("self_employment_income", period)
        expenses = person("snap_self_employment_income_expense", period)
        p = parameters(period).gov.usda.snap.income.deductions.self_employment
        state_code = person.household("state_code", period)
        income_percentage = max_(p.rate[state_code], 0)
        percentage_based_amount = income_percentage * self_employment_income
        # Take the larger of the income percentage and expenses assuming that the filer
        # will optimize for the larger deduction.
        smaller_of_income_percentage_and_expenses = max_(
            percentage_based_amount, expenses
        )
        return where(
            p.expense_based_deduction_applies[state_code],
            smaller_of_income_percentage_and_expenses,
            percentage_based_amount,
        )
