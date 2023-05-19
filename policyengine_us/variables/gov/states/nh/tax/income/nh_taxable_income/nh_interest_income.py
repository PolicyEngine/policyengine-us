from policyengine_us.model_api import *


class nh_interest_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire interest income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH