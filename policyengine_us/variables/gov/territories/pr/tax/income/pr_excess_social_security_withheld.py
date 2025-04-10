from policyengine_us.model_api import *


class pr_excess_social_security_withheld(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico excess social security withheld"
    unit = USD
    definition_period = YEAR
    reference = ""
