from policyengine_us.model_api import *


class hi_military_pay_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii military reserve or national guard duty pay exclusion"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=13"
    )
    definition_period = YEAR
    defined_for = StateCode.HI
