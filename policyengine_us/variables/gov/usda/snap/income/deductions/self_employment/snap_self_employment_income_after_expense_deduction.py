from policyengine_us.model_api import *


class snap_self_employment_income_after_expense_deduction(Variable):
    value_type = float
    entity = Person
    label = "Self-employment income per person after the SNAP self-employment expense deduction"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        self_employment_income = person("self_employment_income", period)
        expense_deduction = person(
            "snap_self_employment_expense_deduction_person", period
        )
        return max_(self_employment_income - expense_deduction, 0)
