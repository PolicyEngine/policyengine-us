from policyengine_us.model_api import *


class sc_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "South Carolina gross earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC

    adds = "gov.states.sc.tax.income.credits.two_wage_earner.earned_income"
