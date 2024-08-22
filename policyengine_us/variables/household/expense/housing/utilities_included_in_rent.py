from policyengine_us.model_api import *


class utilities_included_in_rent(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether utilities are included in rent payments"
    definition_period = YEAR
