from policyengine_us.model_api import *


class vt_subsidy(Variable):
    value_type = bool
    entity = TaxUnit
    label = "The household received subsidies"
    definition_period = YEAR
    defined_for = StateCode.VT
