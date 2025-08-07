from policyengine_us.model_api import *


class takes_up_dc_ptc(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Takes up the DC property tax credit"
    definition_period = YEAR
    defined_for = StateCode.DC
    default_value = True
