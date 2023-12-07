from policyengine_us.model_api import *


class wv_subtractions_part_two(Variable):
    value_type = float
    entity = Person
    label = "West Virginia subtractions from the adjusted gross income part two for senior citizen or disability deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV

    adds = "gov.states.wv.tax.income.subtractions.subtractions_part_two"
