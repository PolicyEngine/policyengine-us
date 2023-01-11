from policyengine_us.model_api import *


class spm_unit_market_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Market income"
    definition_period = YEAR
    unit = USD

    adds = ["market_income"]
