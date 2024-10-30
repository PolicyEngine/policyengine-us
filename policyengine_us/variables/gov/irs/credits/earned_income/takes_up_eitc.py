from policyengine_us.model_api import *


class takes_up_eitc(Variable):
    value_type = bool
    entity = TaxUnit
    label = "takes up the EITC"
    definition_period = YEAR
    default_value = True
