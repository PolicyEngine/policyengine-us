from policyengine_us.model_api import *


class investment_income_form_4952(Variable):
    value_type = float
    entity = TaxUnit
    label = "Investment income from Form 4952"
    unit = USD
    definition_period = YEAR
