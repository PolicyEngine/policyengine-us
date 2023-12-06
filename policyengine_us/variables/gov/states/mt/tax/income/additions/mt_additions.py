from policyengine_us.model_api import *


class mt_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
