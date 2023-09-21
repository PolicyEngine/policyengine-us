from policyengine_us.model_api import *


class ga_agi_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia additions to federal AGI"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
