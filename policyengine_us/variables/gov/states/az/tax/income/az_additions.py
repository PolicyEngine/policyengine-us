from policyengine_us.model_api import *


class az_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
