from policyengine_us.model_api import *


class nyc_school_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC School Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"

    adds = [
        "nyc_school_tax_credit_fixed_amount",
        "nyc_school_tax_credit_rate_reduction_amount",
    ]
