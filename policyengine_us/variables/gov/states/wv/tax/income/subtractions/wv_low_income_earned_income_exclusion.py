from policyengine_us.model_api import *


class wv_low_income_earned_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia low-income earned income exclusion"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR
