from policyengine_us.model_api import *


class co_ccap_is_entry(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether filers are on the entry process of Colorado Child Care Assistance Program"
    definition_period = YEAR
    defined_for = StateCode.CO
