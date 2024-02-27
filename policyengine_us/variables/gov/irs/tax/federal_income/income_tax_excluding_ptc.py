from policyengine_us.model_api import *


class income_tax_excluding_ptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "income tax (excluding PTC)"
    unit = USD
    definition_period = YEAR
    adds = ["income_tax"]
    subtracts = ["premium_tax_credit"]
