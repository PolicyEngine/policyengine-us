from policyengine_us.model_api import *


class hi_alternative_tax_on_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii alternative tax on capital gains"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    adds = [
        "hi_tax_on_capped_reduced_income",
        "hi_eligible_capital_gain_alternative_tax",
    ]
