from policyengine_us.model_api import *


class id_selected_aged_or_disabled_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Idaho selected aged or disabled credit"
    definition_period = YEAR
    defined_for = StateCode.ID
    default_value = True
