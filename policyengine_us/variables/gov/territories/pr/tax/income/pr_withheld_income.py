from policyengine_us.model_api import *


class pr_withheld_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico withheld income including social security and medicare tax"
    unit = USD
    definition_period = YEAR
    reference = ""
