from policyengine_us.model_api import *


class tax_unit_social_security(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit Social Security"
    unit = USD
    definition_period = YEAR

    adds = ["social_security"]
