from policyengine_us.model_api import *


class az_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona adjusted gross income"
    defined_for = StateCode.AZ
    unit = USD
    definition_period = YEAR