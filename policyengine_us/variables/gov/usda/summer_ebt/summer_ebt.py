from policyengine_us.model_api import *


class summer_ebt(Variable):
    value_type = float
    entity = Person
    label = "Summer EBT"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1762#b_2"
    defined_for = "is_summer_ebt_eligible"

    adds = "gov.usda.summer_ebt.amount"
