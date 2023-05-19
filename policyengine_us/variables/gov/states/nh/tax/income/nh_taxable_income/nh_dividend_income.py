from policyengine_us.model_api import *


class nh_dividend_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire dividend income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH