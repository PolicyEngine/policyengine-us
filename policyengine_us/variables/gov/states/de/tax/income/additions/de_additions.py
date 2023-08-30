from policyengine_us.model_api import *


class de_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware agi additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
