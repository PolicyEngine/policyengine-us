from policyengine_us.model_api import *


class ca_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA AGI"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
