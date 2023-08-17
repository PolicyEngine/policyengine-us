from policyengine_us.model_api import *


class co_pension_survivors(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Colorado pension and annuity income from survivors benefits"
    unit = USD
