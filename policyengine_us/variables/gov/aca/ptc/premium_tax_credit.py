from policyengine_us.model_api import *


class premium_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Affordable Care Act Premium Tax Credit"
    unit = USD
    definition_period = MONTH

    adds = ["aca_ptc"]
