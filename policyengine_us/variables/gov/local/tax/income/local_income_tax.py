from policyengine_us.model_api import *


class local_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local income tax"
    unit = USD

    adds = ["nyc_income_tax", "md_local_income_tax_before_credits"]
