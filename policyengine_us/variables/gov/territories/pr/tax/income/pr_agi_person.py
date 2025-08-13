from policyengine_us.model_api import *


class pr_agi_person(Variable):
    value_type = float
    entity = Person
    label = "Puerto Rico adjusted gross income person level"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=2"

    def formula(person, period, parameters):
        total_income = person("pr_gross_income_person", period)
        alimony_paid = person("alimony_expense", period)
        return max_(0, total_income - alimony_paid)
