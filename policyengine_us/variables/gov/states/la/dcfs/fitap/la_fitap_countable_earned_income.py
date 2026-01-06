from policyengine_us.model_api import *


class la_fitap_countable_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Louisiana FITAP countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://ldh.la.gov/page/fitap"
    defined_for = StateCode.LA

    def formula(person, period, parameters):
        gross_earned = person("tanf_gross_earned_income", period)
        deduction = person("la_fitap_earned_income_deduction", period)
        return max_(gross_earned - deduction, 0)
