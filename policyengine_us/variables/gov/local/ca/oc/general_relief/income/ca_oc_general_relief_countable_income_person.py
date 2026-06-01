from policyengine_us.model_api import *


class ca_oc_general_relief_countable_income_person(Variable):
    value_type = float
    entity = Person
    label = "Orange County General Relief countable income per person"
    unit = USD
    definition_period = MONTH
    defined_for = "in_oc"
    reference = (
        "https://www.ssa.ocgov.com/sites/ssa/files/2025-03/Income.pdf#page=04",
        "https://www.ssa.ocgov.com/sites/ssa/files/2025-03/Income.pdf#page=05",
    )

    def formula(person, period, parameters):
        countable_income = add(
            person,
            period,
            [
                "ca_oc_general_relief_countable_earned_income",
                "ca_oc_general_relief_gross_unearned_income",
            ],
        )
        deductions = add(
            person,
            period,
            [
                "health_insurance_premiums",
                "child_support_expense",
            ],
        )
        receives_other_cash_assistance = person(
            "ca_oc_general_relief_receives_other_cash_assistance",
            period,
        )
        return where(
            receives_other_cash_assistance,
            0,
            max_(countable_income - deductions, 0),
        )
