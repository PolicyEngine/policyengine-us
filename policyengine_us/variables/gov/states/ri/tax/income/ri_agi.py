from policyengine_us.model_api import *


class ri_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island adjusted gross income"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR
