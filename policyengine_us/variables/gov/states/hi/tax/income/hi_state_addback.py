from policyengine_us.model_api import *


class hi_state_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii state income tax addback"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=11"
    )
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        
        return 
