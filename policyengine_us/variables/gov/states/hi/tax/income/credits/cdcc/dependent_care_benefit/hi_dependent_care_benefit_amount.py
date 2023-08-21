from policyengine_us.model_api import *

class hi_dcb_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii amount of dependent care benefits recieved"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
