from policyengine_us.model_api import *


class pension_survivors(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Pension and annuity income from survivors benefits"
    unit = USD
