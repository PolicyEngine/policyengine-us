from policyengine_us.model_api import *


class co_ccap_is_re_determination(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Quality rating of child care facility for Colorado Child Care Assistance Program"
    definition_period = YEAR
    defined_for = StateCode.CO
    reference = ""
