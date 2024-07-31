from policyengine_us.model_api import *


class investment_income_elected_form_4952(Variable):
    value_type = float
    entity = Person
    label = "investment income elected on Form 4952"
    unit = USD
    definition_period = YEAR
