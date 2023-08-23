from policyengine_us.model_api import *


class az_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
