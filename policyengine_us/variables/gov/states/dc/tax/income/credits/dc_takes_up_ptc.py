from policyengine_us.model_api import *


class dc_takes_up_ptc(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Takes up the DC property tax credit"
    definition_period = YEAR
    defined_for = StateCode.DC
