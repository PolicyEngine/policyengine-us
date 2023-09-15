from policyengine_us.model_api import *


class hi_disposition_property_investment_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii elected net capital gain from the disposition of property held for investment "
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://files.hawaii.gov/tax/forms/2022/n158_i.pdf#page=2"  # line 4e
    )
