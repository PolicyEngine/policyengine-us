from policyengine_us.model_api import *


class ca_oc_general_relief_countable_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Orange County General Relief countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/sites/ssa/files/2025-03/Income.pdf#page=4"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.oc.general_relief.income
        gross_earned_income = person(
            "ca_oc_general_relief_gross_earned_income",
            period,
        )
        return max_(gross_earned_income * (1 - p.earned_income_deduction_rate), 0)
