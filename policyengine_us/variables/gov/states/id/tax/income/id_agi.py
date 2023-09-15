from policyengine_us.model_api import *


class id_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho adjusted grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = "StateCode.ID"
