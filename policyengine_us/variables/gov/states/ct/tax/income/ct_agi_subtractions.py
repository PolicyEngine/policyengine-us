from policyengine_us.model_api import *


class ct_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut subtractions from federal AGI to get CT AGI"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
