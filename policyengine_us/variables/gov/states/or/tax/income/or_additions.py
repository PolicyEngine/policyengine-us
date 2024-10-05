from policyengine_us.model_api import *


class or_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon income additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR
