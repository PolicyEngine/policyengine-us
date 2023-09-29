from policyengine_us.model_api import *


class id_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
